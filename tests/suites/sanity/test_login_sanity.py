"""Sanity tests for login functionality."""
import pytest
import logging
from tests.base_test import BaseTest

logger = logging.getLogger(__name__)

class TestLoginSanity(BaseTest):
    """Sanity tests for login functionality."""
    
    @pytest.mark.sanity
    @pytest.mark.android
    def test_valid_login_android(self):
        """Test valid login on Android."""
        logger.info("Starting valid login test on Android")
        
        # Perform login with valid credentials
        self.login_page.login(self.valid_username, self.valid_password)
        
        # Verify successful login by checking for home screen element
        # Replace with actual verification for your app
        assert self.login_page.is_element_displayed((AppiumBy.ACCESSIBILITY_ID, "home-screen")) \
            or not self.login_page.is_error_message_displayed()
    
    @pytest.mark.sanity
    @pytest.mark.ios
    def test_valid_login_ios(self):
        """Test valid login on iOS."""
        logger.info("Starting valid login test on iOS")
        
        # Perform login with valid credentials
        self.login_page.login(self.valid_username, self.valid_password)
        
        # Verify successful login by checking for home screen element
        # Replace with actual verification for your app
        assert self.login_page.is_element_displayed((AppiumBy.ACCESSIBILITY_ID, "home-screen")) \
            or not self.login_page.is_error_message_displayed()

    @pytest.mark.sanity
    @pytest.mark.android
    def test_invalid_login_android(self):
        """Test invalid login on Android."""
        logger.info("Starting invalid login test on Android")
        
        # Attempt login with invalid credentials
        self.login_page.login(self.invalid_username, self.invalid_password)
        
        # Verify error message is displayed
        error_message = self.login_page.get_error_message()
        assert error_message is not None, "Expected error message not displayed"
        assert "invalid" in error_message.lower() or "incorrect" in error_message.lower()
    
    @pytest.mark.sanity
    @pytest.mark.ios
    def test_invalid_login_ios(self):
        """Test invalid login on iOS."""
        logger.info("Starting invalid login test on iOS")
        
        # Attempt login with invalid credentials
        self.login_page.login(self.invalid_username, self.invalid_password)
        
        # Verify error message is displayed
        error_message = self.login_page.get_error_message()
        assert error_message is not None, "Expected error message not displayed"
        assert "invalid" in error_message.lower() or "incorrect" in error_message.lower()
    
    @pytest.mark.sanity
    @pytest.mark.parametrize("username,password,expected_error", [
        ("", "Test@1234", "username"),
        ("testuser@example.com", "", "password"),
        ("", "", "credentials"),
    ])
    def test_empty_credentials(self, username, password, expected_error):
        """Test login with empty credentials."""
        logger.info(f"Testing login with empty fields: username='{username}', password='{password}'")
        
        # Attempt login with empty credentials
        self.login_page.login(username, password)
        
        # Verify appropriate error message
        error_message = self.login_page.get_error_message()
        assert error_message is not None, "Expected error message not displayed"
        assert expected_error.lower() in error_message.lower()
