# Configuration Overview

## Introduction

Hei-DataHub uses a layered configuration system with sensible defaults, environment variable overrides, and user configuration files. This document explains the configuration architecture and all available settings.

---

## Configuration Layers

**Configuration is loaded in this order (later sources override earlier ones):**

```
1. Built-in defaults      (hardcoded in code)
2. Config file            (~/.config/hei-datahub/config.toml)
3. Environment variables  (HEI_DATAHUB_*)
4. CLI arguments          (--config, --db-path, etc.)
```

**Example:**

```python
# 1. Default: sync interval = 5 minutes
DEFAULT_SYNC_INTERVAL = 5

# 2. Config file override: sync.interval_minutes = 10
config.toml:
  [sync]
  interval_minutes = 10

# 3. Environment variable override: HEI_DATAHUB_SYNC_INTERVAL=15
export HEI_DATAHUB_SYNC_INTERVAL=15

# 4. CLI argument override: --sync-interval 20
hei-datahub --sync-interval 20

# Final value: 20 minutes
```

---

## Configuration File

### Location

**Default path:** `~/.config/hei-datahub/config.toml`

**Override with environment variable:**
```bash
export HEI_DATAHUB_CONFIG_PATH=/custom/path/config.toml
```

**Override with CLI argument:**
```bash
hei-datahub --config /custom/path/config.toml
```

---

### Format

