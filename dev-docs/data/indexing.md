# Indexing

## Introduction

Hei-DataHub uses **SQLite FTS5** (Full-Text Search version 5) for fast, relevant search across dataset metadata. This document explains the indexing architecture, query capabilities, and performance characteristics.

---

## Index Architecture

### Two-Tier Indexing Strategy

```
┌──────────────────────────────────────┐
│        Application Layer             │
└───────────────┬──────────────────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼─────┐    ┌─────▼──────────┐
│   FTS5      │    │ Fast Search    │
│   Index     │    │ Index          │
│             │    │                │
│ • Full-text │    │ • Autocomplete │
│ • Ranking   │    │ • Prefix match │
│ • Stemming  │    │ • Tag filter   │
└─────────────┘    └────────────────┘
```

**1. FTS5 Index (`datasets_fts`)**
- Purpose: Full-text search with ranking
- Speed: 50-80ms for <10,000 datasets
- Features: BM25 ranking, stemming, phrase search

**2. Fast Search Index (`fast_search_index`)**
- Purpose: Autocomplete and quick lookups
- Speed: 20-40ms
- Features: Prefix matching, tag filtering, project filtering

---

## FTS5 Index

### Schema

```sql
CREATE VIRTUAL TABLE datasets_fts USING fts5(
    id UNINDEXED,           -- Dataset ID (not searchable)
    name,                   -- Dataset name (searchable)
    description,            -- Description (searchable)
    used_in_projects,       -- Projects (searchable)
    data_types,             -- Data types (searchable)
    source,                 -- Source URL (searchable)
    file_format,            -- File format (searchable)
    tokenize = 'porter ascii'
);
```

**Column Configuration:**
- **`id UNINDEXED`:** Not searchable (used for result retrieval only)
- All other columns: Searchable and ranked

**Tokenizer:** `porter ascii`
- **`porter`:** Porter stemming algorithm
  - "running" → "run"
  - "climates" → "climat"
  - Matches word variations automatically
- **`ascii`:** ASCII case-folding
  - "Climate" → "climate"
  - Unicode normalization

---

### Indexing Operations

#### Add/Update Document

```python
def update_fts_index(dataset: dict) -> None:
    """Add or update dataset in FTS5 index"""
    cursor.execute(
        """
        INSERT INTO datasets_fts (id, name, description, used_in_projects, data_types, source, file_format)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            description = excluded.description,
            used_in_projects = excluded.used_in_projects,
            data_types = excluded.data_types,
            source = excluded.source,
            file_format = excluded.file_format
        """,
        (
            dataset["id"],
            dataset["dataset_name"],
            dataset.get("description", ""),
            " ".join(dataset.get("used_in_projects", [])),
            " ".join(dataset.get("data_types", [])),
            dataset.get("source", ""),
            dataset.get("file_format", "")
        )
    )
    conn.commit()
```

**Multi-value fields** (lists) are joined with spaces:
```python
used_in_projects = ["climate-study", "future-projections"]
# Indexed as: "climate-study future-projections"
```

---

#### Delete Document

```python
def delete_from_fts(dataset_id: str) -> None:
    """Remove dataset from FTS5 index"""
    cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))
    conn.commit()
```

---

#### Rebuild Index

```python
def rebuild_fts_index() -> None:
    """Rebuild entire FTS5 index"""
    # 1. Clear existing index
    cursor.execute("DELETE FROM datasets_fts")

    # 2. Rebuild from datasets_store
    cursor.execute("SELECT id, payload FROM datasets_store")
    for row in cursor.fetchall():
        dataset = json.loads(row[1])
        update_fts_index(dataset)

    conn.commit()
    logger.info("FTS5 index rebuilt successfully")
```

---

### Search Queries

#### Simple Search

```python
def search_simple(query: str) -> list[dict]:
    """Simple full-text search"""
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
    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "rank": row[3]
        }
        for row in cursor.fetchall()
    ]
```

**Example:**

```python
results = search_simple("climate")
# Matches: "climate", "climates", "climatic" (stemmed)
```

---

#### Phrase Search

```python
def search_phrase(phrase: str) -> list[dict]:
    """Exact phrase matching"""
    cursor.execute(
        """
        SELECT id, name
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        """,
        (f'"{phrase}"',)  # Wrap in quotes
    )
    return cursor.fetchall()
```

