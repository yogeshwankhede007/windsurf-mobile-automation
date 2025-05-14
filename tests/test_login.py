"""Test cases for the login functionality.

This module contains test cases that verify the login functionality of the application
using the mobile automation framework. It demonstrates best practices for writing
maintainable and reliable UI tests.
"""

import logging
import time
from typing import Dict, Any, Optional

import allure
import pytest
from appium.webdriver.webelement import WebElement

from config.config import config
from pages.base_page import BasePage
from utilities.test_utils import TestBase

# Configure logger
logger: logging.Logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Page Object for the Login page."""
    
    # Locators
    USERNAME_FIELD = ("id", "username")
    PASSWORD_FIELD = ("id", "password")
    LOGIN_BUTTON = ("id", "loginButton")
    FORGOT_PASSWORD_LINK = ("id", "forgotPassword")
    ERROR_MESSAGE = ("id", "errorMessage")
    
    def __init__(self, driver):
        """Initialize the LoginPage."""
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
    
    def is_login_page_visible(self, timeout: int = 10) -> bool:
        """Check if the login page is visible."""
        try:
            return self.is_element_visible(self.USERNAME_FIELD, timeout) and \
                   self.is_element_visible(self.PASSWORD_FIELD, timeout)
        except Exception as e:
            self.logger.error(f"Error checking if login page is visible: {e}")
            return False
    
    def enter_username(self, username: str) -> None:
        """Enter username in the username field."""
        self.logger.info(f"Entering username: {username}")
        self.clear_and_type(self.USERNAME_FIELD, username)
    
    def enter_password(self, password: str) -> None:
        """Enter password in the password field."""
        self.logger.info("Entering password")
        self.clear_and_type(self.PASSWORD_FIELD, password)
    
    def click_login_button(self, expect_success: bool = True) -> Optional[Any]:
        """Click the login button.
        
        Args:
            expect_success: Whether to expect a successful login.
            
        Returns:
            DashboardPage if login is successful, None otherwise.
        """
        self.logger.info("Clicking login button")
        self.click(self.LOGIN_BUTTON)
        
        if expect_success:
            from pages.dashboard_page import DashboardPage  # Avoid circular import
            return DashboardPage(self.driver)
        return None
    
    def click_forgot_password(self) -> 'ForgotPasswordPage':
        """Click the forgot password link."""
        self.logger.info("Clicking forgot password link")
        self.click(self.FORGOT_PASSWORD_LINK)
        return ForgotPasswordPage(self.driver)
    
    def get_error_message(self, timeout: int = 5) -> str:
        """Get the error message text."""
        try:
            return self.get_element_text(self.ERROR_MESSAGE, timeout)
        except Exception as e:
            self.logger.error(f"Error getting error message: {e}")
            return ""


class ForgotPasswordPage(BasePage):
    """Page Object for the Forgot Password page."""
    
    # Locators
    EMAIL_FIELD = ("id", "email")
    RESET_BUTTON = ("id", "resetButton")
    SUCCESS_MESSAGE = ("id", "successMessage")
    
    def __init__(self, driver):
        """Initialize the ForgotPasswordPage."""
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
    
    def request_password_reset(self, email: str) -> 'ResetPasswordPage':
        """Request a password reset.
        
        Args:
            email: The email address to send the reset link to.
            
        Returns:
            ResetPasswordPage: The reset password page object.
        """
        self.logger.info(f"Requesting password reset for email: {email}")
        self.clear_and_type(self.EMAIL_FIELD, email)
        self.click(self.RESET_BUTTON)
        return ResetPasswordPage(self.driver)
    
    def get_success_message(self, timeout: int = 5) -> str:
        """Get the success message text."""
        try:
            return self.get_element_text(self.SUCCESS_MESSAGE, timeout)
        except Exception as e:
            self.logger.error(f"Error getting success message: {e}")
            return ""


class ResetPasswordPage(BasePage):
    """Page Object for the Reset Password page."""
    
    # Locators
    NEW_PASSWORD_FIELD = ("id", "newPassword")
    CONFIRM_PASSWORD_FIELD = ("id", "confirmPassword")
    SUBMIT_BUTTON = ("id", "submitButton")
    
    def __init__(self, driver):
        """Initialize the ResetPasswordPage."""
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
    
    def reset_password(self, new_password: str) -> 'LoginPage':
        """Reset the password.
        
        Args:
            new_password: The new password to set.
            
        Returns:
            LoginPage: The login page object.
        """
        self.logger.info("Resetting password")
        self.clear_and_type(self.NEW_PASSWORD_FIELD, new_password)
        self.clear_and_type(self.CONFIRM_PASSWORD_FIELD, new_password)
        self.click(self.SUBMIT_BUTTON)
        return LoginPage(self.driver)


class DashboardPage(BasePage):
    """Page Object for the Dashboard page."""
    
    # Locators
    DASHBOARD_HEADER = ("id", "dashboardHeader")
    WELCOME_MESSAGE = ("id", "welcomeMessage")
    PROFILE_BUTTON = ("id", "profileButton")
    
    def __init__(self, driver):
        """Initialize the DashboardPage."""
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
    
    def is_dashboard_visible(self, timeout: int = 10) -> bool:
        """Check if the dashboard is visible."""
        try:
            return self.is_element_visible(self.DASHBOARD_HEADER, timeout)
        except Exception as e:
            self.logger.error(f"Error checking if dashboard is visible: {e}")
            return False
    
    def get_welcome_message(self, timeout: int = 5) -> str:
        """Get the welcome message text."""
        try:
            return self.get_element_text(self.WELCOME_MESSAGE, timeout)
        except Exception as e:
            self.logger.error(f"Error getting welcome message: {e}")
            return ""
    
    def navigate_to_profile(self) -> None:
        """Navigate to the profile page."""
        self.logger.info("Navigating to profile page")
        self.click(self.PROFILE_BUTTON)


@allure.epic("Authentication")
@allure.feature("Login")
class TestLogin(TestBase):
    """Test cases for the login functionality.
    
    This test class verifies various login scenarios including successful login,
    invalid credentials, and edge cases.
    """
    
    @pytest.fixture(autouse=True)
    def setup_class(self) -> None:
        """Test class level setup."""
        self.login_page = LoginPage(self.driver)
    
    @allure.story("Successful Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Test successful login with valid credentials.
    
    Steps:
    1. Launch the application
    2. Enter valid username and password
    3. Click the login button
    4. Verify successful login
    """)
    def test_successful_login(self, test_data: Dict[str, str]) -> None:
        """Verify that a user can log in with valid credentials."""
        # Arrange
        username = test_data["valid_username"]
        password = test_data["valid_password"]
        
        # Act
        self.log_step("Navigate to login screen")
        self.login_page.navigate_to_login()
        
        self.log_step("Enter login credentials")
        self.login_page.enter_username(username)
        self.login_page.enter_password(password)
        
        self.log_step("Click login button")
        dashboard_page = self.login_page.click_login_button()
        
        # Assert
        self.log_step("Verify successful login")
        assert dashboard_page.is_dashboard_visible(), "Dashboard not displayed after login"
        
        # Additional verification - check welcome message
        welcome_message = dashboard_page.get_welcome_message()
        assert username in welcome_message, f"Welcome message does not contain username: {username}"
        
        # Take a screenshot for evidence
        self.take_screenshot("after_successful_login")
    
    @allure.story("Login with Invalid Credentials")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("username,password,expected_error", [
        ("invalid_user", "password123", "Invalid username or password"),
        ("test_user", "wrongpass", "Invalid username or password"),
        ("", "password123", "Username is required"),
        ("test_user", "", "Password is required"),
    ])
    def test_invalid_login(
        self, 
        username: str, 
        password: str, 
        expected_error: str
    ) -> None:
        """Verify appropriate error messages for invalid login attempts."""
        # Act
        self.log_step(f"Attempt login with username: {username}")
        self.login_page.navigate_to_login()
        self.login_page.enter_username(username)
        self.login_page.enter_password(password)
        self.login_page.click_login_button(expect_success=False)
        
        # Assert
        error_message = self.login_page.get_error_message()
        assert expected_error in error_message, f"Expected error message not found. Got: {error_message}"
        
        # Take a screenshot for evidence
        self.take_screenshot(f"login_error_{username}")
    
    @allure.story("Password Reset")
    @allure.severity(allure.severity_level.NORMAL)
    def test_password_reset_flow(self, test_data: Dict[str, str]) -> None:
        """Verify the password reset functionality works as expected."""
        # Arrange
        email = test_data["valid_email"]
        
        # Act
        self.log_step("Navigate to password reset page")
        self.login_page.navigate_to_login()
        self.login_page.click_forgot_password()
        
        self.log_step("Request password reset")
        reset_page = self.login_page.request_password_reset(email)
        
        # Assert
        success_message = reset_page.get_success_message()
        assert "reset link" in success_message.lower(), "Password reset success message not displayed"
        
        # Verify email is in the success message
        assert email in success_message, f"Email {email} not found in success message"
        
        # Take a screenshot for evidence
        self.take_screenshot("after_password_reset_request")
    
    @allure.story("Session Management")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_session_expiry(self, test_data: Dict[str, str]) -> None:
        """Verify that the user session expires after inactivity."""
        # Arrange
        username = test_data["valid_username"]
        password = test_data["valid_password"]
        session_timeout = 300  # 5 minutes in seconds
        
        # Log in first
        self.login_page.navigate_to_login()
        self.login_page.enter_username(username)
        self.login_page.enter_password(password)
        dashboard_page = self.login_page.click_login_button()
        
        # Verify initial login
        assert dashboard_page.is_dashboard_visible(), "Dashboard not displayed after login"
        
        # Simulate session timeout
        self.log_step(f"Waiting for session to expire ({session_timeout} seconds)")
        time.sleep(session_timeout + 10)  # Add buffer time
        
        # Try to access a protected page
        dashboard_page.navigate_to_profile()
        
        # Verify redirected to login page
        assert self.login_page.is_login_page_visible(), "Not redirected to login page after session expiry"
        
        # Take a screenshot for evidence
        self.take_screenshot("after_session_expiry")


@pytest.fixture(scope="module")
def test_data() -> Dict[str, Any]:
    """Provide test data for login tests.
    
    In a real-world scenario, this would be loaded from an external data source.
    """
    return {
        "valid_username": "testuser@example.com",
        "valid_password": "securepassword123",
        "valid_email": "testuser@example.com",
        "invalid_username": "nonexistent@example.com",
        "invalid_password": "wrongpassword",
    }
