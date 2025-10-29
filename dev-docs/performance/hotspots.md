# Performance Hotspots

## Introduction

This document identifies known performance bottlenecks in Hei-DataHub and provides mitigation strategies.

---

## Search Hotspots

### 1. FTS5 Query Compilation

**Location:** `src/hei_datahub/services/fast_search.py`

**Issue:**
- SQLite compiles FTS query on every search
- Compilation takes ~10-20ms
- Significant for autocomplete (< 50ms target)

**Profiling:**

```python
@profile
def search(query: str):
    sql = f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{query}'"
    return execute(sql)

# Profile shows:
# Line 1: 18ms (SQL compilation)
# Line 2: 22ms (execution)
```

**Mitigation:**

```python
# Cache prepared statement
from functools import lru_cache

@lru_cache(maxsize=128)
def _get_prepared_statement():
    """Get cached prepared statement"""
    return prepare("SELECT * FROM datasets_fts WHERE datasets_fts MATCH ?")

def search(query: str):
    stmt = _get_prepared_statement()
    return stmt.execute(query)

# After: 5ms compilation (cached) + 22ms execution
```

**Status:** ✅ Fixed in v0.58.0

---

### 2. Large Result Sets

**Location:** `src/hei_datahub/services/fast_search.py`

**Issue:**
- Fetching all results at once
- Memory spike with 1000+ results
- Slow UI rendering

**Profiling:**

```python
def search(query: str):
    results = execute(sql).fetchall()  # Fetches all rows
    return [Dataset.from_row(r) for r in results]

# With 5000 results:
# fetchall(): 150ms
# Object creation: 280ms
# Total: 430ms (too slow!)
```

**Mitigation:**

```python
def search(query: str, limit: int = 20):
    # Limit results
    sql = f"... LIMIT {limit}"
    results = execute(sql).fetchall()

    # Lazy object creation
    return [Dataset.from_row(r) for r in results]

# With limit=20:
# fetchall(): 8ms
# Object creation: 12ms
# Total: 20ms ✓
```

**Status:** ✅ Fixed in v0.56.0

---

### 3. Autocomplete Index Rebuilds

**Location:** `src/hei_datahub/services/autocomplete.py`

**Issue:**
- Rebuilding entire autocomplete index on every dataset change
- Blocks UI thread
- Takes 2-3 seconds for 10,000 datasets

**Profiling:**

```python
def rebuild_autocomplete_index():
    # Delete all
    execute("DELETE FROM autocomplete_index")

    # Rebuild from scratch
    for dataset in get_all_datasets():  # 10,000 iterations
        extract_and_index_terms(dataset)

# Total: 2,800ms
```

**Mitigation:**

```python
def update_autocomplete_index(dataset_id: str):
    """Incremental update"""
    # Delete old terms for this dataset only
    execute("DELETE FROM autocomplete_index WHERE dataset_id = ?", dataset_id)

    # Add new terms
    dataset = get_dataset(dataset_id)
    extract_and_index_terms(dataset)

# Total: 3ms per dataset ✓
```

**Status:** ✅ Fixed in v0.59.0

---

## Sync Hotspots

### 4. Serial WebDAV Downloads

**Location:** `src/hei_datahub/services/sync.py`

**Issue:**
- Downloading datasets sequentially
- Not utilizing network bandwidth
- 1000 datasets takes 45 seconds

**Profiling:**

```python
def sync_download():
    datasets = list_remote_datasets()  # 1000 datasets

    for dataset in datasets:
        download(dataset)  # ~45ms each, serial

# Total: 45,000ms (45 seconds)
```

**Mitigation:**

```python
import asyncio

async def sync_download():
    datasets = await list_remote_datasets()

    # Download in parallel (10 concurrent)
    semaphore = asyncio.Semaphore(10)

    async def download_with_limit(dataset):
        async with semaphore:
            await download_async(dataset)

    await asyncio.gather(*[download_with_limit(d) for d in datasets])

# With 10 concurrent:
# Total: ~5,000ms (5 seconds) ✓
```

**Status:** ✅ Fixed in v0.56.0

---

### 5. Redundant Cloud Checks