**Example:**

```python
results = search_phrase("climate model")
# Matches: "climate model" (exact phrase only)
# Does NOT match: "model climate" or "climate data model"
```

---

#### Boolean Search

```python
def search_boolean(query: str) -> list[dict]:
    """Boolean operators (AND, OR, NOT)"""
    cursor.execute(
        """
        SELECT id, name
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        """,
        (query,)
    )
    return cursor.fetchall()
```

**Examples:**

```python
# AND (both terms required)
search_boolean("climate AND temperature")

# OR (either term)
search_boolean("climate OR ocean")

# NOT (exclude term)
search_boolean("climate NOT temperature")

# Complex query
search_boolean("(climate OR ocean) AND temperature NOT precipitation")
```

---

#### Field-Specific Search

```python
def search_in_field(field: str, query: str) -> list[dict]:
    """Search in specific field"""
    cursor.execute(
        f"""
        SELECT id, name
        FROM datasets_fts
        WHERE {field} MATCH ?
        """,
        (query,)
    )
    return cursor.fetchall()
```

**Examples:**

```python
# Search in name only
search_in_field("name", "climate")

# Search in description only
search_in_field("description", "temperature")

# Search in projects
search_in_field("used_in_projects", "climate-study")
```

---

#### Prefix Search (FTS5)

```python
def search_prefix(prefix: str) -> list[dict]:
    """Prefix matching with FTS5"""
    cursor.execute(
        """
        SELECT id, name
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        """,
        (f"{prefix}*",)  # Asterisk for prefix
    )
    return cursor.fetchall()
```

**Example:**

```python
search_prefix("clim")
# Matches: "climate", "climatic", "climates"
```

---

### Ranking (BM25)

FTS5 uses **BM25 (Best Matching 25)** algorithm for relevance ranking.

**Ranking Factors:**
1. **Term Frequency (TF):** How often query term appears in document
2. **Inverse Document Frequency (IDF):** Rarity of term across all documents
3. **Document Length:** Shorter documents get boosted
4. **Field Boost:** (Not configurable in FTS5)

**Query with Ranking:**

```sql
SELECT id, name, rank
FROM datasets_fts
WHERE datasets_fts MATCH 'climate'
ORDER BY rank  -- Lower rank = better match
LIMIT 50;
```

**Rank Values:**
- Negative numbers (e.g., -5.2, -3.1)
- Lower (more negative) = better match
- Based on BM25 score

---

### Highlighting Matches

```python
def search_with_snippets(query: str) -> list[dict]:
    """Search with highlighted snippets"""
    cursor.execute(
        """
        SELECT
            id,
            name,
            snippet(datasets_fts, 2, '<b>', '</b>', '...', 50) AS snippet
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        ORDER BY rank
        LIMIT 50
        """,
        (query,)
    )
    return cursor.fetchall()
```

**Example Output:**

```python
results = search_with_snippets("climate")
# [{
#     "id": "climate-data",
#     "name": "Climate Model Data",
#     "snippet": "Historical <b>climate</b> model outputs from CMIP6..."
# }]
```

**`snippet()` Parameters:**
1. Table name: `datasets_fts`
2. Column index: `2` (description column)
3. Start marker: `<b>`
4. End marker: `</b>`
5. Ellipsis: `...`
6. Max tokens: `50`

---

## Fast Search Index

### Schema

```sql
CREATE TABLE fast_search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,      -- Dataset ID
    name TEXT NOT NULL,              -- Dataset name
    project TEXT,                    -- Primary project
    tags TEXT,                       -- Space-separated tags
    description TEXT,                -- Brief description
    format TEXT,                     -- File format
    is_remote INTEGER DEFAULT 0,     -- Cloud-only flag
    etag TEXT                        -- WebDAV ETag
);

-- Indexes for fast lookups
CREATE INDEX idx_name ON fast_search_index(name);
CREATE INDEX idx_project ON fast_search_index(project);
CREATE INDEX idx_tags ON fast_search_index(tags);
CREATE INDEX idx_remote ON fast_search_index(is_remote);
```

---

### Autocomplete

#### Name Autocomplete

