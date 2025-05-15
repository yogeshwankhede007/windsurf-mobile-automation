#!/usr/bin/env python3
"""
Test Runner Script

This script provides a convenient way to run tests with various configurations.
It handles environment setup, test execution, and cleanup.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(command: List[str], cwd: Optional[Path] = None) -> int:
    """Run a shell command and return the exit code."""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd or PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        return process.returncode
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return 1


def install_dependencies() -> int:
    """Install project dependencies."""
    logger.info("Installing project dependencies...")
    commands = [
        ["pip", "install", "-r", "requirements.txt"],
        ["pip", "install", "-r", "requirements-dev.txt"],
        ["npm", "install", "-g", "appium"]
    ]
    
    for cmd in commands:
        if run_command(cmd) != 0:
            return 1
    return 0


def run_tests(
    platform: str,
    device_udid: Optional[str] = None,
    app_path: Optional[str] = None,
    install_plugins: bool = False,
    mark: Optional[str] = None,
    num_processes: int = 4,
    suite: str = "all"
) -> int:
    """Run tests with the specified configuration."""
    logger.info(f"Running tests for platform: {platform}")
    
    # Build pytest command
    cmd = [
        "pytest",
        "-v",
        f"--platform={platform}",
        f"-n={num_processes}",
        "--dist=loadscope",
        "--html=reports/report.html",
        "--self-contained-html",
        "--junitxml=reports/junit.xml",
        "--alluredir=reports/allure-results",
        f"--device-count={num_processes}",
        f"--suite={suite}"
    ]
    
    # Add suite-specific test directory if not running all suites
    if suite != "all":
        cmd.append(f"tests/suites/{suite}")
    
    # Add optional arguments
    if device_udid:
        cmd.extend(["--device-udid", device_udid])
    if app_path:
        cmd.extend(["--app-path", app_path])
    if install_plugins:
        cmd.append("--install-plugins")
    if mark:
        cmd.extend(["-m", mark])
    
    return run_command(cmd)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run automated tests.")
    parser.add_argument(
        "--platform",
        type=str,
        choices=["android", "ios"],
        default="android",
        help="Platform to test on (android or ios)"
    )
    parser.add_argument(
        "--suite",
        type=str,
        choices=["all", "sanity", "smoke", "regression"],
        default="all",
        help="Test suite to run (all, sanity, smoke, regression)"
    )
    parser.add_argument(
        "--devices",
        type=int,
        default=4,
        help="Number of parallel devices to run tests on (default: 4)"
    )
    parser.add_argument(
        "--device-udid",
        help="Device/emulator UDID to run tests on"
    )
    parser.add_argument(
        "--app",
        help="Path to the app file (overrides default for the platform)"
    )
    parser.add_argument(
        "--install-plugins",
        action="store_true",
        help="Install required Appium plugins"
    )
    parser.add_argument(
        "--mark",
        help="Run only tests with the specified marker (e.g., 'smoke' or 'regression')"
    )
    
    args = parser.parse_args()
    
    # Install dependencies
    install_dependencies()
    
    # Run tests
    return run_tests(
        platform=args.platform,
        device_udid=args.device_udid,
        app_path=args.app,
        install_plugins=args.install_plugins,
        mark=args.mark,
        num_processes=args.devices,
        suite=args.suite
    )


if __name__ == "__main__":
    sys.exit(main())
