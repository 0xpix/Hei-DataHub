# Environment Variables

## Introduction

Hei-DataHub supports environment variable overrides for all configuration settings. This allows flexible deployment without modifying config files.

---

## Naming Convention

### Format

```
HEI_DATAHUB_<SECTION>_<KEY>
```

- **Prefix:** `HEI_DATAHUB_`
- **Section:** Configuration section (uppercase)
- **Key:** Configuration key (uppercase, underscores for multi-word keys)

---

## Complete Reference

### WebDAV Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_WEBDAV_BASE_URL` | `webdav.base_url` | string | *(required)* | WebDAV server URL |
| `HEI_DATAHUB_WEBDAV_LIBRARY_PATH` | `webdav.library_path` | string | `"research-datasets"` | Library root folder |
| `HEI_DATAHUB_WEBDAV_TIMEOUT` | `webdav.timeout` | integer | `30` | Connection timeout (seconds) |
| `HEI_DATAHUB_WEBDAV_VERIFY_SSL` | `webdav.verify_ssl` | boolean | `true` | Verify SSL certificates |

**Examples:**

```bash
export HEI_DATAHUB_WEBDAV_BASE_URL="https://heibox.uni-heidelberg.de/remote.php/webdav"
export HEI_DATAHUB_WEBDAV_LIBRARY_PATH="my-research"
export HEI_DATAHUB_WEBDAV_TIMEOUT="60"
export HEI_DATAHUB_WEBDAV_VERIFY_SSL="true"
```

---

### Sync Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_SYNC_AUTO_SYNC` | `sync.auto_sync` | boolean | `true` | Enable background sync |
| `HEI_DATAHUB_SYNC_SYNC_INTERVAL` | `sync.sync_interval` | integer | `300` | Sync frequency (seconds) |
| `HEI_DATAHUB_SYNC_RETRY_INTERVAL` | `sync.retry_interval` | integer | `60` | Retry delay (seconds) |
| `HEI_DATAHUB_SYNC_MAX_RETRIES` | `sync.max_retries` | integer | `3` | Maximum retry attempts |
| `HEI_DATAHUB_SYNC_ON_CONFLICT` | `sync.on_conflict` | string | `"last-write-wins"` | Conflict resolution |

**Examples:**

```bash
export HEI_DATAHUB_SYNC_AUTO_SYNC="false"
export HEI_DATAHUB_SYNC_SYNC_INTERVAL="600"  # 10 minutes
export HEI_DATAHUB_SYNC_MAX_RETRIES="5"
```

---

### Search Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_SEARCH_MAX_RESULTS` | `search.max_results` | integer | `50` | Maximum search results |
| `HEI_DATAHUB_SEARCH_SEARCH_TIMEOUT` | `search.search_timeout` | float | `5.0` | Query timeout (seconds) |
| `HEI_DATAHUB_SEARCH_ENABLE_FUZZY` | `search.enable_fuzzy` | boolean | `true` | Enable fuzzy matching |
| `HEI_DATAHUB_SEARCH_AUTOCOMPLETE_MIN_CHARS` | `search.autocomplete_min_chars` | integer | `2` | Min chars for autocomplete |
| `HEI_DATAHUB_SEARCH_AUTOCOMPLETE_MAX_RESULTS` | `search.autocomplete_max_results` | integer | `10` | Max autocomplete results |

**Examples:**

```bash
export HEI_DATAHUB_SEARCH_MAX_RESULTS="100"
export HEI_DATAHUB_SEARCH_ENABLE_FUZZY="false"
export HEI_DATAHUB_SEARCH_AUTOCOMPLETE_MIN_CHARS="3"
```

---

### UI Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_UI_THEME` | `ui.theme` | string | `"nord"` | UI color theme |
| `HEI_DATAHUB_UI_SHOW_WELCOME` | `ui.show_welcome` | boolean | `true` | Show welcome screen |
| `HEI_DATAHUB_UI_CONFIRM_DELETE` | `ui.confirm_delete` | boolean | `true` | Confirm deletions |
| `HEI_DATAHUB_UI_RESULTS_PER_PAGE` | `ui.results_per_page` | integer | `20` | Results per page |

**Examples:**

