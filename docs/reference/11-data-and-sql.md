# Data & SQL Reference

**(req. Hei-DataHub 0.59-beta or later)**

## Data Storage Architecture

Hei-DataHub v0.59-beta uses a **cloud-first storage model**:

1. **Heibox/WebDAV Cloud Storage** — Source of truth for dataset YAML files (team-shared)
2. **Local SQLite Index** — Cached search index for fast queries (user-specific)

```
┌─────────────────────────────────────────────────┐
│  Heibox Cloud Storage (WebDAV)                  │  ← Source of Truth
│  - YAML files stored in Seafile library         │
│  - Shared across team via cloud                 │
│  - Accessed via HTTPS (encrypted in transit)    │
└─────────────────────────────────────────────────┘
              ↓ (synced & indexed)
┌─────────────────────────────────────────────────┐
│  Local SQLite Index (~/.cache/hei-datahub/)     │  ← Search Cache
│  - FTS5 full-text search                        │
│  - BM25 ranking algorithm                       │
│  - Background sync every 15 minutes             │
│  - Fast queries (<80ms average)                 │
└─────────────────────────────────────────────────┘
```

**Key differences from v0.58 and earlier:**

❌ **No local YAML files** - Datasets are NOT stored in `data/` directory
❌ **No Git workflow** - No PRs, branches, or local Git repository needed
✅ **Cloud-only storage** - All datasets live in Heibox (Seafile)
✅ **Instant team sync** - Changes visible immediately to all team members
✅ **Local index only** - SQLite database is just a search cache

---

## Database Schema

Hei-DataHub uses **two tables** in SQLite:

### 1. `datasets_store` (Main Table)

Stores complete dataset metadata as JSON.

```sql
CREATE TABLE IF NOT EXISTS datasets_store (
    id TEXT PRIMARY KEY,                 -- Dataset ID (slug)
    payload TEXT NOT NULL,               -- Full metadata as JSON
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Fields:**

- **id:** Primary key, matches YAML filename (e.g., `weather-q1`)
- **payload:** JSON string containing all metadata fields
- **created_at:** Timestamp when first indexed
- **updated_at:** Timestamp of last update

**Trigger:**

```sql
CREATE TRIGGER IF NOT EXISTS update_datasets_store_timestamp
AFTER UPDATE ON datasets_store
FOR EACH ROW
BEGIN
    UPDATE datasets_store SET updated_at = datetime('now') WHERE id = OLD.id;
END;
```

Automatically updates `updated_at` on every modification.

---

### 2. `datasets_fts` (FTS5 Virtual Table)

Full-text search index with prefix matching.

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts USING fts5(
    id UNINDEXED,                        -- Dataset ID (not searchable)
    name,                                -- Dataset name (searchable)
    description,                         -- Description (searchable)
    used_in_projects,                    -- Projects list (searchable)
    data_types,                          -- Data types list (searchable)
    source,                              -- Source URL/snippet (searchable)
    file_format,                         -- File format (searchable)
    tokenize = 'porter unicode61',       -- Porter stemming + Unicode
    prefix = '2 3 4'                     -- Prefix matching for 2-4 chars
);
```

**Fields:**

- **id:** Dataset ID (UNINDEXED—not included in search)
- **name, description, source, file_format:** Single-value text fields
- **used_in_projects, data_types:** Multi-value fields (joined with spaces)

**Tokenization:**

- **Porter stemming:** "running" matches "run", "runs"
- **Unicode61:** Full Unicode support (accents, non-Latin scripts)

**Prefix matching:**

- **2-char:** "cl" matches "climate", "cloud"
- **3-char:** "cli" matches "climate"
- **4-char:** "clim" matches "climate"

---

## Data Location

In **v0.59-beta**, datasets are stored in **Heibox cloud storage only**:

```
Heibox Library (cloud)       ← Source of Truth
├── weather-q1.yaml          ← Dataset files stored in Seafile
├── burned-area.yaml
├── climate-model.yaml
└── ...

~/.cache/hei-datahub/        ← Local cache (user-specific)
├── index.db                 ← SQLite search index
└── ...
```

