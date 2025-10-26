# Database & Full-Text Search

**Learning Goal**: Master SQLite FTS5 full-text search and understand how Hei-DataHub achieves <80ms search performance.

By the end of this page, you'll:
- Understand the dual-storage architecture (JSON store + FTS5 index)
- Learn how FTS5 virtual tables work
- See how BM25 ranking scores results
- Build FTS5 queries with operators
- Implement incremental search with prefix wildcards
- Manage database connections efficiently
- Index and reindex datasets

---

## The Dual-Storage Architecture

Hei-DataHub uses **two storage mechanisms** working together:

```
┌────────────────────────────────────────┐
│  datasets_store                        │  ← Full JSON blobs
│  ├─ id (primary key)                   │
│  ├─ payload (JSON text)                │
│  ├─ created_at                         │
│  └─ updated_at                         │
└────────────────────────────────────────┘
         ↓ Synchronized with ↓
┌────────────────────────────────────────┐
│  datasets_fts (FTS5 virtual table)     │  ← Searchable text
│  ├─ id                                 │
│  ├─ name                               │
│  ├─ description                        │
│  ├─ used_in_projects                   │
│  ├─ data_types                         │
│  ├─ source                             │
│  └─ file_format                        │
└────────────────────────────────────────┘
```

**Why two tables?**

1. **datasets_store** — Complete metadata in JSON format
   - Fast retrieval by ID
   - Easy schema evolution
   - Full data integrity

2. **datasets_fts** — FTS5 virtual table for search
   - Optimized for full-text search
   - BM25 relevance ranking
   - Incremental search support
   - <80ms query performance

---

## What is FTS5?

**FTS5** (Full-Text Search version 5) is SQLite's built-in search engine.

### Traditional SQL vs. FTS5

**Traditional LIKE query** (slow):
```sql
SELECT * FROM datasets
WHERE description LIKE '%climate%'
  OR dataset_name LIKE '%climate%'
```
⚠️ **Problem**: Scans entire table, no ranking, no stemming

**FTS5 query** (fast):
```sql
SELECT * FROM datasets_fts
WHERE datasets_fts MATCH 'climate*'
ORDER BY bm25(datasets_fts)
```
✅ **Benefits**:
- Inverted index (instant lookup)
- BM25 ranking (best matches first)
- Porter stemming ("climates" → "climate")
- Prefix matching ("clim*" matches "climate")

---

## Creating the FTS5 Table

**File:** Schema definition (executed at startup)

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts
USING fts5(
    id UNINDEXED,              -- Don't index ID (exact match field)
    name,                      -- Dataset name (indexed)
    description,               -- Full description (indexed)
    used_in_projects,          -- Project tags (indexed)
    data_types,                -- Data types (indexed)
    source,                    -- Source URL (indexed)
    file_format,               -- File format (indexed)
    tokenize='porter unicode61' -- Stemming + Unicode support
);
```

**Key concepts:**

1. **VIRTUAL TABLE** — Not a real table, it's a search index
2. **UNINDEXED** — Store but don't search the `id` field
3. **tokenize='porter unicode61'**:
   - `porter` — Stemming algorithm (runs → run, running → run)
   - `unicode61` — Unicode support (handles accents, etc.)

---

## How Data Gets Into FTS5

### Upsert Operation

**File:** `src/mini_datahub/infra/index.py`

```python
def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """
    Insert or update dataset in both store and FTS index.

    Args:
        dataset_id: Unique dataset ID
        metadata: Full metadata dictionary
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Store full JSON payload
        payload = json.dumps(metadata)
        cursor.execute(
            """
            INSERT INTO datasets_store (id, payload, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = datetime('now')
            """,
            (dataset_id, payload),
        )

        # Step 2: Remove old FTS entry if exists
        cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))

        # Step 3: Extract searchable fields
        name = metadata.get("dataset_name", "")
        description = metadata.get("description", "")
        used_in_projects = " ".join(metadata.get("used_in_projects", []))
        data_types = " ".join(metadata.get("data_types", []))
        source = metadata.get("source", "")
        file_format = metadata.get("file_format", "")

        # Step 4: Insert into FTS5 index
        cursor.execute(
            """
            INSERT INTO datasets_fts (
                id, name, description, used_in_projects,
                data_types, source, file_format
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (dataset_id, name, description, used_in_projects,
             data_types, source, file_format),
        )

        conn.commit()
    finally:
        conn.close()
```

**Flow:**
1. Save full JSON to `datasets_store`
2. Delete old FTS5 entry (if exists)
3. Flatten list fields (`["climate", "weather"]` → `"climate weather"`)
4. Insert into FTS5 index
5. Commit transaction

---

## Searching with FTS5

### Simple Search

**File:** `src/mini_datahub/services/search.py`

```python
def _simple_fts_search(query: str, limit: int) -> List[Dict[str, Any]]:
    """
    Execute FTS5 search with BM25 ranking.

    Args:
        query: User's search text (e.g., "climate data")
        limit: Maximum results

    Returns:
        List of ranked results
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Build FTS5 query with prefix wildcards
        tokens = query.strip().split()
        fts_query = " ".join(f"{token}*" for token in tokens)
        # "climate data" → "climate* data*"

        # Step 2: Execute FTS5 query with JOIN
        cursor.execute(
            """
            SELECT
                datasets_fts.id,
                datasets_fts.name,
                snippet(datasets_fts, 2, '<b>', '</b>', '...', 40) as snippet,
                bm25(datasets_fts) as rank,
                datasets_store.payload
            FROM datasets_fts
            JOIN datasets_store ON datasets_fts.id = datasets_store.id
            WHERE datasets_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, limit),
        )

        # Step 3: Parse results
        results = []
        for row in cursor.fetchall():
            payload = json.loads(row["payload"])
            results.append({
                "id": row["id"],
                "name": row["name"],
                "snippet": row["snippet"],  # Highlighted excerpt
                "rank": row["rank"],         # BM25 score (lower = better)
                "metadata": payload,         # Full dataset info
            })

        return results

    finally:
        conn.close()
