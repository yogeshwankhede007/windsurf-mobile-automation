"""
Appium Server and Driver Manager

This module provides functionality to dynamically manage Appium server instances,
drivers, and plugins at runtime. It handles the complete lifecycle including
prerequisite checks, server startup, and cleanup.
"""

import atexit
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from appium.options.common import AppiumOptions
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.webdriver import WebDriver
from loguru import logger


class AppiumManager:
    """Manages Appium server and driver instances with dynamic plugin support."""

    def __init__(self):
        self.appium_service = None
        self.drivers: List[WebDriver] = []
        self.plugins: List[str] = []
        self._ensure_prerequisites()
        atexit.register(self.cleanup)

    def _ensure_prerequisites(self) -> None:
        """Verify all required system dependencies are installed."""
        required_commands = {
            'node': 'Node.js is required. Install from https://nodejs.org/',
            'npm': 'npm is required. It should come with Node.js installation.',
            'appium': 'Appium CLI is required. Install with: npm install -g appium',
            'adb': 'Android Debug Bridge (adb) is required for Android testing.',
            'xcrun': 'Xcode Command Line Tools are required for iOS testing (macOS only).'
        }

        for cmd, error_msg in required_commands.items():
            if not shutil.which(cmd):
                raise EnvironmentError(f"{error_msg} Command not found: {cmd}")

    def install_plugin(self, plugin_name: str) -> None:
        """Install an Appium plugin.
        
        Args:
            plugin_name: Name of the plugin (e.g., 'appium-device-farm')
        """
        try:
            logger.info(f"Installing Appium plugin: {plugin_name}")
            subprocess.run(
                ["appium", "plugin", "install", "--source", "npm", plugin_name],
                check=True,
                capture_output=True,
                text=True
            )
            self.plugins.append(plugin_name)
            logger.success(f"Successfully installed plugin: {plugin_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install plugin {plugin_name}: {e.stderr}")
            raise

    def start_appium_server(
        self,
        host: str = '127.0.0.1',
        port: int = 4723,
        base_path: str = '/wd/hub',
        log_file: Optional[Union[str, Path]] = None,
        **server_args
    ) -> None:
        """Start the Appium server with specified configuration.
        
        Args:
            host: Server host address
            port: Server port
            base_path: Base URL path
            log_file: Path to log file for server logs
            **server_args: Additional server arguments
        """
        if self.appium_service and self.appium_service.is_running:
            logger.warning("Appium server is already running")
            return

        logger.info("Starting Appium server...")
        
        # Prepare server arguments
        args = [
            '--address', host,
            '--port', str(port),
            '--base-path', base_path,
            '--log-timestamp',
            '--local-timezone',
            '--log-no-colors'
        ]
        
        # Add any additional server arguments
        for key, value in server_args.items():
            arg_key = f"--{key.replace('_', '-')}"
            if isinstance(value, bool):
                if value:
                    args.append(arg_key)
            else:
                args.extend([arg_key, str(value)])
        
        # Add plugins if any
        for plugin in self.plugins:
            args.extend(['--use-plugins', plugin])
        
        # Configure log file
        if log_file:
            log_file = Path(log_file).resolve()
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.touch()
            args.extend(['--log', str(log_file)])
        
        # Start the server
        self.appium_service = AppiumService()
        self.appium_service.start(
            args=args,
            env=os.environ
        )
        
        # Wait for server to start
        max_attempts = 10
        for _ in range(max_attempts):
            if self.appium_service.is_running and self.appium_service.is_listening:
                logger.success(
                    f"Appium server started at http://{host}:{port}{base_path}"
                )
                return
            time.sleep(1)
        
        raise RuntimeError("Failed to start Appium server")

    def create_driver(
        self,
        platform_name: str,
        device_name: str,
        app: Optional[str] = None,
        app_package: Optional[str] = None,
        app_activity: Optional[str] = None,
        bundle_id: Optional[str] = None,
        automation_name: str = 'UiAutomator2',
        **capabilities
    ) -> WebDriver:
        """Create a new Appium WebDriver instance with dynamic capabilities.
        
        Args:
            platform_name: 'android' or 'ios'
            device_name: Name of the device/emulator
            app: Path to the app file
            app_package: Android app package name
            app_activity: Android app activity
            bundle_id: iOS bundle ID
            automation_name: Automation engine to use
            **capabilities: Additional capabilities
            
        Returns:
            Configured WebDriver instance
        """
        if not self.appium_service or not self.appium_service.is_running:
            raise RuntimeError("Appium server is not running")
        
        options = AppiumOptions()
        
        # Set platform-specific capabilities
        platform_name = platform_name.lower()
        options.set_capability('platformName', platform_name.capitalize())
        options.set_capability('deviceName', device_name)
        options.set_capability('automationName', automation_name)
        
        if platform_name == 'android':
            if app:
                options.set_capability('app', str(Path(app).resolve()))
            if app_package:
                options.set_capability('appPackage', app_package)
            if app_activity:
                options.set_capability('appActivity', app_activity)
        elif platform_name == 'ios':
            if app:
                options.set_capability('app', str(Path(app).resolve()))
            if bundle_id:
                options.set_capability('bundleId', bundle_id)
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")
        
        # Add any additional capabilities
        for key, value in capabilities.items():
            options.set_capability(key, value)
        
        # Create and store the driver
        driver = WebDriver(
            command_executor='http://localhost:4723/wd/hub',
            options=options
        )
        self.drivers.append(driver)
        return driver

    def stop_driver(self, driver: WebDriver) -> None:
        """Stop a specific WebDriver instance."""
        if driver in self.drivers:
            try:
                driver.quit()
                self.drivers.remove(driver)
                logger.info("WebDriver session terminated")
            except Exception as e:
                logger.error(f"Error stopping WebDriver: {e}")

    def stop_appium_server(self) -> None:
        """Stop the Appium server if it's running."""
        if self.appium_service and self.appium_service.is_running:
            logger.info("Stopping Appium server...")
            self.appium_service.stop()
            logger.success("Appium server stopped")

    def cleanup(self) -> None:
        """Clean up all resources."""
        logger.info("Cleaning up resources...")
        
        # Stop all drivers
        for driver in self.drivers[:]:
            self.stop_driver(driver)
        
        # Stop Appium server
        self.stop_appium_server()
        
        # Clean up any temporary files if needed
        # ...
        
        logger.info("Cleanup completed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def get_available_devices(platform_name: str = 'android') -> List[Dict[str, str]]:
    """Get list of available devices/emulators.
    
    Args:
        platform_name: 'android' or 'ios'
        
    Returns:
        List of dictionaries containing device information
    """
    devices = []
    platform_name = platform_name.lower()
    
    if platform_name == 'android':
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse adb devices output
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                if line.strip() and 'offline' not in line:
                    device_id = line.split('\t')[0]
                    devices.append({
                        'udid': device_id,
                        'name': f"Android Device ({device_id})",
                        'platform': 'Android'
                    })
        except Exception as e:
            logger.error(f"Error getting Android devices: {e}")
    
    elif platform_name == 'ios':
        if platform.system() == 'Darwin':  # macOS
            try:
                # List available iOS simulators
                result = subprocess.run(
                    ['xcrun', 'simctl', 'list', 'devices', '--json'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                import json
                sim_data = json.loads(result.stdout)
                
                for runtime, sims in sim_data.get('devices', {}).items():
                    for sim in sims:
                        if sim['isAvailable']:
                            devices.append({
                                'udid': sim['udid'],
                                'name': f"{sim['name']} ({runtime.split('.')[-2]})",
                                'platform': 'iOS'
                            })
            except Exception as e:
                logger.error(f"Error getting iOS simulators: {e}")
    
    return devices


# Example usage
if __name__ == "__main__":
    # Initialize the manager
    appium_manager = AppiumManager()
    
    try:
        # Install required plugins
        appium_manager.install_plugin('appium-device-farm')
        
        # Start Appium server
        appium_manager.start_appium_server(
            host='127.0.0.1',
            port=4723,
            log_file='appium_server.log',
            allow_insecure='chromedriver_autodownload',
            relaxed_security=True
        )
        
        # Get available devices
        android_devices = get_available_devices('android')
        if android_devices:
            print("Available Android devices:")
            for device in android_devices:
                print(f"- {device['name']} ({device['udid']})")
        
        # Example: Create an Android driver
        # driver = appium_manager.create_driver(
        #     platform_name='android',
        #     device_name='emulator-5554',
        #     app_package='com.example.app',
        #     app_activity='.MainActivity',
        #     automation_name='UiAutomator2',
        #     newCommandTimeout=300
        # )
        
        # Your test code here...
        
    finally:
        # Clean up resources
        appium_manager.cleanup()
