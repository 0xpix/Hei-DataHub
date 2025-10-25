# Infrastructure Module

## Overview

The **Infrastructure Layer** handles all I/O operations: database access, file system operations, network requests, and external service integrations. This layer implements the interfaces defined in the Core layer.

---

## Architecture

**Layer Position:**

```
Services Layer
     ↓
Infrastructure Layer ← YOU ARE HERE
     ↓
External Systems (Database, Filesystem, Network)
```

**Dependencies:**
- ✅ Can import from `core` (to implement interfaces)
- ❌ Cannot import from `services`, `ui`, or `cli`
- ✅ Handles all external I/O operations

**Design Principles:**
- **Implement Core interfaces:** Concrete implementations of abstract interfaces
- **Error handling:** Convert I/O errors to domain errors
- **Isolation:** Keep I/O concerns isolated from business logic
- **Testability:** Use dependency injection for easier mocking

---

## Module Catalog

### Database Operations

#### `db.py` - Database Connection Management

**Purpose:** Manage SQLite database connections and lifecycle

**Key Functions:**

```python
def get_connection() -> sqlite3.Connection:
    """
    Get or create SQLite database connection.

    Features:
    - Connection pooling (singleton pattern)
    - Row factory for dict-like access
    - Foreign keys enabled
    - WAL mode for concurrent reads

    Returns:
        Active SQLite connection
    """

def ensure_database() -> None:
    """
    Ensure database schema exists, create if not.

    Operations:
    1. Create database file if missing
    2. Execute schema.sql
    3. Run pending migrations
    4. Verify integrity
    """

def close_connection() -> None:
    """
    Close database connection gracefully.
    Called on app shutdown.
    """
```

**Connection Configuration:**

```python
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row  # Enable dict-like access
conn.execute("PRAGMA foreign_keys = ON")
conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
```

**Usage:**

```python
from mini_datahub.infra.db import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM datasets_store WHERE id = ?", (dataset_id,))
row = cursor.fetchone()
conn.close()
```

---

#### `index.py` - FTS5 Search Index

**Purpose:** Full-text search using SQLite FTS5

**Key Functions:**

```python
def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """
    Insert or update dataset in both store and FTS index.

    Tables Updated:
    - datasets_store: JSON payload storage
    - datasets_fts: FTS5 search index
    - fast_search_index: Autocomplete index

    Args:
        dataset_id: Unique dataset identifier
        metadata: Complete dataset metadata dict
    """

def search_datasets(
    query: str,
    filters: dict[str, list[str]] | None = None,
    limit: int = 50
) -> list[dict]:
    """
    Search datasets using FTS5 MATCH query.

    Features:
    - Full-text search with BM25 ranking
    - Porter stemming
    - Project filtering
    - Tag filtering (future)

    Args:
        query: Search query string
        filters: Optional filters like {"project": ["proj1"]}
        limit: Maximum results

    Returns:
        List of matching datasets with metadata
    """
```

**Database Schema:**

```sql
-- JSON payload storage
CREATE TABLE datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,  -- JSON metadata
    created_at TEXT,
    updated_at TEXT
);

-- FTS5 virtual table
CREATE TABLE datasets_fts (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    used_in_projects TEXT,
    data_types TEXT,
    source TEXT,
    file_format TEXT
) USING fts5(
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    tokenize = 'porter ascii'
);
```

**FTS5 Query Example:**

```sql
-- Simple search
SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'climate';

-- With ranking
SELECT id, name, rank
FROM datasets_fts
WHERE datasets_fts MATCH 'climate'
ORDER BY rank
LIMIT 50;

-- With project filter
SELECT d.*
FROM datasets_fts f
JOIN datasets_store d ON f.id = d.id
WHERE f.datasets_fts MATCH 'climate'
  AND f.used_in_projects LIKE '%research%';
```

**Performance Optimizations:**

```python
# 1. Create indexes on frequently queried columns
CREATE INDEX idx_datasets_updated ON datasets_store(updated_at);

# 2. Use PRAGMA optimizations
PRAGMA synchronous = NORMAL;   # Faster writes
PRAGMA cache_size = -64000;    # 64MB cache
PRAGMA temp_store = MEMORY;    # In-memory temp tables
```

---

