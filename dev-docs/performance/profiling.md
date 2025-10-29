# Performance Profiling

## Introduction

This document covers profiling tools, techniques, and best practices for analyzing Hei-DataHub performance.

---

## Profiling Tools

### Built-in Python Profilers

**cProfile:**
- Standard library profiler
- Low overhead
- Function-level granularity

**line_profiler:**
- Line-by-line profiling
- Higher overhead
- Detailed insights

**memory_profiler:**
- Memory usage tracking
- Line-by-line memory
- Detect memory leaks

---

## Function-Level Profiling

### Using cProfile

**Basic profiling:**

```bash
# Profile entire application
python -m cProfile -o profile.stats src/hei_datahub/cli/main.py search "test"

# View results
python -m pstats profile.stats
> sort cumtime
> stats 20
```

**In code:**

```python
import cProfile
import pstats

def profile_function():
    """Profile a specific function"""
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    from hei_datahub.services.fast_search import get_fast_search_service
    search = get_fast_search_service()
    results = search.search("machine learning")

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

# Output:
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        1    0.000    0.000    0.042    0.042 fast_search.py:45(search)
#      245    0.015    0.000    0.035    0.000 database.py:89(execute_query)
#      ...
```

---

### Decorator for Easy Profiling

```python
# src/hei_datahub/utils/profiling.py

import cProfile
import pstats
from functools import wraps
from io import StringIO

def profile(sort_by: str = 'cumulative', lines: int = 20):
    """Decorator to profile function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()

            # Print stats
            stream = StringIO()
            stats = pstats.Stats(profiler, stream=stream)
            stats.sort_stats(sort_by)
            stats.print_stats(lines)

            print(f"\n=== Profile: {func.__name__} ===")
            print(stream.getvalue())

            return result

        return wrapper
    return decorator

# Usage
from hei_datahub.utils.profiling import profile

@profile(sort_by='cumulative', lines=10)
def expensive_function():
    """This function will be profiled"""
    # ... code ...
    pass
```

---

## Line-Level Profiling

### Using line_profiler

**Install:**

```bash
uv add --dev line_profiler
```

**Profile specific functions:**

```python
# Add @profile decorator (no import needed)
@profile
def search_datasets(query: str) -> list[Dataset]:
    """Search with line-level profiling"""
    # Parse query
    tokens = tokenize(query)  # Line 1

    # Execute search
    sql = build_query(tokens)  # Line 2
    results = execute_query(sql)  # Line 3

    # Rank results
    ranked = rank_results(results)  # Line 4

    return ranked  # Line 5
```

**Run profiler:**

```bash
kernprof -l -v src/hei_datahub/cli/main.py search "test"

# Output:
# Line #      Hits         Time  Per Hit   % Time  Line Contents
# ==============================================================
#      1         1         50.0     50.0      2.0      tokens = tokenize(query)
#      2         1        120.0    120.0      4.8      sql = build_query(tokens)
#      3         1       2100.0   2100.0     84.0      results = execute_query(sql)
#      4         1        220.0    220.0      8.8      ranked = rank_results(results)
#      5         1          5.0      5.0      0.2      return ranked
```

**Conclusion:** Line 3 (execute_query) is the bottleneck

---

## Memory Profiling

### Using memory_profiler

**Install:**

```bash
uv add --dev memory_profiler
```

**Profile memory usage:**

```python
from memory_profiler import profile

@profile
def load_datasets() -> list[Dataset]:
    """Load datasets with memory profiling"""
    datasets = []

    # Load from database
    rows = fetch_all_rows()  # Line 1

    # Convert to objects
    for row in rows:  # Line 2
        dataset = Dataset.from_row(row)  # Line 3
        datasets.append(dataset)  # Line 4

    return datasets  # Line 5
```

**Run:**

```bash
python -m memory_profiler script.py

# Output:
# Line #    Mem usage    Increment   Line Contents
# ================================================
#      1     42.5 MiB      0.0 MiB       rows = fetch_all_rows()
#      2     42.5 MiB      0.0 MiB       for row in rows:
#      3     65.2 MiB     22.7 MiB           dataset = Dataset.from_row(row)
#      4     68.1 MiB      2.9 MiB           datasets.append(dataset)
#      5     68.1 MiB      0.0 MiB       return datasets
```

**Conclusion:** Line 3 (Dataset.from_row) allocates 22.7 MB

---

### Detecting Memory Leaks

**Using tracemalloc:**

```python
import tracemalloc

def track_memory_leaks():
    """Track memory allocations"""
    tracemalloc.start()

    # Take snapshot before
    snapshot1 = tracemalloc.take_snapshot()

    # Run code
    for i in range(1000):
        search("test query")

    # Take snapshot after
    snapshot2 = tracemalloc.take_snapshot()

    # Compare
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    print("Top 10 memory increases:")
    for stat in top_stats[:10]:
        print(stat)

# Output:
# src/hei_datahub/services/cache.py:45: size=2048 KiB (+2048 KiB), count=500 (+500)
# → Cache is growing without bounds!
```

---

## Async Profiling

### Profiling Async Code

**Using yappi:**

```bash
uv add --dev yappi
```

**Profile async functions:**

```python
import yappi

def profile_async():
    """Profile async code"""
    yappi.set_clock_type("wall")  # Use wall time for async
    yappi.start()

    # Run async code
    import asyncio
    asyncio.run(sync_all_datasets())

    yappi.stop()

    # Print stats
    stats = yappi.get_func_stats()
    stats.sort("totaltime", "desc")
    stats.print_all()

# Output:
# name                                  ncall  tsub      ttot      tavg
# ======================================================================
# sync_all_datasets                         1  0.50000  15.20000  15.20000
# download_dataset (coroutine)           100  12.30000  14.50000   0.14500
# upload_dataset (coroutine)              10   0.80000   0.90000   0.09000
```

