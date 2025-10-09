"""
Version information for mini-datahub.

This module reads version data directly from version.yaml at runtime.
For version updates, simply edit version.yaml - no sync step needed!
"""
import yaml
from pathlib import Path
from typing import Tuple


def _load_version_data() -> dict:
    """
    Load version data from version.yaml.

    Returns:
        Dictionary with version metadata
    """
    # Find version.yaml in project root (3 levels up from this file)
    version_file = Path(__file__).parent.parent.parent / "version.yaml"

    # Fallback: try installed package location
    if not version_file.exists():
        try:
            from importlib import resources
            # Try to find it as a package resource
            version_file = resources.files("mini_datahub").parent.parent / "version.yaml"
        except Exception:
            pass

    # Last resort: use defaults if file not found
    if not version_file.exists():
        return {
            "version": "0.0.0-dev",
            "codename": "Unknown",
            "release_date": "Unknown",
            "compatibility": "Unknown",
            "notes": "",
            "app_name": "Hei-DataHub",
            "github_repo": "0xpix/Hei-DataHub",
        }

    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        # Return defaults on any error
        return {
            "version": "0.0.0-dev",
            "codename": "Unknown",
            "release_date": "Unknown",
            "compatibility": "Unknown",
            "notes": "",
            "app_name": "Hei-DataHub",
            "github_repo": "0xpix/Hei-DataHub",
        }


# Load version data once at module import
_VERSION_DATA = _load_version_data()


def _parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string into tuple."""
    parts = version_str.split("-")[0].split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0)


# Version Components
__version__ = _VERSION_DATA.get("version", "0.0.0-dev")
__version_info__ = _parse_version(__version__) + (_VERSION_DATA.get("version", "").split("-")[1] if "-" in _VERSION_DATA.get("version", "") else "",)

# Application Metadata
__app_name__ = _VERSION_DATA.get("app_name", "Hei-DataHub")
__license__ = _VERSION_DATA.get("license", "MIT")
__description__ = "A local-first TUI for managing datasets with consistent metadata"

# Build Information
_version_parts = __version__.split("-")[0].split(".")
BUILD_NUMBER = "".join(f"{int(p):02d}" for p in _version_parts[:3])
RELEASE_DATE = _VERSION_DATA.get("release_date", "Unknown")
CODENAME = _VERSION_DATA.get("codename", "Unknown")
COMPATIBILITY = _VERSION_DATA.get("compatibility", "Unknown")
RELEASE_NOTES = _VERSION_DATA.get("notes", "")

# Repository Information
GITHUB_REPO = _VERSION_DATA.get("github_repo", "0xpix/Hei-DataHub")
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
ISSUES_URL = f"{GITHUB_URL}/issues"
DOCS_URL = "https://0xpix.github.io/Hei-DataHub"

# Update Check Configuration
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
UPDATE_CHECK_INTERVAL = 86400  # 24 hours in seconds


def get_version_string(include_build: bool = False) -> str:
    """Get the version string with optional build number."""
    version = __version__
    if include_build:
        version = f"{version} (build {BUILD_NUMBER})"
    return version


def get_version_info() -> dict:
    """Get comprehensive version information as a dictionary."""
    import sys
    return {
        "version": __version__,
        "version_tuple": __version_info__,
        "app_name": __app_name__,
        "build_number": BUILD_NUMBER,
        "release_date": RELEASE_DATE,
        "codename": CODENAME,
        "compatibility": COMPATIBILITY,
        "release_notes": RELEASE_NOTES,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_implementation": sys.implementation.name,
        "github_repo": GITHUB_REPO,
        "github_url": GITHUB_URL,
        "docs_url": DOCS_URL,
    }


def print_version_info(verbose: bool = False) -> None:
    """Print version information to stdout."""
    print(f"{__app_name__} {__version__}")
    if verbose:
        print(f"Build: {BUILD_NUMBER}")
        print(f"Release Date: {RELEASE_DATE}")
        print(f"Codename: {CODENAME}")
        print(f"Compatibility: {COMPATIBILITY}")
        print(f"Repository: {GITHUB_URL}")
        print(f"Documentation: {DOCS_URL}")
        import sys
        print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({sys.implementation.name})")


__all__ = [
    "__version__",
    "__version_info__",
    "__app_name__",
    "__license__",
    "__description__",
    "BUILD_NUMBER",
    "RELEASE_DATE",
    "CODENAME",
    "COMPATIBILITY",
    "RELEASE_NOTES",
    "GITHUB_REPO",
    "GITHUB_URL",
    "ISSUES_URL",
    "DOCS_URL",
    "UPDATE_CHECK_URL",
    "UPDATE_CHECK_INTERVAL",
    "get_version_string",
    "get_version_info",
    "print_version_info",
]