**File format:** TOML (Tom's Obvious Minimal Language)

**Why TOML?**
- Human-readable and editable
- Supports complex nested structures
- Strong typing (strings, integers, booleans, arrays)
- Better than JSON for config files (supports comments)

**Example config.toml:**

```toml
# Hei-DataHub Configuration

[webdav]
url = "https://heibox.uni-heidelberg.de"
library = "research-datasets"
key_id = "webdav-heibox-research"  # Reference to keyring entry

[sync]
enabled = true
interval_minutes = 5
auto_sync_on_startup = true

[search]
debounce_ms = 300
max_results = 50
highlight_matches = true

[ui]
theme = "dark"
show_help_on_startup = false

[logging]
level = "INFO"
file = "~/.local/share/hei-datahub/logs/app.log"
max_size_mb = 10
backup_count = 3
```

---

## Configuration Sections

### 1. WebDAV Configuration

**Section:** `[webdav]`

**Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `url` | string | (required) | WebDAV server URL (HTTPS only) |
| `library` | string | (required) | Library/folder name on server |
| `key_id` | string | (auto-generated) | Keyring entry ID for credentials |
| `timeout` | integer | `10` | Request timeout in seconds |
| `verify_ssl` | boolean | `true` | Verify SSL certificates |

**Example:**

```toml
[webdav]
url = "https://heibox.uni-heidelberg.de"
library = "research-datasets"
key_id = "webdav-heibox-research"
timeout = 15
verify_ssl = true
```

**Security Notes:**
- ❌ **Never** store credentials (tokens/passwords) in config file
- ✅ Credentials stored in OS keyring (encrypted)
- ✅ `key_id` is a reference to keyring entry
- ✅ HTTPS enforced (HTTP rejected)

---

### 2. Sync Configuration

**Section:** `[sync]`

**Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | boolean | `true` | Enable background sync |
| `interval_minutes` | integer | `5` | Sync interval in minutes |
| `auto_sync_on_startup` | boolean | `true` | Sync immediately on app start |
| `conflict_resolution` | string | `"last-write-wins"` | Conflict resolution strategy |
| `max_retries` | integer | `5` | Max upload retry attempts |

**Example:**

```toml
[sync]
enabled = true
interval_minutes = 5
auto_sync_on_startup = true
conflict_resolution = "last-write-wins"
max_retries = 5
```

**Sync Intervals:**
- **Minimum:** 1 minute
- **Recommended:** 5 minutes (default)
- **Maximum:** No limit (set to 0 to disable timer-based sync)

**Conflict Resolution Strategies:**
- `last-write-wins` (default): Use newest timestamp
- `manual` (future): Prompt user for resolution

---

### 3. Search Configuration

**Section:** `[search]`

**Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `debounce_ms` | integer | `300` | Input debounce delay (milliseconds) |
| `max_results` | integer | `50` | Maximum search results to display |
| `highlight_matches` | boolean | `true` | Highlight search terms in results |
| `fuzzy_threshold` | float | `0.7` | Fuzzy match threshold (0.0-1.0) |
| `autocomplete_enabled` | boolean | `true` | Enable search autocomplete |

**Example:**

```toml
[search]
debounce_ms = 300
max_results = 50
highlight_matches = true
fuzzy_threshold = 0.7
autocomplete_enabled = true
```

**Debounce Explanation:**
- Lower value (100ms): More responsive but more queries
- Higher value (500ms): Fewer queries but feels slower
- Recommended: 300ms (good balance)

---

### 4. UI Configuration

**Section:** `[ui]`

**Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `theme` | string | `"dark"` | Color theme (`dark` or `light`) |
| `show_help_on_startup` | boolean | `false` | Show help screen on first launch |
| `animation_enabled` | boolean | `true` | Enable UI animations |
| `font_size` | integer | `12` | Terminal font size (hint) |

**Example:**

```toml
[ui]
theme = "dark"
show_help_on_startup = false
animation_enabled = true
```

**Available Themes:**
- `dark` (default): Dark background, light text
- `light`: Light background, dark text

---

### 5. Logging Configuration

**Section:** `[logging]`

**Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `level` | string | `"INFO"` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `file` | string | `~/.local/share/hei-datahub/logs/app.log` | Log file path |
| `max_size_mb` | integer | `10` | Max log file size before rotation |
| `backup_count` | integer | `3` | Number of rotated log files to keep |
| `format` | string | (default) | Log format string |

**Example:**

```toml
[logging]
level = "INFO"
file = "~/.local/share/hei-datahub/logs/app.log"
max_size_mb = 10
backup_count = 3
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Log Levels:**
- `DEBUG`: Verbose debugging information
- `INFO`: General informational messages
- `WARNING`: Warning messages (potential issues)
- `ERROR`: Error messages (failures)

---

### 6. Database Configuration

**Section:** `[database]`

**Settings:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `path` | string | `~/.local/share/hei-datahub/db.sqlite` | Database file path |
| `cache_size_mb` | integer | `64` | SQLite cache size |
| `wal_mode` | boolean | `true` | Enable Write-Ahead Logging |
| `auto_vacuum` | boolean | `true` | Enable automatic vacuuming |

**Example:**

```toml
[database]
path = "~/.local/share/hei-datahub/db.sqlite"
cache_size_mb = 64
wal_mode = true
auto_vacuum = true
```

---

## Environment Variables

**All settings can be overridden via environment variables:**

**Naming convention:** `HEI_DATAHUB_<SECTION>_<KEY>`

**Examples:**

```bash
# WebDAV settings
export HEI_DATAHUB_WEBDAV_URL="https://custom.server.com"
export HEI_DATAHUB_WEBDAV_LIBRARY="my-library"

# Sync settings
export HEI_DATAHUB_SYNC_ENABLED=false
export HEI_DATAHUB_SYNC_INTERVAL_MINUTES=10

# Search settings
export HEI_DATAHUB_SEARCH_DEBOUNCE_MS=500
export HEI_DATAHUB_SEARCH_MAX_RESULTS=100

# Logging
export HEI_DATAHUB_LOGGING_LEVEL=DEBUG
export HEI_DATAHUB_LOGGING_FILE=/tmp/hei-datahub.log

# Database
export HEI_DATAHUB_DATABASE_PATH=/tmp/test.db
```

**Type conversion:**
- Booleans: `true`, `false`, `1`, `0`, `yes`, `no`
- Integers: Numeric strings
- Strings: Raw values

---

## CLI Arguments

**Common CLI overrides:**

```bash
# Config file location
hei-datahub --config /path/to/config.toml

# Database path
hei-datahub --db-path /path/to/db.sqlite

# Log level
hei-datahub --log-level DEBUG

# Disable sync
hei-datahub --no-sync

# Custom sync interval
hei-datahub --sync-interval 10
```

---

## Default Values

**Complete list of defaults:**

```python
DEFAULT_CONFIG = {
    "webdav": {
        "url": None,  # Must be configured
        "library": None,  # Must be configured
        "key_id": None,  # Auto-generated
        "timeout": 10,
        "verify_ssl": True,
    },
    "sync": {
        "enabled": True,
        "interval_minutes": 5,
        "auto_sync_on_startup": True,
        "conflict_resolution": "last-write-wins",
        "max_retries": 5,
    },
    "search": {
        "debounce_ms": 300,
        "max_results": 50,
        "highlight_matches": True,
        "fuzzy_threshold": 0.7,
        "autocomplete_enabled": True,
    },
    "ui": {
        "theme": "dark",
        "show_help_on_startup": False,
        "animation_enabled": True,
        "font_size": 12,
    },
    "logging": {
        "level": "INFO",
        "file": "~/.local/share/hei-datahub/logs/app.log",
        "max_size_mb": 10,
        "backup_count": 3,
    },
    "database": {
        "path": "~/.local/share/hei-datahub/db.sqlite",
        "cache_size_mb": 64,
        "wal_mode": True,
        "auto_vacuum": True,
    },
}
```

---

## Configuration API

### Loading Configuration

```python
from mini_datahub.services.config import load_config

# Load configuration
config = load_config()

# Access settings
webdav_url = config["webdav"]["url"]
sync_enabled = config["sync"]["enabled"]
```

### Saving Configuration

```python
from mini_datahub.services.config import save_config

# Update configuration
config["sync"]["interval_minutes"] = 10
save_config(config)
```

### Getting Single Values

```python
from mini_datahub.services.config import get_config_value

# Get with default
sync_interval = get_config_value("sync.interval_minutes", default=5)
```

---

## Validation

**Configuration is validated on load:**

```python
def validate_config(config: dict) -> None:
    """Validate configuration"""
    # WebDAV URL must be HTTPS
    webdav_url = config.get("webdav", {}).get("url")
    if webdav_url and not webdav_url.startswith("https://"):
        raise ValueError("WebDAV URL must use HTTPS")
    
    # Sync interval must be positive
    sync_interval = config.get("sync", {}).get("interval_minutes")
    if sync_interval is not None and sync_interval < 1:
        raise ValueError("Sync interval must be at least 1 minute")
    
    # Log level must be valid
    log_level = config.get("logging", {}).get("level")
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        raise ValueError(f"Invalid log level: {log_level}")
```

---

## Best Practices

### 1. Use Config File for Persistent Settings

```toml
# ✅ GOOD: Store in config file
[webdav]
url = "https://heibox.uni-heidelberg.de"
library = "research-datasets"
```

```bash
# ❌ BAD: Set every time via CLI
hei-datahub --webdav-url https://... --library ...
```

### 2. Use Environment Variables for CI/CD

```bash
# ✅ GOOD: CI environment
export HEI_DATAHUB_WEBDAV_URL=$WEBDAV_URL
export HEI_DATAHUB_SYNC_ENABLED=false
hei-datahub validate --all
```

### 3. Never Store Secrets in Config

```toml
# ❌ WRONG: Never do this!
[webdav]
token = "my-secret-token"

# ✅ CORRECT: Use keyring
[webdav]
key_id = "webdav-heibox-research"  # Reference only
```

---

## Troubleshooting

### Config File Not Found

```bash
hei-datahub auth doctor
# Check: Config file exists
```

**Fix:**
```bash
# Create default config
mkdir -p ~/.config/hei-datahub
hei-datahub auth setup
```

### Invalid Configuration

```bash
# Error: ValueError: WebDAV URL must use HTTPS
```

**Fix:**
```toml
# Change HTTP to HTTPS
[webdav]
url = "https://heibox.uni-heidelberg.de"  # Not http://
```

### Environment Variable Not Working

```bash
# Not working
export HEI_DATAHUB_SYNC_INTERVAL=10
```

**Fix:**
```bash
# Correct naming (use underscores, not dashes)
export HEI_DATAHUB_SYNC_INTERVAL_MINUTES=10
```

---

## Related Documentation

- **[Configuration Files](files.md)** - Detailed file structure
- **[Environment Variables](environment.md)** - Complete env var reference
- **[Adding Configuration](adding-config.md)** - How to add new config options

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
