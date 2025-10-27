r"""
Cross-platform data directory resolution for Hei-DataHub.

Implements OS-specific defaults with override precedence:
1. CLI --data-dir flag (highest)
2. HEIDATAHUB_DATA_DIR environment variable
3. OS-specific default (lowest)

OS defaults:
- Linux: ~/.local/share/Hei-DataHub
- macOS: ~/Library/Application Support/Hei-DataHub
- Windows: %LOCALAPPDATA%\Hei-DataHub
"""
import os
import platform
import re
from pathlib import Path
from typing import Optional, Tuple


def get_os_type() -> str:
    """
    Get normalized OS type.

    Returns:
        'linux', 'darwin' (macOS), or 'windows'
    """
    system = platform.system().lower()
    if system == 'darwin':
        return 'darwin'
    elif system in ('windows', 'win32'):
        return 'windows'
    else:
        return 'linux'


def get_os_default_data_dir() -> Path:
    """
    Get OS-specific default data directory.

    Returns:
        Path object for the default data directory on this OS
    """
    os_type = get_os_type()

    if os_type == 'darwin':
        # macOS: ~/Library/Application Support/Hei-DataHub
        return Path.home() / "Library" / "Application Support" / "Hei-DataHub"
    elif os_type == 'windows':
        # Windows: %LOCALAPPDATA%\Hei-DataHub
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return Path(local_app_data) / "Hei-DataHub"
        # Fallback if LOCALAPPDATA not set
        return Path.home() / "AppData" / "Local" / "Hei-DataHub"
    else:
        # Linux: ~/.local/share/Hei-DataHub
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            return Path(xdg_data_home) / "Hei-DataHub"
        return Path.home() / ".local" / "share" / "Hei-DataHub"


def resolve_data_directory(cli_override: Optional[str] = None) -> Tuple[Path, str]:
    """
    Resolve data directory with proper precedence.

    Precedence (highest to lowest):
    1. CLI --data-dir flag
    2. HEIDATAHUB_DATA_DIR environment variable
    3. OS-specific default

    Args:
        cli_override: Optional path from --data-dir CLI argument

    Returns:
        Tuple of (resolved_path, reason_string)
        reason_string is one of: 'cli', 'env', 'default'
    """
    # Check CLI override first (highest priority)
    if cli_override:
        resolved = Path(cli_override).expanduser().resolve()
        return resolved, 'cli'

    # Check environment variable
    env_override = os.environ.get('HEIDATAHUB_DATA_DIR')
    if env_override:
        resolved = Path(env_override).expanduser().resolve()
        return resolved, 'env'

    # Use OS default
    return get_os_default_data_dir(), 'default'


def sanitize_windows_filename(name: str) -> str:
    """
    Sanitize filename for Windows compatibility.

    Handles:
    - Illegal characters: \\ / : * ? " < > | → _
    - Reserved names: CON PRN AUX NUL COM1-9 LPT1-9 → <name>_file
    - Trailing dots/spaces: stripped

    Args:
        name: Original filename

    Returns:
        Sanitized filename safe for Windows
    """
    if not name:
        return name

    # Replace illegal characters with underscore
    illegal_chars = r'[\\/:*?"<>|]'
    sanitized = re.sub(illegal_chars, '_', name)

    # Strip trailing dots and spaces (Windows doesn't allow them)
    sanitized = sanitized.rstrip('. ')

    # Check for reserved names (case-insensitive)
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    # Check base name (without extension)
    base_name = sanitized.split('.')[0] if '.' in sanitized else sanitized
    if base_name.upper() in reserved_names:
        sanitized = f"{sanitized}_file"

    return sanitized


def check_case_collision(path: Path, new_name: str) -> Optional[str]:
    """
    Check for case-insensitive filename collisions (Windows/macOS issue).

    Args:
        path: Parent directory to check in
        new_name: Name to check for collision

    Returns:
        Alternative name if collision detected, None otherwise
    """
    if not path.exists():
        return None

    # Get existing names (case-insensitive)
    existing_names = {item.name.lower(): item.name for item in path.iterdir()}

    # Check if new_name collides (case-insensitive) but differs (case-sensitive)
    if new_name.lower() in existing_names:
        existing = existing_names[new_name.lower()]
        if existing != new_name:
            # Collision detected - append suffix
            base, ext = os.path.splitext(new_name)
            counter = 1
            while True:
                alternative = f"{base}-{counter}{ext}"
                if alternative.lower() not in existing_names:
                    return alternative
                counter += 1

    return None


def detect_legacy_linux_path() -> Optional[Path]:
    """
    Detect if a legacy Linux-style path exists (for migration).

    Checks for:
    - ~/.hei-datahub (old v0.57 location)
    - ~/.local/share/hei-datahub (old v0.58 location with lowercase)

    Returns:
        Path if legacy directory exists, None otherwise
    """
    candidates = [
        Path.home() / ".hei-datahub",
        Path.home() / ".local" / "share" / "hei-datahub"
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            # Check if it has data
            datasets_dir = candidate / "datasets"
            if datasets_dir.exists() and any(datasets_dir.iterdir()):
                return candidate

    return None


def format_path_for_display(path: Path, reason: str) -> str:
    """
    Format path and reason for user-friendly display.

    Args:
        path: Resolved path
        reason: One of 'cli', 'env', 'default'

    Returns:
        Formatted string explaining the path choice
    """
    reason_map = {
        'cli': 'from --data-dir flag',
        'env': 'from HEIDATAHUB_DATA_DIR environment variable',
        'default': f'OS default ({get_os_type()})'
    }

    reason_text = reason_map.get(reason, reason)
    return f"{path} ({reason_text})"
