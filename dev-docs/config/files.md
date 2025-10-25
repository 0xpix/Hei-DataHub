# Configuration Files

## Introduction

Hei-DataHub uses **TOML** configuration files for managing application settings. This document explains the configuration file structure, locations, and how settings are loaded.

---

## Configuration File Locations

### Primary Configuration File

**Location:** `~/.config/mini-datahub/config.toml`

**Purpose:** User-specific application configuration

**Created:** Automatically on first run with defaults

---

### System-wide Configuration (Optional)

**Location:** `/etc/mini-datahub/config.toml`

**Purpose:** System-wide defaults (for multi-user systems)

**Priority:** Lower than user config (user config overrides)

---

### Configuration Loading Order

```
1. System defaults (hardcoded in code)
           ↓
2. System config (/etc/mini-datahub/config.toml)
           ↓ (overrides)
3. User config (~/.config/mini-datahub/config.toml)
           ↓ (overrides)
4. Environment variables (HEI_DATAHUB_*)
           ↓ (overrides)
5. Command-line arguments
           ↓ (overrides, highest priority)
```

---

## Configuration File Structure

### Complete Example

```toml
# ~/.config/mini-datahub/config.toml

# ============================================
# WebDAV Configuration
# ============================================
[webdav]
base_url = "https://heibox.uni-heidelberg.de/remote.php/webdav"
library_path = "research-datasets"
timeout = 30
verify_ssl = true

# ============================================
# Sync Configuration
# ============================================
[sync]
auto_sync = true
sync_interval = 300  # seconds
retry_interval = 60
max_retries = 3
on_conflict = "last-write-wins"

# ============================================
# Search Configuration
# ============================================
[search]
max_results = 50
search_timeout = 5.0
enable_fuzzy = true
autocomplete_min_chars = 2
autocomplete_max_results = 10

# ============================================
# UI Configuration
# ============================================
[ui]
theme = "nord"
show_welcome = true
confirm_delete = true
results_per_page = 20

# ============================================
# Logging Configuration
# ============================================
[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_file = "~/.local/share/mini-datahub/logs/app.log"
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
max_log_size_mb = 10
backup_count = 5

# ============================================
# Database Configuration
# ============================================
[database]
path = "~/.local/share/mini-datahub/datasets.db"
backup_on_startup = true
vacuum_on_startup = false
```

---

## Configuration Sections

### 1. WebDAV Configuration

```toml
[webdav]
base_url = "https://heibox.uni-heidelberg.de/remote.php/webdav"
library_path = "research-datasets"
timeout = 30
verify_ssl = true
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | string | *(required)* | WebDAV server URL (HTTPS only) |
| `library_path` | string | `"research-datasets"` | Root folder path on WebDAV |
| `timeout` | integer | `30` | Connection timeout (seconds) |
| `verify_ssl` | boolean | `true` | Verify SSL certificates |

**Validation:**
- `base_url` must start with `https://`
- `library_path` cannot start with `/`
- `timeout` must be > 0

---

### 2. Sync Configuration

```toml
[sync]
auto_sync = true
sync_interval = 300
retry_interval = 60
max_retries = 3
on_conflict = "last-write-wins"
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_sync` | boolean | `true` | Enable background sync |
| `sync_interval` | integer | `300` | Sync frequency (seconds) |
| `retry_interval` | integer | `60` | Retry delay after failure (seconds) |
| `max_retries` | integer | `3` | Max retry attempts |
| `on_conflict` | string | `"last-write-wins"` | Conflict resolution strategy |

**Conflict Strategies:**
- `"last-write-wins"` - Newest timestamp wins (default)
- `"manual"` - Prompt user (future)

---

### 3. Search Configuration

```toml
[search]
max_results = 50
search_timeout = 5.0
enable_fuzzy = true
autocomplete_min_chars = 2
autocomplete_max_results = 10
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_results` | integer | `50` | Maximum search results |
| `search_timeout` | float | `5.0` | Search query timeout (seconds) |
| `enable_fuzzy` | boolean | `true` | Enable fuzzy matching |
| `autocomplete_min_chars` | integer | `2` | Min characters to trigger autocomplete |
| `autocomplete_max_results` | integer | `10` | Max autocomplete suggestions |

---

### 4. UI Configuration

