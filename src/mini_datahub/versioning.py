"""
Runtime version information with environment variable support.

This module provides the single source of truth for version and codename
by reading from environment variables (PROJECT_VERSION, PROJECT_CODENAME)
with fallback to the generated _version.py file.

Priority:
1. Environment variables (PROJECT_VERSION, PROJECT_CODENAME)
2. Fallback to _version.py (generated from version.yaml)

Usage:
    from mini_datahub.versioning import VERSION, CODENAME
"""

import os

# Import fallback values from generated version file
from mini_datahub._version import (
    __version__ as _fallback_version,
    CODENAME as _fallback_codename,
    __app_name__,
    RELEASE_DATE,
    BUILD_NUMBER,
    GITHUB_REPO,
    GITHUB_URL,
    DOCS_URL,
)

# Single source of truth: Environment variables with fallback
VERSION = os.getenv("PROJECT_VERSION", _fallback_version)
CODENAME = os.getenv("PROJECT_CODENAME", _fallback_codename)

# Export all commonly needed values
__all__ = [
    "VERSION",
    "CODENAME",
    "__app_name__",
    "RELEASE_DATE",
    "BUILD_NUMBER",
    "GITHUB_REPO",
    "GITHUB_URL",
    "DOCS_URL",
]
