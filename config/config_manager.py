"""Configuration manager for handling external configuration files."""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Manages loading and accessing configuration from external files."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the ConfigManager with the configuration directory.
        
        Args:
            config_dir: Base directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._config_cache: Dict[str, Any] = {}
    
    def load_config(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            file_type: Type of the file ('json' or 'yaml'). If None, inferred from extension
            
        Returns:
            Dict containing the configuration
        """
        if file_path in self._config_cache:
            return self._config_cache[file_path]
            
        path = self.config_dir / file_path
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        file_type = file_type or path.suffix.lstrip('.')
        
        with open(path, 'r', encoding='utf-8') as f:
            if file_type.lower() == 'json':
                config = json.load(f)
            elif file_type.lower() in ('yaml', 'yml'):
                config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        self._config_cache[file_path] = config
        return config
    
    def get_platform_capabilities(self, platform: str) -> Dict[str, Any]:
        """Get capabilities for a specific platform.
        
        Args:
            platform: Platform name ('android' or 'ios')
            
        Returns:
            Dict containing platform-specific capabilities
        """
        if platform not in ('android', 'ios'):
            raise ValueError(f"Unsupported platform: {platform}")
            
        # Load common capabilities
        common_caps = self.load_config("common/capabilities.json").get("common", {})
        
        # Load platform-specific capabilities
        platform_caps = self.load_config(f"{platform}/capabilities.json").get(platform, {})
        
        # Merge capabilities (platform-specific overrides common)
        return {**common_caps, **platform_caps}
    
    def get_test_data(self, test_suite: str, test_name: str = None) -> Dict[str, Any]:
        """Get test data for a specific test suite and optionally a specific test.
        
        Args:
            test_suite: Name of the test suite
            test_name: Optional name of the specific test
            
        Returns:
            Dict containing test data
        """
        try:
            test_data = self.load_config(f"test_data/{test_suite}.yaml")
            if test_name and test_name in test_data:
                return test_data[test_name]
            return test_data
        except FileNotFoundError:
            return {}


# Singleton instance
config_manager = ConfigManager()