```bash
export HEI_DATAHUB_UI_THEME="gruvbox"
export HEI_DATAHUB_UI_SHOW_WELCOME="false"
export HEI_DATAHUB_UI_RESULTS_PER_PAGE="50"
```

---

### Logging Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_LOGGING_LEVEL` | `logging.level` | string | `"INFO"` | Log level |
| `HEI_DATAHUB_LOGGING_LOG_FILE` | `logging.log_file` | string | `~/.local/share/.../app.log` | Log file path |
| `HEI_DATAHUB_LOGGING_LOG_FORMAT` | `logging.log_format` | string | *(see config)* | Log format string |
| `HEI_DATAHUB_LOGGING_MAX_LOG_SIZE_MB` | `logging.max_log_size_mb` | integer | `10` | Max log size (MB) |
| `HEI_DATAHUB_LOGGING_BACKUP_COUNT` | `logging.backup_count` | integer | `5` | Backup log files |

**Examples:**

```bash
export HEI_DATAHUB_LOGGING_LEVEL="DEBUG"
export HEI_DATAHUB_LOGGING_LOG_FILE="/var/log/hei-datahub/app.log"
export HEI_DATAHUB_LOGGING_MAX_LOG_SIZE_MB="50"
```

---

### Database Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_DATABASE_PATH` | `database.path` | string | `~/.local/share/.../datasets.db` | Database path |
| `HEI_DATAHUB_DATABASE_BACKUP_ON_STARTUP` | `database.backup_on_startup` | boolean | `true` | Backup on startup |
| `HEI_DATAHUB_DATABASE_VACUUM_ON_STARTUP` | `database.vacuum_on_startup` | boolean | `false` | Vacuum on startup |

**Examples:**

```bash
export HEI_DATAHUB_DATABASE_PATH="/data/hei-datahub/datasets.db"
export HEI_DATAHUB_DATABASE_BACKUP_ON_STARTUP="true"
export HEI_DATAHUB_DATABASE_VACUUM_ON_STARTUP="false"
```

---

## Boolean Values

### Accepted Formats

Environment variables for boolean config values accept multiple formats:

**True Values:**
- `"true"` (case-insensitive)
- `"1"`
- `"yes"`

**False Values:**
- `"false"` (case-insensitive)
- `"0"`
- `"no"`

**Examples:**

```bash
# All these set auto_sync to true
export HEI_DATAHUB_SYNC_AUTO_SYNC="true"
export HEI_DATAHUB_SYNC_AUTO_SYNC="TRUE"
export HEI_DATAHUB_SYNC_AUTO_SYNC="1"
export HEI_DATAHUB_SYNC_AUTO_SYNC="yes"

# All these set auto_sync to false
export HEI_DATAHUB_SYNC_AUTO_SYNC="false"
export HEI_DATAHUB_SYNC_AUTO_SYNC="FALSE"
export HEI_DATAHUB_SYNC_AUTO_SYNC="0"
export HEI_DATAHUB_SYNC_AUTO_SYNC="no"
```

---

## Use Cases

### 1. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Install application
RUN uv add hei-datahub

# Set configuration via environment variables
ENV HEI_DATAHUB_WEBDAV_BASE_URL="https://cloud.example.com/webdav"
ENV HEI_DATAHUB_WEBDAV_LIBRARY_PATH="datasets"
ENV HEI_DATAHUB_SYNC_AUTO_SYNC="true"
ENV HEI_DATAHUB_LOGGING_LEVEL="INFO"

CMD ["hei-datahub"]
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  hei-datahub:
    image: hei-datahub:latest
    environment:
      - HEI_DATAHUB_WEBDAV_BASE_URL=https://cloud.example.com/webdav
      - HEI_DATAHUB_WEBDAV_LIBRARY_PATH=datasets
      - HEI_DATAHUB_SYNC_AUTO_SYNC=true
      - HEI_DATAHUB_LOGGING_LEVEL=DEBUG
    volumes:
      - ./data:/data
