"""Configuration and fixtures for pytest with comprehensive Appium plugin support.

This module configures and provides fixtures for the test suite with support for various Appium plugins:
1. Appium Image Comparison Plugin - For visual testing and image comparison
2. Appium Gestures Plugin - For advanced gesture support
3. Appium Settings Plugin - For device settings management
4. Appium Execute Driver Plugin - For parallel test execution
5. Appium WebDriverAgent Plugin - For iOS-specific automation
6. Appium UIAutomator2 Plugin - For Android UI automation
7. Appium XCUITest Plugin - For iOS UI automation
8. Appium Flutter Finder - For Flutter app testing
9. Appium Espresso Driver - For Android Espresso testing
10. Appium YouiEngine Driver - For Youi.tv app testing
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import allure
import pytest
import yaml
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.remote.webdriver import WebDriver

from config.config_manager import config_manager
from config import config  # Keep original config import for backward compatibility
from utilities.appium_manager import AppiumManager, get_available_devices
from utilities.test_utils import TestBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Get logger for this module
logger = logging.getLogger(__name__)


def pytest_addoption(parser: Parser) -> None:
    """Add custom command line options."""
    # Platform and app configuration
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        choices=["android", "ios"],
        help="Platform to run tests on: android or ios"
    )
    parser.addoption(
        "--suite",
        action="store",
        default="all",
        choices=["all", "sanity", "smoke", "regression"],
        help="Test suite to run: all, sanity, smoke, or regression"
    )
    parser.addoption(
        "--device-count",
        type=int,
        default=4,
        help="Number of parallel devices to run tests on"
    )
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to the application file"
    )
    parser.addoption(
        "--appium-host",
        action="store",
        default="127.0.0.1",
        help="Appium server host address"
    )
    parser.addoption(
        "--appium-port",
        type=int,
        default=4723,
        help="Appium server port"
    )
    parser.addoption(
        "--device-udid",
        action="store",
        default=None,
        help="Device UDID to run tests on"
    )
    parser.addoption(
        "--install-plugins",
        action="store_true",
        default=False,
        help="Install required Appium plugins"
    )
    parser.addoption(
        "--device-name",
        action="store",
        default=None,
        help="Name of the device or emulator to use"
    )


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom settings."""
    # Add environment info to the HTML report
    config._metadata["Appium Server"] = config.appium.url
    config._metadata["Platform"] = config.platform
    config._metadata["Test Directory"] = str(Path(__file__).parent)
    
    # Configure Allure environment properties
    if hasattr(config, "_metadata") and config._metadata:
        for key, value in config._metadata.items():
            if key in ("Python", "Platform", "Packages"):
                continue
            # Add to Allure environment
            allure.environment(**{key: value})


@pytest.fixture(scope="session")
def appium_manager(request) -> Generator[AppiumManager, None, None]:
    """Fixture to manage Appium server and plugins."""
    manager = AppiumManager()
    
    # Install required plugins if requested
    if request.config.getoption("--install-plugins"):
        for plugin in ["appium-device-farm", "appium-wda"]:
            try:
                manager.install_plugin(plugin)
            except Exception as e:
                logger.warning(f"Failed to install plugin {plugin}: {e}")
    
    # Start Appium server
    manager.start_appium_server(
        host=request.config.getoption("--appium-host"),
        port=request.config.getoption("--appium-port"),
        log_file=config.LOGS_DIR / "appium_server.log",
        allow_insecure='chromedriver_autodownload',
        relaxed_security=True
    )
    
    yield manager
    
    # Cleanup will be handled by the manager's __exit__


