"""
Version information for mini-datahub.

This module contains version metadata and utility functions for version management.
It provides a centralized location for all version-related information.
"""

import sys
from typing import Dict, Tuple

# Version Components
__version__ = "0.55.0-beta"
__version_info__ = (0, 55, 0, "beta")

# Application Metadata
__app_name__ = "Hei-DataHub"
__author__ = "Your Name"
__author_email__ = "your.email@example.com"
__license__ = "MIT"
__description__ = "A local-first TUI for managing datasets with consistent metadata"

# Build Information
BUILD_NUMBER = "005500"
RELEASE_DATE = "2025-01-04"
CODENAME = "Clean Architecture"

# Repository Information
GITHUB_REPO = "your-username/hei-datahub"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
ISSUES_URL = f"{GITHUB_URL}/issues"
DOCS_URL = f"{GITHUB_URL}#readme"

# Update Check Configuration
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
UPDATE_CHECK_INTERVAL = 86400  # 24 hours in seconds


def get_version_string(include_build: bool = False) -> str:
    """
    Get the version string with optional build number.

    Args:
        include_build: Whether to include the build number in the version string

    Returns:
        The formatted version string

    Example:
        >>> get_version_string()
        '0.55.0-beta'
        >>> get_version_string(include_build=True)
        '0.55.0-beta (build 005500)'
    """
    version = __version__
    if include_build:
        version = f"{version} (build {BUILD_NUMBER})"
    return version


def get_version_info() -> Dict[str, any]:
    """
    Get comprehensive version information as a dictionary.

    Returns:
        Dictionary containing all version metadata

    Example:
        >>> info = get_version_info()
        >>> info['version']
        '0.55.0-beta'
    """
    return {
        "version": __version__,
        "version_tuple": __version_info__,
        "app_name": __app_name__,
        "build_number": BUILD_NUMBER,
        "release_date": RELEASE_DATE,
        "codename": CODENAME,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_implementation": sys.implementation.name,
        "github_repo": GITHUB_REPO,
        "github_url": GITHUB_URL,
    }


def print_version_info(verbose: bool = False) -> None:
    """
    Print version information to stdout.

    Args:
        verbose: If True, print detailed version information

    Example:
        >>> print_version_info()
        Hei-DataHub 0.55.0-beta

        >>> print_version_info(verbose=True)
        Hei-DataHub 0.55.0-beta (build 005500)
        Release Date: 2025-01-04
        Codename: Clean Architecture
        Python: 3.13.0
        Repository: https://github.com/your-username/hei-datahub
    """
    if not verbose:
        print(f"{__app_name__} {__version__}")
        return

    info = get_version_info()
    print(f"{info['app_name']} {info['version']} (build {info['build_number']})")
    print(f"Release Date: {info['release_date']}")
    print(f"Codename: {info['codename']}")
    print(f"Python: {info['python_version']} ({info['python_implementation']})")
    print(f"Repository: {info['github_url']}")


def get_banner() -> str:
    """
    Get a formatted banner string for the application.

    Returns:
        Multi-line ASCII art banner with version information

    Example:
        >>> print(get_banner())
        ╔═══════════════════════════════════════╗
        ║        Hei-DataHub v0.55.0-beta       ║
        ║      Clean Architecture Edition       ║
        ╚═══════════════════════════════════════╝
    """
    banner = f"""
╔═══════════════════════════════════════╗
║     {__app_name__} v{__version__:>15} ║
║   {CODENAME:^33} ║
╚═══════════════════════════════════════╝
    """.strip()
    return banner


def check_version_compatibility(min_version: str) -> bool:
    """
    Check if the current version meets the minimum version requirement.

    Args:
        min_version: Minimum version string (e.g., "0.55.0")

    Returns:
        True if current version >= minimum version, False otherwise

    Example:
        >>> check_version_compatibility("0.40.0")
        True
        >>> check_version_compatibility("1.0.0")
        False
    """
    def parse_version(version_str: str) -> Tuple[int, ...]:
        """Parse version string into tuple of integers."""
        # Remove any suffix like -beta, -alpha, etc.
        version_str = version_str.split('-')[0]
        return tuple(map(int, version_str.split('.')))

    try:
        current = parse_version(__version__)
        required = parse_version(min_version)
        return current >= required
    except (ValueError, AttributeError):
        return False


# Convenience exports
VERSION = __version__
VERSION_INFO = __version_info__
APP_NAME = __app_name__

__all__ = [
    "__version__",
    "__version_info__",
    "__app_name__",
    "__author__",
    "__author_email__",
    "__license__",
    "__description__",
    "BUILD_NUMBER",
    "RELEASE_DATE",
    "CODENAME",
    "GITHUB_REPO",
    "GITHUB_URL",
    "ISSUES_URL",
    "DOCS_URL",
    "UPDATE_CHECK_URL",
    "UPDATE_CHECK_INTERVAL",
    "VERSION",
    "VERSION_INFO",
    "APP_NAME",
    "get_version_string",
    "get_version_info",
    "print_version_info",
    "get_banner",
    "check_version_compatibility",
]