```python
def autocomplete_names(prefix: str) -> list[str]:
    """Autocomplete dataset names"""
    cursor.execute(
        """
        SELECT DISTINCT name
        FROM fast_search_index
        WHERE name LIKE ? COLLATE NOCASE
        ORDER BY name
        LIMIT 10
        """,
        (f"{prefix}%",)
    )
    return [row[0] for row in cursor.fetchall()]
```

**Example:**

```python
autocomplete_names("clim")
# Returns: ["Climate Model Data", "Climate Study Notes"]
```

---

#### Project Autocomplete

```python
def autocomplete_projects(prefix: str) -> list[str]:
    """Autocomplete project names"""
    cursor.execute(
        """
        SELECT DISTINCT project
        FROM fast_search_index
        WHERE project LIKE ? COLLATE NOCASE
        ORDER BY project
        LIMIT 10
        """,
        (f"{prefix}%",)
    )
    return [row[0] for row in cursor.fetchall() if row[0]]
```

---

#### Tag Autocomplete

```python
def autocomplete_tags(prefix: str) -> list[str]:
    """Autocomplete tags (keywords)"""
    # Extract individual tags from space-separated strings
    cursor.execute("SELECT DISTINCT tags FROM fast_search_index WHERE tags IS NOT NULL")
    all_tags = set()
    for row in cursor.fetchall():
        all_tags.update(row[0].split())

    # Filter by prefix
    matching_tags = [tag for tag in all_tags if tag.lower().startswith(prefix.lower())]
    return sorted(matching_tags)[:10]
```

---

### Filtering

#### Filter by Project

```python
def filter_by_project(project: str) -> list[dict]:
    """Get all datasets in a project"""
    cursor.execute(
        """
        SELECT path, name, format
        FROM fast_search_index
        WHERE project = ?
        ORDER BY name
        """,
        (project,)
    )
    return cursor.fetchall()
```

---

#### Filter by Tag

```python
def filter_by_tag(tag: str) -> list[dict]:
    """Get datasets with a specific tag"""
    cursor.execute(
        """
        SELECT path, name, tags
        FROM fast_search_index
        WHERE tags LIKE ?
        ORDER BY name
        """,
        (f"%{tag}%",)
    )
    return cursor.fetchall()
```

---

#### Filter by Format

```python
def filter_by_format(file_format: str) -> list[dict]:
    """Get datasets by file format"""
    cursor.execute(
        """
        SELECT path, name, format
        FROM fast_search_index
        WHERE format = ?
        ORDER BY name
        """,
        (file_format,)
    )
    return cursor.fetchall()
```

---

## Performance Optimization

### 1. Index Selection

```python
# ✅ GOOD: Use fast_search_index for prefix matching
SELECT name FROM fast_search_index WHERE name LIKE 'clim%';
# Performance: ~20-40ms

# ❌ BAD: Use FTS5 for prefix matching
SELECT name FROM datasets_fts WHERE datasets_fts MATCH 'clim*';
# Performance: ~50-80ms (slower)
```

**Rule of Thumb:**
- **Prefix matching** → `fast_search_index` with `LIKE`
- **Full-text search** → `datasets_fts` with `MATCH`

---

### 2. LIMIT Results

```python
# ✅ GOOD: Limit results for autocomplete
SELECT name FROM fast_search_index WHERE name LIKE 'clim%' LIMIT 10;

# ❌ BAD: Return all matches
SELECT name FROM fast_search_index WHERE name LIKE 'clim%';
```

---

### 3. Index Hints

```sql
-- Force use of index
SELECT name
FROM fast_search_index INDEXED BY idx_name
WHERE name LIKE 'clim%';
```

---

### 4. Query Plan Analysis

```sql
EXPLAIN QUERY PLAN
SELECT name FROM fast_search_index WHERE name LIKE 'clim%';
```

**Expected Output:**

```
SEARCH fast_search_index USING INDEX idx_name (name>? AND name<?)
```

---

## Index Maintenance

### Rebuild FTS5 Index

```python
def rebuild_fts_index() -> None:
    """Rebuild FTS5 index from datasets_store"""
    cursor.execute("DELETE FROM datasets_fts")

    cursor.execute("SELECT id, payload FROM datasets_store")
    for row in cursor.fetchall():
        dataset = json.loads(row[1])
        update_fts_index(dataset)

    conn.commit()
```

