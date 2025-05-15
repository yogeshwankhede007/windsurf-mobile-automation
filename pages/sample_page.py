"""
Page object for sample functionality.
"""

import logging
from typing import Dict, Any
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage

# Configure logger
logger = logging.getLogger(__name__)

class SamplePage(BasePage):
    """Page object for sample functionality."""
    
    # Android locators
    ANDROID_SEARCH_BAR = (AppiumBy.ID, 'search_bar')
    ANDROID_SEARCH_BUTTON = (AppiumBy.ID, 'search_button')
    ANDROID_RESULTS = (AppiumBy.ID, 'search_results')
    
    # iOS locators
    IOS_SEARCH_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'Search')
    IOS_SEARCH_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'Search')
    IOS_RESULTS = (AppiumBy.ACCESSIBILITY_ID, 'Results')
    
    def __init__(self, driver):
        """Initialize the SamplePage."""
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
    
    def get_platform_locators(self, platform: str) -> Dict[str, tuple]:
        """Get platform-specific locators.
        
        Args:
            platform: The platform (android/ios)
            
        Returns:
            Dictionary of platform-specific locators
        """
        if platform.lower() == 'android':
            return {
                'search_bar': self.ANDROID_SEARCH_BAR,
                'search_button': self.ANDROID_SEARCH_BUTTON,
                'results': self.ANDROID_RESULTS
            }
        else:
            return {
                'search_bar': self.IOS_SEARCH_FIELD,
                'search_button': self.IOS_SEARCH_BUTTON,
                'results': self.IOS_RESULTS
            }
    
    def perform_search(self, search_text: str) -> None:
        """Perform a search operation.
        
        Args:
            search_text: Text to search for
        """
        locators = self.get_platform_locators(self.driver.platform_name.lower())
        
        # Enter search text
        self.clear_and_type(locators['search_bar'], search_text)
        
        # Click search button
        self.click(locators['search_button'])
        
        # Wait for results
        self.wait_for_element(locators['results'])
