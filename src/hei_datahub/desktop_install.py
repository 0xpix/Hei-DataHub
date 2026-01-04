"""
Desktop integration installer for Hei-DataHub.

This module handles automatic installation of desktop assets (icons and .desktop entry)
on Linux systems. All assets are packaged inside the wheel and installed at runtime.

Public API:
    - install_desktop_assets(): Install/update desktop integration
    - ensure_desktop_assets_once(): Idempotent first-run installer
    - uninstall_desktop_assets(): Remove all desktop integration files
    - get_desktop_assets_status(): Check installation status
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def _is_ephemeral_environment() -> bool:
    """
    Check if running in an ephemeral/temporary environment (like uvx).

    Returns:
        True if running in uvx or similar temporary environment.
    """
    # Check if UV_INTERNAL__PARENT_ID is set (uvx sets this)
    if os.environ.get("UV_INTERNAL__PARENT_ID"):
        return True

    # Check if sys.prefix is in uv cache (uvx creates temp venvs here)
    if ".cache/uv/" in sys.prefix or "cache/uv/" in sys.prefix:
        return True

    # Check if VIRTUAL_ENV looks like a temporary directory
    venv_path = os.environ.get("VIRTUAL_ENV", "")
    if venv_path and (
        venv_path.startswith("/tmp/") or
        "/tmp/" in venv_path or
        "temp" in venv_path.lower()
    ):
        return True

    return False


def _get_xdg_data_home() -> Path:
    """Get XDG data home directory (Linux-only)."""
    if not _is_linux():
        # Return a dummy path on non-Linux systems (should never be used)
        return Path.home() / ".local" / "share"

    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data)
    return Path.home() / ".local" / "share"


def _get_app_data_dir() -> Path:
    """Get application data directory for stamps and metadata (Linux-only)."""
    if not _is_linux():
        # Return a dummy path on non-Linux systems (should never be used)
        return Path.home() / ".local" / "share" / "Hei-DataHub"

    data_home = _get_xdg_data_home()
    app_dir = data_home / "Hei-DataHub"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def _get_version_stamp_path() -> Path:
    """Get path to the version stamp file."""
    return _get_app_data_dir() / ".desktop_assets_version"


def _detect_system_theme() -> str:
    """
    Detect system theme (light/dark) on Linux.
    Returns 'dark' or 'light'. Defaults to 'dark' on failure.
    """
    try:
        # Try GTK/GNOME settings via gsettings
        if shutil.which("gsettings"):
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, timeout=2, check=False
            )
            if result.returncode == 0:
                output = result.stdout.strip().strip("'")
                if "light" in output.lower():
                    return "light"
                if "dark" in output.lower():
                    return "dark"
    except Exception:
        pass

    return "dark"  # Default to dark


def _get_current_version() -> str:
    """Get current application version."""
    try:
        from hei_datahub.version import __version__
        return __version__
    except ImportError:
        return "0.0.0-dev"


def _read_version_stamp() -> Optional[str]:
    """Read the installed version stamp."""
    stamp_path = _get_version_stamp_path()
    if stamp_path.exists():
        try:
            return stamp_path.read_text().strip()
        except Exception:
            return None
    return None


def _write_version_stamp(version: str) -> None:
    """Write the version stamp file."""
    stamp_path = _get_version_stamp_path()
    try:
        stamp_path.write_text(version)
    except Exception as e:
        # Non-fatal - just log and continue
        print(f"Warning: Could not write version stamp: {e}", file=sys.stderr)


def _get_asset_paths() -> dict[str, Path]:
    """Get paths to packaged assets using importlib.resources."""
    try:
        # Python 3.9+ compatible way
        from importlib.resources import files

        assets_root = files("hei_datahub") / "assets"
        icons_dir = assets_root / "icons"
        desktop_dir = assets_root / "desktop"

        return {
            "logo_light": icons_dir / "logo-full-light.svg",
            "logo_dark": icons_dir / "logo-full-dark.svg",
            "symbolic": icons_dir / "hei-datahub-symbolic.svg",
            "desktop_template": desktop_dir / "hei-datahub.desktop.tmpl",
        }
    except Exception as e:
        raise RuntimeError(f"Failed to locate packaged assets: {e}")


def _get_install_paths() -> dict[str, Path]:
    """Get installation paths for desktop assets (XDG compliant)."""
    data_home = _get_xdg_data_home()
    icons_base = data_home / "icons" / "hicolor"

    return {
        "icon_svg": icons_base / "scalable" / "apps" / "hei-datahub.svg",
        "icon_symbolic": icons_base / "scalable" / "status" / "hei-datahub-symbolic.svg",
        "desktop_entry": data_home / "applications" / "hei-datahub.desktop",
        "icons_base": icons_base,
    }


def _get_executable_path() -> str:
    """
    Get the full path to the hei-datahub executable (Linux-only).

    This is necessary for desktop entries because they don't source shell
    environment files, so ~/.local/bin may not be in PATH.

    Returns:
        Absolute path to the executable, or 'hei-datahub' as fallback.
    """
    if not _is_linux():
        # Should never be called on non-Linux systems
        return "hei-datahub"

    # Try to find hei-datahub in PATH
    executable = shutil.which("hei-datahub")
    if executable:
        return executable

    # Fallback: check common installation locations
    possible_paths = [
        Path.home() / ".local" / "bin" / "hei-datahub",  # UV tool install
        Path.home() / ".cargo" / "bin" / "hei-datahub",   # Cargo
        "/usr/local/bin/hei-datahub",                     # System-wide
        "/usr/bin/hei-datahub",                           # System package
    ]

    for path in possible_paths:
        if path.exists() and path.is_file():
            return str(path)

    # Last resort: return command name (will fail if not in PATH)
    return "hei-datahub"


def _atomic_write(source: Path, destination: Path, substitutions: dict = None) -> None:
    """
    Atomically write a file to destination with optional text substitutions.

    Writes to a .tmp file first, then replaces the target.

    Args:
        source: Source file path
        destination: Destination file path
        substitutions: Optional dict of {search_text: replacement_text} for substitution
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = destination.with_suffix(destination.suffix + ".tmp")

    try:
        # Read from source (which might be inside a wheel/zip)
        if hasattr(source, "read_bytes"):
            content = source.read_bytes()
        else:
            # For older importlib.resources versions
            with source.open("rb") as src:
                content = src.read()

        # Apply text substitutions if provided
        if substitutions:
            try:
                text = content.decode('utf-8')
                for search_text, replacement in substitutions.items():
                    text = text.replace(search_text, replacement)
                content = text.encode('utf-8')
            except Exception:
                # If substitution fails, use original content
                pass

        tmp_path.write_bytes(content)

        # Atomic replace
        os.replace(tmp_path, destination)
    except Exception:
        # Cleanup on failure
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def _refresh_icon_cache(icons_base: Path, verbose: bool = False) -> bool:
    """
    Refresh icon caches (best-effort).

    Returns True if cache was refreshed, False otherwise.
    """
    success = False

    # Try gtk-update-icon-cache (GNOME/GTK)
    if shutil.which("gtk-update-icon-cache"):
        try:
            subprocess.run(
                ["gtk-update-icon-cache", "-f", "-t", str(icons_base)],
                stdout=subprocess.DEVNULL if not verbose else None,
                stderr=subprocess.DEVNULL if not verbose else None,
                timeout=5,
                check=False,
            )
            success = True
        except Exception:
            pass

    # Try removing KDE icon cache (KDE Plasma)
    kde_cache = Path.home() / ".cache" / "icon-cache.kcache"
    if kde_cache.exists():
        try:
            kde_cache.unlink()
            success = True
        except Exception:
            pass

    # Try update-desktop-database for .desktop files
    if shutil.which("update-desktop-database"):
        apps_dir = _get_xdg_data_home() / "applications"
        try:
            subprocess.run(
                ["update-desktop-database", str(apps_dir)],
                stdout=subprocess.DEVNULL if not verbose else None,
                stderr=subprocess.DEVNULL if not verbose else None,
                timeout=5,
                check=False,
            )
            success = True
        except Exception:
            pass

    return success


