# Advanced: Performance Optimization

**Learning Goal**: Master performance optimization techniques for Hei-DataHub.

By the end of this page, you'll:
- Measure performance bottlenecks
- Optimize database queries
- Implement caching strategies
- Reduce UI lag
- Profile Python code
- Benchmark improvements

---

## Performance Goals

**Target Metrics:**

| Operation | Target | Critical |
|-----------|--------|----------|
| **Search query** | <50ms | <100ms |
| **Index build** | <1s | <5s |
| **Screen render** | <16ms (60 FPS) | <33ms (30 FPS) |
| **Dataset load** | <100ms | <500ms |
| **Autocomplete** | <10ms | <50ms |

---

## Measuring Performance

### 1. Python `time` Module

**Basic timing:**

```python
import time

start = time.time()
# ... operation ...
elapsed = (time.time() - start) * 1000  # Convert to ms
print(f"Operation took {elapsed:.2f}ms")
```

---

### 2. Context Manager for Timing

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(name: str):
    """Time a block of code."""
    start = time.time()
    yield
    elapsed = (time.time() - start) * 1000
    print(f"{name}: {elapsed:.2f}ms")


# Usage
with timer("Search query"):
    results = search_datasets("climate")
```

---

### 3. Profiling with cProfile

**Full program profiling:**

```bash
# Profile the app
python -m cProfile -o profile.stats -m mini_datahub

# Analyze results
python -m pstats profile.stats
> sort cumtime
> stats 20  # Show top 20 functions
```

**Output:**

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      200    0.050    0.000    2.500    0.013 search.py:45(_simple_fts_search)
     1000    0.100    0.000    1.800    0.002 index.py:20(upsert_dataset)
      500    0.030    0.000    1.200    0.002 db.py:10(get_connection)
```

---

### 4. Line-by-Line Profiling

**Install:**

```bash
pip install line_profiler
```

**Profile specific function:**

```python
from line_profiler import LineProfiler

def profile_search():
    """Profile search function."""
    profiler = LineProfiler()
    profiler.add_function(search_datasets)
    profiler.enable()

    # Run code
    search_datasets("climate")

    profiler.disable()
    profiler.print_stats()
```

---

## Database Optimization

### 1. Use Prepared Statements

**❌ Bad (vulnerable + slow):**

```python
query = f"SELECT * FROM datasets WHERE id = '{dataset_id}'"
cursor.execute(query)
```

**✅ Good (safe + fast):**

```python
query = "SELECT * FROM datasets_store WHERE id = ?"
cursor.execute(query, (dataset_id,))
```

**Why faster?** SQLite can cache the query plan.

---

### 2. Batch Inserts

**❌ Bad (slow):**

```python
for dataset_id in dataset_ids:
    conn.execute("INSERT INTO ...", (...))
    conn.commit()  # Commit per insert
```

**✅ Good (fast):**

```python
conn = get_connection()
try:
    for dataset_id in dataset_ids:
        conn.execute("INSERT INTO ...", (...))
    conn.commit()  # Single commit
finally:
    conn.close()
```

**Speedup:** 10-100x faster!

---

### 3. Index Columns

**Add index for frequently queried columns:**

```sql
-- Add index on source column
CREATE INDEX IF NOT EXISTS idx_source
ON datasets_store((json_extract(payload, '$.source')));

-- Add index on updated_at
CREATE INDEX IF NOT EXISTS idx_updated
ON datasets_store(updated_at);
```

**Query optimization:**

```sql
-- Slow (full table scan)
SELECT * FROM datasets_store
WHERE json_extract(payload, '$.source') = 'github';

-- Fast (uses index)
SELECT * FROM datasets_store
WHERE json_extract(payload, '$.source') = 'github'
AND updated_at > '2025-01-01';  -- Index hint
```

---

### 4. EXPLAIN QUERY PLAN

**Analyze query performance:**