**Important notes:**

❌ **No `data/` directory** - Datasets are NOT stored locally
✅ **Cloud-first** - YAML files live in Heibox (accessed via WebDAV)
✅ **SQLite is cache** - Local index rebuilds from cloud if cleared
✅ **Background sync** - Index updates every 15 minutes automatically

**Configuration required:**

```bash
# Set up WebDAV credentials
hei-datahub auth setup
```

See [Configure Heibox Integration](../how-to/04-settings.md) for details.

---

## Field Conventions

### Required Fields (Schema Enforced)

These must be present in every dataset YAML file:

| Field | Type | Constraint | Example |
|-------|------|------------|---------|
| `id` | String | Lowercase, alphanumeric + `_-` | `weather-q1` |
| `dataset_name` | String | 1-200 chars | `Weather Q1 Data` |
| `description` | String | Min 1 char | `Quarterly weather...` |
| `source` | String | Min 1 char | `https://...` |
| `date_created` | Date | ISO 8601 (`YYYY-MM-DD`) | `2024-10-04` |
| `storage_location` | String | Min 1 char | `s3://bucket/path` |

### Optional Fields

| Field | Type | Notes |
|-------|------|-------|
| `file_format` | String | E.g., "CSV", "GeoTIFF" |
| `size` | String | Human-readable, e.g., "2.5 GB" |
| `data_types` | List[String] | Descriptions of data types |
| `used_in_projects` | List[String] | Project names |

---

## Query Patterns

### Search Query

**Service:** `hei_datahub.services.search.search_datasets(query, limit)`

**SQL:**

```sql
SELECT
    store.id,
    store.payload,
    snippet(fts, 2, '<b>', '</b>', '...', 64) AS snippet,
    bm25(fts) AS score
FROM datasets_fts AS fts
JOIN datasets_store AS store ON fts.id = store.id
WHERE fts MATCH :query
ORDER BY score
LIMIT :limit;
```

**How it works:**

1. **MATCH clause:** FTS5 searches indexed fields for query terms
2. **BM25 scoring:** Ranks results by relevance
3. **Snippet generation:** Extracts context around matched terms (max 64 chars)
4. **JOIN:** Fetches full payload from `datasets_store`

**Performance:**

- **< 10ms** for typical queries (tested with 1000+ datasets)
- **Prefix matching:** Speeds up "as-you-type" search

---

### Get Dataset by ID

**Service:** `hei_datahub.infra.index.get_dataset_from_store(dataset_id)`

**SQL:**

```sql
SELECT payload
FROM datasets_store
WHERE id = :dataset_id;
```

**Performance:**

- **< 5ms** (primary key lookup)
- Returns full JSON payload

---

### List All Datasets

**Service:** `hei_datahub.infra.index.list_all_datasets()`

**SQL:**

```sql
SELECT
    store.id,
    store.payload,
    fts.name,
    snippet(fts, 2, '<b>', '</b>', '...', 64) AS snippet
FROM datasets_store AS store
JOIN datasets_fts AS fts ON store.id = fts.id
ORDER BY store.updated_at DESC;
```

**Performance:**

- **< 50ms** for 1000 datasets
- Sorted by most recently updated

---

### Upsert Dataset

**Service:** `hei_datahub.infra.index.upsert_dataset(dataset_id, metadata)`

**SQL:**

```sql
-- Step 1: Insert or replace in store
INSERT OR REPLACE INTO datasets_store (id, payload, created_at, updated_at)
VALUES (:id, :payload, COALESCE((SELECT created_at FROM datasets_store WHERE id = :id), datetime('now')), datetime('now'));

-- Step 2: Delete old FTS entry
DELETE FROM datasets_fts WHERE id = :id;

-- Step 3: Insert new FTS entry
INSERT INTO datasets_fts (id, name, description, used_in_projects, data_types, source, file_format)
VALUES (:id, :name, :description, :projects, :types, :source, :format);
```

**Performance:**

- **< 20ms** per dataset
- Preserves `created_at` on updates

---

## Performance Tips

### Dataset Details Load

Opening the Details Screen triggers a **single query** to `datasets_store`:

