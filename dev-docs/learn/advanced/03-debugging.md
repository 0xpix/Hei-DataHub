# Advanced: Debugging Strategies

**Learning Goal**: Master debugging techniques for Hei-DataHub development.

By the end of this page, you'll:
- Configure logging effectively
- Debug TUI applications
- Use Python debuggers
- Handle exceptions gracefully
- Debug performance issues
- Troubleshoot common problems

---

## Logging Setup

### 1. Configure Logging

**File:** `src/mini_datahub/logging_config.py`

```python
"""
Logging configuration for Hei-DataHub.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_style: str = "detailed"
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file to write logs to
        format_style: "simple" or "detailed"
    """
    # Define formats
    formats = {
        "simple": "%(levelname)s: %(message)s",
        "detailed": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    }

    log_format = formats.get(format_style, formats["detailed"])

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Silence noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
```

---

### 2. Use Logging in Code

**File:** `src/mini_datahub/services/search.py`

```python
"""
Search service with logging.
"""
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Search service with debugging support."""

    def search(self, query: str, limit: int = 50) -> list:
        """Search datasets."""
        logger.debug(f"Starting search: query={query!r}, limit={limit}")

        try:
            results = self._perform_search(query, limit)
            logger.info(f"Search completed: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise
```

**Logging levels:**

- **DEBUG**: Detailed diagnostic info (e.g., "Parsed query: owner:john")
- **INFO**: General informational messages (e.g., "Indexed 100 datasets")
- **WARNING**: Warning messages (e.g., "Cache miss for query")
- **ERROR**: Error messages (e.g., "Failed to connect to database")
- **CRITICAL**: Critical errors (e.g., "Database corrupted")

---

### 3. Enable Debug Logging

**From CLI:**

```bash
# Set via environment variable
export HEI_DATAHUB_LOG_LEVEL=DEBUG
python -m mini_datahub

# Or create config file
mkdir -p ~/.config/hei-datahub
cat > ~/.config/hei-datahub/logging.yaml << EOF
log_level: DEBUG
log_file: ~/.local/share/hei-datahub/debug.log
EOF
```

**In code:**

```python
from mini_datahub.logging_config import setup_logging

# Enable debug logging
setup_logging(
    level="DEBUG",
    log_file=Path.home() / ".local/share/hei-datahub/debug.log",
    format_style="detailed"
)
```

---

## Debugging TUI Apps

### 1. Textual DevTools

**Enable built-in debugger:**

```python
from textual.app import App

class HeiDataHub(App):
    """Main app with debug mode."""

    def __init__(self):
        super().__init__()
        self.debug = True  # Enable debug mode


# Run with devtools
if __name__ == "__main__":
    app = HeiDataHub()
    app.run(devtools=True)
```

**This opens a browser at `http://localhost:8081` showing:**

- DOM tree (widget hierarchy)
- CSS styles applied
- Live logs
- Event stream

---

### 2. Debug Console

**Add debug console binding:**

```python
from textual.screen import Screen
from textual.binding import Binding

class HomeScreen(Screen):
    """Home screen with debug console."""

    BINDINGS = [
        Binding(":", "debug_console", "Debug", show=False),
    ]

    def action_debug_console(self) -> None:
        """Open debug console."""
        # Log current state
        self.log(f"Current query: {self.query_input.value}")
        self.log(f"Results count: {self.results_table.row_count}")
        self.log(f"Focused widget: {self.focused}")
```

**Access console:** Press `:` in the TUI.

---

### 3. Logging to File (Not Terminal)

**Problem:** TUI overwrites terminal, can't see `print()`.

**Solution:** Log to file.

```python
import logging
from pathlib import Path

# Setup file logging
log_file = Path.home() / ".local/share/hei-datahub/debug.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# Now you can log from anywhere
logger.debug("Screen mounted")
logger.info(f"Search query: {query}")
```

**View logs:**

```bash
tail -f ~/.local/share/hei-datahub/debug.log
```

---

### 4. Inspect Widget Tree

**Print widget hierarchy:**

```python
def action_debug_tree(self) -> None:
    """Print widget tree to log."""
    self.log(self.tree)
```

**Output:**

```
<HomeScreen id='home'>
  <Container id='search-container'>
    <Input id='search-input'>
    <DataTable id='results-table'>
  <Footer>
```

---

## Python Debugger (pdb)

### 1. Set Breakpoint

**In code:**

```python
def search_datasets(query: str) -> list:
    """Search datasets."""
    # Set breakpoint
    breakpoint()  # Python 3.7+

    # Or use pdb directly
    import pdb; pdb.set_trace()

    results = perform_search(query)
    return results
```

**Run and debug:**

```bash
python -m mini_datahub
```

**When breakpoint hits:**

