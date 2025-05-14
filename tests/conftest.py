"""Configuration and fixtures for pytest.

This module contains the configuration and fixtures for the test suite.
It's automatically discovered and used by pytest.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import allure
import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.remote.webdriver import WebDriver

from config import config
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

# Get logger for this module
logger = logging.getLogger(__name__)


def pytest_addoption(parser: Parser) -> None:
    """Add custom command line options."""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        choices=["android", "ios"],
        help="Platform to run tests on: android or ios"
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
    """Fixture to provide a WebDriver instance for each test."""
    platform = request.config.getoption("--platform")
    device_udid = request.config.getoption("--device-udid")
    
    # Get base capabilities based on platform
    if platform == "android":
        capabilities = {
            **config.android.capabilities,
            "app": str(config.android.app) if config.android.app else None,
            "appPackage": "com.saucelabs.mydemoapp.rn",
            "appActivity": ".MainActivity",
            "automationName": "UiAutomator2",
            "platformName": "Android",
            "platformVersion": "13.0",
            "deviceName": "Android Emulator",
            "noReset": True,
            "fullReset": False,
            "autoGrantPermissions": True
        }
    else:  # ios
        capabilities = {
            **config.ios.capabilities,
            "app": str(config.ios.app) if config.ios.app else None,
            "bundleId": "com.saucelabs.mydemoapp.rn",
            "automationName": "XCUITest",
            "platformName": "iOS",
            "platformVersion": "16.4",
            "deviceName": "iPhone 14",
            "noReset": True,
            "fullReset": False,
            "autoAcceptAlerts": True
        }
    
    # Create driver using the manager
    driver = appium_manager.create_driver(
        platform_name=platform,
        device_name=device_udid or (platform.capitalize() + ' Device'),
        **capabilities
    )
    
    # Set implicit wait
    driver.implicitly_wait(10)
    
    # Add finalizer to ensure driver is closed
    request.addfinalizer(lambda: appium_manager.stop_driver(driver))
    
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
    config.addinivalue_line("markers", "android: mark test as Android specific")
    config.addinivalue_line("markers", "ios: mark test as iOS specific")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "device_farm: mark test for device farm execution")
    
    # Create necessary directories
    for directory in [config.LOGS_DIR, config.REPORTS_DIR, config.SCREENSHOTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config.LOGS_DIR / 'test_execution.log')
        ]
    )
