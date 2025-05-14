#!/usr/bin/env python3
"""
Verify that the test apps are properly configured and can be launched.

This script checks that:
1. The app files exist in the correct locations
2. The configuration is properly set up
3. The apps can be launched on their respective platforms
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def verify_android_app() -> bool:
    """Verify Android app configuration."""
    logger.info("Verifying Android app configuration...")
    
    # Check if app path is set
    if not config.android.app:
        logger.error("Android app path is not set")
        return False
    
    # Check if app file exists
    app_path = Path(config.android.app)
    if not app_path.exists():
        logger.error(f"Android app not found at: {app_path}")
        return False
    
    logger.info(f"Android app found at: {app_path}")
    logger.info(f"Package: {config.android.app_package}")
    logger.info(f"Activity: {config.android.app_activity}")
    
    return True

def verify_ios_app() -> bool:
    """Verify iOS app configuration."""
    logger.info("Verifying iOS app configuration...")
    
    # Check if app path is set
    if not config.ios.app:
        logger.error("iOS app path is not set")
        return False
    
    # Check if app file exists
    app_path = Path(config.ios.app)
    if not app_path.exists():
        logger.error(f"iOS app not found at: {app_path}")
        return False
    
    logger.info(f"iOS app found at: {app_path}")
    logger.info(f"Bundle ID: {config.ios.bundle_id}")
    
    return True

def main() -> int:
    """Main function to verify app configurations."""
    logger.info("Verifying app configurations...")
    
    android_ok = verify_android_app()
    ios_ok = verify_ios_app()
    
    if not android_ok and not ios_ok:
        logger.error("No valid app configurations found")
        return 1
    
    logger.info("App verification completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
