# Deep Dive: Testing Strategy

**Learning Goal**: Master the testing strategy for Hei-DataHub across all layers.

By the end of this page, you'll:
- Understand test organization
- Write unit tests with pytest
- Mock external dependencies
- Test TUI components
- Write integration tests
- Use fixtures effectively
- Measure test coverage

---

## Why Test?

**Benefits:**

✅ **Catch bugs early** — Before users do
✅ **Refactor confidently** — Tests prove it still works
✅ **Document behavior** — Tests are executable specs
✅ **Prevent regressions** — Old bugs stay fixed

**Cost:**

❌ **Time to write** — But saves debugging time
❌ **Maintenance** — Tests need updates too

**ROI:** High for core logic, lower for UI.

---

## Test Organization

```
tests/
├── unit/              # Isolated unit tests
│   ├── test_index_service.py
│   ├── test_auth_doctor.py
│   └── test_auth_clear.py
├── services/          # Service layer integration tests
│   └── (empty for now)
├── ui/                # TUI component tests
│   └── (empty for now)
└── manual/            # Manual test scripts
    └── test_auto_index_update.py
```

**Organization:**

- **unit/** — Fast, isolated, no I/O
- **services/** — Integration with real DB/files
- **ui/** — Textual UI component tests
- **manual/** — Scripts for exploratory testing

---

## Test Tools

**Framework:** pytest

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov",  # Coverage reporting
    "pytest-mock",  # Mocking helpers
]
```

**Install:**

```bash
pip install -e ".[dev]"
```

---

## Unit Testing

**Goal:** Test individual functions in isolation.

### Example: Index Service

**File:** `tests/unit/test_index_service.py`

```python
"""
Unit tests for the index service.
"""
import pytest
import tempfile
from pathlib import Path

from mini_datahub.services.index_service import IndexService


@pytest.fixture
def temp_index():
    """Create a temporary index database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_index.db"
        index = IndexService(db_path=db_path)
        yield index


def test_index_initialization(temp_index):
    """Test that index database is created and initialized."""
    assert temp_index.db_path.exists()
    conn = temp_index.get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    assert "items" in tables
    assert "items_fts" in tables
    assert "index_meta" in tables
    conn.close()


def test_upsert_and_search(temp_index):
    """Test inserting items and searching."""
    # Insert test items
    temp_index.upsert_item(
        path="dataset-1",
        name="Climate Data 2024",
        project="climate-research",
        tags="climate temperature",
        description="Temperature measurements from 2024",
        is_remote=False,
    )

    temp_index.upsert_item(
        path="dataset-2",
        name="Rainfall Data",
        project="climate-research",
        tags="climate precipitation",
        description="Precipitation measurements",
        is_remote=True,
    )

    # Test free text search
    results = temp_index.search(query_text="climate")
    assert len(results) == 2
    assert all("climate" in r["name"].lower()
               or "climate" in r.get("description", "").lower()
               for r in results)

    # Test project filter
    results = temp_index.search(query_text="", project_filter="climate")
    assert len(results) == 2
    assert all(r["project"] == "climate-research" for r in results)

    # Test no results
    results = temp_index.search(query_text="nonexistent")
    assert len(results) == 0


def test_bulk_upsert(temp_index):
    """Test bulk insert operation."""
    items = [
        {
            "path": f"dataset-{i}",
            "name": f"Dataset {i}",
            "project": "test-project",
            "tags": "test tag",
            "description": f"Description {i}",
            "is_remote": False,
        }
        for i in range(100)
    ]

    count = temp_index.bulk_upsert(items)
    assert count == 100

    # Verify all items are searchable
    results = temp_index.search(query_text="Dataset")
    assert len(results) == 100
```

**Key patterns:**

1. **Fixtures** — `temp_index` creates isolated test DB
2. **Assertions** — Check expected outcomes
3. **Cleanup** — `tempfile` auto-deletes temp files

---

## Mocking External Dependencies

**Goal:** Test code without hitting real APIs/files.

### Example: Auth Doctor Tests

**File:** `tests/unit/test_auth_doctor.py`

```python
"""
Tests for auth doctor command.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


@pytest.fixture
def mock_config_path(tmp_path):
    """Create a temporary config path."""
    config_dir = tmp_path / ".config" / "hei-datahub"
    config_dir.mkdir(parents=True)
    return config_dir / "config.toml"


@pytest.fixture
def mock_config_with_auth(mock_config_path):
    """Create a config file with auth section."""
    config_content = """
[auth]
method = "token"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "testuser"
key_id = "webdav:token:testuser@heibox.uni-heidelberg.de"
stored_in = "keyring"
"""
    mock_config_path.write_text(config_content)
    return mock_config_path


class TestAuthDoctor:
    """Test cases for auth doctor command."""

    @patch("mini_datahub.auth.doctor.platform.system")
    def test_non_linux_platform(self, mock_platform):
        """Test that doctor fails on non-Linux platforms."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Windows"
        exit_code = run_doctor()

        assert exit_code == 2

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    def test_config_missing(self, mock_get_config_path, mock_platform, mock_config_path):
        """Test when config file doesn't exist."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_path  # File doesn't exist

        exit_code = run_doctor()

        assert exit_code == 2  # Config issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    def test_credentials_not_found(
        self,
        mock_get_auth_store,
        mock_get_config_path,
        mock_platform,
        mock_config_with_auth
    ):
        """Test when credentials are not found in keyring/env."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock auth store that returns None for credentials
        mock_store = Mock()
        mock_store.load_secret.return_value = None
        mock_get_auth_store.return_value = mock_store

        exit_code = run_doctor()

        assert exit_code == 2  # Config/credential issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("mini_datahub.services.webdav_storage.WebDAVStorage")
    def test_successful_validation(
        self,
        mock_webdav,
        mock_get_auth_store,
        mock_get_config_path,
        mock_platform,
        mock_config_with_auth
    ):
        """Test successful auth validation."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock successful credential retrieval
        mock_store = Mock()
        mock_store.load_secret.return_value = "test-token"
        mock_get_auth_store.return_value = mock_store

        # Mock successful WebDAV connection
        mock_storage = Mock()
        mock_storage.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_webdav.return_value = mock_storage

        exit_code = run_doctor()

        assert exit_code == 0  # Success
```

**Mocking patterns:**

1. **`@patch()`** — Replace real functions with mocks
2. **`Mock()`** — Create fake objects
3. **`return_value`** — Control mock behavior
4. **Verify** — Check expected outcomes

---

## Pytest Fixtures

**Goal:** Reusable test setup/teardown.

### Built-in Fixtures

```python
def test_example(tmp_path):
    """tmp_path provides a temporary directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    assert test_file.read_text() == "hello"
```

**Common built-ins:**

- `tmp_path` — Temporary directory (pathlib.Path)
- `capsys` — Capture stdout/stderr
- `monkeypatch` — Modify objects/environment
- `request` — Access test context

---

### Custom Fixtures

```python
@pytest.fixture
def sample_metadata():
    """Provide sample dataset metadata."""
    return {
        "dataset_name": "Test Dataset",
        "description": "A test dataset",
        "used_in_projects": ["test-project"],
        "data_types": ["csv"],
        "source": "github",
        "file_format": "csv",
    }


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory with sample datasets."""
    data_dir = tmp_path / "datasets"
    data_dir.mkdir()

    # Create sample datasets
    for i in range(3):
        dataset_dir = data_dir / f"dataset-{i}"
        dataset_dir.mkdir()

        metadata_file = dataset_dir / "metadata.yaml"
        metadata_file.write_text(f"""
dataset_name: Dataset {i}
description: Test dataset {i}
used_in_projects:
  - test-project
""")

    yield data_dir


def test_with_fixtures(temp_data_dir, sample_metadata):
    """Use multiple fixtures."""
    datasets = list(temp_data_dir.iterdir())
    assert len(datasets) == 3

    assert sample_metadata["dataset_name"] == "Test Dataset"
```

---

### Fixture Scopes

**Scope:** How long fixture lives.

```python
@pytest.fixture(scope="function")  # Default: new for each test
def function_fixture():
    pass


@pytest.fixture(scope="module")  # One per module
def module_fixture():
    pass


@pytest.fixture(scope="session")  # One per test session
def session_fixture():
    pass
```

**Example:**

```python
@pytest.fixture(scope="module")
def shared_database():
    """Create database once for all tests in module."""
    db_path = Path("test.db")
    # Initialize database
    yield db_path
    # Cleanup
    db_path.unlink()
```

---

## Testing TUI Components

**Goal:** Test Textual UI without launching full app.

### Textual Pilot API

```python
from textual.widgets import Input, Button
from textual.app import App, ComposeResult
from textual.pilot import Pilot
import pytest


class SampleScreen(Screen):
    """Sample screen for testing."""

    def compose(self) -> ComposeResult:
        yield Input(id="name_input", placeholder="Enter name")
        yield Button("Submit", id="submit_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit_btn":
            name = self.query_one("#name_input", Input).value
            self.app.notify(f"Hello, {name}!")


@pytest.mark.asyncio
async def test_sample_screen():
    """Test screen interaction with Pilot."""
    app = App()

    async with app.run_test() as pilot:
        # Push screen
        app.push_screen(SampleScreen())

        # Find input widget
        input_widget = pilot.app.query_one("#name_input", Input)

        # Type into input
        await pilot.click("#name_input")
        await pilot.press("A", "l", "i", "c", "e")

        # Verify value
        assert input_widget.value == "Alice"

        # Click button
        await pilot.click("#submit_btn")

        # Verify notification (check app state)
        # Note: This is simplified; real test would check notification system
```

**Pilot API:**

- `pilot.click(selector)` — Click widget by CSS selector
- `pilot.press(*keys)` — Press keyboard keys
- `pilot.app.query_one(selector)` — Get widget
- `pilot.pause(delay)` — Wait for UI updates

---

## Integration Tests

**Goal:** Test multiple components together.

### Example: Full Reindex Flow

```python
def test_full_reindex_flow(tmp_path):
    """Test complete reindex workflow."""
    from mini_datahub.infra.paths import DATA_DIR, DB_PATH
    from mini_datahub.infra.index import reindex_all
    from mini_datahub.infra.store import write_dataset

    # Override paths (monkeypatch or env vars)
    import os
    os.environ['HEIDATAHUB_DATA_DIR'] = str(tmp_path / "data")

    # Create sample datasets
    for i in range(5):
        metadata = {
            "dataset_name": f"Dataset {i}",
            "description": f"Description {i}",
            "used_in_projects": ["test-project"],
        }
        write_dataset(f"dataset-{i}", metadata)

    # Run reindex
    count, errors = reindex_all()

    # Verify
    assert count == 5
    assert len(errors) == 0

    # Verify database
    from mini_datahub.infra.db import get_connection
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM datasets_store")
    assert cursor.fetchone()[0] == 5
    conn.close()
```

---

## Parametrized Tests

**Goal:** Run same test with different inputs.

```python
@pytest.mark.parametrize("query,expected_count", [
    ("climate", 2),
    ("rainfall", 1),
    ("nonexistent", 0),
])
def test_search_queries(temp_index, query, expected_count):
    """Test various search queries."""
    # Setup test data
    temp_index.upsert_item(path="ds1", name="Climate Data", ...)
    temp_index.upsert_item(path="ds2", name="Climate Analysis", ...)
    temp_index.upsert_item(path="ds3", name="Rainfall Data", ...)

    # Test
    results = temp_index.search(query_text=query)
    assert len(results) == expected_count


@pytest.mark.parametrize("input,expected", [
    ("my:dataset", "my_dataset"),
    ("data<2024>.yaml", "data_2024_.yaml"),
    ("CON", "CON_file"),
    ("file.", "file"),
])
def test_windows_filename_sanitization(input, expected):
    """Test filename sanitization for Windows."""
    from mini_datahub.infra.platform_paths import sanitize_windows_filename

    assert sanitize_windows_filename(input) == expected
```

---

## Test Coverage

**Goal:** Measure how much code is tested.

### Running Coverage

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest --cov=mini_datahub tests/

# Generate HTML report
pytest --cov=mini_datahub --cov-report=html tests/

# Open report
open htmlcov/index.html
```

**Output:**

```
---------- coverage: platform linux, python 3.11.5 -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
mini_datahub/__init__.py                    3      0   100%
mini_datahub/infra/index.py               120     15    88%
mini_datahub/services/search.py            85     20    76%
mini_datahub/ui/views/home.py             200    150    25%
-----------------------------------------------------------
TOTAL                                     408    185    55%
```

---

### Coverage Goals

**Good targets:**

| Layer | Target | Reason |
|-------|--------|--------|
| **Core** | 90%+ | Business logic must work |
| **Services** | 80%+ | Orchestration is critical |
| **Infra** | 70%+ | I/O can be mocked |
| **UI** | 50%+ | Hard to test, less critical |

---

## Testing Best Practices

### 1. Arrange-Act-Assert (AAA)

```python
def test_dataset_upsert():
    # Arrange
    dataset_id = "test-dataset"
    metadata = {"dataset_name": "Test"}

    # Act
    upsert_dataset(dataset_id, metadata)

    # Assert
    result = get_dataset_from_store(dataset_id)
    assert result["dataset_name"] == "Test"
```

---

### 2. Test One Thing

**❌ Bad (tests multiple things):**

```python
def test_everything():
    # Tests search, upsert, delete
    upsert_dataset("ds1", {...})
    results = search_datasets("test")
    delete_dataset("ds1")
    # Too much!
```

**✅ Good (focused):**

```python
def test_search_returns_matching_datasets():
    # Setup
    upsert_dataset("ds1", {"dataset_name": "Climate"})

    # Test only search
    results = search_datasets("climate")
    assert len(results) == 1
```

---

### 3. Descriptive Test Names

```python
# ❌ Bad
def test_1():
    pass

# ✅ Good
def test_search_returns_empty_list_when_no_matches():
    pass

def test_upsert_creates_new_dataset_when_id_not_exists():
    pass
```

---

### 4. Use Fixtures for Reusable Setup

```python
# ❌ Bad (repeated setup)
def test_search_1():
    db = create_test_db()
    populate_test_data(db)
    # Test...

def test_search_2():
    db = create_test_db()  # Duplicated!
    populate_test_data(db)
    # Test...


# ✅ Good (fixture)
@pytest.fixture
def populated_db():
    db = create_test_db()
    populate_test_data(db)
    return db

def test_search_1(populated_db):
    # Test...

def test_search_2(populated_db):
    # Test...
```

---

## Running Tests

### Run All Tests

```bash
pytest
```

---

### Run Specific Test File

```bash
pytest tests/unit/test_index_service.py
```

---

### Run Specific Test

```bash
pytest tests/unit/test_index_service.py::test_upsert_and_search
```

---

### Run Tests Matching Pattern

```bash
pytest -k "search"  # Run tests with "search" in name
```

---

### Verbose Output

```bash
pytest -v  # Show each test name
pytest -vv  # Even more verbose
```

---

### Stop on First Failure

```bash
pytest -x
```

---

### Show Print Statements

```bash
pytest -s  # Disable output capture
```

---

## Continuous Integration

**Example:** GitHub Actions workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest --cov=mini_datahub tests/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## What You've Learned

✅ **Test organization** — unit/ services/ ui/ manual/
✅ **Unit tests** — Isolated, fast, no I/O
✅ **Mocking** — Test without real dependencies
✅ **Fixtures** — Reusable test setup
✅ **TUI testing** — Textual Pilot API
✅ **Integration tests** — Multi-component workflows
✅ **Parametrized tests** — Multiple inputs, one test
✅ **Coverage** — Measure test completeness
✅ **Best practices** — AAA, focused tests, descriptive names
✅ **CI/CD** — Automated testing in GitHub Actions

---

## Next Steps

Congratulations! You've completed the **Deep Dive** section. Now let's explore advanced topics.

**Next:** [Extending Hei-DataHub](../advanced/01-extending.md)

---

## Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Textual Testing Guide](https://textual.textualize.io/guide/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
