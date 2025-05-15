"""Utility for loading test data from configuration files."""
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from config.config_manager import config_manager


class TestDataLoader:
    """Loads and manages test data from YAML configuration files."""
    
    @staticmethod
    def load_test_data(test_suite: str, test_case: Optional[str] = None) -> Union[Dict[str, Any], Any]:
        """Load test data for a specific test suite and optionally a specific test case.
        
        Args:
            test_suite: Name of the test suite (filename without .yaml extension)
            test_case: Optional name of the specific test case to load
            
        Returns:
            Dict containing the test data, or the specific test case data if test_case is provided
            
        Example:
            # Load all login test data
            login_data = TestDataLoader.load_test_data('login')
            
            # Load specific test case
            valid_login = TestDataLoader.load_test_data('login', 'valid_credentials')
        """
        return config_manager.get_test_data(test_suite, test_case)
    
    @staticmethod
    def get_test_parameters(test_suite: str, test_case: str) -> Dict[str, Any]:
        """Get test parameters for a specific test case.
        
        This is a convenience method that wraps load_test_data for better readability.
        
        Args:
            test_suite: Name of the test suite
            test_case: Name of the test case
            
        Returns:
            Dict containing the test parameters
            
        Example:
            params = TestDataLoader.get_test_parameters('login', 'valid_credentials')
        """
        return config_manager.get_test_data(test_suite, test_case)
    
    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load data from a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dict containing the parsed YAML data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is malformed
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def save_test_data(cls, test_suite: str, data: Dict[str, Any]) -> None:
        """Save test data to a YAML file.
        
        Args:
            test_suite: Name of the test suite (filename without .yaml extension)
            data: Data to save
            
        Example:
            test_data = {
                'valid_credentials': {
                    'username': 'user1',
                    'password': 'pass123'
                }
            }
            TestDataLoader.save_test_data('login', test_data)
        """
        test_data_dir = Path("config/test_data")
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = test_data_dir / f"{test_suite}.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Singleton instance
test_data_loader = TestDataLoader()
