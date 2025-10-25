# Performance Optimization

## Introduction

This document provides optimization strategies, patterns, and best practices for Hei-DataHub performance.

---

## General Principles

### 1. Measure First, Optimize Second

```python
# ❌ BAD: Premature optimization
def search(query):
    # "This might be slow, let me optimize"
    return ultra_optimized_complex_search(query)

# ✅ GOOD: Measure, then optimize
def search(query):
    # Simple, readable implementation
    results = simple_search(query)

    # Profile shows it's actually fast enough
    return results
```

**Rule:** Don't optimize without profiling data.

---

### 2. Optimize the Bottleneck

```python
# Profile shows:
# Function A: 5ms (10% of time)
# Function B: 45ms (90% of time)

# ❌ BAD: Optimize A (small impact)
def function_a():
    # Micro-optimizations, save 2ms
    pass

# ✅ GOOD: Optimize B (big impact)
def function_b():
    # Even small improvement has big impact
    # Save 10ms → 22% improvement
    pass
```

---

### 3. Balance Complexity vs. Performance

```python
# ❌ BAD: Complex optimization for small gain
def search(query):
    # 500 lines of complex caching logic
    # Saves 5ms (95ms → 90ms)
    pass

# ✅ GOOD: Simple optimization for big gain
def search(query, limit=20):
    # Add LIMIT clause
    # Saves 50ms (95ms → 45ms)
    sql = f"... LIMIT {limit}"
    return execute(sql)
```

---

## Database Optimization

### 1. Use Indexes

```sql
-- ❌ BAD: No index
SELECT * FROM datasets_store
WHERE created_at > '2025-01-01';
-- Query time: 250ms (full table scan)

-- ✅ GOOD: Index on created_at
CREATE INDEX idx_created_at ON datasets_store(created_at);

SELECT * FROM datasets_store
WHERE created_at > '2025-01-01';
-- Query time: 8ms (index scan)
```

**When to index:**
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Foreign keys

**When NOT to index:**
- Small tables (< 1000 rows)
- Frequently updated columns
- Low cardinality columns (few unique values)

---

### 2. Limit Result Sets

```python
# ❌ BAD: Fetch all results
def search(query):
    results = execute(f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{query}'")
    return results.fetchall()  # May return 10,000 rows!

# ✅ GOOD: Limit results
def search(query, limit=20):
    sql = f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{query}' LIMIT {limit}"
    return execute(sql).fetchall()  # Maximum 20 rows
```

---

### 3. Use Prepared Statements

```python
# ❌ BAD: Compile query every time
def search(query):
    sql = f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{query}'"
    return execute(sql)  # Compilation: 15ms

# ✅ GOOD: Prepare once, reuse
_prepared_search = None

def search(query):
    global _prepared_search
    if _prepared_search is None:
        _prepared_search = connection.prepare(
            "SELECT * FROM datasets_fts WHERE datasets_fts MATCH ?"
        )
    return _prepared_search.execute(query)  # Compilation: 0ms (cached)
```

---

### 4. Batch Operations

```python
# ❌ BAD: Insert one at a time
for dataset in datasets:
    execute("INSERT INTO datasets_store VALUES (?)", dataset)
# 1000 datasets: 5,000ms (5ms × 1000)

# ✅ GOOD: Batch insert
execute_many("INSERT INTO datasets_store VALUES (?)", datasets)
# 1000 datasets: 150ms (15× faster)
```

---

## Search Optimization

### 1. FTS5 Query Optimization

```python
# ❌ BAD: Broad query
def search(query):
    # Searches all columns, slow
    return execute(f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{query}'")

# ✅ GOOD: Targeted column search
def search(query, columns=['title', 'description']):
    # Only search specific columns
    column_queries = [f"{col}:{query}" for col in columns]
    match_query = " OR ".join(column_queries)
    return execute(f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{match_query}'")
```

---

### 2. Result Ranking Optimization

```python
# ❌ BAD: Rank all results in Python
def search(query):
    results = execute(f"... MATCH '{query}'").fetchall()
    ranked = rank_results(results)  # Rank 5000 results in Python
    return ranked[:20]

# ✅ GOOD: Rank in SQL
def search(query, limit=20):
    # FTS5 BM25 ranking in SQL
    sql = f"""
        SELECT *, rank FROM datasets_fts
        WHERE datasets_fts MATCH '{query}'
        ORDER BY rank
        LIMIT {limit}
    """
    return execute(sql).fetchall()
```

---

### 3. Autocomplete Optimization

