"""
Installation method detection for Hei-DataHub.

Detects how the application was installed to provide correct update instructions:
- AUR (yay/pacman) on Arch Linux
- Homebrew on macOS
- Windows EXE installer
- UV tool / pipx / pip
- Development mode (running from source)
"""
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Debug mode: HEI_DEBUG_UPDATER=1 for verbose detection logging
_DEBUG = os.environ.get("HEI_DEBUG_UPDATER", "").strip() in ("1", "true", "yes")


class InstallMethod(Enum):
    """Detected installation method."""
    AUR = "aur"              # Arch Linux AUR package (yay/pacman)
    HOMEBREW = "homebrew"    # macOS Homebrew
    WINDOWS_EXE = "windows"  # Windows installer (.exe)
    UV_TOOL = "uv"           # uv tool install
    PIPX = "pipx"            # pipx install
    PIP = "pip"              # pip install
    DEV = "dev"              # Development mode (running from source)
    APPIMAGE = "appimage"    # AppImage (generic Linux)
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


def _is_appimage() -> bool:
    """Check if running from an AppImage."""
    # AppImages set APPIMAGE and APPDIR environment variables
    return bool(os.environ.get("APPIMAGE") or os.environ.get("APPDIR"))


def _is_dev_mode() -> bool:
    """Check if running from repository (development mode)."""
    # Don't check dev mode if we're in an AppImage
    if _is_appimage():
        return False

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
        # Check if pacman exists (use full path as fallback)
        pacman_path = shutil.which("pacman") or "/usr/bin/pacman"
        if not Path(pacman_path).exists():
            return False

        # Check if hei-datahub is installed via pacman
        result = subprocess.run(
            [pacman_path, "-Qq", "hei-datahub"],
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


def _check_pipx_installed() -> bool:
    """Check if package is installed via pipx."""
    try:
        package_path = Path(__file__).resolve()

        # pipx installs to $PIPX_HOME/venvs or ~/.local/pipx/venvs (older)
        # or ~/.local/share/pipx/venvs (newer)
        pipx_home = os.environ.get("PIPX_HOME", "")
        if pipx_home and "pipx" in str(package_path) and pipx_home in str(package_path):
            return True

        # Check common pipx venv paths
        pipx_dirs = [
            Path.home() / ".local" / "pipx" / "venvs",
            Path.home() / ".local" / "share" / "pipx" / "venvs",
        ]
        for pipx_dir in pipx_dirs:
            if str(pipx_dir) in str(package_path):
                return True

        # Also check if pipx is available and lists our package
        if shutil.which("pipx"):
            result = subprocess.run(
                ["pipx", "list", "--short"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and "hei-datahub" in result.stdout.lower():
                return True

        return False
    except Exception:
        return False


def detect_install_method() -> InstallInfo:
    """
    Detect how Hei-DataHub was installed and return update instructions.

    Detection priority is based on specificity:
    1. Frozen exe (PyInstaller) on Windows — definitive, from sys.frozen
    2. Dev mode — definitive, from file path in repo
    3. AppImage — definitive, from $APPIMAGE env var
    4. Frozen exe (PyInstaller) on Linux — check pacman first, then
       treat as generic AppImage-like binary
    5. UV tool — definitive, from file path in uv/tools/
    6. pipx — definitive, from file path in pipx/venvs/
    7. AUR (pacman) — system package manager check (non-frozen)
    8. Homebrew — system package manager check
    9. pip (site-packages) — broad fallback
    10. Unknown

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

    # 2. Check for development mode (before AppImage check)
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

    # 3. Check for AppImage on Linux - then determine how it was installed
    if _is_appimage():
        # AppImage running - check if installed via AUR/pacman
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
        else:
            # Generic AppImage (downloaded manually)
            return InstallInfo(
                method=InstallMethod.APPIMAGE,
                update_command="",
                update_instructions=(
                    "Running from AppImage.\n\n"
                    "To update, download the latest AppImage from:\n"
                    "  https://github.com/0xpix/Hei-DataHub/releases\n\n"
                    "Or install via AUR for automatic updates:\n"
                    "  yay -S hei-datahub"
                )
            )

    # 4. Frozen binary on Linux (not AppImage) — check pacman/AUR
    #    This handles cases where the PyInstaller binary is run directly
    #    (e.g. via AUR wrapper script) without the AppImage layer.
    if _is_frozen() and sys.platform == "linux":
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
        else:
            # Frozen Linux binary not from AppImage or AUR — standalone
            return InstallInfo(
                method=InstallMethod.APPIMAGE,
                update_command="",
                update_instructions=(
                    "Running from standalone binary.\n\n"
                    "To update, download the latest release from:\n"
                    "  https://github.com/0xpix/Hei-DataHub/releases\n\n"
                    "Or install via AUR for automatic updates:\n"
                    "  yay -S hei-datahub"
                )
            )

    # 5. Check for UV tool installation (path-based — definitive)
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

    # 6. Check for pipx installation (path-based — definitive)
    if _check_pipx_installed():
        return InstallInfo(
            method=InstallMethod.PIPX,
            update_command="pipx upgrade hei-datahub",
            update_instructions=(
                "Installed via pipx.\n\n"
                "To update, run:\n"
                "  pipx upgrade hei-datahub"
            )
        )

    # 7. Check for AUR (pacman) on Linux (non-AppImage, non-frozen)
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

    # 8. Check for Homebrew on macOS
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

    # 9. Check if in site-packages (pip install)
    package_path = Path(__file__).resolve()
    if "site-packages" in str(package_path):
        return InstallInfo(
            method=InstallMethod.PIP,
            update_command=f"{sys.executable} -m pip install --upgrade hei-datahub",
            update_instructions=(
                "Installed via pip.\n\n"
                "To update, run:\n"
                f"  {sys.executable} -m pip install --upgrade hei-datahub"
            )
        )

    # 10. Unknown installation method
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
        _pkg_path = Path(__file__).resolve()
        msg = (
            f"Detected install method: {_cached_install_info.method.value} "
            f"(package path: {_pkg_path})"
        )
        if _DEBUG:
            logger.warning(f"[DEBUG-UPDATER] {msg}")
        else:
            logger.info(msg)
    return _cached_install_info
