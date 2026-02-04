"""
Installation method detection for Hei-DataHub.

Detects how the application was installed to provide correct update instructions:
- AUR (yay/pacman) on Arch Linux
- Homebrew on macOS
- Windows EXE installer
- UV tool / pip
- Development mode (running from source)
"""
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class InstallMethod(Enum):
    """Detected installation method."""
    AUR = "aur"              # Arch Linux AUR package (yay/pacman)
    HOMEBREW = "homebrew"    # macOS Homebrew
    WINDOWS_EXE = "windows"  # Windows installer (.exe)
    UV_TOOL = "uv"           # uv tool install
    PIP = "pip"              # pip install
    DEV = "dev"              # Development mode (running from source)
    UNKNOWN = "unknown"      # Unknown installation method


@dataclass
class InstallInfo:
    """Information about how the app was installed."""
    method: InstallMethod
    update_command: str
    update_instructions: str
    package_name: str = "hei-datahub"


def _is_frozen() -> bool:
    """Check if running as frozen executable (PyInstaller)."""
    return getattr(sys, 'frozen', False)


def _is_dev_mode() -> bool:
    """Check if running from repository (development mode)."""
    package_path = Path(__file__).resolve()
    try:
        potential_repo = package_path.parent.parent.parent.parent
        return (
            (potential_repo / "src" / "hei_datahub").exists() and
            (potential_repo / "pyproject.toml").exists() and
            "site-packages" not in str(package_path)
        )
    except Exception:
        return False


def _check_pacman_installed() -> bool:
    """Check if package is installed via pacman/AUR."""
    if sys.platform != "linux":
        return False

    try:
        # Check if pacman exists
        if not shutil.which("pacman"):
            return False

        # Check if hei-datahub is installed via pacman
        result = subprocess.run(
            ["pacman", "-Qq", "hei-datahub"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_homebrew_installed() -> bool:
    """Check if package is installed via Homebrew."""
    if sys.platform != "darwin":
        return False

    try:
        # Check if brew exists
        if not shutil.which("brew"):
            return False

        # Check if hei-datahub is installed via brew
        result = subprocess.run(
            ["brew", "list", "--formula", "hei-datahub"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_uv_installed() -> bool:
    """Check if package is installed via uv tool."""
    try:
        # Check if installed in UV tools directory
        package_path = Path(__file__).resolve()

        # UV installs to ~/.local/share/uv/tools on Unix
        # or %LOCALAPPDATA%/uv/tools on Windows
        if sys.platform == "win32":
            uv_tools = Path(os.environ.get("LOCALAPPDATA", "")) / "uv" / "tools"
        else:
            uv_tools = Path.home() / ".local" / "share" / "uv" / "tools"

        return str(uv_tools) in str(package_path)
    except Exception:
        return False


def detect_install_method() -> InstallInfo:
    """
    Detect how Hei-DataHub was installed and return update instructions.

    Returns:
        InstallInfo with method, update command, and instructions
    """
    # 1. Check for frozen Windows exe
    if _is_frozen() and sys.platform == "win32":
        return InstallInfo(
            method=InstallMethod.WINDOWS_EXE,
            update_command="",
            update_instructions=(
                "The app will download and install the update automatically.\n"
                "After installation, the app will restart."
            )
        )

    # 2. Check for development mode
    if _is_dev_mode():
        return InstallInfo(
            method=InstallMethod.DEV,
            update_command="git pull origin main",
            update_instructions=(
                "Running from source code.\n\n"
                "To update, run in the repository:\n"
                "  git pull origin main\n"
                "  uv sync"
            )
        )

    # 3. Check for AUR (pacman) on Linux
    if _check_pacman_installed():
        return InstallInfo(
            method=InstallMethod.AUR,
            update_command="yay -Syu hei-datahub",
            update_instructions=(
                "Installed via AUR package.\n\n"
                "To update, run:\n"
                "  yay -Syu hei-datahub\n\n"
                "Or with your preferred AUR helper:\n"
                "  paru -Syu hei-datahub"
            )
        )

    # 4. Check for Homebrew on macOS
    if _check_homebrew_installed():
        return InstallInfo(
            method=InstallMethod.HOMEBREW,
            update_command="brew upgrade hei-datahub",
            update_instructions=(
                "Installed via Homebrew.\n\n"
                "To update, run:\n"
                "  brew update\n"
                "  brew upgrade hei-datahub"
            )
        )

    # 5. Check for UV tool installation
    if _check_uv_installed():
        return InstallInfo(
            method=InstallMethod.UV_TOOL,
            update_command="uv tool upgrade hei-datahub",
            update_instructions=(
                "Installed via uv tool.\n\n"
                "To update, run:\n"
                "  uv tool upgrade hei-datahub"
            )
        )

    # 6. Check if in site-packages (pip install)
    package_path = Path(__file__).resolve()
    if "site-packages" in str(package_path):
        return InstallInfo(
            method=InstallMethod.PIP,
            update_command="pip install --upgrade hei-datahub",
            update_instructions=(
                "Installed via pip.\n\n"
                "To update, run:\n"
                "  pip install --upgrade hei-datahub"
            )
        )

    # 7. Unknown installation method
    return InstallInfo(
        method=InstallMethod.UNKNOWN,
        update_command="",
        update_instructions=(
            "Unknown installation method.\n\n"
            "Try one of these commands:\n"
            "  - AUR (Arch): yay -Syu hei-datahub\n"
            "  - Homebrew (macOS): brew upgrade hei-datahub\n"
            "  - pip: pip install --upgrade hei-datahub\n"
            "  - uv: uv tool upgrade hei-datahub"
        )
    )


# Cached result
_cached_install_info: Optional[InstallInfo] = None


def get_install_info() -> InstallInfo:
    """Get installation info (cached)."""
    global _cached_install_info
    if _cached_install_info is None:
        _cached_install_info = detect_install_method()
    return _cached_install_info