---

## UI Profiling

### Textual Performance

**Built-in profiler:**

```python
from textual.app import App

class MiniDataHubApp(App):
    def on_mount(self) -> None:
        # Enable profiling
        self.profiler.start()

    def action_show_profile(self) -> None:
        """Show profiling results"""
        stats = self.profiler.get_stats()
        self.push_screen(ProfilerScreen(stats))
```

**Measure render time:**

```python
import time
from textual.widget import Widget

class ProfiledWidget(Widget):
    def render(self) -> RenderableType:
        start = time.perf_counter()

        # Render content
        content = self._render_content()

        duration = (time.perf_counter() - start) * 1000
        if duration > 16:  # > 1 frame at 60 FPS
            self.log.warning(f"Slow render: {duration:.2f}ms")

        return content
```

---

## Database Profiling

### SQLite Query Analysis

**EXPLAIN QUERY PLAN:**

```python
def analyze_query(query: str):
    """Analyze SQL query performance"""
    conn = get_db_connection()

    # Get query plan
    plan = conn.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()

    print("Query Plan:")
    for row in plan:
        print(f"  {row}")

    # Check if using index
    plan_str = str(plan)
    if "SCAN" in plan_str:
        print("⚠️  Warning: Full table scan!")
    if "USING INDEX" in plan_str:
        print("✓ Using index")

# Example
analyze_query("""
    SELECT * FROM datasets_fts
    WHERE datasets_fts MATCH 'machine learning'
""")

# Output:
# Query Plan:
#   (3, 0, 0, 'SCAN datasets_fts VIRTUAL TABLE INDEX 1:')
# ✓ Using FTS index
```

---

### Track Query Time

```python
import sqlite3
import time

class ProfilingConnection(sqlite3.Connection):
    """SQLite connection with query profiling"""

    def execute(self, sql: str, *args):
        start = time.perf_counter()
        result = super().execute(sql, *args)
        duration = (time.perf_counter() - start) * 1000

        if duration > 100:  # Log slow queries
            print(f"Slow query ({duration:.2f}ms): {sql[:100]}")

        return result

# Usage
conn = sqlite3.connect('data.db', factory=ProfilingConnection)
```

---

## Network Profiling

### WebDAV Request Timing

```python
import time
import httpx

class TimedHTTPTransport(httpx.HTTPTransport):
    """HTTP transport with request timing"""

    def handle_request(self, request):
        start = time.perf_counter()
        response = super().handle_request(request)
        duration = (time.perf_counter() - start) * 1000

        print(f"{request.method} {request.url}: {duration:.0f}ms")

        return response

# Usage
client = httpx.Client(transport=TimedHTTPTransport())
```

---

## Profiling Best Practices

### 1. Profile in Production-Like Environment

```bash
# ✅ GOOD: Production settings
export HEI_DATAHUB_LOG_LEVEL=INFO
python -m cProfile script.py

# ❌ BAD: Debug settings (different performance)
export HEI_DATAHUB_LOG_LEVEL=DEBUG
python -m cProfile script.py
```

---

### 2. Isolate What You're Profiling

```python
# ✅ GOOD: Profile specific function
@profile
def search_datasets(query: str):
    return perform_search(query)

# ❌ BAD: Profile entire app (too much noise)
@profile
def main():
    app = MiniDataHubApp()
    app.run()
```

---

### 3. Use Representative Data

```python
# ✅ GOOD: Realistic dataset size
populate_database(10_000)  # Typical usage
profile_search()

# ❌ BAD: Tiny dataset (not realistic)
populate_database(10)
profile_search()
```

---

### 4. Run Multiple Iterations

```python
# ✅ GOOD: Average of multiple runs
import statistics

times = []
for _ in range(100):
    start = time.perf_counter()
    search("test")
    times.append(time.perf_counter() - start)

print(f"Mean: {statistics.mean(times):.3f}s")
print(f"Stdev: {statistics.stdev(times):.3f}s")

# ❌ BAD: Single run (unreliable)
start = time.perf_counter()
search("test")
print(f"Time: {time.perf_counter() - start:.3f}s")
```

---

## Profiling Workflow

### 1. Identify Slow Operation

```bash
# User report: "Search is slow"
# Reproduce issue
hei-datahub search "machine learning"
# → Takes 2 seconds (too slow!)
```

---

### 2. Profile with cProfile

```bash
python -m cProfile -o profile.stats -m hei_datahub.cli.main search "machine learning"

python -m pstats profile.stats
> sort cumtime
> stats 20

# Identifies: execute_query() takes 80% of time
```

---

### 3. Line-Level Profiling

```python
@profile
def execute_query(sql: str):
    # Line-by-line analysis
    ...

kernprof -l -v search_script.py

# Identifies: SQL compilation is slow
```

---

### 4. Optimize

```python
# Before: Compile SQL every time
def search(query):
    sql = f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{query}'"
    return execute(sql)

# After: Use prepared statement
_prepared_search = None

def search(query):
    global _prepared_search
    if _prepared_search is None:
        _prepared_search = prepare("SELECT * FROM datasets_fts WHERE datasets_fts MATCH ?")
    return _prepared_search.execute(query)
```

---

### 5. Verify Improvement

```bash
# Re-profile
python -m cProfile search_script.py

# Compare results
# Before: 2.0s
# After: 0.05s
# → 40x improvement! ✅
```

---

## Related Documentation

- **[Performance Overview](overview.md)** - Metrics and benchmarks
- **[Hotspots](hotspots.md)** - Known bottlenecks
- **[Optimization](optimization.md)** - Optimization strategies

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