**Location:** `src/hei_datahub/services/sync.py`

**Issue:**
- Checking if every dataset exists on cloud
- 1000 HEAD requests take 30 seconds
- Most datasets haven't changed

**Profiling:**

```python
def sync_upload():
    local_datasets = get_local_datasets()  # 1000 datasets

    for dataset in local_datasets:
        if not exists_on_cloud(dataset):  # HEAD request: 30ms
            upload(dataset)

# Total: 30,000ms just for checks
```

**Mitigation:**

```python
def sync_upload():
    # Track sync state locally
    last_sync = get_last_sync_state()

    # Only check datasets modified since last sync
    modified = get_modified_since(last_sync)  # e.g., 10 datasets

    for dataset in modified:
        if not exists_on_cloud(dataset):
            upload(dataset)

# Total: 300ms (10 checks) ✓
```

**Status:** ✅ Fixed in v0.59.0 (incremental sync)

---

### 6. WebDAV Connection Overhead

**Location:** `src/hei_datahub/infra/webdav_storage.py`

**Issue:**
- Creating new HTTP connection for each request
- TLS handshake overhead: ~100ms per connection
- 1000 requests = 100 seconds of overhead

**Profiling:**

```python
def download(dataset):
    # New connection every time
    client = httpx.Client()
    response = client.get(url)
    client.close()

# Connection + TLS: 100ms
# Download: 20ms
# Total: 120ms per dataset
```

**Mitigation:**

```python
# Connection pooling
_client_pool = None

def get_client():
    global _client_pool
    if _client_pool is None:
        _client_pool = httpx.Client(
            limits=httpx.Limits(max_connections=10),
            timeout=30.0,
        )
    return _client_pool

def download(dataset):
    client = get_client()  # Reuse connection
    response = client.get(url)

# Connection: 0ms (reused)
# Download: 20ms ✓
```

**Status:** ✅ Fixed in v0.58.0

---

## UI Hotspots

### 7. DataTable Re-renders

**Location:** `src/hei_datahub/ui/widgets/dataset_table.py`

**Issue:**
- Re-rendering entire table on every keystroke
- 1000 rows × 5 columns = 5000 cells
- Causes input lag

**Profiling:**

```python
class DatasetTable(DataTable):
    def on_input_changed(self, event):
        # Re-render entire table
        self.clear()
        results = search(event.value)
        for r in results:
            self.add_row(r.title, r.author, r.date, ...)

# Clear + add 1000 rows: 250ms
# → Input lag!
```

**Mitigation:**

```python
class DatasetTable(DataTable):
    def on_input_changed(self, event):
        # Debounce input
        self.set_timer(0.3, lambda: self._update_results(event.value))

    def _update_results(self, query):
        # Only update if query changed
        if query == self._last_query:
            return

        self._last_query = query

        # Update table
        results = search(query, limit=100)  # Limit results
        self._update_table(results)

# Debounced: User sees results after stopping typing
# Limited: Only render 100 rows
# Result: No lag ✓
```

**Status:** ✅ Fixed in v0.57.0

---

### 8. Synchronous Cloud Status Checks

**Location:** `src/hei_datahub/ui/views/home_view.py`

**Issue:**
- Checking cloud sync status on UI thread
- Blocks rendering for 2-3 seconds
- Poor startup experience

**Profiling:**

```python
class HomeView(Screen):
    def on_mount(self):
        # Blocking network call on UI thread
        sync_status = get_sync_status()  # 2,500ms
        self.update_status(sync_status)

# App freeze: 2,500ms
```

**Mitigation:**

```python
class HomeView(Screen):
    async def on_mount(self):
        # Show loading state
        self.show_loading()

        # Async status check
        sync_status = await get_sync_status_async()

        # Update UI
        self.hide_loading()
        self.update_status(sync_status)

# App responsive, status loads in background ✓
```

**Status:** ✅ Fixed in v0.59.0

---

## Database Hotspots

### 9. Missing Indexes

**Location:** `src/hei_datahub/infra/database.py`

**Issue:**
- Full table scan on `datasets_store.uuid`
- Slow lookups (50ms per query)

