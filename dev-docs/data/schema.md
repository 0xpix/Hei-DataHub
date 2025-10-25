# Database Schema

## Introduction

Hei-DataHub uses **SQLite** for local storage with three main components:
1. **datasets_store** - Complete metadata storage (JSON)
2. **datasets_fts** - Full-text search index (FTS5)
3. **fast_search_index** - Autocomplete and quick lookups

---

## Schema Overview

```sql
-- Schema version tracking
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);

-- Main dataset store
CREATE TABLE datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Full-text search index
CREATE VIRTUAL TABLE datasets_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    tokenize = 'porter ascii'
);

-- Fast search index (autocomplete)
CREATE TABLE fast_search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    project TEXT,
    tags TEXT,
    description TEXT,
    format TEXT,
    is_remote INTEGER DEFAULT 0,
    etag TEXT
);

-- Indexes for fast_search_index
CREATE INDEX idx_name ON fast_search_index(name);
CREATE INDEX idx_project ON fast_search_index(project);
CREATE INDEX idx_tags ON fast_search_index(tags);
CREATE INDEX idx_remote ON fast_search_index(is_remote);
```

---

## Table Details

### 1. schema_version

**Purpose:** Track applied database migrations

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `version` | INTEGER | PRIMARY KEY | Migration version number |
| `applied_at` | TEXT | DEFAULT (datetime('now')) | Timestamp when migration applied |

**Example Data:**

```sql
SELECT * FROM schema_version;
```

| version | applied_at |
|---------|------------|
| 1 | 2024-01-15 10:00:00 |
| 2 | 2024-02-20 14:30:00 |
| 3 | 2024-03-10 09:15:00 |

**Usage:**

```python
def get_current_schema_version() -> int:
    """Get current schema version"""
    cursor.execute("SELECT MAX(version) FROM schema_version")
    result = cursor.fetchone()
    return result[0] if result[0] is not None else 0
```

---

### 2. datasets_store

**Purpose:** Primary storage for complete dataset metadata

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Unique dataset identifier |
| `payload` | TEXT | NOT NULL | Complete metadata as JSON |
| `created_at` | TEXT | DEFAULT (datetime('now')) | Creation timestamp |
| `updated_at` | TEXT | DEFAULT (datetime('now')) | Last update timestamp |

**Example Data:**

```sql
SELECT id, created_at, updated_at FROM datasets_store LIMIT 3;
```

| id | created_at | updated_at |
|----|------------|------------|
| climate-data | 2024-01-15 10:30:00 | 2024-01-20 15:45:00 |
| ocean-temp | 2024-01-16 11:00:00 | 2024-01-16 11:00:00 |
| research-notes | 2024-01-17 09:15:00 | 2024-01-18 14:30:00 |

**Payload Structure:**

```json
{
  "id": "climate-data",
  "dataset_name": "Climate Model Data",
  "description": "Historical climate model outputs from CMIP6",
  "source": "https://esgf-node.llnl.gov/",
  "date_created": "2024-01-15",
  "storage_location": "/data/climate/cmip6",
  "file_format": "NetCDF",
  "used_in_projects": ["climate-study", "future-projections"],
  "data_types": ["time-series", "geospatial"],
  "keywords": ["climate", "temperature", "precipitation"],
  "access_level": "public",
  "contact_person": "jane.doe@uni-heidelberg.de",
  "data_size_gb": 150.5,
  "documentation_url": "https://docs.example.com/climate-data"
}
```

**Operations:**

```python
# Insert/Update (upsert)
def upsert_dataset(dataset_id: str, payload: dict) -> None:
    cursor.execute(
        """
        INSERT INTO datasets_store (id, payload, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            payload = excluded.payload,
            updated_at = excluded.updated_at
        """,
        (dataset_id, json.dumps(payload))
    )
    conn.commit()

# Read by ID
def get_dataset(dataset_id: str) -> dict | None:
    cursor.execute(
        "SELECT payload FROM datasets_store WHERE id = ?",
        (dataset_id,)
    )
    row = cursor.fetchone()
    return json.loads(row[0]) if row else None

# List all
def list_all_datasets() -> list[dict]:
    cursor.execute("SELECT id, payload FROM datasets_store")
    return [
        {"id": row[0], **json.loads(row[1])}
        for row in cursor.fetchall()
    ]

# Delete
def delete_dataset(dataset_id: str) -> None:
    cursor.execute("DELETE FROM datasets_store WHERE id = ?", (dataset_id,))
    conn.commit()
```

---

### 3. datasets_fts

**Purpose:** Full-text search index using SQLite FTS5

**Columns:**

| Column | Type | Indexed | Description |
|--------|------|---------|-------------|
| `id` | TEXT | UNINDEXED | Dataset ID (not searchable) |
| `name` | TEXT | YES | Dataset name |
| `description` | TEXT | YES | Dataset description |
| `used_in_projects` | TEXT | YES | Projects using dataset |
| `data_types` | TEXT | YES | Data type tags |
| `source` | TEXT | YES | Data source URL |
| `file_format` | TEXT | YES | File format |

**Configuration:**