```sql
EXPLAIN QUERY PLAN
SELECT * FROM datasets_fts
WHERE datasets_fts MATCH 'climate'
ORDER BY bm25(datasets_fts)
LIMIT 50;
```

**Output:**

```
QUERY PLAN
`--SCAN datasets_fts VIRTUAL TABLE INDEX 0:MATCH
```

**Good:** Using FTS index (not table scan).

---

## Caching Strategies

### 1. In-Memory Query Cache

**Implementation:**

```python
from typing import Dict, Tuple
import time

class SearchService:
    """Search service with query caching."""

    def __init__(self):
        self._query_cache: Dict[str, Tuple[float, list]] = {}
        self._cache_ttl = 60.0  # 60 seconds

    def search(self, query: str, limit: int = 50) -> list:
        """Search with caching."""
        # Check cache
        cache_key = f"{query}:{limit}"
        if cache_key in self._query_cache:
            timestamp, results = self._query_cache[cache_key]

            # Check if still valid
            if time.time() - timestamp < self._cache_ttl:
                return results

        # Cache miss - perform search
        results = self._perform_search(query, limit)

        # Store in cache
        self._query_cache[cache_key] = (time.time(), results)

        return results

    def clear_cache(self) -> None:
        """Clear query cache."""
        self._query_cache.clear()
```

---

### 2. LRU Cache (Least Recently Used)

**Python built-in:**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_dataset_metadata(dataset_id: str) -> dict:
    """Get dataset metadata (cached)."""
    # This result is cached
    return read_dataset(dataset_id)


# Clear cache
get_dataset_metadata.cache_clear()

# Get cache stats
info = get_dataset_metadata.cache_info()
print(f"Hits: {info.hits}, Misses: {info.misses}")
```

---

### 3. Disk-Based Cache

**Using SQLite as cache:**

```python
from pathlib import Path
import sqlite3
import json
import time

class DiskCache:
    """Simple disk-based cache using SQLite."""

    def __init__(self, cache_path: Path, ttl: int = 3600):
        self.cache_path = cache_path
        self.ttl = ttl
        self._init_db()

    def _init_db(self) -> None:
        """Initialize cache database."""
        conn = sqlite3.connect(self.cache_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def get(self, key: str) -> any:
        """Get value from cache."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.execute(
            "SELECT value, timestamp FROM cache WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        value, timestamp = row

        # Check if expired
        if time.time() - timestamp > self.ttl:
            self.delete(key)
            return None

        return json.loads(value)

    def set(self, key: str, value: any) -> None:
        """Set value in cache."""
        conn = sqlite3.connect(self.cache_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO cache (key, value, timestamp)
            VALUES (?, ?, ?)
            """,
            (key, json.dumps(value), time.time())
        )
        conn.commit()
        conn.close()

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        conn = sqlite3.connect(self.cache_path)
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
        conn.close()
```

---

## UI Performance

### 1. Debouncing User Input

**Problem:** Search on every keystroke is expensive.

**Solution:** Wait for typing to pause.

```python
from textual.widgets import Input
import asyncio

class HomeScreen(Screen):
    """Home screen with debounced search."""

    def __init__(self):
        super().__init__()
        self._search_timer: Optional[asyncio.Task] = None
        self._debounce_delay = 0.3  # 300ms

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes (debounced)."""
        # Cancel previous timer
        if self._search_timer:
            self._search_timer.cancel()

        # Start new timer
        self._search_timer = asyncio.create_task(
            self._debounced_search(event.value)
        )

    async def _debounced_search(self, query: str) -> None:
        """Perform search after delay."""
        try:
            await asyncio.sleep(self._debounce_delay)

            # Perform search
            results = search_datasets(query)
            self.update_results(results)

        except asyncio.CancelledError:
            # Timer was cancelled (user still typing)
            pass
```

---

### 2. Lazy Loading

**Load data only when visible:**