```python
payload = get_dataset_from_store(dataset_id)
```

**Optimization:**

- Uses primary key lookup (very fast)
- No joins or full-table scans
- JSON parsing handled by Python (negligible overhead)

**Benchmark:**

- **1000 datasets:** < 5ms
- **10,000 datasets:** < 10ms

---

### Search Debouncing

TUI implements **150ms debounce** on search input to avoid excessive queries while typing.

**Why?**

- Reduces query load
- Smoother UX (no flickering)
- Gives time for user to finish typing

---

### Reindexing

Running `hei-datahub reindex` rebuilds the entire search index:

1. Read all `metadata.yaml` files from `data/`
2. Validate each against JSON Schema
3. Upsert into SQLite (store + FTS5)

**Performance:**

- **100 datasets:** ~2 seconds
- **1000 datasets:** ~20 seconds

**When to reindex:**

- After manual YAML edits
- After pulling changes from Git
- If search results seem stale

---

## Safe Query Patterns

### Avoid Direct SQL in App Code

**❌ Bad:**

```python
import sqlite3
conn = sqlite3.connect("db.sqlite")
cursor = conn.execute("SELECT * FROM datasets_store")
```

**✅ Good:**

```python
from hei_datahub.services.search import search_datasets
results = search_datasets("climate", limit=50)
```

**Why?**

- Services abstract SQL complexity
- Easier to test and maintain
- Consistent error handling

---

### Use Parameterized Queries

If you must write SQL, **always** use parameterized queries:

**❌ Bad (SQL Injection Risk):**

```python
query = f"SELECT * FROM datasets_store WHERE id = '{user_input}'"
```

**✅ Good:**

```python
query = "SELECT * FROM datasets_store WHERE id = ?"
cursor.execute(query, (user_input,))
```

---

### Validate Before Inserting

Always validate metadata before inserting:

```python
from hei_datahub.infra.store import validate_metadata

# Validate against JSON Schema
is_valid, errors = validate_metadata(metadata_dict)
if not is_valid:
    raise ValueError(f"Invalid metadata: {errors}")

# Then upsert
upsert_dataset(dataset_id, metadata_dict)
```

---

## Database Maintenance

### Rebuild Index

If the database is corrupted or out of sync:

```bash
# Delete database
rm db.sqlite

# Reindex from YAML files
hei-datahub reindex
```

---

### Check Database Size

```bash
ls -lh db.sqlite
```

**Typical sizes:**

- **100 datasets:** ~500 KB
- **1000 datasets:** ~5 MB
- **10,000 datasets:** ~50 MB

---

### Optimize FTS5 Index

SQLite FTS5 supports optimization:

```sql
INSERT INTO datasets_fts(datasets_fts) VALUES('optimize');
```

**When to run:**

- After bulk inserts (e.g., reindexing)
- If search queries slow down

**How to run:**

```python
import sqlite3
from hei_datahub.infra.paths import DB_PATH

conn = sqlite3.connect(DB_PATH)
conn.execute("INSERT INTO datasets_fts(datasets_fts) VALUES('optimize')")
conn.commit()
conn.close()
```

---

## Backup & Restore

### Backup

```bash
# Copy database
cp db.sqlite db.sqlite.backup

# Or use SQLite .backup command
sqlite3 db.sqlite ".backup db.sqlite.backup"
```

---

### Restore

```bash
# Restore from backup
cp db.sqlite.backup db.sqlite

# Or reindex from YAML (if YAML files are source of truth)
hei-datahub reindex
```

---

## Future Enhancements

Planned for post-v0.55.x:

- **Separate data repo:** Configure external `data/` directory
- **Dataset history:** Track changes over time
- **Field-specific search:** E.g., `source:github.com`
- **Advanced filters:** Date ranges, size ranges, etc.
- **Export/import:** Bulk export to JSON/CSV

---

## Next Steps

- **[Configuration](12-config.md)** — Configure database paths and settings
- **[FAQ](../help/90-faq.md)** — Troubleshooting database issues
- **[Getting Started](../getting-started/01-getting-started.md)** — Installation and setup