- **Tokenizer:** `porter ascii`
  - `porter` - Porter stemming (e.g., "running" → "run")
  - `ascii` - ASCII case-folding (Unicode normalization)

**Example Data:**

```sql
SELECT id, name FROM datasets_fts LIMIT 3;
```

| id | name |
|----|------|
| climate-data | Climate Model Data |
| ocean-temp | Ocean Temperature Records |
| research-notes | Research Field Notes |

**Search Queries:**

```python
# Simple search
def search_by_term(term: str) -> list[dict]:
    cursor.execute(
        """
        SELECT id, name, rank
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        ORDER BY rank
        LIMIT 50
        """,
        (term,)
    )
    return cursor.fetchall()

# Phrase search (exact match)
def search_phrase(phrase: str) -> list[dict]:
    cursor.execute(
        """
        SELECT id, name
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        """,
        (f'"{phrase}"',)  # Quoted for exact match
    )
    return cursor.fetchall()

# Boolean search
def search_boolean(query: str) -> list[dict]:
    # Example: "climate AND temperature"
    cursor.execute(
        """
        SELECT id, name
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        """,
        (query,)
    )
    return cursor.fetchall()

# Field-specific search
def search_in_field(field: str, term: str) -> list[dict]:
    cursor.execute(
        f"""
        SELECT id, name
        FROM datasets_fts
        WHERE {field} MATCH ?
        """,
        (term,)
    )
    return cursor.fetchall()
```

**Ranking:**

FTS5 uses **BM25 algorithm** for ranking:

```sql
-- View ranking scores
SELECT id, name, rank
FROM datasets_fts
WHERE datasets_fts MATCH 'climate'
ORDER BY rank  -- Lower rank = better match
LIMIT 10;
```

---

### 4. fast_search_index

**Purpose:** Denormalized index for autocomplete and quick lookups

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Auto-increment ID |
| `path` | TEXT | UNIQUE NOT NULL | Dataset ID (unique) |
| `name` | TEXT | NOT NULL | Dataset name |
| `project` | TEXT | NULL | Primary project name |
| `tags` | TEXT | NULL | Space-separated tags |
| `description` | TEXT | NULL | Brief description |
| `format` | TEXT | NULL | File format |
| `is_remote` | INTEGER | DEFAULT 0 | 1 if cloud-only, 0 if local |
| `etag` | TEXT | NULL | WebDAV ETag (for caching) |

**Indexes:**

```sql
CREATE INDEX idx_name ON fast_search_index(name);
CREATE INDEX idx_project ON fast_search_index(project);
CREATE INDEX idx_tags ON fast_search_index(tags);
CREATE INDEX idx_remote ON fast_search_index(is_remote);
```

**Example Data:**

```sql
SELECT * FROM fast_search_index LIMIT 3;
```

| id | path | name | project | tags | format | is_remote | etag |
|----|------|------|---------|------|--------|-----------|------|
| 1 | climate-data | Climate Model Data | climate-study | climate temperature | NetCDF | 0 | "abc123" |
| 2 | ocean-temp | Ocean Temperature Records | ocean-research | ocean temperature | CSV | 0 | "def456" |
| 3 | research-notes | Research Field Notes | field-study | notes observations | Markdown | 1 | "ghi789" |

**Operations:**

```python
# Autocomplete (prefix search)
def autocomplete_names(prefix: str) -> list[str]:
    cursor.execute(
        """
        SELECT DISTINCT name
        FROM fast_search_index
        WHERE name LIKE ?
        LIMIT 10
        """,
        (f"{prefix}%",)
    )
    return [row[0] for row in cursor.fetchall()]

# Filter by project
def datasets_by_project(project: str) -> list[dict]:
    cursor.execute(
        """
        SELECT path, name, format
        FROM fast_search_index
        WHERE project = ?
        """,
        (project,)
    )
    return cursor.fetchall()

# Tag search (contains)
def search_by_tag(tag: str) -> list[dict]:
    cursor.execute(
        """
        SELECT path, name, tags
        FROM fast_search_index
        WHERE tags LIKE ?
        """,
        (f"%{tag}%",)
    )
    return cursor.fetchall()

# Remote-only datasets
def list_remote_only() -> list[str]:
    cursor.execute(
        """
        SELECT path, name
        FROM fast_search_index
        WHERE is_remote = 1
        """
    )
    return cursor.fetchall()

# Upsert entry
def update_fast_index(dataset: dict) -> None:
    cursor.execute(
        """
        INSERT INTO fast_search_index (path, name, project, tags, description, format, is_remote)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            name = excluded.name,
            project = excluded.project,
            tags = excluded.tags,
            description = excluded.description,
            format = excluded.format,
            is_remote = excluded.is_remote
        """,
        (
            dataset["id"],
            dataset["dataset_name"],
            dataset.get("used_in_projects", [None])[0],  # First project
            " ".join(dataset.get("keywords", [])),
            dataset.get("description", ""),
            dataset.get("file_format", ""),
            0  # Local by default
        )
    )
    conn.commit()
```

---

## Data Relationships