```python
from textual.widgets import DataTable

class DatasetTable(DataTable):
    """Table with lazy loading."""

    def __init__(self):
        super().__init__()
        self._page_size = 50
        self._current_page = 0
        self._total_items = 0

    def load_page(self, page: int) -> None:
        """Load a specific page of results."""
        offset = page * self._page_size

        # Load only this page
        results = search_datasets(
            query=self.query,
            limit=self._page_size,
            offset=offset
        )

        # Update table
        self.clear()
        for result in results:
            self.add_row(result["id"], result["name"])

    def on_scroll_end(self) -> None:
        """Load next page when scrolled to end."""
        if self._current_page * self._page_size < self._total_items:
            self._current_page += 1
            self.load_page(self._current_page)
```

---

### 3. Virtual Scrolling

**Render only visible rows:**

```python
class VirtualList(Widget):
    """List that only renders visible items."""

    def __init__(self, items: list):
        super().__init__()
        self.items = items
        self.scroll_offset = 0
        self.visible_count = 20  # Show 20 items at a time

    def render(self) -> RenderResult:
        """Render only visible items."""
        # Calculate visible range
        start = self.scroll_offset
        end = min(start + self.visible_count, len(self.items))

        # Render only visible items
        visible_items = self.items[start:end]

        return "\n".join(str(item) for item in visible_items)
```

---

## Async Operations

### 1. Async I/O

**Run I/O operations asynchronously:**

```python
import asyncio
from pathlib import Path

async def load_datasets_async() -> list:
    """Load all datasets asynchronously."""
    dataset_ids = list_datasets()

    # Load all datasets concurrently
    tasks = [
        asyncio.to_thread(read_dataset, dataset_id)
        for dataset_id in dataset_ids
    ]

    results = await asyncio.gather(*tasks)

    return [r for r in results if r is not None]


# Usage in Textual
async def on_mount(self) -> None:
    """Load datasets when screen mounts."""
    datasets = await load_datasets_async()
    self.update_table(datasets)
```

---

### 2. Background Tasks

**Run expensive operations in background:**

```python
class HomeScreen(Screen):
    """Home screen with background refresh."""

    def on_mount(self) -> None:
        """Start background refresh task."""
        self.set_interval(60.0, self.refresh_data)

    async def refresh_data(self) -> None:
        """Refresh data in background."""
        # Run in worker thread (doesn't block UI)
        results = await self.run_worker(
            lambda: search_datasets(self.current_query)
        )

        # Update UI (runs in main thread)
        self.update_results(results)
```

---

## Benchmarking

### Create Benchmark Suite

**File:** `bench/search_performance_bench.py`

```python
#!/usr/bin/env python3
"""Performance benchmark for search system."""
import time
import statistics
import tempfile
from pathlib import Path

from mini_datahub.services.index_service import IndexService


def benchmark_search_latency():
    """Benchmark search query latency."""
    print("=" * 60)
    print("BENCHMARK: Search Latency")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "bench_index.db"
        index = IndexService(db_path=db_path)

        # Create test data
        items = []
        for i in range(10000):
            items.append({
                "path": f"dataset-{i:05d}",
                "name": f"Dataset {i}",
                "project": f"project-{i % 100}",
                "tags": f"tag-{i % 50}",
                "description": f"Description {i}",
                "is_remote": False,
            })

        index.bulk_upsert(items)

        # Benchmark queries
        queries = ["climate", "data", "project-50", "tag-10"]
        latencies = []

        for query in queries:
            times = []

            # Run 100 queries
            for _ in range(100):
                start = time.time()
                index.search(query_text=query)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)

            # Calculate percentiles
            p50 = statistics.median(times)
            p95 = statistics.quantiles(times, n=20)[18]  # 95th percentile
            p99 = statistics.quantiles(times, n=100)[98]  # 99th percentile

            latencies.append((query, p50, p95, p99))

        # Print results
        print(f"{'Query':<20} {'p50':>8} {'p95':>8} {'p99':>8}")
        print("-" * 50)
        for query, p50, p95, p99 in latencies:
            print(f"{query:<20} {p50:>7.2f}ms {p95:>7.2f}ms {p99:>7.2f}ms")

        # Assertions
        for query, p50, p95, p99 in latencies:
            assert p50 < 50, f"p50 too slow: {p50:.2f}ms for '{query}'"
            assert p95 < 100, f"p95 too slow: {p95:.2f}ms for '{query}'"

    print("✅ PASS: All queries <50ms (p50), <100ms (p95)\n")


if __name__ == "__main__":
    benchmark_search_latency()
```

