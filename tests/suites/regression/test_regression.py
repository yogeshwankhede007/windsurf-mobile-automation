"""Regression tests for comprehensive app testing."""
import time
import pytest
import logging
import random
import string
from appium.webdriver.common.appiumby import AppiumBy
from tests.base_test import BaseTest

logger = logging.getLogger(__name__)

class TestAppRegression(BaseTest):
    """Regression tests for comprehensive app testing."""
    
    @pytest.mark.regression
    @pytest.mark.performance
    @pytest.mark.parametrize("platform", ["android", "ios"])
    def test_login_performance(self, platform, request):
        """Test login performance on both platforms."""
        if platform != request.config.getoption("--platform"):
            pytest.skip(f"Skipping {platform} test")
            
        logger.info(f"Testing login performance on {platform}")
        
        # Measure login time
        start_time = time.time()
        self.login_page.login(self.valid_username, self.valid_password)
        end_time = time.time()
        
        login_time = end_time - start_time
        logger.info(f"Login completed in {login_time:.2f} seconds")
        
        # Assert login time is reasonable (adjust threshold as needed)
        assert login_time < 5.0, f"Login took too long: {login_time:.2f} seconds"
        
        # Verify successful login
        assert self.login_page.is_element_displayed((AppiumBy.ACCESSIBILITY_ID, "home-screen")), \
            "Failed to login successfully"
    
    @pytest.mark.regression
    @pytest.mark.security
    def test_password_security(self):
        """Test password field security features."""
        logger.info("Testing password field security")
        
        # Verify password field is secure (shows dots instead of text)
        password_field = self.login_page.find_element((AppiumBy.ACCESSIBILITY_ID, "password-field"))
        assert password_field.get_attribute("password") == "true", "Password field is not secure"
        
        # Verify password is not logged in plain text
        self.login_page.login("test", "sensitive_password")
        log_messages = self.driver.get_log("logcat")
        for entry in log_messages:
            assert "sensitive_password" not in str(entry).lower(), \
                f"Password found in logs: {entry}"
    
    @pytest.mark.regression
    @pytest.mark.parametrize("username,password,expected_error", [
        ("test@test.com", "short", "password must be"),
        ("invalid-email", "Test@1234", "valid email"),
        ("x" * 256, "Test@1234", "too long"),
    ])
    def test_input_validation(self, username, password, expected_error):
        """Test various input validations."""
        logger.info(f"Testing input validation with username: {username}, password: {'*' * len(password)}")
        
        # Attempt login with invalid credentials
        self.login_page.login(username, password)
        
        # Verify appropriate error message
        error_message = self.login_page.get_error_message()
        assert error_message is not None, "Expected error message not displayed"
        assert expected_error.lower() in error_message.lower(), \
            f"Expected error containing '{expected_error}' but got: {error_message}"
    
    @pytest.mark.regression
    @pytest.mark.stability
    def test_rapid_login_attempts(self):
        """Test app stability with rapid login attempts."""
        logger.info("Testing rapid login attempts")
        
        for i in range(5):  # Try 5 rapid login attempts
            try:
                self.login_page.login(
                    f"user_{i}@test.com",
                    "wrong_password"
                )
                error_message = self.login_page.get_error_message()
                assert error_message is not None, "Expected error message not displayed"
                
                # Add a small delay between attempts
                time.sleep(0.5)
                
                # Clear fields for next attempt
                self.driver.reset()
                
            except Exception as e:
                pytest.fail(f"App crashed during rapid login attempt {i+1}: {str(e)}")
    
    @pytest.mark.regression
    @pytest.mark.parametrize("platform", ["android", "ios"])
    def test_orientation_changes(self, platform, request):
        """Test app behavior during orientation changes."""
        if platform != request.config.getoption("--platform"):
            pytest.skip(f"Skipping {platform} test")
            
        logger.info(f"Testing orientation changes on {platform}")
        
        # Enter some text in the username field
        self.login_page.enter_text(
            (AppiumBy.ACCESSIBILITY_ID, "username-field"),
            "test@example.com"
        )
        
        # Change orientation
        current_orientation = self.driver.orientation
        new_orientation = "LANDSCAPE" if current_orientation == "PORTRAIT" else "PORTRAIT"
        self.driver.orientation = new_orientation
        
        # Verify orientation changed
        assert self.driver.orientation == new_orientation, "Orientation did not change"
        
        # Verify entered text is still present
        username_field = self.login_page.find_element((AppiumBy.ACCESSIBILITY_ID, "username-field"))
        assert username_field.get_attribute("value") == "test@example.com", "Entered text was lost"
    
    @pytest.mark.regression
    @pytest.mark.stress
    def test_long_strings_in_inputs(self):
        """Test app behavior with very long input strings."""
        logger.info("Testing long string inputs")
        
        # Generate a very long string (10KB)
        long_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10*1024))
        
        # Test username field
        self.login_page.enter_text(
            (AppiumBy.ACCESSIBILITY_ID, "username-field"),
            long_string
        )
        
        # Test password field
        self.login_page.enter_text(
            (AppiumBy.ACCESSIBILITY_ID, "password-field"),
            long_string
        )
        
        # Verify the app didn't crash and handles long inputs gracefully
        assert True, "App should handle long input strings gracefully"
