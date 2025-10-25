# Services Module

## Overview

The **Services Layer** orchestrates business logic by coordinating Core domain models and Infrastructure I/O operations. Services implement use cases, handle errors gracefully, and manage cross-cutting concerns like caching and retry logic.

---

## Architecture

**Layer Position:**

```
UI/CLI Layer
     ↓
Services Layer ← YOU ARE HERE
     ↓
Core + Infrastructure
```

**Dependencies:**
- ✅ Can import from `core` and `infra`
- ❌ Cannot import from `ui` or `cli`
- ✅ Implements business workflows

**Design Principles:**
- **Orchestration, not business logic:** Business rules belong in `core`
- **Error handling:** Catch infrastructure errors, provide meaningful responses
- **Stateless preferred:** Minimize mutable state in services
- **Dependency injection:** Accept dependencies via constructor

---

## Service Catalog

### Search Services

#### `fast_search.py` - Main Search Orchestration

**Purpose:** Provide fast, local search without network calls

**Key Functions:**

```python
def search_indexed(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fast search using local SQLite FTS5 index.

    Features:
    - Free text search across all fields
    - `project:name` filter support
    - Sub-100ms query times
    - No network dependency

    Args:
        query: Search query (e.g., "climate project:research")
        limit: Maximum results to return

    Returns:
        List of dataset dictionaries with metadata

    Example:
        >>> results = search_indexed("climate data", limit=10)
        >>> print(results[0]['name'])
        'Climate Model Output'
    """
```

**Query Parsing:**

```python
# Input: "climate project:research tag:oceanography"
# Parsed to:
# - Free text: "climate"
# - Project filter: "research"
# - Tag filter: "oceanography" (future)
```

**Performance:**
- **Target:** <80ms
- **Typical:** 50-80ms
- **Optimization:** Query result caching (60s TTL)

**Usage:**

```python
from mini_datahub.services.fast_search import search_indexed

# Simple search
results = search_indexed("climate data")

# With project filter
results = search_indexed("temperature project:climate-study")

# Limited results
results = search_indexed("ocean", limit=5)
```

---

#### `index_service.py` - FTS5 Index Management

**Purpose:** Manage SQLite FTS5 search index

**Key Class:**

```python
class IndexService:
    """
    Fast local search index with SQLite FTS5.

    Features:
    - Full-text search with BM25 ranking
    - Porter stemming (tokenizer)
    - Automatic index updates
    - Query result caching
    """

    def search(
        self,
        query_text: str,
        project_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Execute FTS5 search query"""
```

**Database Schema:**

```sql
-- Main table
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    project TEXT,
    tags TEXT,
    description TEXT,
    format TEXT,
    source TEXT,
    is_remote INTEGER DEFAULT 0,
    mtime INTEGER,
    etag TEXT
);

-- FTS5 virtual table
CREATE VIRTUAL TABLE items_fts USING fts5(
    name,
    path,
    project,
    tags,
    description,
    tokenize = 'porter ascii'
);

-- Triggers to sync items → items_fts
CREATE TRIGGER items_ai AFTER INSERT ON items BEGIN
    INSERT INTO items_fts(rowid, name, path, project, tags, description)
    VALUES (new.id, new.name, new.path, new.project, new.tags, new.description);
END;
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `search()` | Execute FTS5 query with filters |
| `upsert()` | Add or update dataset in index |
| `delete()` | Remove dataset from index |
| `rebuild()` | Rebuild index from scratch |
| `get_stats()` | Get index statistics (count, size) |

---

#### `autocomplete.py` - Field Autocomplete

**Purpose:** Suggest values for form fields based on existing datasets

**Key Class:**

```python
class AutocompleteManager:
    """
    Provide autocomplete suggestions for dataset fields.

    Suggests:
    - Project names (from used_in_projects)
    - File formats (csv, json, parquet, etc.)
    - Data types (tabular, time-series, geospatial, etc.)
    - Sources (common URLs/paths)
    """

    def get_project_suggestions(self, prefix: str = "") -> List[str]:
        """Get project name suggestions"""

    def get_format_suggestions(self, prefix: str = "") -> List[str]:
        """Get file format suggestions"""
```

**Data Sources:**
1. **Database index:** Fastest, preferred
2. **YAML files:** Fallback if index unavailable
3. **Canonical lists:** Built-in common values

**Normalization:**

```python
# Format normalization
"CSV" → "csv"
"XLSX" → "xlsx"
"Excel" → "xlsx"

# Type normalization
"TimeSeries" → "time-series"
"GeoSpatial" → "geospatial"
```

**Usage:**

```python
autocomplete = AutocompleteManager()
autocomplete.load_from_catalog()

# Get suggestions
projects = autocomplete.get_project_suggestions(prefix="clim")
# Returns: ["climate-study", "climate-modeling", ...]