def _check_icon_theme_match() -> bool:
    """Check if installed icon matches current system theme."""
    try:
        install_paths = _get_install_paths()
        asset_paths = _get_asset_paths()

        if not install_paths["icon_svg"].exists():
            return False

        theme = _detect_system_theme()
        expected_source = asset_paths["logo_dark"] if theme == "dark" else asset_paths["logo_light"]

        # Compare file contents
        installed_bytes = install_paths["icon_svg"].read_bytes()

        if hasattr(expected_source, "read_bytes"):
            expected_bytes = expected_source.read_bytes()
        else:
            with expected_source.open("rb") as f:
                expected_bytes = f.read()

        return installed_bytes == expected_bytes
    except Exception:
        return False


def get_desktop_assets_status() -> dict[str, any]:
    """
    Get current status of desktop assets installation.

    Returns:
        Dictionary with status information including:
        - installed: bool (whether assets are installed)
        - version: str (installed version, if any)
        - current_version: str (current app version)
        - needs_update: bool (whether update is needed)
        - files: dict (which files are present)
    """
    if not _is_linux():
        return {
            "installed": False,
            "version": None,
            "current_version": _get_current_version(),
            "needs_update": False,
            "files": {},
            "platform": sys.platform,
        }

    install_paths = _get_install_paths()
    installed_version = _read_version_stamp()
    current_version = _get_current_version()

    files_status = {
        "icon_svg": install_paths["icon_svg"].exists(),
        "icon_symbolic": install_paths["icon_symbolic"].exists(),
        "desktop_entry": install_paths["desktop_entry"].exists(),
    }

    all_installed = all(files_status.values())
    icon_match = _check_icon_theme_match()

    needs_update = (
        not all_installed or
        installed_version != current_version or
        not icon_match
    )

    return {
        "installed": all_installed,
        "version": installed_version,
        "current_version": current_version,
        "needs_update": needs_update,
        "files": files_status,
        "platform": sys.platform,
    }


