"""Smoke tests for critical app functionality."""
import pytest
import logging
from appium.webdriver.common.appiumby import AppiumBy
from tests.base_test import BaseTest

logger = logging.getLogger(__name__)

class TestAppSmoke(BaseTest):
    """Smoke tests for critical app functionality."""
    
    @pytest.mark.smoke
    @pytest.mark.android
    def test_app_launch_android(self):
        """Test app launch on Android."""
        logger.info("Testing app launch on Android")
        
        # Verify app launches to the login screen
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('username_field')), \
            "Username field not found on login screen"
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('password_field')), \
            "Password field not found on login screen"
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('login_button')), \
            "Login button not found on login screen"
    
    @pytest.mark.smoke
    @pytest.mark.ios
    def test_app_launch_ios(self):
        """Test app launch on iOS."""
        logger.info("Testing app launch on iOS")
        
        # Verify app launches to the login screen
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('username_field')), \
            "Username field not found on login screen"
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('password_field')), \
            "Password field not found on login screen"
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('login_button')), \
            "Login button not found on login screen"
    
    @pytest.mark.smoke
    @pytest.mark.android
    def test_navigation_after_login_android(self):
        """Test basic navigation after successful login on Android."""
        logger.info("Testing navigation after login on Android")
        
        # Perform login
        self.login_page.login(self.valid_username, self.valid_password)
        
        # Verify navigation to home screen
        # Replace with actual home screen element verification
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('home_screen')), \
            "Failed to navigate to home screen after login"
    
    @pytest.mark.smoke
    @pytest.mark.ios
    def test_navigation_after_login_ios(self):
        """Test basic navigation after successful login on iOS."""
        logger.info("Testing navigation after login on iOS")
        
        # Perform login
        self.login_page.login(self.valid_username, self.valid_password)
        
        # Verify navigation to home screen
        # Replace with actual home screen element verification
        assert self.login_page.is_element_displayed(self.login_page.get_platform_locator('home_screen')), \
            "Failed to navigate to home screen after login"
    
    @pytest.mark.smoke
    @pytest.mark.parametrize("platform", ["android", "ios"])
    def test_app_background_foreground(self, platform, request):
        """Test app behavior when sent to background and brought back to foreground."""
        if platform != request.config.getoption("--platform"):
            pytest.skip(f"Skipping {platform} test")
            
        logger.info(f"Testing app background/foreground on {platform}")
        
        # Put app in background
        self.driver.background_app(seconds=2)
        
        # Bring app back to foreground
        self.driver.activate_app(self.driver.current_package)
        
        # Verify app is still on the same screen
        assert self.login_page.is_element_displayed((AppiumBy.ACCESSIBILITY_ID, "username-field")), \
            "App did not return to the login screen after background/foreground"