```toml
[ui]
theme = "nord"
show_welcome = true
confirm_delete = true
results_per_page = 20
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `theme` | string | `"nord"` | UI color theme |
| `show_welcome` | boolean | `true` | Show welcome screen on startup |
| `confirm_delete` | boolean | `true` | Confirm before deleting datasets |
| `results_per_page` | integer | `20` | Results per page in list view |

**Available Themes:**
- `"nord"` - Nord color scheme (default)
- `"monokai"` - Monokai theme
- `"gruvbox"` - Gruvbox theme
- `"dracula"` - Dracula theme

---

### 5. Logging Configuration

```toml
[logging]
level = "INFO"
log_file = "~/.local/share/mini-datahub/logs/app.log"
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
max_log_size_mb = 10
backup_count = 5
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `level` | string | `"INFO"` | Logging level |
| `log_file` | string | `~/.local/share/.../app.log` | Log file path |
| `log_format` | string | *(see example)* | Python logging format string |
| `max_log_size_mb` | integer | `10` | Max log file size before rotation (MB) |
| `backup_count` | integer | `5` | Number of backup log files to keep |

**Log Levels:**
- `"DEBUG"` - Verbose debugging output
- `"INFO"` - General informational messages (default)
- `"WARNING"` - Warning messages
- `"ERROR"` - Error messages only
- `"CRITICAL"` - Critical errors only

---

### 6. Database Configuration

```toml
[database]
path = "~/.local/share/mini-datahub/datasets.db"
backup_on_startup = true
vacuum_on_startup = false
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | string | `~/.local/share/.../datasets.db` | SQLite database path |
| `backup_on_startup` | boolean | `true` | Create backup on app startup |
| `vacuum_on_startup` | boolean | `false` | Run VACUUM on startup (slow) |

---

## Loading Configuration

### Python API

```python
from mini_datahub.core.config import load_config

# Load configuration (merges all sources)
config = load_config()

# Access config values
print(config.webdav.base_url)
print(config.sync.auto_sync)
print(config.search.max_results)
```

---

### Implementation

```python
# src/mini_datahub/core/config.py

import toml
from pathlib import Path
from dataclasses import dataclass
import os

@dataclass
class WebDAVConfig:
    base_url: str
    library_path: str = "research-datasets"
    timeout: int = 30
    verify_ssl: bool = True

@dataclass
class SyncConfig:
    auto_sync: bool = True
    sync_interval: int = 300
    retry_interval: int = 60
    max_retries: int = 3
    on_conflict: str = "last-write-wins"

@dataclass
class SearchConfig:
    max_results: int = 50
    search_timeout: float = 5.0
    enable_fuzzy: bool = True
    autocomplete_min_chars: int = 2
    autocomplete_max_results: int = 10

@dataclass
class UIConfig:
    theme: str = "nord"
    show_welcome: bool = True
    confirm_delete: bool = True
    results_per_page: int = 20

@dataclass
class LoggingConfig:
    level: str = "INFO"
    log_file: str = "~/.local/share/mini-datahub/logs/app.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_log_size_mb: int = 10
    backup_count: int = 5

@dataclass
class DatabaseConfig:
    path: str = "~/.local/share/mini-datahub/datasets.db"
    backup_on_startup: bool = True
    vacuum_on_startup: bool = False

@dataclass
class Config:
    webdav: WebDAVConfig
    sync: SyncConfig
    search: SearchConfig
    ui: UIConfig
    logging: LoggingConfig
    database: DatabaseConfig

def load_config() -> Config:
    """Load configuration from multiple sources"""
    # 1. Start with defaults
    config_dict = get_default_config()
    
    # 2. Load system config (if exists)
    system_config_path = Path("/etc/mini-datahub/config.toml")
    if system_config_path.exists():
        system_config = toml.load(system_config_path)
        merge_config(config_dict, system_config)
    
    # 3. Load user config (if exists)
    user_config_path = get_config_path()
    if user_config_path.exists():
        user_config = toml.load(user_config_path)
        merge_config(config_dict, user_config)
    
    # 4. Override with environment variables
    apply_env_overrides(config_dict)
    
    # 5. Expand paths (e.g., ~ to home directory)
    expand_paths(config_dict)
    
    # 6. Validate configuration
    validate_config(config_dict)
    
    # 7. Create Config object
    return Config(
        webdav=WebDAVConfig(**config_dict["webdav"]),
        sync=SyncConfig(**config_dict["sync"]),
        search=SearchConfig(**config_dict["search"]),
        ui=UIConfig(**config_dict["ui"]),
        logging=LoggingConfig(**config_dict["logging"]),
        database=DatabaseConfig(**config_dict["database"])
    )

def get_config_path() -> Path:
    """Get user config file path"""
    config_dir = Path.home() / ".config" / "mini-datahub"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"

