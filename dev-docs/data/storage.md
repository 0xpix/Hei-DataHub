# Storage Architecture

## Introduction

Hei-DataHub uses a **hybrid local-first storage architecture** combining local SQLite with cloud WebDAV sync. This provides offline access, fast queries, and cross-device synchronization.

---

## Storage Components

### 1. Local Storage (SQLite)

**Location:** `~/.local/share/mini-datahub/datasets.db`

**Purpose:**
- Primary operational data store
- Fast local queries
- Offline access
- FTS5 full-text search

**Schema:**

```sql
-- Main dataset store
CREATE TABLE datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,  -- JSON metadata
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Search index
CREATE VIRTUAL TABLE datasets_fts USING fts5(
    id, name, description, used_in_projects,
    data_types, source, file_format,
    tokenize = 'porter ascii'
);

-- Autocomplete index
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
```

---

### 2. Cloud Storage (WebDAV)

**Protocol:** WebDAV over HTTPS
**Providers:** HeiBox (ownCloud), Seafile
**Format:** YAML metadata files

**Directory Structure:**

```
/research-datasets/          # Library root (configurable)
├── datasets/                # Dataset metadata directory
│   ├── climate-data/
│   │   └── metadata.yaml    # Dataset metadata
│   ├── ocean-temp/
│   │   └── metadata.yaml
│   └── research-notes/
│       └── metadata.yaml
└── .hei-datahub/            # Internal tracking (planned)
    └── sync-state.json
```

**Why WebDAV?**
- ✅ Standard protocol (RFC 4918)
- ✅ University cloud support (HeiBox, Seafile)
- ✅ Simple HTTP-based API
- ✅ Versioning support (server-side)
- ✅ Folder sharing for collaboration

---

### 3. Outbox (Failed Uploads)

**Location:** `~/.local/share/mini-datahub/outbox/`

**Purpose:** Queue datasets that failed to upload during sync

**Structure:**

```
outbox/
├── climate-data.yaml        # Failed upload
└── ocean-temp.yaml          # Failed upload
```

**Behavior:**
- Failed uploads saved to outbox
- Retry on next successful connection
- Preserves data during network outages
- Automatic cleanup after successful upload

---

## Storage Operations

### Write Operations

#### 1. Create/Update Dataset

```python
def save_dataset(metadata: dict) -> None:
    """Save dataset (local + cloud)"""
    # 1. Validate
    validated = DatasetMetadata.model_validate(metadata)

    # 2. Write to local SQLite
    upsert_dataset(validated.id, validated.to_dict())

    # 3. Update FTS5 index
    update_fts_index(validated)

    # 4. Update fast search index
    update_fast_index(validated)

    # 5. Upload to WebDAV (async)
    try:
        upload_to_cloud(validated)
    except WebDAVError as e:
        # Save to outbox for retry
        save_to_outbox(validated)
        logger.warning(f"Upload failed, saved to outbox: {e}")
```

**Transaction Safety:**

```python
def upsert_dataset(dataset_id: str, payload: dict) -> None:
    """Atomic upsert with rollback"""
    with db_transaction():
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
```

---

#### 2. Delete Dataset

```python
def delete_dataset(dataset_id: str) -> None:
    """Delete dataset (local + cloud)"""
    # 1. Delete from local index
    delete_from_index(dataset_id)

    # 2. Delete from FTS5
    delete_from_fts(dataset_id)

    # 3. Delete from fast index
    delete_from_fast_index(dataset_id)

    # 4. Delete from cloud
    webdav_storage.delete_file(f"datasets/{dataset_id}/metadata.yaml")
```

---

### Read Operations

#### 1. Get by ID

```python
def get_dataset(dataset_id: str) -> dict | None:
    """Get dataset by ID (local only)"""
    cursor.execute(
        "SELECT payload FROM datasets_store WHERE id = ?",
        (dataset_id,)
    )
    row = cursor.fetchone()
    return json.loads(row[0]) if row else None
```

**Performance:** ~5-10ms (primary key lookup)

---

#### 2. Search (FTS5)

```python
def search_indexed(query: str) -> list[dict]:
    """Full-text search"""
    cursor.execute(
        """
        SELECT id, name, description, rank
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        ORDER BY rank
        LIMIT 50
        """,
        (query,)
    )
    return cursor.fetchall()
```

**Performance:** ~50-80ms for <10,000 datasets

---

#### 3. Autocomplete

```python
def autocomplete_suggestions(prefix: str) -> list[str]:
    """Autocomplete dataset names"""
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
```

**Performance:** ~20-40ms

---

## WebDAV Operations

### Authentication

```python
from mini_datahub.infra.auth import get_webdav_credentials

# Get credentials from keyring
creds = get_webdav_credentials()
# Returns: {"username": "...", "password": "...", "url": "..."}
```

