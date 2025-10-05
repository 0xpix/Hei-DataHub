"""
User configuration management with precedence handling.

Precedence: CLI args > ENV vars > user config > defaults
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

from mini_datahub.infra.config_paths import get_user_config_file, ensure_user_config_dir

logger = logging.getLogger(__name__)


class SearchDefaults(BaseModel):
    """Search configuration."""
    debounce_ms: int = Field(default=150, ge=50, le=1000)
    max_results: int = Field(default=50, ge=10, le=500)
    highlight_enabled: bool = True


class StartupConfig(BaseModel):
    """Startup behavior configuration."""
    check_updates: bool = True
    auto_reindex: bool = False


class TelemetryConfig(BaseModel):
    """Telemetry and analytics configuration."""
    opt_in: bool = False


class ThemeConfig(BaseModel):
    """Theme configuration."""
    name: str = Field(default="gruvbox")
    overrides: Dict[str, str] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_theme_name(cls, v: str) -> str:
        """Validate theme name against Textual's built-in themes."""
        # Textual built-in themes as of 2024+
        allowed = {
            "textual-dark", "textual-light", "textual-ansi",
            "gruvbox", "monokai", "nord", "dracula",
            "catppuccin-mocha", "catppuccin-latte",
            "flexoki", "tokyo-night", "solarized-light"
        }
        if v not in allowed:
            logger.warning(f"Unknown theme '{v}', falling back to 'gruvbox'. Available: {', '.join(sorted(allowed))}")
            return "gruvbox"
        return v


def get_default_keybindings() -> Dict[str, list[str]]:
    """Get default keybindings configuration."""
    return {
        "add_dataset": ["a"],
        "settings": ["s"],
        "open_details": ["o", "enter"],
        "outbox": ["p"],
        "pull_updates": ["u"],
        "refresh_data": ["r"],
        "quit": ["q"],
        "move_down": ["j", "down"],
        "move_up": ["k", "up"],
        "jump_top": ["g"],
        "jump_bottom": ["G"],
        "focus_search": ["/"],
        "clear_search": ["escape"],
        "debug_console": [":"],
        "show_help": ["?"],
    }


class UserConfig(BaseModel):
    """
    User configuration schema.

    This represents the full user config file structure.
    """
    config_version: int = Field(default=1)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    keybindings: Dict[str, list[str]] = Field(default_factory=get_default_keybindings)
    search: SearchDefaults = Field(default_factory=SearchDefaults)
    startup: StartupConfig = Field(default_factory=StartupConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)

    class Config:
        extra = "allow"  # Allow unknown fields for future compatibility