```

---

### 2. CI/CD Testing

```yaml
# .github/workflows/test.yml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      HEI_DATAHUB_WEBDAV_BASE_URL: https://test-server.example.com/webdav
      HEI_DATAHUB_SYNC_AUTO_SYNC: false
      HEI_DATAHUB_LOGGING_LEVEL: DEBUG
      HEI_DATAHUB_DATABASE_PATH: ./test-data/test.db

    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: uv sync --dev
      - name: Run tests
        run: pytest
```

---

### 3. Systemd Service

```ini
# /etc/systemd/user/hei-datahub.service
[Unit]
Description=Hei-DataHub Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/hei-datahub
Environment="HEI_DATAHUB_WEBDAV_BASE_URL=https://heibox.uni-heidelberg.de/remote.php/webdav"
Environment="HEI_DATAHUB_SYNC_AUTO_SYNC=true"
Environment="HEI_DATAHUB_LOGGING_LEVEL=INFO"
Restart=on-failure

[Install]
WantedBy=default.target
```

---

### 4. Development Environment

```bash
# dev-env.sh - Source this file for development

# WebDAV (local test server)
export HEI_DATAHUB_WEBDAV_BASE_URL="https://localhost:8080/webdav"
export HEI_DATAHUB_WEBDAV_VERIFY_SSL="false"
export HEI_DATAHUB_WEBDAV_LIBRARY_PATH="test-datasets"

# Disable auto-sync for development
export HEI_DATAHUB_SYNC_AUTO_SYNC="false"

# Debug logging
export HEI_DATAHUB_LOGGING_LEVEL="DEBUG"
export HEI_DATAHUB_LOGGING_LOG_FILE="./dev-logs/app.log"

# Test database
export HEI_DATAHUB_DATABASE_PATH="./dev-data/test.db"

echo "Development environment configured"
```

**Usage:**

```bash
source dev-env.sh
hei-datahub
```

---

### 5. Multi-User Server

```bash
# /etc/environment (system-wide)

# Default WebDAV server for all users
HEI_DATAHUB_WEBDAV_BASE_URL="https://heibox.uni-heidelberg.de/remote.php/webdav"

# Conservative sync settings
HEI_DATAHUB_SYNC_SYNC_INTERVAL="600"
HEI_DATAHUB_SYNC_MAX_RETRIES="5"

# Centralized logging
HEI_DATAHUB_LOGGING_LOG_FILE="/var/log/hei-datahub/app.log"
```

---

## Environment Variable Priority

### Override Order

```
1. Hardcoded defaults (lowest priority)
           ↓
2. System config file
           ↓
3. User config file
           ↓
4. Environment variables
           ↓
5. Command-line arguments (highest priority)
```

---

### Example Scenario

**System Config (`/etc/hei-datahub/config.toml`):**

```toml
[sync]
sync_interval = 300
```

**User Config (`~/.config/hei-datahub/config.toml`):**

```toml
[sync]
sync_interval = 600
```

**Environment Variable:**

```bash
export HEI_DATAHUB_SYNC_SYNC_INTERVAL="900"
```

**Command-line Argument:**

```bash
hei-datahub --sync-interval 1200
```

**Effective Value:** `1200` (from command-line argument)

**Priority Chain:**
- Default: `300` (hardcoded)
- System: `300` (from system config)
- User: `600` (user config overrides)
- Environment: `900` (env var overrides)
- **CLI: `1200`** ✅ (highest priority)

---

## Implementation

### Loading Environment Variables

```python
# src/hei_datahub/core/config.py

import os

def apply_env_overrides(config_dict: dict) -> None:
    """Apply environment variable overrides to config"""
    prefix = "HEI_DATAHUB_"

    for env_key, env_value in os.environ.items():
        # Skip non-matching environment variables
        if not env_key.startswith(prefix):
            continue

        # Parse: HEI_DATAHUB_WEBDAV_BASE_URL → ["webdav", "base_url"]
        parts = env_key[len(prefix):].lower().split("_")

        if len(parts) < 2:
            continue

        section = parts[0]
        config_key = "_".join(parts[1:])

        # Skip unknown sections
        if section not in config_dict:
            logger.warning(f"Unknown config section in {env_key}: {section}")
            continue

        # Get current value to determine type
        current_value = config_dict[section].get(config_key)

        # Convert string to appropriate type
        try:
            if isinstance(current_value, bool):
                # Boolean conversion
                converted_value = env_value.lower() in ("true", "1", "yes")
            elif isinstance(current_value, int):
                # Integer conversion
                converted_value = int(env_value)
            elif isinstance(current_value, float):
                # Float conversion
                converted_value = float(env_value)
            else:
                # String (no conversion)
                converted_value = env_value

            # Apply override
            config_dict[section][config_key] = converted_value
            logger.debug(f"Applied env override: {section}.{config_key} = {converted_value}")

        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse {env_key}={env_value}: {e}")