**Security:**
- ✅ Stored in Linux Secret Service (encrypted)
- ✅ Never logged or printed
- ✅ HTTPS-only connections
- ✅ Password never in config files

---

### File Operations

#### Upload File

```python
from mini_datahub.services.webdav_storage import write_file

def upload_dataset(dataset_id: str, metadata: dict) -> None:
    """Upload metadata to WebDAV"""
    yaml_content = yaml.dump(metadata)
    remote_path = f"datasets/{dataset_id}/metadata.yaml"

    write_file(remote_path, yaml_content)
```

**HTTP Request:**

```http
PUT /research-datasets/datasets/climate-data/metadata.yaml HTTP/1.1
Host: heibox.uni-heidelberg.de
Authorization: Basic <base64-credentials>
Content-Type: text/plain

id: climate-data
dataset_name: Climate Model Data
...
```

---

#### Download File

```python
from mini_datahub.services.webdav_storage import read_file

def download_dataset(dataset_id: str) -> dict:
    """Download metadata from WebDAV"""
    remote_path = f"datasets/{dataset_id}/metadata.yaml"
    yaml_content = read_file(remote_path)
    return yaml.safe_load(yaml_content)
```

**HTTP Request:**

```http
GET /research-datasets/datasets/climate-data/metadata.yaml HTTP/1.1
Host: heibox.uni-heidelberg.de
Authorization: Basic <base64-credentials>
```

---

#### List Files

```python
from mini_datahub.services.webdav_storage import list_remote_files

def list_datasets() -> list[dict]:
    """List all datasets on cloud"""
    files = list_remote_files(path="datasets/", recursive=True)
    # Returns: [{"path": "...", "mtime": "...", "size": ...}, ...]
    return [f for f in files if f["path"].endswith("metadata.yaml")]
```

**HTTP Request (PROPFIND):**

```http
PROPFIND /research-datasets/datasets/ HTTP/1.1
Host: heibox.uni-heidelberg.de
Authorization: Basic <base64-credentials>
Depth: infinity
Content-Type: application/xml

<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:displayname/>
    <d:getlastmodified/>
    <d:getcontentlength/>
  </d:prop>
</d:propfind>
```

---

#### Delete File

```python
from mini_datahub.services.webdav_storage import delete_file

def delete_cloud_dataset(dataset_id: str) -> None:
    """Delete dataset from cloud"""
    remote_path = f"datasets/{dataset_id}/metadata.yaml"
    delete_file(remote_path)
```

**HTTP Request:**

```http
DELETE /research-datasets/datasets/climate-data/metadata.yaml HTTP/1.1
Host: heibox.uni-heidelberg.de
Authorization: Basic <base64-credentials>
```

---

## Synchronization

### Sync Strategy

**Local-First with Background Sync:**

1. **Writes:** Save locally first (instant), upload asynchronously
2. **Reads:** Always from local index (no network delay)
3. **Sync:** Background task every 5 minutes
4. **Conflicts:** Last-write-wins (timestamp-based)

---

### Sync Algorithm

```python
def sync_now() -> SyncResult:
    """Bidirectional sync"""
    # 1. List remote files
    remote_files = list_remote_files(path="datasets/", recursive=True)
    remote_map = {
        extract_dataset_id(f["path"]): f["mtime"]
        for f in remote_files
        if f["path"].endswith("metadata.yaml")
    }

    # 2. List local files
    local_datasets = list_all_datasets_from_index()
    local_map = {
        d["id"]: d["updated_at"]
        for d in local_datasets
    }

    # 3. Determine actions
    to_download = []
    to_upload = []

    all_ids = set(remote_map.keys()) | set(local_map.keys())

    for dataset_id in all_ids:
        remote_time = remote_map.get(dataset_id)
        local_time = local_map.get(dataset_id)

        if remote_time and not local_time:
            to_download.append(dataset_id)
        elif local_time and not remote_time:
            to_upload.append(dataset_id)
        elif remote_time > local_time:
            to_download.append(dataset_id)
        elif local_time > remote_time:
            to_upload.append(dataset_id)

    # 4. Execute downloads
    for dataset_id in to_download:
        download_and_index(dataset_id)

    # 5. Execute uploads
    for dataset_id in to_upload:
        upload_dataset(dataset_id)

    # 6. Retry outbox
    retry_outbox_uploads()

    return SyncResult(
        downloads=len(to_download),
        uploads=len(to_upload)
    )
```

---

### Conflict Resolution

**Scenario:** Same dataset edited on two devices

