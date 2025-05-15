"""Base test class for all test suites."""
import os
import pytest
import logging
from datetime import datetime
from typing import Dict, Any
from appium.webdriver.remote.webdriver import WebDriver
from pages.login_page import LoginPage

# Configure logger
logger = logging.getLogger(__name__)

class BaseTest:
    """Base test class that provides common functionality for all tests."""
    
    @pytest.fixture(autouse=True)
    def setup(self, request, driver: WebDriver, test_data: Dict[str, Any]):
        """Setup method that runs before each test."""
        self.driver = driver
        self.platform = request.config.getoption("--platform")
        self.suite = request.config.getoption("--suite")
        self.test_data = test_data
        
        # Reset app state before each test
        self.driver.reset()
        
        # Initialize page objects
        self.login_page = LoginPage(driver)
        
        # Setup test-specific data
        self._setup_test_data()
        
        yield
        
        # Teardown actions here
        if hasattr(request.node, 'rep_call') and hasattr(request.node.rep_call, 'failed') and request.node.rep_call.failed:
            # Take screenshot on test failure
            self._take_screenshot(request.node.name)
    
    def _setup_test_data(self) -> None:
        """Setup test data for the current test."""
        self.valid_username = self.test_data["valid_username"]
        self.valid_password = self.test_data["valid_password"]
        self.invalid_username = self.test_data["invalid_username"]
        self.invalid_password = self.test_data["invalid_password"]
    
    def _take_screenshot(self, test_name: str) -> None:
        """Take a screenshot and save it to the screenshots directory."""
        try:
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshot_dir}/{test_name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
    
    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        """Fixture to provide test data."""
        return {
            "valid_username": "testuser@example.com",
            "valid_password": "Test@1234",
            "invalid_username": "invalid@example.com",
            "invalid_password": "wrongpassword",
            "empty_username": "",
            "empty_password": "",
        }
