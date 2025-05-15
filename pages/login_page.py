"""Page object for the login screen."""
from typing import Optional, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class LoginPage(BasePage):
    """Page object for the login screen."""
    
    # Locators
    USERNAME_FIELD = Locator(
        by=AppiumBy.ACCESSIBILITY_ID,
        value="username-field",
        name="Username Field"
    )
    PASSWORD_FIELD = Locator(
        by=AppiumBy.ACCESSIBILITY_ID,
        value="password-field",
        name="Password Field"
    )
    LOGIN_BUTTON = Locator(
        by=AppiumBy.ACCESSIBILITY_ID,
        value="login-button",
        name="Login Button"
    )
    ERROR_MESSAGE = Locator(
        by=AppiumBy.ACCESSIBILITY_ID,
        value="error-message",
        name="Error Message"
    )
    
    def __init__(self, driver):
        """Initialize with WebDriver instance."""
        super().__init__(driver)
    
    def _verify_page(self):
        """Verify we're on the login page."""
        self.wait_for_element_visibility(self.USERNAME_FIELD)
        self.wait_for_element_visibility(self.PASSWORD_FIELD)
        self.wait_for_element_visibility(self.LOGIN_BUTTON)
    
    def login(self, username: str, password: str) -> None:
        """
        Attempt to log in with the provided credentials.
        
        Args:
            username: Username to log in with
            password: Password to log in with
        """
        self.enter_text(self.USERNAME_FIELD, username)
        self.enter_text(self.PASSWORD_FIELD, password)
        self.click_element(self.LOGIN_BUTTON)
    
    def get_error_message(self) -> Optional[str]:
        """
        Get the error message if login fails.
        
        Returns:
            Optional[str]: The error message text if present, None otherwise
        """
        try:
            return self.get_element_text(self.ERROR_MESSAGE)
        except:
            return None
    
    def is_error_message_displayed(self) -> bool:
        """
        Check if the error message is displayed.
        
        Returns:
            bool: True if error message is displayed, False otherwise
        """
        try:
            return self.is_element_displayed(self.ERROR_MESSAGE)
        except:
            return False