def install_desktop_assets(
    user_scope: bool = True,
    force: bool = False,
    verbose: bool = False
) -> dict[str, any]:
    """
    Install desktop assets (icons and .desktop entry) to XDG paths.

    Args:
        user_scope: If True, install to user directories (~/.local/share).
                   If False, would install system-wide (NOT SUPPORTED - raises error).
        force: If True, reinstall even if already up-to-date.
        verbose: If True, print detailed progress information.

    Returns:
        Dictionary with installation results including:
        - success: bool
        - installed_files: list of paths
        - cache_refreshed: bool
        - message: str

    Raises:
        RuntimeError: If not on Linux or system-wide install requested.
        OSError: If file operations fail.
    """
    if not _is_linux():
        raise RuntimeError(
            f"Desktop integration is only supported on Linux (current platform: {sys.platform})"
        )

    if not user_scope:
        raise RuntimeError(
            "System-wide installation is not supported. Use user_scope=True."
        )

    # Check if update needed
    current_version = _get_current_version()
    installed_version = _read_version_stamp()

    if not force and installed_version == current_version:
        status = get_desktop_assets_status()
        if status["installed"] and not status["needs_update"]:
            return {
                "success": True,
                "installed_files": [],
                "cache_refreshed": False,
                "message": f"Desktop assets already up-to-date (v{current_version})",
                "skipped": True,
            }

    if verbose:
        print("📦 Installing desktop assets...")

    # Get asset and install paths
    try:
        asset_paths = _get_asset_paths()
        install_paths = _get_install_paths()
    except Exception as e:
        return {
            "success": False,
            "installed_files": [],
            "cache_refreshed": False,
            "message": f"Failed to locate assets: {e}",
            "error": str(e),
        }

    # Install files atomically
    installed_files = []

    try:
        # Detect theme and select logo
        theme = _detect_system_theme()
        logo_source = asset_paths["logo_dark"] if theme == "dark" else asset_paths["logo_light"]

        # Install SVG icon
        if verbose:
            print(f"  → Detected system theme: {theme}")
            print(f"  → Installing icon (SVG): {install_paths['icon_svg']}")
        _atomic_write(logo_source, install_paths["icon_svg"])
        installed_files.append(install_paths["icon_svg"])

        # Install symbolic icon
        if verbose:
            print(f"  → Installing symbolic icon: {install_paths['icon_symbolic']}")
        _atomic_write(asset_paths["symbolic"], install_paths["icon_symbolic"])
        installed_files.append(install_paths["icon_symbolic"])

        # Install desktop entry with executable path substitution
        if verbose:
            print(f"  → Installing desktop entry: {install_paths['desktop_entry']}")

        # Get the actual executable path (needed because desktop launchers don't source .bashrc)
        exec_path = _get_executable_path()
        if verbose and exec_path != "hei-datahub":
            print(f"     Using executable: {exec_path}")

        # Write desktop entry with path substitution
        _atomic_write(
            asset_paths["desktop_template"],
            install_paths["desktop_entry"],
            substitutions={"Exec=hei-datahub": f"Exec={exec_path}"}
        )
        installed_files.append(install_paths["desktop_entry"])

    except Exception as e:
        return {
            "success": False,
            "installed_files": installed_files,
            "cache_refreshed": False,
            "message": f"Failed to install files: {e}",
            "error": str(e),
        }

    # Refresh caches (best-effort)
    cache_refreshed = _refresh_icon_cache(install_paths["icons_base"], verbose=verbose)

    if verbose and cache_refreshed:
        print("  ✓ Icon caches refreshed")

    # Write version stamp
    _write_version_stamp(current_version)

    return {
        "success": True,
        "installed_files": installed_files,
        "cache_refreshed": cache_refreshed,
        "message": f"Desktop assets installed successfully (v{current_version})",
        "version": current_version,
    }


