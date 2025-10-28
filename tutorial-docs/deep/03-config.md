# Deep Dive: Configuration System

**Learning Goal**: Master the configuration hierarchy and settings management.

By the end of this page, you'll:
- Understand configuration precedence
- Work with TOML config files
- Handle platform-specific paths
- Override settings via environment variables
- Build settings UI screens
- Validate and migrate configs

---

## Why Configuration Matters

**Problem:** Users need different settings:

```
Developer     → Debug logging, local data dir
Production    → Cloud sync, auto-updates
CI/CD         → ENV variables, headless mode
```

**Solution:** Hierarchical configuration with multiple override levels.

---

## Configuration Hierarchy

```
┌────────────────────────────────────────┐
│  1. CLI Arguments (highest priority)   │
│     --data-dir=/custom/path            │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  2. Environment Variables              │
│     HEIDATAHUB_DATA_DIR=/path          │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  3. User Config File                   │
│     ~/.config/hei-datahub/config.toml  │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  4. Built-in Defaults (lowest)         │
│     Hard-coded in application          │
└────────────────────────────────────────┘
```

**Precedence:** Higher levels override lower levels.

---

## Platform-Specific Paths

**File:** `src/hei_datahub/infra/platform_paths.py`

### OS Detection

```python
import platform

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
```

---

### OS-Specific Defaults

**Goal:** Follow platform conventions.

```python
from pathlib import Path
import os

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
        # Linux: ~/.local/share/Hei-DataHub (XDG Base Directory)
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            return Path(xdg_data_home) / "Hei-DataHub"
        return Path.home() / ".local" / "share" / "Hei-DataHub"
```

**Platform conventions:**

| Platform | Data Directory |
|----------|---------------|
| Linux | `~/.local/share/Hei-DataHub` (XDG) |
| macOS | `~/Library/Application Support/Hei-DataHub` |
| Windows | `%LOCALAPPDATA%\Hei-DataHub` |

---

### XDG Base Directory (Linux)

**Specification:** [freedesktop.org](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)

```python
# Data directory
XDG_DATA_HOME = ~/.local/share  (default)
# Config directory
XDG_CONFIG_HOME = ~/.config     (default)
# Cache directory
XDG_CACHE_HOME = ~/.cache       (default)
```

**Example:**

```python
xdg_data_home = os.environ.get('XDG_DATA_HOME')
if xdg_data_home:
    data_dir = Path(xdg_data_home) / "Hei-DataHub"
else:
    data_dir = Path.home() / ".local" / "share" / "Hei-DataHub"
```

---

### Directory Resolution with Override

**Goal:** Respect CLI and ENV overrides.

```python
from typing import Tuple, Optional

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
```

**Usage:**

```python
# From CLI: hei-datahub --data-dir=/tmp/data
data_dir, source = resolve_data_directory(cli_override="/tmp/data")
# → (Path('/tmp/data'), 'cli')

# From ENV: HEIDATAHUB_DATA_DIR=/opt/data
data_dir, source = resolve_data_directory()
# → (Path('/opt/data'), 'env')

# Default
data_dir, source = resolve_data_directory()
# → (Path('/home/user/.local/share/Hei-DataHub'), 'default')
```

---

## Config File Paths

**File:** `src/hei_datahub/infra/config_paths.py`

### User Config Directory

```python
from pathlib import Path
import os

def get_user_config_dir() -> Path:
    """
    Get the user configuration directory for Hei-DataHub.

    Follows XDG Base Directory specification:
    - Uses $XDG_CONFIG_HOME/hei-datahub if set
    - Falls back to ~/.config/hei-datahub
    - Can be overridden with $HEIDH_CONFIG_DIR

    Returns:
        Path to config directory
    """
    # Check for environment variable override (highest priority)
    if config_dir := os.getenv("HEIDH_CONFIG_DIR"):
        return Path(config_dir).expanduser()

    # Follow XDG Base Directory specification
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / "hei-datahub"

    # Default to ~/.config/hei-datahub (XDG standard)
    return Path.home() / ".config" / "hei-datahub"


def ensure_user_config_dir() -> Path:
    """
    Ensure the user config directory exists and return its path.

    Returns:
        Path to the created/existing config directory
    """
    config_dir = get_user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
```