```

**What's happening:**

1. **Prefix wildcards** (`climate*`) — Matches "climate", "climatic", "climatology"
2. **snippet()** — Generates highlighted excerpt: `...about <b>climate</b> change...`
3. **bm25()** — Relevance score (lower is better in SQLite FTS5)
4. **JOIN** — Combine FTS index with full JSON payload
5. **ORDER BY rank** — Best matches first

---

## BM25 Ranking Explained

**BM25** (Best Matching 25) is a probabilistic ranking function.

### How BM25 Works

```
BM25(term, document) =
    IDF(term) * (f(term, document) * (k1 + 1))
    / (f(term, document) + k1 * (1 - b + b * |document| / avgdl))
```

**In plain English:**

1. **IDF** (Inverse Document Frequency) — Rare words score higher
   - "the" → low score (appears everywhere)
   - "climatology" → high score (rare term)

2. **Term frequency** — How often term appears in document
   - Appears 3 times → better than 1 time

3. **Document length normalization** — Prevents bias toward long documents
   - Short document with "climate" → boosted score
   - Long document with "climate" → penalized

**Example:**

```
Query: "climate data"

Results:
1. "Climate Change Data 2023" — rank: -2.5 (best)
2. "Weather and Climate Trends" — rank: -1.8
3. "Environmental Data Archive" — rank: -0.9 (worst)
```

Lower scores = better matches!

---

## FTS5 Query Operators

### 1. Prefix Search

```sql
WHERE datasets_fts MATCH 'climate*'
```
Matches: "climate", "climates", "climatic", "climatology"

---

### 2. AND (implicit)

```sql
WHERE datasets_fts MATCH 'climate data'
```
Finds documents with **both** "climate" AND "data"

---

### 3. OR

```sql
WHERE datasets_fts MATCH 'climate OR weather'
```
Finds documents with **either** term

---

### 4. NOT

```sql
WHERE datasets_fts MATCH 'climate NOT forecast'
```
Finds documents with "climate" but **without** "forecast"

---

### 5. Phrase Search

```sql
WHERE datasets_fts MATCH '"climate change"'
```
Finds exact phrase (words must be adjacent)

---

### 6. Column-Specific Search

```sql
WHERE datasets_fts MATCH 'name:climate'
```
Search only in the `name` column

---

### 7. NEAR Operator

```sql
WHERE datasets_fts MATCH 'NEAR(climate data, 10)'
```
Words must be within 10 tokens of each other

---

## Incremental Search Implementation

**Goal:** Update results as user types, with <80ms latency.

### The Challenge

User types: `c` → `cl` → `cli` → `clim` → `clima` → `climat` → `climate`

**Naive approach**: 7 separate queries (slow!)

**Smart approach**: Debounce + prefix wildcards

### Implementation

**File:** `src/mini_datahub/ui/views/home.py`

```python
class HomeScreen(Screen):
    _debounce_timer: Optional[Timer] = None

    def on_input_changed(self, event: Input.Changed):
        """Handle search input changes (debounced)."""
        query = event.value

        # Cancel previous timer
        if self._debounce_timer:
            self._debounce_timer.stop()

        # Set new timer (200ms)
        self._debounce_timer = self.set_timer(
            0.2,
            lambda: self.perform_search(query)
        )

    def perform_search(self, query: str):
        """Execute search with prefix wildcard."""
        from mini_datahub.services.search import search_datasets

        # Add prefix wildcard for incremental search
        # User types "clim" → FTS5 searches "clim*"
        results = search_datasets(query, limit=50)

        # Update table
        self.populate_table(results)