formats = autocomplete.get_format_suggestions()
# Returns: ["csv", "json", "parquet", ...]
```

---

### Storage Services

#### `webdav_storage.py` - WebDAV Client

**Purpose:** WebDAV operations for HeiBox/Seafile

**Key Class:**

```python
class WebDAVStorage:
    """
    WebDAV storage client for remote dataset storage.

    Features:
    - HTTPS-only connections
    - Token authentication
    - Directory listing (PROPFIND)
    - File upload/download (PUT/GET)
    - Error handling and retries
    """

    def list_remote_files(self, remote_dir: str = "datasets") -> List[Dict]:
        """List files in remote directory"""

    def download_file(self, remote_path: str, local_path: Path) -> None:
        """Download file from WebDAV to local path"""

    def upload_file(self, local_path: Path, remote_path: str) -> None:
        """Upload file from local path to WebDAV"""
```

**HTTP Methods Used:**

| Method | Purpose | Example |
|--------|---------|---------|
| `PROPFIND` | List files + metadata | Get all datasets in `/datasets` |
| `GET` | Download file | Download `metadata.yaml` |
| `PUT` | Upload file | Upload new dataset |
| `DELETE` | Remove file | Delete dataset |
| `MKCOL` | Create directory | Create project folder |

**Authentication:**

```python
# Token-based authentication
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "text/yaml"
}
```

**Error Handling:**

```python
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.Timeout:
    logger.error("WebDAV request timed out")
    raise StorageError("Connection timeout")
except requests.HTTPError as e:
    if e.response.status_code == 401:
        raise AuthenticationError("Invalid credentials")
    raise StorageError(f"HTTP {e.response.status_code}")
