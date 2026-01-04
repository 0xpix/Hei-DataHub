"""
Configuration paths and user directory management.
"""
from pathlib import Path
from typing import Optional

from hei_datahub.infra.paths import CONFIG_DIR


def get_user_config_dir() -> Path:
    """
    Get the user configuration directory for Hei-DataHub.

    Returns:
        Path to config directory (respects dev mode from infra.paths)
    """
    return CONFIG_DIR


def ensure_user_config_dir() -> Path:
    """
    Ensure the user config directory exists and return its path.

    Returns:
        Path to the created/existing config directory
    """
    config_dir = get_user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_user_config_file() -> Path:
    """
    Get the path to the user config file.

    Returns:
        Path to ~/.config/hei-datahub/config.yaml (or XDG_CONFIG_HOME/hei-datahub/config.yaml)
    """
    return ensure_user_config_dir() / "config.yaml"


def get_config_path() -> Path:
    """
    Get the path to the TOML config file for auth and other settings.

    Returns:
        Path to ~/.config/hei-datahub/config.toml (or XDG_CONFIG_HOME/hei-datahub/config.toml)
    """
    return ensure_user_config_dir() / "config.toml"


def get_keybindings_export_path(filename: Optional[str] = None) -> Path:
    """
    Get the path for exporting/importing keybindings.

    Args:
        filename: Optional custom filename (defaults to keybindings.yaml)

    Returns:
        Path to keybindings export file
    """
    if filename:
        return Path(filename)
    return ensure_user_config_dir() / "keybindings.yaml"