---

### Rebuild Fast Search Index

```python
def rebuild_fast_index() -> None:
    """Rebuild fast_search_index from datasets_store"""
    cursor.execute("DELETE FROM fast_search_index")

    cursor.execute("SELECT id, payload FROM datasets_store")
    for row in cursor.fetchall():
        dataset = json.loads(row[1])
        update_fast_index(dataset)

    conn.commit()
```

---

### Vacuum Database

```python
def vacuum_database() -> None:
    """Reclaim unused space and rebuild indexes"""
    cursor.execute("VACUUM")
    conn.commit()
    logger.info("Database vacuumed successfully")
```

**When to vacuum:**
- After mass deletions
- When database file is bloated
- During maintenance windows

---

## Benchmarks

### Search Performance

| Operation | Index | Query | Time (ms) | Notes |
|-----------|-------|-------|-----------|-------|
| Simple search | FTS5 | `climate` | 50-80 | 10,000 datasets |
| Phrase search | FTS5 | `"climate model"` | 60-90 | 10,000 datasets |
| Boolean search | FTS5 | `climate AND temp` | 70-100 | 10,000 datasets |
| Autocomplete | Fast | `name LIKE 'clim%'` | 20-40 | 10,000 datasets |
| Tag filter | Fast | `tags LIKE '%climate%'` | 30-50 | 10,000 datasets |
| Project filter | Fast | `project = '...'` | 10-20 | 10,000 datasets |

---

### Index Size

| Index | Size per Dataset | Total (10,000 datasets) |
|-------|------------------|-------------------------|
| FTS5 index | ~1 KB | ~10 MB |
| Fast search index | ~500 bytes | ~5 MB |
| Total index overhead | ~1.5 KB | ~15 MB |

---

## Best Practices

### 1. Choose the Right Index

```python
# ✅ Autocomplete → fast_search_index
autocomplete_names("clim")

# ✅ Full-text search → datasets_fts
search_simple("climate temperature")

# ✅ Exact ID lookup → datasets_store
get_dataset("climate-data")
```

---

### 2. Keep Indexes in Sync

```python
def save_dataset(metadata: dict) -> None:
    """Save dataset and update all indexes"""
    # 1. Save to store
    upsert_dataset(metadata["id"], metadata)

    # 2. Update FTS5
    update_fts_index(metadata)

    # 3. Update fast index
    update_fast_index(metadata)

    conn.commit()  # Single transaction
```

---

### 3. Batch Index Updates

```python
# ✅ GOOD: Batch updates in one transaction
cursor.execute("BEGIN TRANSACTION")
for dataset in datasets:
    update_fts_index(dataset)
    update_fast_index(dataset)
cursor.execute("COMMIT")

# ❌ BAD: Individual commits
for dataset in datasets:
    update_fts_index(dataset)
    conn.commit()
```

---

## Troubleshooting

### Slow Queries

**Symptom:** Search taking >200ms

**Diagnosis:**

```python
import time

start = time.time()
results = search_simple("climate")
elapsed = (time.time() - start) * 1000
print(f"Query took {elapsed:.2f}ms")
```

**Solutions:**
1. Check index exists: `PRAGMA index_list('fast_search_index');`
2. Rebuild FTS5 index: `rebuild_fts_index()`
3. Vacuum database: `VACUUM;`
4. Check query plan: `EXPLAIN QUERY PLAN SELECT ...`

---

### Missing Results

**Symptom:** Expected datasets not in search results

**Diagnosis:**

```python
# Check if dataset in FTS5 index
cursor.execute("SELECT * FROM datasets_fts WHERE id = ?", (dataset_id,))
print(cursor.fetchone())

# Check if dataset in store
cursor.execute("SELECT * FROM datasets_store WHERE id = ?", (dataset_id,))
print(cursor.fetchone())
```

**Solutions:**
1. Rebuild FTS5 index from store
2. Check indexing code updates FTS5 on insert
3. Verify field values are not empty

---

## Related Documentation

- **[Data Layer Overview](overview.md)** - Architecture overview
- **[Schema](schema.md)** - Database schema
- **[Storage](storage.md)** - Storage mechanisms
- **[Services: Fast Search](../codebase/services-module.md#fast-search)** - Search service implementation

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