---

### Config File Paths

```python
def get_config_path() -> Path:
    """
    Get the path to the TOML config file for auth and other settings.

    Returns:
        Path to ~/.config/hei-datahub/config.toml
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
```

**File structure:**

```
~/.config/hei-datahub/
├── config.toml          # Main config (auth, settings)
└── keybindings.yaml     # Custom keybindings
```

---

## TOML Configuration Format

**File:** `~/.config/hei-datahub/config.toml`

### Auth Section

```toml
[auth]
method = "webdav"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "alice"
library = "Testing-hei-datahub"
stored_in = "keyring"
key_id = "webdav:password:alice@heibox.uni-heidelberg.de"
```

**Fields:**
- `method` — Authentication method (`"webdav"`)
- `url` — WebDAV base URL
- `username` — Username (optional for anonymous)
- `library` — Library/folder name in WebDAV
- `stored_in` — Credential storage (`"keyring"` or `"env"`)
- `key_id` — Key for retrieving credential

---

### Settings Section

```toml
[settings]
auto_check_updates = true
suggest_from_catalog_values = true
background_fetch_interval_minutes = 0
debug_logging = false

[search]
max_results = 50
highlight_matches = true

[ui]
theme = "dark"
vim_mode = true
```

---

### Loading TOML Config

```python
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python

from pathlib import Path

def load_config(config_path: Path) -> dict:
    """
    Load TOML configuration file.

    Args:
        config_path: Path to config.toml

    Returns:
        Dictionary of config values
    """
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return {}
```

**Usage:**

```python
from hei_datahub.infra.config_paths import get_config_path

config_path = get_config_path()
config = load_config(config_path)

auth_config = config.get("auth", {})
url = auth_config.get("url", "https://heibox.uni-heidelberg.de/seafdav")
```

---

### Writing TOML Config

```python
import tomli_w  # pip install tomli-w

def save_config(config_path: Path, config: dict) -> None:
    """
    Save configuration to TOML file.

    Args:
        config_path: Path to config.toml
        config: Dictionary of config values
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)
```

**Usage:**

```python
from hei_datahub.infra.config_paths import get_config_path

config = {
    "auth": {
        "method": "webdav",
        "url": "https://heibox.uni-heidelberg.de/seafdav",
        "username": "alice",
        "library": "my-library",
        "stored_in": "keyring",
        "key_id": "webdav:password:alice@heibox.uni-heidelberg.de",
    },
    "settings": {
        "auto_check_updates": True,
        "debug_logging": False,
    },
}

config_path = get_config_path()
save_config(config_path, config)
```

---

## Settings Models (Pydantic)

**File:** `src/hei_datahub/app/settings.py`

**Goal:** Type-safe configuration with validation.

### Settings Class

```python
from pydantic import BaseModel, Field
from typing import Optional

class SearchSettings(BaseModel):
    """Search-related settings."""
    max_results: int = Field(default=50, ge=1, le=1000)
    highlight_matches: bool = True
    fuzzy_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class UISettings(BaseModel):
    """UI-related settings."""
    theme: str = Field(default="dark", pattern="^(dark|light)$")
    vim_mode: bool = False
    show_help_on_startup: bool = True


class Settings(BaseModel):
    """Application settings."""
    auto_check_updates: bool = True
    suggest_from_catalog_values: bool = True
    background_fetch_interval_minutes: int = Field(default=0, ge=0)
    debug_logging: bool = False

    search: SearchSettings = Field(default_factory=SearchSettings)
    ui: UISettings = Field(default_factory=UISettings)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Settings":
        """
        Load settings from config file.

        Args:
            config_path: Path to config.toml (if None, use default)

        Returns:
            Settings instance
        """
        if config_path is None:
            from hei_datahub.infra.config_paths import get_config_path
            config_path = get_config_path()

        if not config_path.exists():
            # Return defaults
            return cls()

        # Load TOML
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        with open(config_path, "rb") as f:
            config = tomllib.load(f)

        # Extract settings section
        settings_data = config.get("settings", {})

        # Merge with defaults
        return cls(**settings_data)

    def save(self, config_path: Optional[Path] = None) -> None:
        """
        Save settings to config file.

        Args:
            config_path: Path to config.toml (if None, use default)
        """
        if config_path is None:
            from hei_datahub.infra.config_paths import get_config_path
            config_path = get_config_path()

        # Load existing config (to preserve auth section)
        existing_config = load_config(config_path)

        # Update settings section
        existing_config["settings"] = self.model_dump()

        # Write back
        import tomli_w
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "wb") as f:
            tomli_w.dump(existing_config, f)
```

