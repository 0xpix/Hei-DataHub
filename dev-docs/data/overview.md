# Data Layer Overview

## Introduction

The **Data Layer** in Hei-DataHub manages how dataset metadata is stored, indexed, and accessed. It combines local SQLite storage with cloud WebDAV sync for a hybrid local-first architecture.

---

## Architecture

### Storage Architecture

```
┌──────────────────────────────────────────────────┐
│              Application Layer                   │
└───────────────────┬──────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌─────────▼────────┐
│  Local Storage │    │  Cloud Storage   │
│   (SQLite)     │◄──►│    (WebDAV)      │
└────────────────┘    └──────────────────┘
        │                       │
        │                       │
    ┌───▼───┐              ┌────▼────┐
    │ Index │              │  YAML   │
    │ (FTS5)│              │  Files  │
    └───────┘              └─────────┘
```

**Key Components:**

1. **Local SQLite Database**
   - Primary data store for active use
   - FTS5 full-text search index
   - Fast queries (<80ms)
   - Offline access

2. **Cloud WebDAV Storage**
   - Authoritative source of truth
   - YAML metadata files
   - Shared across devices
   - Versioned (by timestamp)

3. **Sync Manager**
   - Bidirectional synchronization
   - Conflict resolution (last-write-wins)
   - Background sync (every 5 minutes)
   - Outbox for failed uploads

---

## Data Flow

### Write Path (Create/Update Dataset)

```
User creates/edits dataset
         ↓
Validate metadata (Pydantic)
         ↓
Write to local SQLite
         ↓
Update FTS5 index
         ↓
Convert to YAML
         ↓
Upload to WebDAV (async)
         ↓
(If upload fails → Outbox)
```

**Code Example:**

```python
from mini_datahub.services.dataset_service import save_dataset

# User provides metadata
metadata = {
    "id": "climate-data",
    "dataset_name": "Climate Model Data",
    "description": "Historical climate outputs",
    # ... other fields
}

# Save (local + cloud)
save_dataset(metadata)
# 1. Validates metadata
# 2. Writes to SQLite
# 3. Updates FTS5 index
# 4. Uploads YAML to WebDAV
```

---

### Read Path (Search/Retrieve)

```
User searches for datasets
         ↓
Query local FTS5 index
         ↓
Return results (from SQLite)
         ↓
(No network access needed)
```

**Code Example:**

```python
from mini_datahub.services.fast_search import search_indexed

# Search (local only, fast)
results = search_indexed("climate")
# Returns results in <80ms
# No network dependency
```

---

### Sync Path (Background Sync)

```
Timer triggers sync (every 5 min)
         ↓
List remote files (WebDAV PROPFIND)
         ↓
Compare timestamps
         ↓
Download newer remote files
         ↓
Upload newer local files
         ↓
Update local index
```

**Code Example:**

```python
from mini_datahub.services.sync import sync_now

# Manual sync trigger
result = sync_now()
print(f"Downloaded: {result.downloads}")
print(f"Uploaded: {result.uploads}")
```

---

## Storage Formats

### Local Storage (SQLite)

#### Database Schema

```sql
-- Dataset store (JSON payloads)
CREATE TABLE datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,  -- Complete JSON metadata
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- FTS5 search index
CREATE VIRTUAL TABLE datasets_fts USING fts5(
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
CREATE TABLE fast_search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    project TEXT,
    tags TEXT,
    description TEXT,
    format TEXT,
    is_remote INTEGER DEFAULT 0
);
```

**Why Three Tables?**

1. **datasets_store**: Complete metadata storage (JSON blob)
   - Preserves all fields
   - Easy to extend schema
   - Single source of truth locally

2. **datasets_fts**: Full-text search (FTS5 virtual table)
   - Optimized for search queries
   - BM25 ranking algorithm
   - Porter stemming for better matches

3. **fast_search_index**: Autocomplete & quick lookups
   - Denormalized for speed
   - Project/tag filtering
   - Remote vs local tracking

---

### Cloud Storage (WebDAV)

#### Directory Structure

```
/research-datasets/          # Library root
├── datasets/                # Dataset metadata
│   ├── climate-data/
│   │   └── metadata.yaml
│   ├── ocean-temp/
│   │   └── metadata.yaml
│   └── research-notes/
│       └── metadata.yaml
```

