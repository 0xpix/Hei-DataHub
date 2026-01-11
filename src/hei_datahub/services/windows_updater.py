"""
Windows auto-updater for Hei-DataHub.

Downloads and installs new versions from GitHub releases.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Optional

import requests

from hei_datahub import UPDATE_CHECK_URL, __version__
from hei_datahub.services.update_check import parse_version

# GitHub releases asset pattern
ASSET_NAME = "hei-datahub-setup.exe"


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_frozen() -> bool:
    """Check if running as PyInstaller bundle."""
    return getattr(sys, 'frozen', False)


def get_download_url() -> Optional[dict]:
    """
    Get the download URL for the latest release.

    Returns:
        Dict with update info or None if no update available.
        {
            "has_update": bool,
            "current_version": str,
            "latest_version": str,
            "download_url": str,
            "file_size": int,
            "release_notes": str,
            "error": str (if failed)
        }
    """
    try:
        response = requests.get(
            UPDATE_CHECK_URL,
            timeout=10,
            headers={"Accept": "application/vnd.github.v3+json"}
        )

        if response.status_code == 404:
            return {"error": "No releases found on GitHub yet"}

        if response.status_code != 200:
            return {"error": f"GitHub API error: {response.status_code}"}

        release_data = response.json()
        latest_version = release_data.get("tag_name", "").lstrip('v')

        if not latest_version:
            return {"error": "Release has no version tag"}

        # Compare versions
        current_tuple = parse_version(__version__)
        latest_tuple = parse_version(latest_version)
        has_update = latest_tuple > current_tuple

        # Find the setup.exe asset
        download_url = None
        file_size = 0

        for asset in release_data.get("assets", []):
            if asset.get("name") == ASSET_NAME:
                download_url = asset.get("browser_download_url")
                file_size = asset.get("size", 0)
                break

        if not download_url:
            return {"error": f"Release missing {ASSET_NAME} asset"}

        return {
            "has_update": has_update,
            "current_version": __version__,
            "latest_version": latest_version,
            "download_url": download_url,
            "file_size": file_size,
            "release_notes": release_data.get("body", "")[:500]
        }

    except requests.exceptions.Timeout:
        return {"error": "Connection timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


def download_update(
    download_url: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Optional[Path]:
    """
    Download the update installer.

    Args:
        download_url: URL to download from
        progress_callback: Optional callback(bytes_downloaded, total_bytes)

    Returns:
        Path to downloaded file or None on failure
    """
    try:
        response = requests.get(download_url, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        # Create temp directory for download
        temp_dir = Path(tempfile.gettempdir()) / "hei-datahub-update"
        temp_dir.mkdir(exist_ok=True)

        download_path = temp_dir / ASSET_NAME
        downloaded = 0

        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)

        return download_path

    except Exception:
        return None


def install_update(installer_path: Path) -> bool:
    """
    Run the installer and exit the current application.

    Args:
        installer_path: Path to the downloaded installer

    Returns:
        True if installer started successfully
    """
    if not installer_path.exists():
        return False

    try:
        # Start installer in a new process (detached)
        if is_windows():
            # Use DETACHED_PROCESS flag on Windows
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008

            subprocess.Popen(
                [str(installer_path)],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )
        else:
            # On Unix, just run normally (shouldn't be called)
            subprocess.Popen([str(installer_path)])

        return True

    except Exception:
        return False


def perform_update(
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> tuple[bool, str]:
    """
    Perform the full update process.

    Args:
        progress_callback: Optional callback(status_message, percent)

    Returns:
        Tuple of (success: bool, message: str)
    """
    def update_status(msg: str, pct: int):
        if progress_callback:
            progress_callback(msg, pct)

    # Step 1: Check for updates
    update_status("Checking for updates...", 5)
    update_info = get_download_url()

    if not update_info:
        return False, "Failed to check for updates"

    if "error" in update_info:
        return False, update_info["error"]

    if not update_info.get("has_update"):
        return False, f"Already on latest version ({__version__})"

    latest = update_info["latest_version"]
    update_status(f"Found update: v{latest}", 10)

    # Step 2: Download
    download_url = update_info["download_url"]
    total_size = update_info["file_size"]

    def download_progress(downloaded: int, total: int):
        if total > 0:
            pct = 10 + int(80 * downloaded / total)  # 10-90%
            mb_done = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            update_status(f"Downloading... {mb_done:.1f}/{mb_total:.1f} MB", pct)

    update_status("Starting download...", 10)
    installer_path = download_update(download_url, download_progress)

    if not installer_path:
        return False, "Download failed"

    # Step 3: Install
    update_status("Starting installer...", 95)

    if not install_update(installer_path):
        return False, "Failed to start installer"

    update_status("Update ready - closing app...", 100)
    return True, f"Updating to v{latest}..."


def check_update_available() -> Optional[str]:
    """
    Quick check if an update is available.

    Returns:
        Latest version string if update available, None otherwise
    """
    update_info = get_download_url()
    if update_info and update_info.get("has_update"):
        return update_info["latest_version"]
    return None