```

---

#### `storage_manager.py` - Unified Storage Interface

**Purpose:** Abstract storage backend (local vs. remote)

**Key Class:**

```python
class StorageManager:
    """
    Unified interface for dataset storage.

    Supports:
    - Local filesystem storage
    - WebDAV remote storage
    - Hybrid (local cache + remote sync)
    """

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Get dataset from local cache or remote"""

    def save_dataset(self, dataset_id: str, metadata: Dict) -> None:
        """Save dataset to local + queue for remote upload"""

    def delete_dataset(self, dataset_id: str) -> None:
        """Delete dataset locally and remotely"""
```

**Storage Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| `local` | Local filesystem only | Development, testing |
| `remote` | WebDAV only | Shared datasets, CI/CD |
| `hybrid` | Local cache + remote sync | Normal operation (default) |

**Hybrid Mode Flow:**

```
Read:  Check local cache → If miss, download from remote
Write: Save to local → Queue for background upload
Delete: Delete local → Queue for remote deletion
```

---

#### `outbox.py` - Failed Upload Queue

**Purpose:** Retry mechanism for failed uploads

**Key Class:**

```python
class OutboxManager:
    """
    Queue for failed uploads (outbox pattern).

    When uploads fail (network error, timeout):
    1. Save to outbox queue
    2. Retry in background (exponential backoff)
    3. Remove from outbox when successful
    """

    def add_to_outbox(self, dataset_id: str, content: str) -> None:
        """Add failed upload to retry queue"""

    def process_outbox(self) -> int:
        """Retry all queued uploads, return success count"""
```

**Retry Strategy:**

```python
# Exponential backoff
attempt_1: Wait 1 minute
attempt_2: Wait 2 minutes
attempt_3: Wait 4 minutes
attempt_4: Wait 8 minutes
attempt_5: Wait 16 minutes
# Max: 5 attempts, then manual intervention required
```

**Outbox Storage:**

```
~/.local/share/hei-datahub/outbox/
├── climate-data.yaml         # Queued upload
├── ocean-temp.yaml
└── .metadata.json            # Retry counts, timestamps
```

---

### Sync Services

#### `sync.py` - Background Sync Manager

**Purpose:** Orchestrate bidirectional sync between local and remote

**Key Functions:**

```python
def sync_now() -> SyncResult:
    """
    Perform one-time sync operation.

    Algorithm:
    1. List remote files (WebDAV PROPFIND)
    2. List local files (SQLite query)
    3. Compare timestamps (mtime)
    4. Download remote-newer files
    5. Upload local-newer files
    6. Update index

    Returns:
        SyncResult with download/upload counts
    """
```

**Sync Algorithm:**

```python
for dataset_id in all_datasets:
    local_mtime = get_local_mtime(dataset_id)
    remote_mtime = get_remote_mtime(dataset_id)

    if remote_mtime > local_mtime:
        download(dataset_id)  # Remote is newer
    elif local_mtime > remote_mtime:
        upload(dataset_id)    # Local is newer
    else:
        pass  # Already in sync
```

**Conflict Resolution:**
- **Strategy:** Last-write-wins (timestamp comparison)
- **No user prompt:** Automatic resolution
- **Risk:** Concurrent edits may lose changes
- **Future:** Conflict detection UI

**Background Sync:**

```python
# Run every 5 minutes (configurable)
while app_running:
    time.sleep(SYNC_INTERVAL)
    try:
        result = sync_now()
        logger.info(f"Synced: {result.downloads} down, {result.uploads} up")
    except Exception as e:
        logger.error(f"Sync failed: {e}")
```

---

### Catalog Services

#### `catalog.py` - Catalog Operations

**Purpose:** High-level catalog management (list, validate, export)

**Key Functions:**

```python
def list_all_datasets(include_remote: bool = True) -> List[Dict]:
    """List all datasets (local + optionally remote)"""

def validate_catalog() -> List[ValidationError]:
    """Validate all datasets against schema"""

def export_catalog(output_path: Path, format: str = "json") -> None:
    """Export entire catalog to file"""
```

**Validation:**

```python
errors = validate_catalog()
for error in errors:
    print(f"{error.dataset_id}: {error.message}")

# Example output:
# climate-data: Missing required field 'source'
# ocean-temp: Invalid date format in 'date_created'
```

---

### Utility Services

#### `config.py` - Configuration Management

**Purpose:** Load and save configuration files

**Key Functions:**

```python
def load_config() -> Dict[str, Any]:
    """Load config.toml from standard location"""

def save_config(config: Dict) -> None:
    """Save config.toml"""

def get_config_value(key: str, default: Any = None) -> Any:
    """Get single config value with default"""
```

**Config File Structure:**

```toml
[webdav]
url = "https://heibox.uni-heidelberg.de"
library = "research-datasets"
key_id = "webdav-heibox-research"  # Reference to keyring

[sync]
enabled = true
interval_minutes = 5

[search]
debounce_ms = 300
max_results = 50
```

---

#### `update_check.py` - Version Update Checker

**Purpose:** Check for newer versions

**Key Function:**

```python
def check_for_updates() -> Optional[UpdateInfo]:
    """
    Check for newer version.

    Returns:
        UpdateInfo if update available, else None
    """
```

**Usage:**

```python
update = check_for_updates()
if update:
    print(f"New version available: {update.version}")
    print(f"Download: {update.url}")
```

**Update Check Strategy:**
- Check on startup (if enabled)
- Check every 24 hours
- Respect `check_for_updates = false` in config

---

## Service Interaction Patterns

### Dependency Injection

**✅ CORRECT:** Inject dependencies

```python
class DatasetService:
    def __init__(
        self,
        index: IndexService,
        storage: WebDAVStorage,
        outbox: OutboxManager
    ):
        self.index = index
        self.storage = storage
        self.outbox = outbox
```

**❌ WRONG:** Hardcoded dependencies

```python
class DatasetService:
    def __init__(self):
        self.index = IndexService()  # ❌ Hardcoded
        self.storage = WebDAVStorage()  # ❌ Hard to test
```

### Error Handling

**✅ CORRECT:** Graceful degradation

```python
def search_with_fallback(query: str) -> List[Dict]:
    """Search with fallback to simpler method"""
    try:
        return search_indexed(query)  # Fast FTS5 search
    except DatabaseError as e:
        logger.warning(f"Index search failed: {e}")
        return search_simple(query)  # Fallback to basic search
```

### Caching

**✅ CORRECT:** Cache with TTL

```python
class SearchCache:
    def __init__(self, ttl: int = 60):
        self._cache: Dict[str, Tuple[float, List]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[List]:
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
        return None
```

---

## Testing Services

### Unit Testing

**Mock infrastructure dependencies:**

```python
def test_search_with_filters():
    # Arrange
    mock_index = Mock(spec=IndexService)
    mock_index.search.return_value = [{"id": "test", "name": "Test"}]

    # Act
    results = fast_search.search_indexed("query")

    # Assert
    assert len(results) == 1
    mock_index.search.assert_called_once()
```

### Integration Testing

**Test service + infrastructure:**

```python
def test_search_end_to_end(tmp_path):
    # Use real IndexService with temp database
    index = IndexService(db_path=tmp_path / "test.db")
    index.upsert({"id": "test", "name": "Test Dataset"})

    results = search_indexed("Test")
    assert len(results) == 1
    assert results[0]["name"] == "Test Dataset"
```

---

## Performance Targets

| Service | Operation | Target | Typical |
|---------|-----------|--------|---------|
| `fast_search` | Simple query | <80ms | 50-80ms |
| `autocomplete` | Get suggestions | <50ms | 20-40ms |
| `index_service` | Upsert | <10ms | 5-10ms |
| `webdav_storage` | List files | <500ms | 200-500ms |
| `sync` | Full sync (100 datasets) | <30s | 15-30s |

---

## Related Documentation

- **[Architecture Overview](../architecture/overview.md)** - System architecture
- **[Infrastructure Module](infra-module.md)** - I/O layer details
- **[Core Module](core-module.md)** - Domain models
- **[Module Walkthrough](module-walkthrough.md)** - Function-level tour

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