```python
# ❌ BAD: Fuzzy matching on every keystroke
def autocomplete(prefix):
    # Check all datasets for fuzzy matches
    all_terms = get_all_terms()  # 100,000 terms
    matches = [t for t in all_terms if fuzzy_match(t, prefix)]
    return matches[:10]

# ✅ GOOD: Prefix index
def autocomplete(prefix):
    # Prefix search on indexed terms
    sql = "SELECT term FROM autocomplete_index WHERE term LIKE ? LIMIT 10"
    return execute(sql, f"{prefix}%").fetchall()
```

---

## Network Optimization

### 1. Connection Pooling

```python
# ❌ BAD: New connection every request
def download(url):
    client = httpx.Client()
    response = client.get(url)
    client.close()
    return response
# Per request: 100ms (TLS handshake) + 20ms (download)

# ✅ GOOD: Reuse connections
_client = httpx.Client(
    limits=httpx.Limits(max_connections=10, keepalive_expiry=60)
)

def download(url):
    return _client.get(url)
# Per request: 0ms (reused) + 20ms (download)
```

---

### 2. Parallel Requests

```python
# ❌ BAD: Sequential downloads
async def sync_download(datasets):
    results = []
    for dataset in datasets:
        result = await download(dataset)  # 50ms each, serial
        results.append(result)
    return results
# 100 datasets: 5,000ms

# ✅ GOOD: Parallel downloads
async def sync_download(datasets):
    # 10 concurrent downloads
    semaphore = asyncio.Semaphore(10)

    async def download_limited(dataset):
        async with semaphore:
            return await download(dataset)

    return await asyncio.gather(*[download_limited(d) for d in datasets])
# 100 datasets: 500ms (10× faster)
```

---

### 3. Incremental Sync

```python
# ❌ BAD: Full sync every time
def sync():
    remote = list_all_remote_datasets()  # 1000 datasets
    local = list_all_local_datasets()

    for dataset in remote:
        if dataset not in local:
            download(dataset)
# Every sync: Check 1000 datasets

# ✅ GOOD: Track sync state
def sync():
    last_sync = get_last_sync_timestamp()

    # Only get datasets modified since last sync
    modified = list_modified_since(last_sync)  # e.g., 10 datasets

    for dataset in modified:
        if should_download(dataset):
            download(dataset)

    update_last_sync_timestamp()
# Typical sync: Check 10 datasets (100× faster)
```

---

## UI Optimization

### 1. Debounce User Input

```python
# ❌ BAD: Search on every keystroke
class SearchInput(Input):
    def on_input_changed(self, event):
        results = search(event.value)  # 45ms per keystroke
        self.update_results(results)
# Typing "machine learning" triggers 17 searches

# ✅ GOOD: Debounce input
class SearchInput(Input):
    def on_input_changed(self, event):
        # Cancel previous timer
        if self._search_timer:
            self._search_timer.cancel()

        # Start new timer (300ms delay)
        self._search_timer = self.set_timer(
            0.3,
            lambda: self._do_search(event.value)
        )

    def _do_search(self, query):
        results = search(query)
        self.update_results(results)
# Typing "machine learning" triggers 1 search (after pause)
```

---

### 2. Lazy Rendering

```python
# ❌ BAD: Render all rows
class DatasetTable(DataTable):
    def update_results(self, results):
        self.clear()
        for r in results:  # 5000 results
            self.add_row(r.title, r.author, ...)
        # Render time: 800ms

# ✅ GOOD: Virtual scrolling (built into Textual DataTable)
class DatasetTable(DataTable):
    def update_results(self, results):
        self.clear()
        # DataTable only renders visible rows
        for r in results[:100]:  # Limit initial render
            self.add_row(r.title, r.author, ...)
        # More rows loaded on scroll
        # Render time: 45ms
```

---

### 3. Async UI Updates

```python
# ❌ BAD: Block UI thread
class HomeView(Screen):
    def on_mount(self):
        # Blocking call
        sync_status = check_cloud_status()  # 2,000ms
        self.update_status(sync_status)
# UI frozen for 2 seconds

# ✅ GOOD: Async loading
class HomeView(Screen):
    async def on_mount(self):
        # Show loading state
        self.show_loading()

        # Non-blocking async call
        sync_status = await check_cloud_status_async()

        # Update UI
        self.hide_loading()
        self.update_status(sync_status)
# UI responsive, status loads in background
```

---

## Memory Optimization

### 1. Use Generators

```python
# ❌ BAD: Load all in memory
def get_all_datasets():
    results = execute("SELECT * FROM datasets_store").fetchall()
    return [Dataset.from_row(r) for r in results]  # 50 MB in memory
# Memory: 50 MB

# ✅ GOOD: Yield results
def get_all_datasets():
    results = execute("SELECT * FROM datasets_store")
    for row in results:
        yield Dataset.from_row(row)
# Memory: ~1 MB (streaming)
```

