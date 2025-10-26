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


class LogoConfig(BaseModel):
    """Logo configuration."""
    path: Optional[str] = None  # User override path
    align: str = Field(default="center")  # left | center | right
    color: str = Field(default="cyan")  # color name or theme token
    padding_top: int = Field(default=0, ge=0)
    padding_bottom: int = Field(default=1, ge=0)
    show_version_tag: bool = Field(default=True)  # Show version tag under logo
    version_format: str = Field(default="v{version} — {codename}")  # Format string for version tag
    version_style: Optional[str] = Field(default="accent")  # Rich markup style for version tag


class ThemeConfig(BaseModel):
    """Theme configuration."""
    name: str = Field(default="catppuccin-mocha")
    overrides: Dict[str, str] = Field(default_factory=dict)
    stylesheets: list[str] = Field(default_factory=list)  # User TCSS files
    tokens: Optional[str] = None  # Path to tokens YAML file
    stylesheets: list[str] = Field(default_factory=list)  # User TCSS files
    tokens: Optional[str] = None  # Path to tokens YAML file

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


class UIConfig(BaseModel):
    """UI customization configuration."""
    logo: LogoConfig = Field(default_factory=LogoConfig)
    help_file: Optional[str] = None  # Optional external help file


class StorageConfig(BaseModel):
    """Storage backend configuration for cloud/remote access."""
    backend: str = Field(default="filesystem")  # "filesystem" | "webdav"
    base_url: Optional[str] = None  # WebDAV base URL (e.g., https://heibox.uni-heidelberg.de/seafdav)
    library: Optional[str] = None  # Library/folder name (e.g., testing-hei-datahub)
    username: Optional[str] = None  # WebDAV username (empty = use env)
    password_env: str = Field(default="HEIBOX_WEBDAV_TOKEN")  # Env var name for password/token
    data_dir: Optional[str] = None  # Filesystem mode: local data directory
    connect_timeout: int = Field(default=5, ge=1, le=30)  # Connection timeout in seconds
    read_timeout: int = Field(default=60, ge=10, le=300)  # Read timeout in seconds
    max_retries: int = Field(default=3, ge=0, le=10)  # Max retry attempts on 5xx errors

    @field_validator("backend")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate storage backend type."""
        allowed = {"filesystem", "webdav"}
        if v not in allowed:
            logger.warning(f"Unknown storage backend '{v}', falling back to 'filesystem'. Available: {', '.join(sorted(allowed))}")
            return "filesystem"
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
    config_version: int = Field(default=2)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
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

                # Migrate config if needed
                data = self._migrate_config(data)

                logger.info(f"Loaded user config from {config_file}")
                config = UserConfig(**data)

                # Save migrated config if version changed
                if data.get("config_version", 1) < 2:
                    logger.info("Migrating config to version 2")
                    self._save_user_config(config)

                return config
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

    def _migrate_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate config from v1 to v2 non-destructively."""
        current_version = data.get("config_version", 1)

        if current_version < 2:
            # Add v2 fields if they don't exist
            if "ui" not in data:
                data["ui"] = {
                    "logo": {
                        "path": None,  # Will use packaged default
                        "align": "center",
                        "color": "cyan",
                        "padding_top": 0,
                        "padding_bottom": 1,
                        "show_version_tag": True,
                        "version_format": "v{version} — {codename}",
                        "version_style": "accent"
                    }
                }
            else:
                # Ensure logo section exists and has new fields
                if "logo" not in data["ui"]:
                    data["ui"]["logo"] = {}

                logo = data["ui"]["logo"]
                if "show_version_tag" not in logo:
                    logo["show_version_tag"] = True
                if "version_format" not in logo:
                    logo["version_format"] = "v{version} — {codename}"
                if "version_style" not in logo:
                    logo["version_style"] = "accent"

            # Add theme.stylesheets and theme.tokens if not present
            if "theme" in data:
                if "stylesheets" not in data["theme"]:
                    data["theme"]["stylesheets"] = []
                if "tokens" not in data["theme"]:
                    data["theme"]["tokens"] = None

            # Add storage section if not present
            if "storage" not in data:
                data["storage"] = {
                    "backend": "filesystem",
                    "base_url": None,
                    "library": None,
                    "username": None,
                    "password_env": "HEIBOX_WEBDAV_TOKEN",
                    "data_dir": None,
                    "connect_timeout": 5,
                    "read_timeout": 60,
                    "max_retries": 3,
                }

            # Update version
            data["config_version"] = 2
            logger.info("Migrated config from v1 to v2")

        return data

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

                # Write UI section
                f.write("# UI Customization\n")
                f.write("ui:\n")
                f.write("  logo:\n")
                f.write(f"    path: {data['ui']['logo'].get('path') or 'null'}  # Custom logo path (null = use default)\n")
                f.write(f"    align: {data['ui']['logo']['align']}  # left | center | right\n")
                f.write(f"    color: {data['ui']['logo']['color']}  # color name\n")
                f.write(f"    padding_top: {data['ui']['logo']['padding_top']}\n")
                f.write(f"    padding_bottom: {data['ui']['logo']['padding_bottom']}\n")
                f.write(f"    show_version_tag: {str(data['ui']['logo'].get('show_version_tag', True)).lower()}  # Show version tag under logo\n")
                f.write(f"    version_format: \"{data['ui']['logo'].get('version_format', 'v{version} — {codename}')}\"  # Format: {{version}} {{codename}}\n")
                f.write(f"    version_style: {data['ui']['logo'].get('version_style') or 'accent'}  # Rich markup style (accent, cyan, etc.)\n")
                if data['ui'].get('help_file'):
                    f.write(f"  help_file: {data['ui']['help_file']}\n")
                f.write("\n")

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
                f.write("  stylesheets: []  # List of custom TCSS file paths\n")
                f.write("  tokens: null     # Path to design tokens YAML (optional)\n")
                f.write("  stylesheets: []  # List of custom TCSS file paths\n")
                f.write("  tokens: null     # Path to design tokens YAML (optional)\n")
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

                # Write storage section
                f.write("# Storage backend (webdav for cloud, filesystem for local)\n")
                f.write("storage:\n")
                f.write(f"  backend: {data['storage']['backend']}  # filesystem | webdav\n")
                f.write(f"  base_url: {data['storage'].get('base_url') or 'null'}  # WebDAV URL (e.g., https://heibox.uni-heidelberg.de/seafdav)\n")
                f.write(f"  library: {data['storage'].get('library') or 'null'}  # Library/folder name\n")
                f.write(f"  username: {data['storage'].get('username') or 'null'}  # WebDAV username (empty = use env)\n")
                f.write(f"  password_env: {data['storage']['password_env']}  # Env var for token/password\n")
                f.write(f"  data_dir: {data['storage'].get('data_dir') or 'null'}  # Filesystem mode only\n")
                f.write(f"  connect_timeout: {data['storage']['connect_timeout']}  # seconds\n")
                f.write(f"  read_timeout: {data['storage']['read_timeout']}  # seconds\n")
                f.write(f"  max_retries: {data['storage']['max_retries']}  # retry attempts\n")
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

    def get_logo_config(self) -> Dict[str, Any]:
        """Get logo configuration with defaults."""
        return {
            "path": self.get("ui.logo.path"),
            "align": self.get("ui.logo.align", "center"),
            "color": self.get("ui.logo.color", "cyan"),
            "padding_top": self.get("ui.logo.padding_top", 0),
            "padding_bottom": self.get("ui.logo.padding_bottom", 1),
            "show_version_tag": self.get("ui.logo.show_version_tag", True),
            "version_format": self.get("ui.logo.version_format", "v{version} — {codename}"),
            "version_style": self.get("ui.logo.version_style", "accent"),
        }

    def get_stylesheets(self) -> list[str]:
        """Get user-defined stylesheets."""
        return self.get("theme.stylesheets", [])

    def get_theme_tokens_path(self) -> Optional[str]:
        """Get path to theme tokens file."""
        return self.get("theme.tokens")

    def get_help_file_path(self) -> Optional[str]:
        """Get path to custom help file."""
        return self.get("ui.help_file")

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

    def reload_config(self) -> None:
        """
        Reload configuration from file.

        This is useful when config file has been modified externally
        or when you want to pick up changes after updating config.
        """
        self._user_config = self._load_user_config()
        # Clear CLI overrides as they should only apply to current session
        # (don't clear them - they persist for the session)


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> ConfigManager:
    """
    Reload the global config manager from file.

    This forces a complete reload of the configuration,
    picking up any changes made to the config file.

    Returns:
        The reloaded config manager instance
    """
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> None:
    """Reload configuration from disk."""
    global _config_manager
    _config_manager = ConfigManager()