#### `store.py` - Dataset Store Operations

**Purpose:** CRUD operations for dataset storage

**Key Functions:**

```python
def get_dataset(dataset_id: str) -> dict | None:
    """Get dataset by ID from store"""

def list_datasets(limit: int = 200) -> list[dict]:
    """List all datasets"""

def dataset_exists(dataset_id: str) -> bool:
    """Check if dataset exists"""

def get_dataset_count() -> int:
    """Get total dataset count"""
```

**Implementation:**

```python
def get_dataset(dataset_id: str) -> dict | None:
    """Get dataset metadata by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT payload FROM datasets_store WHERE id = ?",
        (dataset_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row["payload"])
    return None
```

---

### File System Operations

#### `paths.py` - Path Configuration

**Purpose:** Centralized path configuration for all app directories

**Key Paths:**

```python
from pathlib import Path

# User directories (XDG Base Directory spec)
CONFIG_DIR = Path.home() / ".config" / "hei-datahub"
DATA_DIR = Path.home() / ".local" / "share" / "hei-datahub"
CACHE_DIR = Path.home() / ".cache" / "hei-datahub"

# Specific files
CONFIG_FILE = CONFIG_DIR / "config.toml"
DB_PATH = DATA_DIR / "db.sqlite"
INDEX_DB_PATH = CACHE_DIR / "index.db"
OUTBOX_DIR = DATA_DIR / "outbox"
LOG_DIR = DATA_DIR / "logs"

# Dataset directories
DATASETS_DIR = DATA_DIR / "datasets"
SCHEMAS_DIR = DATA_DIR / "schemas"
```

**Directory Creation:**

```python
def ensure_directories() -> None:
    """Create all necessary directories"""
    for directory in [CONFIG_DIR, DATA_DIR, CACHE_DIR, OUTBOX_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
```

**Usage:**

```python
from mini_datahub.infra.paths import CONFIG_FILE, DB_PATH

# Load config
with open(CONFIG_FILE) as f:
    config = toml.load(f)

# Open database
conn = sqlite3.connect(DB_PATH)
```

---

#### `config_paths.py` - Platform-Specific Paths

**Purpose:** Handle platform-specific path differences (Linux/macOS/Windows)

**Platform Detection:**

```python
import platform

def get_platform_config_dir() -> Path:
    """Get platform-specific config directory"""
    system = platform.system()

    if system == "Linux":
        return Path.home() / ".config" / "hei-datahub"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "hei-datahub"
    elif system == "Windows":
        return Path(os.environ["APPDATA"]) / "hei-datahub"
    else:
        return Path.home() / ".hei-datahub"
```

---

### SQL Schema Files

#### `sql/schema.sql` - Database Schema

**Purpose:** Initial database schema definition

**Contents:**

```sql
-- Datasets store (JSON payloads)
CREATE TABLE IF NOT EXISTS datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- FTS5 search index
CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts USING fts5(
    id,
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    tokenize = 'porter ascii'
);

-- Fast search index (autocomplete)
CREATE TABLE IF NOT EXISTS fast_search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_datasets_updated
    ON datasets_store(updated_at);

CREATE INDEX IF NOT EXISTS idx_fast_search_name
    ON fast_search_index(name);

CREATE INDEX IF NOT EXISTS idx_fast_search_project
    ON fast_search_index(project);
```

**Execution:**

```python
def ensure_database():
    """Create database schema from schema.sql"""
    conn = get_connection()
    schema_path = Path(__file__).parent / "sql" / "schema.sql"

    with open(schema_path) as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
```

---

#### `sql/migrations/` - Database Migrations

**Purpose:** Schema evolution over versions

**Structure:**

```
sql/migrations/
├── 001_add_fast_search.sql
├── 002_add_timestamps.sql
└── 003_add_webdav_fields.sql
```

**Migration Example:**

```sql
-- 003_add_webdav_fields.sql
ALTER TABLE fast_search_index ADD COLUMN etag TEXT;
ALTER TABLE fast_search_index ADD COLUMN is_remote INTEGER DEFAULT 0;

-- Update version
INSERT INTO schema_version (version, applied_at)
VALUES (3, datetime('now'));
```

**Migration Runner:**