class ConfigManager:
    """
    Manages configuration with precedence: CLI > ENV > user config > defaults.
    """

    def __init__(self):
        self._user_config: UserConfig = self._load_user_config()
        self._cli_overrides: Dict[str, Any] = {}

    def _load_user_config(self) -> UserConfig:
        """Load user config from file or create defaults."""
        config_file = get_user_config_file()

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                logger.info(f"Loaded user config from {config_file}")
                return UserConfig(**data)
            except Exception as e:
                logger.error(f"Failed to load user config: {e}")
                logger.info("Using default configuration")
                return UserConfig()
        else:
            # Create default config file
            logger.info(f"Creating default config at {config_file}")
            config = UserConfig()
            self._save_user_config(config)
            return config

    def _save_user_config(self, config: UserConfig) -> None:
        """Save user config to file with documentation."""
        config_file = get_user_config_file()
        ensure_user_config_dir()

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                # Write header comment
                f.write("# Hei-DataHub Configuration\n")
                f.write("# This file is auto-generated on first run.\n")
                f.write("# Edit any values to customize your experience.\n\n")

                # Convert to dict and write
                data = config.model_dump(exclude_none=True)

                # Write config_version
                f.write(f"config_version: {data['config_version']}\n\n")

                # Write theme section
                f.write("# Available themes: textual-dark, textual-light, gruvbox, monokai,\n")
                f.write("# nord, dracula, catppuccin-mocha, catppuccin-latte, flexoki,\n")
                f.write("# tokyo-night, solarized-light\n")
                f.write("theme:\n")
                f.write(f"  name: {data['theme']['name']}\n")
                if data['theme'].get('overrides'):
                    f.write("  overrides:\n")
                    for k, v in data['theme']['overrides'].items():
                        f.write(f"    {k}: {v}\n")
                f.write("\n")

                # Write keybindings section
                f.write("# Keybindings: Customize any action with your preferred keys\n")
                f.write("# Format: action_name: [\"key1\", \"key2\"]\n")
                f.write("# Special keys: ctrl+key, shift+key, alt+key\n")
                f.write("keybindings:\n")
                for action, keys in data['keybindings'].items():
                    keys_str = str(keys).replace("'", '"')
                    f.write(f"  {action}: {keys_str}\n")
                f.write("\n")

                # Write search section
                f.write("# Search configuration\n")
                f.write("search:\n")
                for k, v in data['search'].items():
                    f.write(f"  {k}: {v}\n")
                f.write("\n")

                # Write startup section
                f.write("# Startup behavior\n")
                f.write("startup:\n")
                for k, v in data['startup'].items():
                    f.write(f"  {k}: {v}\n")
                f.write("\n")

                # Write telemetry section
                f.write("# Telemetry (opt-in only, no data collected by default)\n")
                f.write("telemetry:\n")
                for k, v in data['telemetry'].items():
                    f.write(f"  {k}: {v}\n")

            logger.info(f"Saved user config to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a config value with full precedence resolution.

        Args:
            key: Dot-separated config key (e.g., "theme.name")
            default: Default value if not found

        Returns:
            Config value with precedence: CLI > ENV > user config > default
        """
        # 1. Check CLI overrides
        if key in self._cli_overrides:
            return self._cli_overrides[key]

        # 2. Check environment variables
        env_key = f"HEIDH_{key.upper().replace('.', '_')}"
        if env_value := os.getenv(env_key):
            return self._parse_env_value(env_value)

        # 3. Check user config
        parts = key.split(".")
        value = self._user_config
        for part in parts:
            if isinstance(value, BaseModel):
                value = getattr(value, part, None)
            elif isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break

            if value is None:
                break

        if value is not None:
            return value

        # 4. Return default
        return default

    def set_cli_override(self, key: str, value: Any) -> None:
        """
        Set a CLI override (highest precedence).

        Args:
            key: Config key
            value: Value to set
        """
        self._cli_overrides[key] = value

    def parse_cli_overrides(self, overrides: list[str]) -> None:
        """
        Parse CLI overrides in format key=value.

        Args:
            overrides: List of "key=value" strings
        """
        for override in overrides:
            if "=" not in override:
                logger.warning(f"Invalid override format: {override}")
                continue

            key, value = override.split("=", 1)
            key = key.strip()
            value = self._parse_env_value(value.strip())
            self.set_cli_override(key, value)
            logger.info(f"CLI override: {key}={value}")

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Boolean
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String
        return value

    def get_theme_name(self) -> str:
        """Get current theme name."""
        return self.get("theme.name", "gruvbox")

    def get_theme_overrides(self) -> Dict[str, str]:
        """Get theme overrides."""
        return self.get("theme.overrides", {})

    def get_keybindings(self) -> Dict[str, list[str]]:
        """Get user keybindings."""
        return self.get("keybindings", {})

    def update_user_config(self, updates: Dict[str, Any]) -> None:
        """
        Update user config and save to file.

        Args:
            updates: Dictionary of updates (supports dot notation)
        """
        # Apply updates to user config
        for key, value in updates.items():
            parts = key.split(".")
            target = self._user_config

            for part in parts[:-1]:
                if hasattr(target, part):
                    target = getattr(target, part)
                else:
                    break

            if hasattr(target, parts[-1]):
                setattr(target, parts[-1], value)

        # Save to file
        self._save_user_config(self._user_config)


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> None:
    """Reload configuration from disk."""
    global _config_manager
    _config_manager = ConfigManager()
