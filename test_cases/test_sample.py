import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from utilities.test_utils import TestBase

# Sample locators
class SampleLocators:
    # Android locators
    ANDROID_SEARCH_BAR = (AppiumBy.ID, 'search_bar')
    ANDROID_SEARCH_BUTTON = (AppiumBy.ID, 'search_button')
    ANDROID_RESULTS = (AppiumBy.ID, 'search_results')
    
    # iOS locators
    IOS_SEARCH_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'Search')
    IOS_SEARCH_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'Search')
    IOS_RESULTS = (AppiumBy.ACCESSIBILITY_ID, 'Results')
    
    @classmethod
    def get_locators(cls, platform):
        """Get platform-specific locators."""
        if platform.lower() == 'android':
            return {
                'search_bar': cls.ANDROID_SEARCH_BAR,
                'search_button': cls.ANDROID_SEARCH_BUTTON,
                'results': cls.ANDROID_RESULTS
            }
        else:
            return {
                'search_bar': cls.IOS_SEARCH_FIELD,
                'search_button': cls.IOS_SEARCH_BUTTON,
                'results': cls.IOS_RESULTS
            }

class TestSample(TestBase):
    """Sample test class demonstrating the framework usage."""
    
    @pytest.fixture(autouse=True)
    def setup_class(self, request):
        """Class level setup."""
        self.locators = SampleLocators.get_locators(self.platform)
    
    @allure.feature('Search')
    @allure.story('Perform search operation')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_functionality(self):
        """Test search functionality."""
        with allure.step("1. Launch the app"):
            self.log_step("App launched successfully")
        
        with allure.step("2. Perform search operation"):
            search_bar = self.wait_for_element(self.locators['search_bar'])
            search_bar.clear()
            search_bar.send_keys("test search")
            
            search_button = self.wait_for_element(self.locators['search_button'])
            search_button.click()
            
            self.log_step("Search operation completed")
        
        with allure.step("3. Verify search results"):
            results = self.wait_for_element(self.locators['results'])
            assert results.is_displayed(), "Search results not displayed"
            self.log_step("Search results verified")
            
            # Take a screenshot of the results
            self.take_screenshot("search_results")
    
    @allure.feature('Navigation')
    @allure.story('Test screen navigation')
    @allure.severity(allure.severity_level.NORMAL)
    def test_navigation(self):
        """Test screen navigation."""
        with allure.step("1. Navigate to different screens"):
            # Example navigation code
            self.log_step("Navigation test started")
            
            # Add your navigation test steps here
            # Example:
            # menu_button = self.wait_for_element((AppiumBy.ID, 'menu_button'))
            # menu_button.click()
            
            self.log_step("Navigation test completed")
            
            # Mark test as passed explicitly
            assert True

# Example of parameterized test for cross-platform testing
@pytest.mark.parametrize('platform', ['android', 'ios'])
class TestCrossPlatform(TestBase):
    """Test class demonstrating cross-platform testing."""
    
    def test_platform_specific_features(self, platform):
        """Test platform-specific features."""
        self.log_step(f"Running test on {platform}")
        
        if platform == 'android':
            # Android specific test steps
            self.log_step("Running Android specific test")
        else:
            # iOS specific test steps
            self.log_step("Running iOS specific test")
        
        # Example assertion
        assert True, f"Test completed on {platform}"
