"""
Update checker for new releases.
Queries GitHub API to check for newer versions.
"""
from datetime import datetime, timedelta
from typing import Optional

import requests
from hei_datahub.services.state import get_state_manager  # type: ignore

from hei_datahub import UPDATE_CHECK_URL, __version__


def parse_version(version_str: str) -> tuple[int, ...]:
    """
    Parse semantic version string to tuple.

    Args:
        version_str: Version string (e.g., "3.0.0" or "v3.0.0")

    Returns:
        Version tuple (e.g., (3, 0, 0))
    """
    # Strip leading 'v' if present
    clean = version_str.lstrip('v')

    try:
        parts = clean.split('.')
        return tuple(int(p) for p in parts)
    except Exception:
        return (0, 0, 0)


def check_for_updates(force: bool = False) -> Optional[dict]:
    """
    Check if a newer version is available.

    Args:
        force: Force check even if checked recently

    Returns:
        Dict with update info if available, None otherwise.
        Format: {
            "has_update": bool,
            "current_version": str,
            "latest_version": str,
            "release_url": str,
            "release_notes": str
        }
    """
    state_manager = get_state_manager()

    # Check if we should skip (unless forced)
    if not force:
        last_check = state_manager.get_last_update_check()
        if last_check:
            # Only check once per week
            if datetime.now() - last_check < timedelta(days=7):
                return None

    try:
        # Query GitHub API
        response = requests.get(
            UPDATE_CHECK_URL,
            timeout=5,
            headers={"Accept": "application/vnd.github.v3+json"}
        )

        if response.status_code == 404:
            # No releases yet - treat as "up to date"
            return {
                "has_update": False,
                "current_version": __version__,
                "latest_version": __version__,
                "release_url": "",
                "release_notes": "No releases published yet"
            }

        if response.status_code != 200:
            return {"error": f"GitHub API returned {response.status_code}"}

        release_data = response.json()

        # Extract version
        latest_version = release_data.get("tag_name", "").lstrip('v')
        if not latest_version:
            # No version tag - treat as up to date
            return {
                "has_update": False,
                "current_version": __version__,
                "latest_version": __version__,
                "release_url": "",
                "release_notes": "Release has no version tag"
            }

        # Update last check timestamp
        state_manager.set_last_update_check()

        # Compare versions
        current_tuple = parse_version(__version__)
        latest_tuple = parse_version(latest_version)

        has_update = latest_tuple > current_tuple

        return {
            "has_update": has_update,
            "current_version": __version__,
            "latest_version": latest_version,
            "release_url": release_data.get("html_url", ""),
            "release_notes": release_data.get("body", "")[:500]  # Truncate notes
        }

    except requests.exceptions.Timeout:
        return {"error": "Connection timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection"}
    except Exception as e:
        return {"error": f"Update check failed: {str(e)}"}


def format_update_message(update_info: dict) -> str:
    """
    Format update notification message.

    Args:
        update_info: Update info dict from check_for_updates()

    Returns:
        Formatted message string
    """
    if not update_info or not update_info.get("has_update"):
        return ""

    current = update_info["current_version"]
    latest = update_info["latest_version"]
    url = update_info["release_url"]

    message = f"New version available: {latest} (current: {current})\n"
    message += f"Download: {url}"

    return message