**Profiling:**

```sql
EXPLAIN QUERY PLAN
SELECT * FROM datasets_store WHERE uuid = 'abc123';

-- Result:
-- SCAN datasets_store  ← Full table scan!
```

**Mitigation:**

```sql
-- Add index
CREATE INDEX idx_datasets_uuid ON datasets_store(uuid);

EXPLAIN QUERY PLAN
SELECT * FROM datasets_store WHERE uuid = 'abc123';

-- Result:
-- SEARCH datasets_store USING INDEX idx_datasets_uuid ✓
```

**Performance:**
- Before: 50ms
- After: 2ms
- Improvement: 25x

**Status:** ✅ Fixed in v0.58.0

---

### 10. FTS5 Rebuild on Startup

**Location:** `src/hei_datahub/infra/index_service.py`

**Issue:**
- Checking FTS index integrity on every startup
- Rebuilding if mismatch detected
- Takes 5-10 seconds for 10,000 datasets

**Profiling:**

```python
def initialize():
    # Check integrity
    if not fts_index_valid():
        rebuild_fts_index()  # 8,000ms for 10k datasets

# Slow startup!
```

**Mitigation:**

```python
def initialize():
    # Quick validation
    if not quick_fts_check():
        # Only rebuild if clearly broken
        rebuild_fts_index()

    # Full validation in background
    asyncio.create_task(validate_fts_async())

def quick_fts_check():
    """Fast sanity check"""
    try:
        # Simple query
        execute("SELECT * FROM datasets_fts LIMIT 1")
        return True
    except:
        return False

# Startup: 200ms (quick check)
# Full validation: Background task
```

**Status:** ⚠️ Partially fixed in v0.59.0

---

## Memory Hotspots

### 11. Caching All Search Results

**Location:** `src/hei_datahub/services/cache.py`

**Issue:**
- Unbounded cache of search results
- Memory grows indefinitely
- 100 MB after 1000 searches

**Profiling:**

```python
_cache = {}  # Unbounded!

def search_cached(query: str):
    if query not in _cache:
        _cache[query] = search(query)
    return _cache[query]

# After 1000 unique queries:
# Cache size: 100 MB
```

**Mitigation:**

```python
from functools import lru_cache

@lru_cache(maxsize=128)  # Limit cache size
def search_cached(query: str):
    return search(query)

# Cache size: ~5 MB (128 recent queries) ✓
```

**Status:** ✅ Fixed in v0.58.0

---

## Summary

| Hotspot | Location | Impact | Status | Version |
|---------|----------|--------|--------|---------|
| FTS query compilation | fast_search.py | Medium | ✅ Fixed | 0.58.0 |
| Large result sets | fast_search.py | Medium | ✅ Fixed | 0.56.0 |
| Autocomplete rebuilds | autocomplete.py | High | ✅ Fixed | 0.59.0 |
| Serial downloads | sync.py | High | ✅ Fixed | 0.56.0 |
| Redundant cloud checks | sync.py | High | ✅ Fixed | 0.59.0 |
| Connection overhead | webdav_storage.py | Medium | ✅ Fixed | 0.58.0 |
| DataTable re-renders | dataset_table.py | Medium | ✅ Fixed | 0.57.0 |
| Sync cloud checks | home_view.py | Medium | ✅ Fixed | 0.59.0 |
| Missing indexes | database.py | High | ✅ Fixed | 0.58.0 |
| FTS startup rebuild | index_service.py | Medium | ⚠️ Partial | 0.59.0 |
| Unbounded cache | cache.py | Low | ✅ Fixed | 0.58.0 |

---

## Ongoing Monitoring

**Track new hotspots:**

```bash
# Run benchmarks regularly
make bench

# Profile on each release
python -m cProfile app.py
```

**Watch for regressions:**

```yaml
# CI performance tests
- name: Performance regression check
  run: pytest tests/performance/ --benchmark-compare
```

---

## Related Documentation

- **[Performance Overview](overview.md)** - Metrics and goals
- **[Profiling](profiling.md)** - Profiling techniques
- **[Optimization](optimization.md)** - Optimization strategies

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