#### YAML Format

```yaml
# datasets/climate-data/metadata.yaml
id: climate-data
dataset_name: Climate Model Data
description: |
  Historical climate model outputs from CMIP6.
  Includes temperature, precipitation, and wind data.
source: https://esgf-node.llnl.gov/
date_created: '2024-01-15'
storage_location: /data/climate/cmip6
file_format: NetCDF
used_in_projects:
  - climate-study
  - future-projections
data_types:
  - time-series
  - geospatial
keywords:
  - climate
  - temperature
  - precipitation
access_level: public
```

**Why YAML for Cloud?**
- ✅ Human-readable and editable
- ✅ Git-friendly (diffs, merges)
- ✅ Supports multi-line strings
- ✅ Standard format in research
- ✅ Easy to share and version

**Why JSON for Local?**
- ✅ Faster parsing (native SQLite)
- ✅ More compact storage
- ✅ No schema ambiguity
- ✅ Direct serialization from Python

---

## Data Operations

### Create

```python
def create_dataset(metadata: dict) -> None:
    """Create new dataset"""
    # 1. Validate
    validated = DatasetMetadata.model_validate(metadata)

    # 2. Store locally
    upsert_dataset(validated.id, validated.to_dict())

    # 3. Upload to cloud
    yaml_content = yaml.dump(validated.to_dict())
    webdav_storage.write_file(
        f"datasets/{validated.id}/metadata.yaml",
        yaml_content
    )
```

### Read

```python
def get_dataset(dataset_id: str) -> dict | None:
    """Get dataset by ID (from local cache)"""
    return read_dataset_from_store(dataset_id)
```

### Update

```python
def update_dataset(dataset_id: str, metadata: dict) -> None:
    """Update existing dataset"""
    # Same as create (upsert)
    create_dataset(metadata)
```

### Delete

```python
def delete_dataset(dataset_id: str) -> None:
    """Delete dataset (local + cloud)"""
    # 1. Delete from local index
    delete_from_index(dataset_id)

    # 2. Delete from cloud
    webdav_storage.delete_file(f"datasets/{dataset_id}/metadata.yaml")
```

---

## Indexing

### Full-Text Search (FTS5)

**Features:**
- **BM25 Ranking:** Relevance-based result ordering
- **Porter Stemming:** Matches variations (e.g., "running" → "run")
- **Phrase Matching:** Exact phrase queries with quotes
- **Boolean Operators:** AND, OR, NOT support

**Query Examples:**

```sql
-- Simple search
SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'climate';

-- Phrase search
SELECT * FROM datasets_fts WHERE datasets_fts MATCH '"climate model"';

-- Boolean search
SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'climate AND temperature';

-- Field-specific search
SELECT * FROM datasets_fts WHERE name MATCH 'climate';

-- With ranking
SELECT id, name, rank
FROM datasets_fts
WHERE datasets_fts MATCH 'climate'
ORDER BY rank
LIMIT 50;
```

---

### Autocomplete Index

**Purpose:** Fast prefix matching for autocomplete suggestions

**Structure:**

```sql
CREATE TABLE fast_search_index (
    path TEXT PRIMARY KEY,      -- Dataset ID
    name TEXT NOT NULL,         -- Dataset name
    project TEXT,               -- Primary project
    tags TEXT,                  -- Space-separated tags
    description TEXT            -- Brief description
);

-- Index for fast prefix search
CREATE INDEX idx_name ON fast_search_index(name);
CREATE INDEX idx_project ON fast_search_index(project);
```

**Query Example:**

```sql
-- Autocomplete on name
SELECT name FROM fast_search_index
WHERE name LIKE 'clim%'
LIMIT 10;

-- Autocomplete on project
SELECT DISTINCT project FROM fast_search_index
WHERE project LIKE 'res%';
```

---

## Synchronization

### Sync Algorithm

