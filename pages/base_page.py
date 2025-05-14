"""Base page class with common functionality for all page objects."""

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import action_builder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as RemoteWebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Type variables for better type hints
T = TypeVar('T', bound='BasePage')
LocatorType = Tuple[By, str]
ElementType = Union[WebElement, RemoteWebElement]

# Configure logger
logger: logging.Logger = logging.getLogger(__name__)


class Locator:
    """Wrapper for locator strategies and values with self-healing capabilities.
    
    Attributes:
        by: Locator strategy (e.g., By.ID, By.XPATH)
        value: Locator value
        name: Human-readable name for the locator
        alternatives: List of alternative locators to try if primary fails
    """
    
    def __init__(
        self,
        by: By,
        value: str,
        name: Optional[str] = None,
        alternatives: Optional[List[LocatorType]] = None,
    ) -> None:
        """Initialize Locator with strategy, value, and optional name/alternatives."""
        self.by: By = by
        self.value: str = value
        self.name: str = name or f"{by}={value}"
        self.alternatives: List[LocatorType] = alternatives or []
    
    def __str__(self) -> str:
        """Return string representation of the locator."""
        return self.name
    
    def to_tuple(self) -> LocatorType:
        """Convert locator to (by, value) tuple."""
        return (self.by, self.value)


