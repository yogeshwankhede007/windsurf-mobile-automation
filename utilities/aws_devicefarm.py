"""
AWS Device Farm Integration

This module provides functionality to run tests on AWS Device Farm.
It handles test package creation, upload, and execution on AWS Device Farm.
"""

import base64
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSDeviceFarm:
    """AWS Device Farm integration for running mobile tests in the cloud."""

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = 'us-west-2'
    ):
        """Initialize AWS Device Farm client.
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region (default: us-west-2)
        """
        self.region = region
        self.client = boto3.client(
            'devicefarm',
            region_name=region,
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.project_arn = None
        self.device_pool_arn = None
        self.test_spec = {
            "version": 0.1,
            "test_package": {
                "type": "APPIUM_PYTHON_TEST_PACKAGE",
                "test_spec": {
                    "type": "INSTRUMENTATION"
                }
            },
            "environment_variables": {}
        }

    def set_project(self, project_name: str) -> str:
        """Set or create the Device Farm project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            str: Project ARN
        """
        try:
            projects = self.client.list_projects()
            for project in projects['projects']:
                if project['name'] == project_name:
                    self.project_arn = project['arn']
                    logger.info(f"Using existing project: {project_name}")
                    return self.project_arn
            
            # Create new project if not exists
            response = self.client.create_project(name=project_name)
            self.project_arn = response['project']['arn']
            logger.info(f"Created new project: {project_name}")
            return self.project_arn
            
        except ClientError as e:
            logger.error(f"Error setting project: {e}")
            raise

    def set_device_pool(
        self,
        pool_name: str = 'Top Devices',
        rules: Optional[List[Dict]] = None
    ) -> str:
        """Set or create a device pool.
        
        Args:
            pool_name: Name of the device pool
            rules: List of rules for device selection
            
        Returns:
            str: Device pool ARN
        """
        if not self.project_arn:
            raise ValueError("Project must be set before setting device pool")
            
        try:
            # Check if pool exists
            pools = self.client.list_device_pools(arn=self.project_arn)
            for pool in pools['devicePools']:
                if pool['name'] == pool_name:
                    self.device_pool_arn = pool['arn']
                    logger.info(f"Using existing device pool: {pool_name}")
                    return self.device_pool_arn
            
            # Default rules if none provided
            if not rules:
                rules = [
                    {
                        'attribute': 'MANUFACTURER',
                        'operator': 'EQUALS',
                        'value': 'Google'
                    },
                    {
                        'attribute': 'PLATFORM',
                        'operator': 'EQUALS',
                        'value': 'ANDROID'
                    }
                ]
            
            # Create new pool
            response = self.client.create_device_pool(
                projectArn=self.project_arn,
                name=pool_name,
                rules={'rules': rules}
            )
            self.device_pool_arn = response['devicePool']['arn']
            logger.info(f"Created new device pool: {pool_name}")
            return self.device_pool_arn
            
        except ClientError as e:
            logger.error(f"Error setting device pool: {e}")
            raise

    def upload_file(
        self,
        file_path: str,
        file_type: str,
        mime_type: str = 'application/octet-stream'
    ) -> str:
        """Upload a file to AWS Device Farm.
        
        Args:
            file_path: Path to the file to upload
            file_type: Type of the file (e.g., 'APPIUM_PYTHON_TEST_PACKAGE')
            mime_type: MIME type of the file
            
        Returns:
            str: Upload ARN
        """
        if not self.project_arn:
            raise ValueError("Project must be set before uploading files")
            
        try:
            # Get upload URL
            response = self.client.create_upload(
                projectArn=self.project_arn,
                name=os.path.basename(file_path),
                type=file_type,
                contentType=mime_type
            )
            
            upload_url = response['upload']['url']
            upload_arn = response['upload']['arn']
            
            # Upload the file
            with open(file_path, 'rb') as file_data:
                import requests
                response = requests.put(
                    upload_url,
                    data=file_data,
                    headers={'Content-Type': mime_type}
                )
                response.raise_for_status()
            
            # Wait for upload to complete
            while True:
                upload = self.client.get_upload(arn=upload_arn)['upload']
                status = upload['status']
                
                if status == 'FAILED':
                    raise Exception(f"Upload failed: {upload.get('message', 'Unknown error')}")
                elif status == 'SUCCEEDED':
                    logger.info(f"Successfully uploaded {file_path}")
                    return upload_arn
                
                time.sleep(5)
                
        except (ClientError, Exception) as e:
            logger.error(f"Error uploading file: {e}")
            raise

    def run_tests(
        self,
        app_arn: str,
        test_package_arn: str,
        test_spec_arn: Optional[str] = None,
        name: Optional[str] = None,
        device_pool_arn: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        wait_for_completion: bool = True,
        timeout: int = 3600
    ) -> Dict:
        """Run tests on AWS Device Farm.
        
        Args:
            app_arn: ARN of the app to test
            test_package_arn: ARN of the test package
            test_spec_arn: ARN of the test spec (optional)
            name: Name of the test run
            device_pool_arn: ARN of the device pool to use
            environment_variables: Environment variables to pass to tests
            wait_for_completion: Whether to wait for test completion
            timeout: Maximum time to wait for completion (seconds)
            
        Returns:
            Dict: Test run details
        """
        if not self.project_arn:
            raise ValueError("Project must be set before running tests")
            
        if not device_pool_arn and not self.device_pool_arn:
            raise ValueError("Device pool must be set before running tests")
            
        device_pool_arn = device_pool_arn or self.device_pool_arn
        
        try:
            # Update test spec with environment variables
            if environment_variables:
                self.test_spec['environment_variables'].update(environment_variables)
            
            # Create test run
            run_name = name or f"TestRun-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            test_params = {
                'projectArn': self.project_arn,
                'appArn': app_arn,
                'devicePoolArn': device_pool_arn,
                'name': run_name,
                'test': {
                    'type': 'APPIUM_PYTHON_TEST_SPEC',
                    'testPackageArn': test_package_arn,
                    'testSpecArn': test_spec_arn,
                    'parameters': {
                        'test_package_parameters': json.dumps(self.test_spec)
                    }
                }
            }
            
            response = self.client.schedule_run(**test_params)
            run_arn = response['run']['arn']
            logger.info(f"Started test run: {run_name} (ARN: {run_arn})")
            
            if not wait_for_completion:
                return response['run']
            
            # Wait for test completion
            start_time = time.time()
            while True:
                run = self.client.get_run(arn=run_arn)['run']
                status = run['status']
                
                if status in ['COMPLETED', 'STOPPED']:
                    logger.info(f"Test run {status.lower()} with result: {run.get('result', 'UNKNOWN')}")
                    return run
                elif status in ['ERRORED', 'FAILED']:
                    logger.error(f"Test run {status.lower()}: {run.get('message', 'No error message')}")
                    return run
                
                if time.time() - start_time > timeout:
                    logger.warning(f"Test run timed out after {timeout} seconds")
                    return run
                
                logger.info(f"Test run status: {status} - Waiting...")
                time.sleep(30)
                
        except ClientError as e:
            logger.error(f"Error running tests: {e}")
            raise

    def download_artifacts(self, run_arn: str, output_dir: str) -> None:
        """Download test artifacts from a completed run.
        
        Args:
            run_arn: ARN of the test run
            output_dir: Directory to save artifacts
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get list of artifacts
            artifacts = self.client.list_artifacts(arn=run_arn, type='FILE')
            
            for artifact in artifacts.get('artifacts', []):
                artifact_name = artifact['name']
                artifact_extension = artifact.get('extension', '')
                
                # Skip if no URL
                if 'url' not in artifact or not artifact['url']:
                    continue
                
                # Download the artifact
                import requests
                response = requests.get(artifact['url'], stream=True)
                response.raise_for_status()
                
                # Save the artifact
                file_name = f"{artifact_name}{artifact_extension}"
                file_path = os.path.join(output_dir, file_name)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Downloaded artifact: {file_path}")
                
        except (ClientError, Exception) as e:
            logger.error(f"Error downloading artifacts: {e}")
            raise


def create_test_package(
    test_dir: str,
    output_dir: str = 'dist',
    package_name: str = 'test_package.zip'
) -> str:
    """Create a test package for AWS Device Farm.
    
    Args:
        test_dir: Directory containing test files
        output_dir: Output directory for the package
        package_name: Name of the output package file
        
    Returns:
        str: Path to the created package
    """
    import zipfile
    import tempfile
    import shutil
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, package_name)
    
    # Create a temporary directory for the package
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy test files to the temporary directory
        shutil.copytree(
            test_dir,
            os.path.join(temp_dir, os.path.basename(test_dir)),
            dirs_exist_ok=True
        )
        
        # Create requirements.txt if it doesn't exist
        requirements_path = os.path.join(temp_dir, 'requirements.txt')
        if not os.path.exists(requirements_path):
            with open(requirements_path, 'w') as f:
                f.write("pytest\npytest-html\npytest-xdist\nAppium-Python-Client\n")
        
        # Create test_spec.yml
        test_spec = {
            'version': 0.1,
            'test_package': {
                'type': 'APPIUM_PYTHON_TEST_PACKAGE',
                'test_spec': {
                    'type': 'INSTRUMENTATION',
                    'test_package_name': os.path.basename(test_dir)
                }
            },
            'environment_variables': {}
        }
        
        with open(os.path.join(temp_dir, 'test_spec.yml'), 'w') as f:
            import yaml
            yaml.dump(test_spec, f)
        
        # Create the zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
    
    logger.info(f"Created test package: {output_path}")
    return output_path