def ensure_desktop_assets_once(verbose: bool = False) -> bool:
    """
    Ensure desktop assets are installed (idempotent, fast path).

    This is called automatically on first run. It's designed to be very fast
    when assets are already installed.

    Args:
        verbose: If True, print installation message.

    Returns:
        True if assets were just installed, False if already present.
    """
    if not _is_linux():
        return False

    # Skip desktop integration in ephemeral environments (uvx, temporary venvs)
    if _is_ephemeral_environment():
        return False

    # Fast path: check version stamp
    status = get_desktop_assets_status()
    if status["installed"] and not status["needs_update"]:
        return False

    # Install assets
    result = install_desktop_assets(verbose=verbose)

    if result["success"] and not result.get("skipped", False):
        if verbose:
            print("✓ Registered desktop launcher and icons in your user profile.")
        return True

    return False


def uninstall_desktop_assets(verbose: bool = False) -> dict[str, any]:
    """
    Remove all desktop integration files.

    Args:
        verbose: If True, print what's being removed.

    Returns:
        Dictionary with uninstall results including:
        - success: bool
        - removed_files: list of paths that were removed
        - message: str
    """
    if not _is_linux():
        return {
            "success": True,
            "removed_files": [],
            "message": "No desktop assets to remove (not on Linux)",
        }

    install_paths = _get_install_paths()
    removed_files = []

    # Remove files (don't fail if missing)
    files_to_remove = [
        install_paths["icon_svg"],
        install_paths["icon_symbolic"],
        install_paths["desktop_entry"],
        _get_version_stamp_path(),
    ]

    for filepath in files_to_remove:
        if filepath.exists():
            try:
                filepath.unlink()
                removed_files.append(filepath)
                if verbose:
                    print(f"  ✓ Removed: {filepath}")
            except Exception as e:
                if verbose:
                    print(f"  ⚠ Could not remove {filepath}: {e}")

    # Refresh caches
    if removed_files:
        _refresh_icon_cache(install_paths["icons_base"], verbose=verbose)
        if verbose:
            print("  ✓ Icon caches refreshed")

    return {
        "success": True,
        "removed_files": removed_files,
        "message": f"Removed {len(removed_files)} desktop asset file(s)",
    }


def get_install_paths_info() -> str:
    """
    Get human-readable information about install paths.

    Returns:
        Formatted string with path information.
    """
    if not _is_linux():
        return "Desktop integration is only available on Linux."

    install_paths = _get_install_paths()

    info = "Desktop Assets Installation Paths:\n"
    info += "  Icons:\n"
    info += f"    • SVG (scalable): {install_paths['icon_svg']}\n"
    info += f"    • Symbolic:       {install_paths['icon_symbolic']}\n"
    info += "  Desktop Entry:\n"
    info += f"    • {install_paths['desktop_entry']}\n"
    info += "  Version Stamp:\n"
    info += f"    • {_get_version_stamp_path()}\n"

    return info