def create_default_config() -> None:
    """Create default config file if doesn't exist"""
    config_path = get_config_path()
    
    if config_path.exists():
        return
    
    default_config = get_default_config()
    
    with open(config_path, "w") as f:
        toml.dump(default_config, f)
    
    print(f"Created default configuration: {config_path}")
```

---

## Environment Variable Overrides

### Naming Convention

```
HEI_DATAHUB_<SECTION>_<KEY>
```

**Examples:**

```bash
# WebDAV configuration
export HEI_DATAHUB_WEBDAV_BASE_URL="https://seafile.example.com/seafdav"
export HEI_DATAHUB_WEBDAV_TIMEOUT="60"

# Sync configuration
export HEI_DATAHUB_SYNC_AUTO_SYNC="false"
export HEI_DATAHUB_SYNC_INTERVAL="600"

# Logging configuration
export HEI_DATAHUB_LOGGING_LEVEL="DEBUG"
```

---

### Implementation

```python
def apply_env_overrides(config_dict: dict) -> None:
    """Apply environment variable overrides"""
    prefix = "HEI_DATAHUB_"
    
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        
        # Parse key: HEI_DATAHUB_WEBDAV_BASE_URL → ["webdav", "base_url"]
        parts = key[len(prefix):].lower().split("_")
        
        if len(parts) < 2:
            continue
        
        section = parts[0]
        config_key = "_".join(parts[1:])
        
        if section not in config_dict:
            continue
        
        # Convert value to appropriate type
        current_value = config_dict[section].get(config_key)
        
        if isinstance(current_value, bool):
            # Convert "true"/"false" strings to boolean
            value = value.lower() in ("true", "1", "yes")
        elif isinstance(current_value, int):
            value = int(value)
        elif isinstance(current_value, float):
            value = float(value)
        
        config_dict[section][config_key] = value
```

---

## Validation

### Configuration Validation

```python
def validate_config(config_dict: dict) -> None:
    """Validate configuration values"""
    # Validate WebDAV URL
    webdav_url = config_dict["webdav"]["base_url"]
    if not webdav_url.startswith("https://"):
        raise ValueError("WebDAV URL must use HTTPS")
    
    # Validate sync interval
    if config_dict["sync"]["sync_interval"] < 60:
        raise ValueError("Sync interval must be at least 60 seconds")
    
    # Validate log level
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    log_level = config_dict["logging"]["level"]
    if log_level not in valid_levels:
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Validate theme
    valid_themes = {"nord", "monokai", "gruvbox", "dracula"}
    theme = config_dict["ui"]["theme"]
    if theme not in valid_themes:
        raise ValueError(f"Invalid theme: {theme}")
```

---

## Accessing Configuration

### In Services

```python
# src/mini_datahub/services/webdav_storage.py

from mini_datahub.core.config import load_config

class WebDAVStorage:
    def __init__(self):
        config = load_config()
        self.base_url = config.webdav.base_url
        self.library_path = config.webdav.library_path
        self.timeout = config.webdav.timeout
        self.verify_ssl = config.webdav.verify_ssl
```

---

### In CLI

```python
# src/mini_datahub/cli/commands.py

import argparse
from mini_datahub.core.config import load_config

def search_command(args: argparse.Namespace) -> None:
    config = load_config()
    
    # Use config values
    max_results = args.max_results or config.search.max_results
    
    # Perform search...
```

---

## Example Configurations

### Development Configuration

```toml
# ~/.config/mini-datahub/config.toml (dev)

[webdav]
base_url = "https://localhost:8080/webdav"
library_path = "test-datasets"
verify_ssl = false  # Local testing

[sync]
auto_sync = false  # Manual sync only
sync_interval = 600

[logging]
level = "DEBUG"
log_file = "./dev-logs/app.log"

[database]
path = "./dev-data/datasets.db"
backup_on_startup = false
```

---

### Production Configuration

```toml
# ~/.config/mini-datahub/config.toml (production)

[webdav]
base_url = "https://heibox.uni-heidelberg.de/remote.php/webdav"
library_path = "research-datasets"
timeout = 30
verify_ssl = true

[sync]
auto_sync = true
sync_interval = 300
max_retries = 5

[logging]
level = "INFO"
max_log_size_mb = 50
backup_count = 10

[database]
backup_on_startup = true
vacuum_on_startup = false
```

---

## Related Documentation

- **[Configuration Overview](overview.md)** - Configuration system overview
- **[Environment Variables](environment.md)** - Complete env var reference
- **[Adding Configuration](adding-config.md)** - How to add new config options

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