class BasePage:
    """Base page object with self-healing locators and smart wait functionality.
    
    This class provides common functionality for all page objects, including:
    - Smart element location with self-healing capabilities
    - Explicit and implicit waits
    - Common UI interactions (click, type, swipe, etc.)
    - Screenshot capture
    - Platform-specific handling
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """Initialize base page with WebDriver instance.
        
        Args:
            driver: WebDriver instance for browser/app interaction
        """
        self.driver: WebDriver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, 30)
        self.implicit_wait: int = 10
        self.driver.implicitly_wait(self.implicit_wait)
        self._verify_page()
    
    def _verify_page(self) -> None:
        """Verify that the page has been loaded correctly.
        
        Subclasses should override this method to implement page-specific
        verification logic.
        """
        pass
    
    def find_element(
        self,
        locator: Union[Locator, LocatorType],
        timeout: Optional[int] = None,
        check_visibility: bool = True,
        check_clickable: bool = False,
    ) -> WebElement:
        """Find an element with self-healing capabilities.
        
        Args:
            locator: Locator object or tuple of (by, value)
            timeout: Maximum time to wait for the element (in seconds)
            check_visibility: If True, wait for element to be visible
            check_clickable: If True, wait for element to be clickable
            
        Returns:
            WebElement: The found element
            
        Raises:
            NoSuchElementException: If element is not found after all attempts
            TimeoutException: If element is not found within the specified timeout
            ElementNotInteractableException: If element is not interactable when check_clickable is True
        """
        if not isinstance(locator, Locator):
            by, value = locator
            locator = Locator(by, value)
        
        timeout = timeout or self.implicit_wait
        wait = WebDriverWait(self.driver, timeout)
        
        # Try the primary locator first, then any alternatives
        locators_to_try = [locator.to_tuple()] + locator.alternatives
        
        last_error: Optional[Exception] = None
        
        for by, value in locators_to_try:
            try:
                logger.debug("Attempting to find element: %s=%s", by, value)
                
                # Always check for presence first
                element = wait.until(
                    EC.presence_of_element_located((by, value)),
                    f"Element {locator} not found with {by}={value}"
                )
                
                # Additional checks if requested
                if check_visibility:
                    element = wait.until(
                        EC.visibility_of(element),
                        f"Element {locator} not visible with {by}={value}"
                    )
                
                if check_clickable:
                    element = wait.until(
                        EC.element_to_be_clickable((by, value)),
                        f"Element {locator} not clickable with {by}={value}"
                    )
                
                logger.debug("Successfully found element: %s", locator)
                return element
                
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                last_error = e
                logger.warning("Element not found with %s=%s: %s", by, value, str(e))
                if (by, value) == locators_to_try[-1]:  # Last attempt
                    logger.error("All locator strategies failed for %s", locator)
                    if isinstance(last_error, NoSuchElementException):
                        raise NoSuchElementException(
                            f"Could not find element {locator} with any strategy"
                        ) from last_error
                    raise TimeoutException(
                        f"Timed out waiting for element {locator} to be present"
                    ) from last_error
                continue
        
        # This should never be reached due to the raise in the loop
        raise NoSuchElementException(f"Failed to find element {locator}")
    
    def wait_for_page_load(self, timeout: int = 30) -> None:
        """Wait for the page to be fully loaded.
        
        This method waits for the document.readyState to be 'complete' and for any
        pending AJAX requests to finish.
        
        Args:
            timeout: Maximum time in seconds to wait for page load
            
        Raises:
            TimeoutException: If the page does not load within the specified timeout
        """
        try:
            # Wait for document.readyState to be 'complete'
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete',
                f"Page did not load within {timeout} seconds"
            )
            
            # Additional check for jQuery AJAX requests if jQuery is used
            try:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script('return (typeof jQuery === "undefined") || jQuery.active === 0'),
                    f"jQuery AJAX requests did not complete within {timeout} seconds"
                )
            except Exception as e:
                logger.warning("jQuery check failed or not applicable: %s", str(e))
            
            logger.info("Page load completed successfully")
            
        except TimeoutException as e:
            logger.error("Page load timed out after %s seconds: %s", timeout, str(e))
            self.take_screenshot("page_load_timeout")
            raise
        except Exception as e:
            logger.error("Error during page load: %s", str(e), exc_info=True)
            self.take_screenshot("page_load_error")
            raise
    
    def take_screenshot(self, filename: str, subfolder: Optional[str] = None) -> str:
        """Take a screenshot and save it to the screenshots directory.
        
        Args:
            filename: Base name for the screenshot file (without extension)
            subfolder: Optional subfolder within the screenshots directory
            
        Returns:
            str: Full path to the saved screenshot
            
        Raises:
            RuntimeError: If screenshot capture fails
        """
        try:
            # Create filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.png".replace(" ", "_")
            
            # Determine the base directory for screenshots
            base_dir = Path(__file__).parent.parent / "screenshots"
            
            # Add subfolder if specified
            if subfolder:
                screenshot_dir = base_dir / subfolder
            else:
                screenshot_dir = base_dir
            
            # Ensure directory exists
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Create full filepath
            filepath = screenshot_dir / safe_filename
            
            # Take and save screenshot
            self.driver.save_screenshot(str(filepath))
            
            logger.info("Screenshot saved to %s", filepath)
            return str(filepath)
            
        except Exception as e:
            error_msg = f"Failed to take screenshot: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def get_platform(self) -> str:
        """Get the current platform name in lowercase (e.g., 'android', 'ios').
        
        Returns:
            str: The platform name in lowercase
            
        Raises:
            ValueError: If platform name cannot be determined
        """
        try:
            platform = self.driver.desired_capabilities.get('platformName')
            if not platform:
                raise ValueError("Platform name not found in desired capabilities")
            return str(platform).lower()
        except Exception as e:
            error_msg = f"Failed to determine platform: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
    
    def is_android(self) -> bool:
        """Check if the current platform is Android.
        
        Returns:
            bool: True if the platform is Android, False otherwise
        """
        try:
            return self.get_platform() == 'android'
        except ValueError:
            return False
    
    def is_ios(self) -> bool:
        """Check if the current platform is iOS.
        
        Returns:
            bool: True if the platform is iOS, False otherwise
        """
        try:
            return self.get_platform() in ('ios', 'iphone', 'ipad')
        except ValueError:
            return False
    
    def scroll_to_element(
        self,
        element: Union[WebElement, Locator],
        timeout: Optional[int] = None,
        max_swipes: int = 5,
    ) -> WebElement:
        """Scroll to the specified element.
        
        Args:
            element: Either a WebElement or Locator to scroll to
            timeout: Maximum time in seconds to spend scrolling
            max_swipes: Maximum number of swipe attempts
            
        Returns:
            WebElement: The found element
            
        Raises:
            TimeoutException: If element is not found after max_swipes
            NoSuchElementException: If element is not found
        """
        if isinstance(element, Locator):
            # Try to find the element first (may be already visible)
            try:
                return self.find_element(element, timeout=timeout or self.implicit_wait)
            except (NoSuchElementException, TimeoutException):
                pass
                
        # Get window size for scrolling
        window_size = self.driver.get_window_size()
        start_x = window_size['width'] // 2
        start_y = window_size['height'] * 3 // 4
        end_y = window_size['height'] // 4
        
        # Try to find the element with scrolling
        for _ in range(max_swipes):
            try:
                if isinstance(element, WebElement):
                    # If element is stale, re-find it
                    try:
                        element.is_displayed()
                        return element
                    except StaleElementReferenceException:
                        raise NoSuchElementException("Element is no longer attached to the DOM")
                else:
                    # Try to find the element
                    return self.find_element(element, timeout=1)
            except (NoSuchElementException, StaleElementReferenceException):
                # Scroll and try again
                self.swipe(start_x, start_y, start_x, end_y, duration=500)
                time.sleep(0.5)  # Small delay between swipes
        
        # If we get here, element was not found
        raise TimeoutException(
            f"Could not find element after {max_swipes} swipe attempts"
        )
    
    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int = 200,
        element: Optional[WebElement] = None,
    ) -> None:
        """Perform a swipe action from one point to another.
        
        Args:
            start_x: X coordinate of the start point
            start_y: Y coordinate of the start point
            end_x: X coordinate of the end point
            end_y: Y coordinate of the end point
            duration: Time in milliseconds for the swipe (default: 200ms)
            element: Optional element to perform the swipe relative to
            
        Raises:
            ValueError: If coordinates are invalid
        """
        try:
            # Validate coordinates
            if any(not isinstance(coord, (int, float)) for coord in [start_x, start_y, end_x, end_y]):
                raise ValueError("All coordinates must be numbers")
                
            # Get window size for bounds checking
            window_size = self.driver.get_window_size()
            max_x, max_y = window_size['width'], window_size['height']
            
            # Ensure coordinates are within screen bounds
            def clamp(value: float, max_value: int) -> int:
                return max(0, min(int(value), max_value - 1))
            
            start_x = clamp(start_x, max_x)
            start_y = clamp(start_y, max_y)
            end_x = clamp(end_x, max_x)
            end_y = clamp(end_y, max_y)
            
            # Perform the swipe
            action = ActionChains(self.driver)
            
            if element:
                # If an element is provided, perform the action relative to it
                action.w3c_actions = action_builder.ActionBuilder(
                    self.driver,
                    mouse=PointerInput(PointerInput.POINTER_TOUCH, "touch")
                )
                action.w3c_actions.pointer_action.move_to_location(start_x, start_y)
                action.w3c_actions.pointer_action.pointer_down()
                action.w3c_actions.pointer_action.pause(duration / 1000)  # Convert to seconds
                action.w3c_actions.pointer_action.move_to_location(end_x, end_y)
                action.w3c_actions.pointer_action.release()
            else:
                # Standard swipe
                action.w3c_actions = action_builder.ActionBuilder(
                    self.driver,
                    mouse=PointerInput(PointerInput.POINTER_TOUCH, "touch")
                )
                action.w3c_actions.pointer_action.move_to_location(start_x, start_y)
                action.w3c_actions.pointer_action.pointer_down()
                action.w3c_actions.pointer_action.pause(duration / 1000)  # Convert to seconds
                action.w3c_actions.pointer_action.move_to_location(end_x, end_y)
                action.w3c_actions.pointer_action.release()
            
            action.perform()
            
        except Exception as e:
            error_msg = f"Swipe action failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.take_screenshot("swipe_error")
            raise
    
    def wait_for_element_visibility(
        self,
        locator: Union[Locator, LocatorType],
        timeout: Optional[int] = None,
    ) -> WebElement:
        """Wait for an element to be visible in the DOM and on the page.
        
        This is a convenience method that combines finding and waiting for visibility.
        
        Args:
            locator: Locator object or tuple of (by, value)
            timeout: Maximum time in seconds to wait (defaults to implicit wait)
            
        Returns:
            WebElement: The first WebElement once it is visible
            
        Raises:
            TimeoutException: If the element is not visible within the timeout
            NoSuchElementException: If the element is not found in the DOM
        """
        return self.find_element(
            locator=locator,
            timeout=timeout,
            check_visibility=True,
            check_clickable=False
        )
    
    def wait_for_element_clickable(
        self,
        locator: Union[Locator, LocatorType],
        timeout: Optional[int] = None,
    ) -> WebElement:
        """Wait for an element to be visible and clickable.
        
        Args:
            locator: Locator object or tuple of (by, value)
            timeout: Maximum time in seconds to wait (defaults to implicit wait)
            
        Returns:
            WebElement: The first WebElement once it is clickable
            
        Raises:
            TimeoutException: If the element is not clickable within the timeout
            NoSuchElementException: If the element is not found in the DOM
        """
        return self.find_element(
            locator=locator,
            timeout=timeout,
            check_visibility=True,
            check_clickable=True
        )
    
    def click_element(
        self,
        locator: Union[Locator, LocatorType, WebElement],
        timeout: Optional[int] = None,
        scroll_to: bool = True,
    ) -> None:
        """Click an element with retry logic and error handling.
        
        Args:
            locator: Locator, tuple, or WebElement to click
            timeout: Maximum time in seconds to wait for the element
            scroll_to: Whether to scroll to the element before clicking
            
        Raises:
            ElementClickInterceptedException: If the click is intercepted
            ElementNotInteractableException: If the element is not interactable
            TimeoutException: If the element is not found or clickable within timeout
        """
        element = (
            locator
            if isinstance(locator, WebElement)
            else self.wait_for_element_clickable(locator, timeout)
        )
        
        if scroll_to and not self._is_element_in_viewport(element):
            self.scroll_to_element(element)
        
        try:
            element.click()
            logger.debug("Successfully clicked element: %s", element)
        except ElementClickInterceptedException as e:
            error_msg = f"Click intercepted for element {element}"
            logger.error(error_msg, exc_info=True)
            self.take_screenshot("click_intercepted")
            raise ElementClickInterceptedException(error_msg) from e
        except ElementNotInteractableException as e:
            error_msg = f"Element not interactable: {element}"
            logger.error(error_msg, exc_info=True)
            self.take_screenshot("element_not_interactable")
            raise ElementNotInteractableException(error_msg) from e
    
    def _is_element_in_viewport(self, element: WebElement) -> bool:
        """Check if an element is within the viewport.
        
        Args:
            element: WebElement to check
            
        Returns:
            bool: True if the element is in the viewport, False otherwise
        """
        try:
            return self.driver.execute_script(
                """
                var element = arguments[0];
                var rect = element.getBoundingClientRect();
                var windowHeight = window.innerHeight || document.documentElement.clientHeight;
                var windowWidth = window.innerWidth || document.documentElement.clientWidth;
                
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= windowHeight &&
                    rect.right <= windowWidth
                );
                """,
                element
            )
        except Exception as e:
            logger.warning("Failed to check if element is in viewport: %s", str(e))
            return False
