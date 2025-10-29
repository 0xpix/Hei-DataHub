# Adding New Configuration

## Introduction

This guide explains how to add new configuration options to Hei-DataHub. Follow these steps to ensure configuration options are properly integrated across all layers.

---

## Step-by-Step Guide

### 1. Define Configuration Schema

**Location:** `src/hei_datahub/core/config.py`

Add the new field to the appropriate configuration dataclass:

```python
from dataclasses import dataclass

@dataclass
class SearchConfig:
    max_results: int = 50
    search_timeout: float = 5.0
    enable_fuzzy: bool = True
    autocomplete_min_chars: int = 2
    autocomplete_max_results: int = 10

    # NEW FIELD
    enable_stemming: bool = True  # Add stemming to search
```

**Best Practices:**
- ✅ Provide sensible defaults
- ✅ Use type hints
- ✅ Add inline comment explaining purpose
- ✅ Choose appropriate data type (bool, int, float, str)

---

### 2. Update Default Configuration

**Location:** `src/hei_datahub/core/config.py`

Add the default value to `get_default_config()`:

```python
def get_default_config() -> dict:
    """Get default configuration values"""
    return {
        "search": {
            "max_results": 50,
            "search_timeout": 5.0,
            "enable_fuzzy": True,
            "autocomplete_min_chars": 2,
            "autocomplete_max_results": 10,
            "enable_stemming": True,  # NEW FIELD
        },
        # ... other sections
    }
```

---

### 3. Add to Config File Template

**Location:** Create/update default config template

```toml
# ~/.config/hei-datahub/config.toml

[search]
max_results = 50
search_timeout = 5.0
enable_fuzzy = true
autocomplete_min_chars = 2
autocomplete_max_results = 10
enable_stemming = true  # NEW FIELD - Enable Porter stemming
```

---

### 4. Add Validation (Optional)

**Location:** `src/hei_datahub/core/config.py`

Add validation in `validate_config()`:

```python
def validate_config(config_dict: dict) -> None:
    """Validate configuration values"""
    # Existing validation...

    # NEW VALIDATION
    if "enable_stemming" in config_dict["search"]:
        if not isinstance(config_dict["search"]["enable_stemming"], bool):
            raise ValueError("enable_stemming must be a boolean")
```

---

### 5. Document Environment Variable

**Location:** `dev-docs/config/environment.md`

Add the environment variable to documentation:

```markdown
### Search Configuration

| Environment Variable | Config Key | Type | Default | Description |
|---------------------|------------|------|---------|-------------|
| `HEI_DATAHUB_SEARCH_ENABLE_STEMMING` | `search.enable_stemming` | boolean | `true` | Enable Porter stemming |
```

---

### 6. Use Configuration in Code

**Example:** Using the new config in a service

```python
# src/hei_datahub/services/fast_search.py

from hei_datahub.core.config import load_config

class FastSearchService:
    def __init__(self):
        config = load_config()
        self.enable_stemming = config.search.enable_stemming

    def search(self, query: str) -> list[dict]:
        """Search with optional stemming"""
        if self.enable_stemming:
            # Use FTS5 with Porter stemming
            return self._search_with_stemming(query)
        else:
            # Use exact matching
            return self._search_exact(query)
```

---

### 7. Add CLI Argument (Optional)

**Location:** `src/hei_datahub/cli/commands.py`

Add command-line argument override:

```python
def add_search_args(parser: argparse.ArgumentParser) -> None:
    """Add search-related arguments"""
    parser.add_argument(
        "--no-stemming",
        action="store_true",
        help="Disable Porter stemming in search"
    )

def search_command(args: argparse.Namespace) -> None:
    """Execute search command"""
    config = load_config()

    # Override from CLI argument
    enable_stemming = not args.no_stemming if args.no_stemming else config.search.enable_stemming

    # Use configuration...
```

---

### 8. Write Tests

**Location:** `tests/unit/test_config.py`

Add tests for the new configuration option:

```python
import pytest
from hei_datahub.core.config import load_config, Config

def test_enable_stemming_default():
    """Test default value for enable_stemming"""
    config = load_config()
    assert config.search.enable_stemming is True

def test_enable_stemming_from_config(tmp_path, monkeypatch):
    """Test loading enable_stemming from config file"""
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[search]
enable_stemming = false
""")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config = load_config()

    assert config.search.enable_stemming is False

def test_enable_stemming_from_env(monkeypatch):
    """Test environment variable override"""
    monkeypatch.setenv("HEI_DATAHUB_SEARCH_ENABLE_STEMMING", "false")

    config = load_config()

    assert config.search.enable_stemming is False
```

---

### 9. Update Documentation

**Location:** `dev-docs/config/files.md`

Document the new option:

```markdown
### Search Configuration

```toml
[search]
max_results = 50
enable_stemming = true  # Enable Porter stemming for better matches
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable_stemming` | boolean | `true` | Enable Porter stemming algorithm |
```

---

### 10. Add Changelog Entry

**Location:** `CHANGELOG.md`

```markdown
## [Unreleased]

### Added
- Configuration option `search.enable_stemming` to toggle Porter stemming (#123)
```

---

## Complete Example

### Adding Cache Configuration

Let's walk through adding a complete cache configuration section:

#### 1. Define Schema

```python
# src/hei_datahub/core/config.py

@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    max_size_mb: int = 100
    ttl_seconds: int = 3600
    eviction_policy: str = "lru"

@dataclass
class Config:
    webdav: WebDAVConfig
    sync: SyncConfig
    search: SearchConfig
    ui: UIConfig
    logging: LoggingConfig
    database: DatabaseConfig
    cache: CacheConfig  # NEW SECTION
```

---

#### 2. Add Defaults

```python
def get_default_config() -> dict:
    return {
        # ... existing sections
        "cache": {
            "enabled": True,
            "max_size_mb": 100,
            "ttl_seconds": 3600,
            "eviction_policy": "lru"
        }
    }
```

---

#### 3. Add to Config Template

```toml
# ~/.config/hei-datahub/config.toml

[cache]
enabled = true
max_size_mb = 100       # Maximum cache size in MB
ttl_seconds = 3600      # Time to live (1 hour)
eviction_policy = "lru" # Eviction policy: lru, lfu, fifo
```

---

#### 4. Add Validation

```python
def validate_config(config_dict: dict) -> None:
    # ... existing validation

    # Validate cache config
    if config_dict["cache"]["max_size_mb"] < 10:
        raise ValueError("Cache size must be at least 10 MB")

    valid_policies = {"lru", "lfu", "fifo"}
    policy = config_dict["cache"]["eviction_policy"]
    if policy not in valid_policies:
        raise ValueError(f"Invalid eviction policy: {policy}")
```

---

#### 5. Update load_config()

```python
def load_config() -> Config:
    # ... existing loading logic

    return Config(
        webdav=WebDAVConfig(**config_dict["webdav"]),
        sync=SyncConfig(**config_dict["sync"]),
        search=SearchConfig(**config_dict["search"]),
        ui=UIConfig(**config_dict["ui"]),
        logging=LoggingConfig(**config_dict["logging"]),
        database=DatabaseConfig(**config_dict["database"]),
        cache=CacheConfig(**config_dict["cache"])  # NEW
    )
```

---

#### 6. Use in Code

```python
# src/hei_datahub/infra/cache.py

from hei_datahub.core.config import load_config
from functools import lru_cache

class CacheManager:
    def __init__(self):
        config = load_config()
        self.enabled = config.cache.enabled
        self.max_size_mb = config.cache.max_size_mb
        self.ttl_seconds = config.cache.ttl_seconds
        self.eviction_policy = config.cache.eviction_policy

    def get_cached_search_results(self, query: str):
        if not self.enabled:
            return None

        # Cache lookup logic...
```

---

#### 7. Environment Variables

```bash
export HEI_DATAHUB_CACHE_ENABLED="true"
export HEI_DATAHUB_CACHE_MAX_SIZE_MB="200"
export HEI_DATAHUB_CACHE_TTL_SECONDS="7200"
export HEI_DATAHUB_CACHE_EVICTION_POLICY="lfu"
```

---

#### 8. CLI Arguments

```python
parser.add_argument(
    "--no-cache",
    action="store_true",
    help="Disable caching"
)

parser.add_argument(
    "--cache-size",
    type=int,
    metavar="MB",
    help="Cache size in MB"
)
```