```
> /home/user/src/mini_datahub/services/search.py(12)search_datasets()
-> results = perform_search(query)
(Pdb)
```

---

### 2. pdb Commands

| Command | Description |
|---------|-------------|
| `l` | List source code around current line |
| `n` | Next line (step over) |
| `s` | Step into function |
| `c` | Continue execution |
| `p <expr>` | Print expression |
| `pp <expr>` | Pretty-print expression |
| `w` | Where am I? (stack trace) |
| `u` | Move up stack frame |
| `d` | Move down stack frame |
| `q` | Quit debugger |

---

### 3. Conditional Breakpoints

```python
def search_datasets(query: str) -> list:
    """Search datasets."""
    # Only break if query contains "climate"
    if "climate" in query:
        breakpoint()

    results = perform_search(query)
    return results
```

---

### 4. Post-Mortem Debugging

**Debug after exception:**

```python
import pdb

try:
    results = search_datasets(query)
except Exception:
    pdb.post_mortem()  # Opens debugger at exception
```

---

## VS Code Debugger

### 1. Configure Launch Settings

**File:** `.vscode/launch.json`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Hei-DataHub",
      "type": "python",
      "request": "launch",
      "module": "mini_datahub",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v",
        "--tb=short"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Debug Current Test",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

---

### 2. Set Breakpoints

**In VS Code:**

1. Click left gutter to set breakpoint (red dot)
2. Press `F5` to start debugging
3. Use debug toolbar to step through code

---

## Exception Handling

### 1. Graceful Error Handling

**❌ Bad (crashes app):**

```python
def search_datasets(query: str) -> list:
    """Search datasets."""
    conn = sqlite3.connect(DB_PATH)
    results = conn.execute("SELECT * FROM datasets_fts WHERE ...").fetchall()
    return results
```

**✅ Good (handles errors):**

```python
import logging

logger = logging.getLogger(__name__)


def search_datasets(query: str) -> list:
    """Search datasets."""
    try:
        conn = sqlite3.connect(DB_PATH)
        results = conn.execute("SELECT * FROM datasets_fts WHERE ...").fetchall()
        return results

    except sqlite3.OperationalError as e:
        logger.error(f"Database error: {e}")
        return []  # Return empty results

    except Exception as e:
        logger.exception(f"Unexpected error in search: {e}")
        raise  # Re-raise unexpected errors

    finally:
        if conn:
            conn.close()
```

---

### 2. Custom Exceptions

```python
class HeiDataHubError(Exception):
    """Base exception for Hei-DataHub."""
    pass


class SearchError(HeiDataHubError):
    """Raised when search fails."""
    pass


class IndexCorruptedError(HeiDataHubError):
    """Raised when index is corrupted."""
    pass


# Usage
def search_datasets(query: str) -> list:
    """Search datasets."""
    if not query:
        raise SearchError("Query cannot be empty")

    try:
        return perform_search(query)
    except sqlite3.DatabaseError as e:
        raise IndexCorruptedError(f"Index corrupted: {e}") from e
```

---

### 3. Context Managers for Cleanup

```python
from contextlib import contextmanager
import sqlite3

@contextmanager
def get_db_connection(db_path):
    """Get database connection with automatic cleanup."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


# Usage
with get_db_connection(DB_PATH) as conn:
    results = conn.execute("SELECT ...").fetchall()
# Connection automatically closed
```

---

## Debugging Performance Issues

### 1. Add Timing Logs

```python
import time
import logging

logger = logging.getLogger(__name__)


def search_datasets(query: str) -> list:
    """Search datasets with timing."""
    start = time.time()

    try:
        results = perform_search(query)

        elapsed = (time.time() - start) * 1000
        logger.debug(f"Search took {elapsed:.2f}ms for query: {query!r}")

        return results

    except Exception as e:
        elapsed = (time.time() - start) * 1000
        logger.error(f"Search failed after {elapsed:.2f}ms: {e}")
        raise
```

---

### 2. Profile Slow Functions

```python
import cProfile
import pstats

def profile_search():
    """Profile search function."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run code
    search_datasets("climate")

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime')
    stats.print_stats(20)  # Top 20 functions
```

---

### 3. Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler -m mini_datahub
```

**In code:**

```python
from memory_profiler import profile

@profile
def load_all_datasets():
    """Load all datasets (memory profiled)."""
    datasets = []
    for dataset_id in list_datasets():
        datasets.append(read_dataset(dataset_id))
    return datasets
```

---

## Common Issues and Solutions

### Issue 1: TUI Not Responding

**Symptoms:** App freezes, no keyboard input.

**Debug:**

```python
import logging

logger = logging.getLogger(__name__)


class HomeScreen(Screen):
    """Home screen with debug logging."""

    async def on_key(self, event: events.Key) -> None:
        """Log all key events."""
        logger.debug(f"Key pressed: {event.key}")

        # Your key handling code
        ...
