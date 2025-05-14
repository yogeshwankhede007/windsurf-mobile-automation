#!/usr/bin/env python3
"""
AWS Device Farm Test Runner

This script provides a command-line interface to run tests on AWS Device Farm.
It handles test package creation, upload, and execution.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utilities.aws_devicefarm import AWSDeviceFarm, create_test_package
from config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    # Load config to get default app paths
    config = Config.from_env()
    
    # Default app paths from config
    default_android_app = str(config.app.find_latest_app('android')) if config.app.find_latest_app('android') else None
    default_ios_app = str(config.app.find_latest_app('ios')) if config.app.find_latest_app('ios') else None
    
    parser = argparse.ArgumentParser(description='Run tests on AWS Device Farm')
    
    # AWS credentials
    parser.add_argument('--aws-access-key', help='AWS access key ID')
    parser.add_argument('--aws-secret-key', help='AWS secret access key')
    parser.add_argument('--region', default='us-west-2', help='AWS region')
    
    # Project and device pool
    parser.add_argument('--project-name', required=True, help='Device Farm project name')
    parser.add_argument('--device-pool', default='Top Devices', help='Device pool name')
    
    # Test configuration
    parser.add_argument('--test-dir', default='tests', help='Directory containing test files')
    parser.add_argument('--app-path', 
                      help=f'Path to the app file (APK/IPA). Defaults to latest in apps directory.\n'
                           f'Android: {default_android_app or "No Android app found"}\n'
                           f'iOS: {default_ios_app or "No iOS app found"}')
    parser.add_argument('--platform', choices=['android', 'ios'], required=True, 
                       help='Target platform (android/ios)')
    parser.add_argument('--output-dir', default='reports/aws_devicefarm', help='Output directory for reports')
    
    # Test execution
    parser.add_argument('--wait', action='store_true', help='Wait for test completion')
    parser.add_argument('--timeout', type=int, default=3600, help='Maximum time to wait (seconds)')
    parser.add_argument('--env-var', action='append', help='Environment variables (KEY=VALUE)')
    
    return parser.parse_args()


def parse_environment_variables(env_vars: Optional[list]) -> Dict[str, str]:
    """Parse environment variables from command line."""
    if not env_vars:
        return {}
    
    result = {}
    for var in env_vars:
        if '=' in var:
            key, value = var.split('=', 1)
            result[key] = value
    return result


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # If app path is not provided, try to find it from config
    if not args.app_path:
        config = Config.from_env()
        if args.platform.lower() == 'android':
            args.app_path = config.app.find_latest_app('android')
            if not args.app_path:
                logger.error("No Android app found in apps/android directory")
                sys.exit(1)
        elif args.platform.lower() == 'ios':
            args.app_path = config.app.find_latest_app('ios')
            if not args.app_path:
                logger.error("No iOS app found in apps/ios directory")
                sys.exit(1)
    
    logger.info(f"Using app: {args.app_path}")
    
    try:
        # Initialize AWS Device Farm client
        device_farm = AWSDeviceFarm(
            aws_access_key_id=args.aws_access_key,
            aws_secret_access_key=args.aws_secret_key,
            region=args.region
        )
        
        # Set project and device pool
        device_farm.set_project(args.project_name)
        device_farm.set_device_pool(args.device_pool)
        
        # Create test package
        logger.info("Creating test package...")
        test_package_path = create_test_package(
            test_dir=args.test_dir,
            output_dir=args.output_dir,
            package_name='test_package.zip'
        )
        
        # Upload files
        logger.info("Uploading app file...")
        app_arn = device_farm.upload_file(
            file_path=args.app_path,
            file_type='ANDROID_APP' if args.app_path.endswith('.apk') else 'IOS_APP'
        )
        
        logger.info("Uploading test package...")
        test_package_arn = device_farm.upload_file(
            file_path=test_package_path,
            file_type='APPIUM_PYTHON_TEST_PACKAGE'
        )
        
        # Parse environment variables
        env_vars = parse_environment_variables(args.env_var)
        
        # Get app filename for the run name
        app_filename = os.path.basename(args.app_path) if args.app_path else 'auto-detected-app'
        
        # Run tests
        logger.info("Starting test run...")
        run = device_farm.run_tests(
            app_arn=app_arn,
            test_package_arn=test_package_arn,
            name=f"{args.platform.upper()}-{app_filename}-{os.environ.get('GIT_COMMIT', 'local')[:7]}",
            environment_variables={
                **env_vars,
                'PLATFORM': args.platform,
                'ENV': 'aws-device-farm'
            },
            wait_for_completion=args.wait,
            timeout=args.timeout
        )
        
        # Save run details
        run_details_path = os.path.join(args.output_dir, 'run_details.json')
        with open(run_details_path, 'w') as f:
            json.dump(run, f, indent=2)
        
        logger.info(f"Test run details saved to: {run_details_path}")
        
        # Download artifacts if test completed
        if args.wait and run.get('status') == 'COMPLETED':
            logger.info("Downloading artifacts...")
            artifacts_dir = os.path.join(args.output_dir, 'artifacts')
            device_farm.download_artifacts(run['arn'], artifacts_dir)
            logger.info(f"Artifacts downloaded to: {artifacts_dir}")
        
        # Return non-zero exit code if test failed
        if run.get('result') not in ['PASSED', 'WARNED']:
            logger.error("Test run failed or produced warnings")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