---

#### 9. Tests

```python
def test_cache_config_defaults():
    config = load_config()
    assert config.cache.enabled is True
    assert config.cache.max_size_mb == 100
    assert config.cache.ttl_seconds == 3600
    assert config.cache.eviction_policy == "lru"

def test_cache_config_validation():
    with pytest.raises(ValueError, match="Cache size must be at least 10 MB"):
        validate_config({"cache": {"max_size_mb": 5}})
```

---

## Configuration Migration

### Handling Breaking Changes

When renaming or removing configuration options:

#### 1. Deprecation Warning

```python
def load_config() -> Config:
    config_dict = # ... load config

    # Check for deprecated options
    if "old_field_name" in config_dict["search"]:
        logger.warning(
            "Configuration option 'search.old_field_name' is deprecated. "
            "Use 'search.new_field_name' instead."
        )
        # Migrate old value to new field
        if "new_field_name" not in config_dict["search"]:
            config_dict["search"]["new_field_name"] = config_dict["search"]["old_field_name"]
```

---

#### 2. Migration Function

```python
def migrate_config(config_dict: dict, version: str) -> dict:
    """Migrate configuration from older versions"""
    if version < "0.58.0":
        # Rename sync.auto_sync to sync.enabled
        if "auto_sync" in config_dict["sync"]:
            config_dict["sync"]["enabled"] = config_dict["sync"]["auto_sync"]
            del config_dict["sync"]["auto_sync"]

    return config_dict
```

---

## Best Practices

### 1. Use Sensible Defaults

```python
# ✅ GOOD: Works out-of-the-box
@dataclass
class SearchConfig:
    max_results: int = 50  # Reasonable default

# ❌ BAD: Requires user configuration
@dataclass
class SearchConfig:
    max_results: int  # No default, will fail
```

---

### 2. Validate Early

```python
# ✅ GOOD: Validate on load
def load_config() -> Config:
    config_dict = load_from_file()
    validate_config(config_dict)  # Fail fast
    return Config(...)

# ❌ BAD: Validate on use (fails later)
def search(query: str):
    if config.max_results < 1:
        raise ValueError("Invalid config")
```

---

### 3. Document Constraints

```toml
[search]
max_results = 50  # Must be between 1 and 1000
search_timeout = 5.0  # Seconds, must be > 0
```

---

### 4. Group Related Options

```python
# ✅ GOOD: Grouped by feature
@dataclass
class CacheConfig:
    enabled: bool
    max_size_mb: int
    ttl_seconds: int

# ❌ BAD: Scattered across sections
@dataclass
class Config:
    cache_enabled: bool
    max_cache_size: int  # In different section
```

---

### 5. Use Type Hints

```python
# ✅ GOOD: Clear types
@dataclass
class SyncConfig:
    auto_sync: bool = True
    sync_interval: int = 300
    timeout: float = 30.0

# ❌ BAD: No type information
@dataclass
class SyncConfig:
    auto_sync = True  # Type unclear
```

---

## Troubleshooting

### Configuration Not Applied

**Problem:** New configuration option not taking effect

**Checklist:**
1. ✅ Added to dataclass?
2. ✅ Added to `get_default_config()`?
3. ✅ Added to `load_config()` return?
4. ✅ Config file syntax correct (TOML)?
5. ✅ Environment variable name correct?
6. ✅ Restarted application?

---

### Type Conversion Errors

**Problem:** `TypeError: __init__() got an unexpected keyword argument`

**Solution:** Ensure field names match exactly:

```python
# Config file
[search]
max_results = 50  # Underscore!

# Dataclass
@dataclass
class SearchConfig:
    max_results: int  # Must match exactly
```

---

### Validation Failures

**Problem:** Configuration validation fails

**Debug:**

```python
import json
config_dict = load_from_file()
print(json.dumps(config_dict, indent=2))

validate_config(config_dict)  # See exact error
```

---

## Related Documentation

- **[Configuration Overview](overview.md)** - Configuration system architecture
- **[Configuration Files](files.md)** - File structure and syntax
- **[Environment Variables](environment.md)** - Environment variable reference

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
