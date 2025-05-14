"""Test utilities and base test classes for mobile test automation."""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast, Generator

import allure
import pytest
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webelement import WebElement

from config.config import ANDROID_CAPS, IOS_CAPS, APPIUM_URL, SCREENSHOT_DIR, SECURE_STORAGE_PATH
from pages.base_page import BasePage, Locator, LocatorType

# Type variables for better type hints
T = TypeVar('T', bound='TestBase')

# Configure logger
logger: logging.Logger = logging.getLogger(__name__)


def get_driver(platform: str = 'android') -> WebDriver:
    """Initialize and return an Appium WebDriver instance based on the platform.
    
    This function initializes a WebDriver instance with the appropriate capabilities
    for the specified platform (Android or iOS). It includes error handling and
    logging for better debugging.
    
    Args:
        platform: The target platform ('android' or 'ios'). Defaults to 'android'.
        
    Returns:
        WebDriver: Initialized Appium WebDriver instance.
        
    Raises:
        ValueError: If an unsupported platform is specified.
        WebDriverException: If WebDriver initialization fails.
        
    Example:
        >>> driver = get_driver('android')
    """
    platform = platform.lower()
    if platform not in ('android', 'ios'):
        error_msg = f"Unsupported platform: {platform}. Must be 'android' or 'ios'"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    capabilities = ANDROID_CAPS if platform == 'android' else IOS_CAPS
    logger.info("Initializing %s driver with capabilities: %s", platform.upper(), capabilities)
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            driver = webdriver.Remote(
                command_executor=APPIUM_URL,
                desired_capabilities=capabilities,
                keep_alive=True
            )
            
            # Verify the session was created successfully
            if not driver.session_id:
                raise WebDriverException("Failed to create WebDriver session: No session ID returned")
                
            logger.info("Successfully initialized %s driver (attempt %d/%d)", 
                      platform.upper(), attempt, max_retries)
            return driver
            
        except Exception as e:
            if attempt == max_retries:
                error_msg = f"Failed to initialize {platform.upper()} driver after {max_retries} attempts: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise WebDriverException(error_msg) from e
                
            logger.warning("Attempt %d/%d failed: %s. Retrying in %d seconds...",
                        attempt, max_retries, str(e), retry_delay)
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Create test report and attach screenshots and logs on test failure or success.
    
    This hook is called for each test phase (setup, call, teardown) and captures
    screenshots, page source, and logs when a test fails. It also handles cleanup
    of test artifacts.
    
    Args:
        item: The test item being executed.
        call: The call information for the test phase.
    """
    outcome = yield
    report = outcome.get_result()
    
    # Only process failed tests or tests with errors
    if report.failed or report.when == 'teardown':
        driver = item.funcargs.get('driver')
        if not driver:
            return
            
        test_name = report.nodeid.replace("::", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Create a subdirectory for this test's artifacts
            test_artifacts_dir = Path(SCREENSHOT_DIR) / f"{test_name}_{timestamp}"
            test_artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            # Take screenshot
            screenshot_path = test_artifacts_dir / f"{report.when}_screenshot.png"
            try:
                driver.save_screenshot(str(screenshot_path))
                allure.attach.file(
                    str(screenshot_path),
                    name=f"{report.when}_screenshot",
                    attachment_type=allure.attachment_type.PNG,
                    extension=".png"
                )
            except Exception as e:
                logger.warning("Failed to capture screenshot: %s", str(e))
            
            # Save page source
            page_source_path = test_artifacts_dir / f"{report.when}_page_source.xml"
            try:
                page_source = driver.page_source
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                allure.attach(
                    page_source,
                    name=f"{report.when}_page_source",
                    attachment_type=allure.attachment_type.XML
                )
            except Exception as e:
                logger.warning("Failed to capture page source: %s", str(e))
            
            # Capture logs if available
            try:
                log_types = driver.log_types
                for log_type in log_types:
                    try:
                        log = driver.get_log(log_type)
                        if log:
                            log_path = test_artifacts_dir / f"{report.when}_{log_type}_log.json"
                            with open(log_path, 'w', encoding='utf-8') as f:
                                json.dump(log, f, indent=2)
                            allure.attach.file(
                                str(log_path),
                                name=f"{report.when}_{log_type}_log",
                                attachment_type=allure.attachment_type.JSON
                            )
                    except Exception as e:
                        logger.warning("Failed to capture %s logs: %s", log_type, str(e))
                        
        except Exception as e:
            logger.error("Error in pytest_runtest_makereport: %s", str(e), exc_info=True)

class TestBase:
    """Base test class with common setup and teardown methods.
    
    This class provides a foundation for all test classes, handling WebDriver
    initialization, test environment setup, and cleanup. It also includes
    common test utilities and assertions.
    
    Attributes:
        driver: The WebDriver instance for the test.
        base_page: An instance of BasePage for common page interactions.
        platform: The target platform ('android' or 'ios').
    """
    
    driver: WebDriver
    base_page: BasePage
    platform: str = 'android'
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, request: pytest.FixtureRequest) -> Generator[None, None, None]:
        """Setup and teardown for each test method.
        
        This fixture:
        1. Initializes the WebDriver for the specified platform
        2. Sets up the BasePage instance
        3. Makes the driver and page objects available to test methods
        4. Handles cleanup after the test completes
        
        Args:
            request: The pytest request object providing access to test context.
            
        Yields:
            None: Control is yielded back to the test function.
        """
        # Get platform from test class or use default
        platform = getattr(request.cls, 'platform', 'android')
        self.platform = platform
        
        # Initialize WebDriver and BasePage
        self.driver = get_driver(platform)
        self.base_page = BasePage(self.driver)
        
        # Make driver and page available to test methods
        request.cls.driver = self.driver
        request.cls.base_page = self.base_page
        
        # Setup complete, run the test
        yield
        
        # Teardown
        self._teardown()
    
    def _teardown(self) -> None:
        """Clean up resources after test execution."""
        try:
            if hasattr(self, 'driver') and self.driver is not None:
                # Take final screenshot if test failed
                if hasattr(self, '_test_outcome') and self._test_outcome.failed:
                    self.take_screenshot("test_failure")
                
                # Quit the driver
                try:
                    self.driver.quit()
                    logger.info("WebDriver session terminated successfully")
                except Exception as e:
                    logger.error("Error quitting WebDriver: %s", str(e))
                finally:
                    self.driver = None  # type: ignore
                    self.base_page = None  # type: ignore
        except Exception as e:
            logger.error("Error during test teardown: %s", str(e), exc_info=True)
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo) -> None:
        """Store test outcome for teardown handling."""
        outcome = yield
        self._test_outcome = outcome.get_result()
    
    def take_screenshot(self, name: str) -> str:
        """Take a screenshot and attach it to the Allure report.
        
        Args:
            name: Base name for the screenshot file (without extension).
            
        Returns:
            str: Path to the saved screenshot file.
        """
        if not hasattr(self, 'driver') or not self.driver:
            logger.warning("Cannot take screenshot: WebDriver not initialized")
            return ""
            
        try:
            return self.base_page.take_screenshot(name, subfolder="screenshots")
        except Exception as e:
            logger.error("Failed to take screenshot: %s", str(e))
            return ""
    
    def log_step(self, step_name: str) -> None:
        """Log a step in the Allure report.
        
        Args:
            step_name: The name or description of the step.
        """
        with allure.step(step_name):
            logger.info(step_name)
    
    def wait_for_element(
        self,
        locator: Union[Locator, LocatorType],
        timeout: Optional[int] = None,
    ) -> WebElement:
        """Wait for an element to be present and return it.
        
        Args:
            locator: The locator for the element to wait for.
            timeout: Maximum time to wait in seconds.
            
        Returns:
            WebElement: The found element.
            
        Raises:
            TimeoutException: If the element is not found within the timeout.
        """
        return self.base_page.wait_for_element_visibility(locator, timeout)
    
    def scroll_to_element(self, element: Union[WebElement, Locator]) -> WebElement:
        """Scroll to the specified element.
        
        Args:
            element: The element or locator to scroll to.
            
        Returns:
            WebElement: The scrolled-to element.
        """
        return self.base_page.scroll_to_element(element)
    
    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int = 200,
    ) -> None:
        """Perform a swipe action.
        
        Args:
            start_x: X coordinate of the start point.
            start_y: Y coordinate of the start point.
            end_x: X coordinate of the end point.
            end_y: Y coordinate of the end point.
            duration: Time in milliseconds for the swipe.
        """
        self.base_page.swipe(start_x, start_y, end_x, end_y, duration)
    
    def take_screenshot(self, name):
        """Take a screenshot and attach it to the Allure report."""
        try:
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
    
    def log_step(self, step_name):
        """Log a step in the Allure report."""
        with allure.step(step_name):
            logger.info(step_name)
    
    def wait_for_element(self, locator, timeout=10):
        """Wait for an element to be present and return it."""
        return self.base_page.wait_for_element_visibility(locator, timeout)
    
    def scroll_to_element(self, element):
        """Scroll to the specified element."""
        self.base_page.scroll_to_element(element)
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=200):
        """Perform swipe action."""
        self.base_page.swipe(start_x, start_y, end_x, end_y, duration)