```

**Common causes:**

- Blocking operation in UI thread
- Event handler not calling `super()` or preventing default
- Focus stuck on non-interactive widget

---

### Issue 2: Search Returns No Results

**Debug checklist:**

```python
def debug_search(query: str) -> None:
    """Debug search pipeline."""
    logger.debug(f"1. Raw query: {query!r}")

    # Check query parsing
    parsed = parse_query(query)
    logger.debug(f"2. Parsed query: {parsed}")

    # Check index exists
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM datasets_fts").fetchone()[0]
    logger.debug(f"3. Items in index: {count}")

    # Check FTS query
    fts_query = build_fts_query(parsed)
    logger.debug(f"4. FTS query: {fts_query}")

    # Run query
    results = conn.execute(
        "SELECT * FROM datasets_fts WHERE datasets_fts MATCH ?",
        (fts_query,)
    ).fetchall()
    logger.debug(f"5. Raw results: {len(results)} rows")
```

---

### Issue 3: Import Errors

**Symptoms:** `ModuleNotFoundError` or `ImportError`.

**Debug:**

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check if module is installed
python -c "import mini_datahub; print(mini_datahub.__file__)"

# Install in development mode
pip install -e .
```

---

### Issue 4: Configuration Not Loaded

**Debug:**

```python
from mini_datahub.infra.config_paths import get_config_path

config_path = get_config_path()
print(f"Looking for config at: {config_path}")
print(f"Exists: {config_path.exists()}")

if config_path.exists():
    with open(config_path) as f:
        print(f"Contents:\n{f.read()}")
```

---

## Testing Strategies

### 1. Unit Tests with pytest

**File:** `tests/unit/test_search.py`

```python
"""
Unit tests for search service.
"""
import pytest
from mini_datahub.services.search import SearchService


@pytest.fixture
def search_service():
    """Create search service for testing."""
    return SearchService()


def test_simple_search(search_service):
    """Test simple text search."""
    results = search_service.search("climate")

    assert len(results) > 0
    assert all("climate" in r["name"].lower() for r in results)


def test_field_search(search_service):
    """Test field-specific search."""
    results = search_service.search("owner:john")

    assert len(results) > 0
    assert all(r["owner"] == "john" for r in results)


def test_empty_query(search_service):
    """Test empty query returns all results."""
    results = search_service.search("")

    assert len(results) > 0
```

---

### 2. Integration Tests

**File:** `tests/integration/test_search_flow.py`

```python
"""
Integration tests for search flow.
"""
import tempfile
from pathlib import Path

from mini_datahub.services.index_service import IndexService
from mini_datahub.services.search import SearchService


def test_end_to_end_search():
    """Test complete search flow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Create index
        index = IndexService(db_path=db_path)

        # Add test data
        index.upsert_item(
            path="dataset-1",
            name="Climate Data",
            project="research",
            tags="climate temperature",
            description="Temperature measurements",
            is_remote=False,
        )

        # Search
        search = SearchService(db_path=db_path)
        results = search.search("climate")

        # Verify
        assert len(results) == 1
        assert results[0]["name"] == "Climate Data"
```

---

### 3. Run Tests with Coverage

```bash
# Install pytest and coverage
pip install pytest pytest-cov

# Run tests with coverage
pytest tests/ --cov=mini_datahub --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Debug Mode Checklist

When debugging an issue:

- [ ] Enable DEBUG logging
- [ ] Log to file (not terminal for TUI)
- [ ] Add timing logs for performance
- [ ] Use pdb/breakpoints strategically
- [ ] Check exception messages
- [ ] Verify configuration loaded
- [ ] Test in isolation (unit tests)
- [ ] Check database state
- [ ] Review recent changes (git diff)
- [ ] Read stack trace carefully

---

## What You've Learned

✅ **Logging setup** — Configure levels, handlers, formatters
✅ **TUI debugging** — DevTools, debug console, file logging
✅ **Python debugger** — pdb commands, breakpoints, post-mortem
✅ **VS Code debugger** — Launch configs, breakpoints
✅ **Exception handling** — Graceful errors, custom exceptions
✅ **Performance debugging** — Timing logs, profiling, memory
✅ **Common issues** — Troubleshooting TUI, search, imports, config
✅ **Testing strategies** — Unit tests, integration tests, coverage

---

## Next Steps

Now let's explore packaging and deployment options.

**Next:** [Deployment and Packaging](04-deployment.md)

---

## Further Reading

- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [pdb Documentation](https://docs.python.org/3/library/pdb.html)
- [Textual Devtools](https://textual.textualize.io/guide/devtools/)
- [pytest Documentation](https://docs.pytest.org/)