```

**Result:** Only searches 200ms after user stops typing, not on every keystroke!

---

## Structured Query Support

Hei-DataHub supports **field-specific filters**:

```
source:github climate
format:csv
date:>2025-01
project:gideon data
```

### How It Works

**File:** `src/mini_datahub/services/search.py`

```python
def _structured_search(parsed: ParsedQuery, limit: int) -> List[Dict[str, Any]]:
    """
    Execute search with structured filters.

    Example:
        parsed.field_filters = [("source", EQUALS, "github")]
        parsed.free_text_query = "climate"
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Build WHERE clause from filters
    where_clauses = []
    params = []

    for field, operator, value in parsed.field_filters:
        if field == "source":
            if operator == QueryOperator.EQUALS:
                where_clauses.append("datasets_fts.source MATCH ?")
                params.append(value)

        elif field == "format":
            where_clauses.append("datasets_fts.file_format MATCH ?")
            params.append(value)

        # Add more field handlers...

    # Step 2: Add free text search if present
    if parsed.free_text_query:
        tokens = parsed.free_text_query.split()
        fts_query = " ".join(f"{t}*" for t in tokens)
        where_clauses.append("datasets_fts MATCH ?")
        params.append(fts_query)

    # Step 3: Combine clauses
    where_sql = " AND ".join(where_clauses)

    # Step 4: Execute query
    cursor.execute(
        f"""
        SELECT
            datasets_fts.id,
            datasets_fts.name,
            snippet(datasets_fts, 2, '<b>', '</b>', '...', 40) as snippet,
            bm25(datasets_fts) as rank,
            datasets_store.payload
        FROM datasets_fts
        JOIN datasets_store ON datasets_fts.id = datasets_store.id
        WHERE {where_sql}
        ORDER BY rank
        LIMIT ?
        """,
        (*params, limit),
    )

    # Parse results...
    return results
```

**Example Query:**

```
User types: "source:github climate data"

Step 1: Parse
  - field_filters: [("source", EQUALS, "github")]
  - free_text_query: "climate data"

Step 2: Build SQL
  WHERE datasets_fts.source MATCH 'github'
    AND datasets_fts MATCH 'climate* data*'

Step 3: Execute
  Returns datasets from GitHub about climate data
```

---

## Database Connection Management

### Singleton Pattern

**File:** `src/mini_datahub/infra/db.py`

```python
_connection = None  # Global singleton

def get_connection() -> sqlite3.Connection:
    """
    Get or create database connection.

    Uses singleton pattern to reuse connection.
    """
    global _connection

    if _connection is None:
        db_path = DB_PATH  # ~/.local/share/hei-datahub/db.sqlite
        db_path.parent.mkdir(parents=True, exist_ok=True)

        _connection = sqlite3.connect(str(db_path))
        _connection.row_factory = sqlite3.Row  # Access columns by name

        # Performance optimizations
        _connection.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        _connection.execute("PRAGMA synchronous=NORMAL")
        _connection.execute("PRAGMA cache_size=10000")

    return _connection
```

**Benefits:**
- One connection per process (fast)
- No connection overhead on repeated calls
- WAL mode for concurrent reads/writes

---

### WAL Mode Explained

**WAL** (Write-Ahead Logging) = Better concurrency

**Without WAL:**
- Reads block writes
- Writes block reads
- One operation at a time

**With WAL:**
- Reads and writes happen simultaneously
- Faster for search-heavy workloads
- Hei-DataHub benefits: User can search while indexer runs in background

---

## Reindexing All Datasets

Sometimes you need to rebuild the entire index (e.g., after schema changes).

**File:** `src/mini_datahub/infra/index.py`

```python
def reindex_all() -> Tuple[int, List[str]]:
    """
    Rebuild FTS5 index from YAML files on disk.

    Returns:
        (count, errors) - number indexed and error messages
    """
    from mini_datahub.infra.paths import DATA_DIR
    from mini_datahub.infra.store import read_dataset

    count = 0
    errors = []

    # Step 1: Clear existing index
    conn = get_connection()
    conn.execute("DELETE FROM datasets_fts")
    conn.execute("DELETE FROM datasets_store")
    conn.commit()

    # Step 2: Scan data directory
    for dataset_dir in DATA_DIR.iterdir():
        if not dataset_dir.is_dir():
            continue

        dataset_id = dataset_dir.name

        try:
            # Step 3: Read metadata.yaml
            metadata = read_dataset(dataset_id)
            if metadata:
                # Step 4: Re-index
                upsert_dataset(dataset_id, metadata)
                count += 1

        except Exception as e:
            errors.append(f"{dataset_id}: {str(e)}")

    return count, errors
```

**Usage:**

```bash
# CLI command
hei-datahub reindex

# Or from Python
from mini_datahub.infra.index import reindex_all
count, errors = reindex_all()
print(f"Indexed {count} datasets")
```

---

## Performance Benchmarks

Real performance from Hei-DataHub:

| Operation | Time | Details |
|-----------|------|---------|
| Simple search | **<80ms** | 1000 datasets, single term |
| Complex search | **<120ms** | Multiple filters + free text |
| Index one dataset | **<10ms** | Upsert to both tables |
| Reindex all | **<5s** | 1000 datasets |

**Why so fast?**

1. **FTS5 inverted index** — O(1) term lookup
2. **BM25 ranking** — Computed during query (not stored)
3. **WAL mode** — No lock contention
4. **Prefix wildcards** — Incremental search without re-querying
5. **Connection pooling** — Singleton pattern eliminates overhead

---

## What You've Learned

✅ **Dual-storage architecture** — JSON store + FTS5 index
✅ **FTS5 virtual tables** — How they work and why they're fast
✅ **BM25 ranking** — Relevance scoring algorithm
✅ **Query operators** — Prefix, AND, OR, NOT, phrases, NEAR
✅ **Incremental search** — Debouncing + prefix wildcards
✅ **Connection management** — Singleton pattern with WAL mode
✅ **Reindexing** — Rebuilding the search index

---

## Try It Yourself

### Exercise 1: Add Custom Ranking

**Goal:** Boost results where term appears in `name` vs `description`.

**Hint:** Use FTS5 column weights:

```sql
CREATE VIRTUAL TABLE datasets_fts
USING fts5(
    id UNINDEXED,
    name,
    description,
    ...,
    tokenize='porter unicode61'
);

-- Then search with:
SELECT *, bm25(datasets_fts, 10.0, 1.0) as rank
FROM datasets_fts
WHERE datasets_fts MATCH 'climate*'
ORDER BY rank;
```

First number (10.0) = weight for `name`
Second number (1.0) = weight for `description`

---

### Exercise 2: Implement Fuzzy Search

**Goal:** Find "clmate" when user meant "climate".

**Hint:** Use Levenshtein distance or try multiple spellings:

```python
def fuzzy_search(query: str):
    # Try exact match first
    results = search_datasets(query)
    if results:
        return results

    # Try common typos
    variations = [
        query.replace("ei", "ie"),  # recieve → receive
        query.replace("ie", "ei"),  # freind → friend
        # Add more rules...
    ]

    for variant in variations:
        results = search_datasets(variant)
        if results:
            return results

    return []
```

---

### Exercise 3: Add Search Analytics

**Goal:** Track which queries return no results.

**Hint:** Create a `search_log` table:

```sql
CREATE TABLE search_log (
    id INTEGER PRIMARY KEY,
    query TEXT,
    result_count INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Log every search and analyze zero-result queries to improve dataset metadata.

---

## Next Steps

Now you understand the database layer. Next, let's explore **autocomplete and suggestion ranking**.

**Next:** [Autocomplete & Suggestions](03-autocomplete.md)

---

## Further Reading

- [SQLite FTS5 Documentation](https://www.sqlite.org/fts5.html)
- [BM25 Ranking Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [Hei-DataHub Performance](../../performance/overview.md)
