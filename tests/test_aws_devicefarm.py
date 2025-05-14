"""
Test cases for AWS Device Farm integration.

These tests demonstrate how to write tests that can run both locally and on AWS Device Farm.
"""

import os
import pytest
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Test markers
pytestmark = [
    pytest.mark.aws_devicefarm,
    pytest.mark.smoke
]

class TestAWSDeviceFarm:
    """Test cases for AWS Device Farm integration."""
    
    def test_app_launch(self, driver):
        """Test that the app launches successfully."""
        # Get the current platform from the driver capabilities
        platform_name = driver.capabilities['platformName'].lower()
        logger.info(f"Running test on platform: {platform_name}")
        
        # Simple assertion to verify the app is running
        # The actual check will depend on your app's structure
        assert driver.current_activity is not None or \
               driver.current_package is not None or \
               driver.current_context is not None
        
        logger.info("App launched successfully")
    
    def test_device_info(self, driver):
        """Test that device information is available."""
        # Get device information
        capabilities = driver.capabilities
        logger.info(f"Device capabilities: {capabilities}")
        
        # Verify basic device information is available
        assert 'deviceName' in capabilities
        assert 'platformName' in capabilities
        assert 'platformVersion' in capabilities
        
        logger.info("Device information verified")
    
    @pytest.mark.parametrize("orientation", ["PORTRAIT", "LANDSCAPE"])
    def test_screen_orientation(self, driver, orientation):
        """Test screen orientation changes."""
        # Skip if the device doesn't support orientation changes
        if 'orientation' not in driver.capabilities:
            pytest.skip("Orientation not supported on this device")
        
        # Set orientation
        driver.orientation = orientation
        assert driver.orientation == orientation
        
        logger.info(f"Successfully changed orientation to {orientation}")


# This allows the test to be run directly with python -m pytest
def test_main():
    ""
    This function allows the test to be run directly with `python -m pytest tests/test_aws_devicefarm.py`.
    It's useful for local development and debugging.
    """
    import sys
    import pytest
    
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent
    
    # Add the project root to the Python path
    sys.path.insert(0, str(project_root))
    
    # Run the tests
    sys.exit(pytest.main([str(Path(__file__).relative_to(project_root))]))


if __name__ == "__main__":
    test_main()
