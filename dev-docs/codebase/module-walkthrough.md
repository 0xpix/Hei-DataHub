# Module Walkthrough

## Overview

This document provides a **file-by-file walkthrough** of the key modules in Hei-DataHub. Each section explains the module's purpose, main functions, and how it fits into the overall architecture.

**Target audience:** Developers working on the codebase who need function-level understanding.

**Structure:** `src/hei_datahub/` organized by Clean Architecture layers:

```
src/hei_datahub/
├── core/          # Pure business logic (no I/O)
├── services/      # Orchestration layer
├── infra/         # Infrastructure (DB, filesystem, I/O)
├── auth/          # Authentication & credential management
├── cli/           # Command-line interface
└── ui/            # Terminal UI (Textual)
```

---

## Table of Contents

- [Core Layer](#core-layer)
  - [models.py](#coremodelspy) - Pydantic data models
  - [queries.py](#corequeriespy) - Query parsing
- [Authentication Layer](#authentication-layer)
  - [credentials.py](#authcredentialspy) - Credential storage
  - [setup.py](#authsetuppy) - Setup wizard
  - [validator.py](#authvalidatorpy) - Credential validation
  - [doctor.py](#authdoctorpy) - Diagnostics
  - [clear.py](#authclearpy) - Credential removal
- [Services Layer](#services-layer)
  - [fast_search.py](#servicesfast_searchpy) - Search interface
  - [webdav_storage.py](#serviceswebdav_storagepy) - WebDAV client
  - [autocomplete.py](#servicesautocompletepy) - Autocomplete engine
  - [sync.py](#servicessyncpy) - Background sync
- [Infrastructure Layer](#infrastructure-layer)
  - [db.py](#infradbpy) - Database connections
  - [index.py](#infraindexpy) - FTS5 operations
  - [paths.py](#infrapathspy) - Path management

---

## Core Layer

### `core/models.py`

**Purpose:** Define Pydantic models for type-safe dataset metadata validation.

**Key Concepts:**
- Mirrors `schema.json` structure
- Validates all dataset fields
- Provides serialization/deserialization

**Main Classes:**

#### `SchemaField`

Represents a single field in a dataset's schema.

```python
class SchemaField(BaseModel):
    name: str           # Field name (e.g., "temperature")
    type: str           # Data type (e.g., "float")
    description: Optional[str]  # Field description
```

**Example:**
```python
field = SchemaField(
    name="temperature",
    type="float",
    description="Temperature in Celsius"
)
```

#### `DatasetMetadata`

Complete dataset metadata model with validation.

```python
class DatasetMetadata(BaseModel):
    # Required fields
    id: str                     # Unique slug (e.g., "dataset-climate-2024")
    dataset_name: str           # Human-readable name
    description: str            # Detailed description
    source: str                 # Data source URL
    date_created: date          # Creation date
    storage_location: str       # Where data is stored

    # Optional fields
    file_format: Optional[str]
    size: Optional[str]
    data_types: Optional[List[str]]
    used_in_projects: Optional[List[str]]
    schema_fields: Optional[List[SchemaField]]
    last_updated: Optional[date]
    # ... 10+ more optional fields
```

**Validation:**
- `id`: Must match `^[a-z0-9][a-z0-9_-]*$` (valid slug)
- `id`: Automatically lowercased
- Dates: Parsed as `datetime.date` objects

**Methods:**

##### `validate_id(v: str) -> str`

Custom validator for the `id` field.

```python
@field_validator("id")
@classmethod
def validate_id(cls, v: str) -> str:
    if not v:
        raise ValueError("ID cannot be empty")
    if not v[0].isalnum():
        raise ValueError("ID must start with an alphanumeric character")
    return v.lower()
```

##### `to_dict() -> dict`

Convert model to dictionary with YAML-friendly keys.

```python
def to_dict(self) -> dict:
    """Convert to dictionary with aliases."""
    return self.model_dump(by_alias=True, exclude_none=True)
```

**Usage Example:**

```python
from hei_datahub.core.models import DatasetMetadata

# Parse from YAML
metadata = DatasetMetadata(
    id="my-dataset",
    dataset_name="My Dataset",
    description="A dataset about...",
    source="https://example.com",
    date_created="2024-01-01",
    storage_location="/data/my-dataset"
)

# Validate
metadata.model_validate(data_dict)

# Serialize
yaml_dict = metadata.to_dict()
```

**Related:**
- Used by: Services layer for validation
- Configured via: `schema.json`

---

### `core/queries.py`

**Purpose:** Parse search queries into structured filter objects.

**Key Concepts:**
- Supports free-text search
- Parses `project:` filters
- Separates filters from search text

**Main Classes:**

#### `QueryTerm`

Represents a single term in a query (filter or free text).

```python
class QueryTerm:
    field: Optional[str]    # Filter field (e.g., "project")
    value: str              # Term value
    is_free_text: bool      # True if not a filter
```

#### `ParsedQuery`

Result of parsing a query string.

```python
class ParsedQuery:
    terms: List[QueryTerm]       # All terms
    free_text_query: str         # Combined free text
    filters: Dict[str, str]      # Extracted filters
```

**Main Class:**

#### `QueryParser`

Parses query strings into structured objects.

```python
class QueryParser:
    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a query string.

        Supports:
        - Free text: "climate data"
        - Filters: "project:weather"
        - Combined: "project:weather precipitation"
        """
```

**Example:**

```python
from hei_datahub.core.queries import QueryParser

parser = QueryParser()

# Simple query
parsed = parser.parse("climate precipitation")
# parsed.free_text_query == "climate precipitation"
# parsed.filters == {}

# Query with filter
parsed = parser.parse("project:weather temperature")
# parsed.free_text_query == "temperature"
# parsed.filters == {"project": "weather"}
```

**Related:**
- Used by: `services/fast_search.py`
- See: [Search & Autocomplete](../architecture/search-and-autocomplete.md#query-parser)

---

## Authentication Layer

All authentication modules are **Linux-only** and use the Secret Service keyring API.

### `auth/credentials.py`

**Purpose:** Abstract credential storage with keyring and environment variable backends.

**Key Concepts:**
- Pluggable storage backends
- Keyring-first, ENV fallback
- Secret redaction for logging

**Main Classes:**

#### `AuthStore` (Abstract)

Base interface for credential storage.

```python
class AuthStore(ABC):
    @abstractmethod
    def store_secret(self, key_id: str, value: str) -> None:
        """Store a secret."""
        pass

    @abstractmethod
    def load_secret(self, key_id: str) -> Optional[str]:
        """Load a secret. Returns None if not found."""
        pass

    @abstractmethod
    def available(self) -> bool:
        """Check if backend is available."""
        pass

    @property
    @abstractmethod
    def strategy(self) -> Literal["keyring", "env"]:
        """Return storage strategy name."""
        pass
```

#### `KeyringAuthStore`

Linux keyring implementation (Secret Service).

```python
class KeyringAuthStore(AuthStore):
    SERVICE_NAME = "hei-datahub"

    def __init__(self):
        """Initialize keyring store (Linux only)."""
        if platform.system() != "Linux":
            raise RuntimeError("KeyringAuthStore is only supported on Linux")

        import keyring
        self._keyring = keyring
        # Test availability
        self._available = self._test_backend()
```

**Methods:**

##### `store_secret(key_id: str, value: str) -> None`

Store credential in keyring.

```python
def store_secret(self, key_id: str, value: str) -> None:
    """
    Store secret in Linux keyring.

    Raises:
        RuntimeError: If keyring backend unavailable
    """
    self._keyring.set_password(self.SERVICE_NAME, key_id, value)
    logger.info(f"Stored secret in keyring: {key_id}")
```

##### `load_secret(key_id: str) -> Optional[str]`

Load credential from keyring.

```python
def load_secret(self, key_id: str) -> Optional[str]:
    """
    Load secret from Linux keyring.

    Returns:
        Secret value or None if not found
    """
    return self._keyring.get_password(self.SERVICE_NAME, key_id)
```

#### `EnvAuthStore`

Environment variable fallback storage.

```python
class EnvAuthStore(AuthStore):
    """Environment variable storage (less secure)."""

    def store_secret(self, key_id: str, value: str) -> None:
        """Store in ENV (warning logged)."""
        logger.warning("Storing credentials in environment variables (less secure)")
        os.environ[key_id.upper().replace(":", "_")] = value

    def load_secret(self, key_id: str) -> Optional[str]:
        """Load from ENV."""
        return os.environ.get(key_id.upper().replace(":", "_"))
```

**Helper Functions:**

##### `redact(s: str) -> str`

Redact sensitive strings for logging.

```python
def redact(s: str) -> str:
    """Redact sensitive strings for logging."""
    if not s or len(s) < 4:
        return "***"
    return s[:2] + "***" + s[-2:]

# Example
redact("mySecretToken123")  # "my***23"
```

**Usage Example:**

```python
from hei_datahub.auth.credentials import KeyringAuthStore

store = KeyringAuthStore()

# Store credential
key_id = "webdav:token:-@heibox.uni-heidelberg.de"
store.store_secret(key_id, "my-webdav-token")

# Load credential
token = store.load_secret(key_id)

# Check availability
if not store.available():
    print("Keyring backend not available")
```

**Related:**
- Used by: `auth/setup.py`, `auth/validator.py`
- See: [Security & Privacy](../architecture/security-privacy.md#storage-architecture)

---

### `auth/setup.py`

**Purpose:** Interactive wizard for WebDAV authentication setup.

**Key Concepts:**
- Interactive and non-interactive modes
- TOML config generation
- Credential validation
- Keyring storage

**Main Function:**

#### `run_setup_wizard(...) -> int`

Run the authentication setup wizard.

```python
def run_setup_wizard(
    url: Optional[str] = None,
    username: Optional[str] = None,
    token: Optional[str] = None,
    password: Optional[str] = None,
    library: Optional[str] = None,
    store: Optional[Literal["keyring", "env"]] = None,
    no_validate: bool = False,
    overwrite: bool = False,
    timeout: int = 8,
    non_interactive: bool = False,
) -> int:
    """
    Run the auth setup wizard.

    Args:
        url: WebDAV URL
        username: Username (for password auth)
        token: Token credential (recommended)
        password: Password credential
        library: Library/folder name
        store: Storage backend (keyring/env)
        no_validate: Skip credential validation
        overwrite: Overwrite existing config
        timeout: Validation timeout
        non_interactive: Non-interactive mode

    Returns:
        Exit code: 0=success, 1=validation failed, 2=usage error
    """
```

**Interactive Flow:**

```python
# 1. Check for existing config
if config_exists and not overwrite:
    choice = input("[O]verwrite, [S]kip, [T]est? ")

# 2. Collect inputs
url = input("Enter WebDAV URL: ")
library = input("Enter library name: ")
method = input("[T]oken or [P]assword? ")

# 3. Validate credentials
if not no_validate:
    validate_webdav_connection(...)

# 4. Save config (TOML)
save_toml_config(...)

# 5. Store credentials (keyring)
store.store_secret(key_id, credential)
```

**Helper Functions:**

##### `_derive_key_id(method, username, url) -> str`

Derive keyring key ID from credentials.

```python
def _derive_key_id(
    method: Literal["token", "password"],
    username: Optional[str],
    url: str
) -> str:
    """
    Derive key ID for keyring storage.

    Format: webdav:{method}:{username_or_dash}@{host}

    Examples:
        webdav:token:-@heibox.uni-heidelberg.de
        webdav:password:user@heibox.uni-heidelberg.de
    """
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    user_part = username if username else "-"
    return f"webdav:{method}:{user_part}@{host}"
```

**Non-Interactive Example:**

```bash
hei-datahub auth setup \
  --url "https://heibox.uni-heidelberg.de/seafdav" \
  --token "$WEBDAV_TOKEN" \
  --library "my-datasets" \
  --non-interactive
```

**Config Output (TOML):**

```toml
[auth]
method = "token"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "-"
library = "my-datasets"
stored_in = "keyring"
key_id = "webdav:token:-@heibox.uni-heidelberg.de"
```

**Related:**
- CLI command: `hei-datahub auth setup`
- See: [Authentication & Sync](../architecture/auth-and-sync.md#hei-datahub-auth-setup)

---

### `auth/validator.py`

**Purpose:** Validate WebDAV credentials and connection.

**Main Function:**

#### `validate_webdav_connection(...) -> bool`

Test WebDAV connection with credentials.

```python
def validate_webdav_connection(
    url: str,
    username: Optional[str],
    credential: str,
    library: str,
    timeout: int = 8,
    test_write: bool = True
) -> bool:
    """
    Validate WebDAV connection.

    Tests:
    1. URL reachable (network check)
    2. Authentication successful (401 check)
    3. Read permission (list files)
    4. Write permission (create/delete test file)

    Args:
        url: WebDAV base URL
        username: Username (for password auth, None for token)
        credential: Token or password
        library: Library/folder name
        timeout: Network timeout in seconds
        test_write: Also test write permissions

    Returns:
        True if all checks pass, False otherwise
    """
```

**Validation Steps:**

```python
# 1. Build WebDAV URL
full_url = f"{url}/{library}"

# 2. Test reachability
response = requests.head(full_url, timeout=timeout)

# 3. Test authentication
response = requests.request(
    "PROPFIND",
    full_url,
    auth=(username, credential),
    timeout=timeout
)
if response.status_code == 401:
    return False  # Auth failed

# 4. Test read permission
# List directory contents

# 5. Test write permission (optional)
# Create test file, then delete it
```

**Usage Example:**

```python
from hei_datahub.auth.validator import validate_webdav_connection

valid = validate_webdav_connection(
    url="https://heibox.uni-heidelberg.de/seafdav",
    username=None,  # Token auth
    credential="my-webdav-token",
    library="my-datasets",
    timeout=8,
    test_write=True
)

if valid:
    print("✓ Connection successful")
else:
    print("✗ Validation failed")
```

**Related:**
- Used by: `auth/setup.py`, `auth/doctor.py`
- See: [Authentication & Sync](../architecture/auth-and-sync.md)

---

### `auth/doctor.py`

**Purpose:** Comprehensive WebDAV authentication diagnostics.

**Main Function:**

#### `run_auth_doctor(...) -> int`

Run authentication diagnostics.

```python
def run_auth_doctor(
    json_output: bool = False,
    no_write: bool = False,
    timeout: int = 8
) -> int:
    """
    Run comprehensive auth diagnostics.

    Checks:
    1. Config file exists
    2. Config has [auth] section
    3. Credentials found in keyring
    4. WebDAV URL reachable
    5. Authentication successful
    6. Read permission verified
    7. Write permission verified

    Args:
        json_output: Output results as JSON
        no_write: Skip write permission tests
        timeout: Network timeout

    Returns:
        Exit code: 0=all pass, 1=one or more failed
    """
```

**Diagnostic Flow:**

```python
results = []

# Check 1: Config file exists
results.append({"check": "Config file exists", "status": "PASS"})

# Check 2: Config has [auth] section
# Check 3: Credentials in keyring
# Check 4: URL reachable
# Check 5: Auth successful
# Check 6: Read permission
# Check 7: Write permission (if not no_write)

# Display results
for result in results:
    print(f"[{i}/{total}] {result['check']} ... {result['status']}")

# Summary
if all_pass:
    print("✓ All checks passed!")
    return 0
else:
    print("✗ Diagnostics failed")
    return 1
```

**JSON Output:**

```json
{
  "checks": [
    {"name": "Config file exists", "status": "PASS", "message": null},
    {"name": "URL reachable", "status": "FAIL", "message": "Connection timeout"}
  ],
  "summary": {
    "total": 7,
    "passed": 6,
    "failed": 1
  }
}
```

**Related:**
- CLI command: `hei-datahub auth doctor`
- See: [Authentication & Sync](../architecture/auth-and-sync.md#hei-datahub-auth-doctor)

---

### `auth/clear.py`

**Purpose:** Remove stored credentials and configuration.

**Main Function:**

#### `clear_auth(...) -> int`

Clear authentication configuration.

```python
def clear_auth(
    force: bool = False,
    clear_all: bool = False
) -> int:
    """
    Clear WebDAV authentication.

    Removes:
    - Config file (config.toml)
    - Keyring entry
    - Search index (db.sqlite)
    - Cache files (if --all)

    Args:
        force: Skip confirmation prompt
        clear_all: Also remove cache files

    Returns:
        Exit code: 0=success, 1=user aborted
    """
```

**Removal Flow:**

```python
# 1. Confirm (unless --force)
if not force:
    confirm = input("Continue? [y/N] ")
    if confirm.lower() != "y":
        return 1

# 2. Load config to get key_id
config = load_toml_config()
key_id = config.get("auth", {}).get("key_id")

# 3. Remove keyring entry
store = KeyringAuthStore()
store.delete_secret(key_id)

# 4. Remove config file
config_path.unlink()

# 5. Remove database
db_path.unlink()

# 6. Remove cache (if --all)
if clear_all:
    shutil.rmtree(CACHE_DIR)

print("✓ Authentication cleared")
```

**Related:**
- CLI command: `hei-datahub auth clear`
- See: [CLI Commands Reference](../api-reference/cli-commands.md#auth-clear)

---

## Services Layer

### `services/fast_search.py`

**Purpose:** Unified search interface using SQLite FTS5.

**Key Concepts:**
- Never hits network (local-only)
- Supports free text + filters
- BM25 ranking
- <80ms latency target

**Main Functions:**

#### `search_indexed(query: str, limit: int = 50) -> List[Dict]`

Fast search using local index.

```python
def search_indexed(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fast search using the local index (never hits network).

    Supports:
    - Free text search: "climate precipitation"
    - project: filter: "project:weather"
    - Combined: "project:weather temperature"

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of search results with metadata
    """
```

**Search Flow:**

```python
# 1. Parse query
parser = QueryParser()
parsed = parser.parse(query)

# 2. Extract filters
project_filter = None
for term in parsed.terms:
    if term.field == "project":
        project_filter = term.value

# 3. Get free text part
query_text = parsed.free_text_query or ""

# 4. Search index
index_service = get_index_service()
results = index_service.search(
    query_text=query_text,
    project_filter=project_filter,
    limit=limit
)

# 5. Format results
formatted_results = []
for item in results:
    formatted_results.append({
        "id": item["path"],
        "name": item["name"],
        "snippet": item.get("description", "")[:80],
        "metadata": { ... }
    })

return formatted_results
```

**Usage Example:**

```python
from hei_datahub.services.fast_search import search_indexed

# Simple search
results = search_indexed("climate data")

# Filtered search
results = search_indexed("project:weather precipitation")

# Limit results
results = search_indexed("temperature", limit=10)
```

**Related:**
- Uses: `core/queries.py`, `services/index_service.py`
- See: [Search & Autocomplete](../architecture/search-and-autocomplete.md#search-query-flow)

---

### `services/webdav_storage.py`

**Purpose:** WebDAV client for Seafile/HeiBox integration.

**Key Concepts:**
- Standard HTTP methods (PROPFIND, GET, PUT, MKCOL, DELETE)
- Retry logic for 5xx errors
- Credential masking in logs

**Main Class:**

#### `WebDAVStorage`

WebDAV storage backend implementation.

```python
class WebDAVStorage(StorageBackend):
    """WebDAV storage backend for Seafile/Heibox."""

    def __init__(
        self,
        base_url: str,
        library: str,
        username: str,
        password: str,
        connect_timeout: int = 5,
        read_timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize WebDAV storage backend.

        Args:
            base_url: Base WebDAV URL
            library: Library/folder name
            username: WebDAV username
            password: WebDAV password/token
            connect_timeout: Connection timeout
            read_timeout: Read timeout
            max_retries: Max retry attempts on 5xx
        """
```

**Key Methods:**

##### `listdir(path: str = "") -> List[FileEntry]`

List directory contents using PROPFIND.

```python
def listdir(self, path: str = "") -> List[FileEntry]:
    """
    List directory contents using WebDAV PROPFIND.

    Args:
        path: Path relative to library root

    Returns:
        Sorted list of FileEntry objects (directories first)

    Raises:
        StorageAuthError: Authentication failed (401, 403)
        StorageNotFoundError: Path not found (404)
        StorageConnectionError: Network error
    """
```

**PROPFIND Request:**

```python
# Build URL
url = self._get_url(path)

# WebDAV PROPFIND XML
propfind_xml = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:resourcetype/>
    <d:getcontentlength/>
    <d:getlastmodified/>
  </d:prop>
</d:propfind>"""

# Send request
response = self.session.request(
    "PROPFIND",
    url,
    data=propfind_xml.encode("utf-8"),
    headers={"Depth": "1"},
    timeout=(self.connect_timeout, self.read_timeout),
)

# Parse XML response
root = ET.fromstring(response.content)
entries = []
for response in root.findall(".//d:response", NS):
    # Extract href, size, modified, is_dir
    entry = FileEntry(...)
    entries.append(entry)

return sorted(entries, key=lambda e: (not e.is_dir, e.name))
```

##### `read_file(path: str) -> bytes`

Download file contents.

```python
def read_file(self, path: str) -> bytes:
    """
    Download file contents using GET.

    Args:
        path: File path relative to library root

    Returns:
        File contents as bytes

    Raises:
        StorageNotFoundError: File not found
        StorageConnectionError: Network error
    """
```

##### `write_file(path: str, content: bytes) -> None`

Upload file contents.

```python
def write_file(self, path: str, content: bytes) -> None:
    """
    Upload file contents using PUT.

    Args:
        path: File path relative to library root
        content: File contents as bytes

    Raises:
        StorageAuthError: Permission denied
        StorageConnectionError: Network error
    """
```

##### `mkdir(path: str) -> None`

Create directory.

```python
def mkdir(self, path: str) -> None:
    """
    Create directory using MKCOL.

    Args:
        path: Directory path relative to library root

    Raises:
        StorageError: Directory already exists
        StorageAuthError: Permission denied
    """
```

**Helper Functions:**

##### `_mask_auth(url: str) -> str`

Mask authentication info in URLs for logging.

```python
def _mask_auth(url: str) -> str:
    """Mask authentication info in URLs for logging."""
    parsed = urlparse(url)
    if parsed.username:
        return url.replace(
            f"{parsed.username}:{parsed.password}@",
            "***:***@"
        )
    return url

# Example
_mask_auth("https://user:pass@heibox.uni-heidelberg.de/seafdav")
# "https://***:***@heibox.uni-heidelberg.de/seafdav"
```

**Usage Example:**

```python
from hei_datahub.services.webdav_storage import WebDAVStorage

# Initialize
storage = WebDAVStorage(
    base_url="https://heibox.uni-heidelberg.de/seafdav",
    library="my-datasets",
    username="-",
    password="my-webdav-token"
)

# List directory
entries = storage.listdir("datasets")
for entry in entries:
    print(f"{entry.name} ({'dir' if entry.is_dir else 'file'})")

# Read file
content = storage.read_file("datasets/my-dataset/metadata.yaml")

# Write file
storage.write_file("datasets/new-file.txt", b"Hello World")

# Create directory
storage.mkdir("datasets/new-folder")
```

**Related:**
- Implements: `storage_backend.py` interface
- See: [Authentication & Sync](../architecture/auth-and-sync.md#webdav-authentication)

---

### `services/autocomplete.py`

**Purpose:** Real-time autocomplete suggestions for search queries.

**Key Concepts:**
- Debouncing (300ms default)
- Normalization (lowercase, trim)
- Result caching
- Multiple suggestion sources

**Main Class:**

#### `AutocompleteManager`

Manages autocomplete state and suggestions.

```python
class AutocompleteManager:
    """Manages autocomplete suggestions for search queries."""

    def __init__(self, debounce_ms: int = 300):
        """
        Initialize autocomplete manager.

        Args:
            debounce_ms: Debounce delay in milliseconds
        """
        self.debounce_ms = debounce_ms
        self._cache: Dict[str, List[str]] = {}
        self._last_query: Optional[str] = None
```

**Key Methods:**

##### `get_suggestions(query: str) -> List[str]`

Get autocomplete suggestions for query.

```python
def get_suggestions(self, query: str) -> List[str]:
    """
    Get autocomplete suggestions.

    Sources:
    1. Dataset names (partial match)
    2. Project names (from used_in_projects)
    3. Tags/keywords
    4. Recent queries (history)

    Args:
        query: Current search query

    Returns:
        List of suggestions (max 10)
    """
```

**Suggestion Flow:**

```python
# 1. Normalize query
normalized = self._normalize(query)

# 2. Check cache
if normalized in self._cache:
    return self._cache[normalized]

# 3. Gather suggestions
suggestions = []

# From dataset names
for dataset in all_datasets:
    if normalized in dataset.name.lower():
        suggestions.append(dataset.name)

# From projects
for project in all_projects:
    if normalized in project.lower():
        suggestions.append(f"project:{project}")

# From tags
for tag in all_tags:
    if normalized in tag.lower():
        suggestions.append(tag)

# 4. Rank and deduplicate
ranked = self._rank_suggestions(suggestions, normalized)

# 5. Cache results
self._cache[normalized] = ranked[:10]

return ranked[:10]
```

##### `_normalize(query: str) -> str`

Normalize query for matching.

```python
def _normalize(self, query: str) -> str:
    """Normalize query: lowercase, trim, collapse whitespace."""
    return " ".join(query.lower().strip().split())
```

**Usage Example:**

```python
from hei_datahub.services.autocomplete import AutocompleteManager

manager = AutocompleteManager(debounce_ms=300)

# Get suggestions
suggestions = manager.get_suggestions("clim")
# ["climate-data-2024", "project:climate", "climate"]

# Type more
suggestions = manager.get_suggestions("climate pre")
# ["climate precipitation", "climate pressure"]
```

**Related:**
- Used by: UI search input
- See: [Search & Autocomplete](../architecture/search-and-autocomplete.md#autocomplete-system)

---

### `services/sync.py`

**Purpose:** Background synchronization between local and WebDAV storage.

**Key Concepts:**
- Periodic sync (5 minutes)
- Conflict resolution (last-write-wins)
- Outbox for failed operations
- Sync triggers (startup, background, manual)

**Main Functions:**

#### `start_background_sync(interval: int = 300) -> None`

Start background sync thread.

```python
def start_background_sync(interval: int = 300) -> None:
    """
    Start background sync thread.

    Args:
        interval: Sync interval in seconds (default 5 minutes)
    """
    thread = threading.Thread(
        target=_sync_loop,
        args=(interval,),
        daemon=True
    )
    thread.start()
```

#### `sync_now(direction: str = "bidirectional") -> SyncResult`

Perform immediate synchronization.

```python
def sync_now(direction: str = "bidirectional") -> SyncResult:
    """
    Perform immediate sync.

    Args:
        direction: "bidirectional", "download", or "upload"

    Returns:
        SyncResult with stats (uploaded, downloaded, conflicts)
    """
```

**Sync Flow:**

```python
# 1. Get local datasets
local_datasets = list_local_datasets()

# 2. Get remote datasets (WebDAV)
remote_datasets = webdav_storage.listdir("datasets")

# 3. Compare timestamps
for dataset_id in all_dataset_ids:
    local_modified = get_local_modified_time(dataset_id)
    remote_modified = get_remote_modified_time(dataset_id)

    if local_modified > remote_modified:
        # Upload
        upload_dataset(dataset_id)
    elif remote_modified > local_modified:
        # Download
        download_dataset(dataset_id)
    # else: in sync

# 4. Handle conflicts (last-write-wins)
# 5. Update index
# 6. Process outbox (retry failed operations)
```

**Outbox Pattern:**

Failed operations are stored in the outbox for retry.

```python
# On sync failure
def _save_to_outbox(operation: str, dataset_id: str, data: dict):
    """Save failed operation to outbox."""
    outbox_file = OUTBOX_DIR / f"{operation}_{dataset_id}_{timestamp}.json"
    outbox_file.write_text(json.dumps(data))

# On next sync
def _process_outbox():
    """Retry failed operations from outbox."""
    for outbox_file in OUTBOX_DIR.glob("*.json"):
        operation_data = json.loads(outbox_file.read_text())
        try:
            retry_operation(operation_data)
            outbox_file.unlink()  # Success, remove
        except Exception:
            pass  # Keep in outbox for next retry
```

**Related:**
- Uses: `services/webdav_storage.py`
- See: [Authentication & Sync](../architecture/auth-and-sync.md#background-synchronization)

---

## Infrastructure Layer

### `infra/db.py`

**Purpose:** SQLite database connection management.

**Key Concepts:**
- Singleton connection pool
- Row factory (dict results)
- Auto-initialization

**Main Functions:**

#### `get_connection() -> sqlite3.Connection`

Get database connection with row factory.

```python
def get_connection() -> sqlite3.Connection:
    """
    Get SQLite connection with row factory.

    Returns:
        Connection with dict-like row access
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn
```

#### `ensure_database() -> None`

Ensure database exists and is initialized.

```python
def ensure_database() -> None:
    """
    Ensure database exists and schema is initialized.

    Creates tables:
    - datasets_store (JSON payload storage)
    - datasets_fts (FTS5 virtual table)
    - fast_search_index (autocomplete index)
    """
```

**Schema Initialization:**

```python
def ensure_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create store table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_store (
            id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create FTS5 virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts
        USING fts5(
            id UNINDEXED,
            name,
            description,
            used_in_projects,
            data_types,
            source,
            file_format,
            tokenize='porter unicode61'
        )
    """)

    # Create fast search index
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fast_search_index (
            path TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            project TEXT,
            tags TEXT,
            description TEXT,
            format TEXT,
            source TEXT,
            is_remote INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
```

**Usage Example:**

```python
from hei_datahub.infra.db import get_connection, ensure_database

# Initialize database
ensure_database()

# Get connection
conn = get_connection()
cursor = conn.cursor()

# Query (row factory enabled)
cursor.execute("SELECT * FROM datasets_store")
for row in cursor.fetchall():
    print(row["id"], row["payload"])

conn.close()
```

**Related:**
- Used by: `infra/index.py`
- See: [Search & Autocomplete](../architecture/search-and-autocomplete.md#database-schema)

---

### `infra/index.py`

**Purpose:** FTS5 full-text search operations (upsert, delete, query).

**Key Concepts:**
- Dual storage (JSON payload + FTS index)
- Flattens lists for FTS
- Updates fast search index

**Main Functions:**

#### `upsert_dataset(dataset_id: str, metadata: dict) -> None`

Upsert dataset into store and FTS index.

```python
def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """
    Upsert a dataset into both the store and FTS index.
    Also updates the fast search index for instant search.

    Args:
        dataset_id: Dataset ID
        metadata: Full metadata dictionary
    """
```

**Upsert Flow:**

```python
conn = get_connection()
cursor = conn.cursor()

# 1. Store JSON payload
payload = json.dumps(metadata)
cursor.execute("""
    INSERT INTO datasets_store (id, payload, created_at, updated_at)
    VALUES (?, ?, datetime('now'), datetime('now'))
    ON CONFLICT(id) DO UPDATE SET
        payload = excluded.payload,
        updated_at = datetime('now')
""", (dataset_id, payload))

# 2. Delete old FTS entry
cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))

# 3. Insert into FTS index
name = metadata.get("dataset_name", "")
description = metadata.get("description", "")
projects = " ".join(metadata.get("used_in_projects", []))

cursor.execute("""
    INSERT INTO datasets_fts (id, name, description, used_in_projects, ...)
    VALUES (?, ?, ?, ?, ...)
""", (dataset_id, name, description, projects, ...))

conn.commit()

# 4. Update fast search index
index_service.upsert_item(
    path=dataset_id,
    name=name,
    project=projects.split()[0],
    tags=" ".join(metadata.get("keywords", [])),
    ...
)
```

#### `delete_dataset(dataset_id: str) -> None`

Delete dataset from store and FTS index.

```python
def delete_dataset(dataset_id: str) -> None:
    """
    Delete a dataset from both store and FTS index.
    Also removes from the fast search index.

    Args:
        dataset_id: Dataset ID
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM datasets_store WHERE id = ?", (dataset_id,))
    cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))
    conn.commit()

    # Also delete from fast search
    index_service.delete_item(dataset_id)
```

#### `get_dataset_from_store(dataset_id: str) -> Dict`

Get dataset payload from store.

```python
def get_dataset_from_store(dataset_id: str) -> Dict[str, Any]:
    """
    Get dataset payload from store.

    Args:
        dataset_id: Dataset ID

    Returns:
        Dataset metadata dictionary, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT payload FROM datasets_store WHERE id = ?",
        (dataset_id,)
    )
    row = cursor.fetchone()

    if row:
        return json.loads(row["payload"])
    return None
```

**Related:**
- Uses: `infra/db.py`
- Used by: `services/fast_search.py`
- See: [Search & Autocomplete](../architecture/search-and-autocomplete.md#sqlite-fts5-search-engine)

---

### `infra/paths.py`

**Purpose:** Centralized path management for all file system paths.

**Key Concepts:**
- Cross-platform support (Linux, macOS, Windows)
- XDG Base Directory compliance
- Dev mode vs installed mode
- CLI overrides

**Key Paths:**

```python
# XDG Base Directories (all platforms)
XDG_CONFIG_HOME = Path.home() / ".config"
XDG_DATA_HOME = Path.home() / ".local" / "share"
XDG_CACHE_HOME = Path.home() / ".cache"
XDG_STATE_HOME = Path.home() / ".local" / "state"

# Application directories
CONFIG_DIR = XDG_CONFIG_HOME / "hei-datahub"
DATA_DIR = XDG_DATA_HOME / "Hei-DataHub" / "datasets"
CACHE_DIR = XDG_CACHE_HOME / "hei-datahub"
STATE_DIR = XDG_STATE_HOME / "hei-datahub"

# Database
DB_PATH = DATA_DIR.parent / "db.sqlite"

# Config files
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYMAP_FILE = CONFIG_DIR / "keymap.json"

# Logs
LOG_DIR = STATE_DIR / "logs"

# Outbox
OUTBOX_DIR = STATE_DIR / "outbox"
```

**Mode Detection:**

#### `_is_installed_package() -> bool`

Check if running from installed package.

```python
def _is_installed_package() -> bool:
    """Check if running from an installed package (not development mode)."""
    package_path = Path(__file__).resolve()
    return (
        "site-packages" in str(package_path) or
        ".local/share/uv" in str(package_path)
    )
```

#### `_is_dev_mode() -> bool`

Check if running from repository.

```python
def _is_dev_mode() -> bool:
    """
    Check if running from repository (development mode).

    Looks for repo structure: /repo/src/hei_datahub
    """
    package_path = Path(__file__).resolve()
    # Go up 4 levels: infra -> hei_datahub -> src -> repo_root
    potential_repo = package_path.parent.parent.parent.parent
    return (
        (potential_repo / "src" / "hei_datahub").exists() and
        (potential_repo / "pyproject.toml").exists()
    )
```

**Initialization:**

#### `ensure_directories() -> None`

Ensure all required directories exist.

```python
def ensure_directories():
    """Ensure all required directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
```

#### `initialize_workspace() -> None`

Initialize application on first run.

```python
def initialize_workspace():
    """Initialize application on first run (for installed package)."""
    # Ensure directories
    ensure_directories()

    # Copy schema.json to user data directory
    user_schema = PROJECT_ROOT / "schema.json"
    if not user_schema.exists():
        packaged_schema = Path(__file__).parent.parent / "schema.json"
        shutil.copy(packaged_schema, user_schema)

    # Install desktop assets (Linux only)
    if platform.system() == "Linux":
        install_desktop_assets()
```

**Usage Example:**

```python
from hei_datahub.infra.paths import (
    DATA_DIR,
    CONFIG_DIR,
    DB_PATH,
    ensure_directories,
    initialize_workspace
)

# Initialize on first run
initialize_workspace()

# Use paths
dataset_path = DATA_DIR / "my-dataset"
config_path = CONFIG_DIR / "config.toml"
```

**Platform-Specific Paths:**

| Platform | Data Directory |
|----------|----------------|
| Linux | `~/.local/share/Hei-DataHub/` |
| macOS | `~/Library/Application Support/Hei-DataHub/` |
| Windows | `%LOCALAPPDATA%\Hei-DataHub\` |

**Related:**
- Used by: All modules needing file system access
- See: [Architecture Overview](../architecture/overview.md#persistence-strategy)

---

## Summary

This walkthrough covered the key modules in Hei-DataHub:

**Core Layer:**
- `models.py` - Pydantic validation
- `queries.py` - Query parsing

**Authentication Layer:**
- `credentials.py` - Keyring storage
- `setup.py` - Setup wizard
- `validator.py` - Connection validation
- `doctor.py` - Diagnostics
- `clear.py` - Credential removal

**Services Layer:**
- `fast_search.py` - Search interface
- `webdav_storage.py` - WebDAV client
- `autocomplete.py` - Autocomplete engine
- `sync.py` - Background sync

**Infrastructure Layer:**
- `db.py` - Database connections
- `index.py` - FTS5 operations
- `paths.py` - Path management

---

## Related Documentation

- **[Architecture Overview](../architecture/overview.md)** - System architecture
- **[Codebase Overview](overview.md)** - High-level codebase structure
- **[Authentication & Sync](../architecture/auth-and-sync.md)** - WebDAV integration
- **[Search & Autocomplete](../architecture/search-and-autocomplete.md)** - FTS5 search
- **[Security & Privacy](../architecture/security-privacy.md)** - Security best practices
- **[CLI Commands Reference](../api-reference/cli-commands.md)** - Command-line interface

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
