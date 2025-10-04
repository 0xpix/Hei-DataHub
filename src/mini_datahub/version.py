"""
Version information and metadata for Hei-DataHub.

This module provides version info, build metadata, and system information
for debugging and diagnostics.
"""
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Version info
__version__ = "0.55.0-beta"
__version_info__ = (0, 55, 0, "beta")
__app_name__ = "Hei-DataHub"
__description__ = "A local-first TUI for managing datasets with consistent metadata"

# Release metadata
RELEASE_DATE = "2025-10-04"
BUILD_NUMBER = "005500"
CODENAME = "Clean Architecture"

# GitHub repository
GITHUB_REPO = "0xpix/Hei-DataHub"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# License
LICENSE = "MIT"
AUTHOR = "0xpix"


def get_version_string(include_build: bool = False) -> str:
    """
    Get formatted version string.

    Args:
        include_build: Include build number in version string

    Returns:
        Formatted version string

    Examples:
        >>> get_version_string()
        '0.55.0-beta'
        >>> get_version_string(include_build=True)
        '0.55.0-beta+005500'
    """
    version = __version__
    if include_build:
        version += f"+{BUILD_NUMBER}"
    return version


def get_version_info() -> Dict[str, Any]:
    """
    Get comprehensive version and system information.

    Returns:
        Dictionary containing version, system, and build information
    """
    return {
        "app_name": __app_name__,
        "version": __version__,
        "version_info": __version_info__,
        "build_number": BUILD_NUMBER,
        "release_date": RELEASE_DATE,
        "codename": CODENAME,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "github_repo": GITHUB_REPO,
        "github_url": GITHUB_URL,
        "license": LICENSE,
        "author": AUTHOR,
    }


def print_version_info(verbose: bool = False) -> None:
    """
    Print version information to stdout.

    Args:
        verbose: If True, print detailed system information
    """
    if verbose:
        print(f"{__app_name__} v{__version__}")
        print(f"Codename: {CODENAME}")
        print(f"Released: {RELEASE_DATE}")
        print(f"Build: {BUILD_NUMBER}")
        print()
        print("System Information:")
        print(f"  Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({platform.python_implementation()})")
        print(f"  Platform: {platform.platform()}")
        print(f"  System: {platform.system()} ({platform.machine()})")
        print()
        print(f"Repository: {GITHUB_URL}")
        print(f"License: {LICENSE}")
    else:
        print(f"{__app_name__} {__version__}")


def get_banner() -> str:
    """
    Get ASCII art banner for the application.

    Returns:
        Multi-line banner string
    """
    return f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   _   _ _____ ___     ____    _  _____  _    _   _ _   _ ____║
║  | | | | ____|_ _|   |  _ \\  / \\|_   _|/ \\  | | | | | | | __ )
║  | |_| |  _|  | |    | | | |/ _ \\ | | / _ \\ | |_| | | | |  _ \\
║  |  _  | |___ | |    | |_| / ___ \\| |/ ___ \\|  _  | |_| | |_) |
║  |_| |_|_____|___|   |____/_/   \\_\\_/_/   \\_\\_| |_|\\___/|____/║
║                                                               ║
║  {__app_name__:<40} v{__version__:<16} ║
║  {CODENAME:<59} ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """.strip()


def check_version_compatibility(min_version: str) -> bool:
    """
    Check if current version meets minimum requirement.

    Args:
        min_version: Minimum required version string (e.g., "0.40.0")

    Returns:
        True if current version meets requirement, False otherwise
    """
    def parse_version(v: str) -> tuple:
        # Remove any suffix like -beta, -alpha, etc.
        v_clean = v.split('-')[0].split('+')[0]
        return tuple(map(int, v_clean.split('.')))

    current = parse_version(__version__)
    required = parse_version(min_version)

    return current >= required


__all__ = [
    "__version__",
    "__version_info__",
    "__app_name__",
    "__description__",
    "RELEASE_DATE",
    "BUILD_NUMBER",
    "CODENAME",
    "GITHUB_REPO",
    "GITHUB_URL",
    "UPDATE_CHECK_URL",
    "LICENSE",
    "AUTHOR",
    "get_version_string",
    "get_version_info",
    "print_version_info",
    "get_banner",
    "check_version_compatibility",
]
