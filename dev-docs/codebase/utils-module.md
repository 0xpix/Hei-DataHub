# Utils Module

## Overview

The **Utils Module** contains shared utility functions used across the codebase. These are pure, reusable helpers that don't depend on business logic or infrastructure.

---

## Design Principles

**Utility Function Guidelines:**

- ✅ **Pure functions preferred** - No side effects when possible
- ✅ **Well-tested** - Utilities are widely used, test thoroughly
- ✅ **Minimal dependencies** - Avoid heavy imports
- ✅ **Single responsibility** - Each function does one thing well
- ✅ **Type hints** - Clear input/output types

---

## Module Catalog

### Text Formatting

#### `formatting.py` - Output Formatting

**Purpose:** Format data for display in CLI/TUI

**Key Functions:**

```python
def format_table(
    data: list[dict],
    columns: list[str],
    headers: dict[str, str] | None = None
) -> str:
    """
    Format list of dicts as ASCII table.

    Args:
        data: List of dictionaries to display
        columns: Column keys to include
        headers: Optional custom column headers

    Returns:
        Formatted ASCII table string

    Example:
        >>> data = [
        ...     {"id": "ds1", "name": "Dataset 1", "size": 1024},
        ...     {"id": "ds2", "name": "Dataset 2", "size": 2048}
        ... ]
        >>> print(format_table(data, ["id", "name", "size"]))
        ┌─────┬───────────┬──────┐
        │ ID  │ Name      │ Size │
        ├─────┼───────────┼──────┤
        │ ds1 │ Dataset 1 │ 1024 │
        │ ds2 │ Dataset 2 │ 2048 │
        └─────┴───────────┴──────┘
    """
```

**Implementation:**

```python
def format_table(data, columns, headers=None):
    """Format data as ASCII table"""
    if not data:
        return "No data"

    # Use custom headers or column names
    headers = headers or {col: col.title() for col in columns}

    # Calculate column widths
    widths = {col: len(headers[col]) for col in columns}
    for row in data:
        for col in columns:
            value = str(row.get(col, ""))
            widths[col] = max(widths[col], len(value))

    # Build table
    lines = []

    # Top border
    lines.append("┌" + "┬".join("─" * (widths[col] + 2) for col in columns) + "┐")

    # Header row
    header_cells = [f" {headers[col]:<{widths[col]}} " for col in columns]
    lines.append("│" + "│".join(header_cells) + "│")

    # Header separator
    lines.append("├" + "┼".join("─" * (widths[col] + 2) for col in columns) + "┤")

    # Data rows
    for row in data:
        cells = [f" {str(row.get(col, '')):<{widths[col]}} " for col in columns]
        lines.append("│" + "│".join(cells) + "│")

    # Bottom border
    lines.append("└" + "┴".join("─" * (widths[col] + 2) for col in columns) + "┘")

    return "\n".join(lines)
```

---

#### `truncate_text()` - Text Truncation

```python
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append (default "...")

    Returns:
        Truncated text

    Example:
        >>> truncate_text("This is a long description", 15)
        'This is a lo...'
    """
    if len(text) <= max_length:
        return text

    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix
```

---

#### `format_bytes()` - Human-Readable Byte Sizes

```python
def format_bytes(bytes: int, precision: int = 1) -> str:
    """
    Format bytes as human-readable size.

    Args:
        bytes: Number of bytes
        precision: Decimal places

    Returns:
        Formatted size string

    Example:
        >>> format_bytes(1024)
        '1.0 KB'
        >>> format_bytes(1536, precision=2)
        '1.50 KB'
        >>> format_bytes(1048576)
        '1.0 MB'
    """
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.{precision}f} {units[unit_index]}"
```

---

### Date/Time Utilities

#### `timing.py` - Performance Timing

**Purpose:** Measure and format execution times

**Decorator:**

```python
import time
from functools import wraps

def timing(func):
    """
    Decorator to measure function execution time.

    Example:
        @timing
        def slow_function():
            time.sleep(1)

        # Output: slow_function took 1.001s
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper
```

**Context Manager:**

```python
from contextlib import contextmanager

@contextmanager
def measure_time(label: str = "Operation"):
    """
    Context manager to measure execution time.

    Example:
        with measure_time("Search"):
            results = search_indexed("query")
        # Output: Search took 0.052s
    """
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{label} took {elapsed:.3f}s")
```

---

#### `format_datetime()` - Date/Time Formatting

```python
from datetime import datetime

def format_datetime(dt: datetime, format: str = "human") -> str:
    """
    Format datetime in various styles.

    Args:
        dt: Datetime object
        format: Output format ("human", "iso", "date", "time")

    Returns:
        Formatted datetime string

    Example:
        >>> now = datetime.now()
        >>> format_datetime(now, "human")
        '2 hours ago'
        >>> format_datetime(now, "iso")
        '2024-10-25T14:32:15'
    """
    if format == "iso":
        return dt.isoformat()
    elif format == "date":
        return dt.strftime("%Y-%m-%d")
    elif format == "time":
        return dt.strftime("%H:%M:%S")
    elif format == "human":
        return humanize_datetime(dt)
    else:
        return str(dt)

def humanize_datetime(dt: datetime) -> str:
    """Convert datetime to human-readable relative time"""
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
```

---

### YAML Utilities

#### `yaml_utils.py` - YAML Operations

**Purpose:** Safe YAML parsing and serialization

**Key Functions:**

