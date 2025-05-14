"""Configuration management for the mobile test automation framework.

This module handles loading configuration from environment variables, validating
configuration values, and providing type-safe access to configuration settings.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union, cast, List, Literal

from pydantic import BaseModel, Field, validator, HttpUrl, DirectoryPath, FilePath
from pydantic.types import constr, conint, confloat
from dotenv import load_dotenv

# Configure logger
logger: logging.Logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T', bound='BaseModel')

# Load environment variables from .env file
load_dotenv()


class AppConfig(BaseModel):
    """Application configuration settings."""
    
    apps_dir: DirectoryPath = Field(
        default_factory=lambda: Path(__file__).parent.parent / 'apps',
        description='Base directory for application files',
        env='APPS_DIR'
    )
    
    @property
    def android_apps_dir(self) -> Path:
        """Get the directory for Android apps."""
        return self.apps_dir / 'android'
    
    @property
    def ios_apps_dir(self) -> Path:
        """Get the directory for iOS apps."""
        return self.apps_dir / 'ios'
    
    def find_latest_app(self, platform: str, pattern: str = '*') -> Optional[Path]:
        """Find the most recent app file matching the pattern.
        
        Args:
            platform: 'android' or 'ios'
            pattern: Filename pattern to match (supports glob format)
            
        Returns:
            Path to the latest matching app file, or None if not found
        """
        if platform.lower() == 'android':
            search_dir = self.android_apps_dir
            extensions = ('.apk', '.aab')
        elif platform.lower() == 'ios':
            search_dir = self.ios_apps_dir
            extensions = ('.ipa', '.app', '.zip')
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        if not search_dir.exists():
            logger.warning(f"Apps directory not found: {search_dir}")
            return None
            
        # Find all matching files
        files = []
        for ext in extensions:
            files.extend(search_dir.glob(f"{pattern}{ext}"))
        
        if not files:
            return None
            
        # Return the most recently modified file
        return max(files, key=lambda f: f.stat().st_mtime)


class AppiumConfig(BaseModel):
    """Configuration for Appium server connection."""
    
    host: str = Field(
        default='127.0.0.1',
        description='Hostname or IP address of the Appium server',
        env='APPIUM_HOST'
    )
    
    port: int = Field(
        default=4723,
        description='Port number of the Appium server',
        ge=1,
        le=65535,
        env='APPIUM_PORT'
    )
    
    base_path: str = Field(
        default='wd/hub',
        description='Base path for the Appium server',
        env='APPIUM_BASE_PATH'
    )
    
    @property
    def url(self) -> str:
        """Get the full Appium server URL."""
        return f'http://{self.host}:{self.port}/{self.base_path}'
    
    @validator('host')
    def validate_host(cls, v: str) -> str:
        """Validate the hostname or IP address."""
        if not v:
            raise ValueError('Appium host cannot be empty')
        return v.strip()


class AndroidCapabilities(BaseModel):
    """Capabilities for Android devices."""
    
    platform_name: Literal['Android'] = Field(
        default='Android',
        description='The mobile OS platform',
        env='ANDROID_PLATFORM_NAME'
    )
    
    automation_name: str = Field(
        default='UiAutomator2',
        description='Automation engine to use',
        env='ANDROID_AUTOMATION_NAME'
    )
    
    device_name: str = Field(
        default='Android Emulator',
        description='Name of the mobile device or emulator',
        env='ANDROID_DEVICE_NAME'
    )
    
    platform_version: str = Field(
        default='13.0',
        description='Version of the Android platform',
        pattern=r'^\d+(\.\d+)*$',
        env='ANDROID_PLATFORM_VERSION'
    )
    
    app: Optional[FilePath] = Field(
        default=None,
        description='Path to the Android application file (.apk or .aab). '
                   'If not provided, will look for the latest .apk in the apps/android directory.',
        env='ANDROID_APP_PATH'
    )
    
    app_package: str = Field(
        default='com.saucelabs.mydemoapp.rn',
        description='Package name of the Android app',
        pattern=r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*$',
        env='ANDROID_APP_PACKAGE'
    )
    
    app_activity: str = Field(
        default='.MainActivity',
        description='Activity name to launch',
        env='ANDROID_APP_ACTIVITY'
    )
    
    @validator('app', pre=True, always=True)
    def set_default_android_app(cls, v, values, **kwargs):
        """Set default Android app path if not provided."""
        if v is not None:
            return v
            
        # Try to find the latest APK in the apps directory
        apps_dir = Path(__file__).parent.parent / 'apps' / 'android'
        if apps_dir.exists():
            apk_files = list(apps_dir.glob('*.apk'))
            if apk_files:
                latest_apk = max(apk_files, key=lambda x: x.stat().st_mtime)
                logger.info(f"Using latest APK: {latest_apk}")
                return str(latest_apk)
        
        return None
    
    no_reset: bool = Field(
        default=False,
        description='Do not reset app state before this session',
        env='ANDROID_NO_RESET'
    )
    
    full_reset: bool = Field(
        default=False,
        description='Perform a complete reset before session starts',
        env='ANDROID_FULL_RESET'
    )
    
    auto_grant_permissions: bool = Field(
        default=True,
        description='Automatically grant all permissions',
        env='ANDROID_AUTO_GRANT_PERMISSIONS'
    )
    
    new_command_timeout: int = Field(
        default=300,
        description='Timeout in seconds for waiting for a new command',
        ge=0,
        env='ANDROID_NEW_COMMAND_TIMEOUT'
    )
    
    auto_accept_alerts: bool = Field(
        default=True,
        description='Accept all iOS alerts automatically',
        env='ANDROID_AUTO_ACCEPT_ALERTS'
    )
    
    auto_dismiss_alerts: bool = Field(
        default=True,
        description='Dismiss all iOS alerts automatically',
        env='ANDROID_AUTO_DISMISS_ALERTS'
    )
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """Get capabilities as a dictionary."""
        return self.dict(by_alias=True, exclude_none=True)


class IOSCapabilities(BaseModel):
    """Capabilities for iOS devices."""
    
    platform_name: Literal['iOS'] = Field(
        default='iOS',
        description='The mobile OS platform',
        env='IOS_PLATFORM_NAME'
    )
    
    automation_name: str = Field(
        default='XCUITest',
        description='Automation engine to use',
        env='IOS_AUTOMATION_NAME'
    )
    
    device_name: str = Field(
        default='iPhone 14',
        description='Name of the iOS device or simulator',
        env='IOS_DEVICE_NAME'
    )
    
    platform_version: str = Field(
        default='16.4',
        description='Version of the iOS platform',
        pattern=r'^\d+(\.\d+)*$',
        env='IOS_PLATFORM_VERSION'
    )
    
    app: Optional[FilePath] = Field(
        default=None,
        description='Path to the iOS application file (.app, .ipa, or .app.zip). '
                   'If not provided, will look for the latest .ipa in the apps/ios directory.',
        env='IOS_APP_PATH'
    )
    
    bundle_id: str = Field(
        default='com.saucelabs.mydemoapp.rn',
        description='Bundle ID of the iOS app',
        env='IOS_BUNDLE_ID'
    )
    
    @validator('app', pre=True, always=True)
    def set_default_ios_app(cls, v, values, **kwargs):
        """Set default iOS app path if not provided."""
        if v is not None:
            return v
            
        # Try to find the latest IPA in the apps directory
        apps_dir = Path(__file__).parent.parent / 'apps' / 'ios'
        if apps_dir.exists():
            ipa_files = list(apps_dir.glob('*.ipa'))
            if ipa_files:
                latest_ipa = max(ipa_files, key=lambda x: x.stat().st_mtime)
                logger.info(f"Using latest IPA: {latest_ipa}")
                return str(latest_ipa)
        
        return None
    
    no_reset: bool = Field(
        default=False,
        description='Do not reset app state before this session',
        env='IOS_NO_RESET'
    )
    
    full_reset: bool = Field(
        default=False,
        description='Perform a complete reset before session starts',
        env='IOS_FULL_RESET'
    )
    
    auto_accept_alerts: bool = Field(
        default=True,
        description='Accept all iOS alerts automatically',
        env='IOS_AUTO_ACCEPT_ALERTS'
    )
    
    new_command_timeout: int = Field(
        default=300,
        description='Timeout in seconds for waiting for a new command',
        ge=0,
        env='IOS_NEW_COMMAND_TIMEOUT'
    )
    
    wda_launch_timeout: int = Field(
        default=60000,
        description='Time to wait for WebDriverAgent to be pingable',
        ge=0,
        env='IOS_WDA_LAUNCH_TIMEOUT'
    )
    
    wda_connection_timeout: int = Field(
        default=60000,
        description='Timeout for waiting for a response from WebDriverAgent',
        ge=0,
        env='IOS_WDA_CONNECTION_TIMEOUT'
    )
    
    @property
    def capabilities(self) -> Dict[str, Any]:
        """Get capabilities as a dictionary."""
        return self.dict(by_alias=True, exclude_none=True)


class TestConfig(BaseModel):
    """Test execution configuration."""
    
    wait_time: int = Field(
        default=10,
        description='Default explicit wait time in seconds',
        ge=0,
        env='WAIT_TIME'
    )
    
    implicit_wait: int = Field(
        default=10,
        description='Default implicit wait time in seconds',
        ge=0,
        env='IMPLICIT_WAIT'
    )
    
    screenshot_dir: DirectoryPath = Field(
        default_factory=lambda: Path(__file__).parent.parent / 'screenshots',
        description='Directory to save screenshots',
        env='SCREENSHOT_DIR'
    )
    
    secure_storage_path: DirectoryPath = Field(
        default_factory=lambda: Path(__file__).parent.parent / 'secure',
        description='Directory for secure storage',
        env='SECURE_STORAGE_PATH'
    )
    
    log_level: str = Field(
        default='INFO',
        description='Logging level',
        pattern=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$',
        env='LOG_LEVEL'
    )
    
    max_retries: int = Field(
        default=3,
        description='Maximum number of retries for flaky tests',
        ge=0,
        env='MAX_RETRIES'
    )
    
    headless: bool = Field(
        default=False,
        description='Run tests in headless mode if supported',
        env='HEADLESS'
    )
    
    def ensure_directories_exist(self) -> None:
        """Ensure all required directories exist."""
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.secure_storage_path.mkdir(parents=True, exist_ok=True)
        # Set secure permissions for sensitive directories
        self.secure_storage_path.chmod(0o700)


class Config(BaseModel):
    """Main configuration class for the test framework."""
    
    app: AppConfig = Field(default_factory=AppConfig)
    appium: AppiumConfig = Field(default_factory=AppiumConfig)
    android: AndroidCapabilities = Field(default_factory=AndroidCapabilities)
    ios: IOSCapabilities = Field(default_factory=IOSCapabilities)
    test: TestConfig = Field(default_factory=TestConfig)
    
    @classmethod
    def from_env(cls: Type[T]) -> T:
        """Load configuration from environment variables."""
        return cls()
    
    def validate_configuration(self) -> None:
        """Validate the configuration and ensure all required settings are present."""
        # Ensure apps directory exists
        if not self.app.apps_dir.exists():
            logger.warning(f"Apps directory not found: {self.app.apps_dir}")
            self.app.apps_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure platform-specific app directories exist
        for platform_dir in [self.app.android_apps_dir, self.app.ios_apps_dir]:
            if not platform_dir.exists():
                logger.info(f"Creating directory: {platform_dir}")
                platform_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if app path is provided for the target platform
        if hasattr(self, 'platform') and self.platform:
            if self.platform.lower() == 'android':
                if not self.android.app:
                    # Try to find the latest APK
                    latest_apk = self.app.find_latest_app('android')
                    if latest_apk:
                        self.android.app = latest_apk
                    else:
                        raise ValueError(
                            "Android app path is required and no APK found in apps/android directory. "
                            "Set ANDROID_APP_PATH environment variable or add an APK to the apps/android directory."
                        )
                logger.info(f"Using Android app: {self.android.app}")
                
            elif self.platform.lower() == 'ios':
                if not self.ios.app:
                    # Try to find the latest IPA
                    latest_ipa = self.app.find_latest_app('ios')
                    if latest_ipa:
                        self.ios.app = latest_ipa
                    else:
                        raise ValueError(
                            "iOS app path is required and no IPA found in apps/ios directory. "
                            "Set IOS_APP_PATH environment variable or add an IPA to the apps/ios directory."
                        )
                logger.info(f"Using iOS app: {self.ios.app}")
        
        # Ensure required Android settings are present when Android is used
        if self.android.app and not self.android.app.exists():
            logger.warning("Android app path does not exist: %s", self.android.app)
        
        # Ensure required iOS settings are present when iOS is used
        if self.ios.app and not self.ios.app.exists():
            logger.warning("iOS app path does not exist: %s", self.ios.app)
        
        # Ensure directories exist
        self.test.ensure_directories_exist()


# Create and validate the global configuration
config = Config.from_env()
config.validate_configuration()

# Export commonly used configuration values for backward compatibility
APPIUM_URL = config.appium.url
ANDROID_CAPS = config.android.capabilities
IOS_CAPS = config.ios.capabilities
WAIT_TIME = config.test.wait_time
IMPLICIT_WAIT = config.test.implicit_wait
SCREENSHOT_DIR = str(config.test.screenshot_dir)
SECURE_STORAGE_PATH = str(config.test.secure_storage_path)

# Log the configuration
logger.debug("Appium URL: %s", APPIUM_URL)
logger.debug("Android capabilities: %s", ANDROID_CAPS)
logger.debug("iOS capabilities: %s", IOS_CAPS)
logger.debug("Test configuration: %s", config.test.dict())