---

### 2. Limit Cache Size

```python
# ❌ BAD: Unbounded cache
_cache = {}

def get_dataset(uuid):
    if uuid not in _cache:
        _cache[uuid] = fetch_dataset(uuid)
    return _cache[uuid]
# After 10,000 lookups: 100 MB

# ✅ GOOD: LRU cache
from functools import lru_cache

@lru_cache(maxsize=128)
def get_dataset(uuid):
    return fetch_dataset(uuid)
# Cache size: ~5 MB (128 recent datasets)
```

---

### 3. Lazy Loading

```python
# ❌ BAD: Eager loading
class Dataset:
    def __init__(self, uuid):
        self.uuid = uuid
        self.metadata = fetch_metadata(uuid)  # Expensive
        self.files = fetch_files(uuid)        # Expensive

# ✅ GOOD: Lazy properties
class Dataset:
    def __init__(self, uuid):
        self.uuid = uuid
        self._metadata = None
        self._files = None

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = fetch_metadata(self.uuid)
        return self._metadata

    @property
    def files(self):
        if self._files is None:
            self._files = fetch_files(self.uuid)
        return self._files
# Only load when accessed
```

---

## Algorithmic Optimization

### 1. Use Appropriate Data Structures

```python
# ❌ BAD: Linear search in list
synced_ids = []  # List of 10,000 UUIDs

def is_synced(uuid):
    return uuid in synced_ids  # O(n) lookup
# 10,000 checks: 5,000ms

# ✅ GOOD: Hash set
synced_ids = set()  # Set of 10,000 UUIDs

def is_synced(uuid):
    return uuid in synced_ids  # O(1) lookup
# 10,000 checks: 5ms (1000× faster)
```

---

### 2. Avoid Repeated Computation

```python
# ❌ BAD: Recompute every time
def format_dataset(dataset):
    # Compute hash every call
    hash_value = compute_hash(dataset)  # 5ms
    return f"{dataset.title} ({hash_value})"

# Called 1000 times: 5,000ms

# ✅ GOOD: Cache computation
class Dataset:
    @cached_property
    def hash(self):
        return compute_hash(self)

def format_dataset(dataset):
    return f"{dataset.title} ({dataset.hash})"
# First call: 5ms, subsequent: 0ms
```

---

### 3. Early Termination

```python
# ❌ BAD: Check all items
def has_unsynced_datasets(datasets):
    unsynced = [d for d in datasets if not d.synced]
    return len(unsynced) > 0
# Checks all 10,000 datasets

# ✅ GOOD: Return early
def has_unsynced_datasets(datasets):
    return any(not d.synced for d in datasets)
# Returns as soon as first unsynced found
```

---

## Optimization Checklist

### Before Optimization

- [ ] Profile to identify bottleneck
- [ ] Measure current performance
- [ ] Set target performance goal
- [ ] Estimate optimization effort

### During Optimization

- [ ] Keep changes isolated
- [ ] Test each change independently
- [ ] Maintain code readability
- [ ] Document trade-offs

### After Optimization

- [ ] Re-profile to verify improvement
- [ ] Run full test suite
- [ ] Update benchmarks
- [ ] Document optimization

---

## Quick Wins

**Easy optimizations with big impact:**

1. **Add `LIMIT` to queries** - 5 min, 50% improvement
2. **Enable connection pooling** - 10 min, 80% improvement
3. **Debounce user input** - 15 min, 90% improvement
4. **Use indexes** - 5 min, 95% improvement
5. **Batch database operations** - 20 min, 90% improvement

---

## Anti-Patterns

### Don't Micro-Optimize

```python
# ❌ BAD: Premature micro-optimization
def search(query):
    # Using bitwise operations for "speed"
    results = []
    for i in range(len(datasets)):
        if (datasets[i].flags & 0x01):  # ???
            results.append(datasets[i])
    return results

# ✅ GOOD: Readable code
def search(query):
    return [d for d in datasets if d.is_active]
```

---

### Don't Sacrifice Correctness

```python
# ❌ BAD: Fast but wrong
def search(query):
    # Cache results forever, never updates
    if query in cache:
        return cache[query]
    results = perform_search(query)
    cache[query] = results  # Stale data!
    return results

# ✅ GOOD: Fast and correct
def search(query):
    cache_key = (query, get_db_version())  # Include version
    if cache_key in cache:
        return cache[cache_key]
    results = perform_search(query)
    cache[cache_key] = results
    return results
```

---

## Related Documentation

- **[Performance Overview](overview.md)** - Metrics and goals
- **[Profiling](profiling.md)** - Profiling techniques
- **[Hotspots](hotspots.md)** - Known bottlenecks

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
