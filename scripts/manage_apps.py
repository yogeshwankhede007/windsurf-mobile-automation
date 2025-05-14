#!/usr/bin/env python3
"""
App Management Utility

This script provides a command-line interface to manage mobile application files
in the apps directory. It helps with adding, listing, and cleaning up app files.
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

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
APPS_DIR = PROJECT_ROOT / 'apps'
ANDROID_APPS_DIR = APPS_DIR / 'android'
IOS_APPS_DIR = APPS_DIR / 'ios'

# Supported file extensions
ANDROID_EXTENSIONS = ('.apk', '.aab')
IOS_EXTENSIONS = ('.ipa', '.app', '.zip')


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    for directory in [APPS_DIR, ANDROID_APPS_DIR, IOS_APPS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


def get_platform_from_extension(file_path: Path) -> Optional[str]:
    """Determine the platform based on file extension."""
    ext = file_path.suffix.lower()
    if ext in ANDROID_EXTENSIONS:
        return 'android'
    elif ext in IOS_EXTENSIONS:
        return 'ios'
    return None


def add_app(file_path: Path, platform: Optional[str] = None) -> Tuple[bool, str]:
    """
    Add an app file to the appropriate directory.
    
    Args:
        file_path: Path to the app file
        platform: Optional platform ('android' or 'ios'). If not provided, will be detected from extension.
        
    Returns:
        Tuple of (success, message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    # Determine platform
    if not platform:
        platform = get_platform_from_extension(file_path)
        if not platform:
            return False, f"Could not determine platform from file extension. Supported extensions: {ANDROID_EXTENSIONS + IOS_EXTENSIONS}"
    
    platform = platform.lower()
    
    # Get target directory
    if platform == 'android':
        target_dir = ANDROID_APPS_DIR
    elif platform == 'ios':
        target_dir = IOS_APPS_DIR
    else:
        return False, f"Unsupported platform: {platform}. Must be 'android' or 'ios'."
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    target_path = target_dir / file_path.name
    
    try:
        shutil.copy2(file_path, target_path)
        return True, f"Successfully added {platform} app: {target_path}"
    except Exception as e:
        return False, f"Failed to add app: {str(e)}"


def list_apps(platform: Optional[str] = None) -> List[Path]:
    """
    List all app files in the apps directory.
    
    Args:
        platform: Optional platform filter ('android' or 'ios')
        
    Returns:
        List of Path objects for app files
    """
    apps = []
    
    if not platform or platform.lower() == 'android':
        for ext in ANDROID_EXTENSIONS:
            apps.extend(ANDROID_APPS_DIR.glob(f'*{ext}'))
    
    if not platform or platform.lower() == 'ios':
        for ext in IOS_EXTENSIONS:
            apps.extend(IOS_APPS_DIR.glob(f'*{ext}'))
    
    # Sort by modification time (newest first)
    return sorted(apps, key=lambda f: f.stat().st_mtime, reverse=True)


def clean_apps(platform: Optional[str] = None, keep: int = 3) -> List[str]:
    """
    Clean up old app files, keeping only the most recent ones.
    
    Args:
        platform: Optional platform filter ('android' or 'ios')
        keep: Number of most recent files to keep
        
    Returns:
        List of messages about deleted files
    """
    messages = []
    
    platforms = ['android', 'ios']
    if platform:
        platforms = [platform.lower()]
    
    for plat in platforms:
        if plat == 'android':
            apps = list_apps('android')
            plat_name = 'Android'
        else:
            apps = list_apps('ios')
            plat_name = 'iOS'
        
        if len(apps) <= keep:
            messages.append(f"No {plat_name} apps to clean (keeping {len(apps)} of {keep} max)")
            continue
        
        # Keep the most recent files
        to_keep = apps[:keep]
        to_delete = apps[keep:]
        
        for app in to_delete:
            try:
                app.unlink()
                messages.append(f"Deleted old {plat_name} app: {app.name}")
            except Exception as e:
                messages.append(f"Failed to delete {app}: {str(e)}")
    
    return messages


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Manage mobile application files')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add an app file')
    add_parser.add_argument('file', type=Path, help='Path to the app file')
    add_parser.add_argument('--platform', choices=['android', 'ios'], 
                          help='Platform (android/ios). If not provided, will be detected from file extension.')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List app files')
    list_parser.add_argument('--platform', choices=['android', 'ios'], 
                            help='Filter by platform')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean up old app files')
    clean_parser.add_argument('--platform', choices=['android', 'ios'], 
                             help='Platform to clean')
    clean_parser.add_argument('--keep', type=int, default=3, 
                             help='Number of most recent files to keep (default: 3)')
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Ensure directories exist
    ensure_directories()
    
    # Parse arguments
    args = parse_arguments()
    
    if args.command == 'add':
        success, message = add_app(args.file, args.platform)
        if success:
            logger.info(message)
        else:
            logger.error(message)
            sys.exit(1)
    
    elif args.command == 'list':
        apps = list_apps(args.platform)
        if not apps:
            platform = args.platform or 'Android/iOS'
            logger.info(f"No {platform} apps found in {APPS_DIR}")
        else:
            logger.info(f"Found {len(apps)} {args.platform or 'Android/iOS'} apps:")
            for i, app in enumerate(apps, 1):
                mtime = app.stat().st_mtime
                mtime_str = app.stat().st_mtime
                logger.info(f"{i}. {app.name} ({app.parent.name}, {app.stat().st_size/1024/1024:.1f} MB, mtime: {mtime_str})")
    
    elif args.command == 'clean':
        messages = clean_apps(args.platform, args.keep)
        for msg in messages:
            logger.info(msg)
    
    else:
        logger.error("No command specified. Use 'add', 'list', or 'clean'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