**Usage:**

```python
from hei_datahub.app.settings import Settings

# Load settings
settings = Settings.load()

print(settings.search.max_results)  # 50
print(settings.ui.theme)            # "dark"

# Modify and save
settings.debug_logging = True
settings.search.max_results = 100
settings.save()
```

---

## Environment Variable Overrides

**Pattern:** `HEIDATAHUB_<SECTION>_<SETTING>`

### Examples

```bash
# Data directory
export HEIDATAHUB_DATA_DIR="/opt/hei-datahub/data"

# Debug logging
export HEIDATAHUB_DEBUG_LOGGING="true"

# Max search results
export HEIDATAHUB_SEARCH_MAX_RESULTS="100"

# WebDAV token (from auth setup)
export HEIDATAHUB_WEBDAV_TOKEN="secret123"
```

---

### Parsing ENV Variables

```python
import os
from typing import Any

def get_env_override(key: str, default: Any = None) -> Any:
    """
    Get environment variable override for setting.

    Args:
        key: Setting key (e.g., "search.max_results")
        default: Default value if not set

    Returns:
        Value from environment or default
    """
    # Convert key to env var name
    # "search.max_results" → "HEIDATAHUB_SEARCH_MAX_RESULTS"
    env_name = "HEIDATAHUB_" + key.upper().replace(".", "_")

    value = os.environ.get(env_name)
    if value is None:
        return default

    # Type conversion
    if isinstance(default, bool):
        return value.lower() in ("true", "1", "yes")
    elif isinstance(default, int):
        return int(value)
    elif isinstance(default, float):
        return float(value)
    else:
        return value
```

**Usage:**

```python
# Check for ENV override
max_results = get_env_override("search.max_results", default=50)
debug = get_env_override("debug_logging", default=False)
```

---

## Windows Filename Sanitization

**Problem:** Windows has strict filename rules.

### Invalid Characters

**Illegal:** `\ / : * ? " < > |`

**Reserved names:**
- `CON`, `PRN`, `AUX`, `NUL`
- `COM1` - `COM9`
- `LPT1` - `LPT9`

---

### Sanitization Function

```python
import re

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
```

**Examples:**

```python
sanitize_windows_filename("my:dataset")      # → "my_dataset"
sanitize_windows_filename("data<2024>.yaml") # → "data_2024_.yaml"
sanitize_windows_filename("CON")             # → "CON_file"
sanitize_windows_filename("file.")           # → "file"
```

---

## Settings UI Screen

**Goal:** Let users edit settings in TUI.

### Settings Screen