```python
def sync_now() -> SyncResult:
    """Bidirectional sync"""
    # 1. List remote files
    remote_files = webdav_storage.list_remote_files()

    # 2. List local files
    local_files = list_all_datasets_from_index()

    # 3. Build file maps
    remote_map = {f["path"]: f["mtime"] for f in remote_files}
    local_map = {f["id"]: f["updated_at"] for f in local_files}

    # 4. Sync logic
    downloads = 0
    uploads = 0

    for dataset_id in set(remote_map.keys()) | set(local_map.keys()):
        remote_time = remote_map.get(dataset_id)
        local_time = local_map.get(dataset_id)

        if remote_time and not local_time:
            # Only on remote → Download
            download_dataset(dataset_id)
            downloads += 1

        elif local_time and not remote_time:
            # Only local → Upload
            upload_dataset(dataset_id)
            uploads += 1

        elif remote_time > local_time:
            # Remote newer → Download
            download_dataset(dataset_id)
            downloads += 1

        elif local_time > remote_time:
            # Local newer → Upload
            upload_dataset(dataset_id)
            uploads += 1

    return SyncResult(downloads=downloads, uploads=uploads)
```

---

### Conflict Resolution

**Strategy:** Last-write-wins (timestamp-based)

**Example:**

```
Device A: Edit dataset at 14:30
Device B: Edit dataset at 14:35

Sync:
  Device A downloads (remote 14:35 > local 14:30)
  Device B uploads (local 14:35 > remote 14:30)

Result: Device B's changes win
```

**Limitations:**
- ⚠️ Concurrent edits may lose changes
- ⚠️ No automatic merge of conflicting changes
- ⚠️ No conflict detection UI (yet)

**Future Improvements:**
- Detect conflicts based on content hash
- Prompt user for resolution
- Support manual merge

---

## Data Migrations

### Schema Evolution

**Version tracking:**

```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);
```

**Migration example:**

```sql
-- migrations/003_add_etag_field.sql
ALTER TABLE fast_search_index ADD COLUMN etag TEXT;
ALTER TABLE fast_search_index ADD COLUMN is_remote INTEGER DEFAULT 0;

INSERT INTO schema_version (version) VALUES (3);
```

**Migration runner:**

```python
def run_migrations() -> None:
    """Apply pending migrations"""
    current_version = get_current_schema_version()

    for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = extract_version_from_filename(migration_file)

        if version > current_version:
            execute_migration(migration_file)
            logger.info(f"Applied migration {version}")
```

---

## Performance Characteristics

### Query Performance

| Operation | Target | Typical | Notes |
|-----------|--------|---------|-------|
| Simple search | <80ms | 50-80ms | FTS5 with <10,000 datasets |
| Autocomplete | <50ms | 20-40ms | Prefix matching on indexed column |
| Get by ID | <10ms | 5-10ms | Primary key lookup |
| List all | <100ms | 50-100ms | 1,000 datasets |
| Upsert | <20ms | 10-20ms | Single transaction |

### Storage Size

| Component | Size per Dataset | Notes |
|-----------|------------------|-------|
| JSON payload | ~2 KB | Complete metadata |
| FTS5 index entry | ~1 KB | Searchable fields only |
| Fast index entry | ~500 bytes | Denormalized fields |
| YAML file (cloud) | ~2 KB | Human-readable format |

**Example:** 10,000 datasets ≈ 35 MB total storage

---

## Best Practices

### 1. Use Local Index for Reads

```python
# ✅ GOOD: Fast local search
results = search_indexed("climate")

# ❌ BAD: Slow remote list + filter
files = webdav_storage.list_remote_files()
results = [f for f in files if "climate" in f["name"]]
```

### 2. Batch Operations

```python
# ✅ GOOD: Bulk upsert
for dataset in datasets:
    upsert_dataset(dataset["id"], dataset)
commit()

# ❌ BAD: Individual commits
for dataset in datasets:
    upsert_dataset(dataset["id"], dataset)
    commit()  # Slow!
```

### 3. Let Sync Handle Cloud Updates

```python
# ✅ GOOD: Save locally, let background sync upload
save_dataset(metadata)  # Immediate local save
# Sync uploads in background

# ❌ BAD: Blocking on upload
save_dataset_and_wait_for_upload(metadata)  # Slow!
```

---

## Related Documentation

- **[Storage Architecture](storage.md)** - Detailed storage design
- **[Schema](schema.md)** - Database schema reference
- **[Indexing](indexing.md)** - FTS5 and autocomplete details
- **[Migrations](migrations.md)** - Schema migration guide

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