**Run:**

```bash
python bench/search_performance_bench.py
```

**Output:**

```
============================================================
BENCHMARK: Search Latency
============================================================
Query                     p50      p95      p99
--------------------------------------------------
climate                 12.50ms  18.30ms  22.10ms
data                     8.20ms  14.50ms  19.80ms
project-50              10.10ms  16.20ms  20.50ms
tag-10                   9.80ms  15.10ms  18.90ms
✅ PASS: All queries <50ms (p50), <100ms (p95)
```

---

## Memory Optimization

### 1. Use Generators

**❌ Bad (loads everything into memory):**

```python
def list_all_datasets() -> list:
    """List all datasets."""
    datasets = []
    for dataset_id in list_datasets():
        metadata = read_dataset(dataset_id)
        datasets.append(metadata)
    return datasets  # Returns huge list
```

**✅ Good (yields one at a time):**

```python
def iter_datasets():
    """Iterate over datasets."""
    for dataset_id in list_datasets():
        metadata = read_dataset(dataset_id)
        yield metadata  # Yields one at a time


# Usage
for dataset in iter_datasets():
    process(dataset)  # Only one in memory at a time
```

---

### 2. Clear Unused References

```python
class SearchService:
    """Search service."""

    def search(self, query: str) -> list:
        """Search datasets."""
        # Large temporary data
        raw_results = self._fetch_raw_results(query)

        # Process results
        processed = self._process_results(raw_results)

        # Clear reference to raw data
        del raw_results

        return processed
```

---

## Performance Checklist

### Database

- [ ] Use prepared statements
- [ ] Batch inserts/updates
- [ ] Add indexes on frequently queried columns
- [ ] Run EXPLAIN QUERY PLAN
- [ ] Use FTS5 for full-text search
- [ ] Enable WAL mode for concurrency

---

### Caching

- [ ] Cache query results (in-memory)
- [ ] Use LRU cache for expensive functions
- [ ] Disk cache for large datasets
- [ ] Set appropriate TTL
- [ ] Clear cache when data changes

---

### UI

- [ ] Debounce user input (300ms)
- [ ] Lazy load data
- [ ] Virtual scrolling for large lists
- [ ] Run I/O in background
- [ ] Show loading indicators

---

### Code

- [ ] Use generators for large datasets
- [ ] Profile hot paths
- [ ] Minimize allocations in loops
- [ ] Clear unused references
- [ ] Use appropriate data structures

---

## What You've Learned

✅ **Measuring performance** — time, cProfile, line_profiler
✅ **Database optimization** — Prepared statements, batching, indexes
✅ **Caching strategies** — In-memory, LRU, disk cache
✅ **UI performance** — Debouncing, lazy loading, virtual scrolling
✅ **Async operations** — Background tasks, async I/O
✅ **Benchmarking** — Test suites, percentiles
✅ **Memory optimization** — Generators, clearing references

---

## Next Steps

Now let's explore debugging techniques and tools.

**Next:** [Debugging Strategies](03-debugging.md)

---

## Further Reading

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [SQLite Performance Tuning](https://www.sqlite.org/optoverview.html)
- [cProfile Documentation](https://docs.python.org/3/library/profile.html)
- [Asyncio Best Practices](https://docs.python.org/3/library/asyncio-task.html)