```
┌─────────────────────┐
│  datasets_store     │ ← Primary storage (JSON payloads)
│  id (PK)            │
│  payload            │
│  created_at         │
│  updated_at         │
└──────────┬──────────┘
           │
           │ (Sync on write)
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌─────────────────────┐
│  datasets_fts    │   │ fast_search_index   │
│  id              │   │ path                │
│  name            │   │ name                │
│  description     │   │ project             │
│  ...             │   │ tags                │
└──────────────────┘   └─────────────────────┘
   (FTS5 search)          (Autocomplete)
```

**Data Flow:**

1. **Write:** Insert/update `datasets_store` → Update `datasets_fts` and `fast_search_index`
2. **Read:** Query `datasets_fts` or `fast_search_index` → Fetch full data from `datasets_store`
3. **Delete:** Remove from all three tables

---

## Schema Migrations

### Migration Files

**Location:** `src/mini_datahub/infra/migrations/`

**Naming:** `XXX_description.sql` (e.g., `003_add_etag_field.sql`)

**Example Migration:**

```sql
-- migrations/003_add_etag_field.sql

-- Add ETag column for caching
ALTER TABLE fast_search_index ADD COLUMN etag TEXT;

-- Add is_remote flag
ALTER TABLE fast_search_index ADD COLUMN is_remote INTEGER DEFAULT 0;

-- Create index for remote filtering
CREATE INDEX idx_remote ON fast_search_index(is_remote);

-- Record migration
INSERT INTO schema_version (version) VALUES (3);
```

---

### Migration Runner

```python
def run_migrations() -> None:
    """Apply pending migrations"""
    current_version = get_current_schema_version()

    migration_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migration_dir.glob("*.sql"))

    for migration_file in migration_files:
        # Extract version from filename (e.g., "003_add_etag.sql" → 3)
        version = int(migration_file.stem.split("_")[0])

        if version > current_version:
            logger.info(f"Applying migration {version}: {migration_file.name}")

            with open(migration_file) as f:
                sql = f.read()

            cursor.executescript(sql)
            conn.commit()

            logger.info(f"Migration {version} applied successfully")
```

---

## Performance Optimization

### 1. Indexes

```sql
-- Existing indexes (automatically created)
CREATE INDEX idx_name ON fast_search_index(name);
CREATE INDEX idx_project ON fast_search_index(project);

-- Add custom indexes as needed
CREATE INDEX idx_format ON fast_search_index(format);
```

---

### 2. Query Optimization

```python
# ✅ GOOD: Use index for prefix search
SELECT name FROM fast_search_index WHERE name LIKE 'clim%';

# ❌ BAD: Full table scan (wildcard at start)
SELECT name FROM fast_search_index WHERE name LIKE '%data%';

# ✅ GOOD: Use FTS5 for full-text search
SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'data';
```

---

### 3. Transaction Batching

```python
# ✅ GOOD: Batch inserts in one transaction
def bulk_upsert(datasets: list[dict]) -> None:
    cursor.execute("BEGIN TRANSACTION")
    for dataset in datasets:
        upsert_dataset(dataset["id"], dataset)
    cursor.execute("COMMIT")

# ❌ BAD: Individual transactions (slow)
for dataset in datasets:
    upsert_dataset(dataset["id"], dataset)
    conn.commit()  # Commit each time
```

---

## Data Integrity

### Foreign Key Constraints

**Not used** - Tables are loosely coupled for flexibility

**Why?**
- `datasets_fts` and `fast_search_index` are derived from `datasets_store`
- Deletion handled manually in application code
- Allows partial rebuilds without constraint violations

---

### Data Validation

```python
from pydantic import BaseModel, field_validator

class DatasetMetadata(BaseModel):
    id: str
    dataset_name: str
    description: str
    # ... other fields

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        if "/" in v or "\\" in v:
            raise ValueError("ID cannot contain path separators")
        return v.strip()

# Usage
def save_dataset(metadata: dict) -> None:
    validated = DatasetMetadata.model_validate(metadata)
    upsert_dataset(validated.id, validated.to_dict())
```

---

## Backup and Recovery

### Manual Backup

```bash
# Backup database
cp ~/.local/share/mini-datahub/datasets.db ~/backups/datasets-$(date +%Y%m%d).db

# Restore from backup
cp ~/backups/datasets-20240115.db ~/.local/share/mini-datahub/datasets.db
```

---

### Rebuild Index

```python
def rebuild_search_index() -> None:
    """Rebuild FTS5 and fast_search_index from datasets_store"""
    # Clear existing indexes
    cursor.execute("DELETE FROM datasets_fts")
    cursor.execute("DELETE FROM fast_search_index")

    # Rebuild from datasets_store
    for dataset in list_all_datasets():
        update_fts_index(dataset)
        update_fast_index(dataset)

    conn.commit()
    logger.info("Search indexes rebuilt successfully")
```

---

## Related Documentation

- **[Data Layer Overview](overview.md)** - Architecture overview
- **[Storage](storage.md)** - Storage mechanisms
- **[Indexing](indexing.md)** - FTS5 details
- **[Migrations](migrations.md)** - Migration guide

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