```python
def run_migrations():
    """Run pending database migrations"""
    conn = get_connection()
    current_version = get_schema_version(conn)

    migrations_dir = Path(__file__).parent / "sql" / "migrations"
    for migration_file in sorted(migrations_dir.glob("*.sql")):
        version = int(migration_file.stem.split("_")[0])

        if version > current_version:
            with open(migration_file) as f:
                conn.executescript(f.read())
            logger.info(f"Applied migration {version}")

    conn.commit()
```

---

## Error Handling

### Converting I/O Errors to Domain Errors

**✅ CORRECT:** Wrap I/O errors

```python
from mini_datahub.core.exceptions import StorageError

def read_dataset_file(path: Path) -> dict:
    """Read dataset YAML file"""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise StorageError(f"Dataset file not found: {path}")
    except yaml.YAMLError as e:
        raise StorageError(f"Invalid YAML in {path}: {e}")
    except PermissionError:
        raise StorageError(f"Permission denied reading {path}")
```

### Database Error Handling

**✅ CORRECT:** Handle SQLite errors

```python
def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """Insert or update dataset"""
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO datasets_store (id, payload) VALUES (?, ?)",
            (dataset_id, json.dumps(metadata))
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise StorageError(f"Database integrity error: {e}")
    except sqlite3.OperationalError as e:
        conn.rollback()
        raise StorageError(f"Database operation failed: {e}")
    finally:
        conn.close()
```

---

## Performance Considerations

### Database Optimization

**1. Use Indexes:**

```sql
CREATE INDEX idx_datasets_updated ON datasets_store(updated_at);
CREATE INDEX idx_fast_search_name ON fast_search_index(name);
```

**2. Batch Operations:**

```python
def bulk_upsert(datasets: list[tuple[str, dict]]) -> None:
    """Bulk insert datasets (faster than individual upserts)"""
    conn = get_connection()
    cursor = conn.cursor()

    # Prepare data
    data = [(id, json.dumps(meta)) for id, meta in datasets]

    # Use executemany for batch insert
    cursor.executemany(
        "INSERT OR REPLACE INTO datasets_store (id, payload) VALUES (?, ?)",
        data
    )
    conn.commit()
    conn.close()
```

**3. Connection Pooling:**

```python
# Singleton connection pattern
_connection = None

def get_connection() -> sqlite3.Connection:
    """Get cached connection (connection pooling)"""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection
```

### FTS5 Query Optimization

**1. Use Specific Columns:**

```sql
-- ✅ GOOD: Search specific column
SELECT * FROM datasets_fts WHERE name MATCH 'climate';

-- ❌ SLOW: Search all columns
SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'climate';
```

**2. Limit Results:**

```sql
-- Always use LIMIT
SELECT * FROM datasets_fts WHERE name MATCH 'climate' LIMIT 50;
```

**3. Use Query Cache:**

```python
@lru_cache(maxsize=128)
def search_cached(query: str, limit: int) -> tuple:
    """Cache search results (tuple for hashability)"""
    results = search_datasets(query, limit=limit)
    return tuple(json.dumps(r) for r in results)
```

---

## Testing Infrastructure

### Unit Testing with Mock Database

```python
import tempfile
from pathlib import Path
import pytest

@pytest.fixture
def test_db():
    """Create temporary test database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Override DB_PATH
        import mini_datahub.infra.db as db_module
        original_path = db_module.DB_PATH
        db_module.DB_PATH = db_path

        # Initialize schema
        db_module.ensure_database()

        yield db_path

        # Restore original path
        db_module.DB_PATH = original_path

def test_upsert_dataset(test_db):
    """Test dataset upsert"""
    from mini_datahub.infra.index import upsert_dataset

    metadata = {"id": "test", "dataset_name": "Test Dataset"}
    upsert_dataset("test", metadata)

    # Verify stored
    from mini_datahub.infra.store import get_dataset
    stored = get_dataset("test")
    assert stored["dataset_name"] == "Test Dataset"
```

---

## Related Documentation

- **[Services Module](services-module.md)** - Business logic layer
- **[Core Module](core-module.md)** - Domain models
- **[Data Layer](../data/overview.md)** - Data storage architecture
- **[Performance](../performance/overview.md)** - Performance optimization

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