@pytest.fixture(scope="function")
def driver(
    request: FixtureRequest,
    appium_manager: AppiumManager
) -> Generator[WebDriver, None, None]:
    """Fixture to provide a WebDriver instance with Appium plugin support.
    
    This fixture initializes the WebDriver with capabilities loaded from external
    configuration files, supporting various Appium plugins.
    
    Returns:
        WebDriver: Configured WebDriver instance with plugin support
    """
    platform = request.config.getoption("--platform")
    device_udid = request.config.getoption("--device-udid")
    
    try:
        # Load capabilities from configuration files
        capabilities = config_manager.get_platform_capabilities(platform)
        
        # Add app path from config if available
        if platform == "android" and hasattr(config, 'android') and hasattr(config.android, 'app'):
            capabilities["app"] = str(config.android.app)
        elif hasattr(config, 'ios') and hasattr(config.ios, 'app'):
            capabilities["app"] = str(config.ios.app)
            
        # Add any additional capabilities from the config module
        if hasattr(config, platform) and hasattr(getattr(config, platform), 'capabilities'):
            capabilities.update(getattr(getattr(config, platform), 'capabilities'))
            
        # Set device UDID if provided
        if device_udid:
            capabilities["udid"] = device_udid
            
        logger.info(f"Initializing {platform.upper()} driver with capabilities: {json.dumps(capabilities, indent=2)}")
    
        # Initialize driver with all capabilities
        driver = appium_manager.create_driver(
            platform_name=platform,
            device_name=device_udid or f"{platform.capitalize()} Device",
            **capabilities
        )
    
    # Configure timeouts
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)
    
    # Initialize plugin-specific features
    try:
        # Image Comparison Plugin - Verify it's working
        driver.execute_script('mobile: isFeatureSupported', {'feature': 'compareImages'})
        
        # Gestures Plugin - Enable advanced touch actions
        driver.execute_script('mobile: touchAction', {'action': 'longPress', 'x': 100, 'y': 200, 'duration': 1000})
        
        # Settings Plugin - Configure default settings
        driver.update_settings({
            'ignoreUnimportantViews': True,
            'waitForIdleTimeout': 100,
            'waitForSelectorTimeout': 10000
        })
        
        # Execute Driver Plugin - Verify it's available
        driver.execute_script('mobile: executeDriver', {
            'script': 'mobile: getDeviceInfo',
            'type': 'webdriverio'
        })
        
    except Exception as e:
        logger.warning(f"Some Appium plugins might not be available: {str(e)}")
        raise
    
    # Add finalizer to ensure proper cleanup
    def cleanup():
        try:
            # Take screenshot on test failure
            if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
                screenshot = driver.get_screenshot_as_base64()
                allure.attach(
                    screenshot,
                    name=f"screenshot_{request.node.name}",
                    attachment_type=allure.attachment_type.PNG
                )
            
            # Stop the driver through the manager
            appium_manager.stop_driver(driver)
            
        except Exception as e:
            logger.error(f"Error during driver cleanup: {str(e)}")
    
    request.addfinalizer(cleanup)
    
    return driver


@pytest.fixture(scope="function")
def login_page(driver: WebDriver) -> Any:
    """Fixture to provide a LoginPage instance for each test."""
    from pages.login_page import LoginPage
    return LoginPage(driver)


@pytest.fixture(scope="function")
def test_data() -> Dict[str, Any]:
    """Fixture to provide test data for tests."""
    return {
        "valid_username": "testuser@example.com",
        "valid_password": "securepassword123",
        "valid_email": "testuser@example.com",
        "invalid_username": "nonexistent@example.com",
        "invalid_password": "wrongpassword",
    }


def pytest_exception_interact(
    node: Item,
    call: CallInfo,
    report: Any
) -> None:
    """Handle test exceptions and take screenshots."""
    if report.failed:
        # Get the test instance to access driver
        test_instance = node.instance if hasattr(node, 'instance') else None
        if test_instance and hasattr(test_instance, 'driver'):
            try:
                # Take screenshot on failure
                screenshot_path = os.path.join(
                    config.test.screenshot_dir,
                    f"failure_{node.name}.png"
                )
                test_instance.driver.save_screenshot(screenshot_path)
                
                # Attach to Allure report
                allure.attach.file(
                    screenshot_path,
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
                
                # Log page source for debugging
                page_source = test_instance.driver.page_source
                page_source_path = os.path.join(
                    config.test.screenshot_dir,
                    f"failure_{node.name}_page_source.xml"
                )
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                logger.error(f"Test failed. Screenshot saved to: {screenshot_path}")
                logger.error(f"Page source saved to: {page_source_path}")
                
            except Exception as e:
                logger.error(f"Failed to capture failure artifacts: {e}")


def pytest_collection_modifyitems(
    config: Config,
    items: List[Item]
) -> None:
    """Modify test items during collection."""
    # Add custom markers
    for item in items:
        # Add "web" marker to all tests by default
        if not any(marker.name == "web" for marker in item.own_markers):
            item.add_marker(pytest.mark.web)


# Add custom markers
def pytest_configure(config: Config) -> None:
    """Register custom markers and configure test environment."""
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers",
        "sanity: mark test as sanity test"
    )
    config.addinivalue_line(
        "markers",
        "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers",
        "android: mark test as android specific"
    )
    config.addinivalue_line(
        "markers",
        "ios: mark test as ios specific"
    )
    config.addinivalue_line(
        "markers",
        "wip: work in progress - do not run in CI"
    )
    
    # Set parallel execution settings
    if config.getoption("numprocesses") is None:
        device_count = config.getoption("--device-count")
        config.option.numprocesses = device_count
        logger.info(f"Running tests on {device_count} parallel devices")
    
    # Create necessary directories
    for directory in [config.LOGS_DIR, config.REPORTS_DIR, config.SCREENSHOTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config.LOGS_DIR / 'test_execution.log')
        ]
    )
