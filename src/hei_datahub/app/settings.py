"""
Application settings and configuration.

Lightweight configuration for application runtime settings.
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from hei_datahub.infra.paths import CONFIG_DIR

logger = logging.getLogger(__name__)

CONFIG_FILE = CONFIG_DIR / "app_settings.json"


class AppSettings:
    """Application settings manager."""

    def __init__(self):
        # Feature settings
        self.auto_check_updates: bool = True  # Weekly update check
        self.debug_logging: bool = False  # Enable debug logs
        self.theme: str = "default"  # UI theme

        # Load config from file
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not CONFIG_FILE.exists():
            return

        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)

            self.auto_check_updates = data.get("auto_check_updates", True)
            self.debug_logging = data.get("debug_logging", False)
            self.theme = data.get("theme", "default")

        except Exception as e:
            logger.error(f"Failed to load config from {CONFIG_FILE}: {e}")

    def save_config(self) -> None:
        """Save configuration to file."""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "auto_check_updates": self.auto_check_updates,
            "debug_logging": self.debug_logging,
            "theme": self.theme,
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Export config as dictionary."""
        return {
            "auto_check_updates": self.auto_check_updates,
            "debug_logging": self.debug_logging,
            "theme": self.theme,
        }


# Global config instance
_settings_instance: Optional[AppSettings] = None


def get_app_settings() -> AppSettings:
    """Get the global app settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AppSettings()
    return _settings_instance


def reload_settings() -> AppSettings:
    """Reload settings from file."""
    global _settings_instance
    _settings_instance = AppSettings()
    return _settings_instance


# Legacy aliases for compatibility
def load_config() -> AppSettings:
    """Compatibility alias - returns app settings."""
    return get_app_settings()


def get_github_config() -> AppSettings:
    """Compatibility alias - returns app settings."""
    return get_app_settings()