```

---

## Testing with Environment Variables

### Unit Tests

```python
# tests/unit/test_config_env.py

import os
import pytest
from hei_datahub.core.config import load_config

def test_webdav_url_override(monkeypatch):
    """Test WebDAV URL override via environment variable"""
    monkeypatch.setenv("HEI_DATAHUB_WEBDAV_BASE_URL", "https://test.example.com/webdav")

    config = load_config()

    assert config.webdav.base_url == "https://test.example.com/webdav"

def test_sync_interval_override(monkeypatch):
    """Test sync interval override"""
    monkeypatch.setenv("HEI_DATAHUB_SYNC_SYNC_INTERVAL", "900")

    config = load_config()

    assert config.sync.sync_interval == 900

def test_boolean_override_true(monkeypatch):
    """Test boolean override (true)"""
    monkeypatch.setenv("HEI_DATAHUB_SYNC_AUTO_SYNC", "true")

    config = load_config()

    assert config.sync.auto_sync is True

def test_boolean_override_false(monkeypatch):
    """Test boolean override (false)"""
    monkeypatch.setenv("HEI_DATAHUB_SYNC_AUTO_SYNC", "0")

    config = load_config()

    assert config.sync.auto_sync is False
```

---

## Best Practices

### 1. Use Environment Variables for Secrets

```bash
# ✅ GOOD: Credentials via environment (not committed to config)
export HEI_DATAHUB_WEBDAV_BASE_URL="https://heibox.uni-heidelberg.de/..."

# ❌ BAD: Hardcoding credentials in config file
# (Never put passwords in config files)
```

---

### 2. Document Required Variables

```bash
# required-env.sh - Template for required environment variables

# REQUIRED: WebDAV server URL
export HEI_DATAHUB_WEBDAV_BASE_URL="https://your-server.example.com/webdav"

# OPTIONAL: Override sync interval (default: 300 seconds)
# export HEI_DATAHUB_SYNC_SYNC_INTERVAL="600"

# OPTIONAL: Enable debug logging
# export HEI_DATAHUB_LOGGING_LEVEL="DEBUG"
```

---

### 3. Validate Environment Variables

```python
def validate_env_vars() -> None:
    """Validate required environment variables"""
    required = ["HEI_DATAHUB_WEBDAV_BASE_URL"]

    missing = [var for var in required if var not in os.environ]

    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
```

---

## Troubleshooting

### Environment Variable Not Applied

**Symptom:** Setting environment variable has no effect

**Diagnosis:**

```python
import os
print("HEI_DATAHUB_SYNC_AUTO_SYNC:", os.environ.get("HEI_DATAHUB_SYNC_AUTO_SYNC"))

from hei_datahub.core.config import load_config
config = load_config()
print("Config value:", config.sync.auto_sync)
```

**Common Causes:**
1. Variable not exported: Use `export` in bash
2. Typo in variable name
3. CLI argument overriding env var
4. Config file value takes precedence (check loading order)

---

### Type Conversion Errors

**Symptom:** Application fails to start with type error

**Diagnosis:**

```bash
# Check environment variable value
echo $HEI_DATAHUB_SYNC_SYNC_INTERVAL

# Try manual conversion
python3 -c "print(int('$HEI_DATAHUB_SYNC_SYNC_INTERVAL'))"
```

**Solution:**

```bash
# Ensure value is valid for expected type
export HEI_DATAHUB_SYNC_SYNC_INTERVAL="600"  # Integer, not "600 seconds"
```

---

## Related Documentation

- **[Configuration Overview](overview.md)** - Configuration system
- **[Configuration Files](files.md)** - Config file structure
- **[Adding Configuration](adding-config.md)** - Add new config options

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