```python
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Switch, Input, Button
from textual.containers import Vertical, Horizontal

class SettingsScreen(Screen):
    """Settings editor screen."""

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("⚙️  Settings", classes="title")

            # Auto-check updates
            with Horizontal():
                yield Static("Auto-check for updates:")
                yield Switch(id="auto_check_updates", value=True)

            # Debug logging
            with Horizontal():
                yield Static("Enable debug logging:")
                yield Switch(id="debug_logging", value=False)

            # Max search results
            with Horizontal():
                yield Static("Max search results:")
                yield Input(value="50", id="max_results")

            # Theme
            with Horizontal():
                yield Static("Theme:")
                yield Input(value="dark", id="theme")

            # Buttons
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

        yield Footer()

    def on_mount(self) -> None:
        """Load settings when screen mounts."""
        from hei_datahub.app.settings import Settings

        self.settings = Settings.load()

        # Populate fields
        self.query_one("#auto_check_updates", Switch).value = self.settings.auto_check_updates
        self.query_one("#debug_logging", Switch).value = self.settings.debug_logging
        self.query_one("#max_results", Input).value = str(self.settings.search.max_results)
        self.query_one("#theme", Input).value = self.settings.ui.theme

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "save":
            # Read values
            self.settings.auto_check_updates = self.query_one("#auto_check_updates", Switch).value
            self.settings.debug_logging = self.query_one("#debug_logging", Switch).value
            self.settings.search.max_results = int(self.query_one("#max_results", Input).value)
            self.settings.ui.theme = self.query_one("#theme", Input).value

            # Save
            self.settings.save()

            self.app.notify("✓ Settings saved")
            self.app.pop_screen()

        elif event.button.id == "cancel":
            self.app.pop_screen()
```

**Usage:**

```python
from hei_datahub.ui.views.settings import SettingsScreen

# In HomeScreen action
def action_open_settings(self) -> None:
    """Open settings screen."""
    self.app.push_screen(SettingsScreen())
```

---

## Config Migration

**Goal:** Handle config format changes across versions.

### Migration Example

```python
def migrate_config(config: dict, from_version: str, to_version: str) -> dict:
    """
    Migrate config from one version to another.

    Args:
        config: Current config dict
        from_version: Source version (e.g., "0.60.0")
        to_version: Target version (e.g., "0.61.0")

    Returns:
        Migrated config dict
    """
    migrations = {
        ("0.60.0", "0.61.0"): _migrate_0_60_to_0_61,
    }

    migration_fn = migrations.get((from_version, to_version))
    if migration_fn:
        return migration_fn(config)

    return config


def _migrate_0_60_to_0_61(config: dict) -> dict:
    """
    Migrate from v0.60 to v0.61.

    Changes:
    - Rename "github.token" → "auth.key_id"
    - Move "search_limit" → "search.max_results"
    """
    migrated = config.copy()

    # Move github token to auth
    if "github" in migrated:
        github_config = migrated.pop("github")
        if "token" in github_config:
            migrated.setdefault("auth", {})
            migrated["auth"]["key_id"] = github_config["token"]

    # Move search limit
    if "search_limit" in migrated:
        limit = migrated.pop("search_limit")
        migrated.setdefault("search", {})
        migrated["search"]["max_results"] = limit

    return migrated
```

**Usage:**

```python
# Load config
config = load_config(config_path)

# Check version
config_version = config.get("version", "0.60.0")
if config_version != CURRENT_VERSION:
    # Migrate
    config = migrate_config(config, config_version, CURRENT_VERSION)
    config["version"] = CURRENT_VERSION

    # Save migrated config
    save_config(config_path, config)
```

---

## What You've Learned

✅ **Configuration hierarchy** — CLI → ENV → Config file → Defaults
✅ **Platform-specific paths** — XDG (Linux), Application Support (macOS), AppData (Windows)
✅ **TOML format** — Type-safe config with tomllib/tomli
✅ **Pydantic settings** — Validated settings models
✅ **ENV overrides** — `HEIDATAHUB_*` variables
✅ **Windows sanitization** — Filename safety
✅ **Settings UI** — TUI screen for editing config
✅ **Config migration** — Version-aware upgrades

---

## Next Steps

Now let's explore the FTS5 indexing system internals.

**Next:** [FTS5 Indexing Deep Dive](04-indexing.md)

---

## Further Reading

- [XDG Base Directory Spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [TOML Format](https://toml.io/)
- [Pydantic Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