```python
import yaml
from pathlib import Path

def safe_load_yaml(path: Path) -> dict:
    """
    Safely load YAML file with error handling.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML as dict

    Raises:
        ValueError: If YAML is invalid or file not found

    Example:
        >>> data = safe_load_yaml(Path("config.yaml"))
    """
    if not path.exists():
        raise ValueError(f"File not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}")

def safe_dump_yaml(data: dict, path: Path, *, indent: int = 2) -> None:
    """
    Safely write dict to YAML file.

    Args:
        data: Dictionary to serialize
        path: Output file path
        indent: Indentation spaces

    Example:
        >>> safe_dump_yaml({"key": "value"}, Path("output.yaml"))
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, indent=indent)
    except Exception as e:
        raise ValueError(f"Failed to write YAML to {path}: {e}")
```

**Merge YAML:**

```python
def merge_yaml(base: dict, override: dict) -> dict:
    """
    Deep merge two YAML structures.

    Args:
        base: Base dictionary
        override: Override dictionary (takes precedence)

    Returns:
        Merged dictionary

    Example:
        >>> base = {"a": 1, "b": {"c": 2}}
        >>> override = {"b": {"d": 3}}
        >>> merge_yaml(base, override)
        {'a': 1, 'b': {'c': 2, 'd': 3}}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_yaml(result[key], value)
        else:
            result[key] = value

    return result
```

---

### Network Utilities

#### `network.py` - Network Operations

**Purpose:** Network connectivity and validation

**Key Functions:**

```python
import socket
import requests

def is_network_available(timeout: float = 2.0) -> bool:
    """
    Check if network is available.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        True if network is reachable

    Example:
        >>> if is_network_available():
        ...     sync_now()
    """
    try:
        # Try to connect to Google DNS
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

def is_url_reachable(url: str, timeout: float = 5.0) -> bool:
    """
    Check if URL is reachable.

    Args:
        url: URL to check
        timeout: Request timeout

    Returns:
        True if URL responds

    Example:
        >>> if is_url_reachable("https://example.com"):
        ...     print("Site is up")
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code < 500
    except requests.RequestException:
        return False
```

---

### String Utilities

#### `slugify()` - Convert to URL-Safe Slug

```python
import re

def slugify(text: str, max_length: int = 100) -> str:
    """
    Convert text to URL-safe slug.

    Args:
        text: Text to slugify
        max_length: Maximum slug length

    Returns:
        Slugified text

    Example:
        >>> slugify("Climate Model Data 2024")
        'climate-model-data-2024'
        >>> slugify("Ocean Temp (High Res)")
        'ocean-temp-high-res'
    """
    # Lowercase
    text = text.lower()

    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    # Truncate
    if len(text) > max_length:
        text = text[:max_length].rstrip("-")

    return text
```

---

#### `normalize_whitespace()` - Normalize Whitespace

```python
def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    - Collapse multiple spaces to single space
    - Remove leading/trailing whitespace
    - Preserve single newlines

    Args:
        text: Text to normalize

    Returns:
        Normalized text

    Example:
        >>> normalize_whitespace("  multiple   spaces  ")
        'multiple spaces'
    """
    # Collapse multiple spaces
    text = re.sub(r"  +", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text
```

---

### Validation Utilities

#### `is_valid_email()` - Email Validation

```python
import re

def is_valid_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid format

    Example:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid-email")
        False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
```

---

#### `is_valid_url()` - URL Validation

```python
from urllib.parse import urlparse

def is_valid_url(url: str, require_https: bool = False) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate
        require_https: Require HTTPS scheme

    Returns:
        True if valid URL

    Example:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("http://example.com", require_https=True)
        False
    """
    try:
        result = urlparse(url)

        # Check scheme and netloc
        if not all([result.scheme, result.netloc]):
            return False

        # Check HTTPS requirement
        if require_https and result.scheme != "https":
            return False

        return True
    except Exception:
        return False
```

---

## Testing Utilities

### Test Helpers

```python
# tests/utils/test_helpers.py

def create_test_dataset(dataset_id: str = "test-dataset") -> dict:
    """Create test dataset metadata"""
    return {
        "id": dataset_id,
        "dataset_name": "Test Dataset",
        "description": "Test description",
        "source": "test",
        "date_created": "2024-01-01",
        "storage_location": "/test/path"
    }

def create_temp_config(tmp_path: Path) -> Path:
    """Create temporary config file"""
    config_path = tmp_path / "config.toml"
    config = {
        "webdav": {
            "url": "https://test.example.com",
            "library": "test-library"
        }
    }

    with open(config_path, "w") as f:
        toml.dump(config, f)

    return config_path
```

---

## Usage Examples

### Format Search Results

```python
from mini_datahub.utils.formatting import format_table

results = search_indexed("climate")

# Format as table
table = format_table(
    data=results,
    columns=["id", "name", "snippet"],
    headers={"id": "ID", "name": "Name", "snippet": "Description"}
)

print(table)
```

### Measure Performance

```python
from mini_datahub.utils.timing import timing, measure_time

@timing
def expensive_operation():
    # ... complex logic
    pass

# Or use context manager
with measure_time("Database query"):
    results = db.execute("SELECT ...")
```

### Validate Input

```python
from mini_datahub.utils.network import is_url_reachable
from mini_datahub.utils.formatting import is_valid_email

# Validate WebDAV URL
if not is_valid_url(url, require_https=True):
    raise ValueError("HTTPS URL required")

# Check if reachable
if not is_url_reachable(url):
    raise ConnectionError(f"Cannot reach {url}")
```

---

## Related Documentation

- **[Core Module](core-module.md)** - Domain models
- **[Services Module](services-module.md)** - Business logic
- **[Testing Guide](tests.md)** - Testing utilities

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