```
Device A (Laptop):
  Edit "climate-data" at 14:30
  Local time: 2024-01-15 14:30:00

Device B (Desktop):
  Edit "climate-data" at 14:35
  Local time: 2024-01-15 14:35:00

Sync Sequence:
  1. Device B syncs first
     → Uploads (local 14:35 > remote 14:30)
     → Cloud now has 14:35 version

  2. Device A syncs later
     → Downloads (remote 14:35 > local 14:30)
     → Device A's changes overwritten

Result: Device B's changes preserved (last-write-wins)
```

**Trade-offs:**
- ✅ Simple algorithm
- ✅ No manual intervention needed
- ❌ Concurrent edits may lose changes
- ❌ No merge capability

**Future Enhancement:**
- Content hashing to detect conflicts
- Conflict resolution UI
- Manual merge support

---

## Data Formats

### Local Format (JSON in SQLite)

```json
{
  "id": "climate-data",
  "dataset_name": "Climate Model Data",
  "description": "Historical climate model outputs",
  "source": "https://esgf-node.llnl.gov/",
  "date_created": "2024-01-15",
  "storage_location": "/data/climate/cmip6",
  "file_format": "NetCDF",
  "used_in_projects": ["climate-study"],
  "data_types": ["time-series", "geospatial"],
  "keywords": ["climate", "temperature"],
  "access_level": "public",
  "contact_person": "jane.doe@uni-heidelberg.de"
}
```

**Advantages:**
- Fast parsing (native SQLite)
- Compact storage
- No schema ambiguity
- Direct Python serialization

---

### Cloud Format (YAML on WebDAV)

```yaml
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
contact_person: jane.doe@uni-heidelberg.de
```

**Advantages:**
- Human-readable
- Git-friendly (diffs, merges)
- Multi-line strings (descriptions)
- Standard in research workflows
- Easy to edit in file browser

---

## Performance Optimization

### 1. Connection Pooling

```python
class WebDAVStorage:
    def __init__(self):
        self._session = requests.Session()  # Reuse connections
        self._session.headers.update({
            "User-Agent": "Hei-DataHub/0.59.0"
        })
```

---

### 2. Batch Operations

```python
def bulk_download(dataset_ids: list[str]) -> None:
    """Download multiple datasets efficiently"""
    for dataset_id in dataset_ids:
        # Reuse connection from session pool
        download_dataset(dataset_id)
```

---

### 3. ETags for Caching

```python
def download_if_modified(dataset_id: str, local_etag: str) -> bool:
    """Only download if remote changed"""
    headers = {"If-None-Match": local_etag}
    response = session.get(remote_url, headers=headers)

    if response.status_code == 304:
        # Not modified, skip download
        return False

    # Download new content
    save_dataset(response.text)
    return True
```

---

## Error Handling

### Network Errors

```python
def safe_upload(dataset_id: str, metadata: dict) -> None:
    """Upload with error handling"""
    try:
        upload_to_cloud(dataset_id, metadata)
    except requests.ConnectionError:
        logger.warning("No network connection, saving to outbox")
        save_to_outbox(dataset_id, metadata)
    except requests.Timeout:
        logger.warning("Upload timeout, saving to outbox")
        save_to_outbox(dataset_id, metadata)
    except WebDAVError as e:
        logger.error(f"WebDAV error: {e}")
        save_to_outbox(dataset_id, metadata)
```

---

### Data Integrity

```python
def verify_sync_integrity() -> None:
    """Check local vs cloud consistency"""
    local_ids = {d["id"] for d in list_all_datasets_from_index()}
    remote_files = list_remote_files(path="datasets/", recursive=True)
    remote_ids = {extract_dataset_id(f["path"]) for f in remote_files}

    missing_local = remote_ids - local_ids
    missing_remote = local_ids - remote_ids

    if missing_local:
        logger.warning(f"Datasets only on cloud: {missing_local}")
    if missing_remote:
        logger.warning(f"Datasets only local: {missing_remote}")
```

---

## Security

### Transport Security

- ✅ **HTTPS Only:** All WebDAV connections over TLS
- ✅ **Certificate Validation:** Verify server certificates
- ✅ **No HTTP Fallback:** Reject insecure connections

```python
def validate_webdav_url(url: str) -> None:
    """Ensure HTTPS"""
    if not url.startswith("https://"):
        raise ValueError("WebDAV URL must use HTTPS")
```

---

### Credential Storage

- ✅ **Linux Keyring:** Secret Service API (encrypted)
- ✅ **No Plaintext:** Never stored in config files
- ✅ **No Logging:** Credentials never logged

```python
import keyring

# Store (encrypted)
keyring.set_password("hei-datahub", "webdav_password", password)

# Retrieve
password = keyring.get_password("hei-datahub", "webdav_password")
```

---

## Related Documentation

- **[Data Layer Overview](overview.md)** - Architecture overview
- **[Schema](schema.md)** - Database schema reference
- **[Indexing](indexing.md)** - FTS5 and autocomplete
- **[Migrations](migrations.md)** - Schema migrations

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
