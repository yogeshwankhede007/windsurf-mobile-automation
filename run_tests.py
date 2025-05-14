#!/usr/bin/env python3
"""Test runner script for the mobile automation framework.

This script provides a convenient way to run tests with various options and configurations.
It supports running tests in parallel, generating different types of reports, and more.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).parent
REPORTS_DIR = PROJECT_ROOT / "reports"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
ALLURE_RESULTS = PROJECT_ROOT / "allure-results"
ALLURE_REPORT = PROJECT_ROOT / "allure-report"
PYTEST_CMD = ["pytest", "-v"]
VALID_PLATFORMS = ["android", "ios"]


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Run mobile automation tests")
    
    # Test selection
    parser.add_argument(
        "-m",
        "--mark",
        help="Run tests with the specified mark",
        default="",
    )
    parser.add_argument(
        "-k",
        "--keyword",
        help="Only run tests which match the given substring expression",
        default="",
    )
    parser.add_argument(
        "tests",
        nargs="*",
        help="Test files or directories to run",
        default=["tests/"],
    )
    
    # Platform and device
    parser.add_argument(
        "--platform",
        choices=VALID_PLATFORMS,
        default="android",
        help="Platform to run tests on",
    )
    parser.add_argument(
        "--device-name",
        help="Name of the device or emulator to use",
    )
    parser.add_argument(
        "--app-path",
        help="Path to the application file",
    )
    
    # Test execution
    parser.add_argument(
        "-n",
        "--num-processes",
        type=int,
        default=1,
        help="Number of processes to use for test execution",
    )
    parser.add_argument(
        "--reruns",
        type=int,
        default=0,
        help="Number of times to re-run failed tests",
    )
    
    # Reporting
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report",
    )
    parser.add_argument(
        "--allure",
        action="store_true",
        help="Generate Allure report",
    )
    parser.add_argument(
        "--no-clean",
        action="store_false",
        dest="clean",
        help="Don't clean up previous test artifacts",
    )
    
    # Debugging
    parser.add_argument(
        "--pdb",
        action="store_true",
        help="Start the interactive Python debugger on errors",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    
    return parser.parse_args()


def setup_directories(clean: bool = True) -> None:
    """Set up directories for test artifacts.
    
    Args:
        clean: If True, clean up existing directories.
    """
    if clean:
        for directory in [REPORTS_DIR, SCREENSHOTS_DIR, ALLURE_RESULTS]:
            if directory.exists():
                shutil.rmtree(directory)
    
    for directory in [REPORTS_DIR, SCREENSHOTS_DIR, ALLURE_RESULTS]:
        directory.mkdir(parents=True, exist_ok=True)


def build_pytest_command(args: argparse.Namespace) -> List[str]:
    """Build the pytest command based on the provided arguments.
    
    Args:
        args: Parsed command line arguments.
        
    Returns:
        List[str]: List of command line arguments for pytest.
    """
    cmd = PYTEST_CMD.copy()
    
    # Platform and device
    cmd.extend(["--platform", args.platform])
    if args.device_name:
        cmd.extend(["--device-name", args.device_name])
    if args.app_path:
        cmd.extend(["--app-path", str(Path(args.app_path).absolute())])
    
    # Test selection
    if args.mark:
        cmd.extend(["-m", args.mark])
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    # Parallel execution
    if args.num_processes > 1:
        cmd.extend(["-n", str(args.num_processes)])
    
    # Rerun failed tests
    if args.reruns > 0:
        cmd.extend(["--reruns", str(args.reruns)])
    
    # Debugging
    if args.pdb:
        cmd.append("--pdb")
    
    # HTML report
    if args.html:
        html_report = REPORTS_DIR / "report.html"
        cmd.extend(["--html", str(html_report), "--self-contained-html"])
    
    # Allure report
    if args.allure:
        cmd.extend(["--alluredir", str(ALLURE_RESULTS)])
    
    # Add test files/directories
    cmd.extend([str(Path(t).absolute()) for t in args.tests])
    
    return cmd


def generate_allure_report() -> None:
    """Generate Allure report from test results."""
    if not ALLURE_RESULTS.exists() or not any(ALLURE_RESULTS.iterdir()):
        logger.warning("No Allure results found to generate report")
        return
    
    try:
        # Generate the report
        cmd = ["allure", "generate", str(ALLURE_RESULTS), "-o", str(ALLURE_REPORT), "--clean"]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Open the report in the default browser
        cmd = ["allure", "open", str(ALLURE_REPORT)]
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate Allure report: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr}")
    except FileNotFoundError:
        logger.error("Allure command line tool is not installed. Install it with 'pip install allure-pytest'")


def main() -> int:
    """Main entry point for the test runner.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    args = parse_arguments()
    
    # Set log level
    logging.getLogger().setLevel(args.log_level)
    
    try:
        # Set up directories
        setup_directories(args.clean)
        
        # Build and run pytest command
        cmd = build_pytest_command(args)
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd)
        
        # Generate Allure report if requested
        if args.allure and result.returncode == 0:
            generate_allure_report()
        
        return result.returncode
        
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
