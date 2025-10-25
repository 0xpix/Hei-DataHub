# Tests

## Overview

This document describes the testing strategy, structure, and guidelines for Hei-DataHub. Comprehensive testing ensures reliability, catches regressions, and enables confident refactoring.

---

## Testing Strategy

### Test Pyramid

```
        ┌────────────────┐
        │   E2E Tests    │  5%  - Full user workflows
        │    (Manual)    │
        ├────────────────┤
        │  Integration   │ 25%  - Multi-module interactions
        │     Tests      │
        ├────────────────┤
        │   Unit Tests   │ 70%  - Individual functions
        └────────────────┘
```

**Rationale:**
- **Unit tests (70%):** Fast, isolated, easy to debug
- **Integration tests (25%):** Catch interface issues
- **E2E tests (5%):** Validate critical user flows

---

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared pytest fixtures
│
├── unit/                    # Unit tests (isolated)
│   ├── __init__.py
│   ├── core/
│   │   ├── test_models.py           # Pydantic model tests
│   │   └── test_validators.py       # Validation logic tests
│   ├── services/
│   │   ├── test_fast_search.py      # Search service tests
│   │   ├── test_autocomplete.py     # Autocomplete tests
│   │   └── test_sync.py             # Sync logic tests
│   ├── infra/
│   │   ├── test_index.py            # FTS5 index tests
│   │   └── test_db.py               # Database tests
│   └── utils/
│       ├── test_formatting.py       # Formatting utils tests
│       └── test_timing.py           # Timing utils tests
│
├── integration/             # Integration tests (multi-module)
│   ├── __init__.py
│   ├── test_search_flow.py          # Search end-to-end
│   ├── test_sync_flow.py            # Sync end-to-end
│   └── test_dataset_lifecycle.py    # Create/update/delete
│
├── manual/                  # Manual test scripts
│   ├── test_webdav.py               # WebDAV connection test
│   ├── test_keyring.py              # Keyring integration test
│   └── README.md                    # Manual test instructions
│
├── services/                # Service-level tests
│   ├── test_webdav_storage.py       # WebDAV client tests
│   └── test_index_service.py        # Index service tests
│
└── ui/                      # UI tests
    ├── test_views.py                # View rendering tests
    └── test_widgets.py              # Widget behavior tests
```

---

## Unit Tests

### Core Module Tests

#### `test_models.py` - Pydantic Model Tests

**Purpose:** Test domain model validation and serialization

**Example:**

```python
import pytest
from pydantic import ValidationError

from mini_datahub.core.models import DatasetMetadata


def test_dataset_metadata_valid():
    """Test valid dataset creation"""
    data = {
        "id": "test-dataset",
        "dataset_name": "Test Dataset",
        "description": "Test description",
        "source": "test source",
        "date_created": "2024-01-01",
        "storage_location": "/test/path"
    }

    dataset = DatasetMetadata.model_validate(data)

    assert dataset.id == "test-dataset"
    assert dataset.dataset_name == "Test Dataset"


def test_dataset_metadata_missing_required_field():
    """Test validation fails for missing required field"""
    data = {
        "id": "test-dataset",
        # Missing required fields
    }

    with pytest.raises(ValidationError) as exc_info:
        DatasetMetadata.model_validate(data)

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(e["type"] == "missing" for e in errors)


def test_dataset_id_format_validation():
    """Test ID format validation (lowercase, alphanumeric, dashes)"""
    # Valid IDs
    valid_ids = ["dataset-1", "climate_data", "test123"]
    for valid_id in valid_ids:
        dataset = DatasetMetadata.model_validate({
            "id": valid_id,
            "dataset_name": "Test",
            "description": "Test",
            "source": "test",
            "date_created": "2024-01-01",
            "storage_location": "/test"
        })
        assert dataset.id == valid_id

    # Invalid IDs
    invalid_ids = ["Dataset-1", "-invalid", "with space"]
    for invalid_id in invalid_ids:
        with pytest.raises(ValidationError):
            DatasetMetadata.model_validate({
                "id": invalid_id,
                "dataset_name": "Test",
                "description": "Test",
                "source": "test",
                "date_created": "2024-01-01",
                "storage_location": "/test"
            })


def test_dataset_to_dict():
    """Test serialization to dict"""
    dataset = DatasetMetadata.model_validate({
        "id": "test",
        "dataset_name": "Test",
        "description": "Test",
        "source": "test",
        "date_created": "2024-01-01",
        "storage_location": "/test"
    })

    data = dataset.to_dict()

    assert isinstance(data, dict)
    assert data["id"] == "test"
    assert "dataset_name" in data
```

---

### Services Module Tests

#### `test_fast_search.py` - Search Service Tests

**Purpose:** Test search orchestration logic

**Example:**

```python
from unittest.mock import Mock, patch
import pytest

from mini_datahub.services.fast_search import search_indexed


def test_search_indexed_simple_query():
    """Test simple search query"""
    # Mock the index service
    with patch("mini_datahub.services.fast_search.get_index_service") as mock_get_index:
        mock_index = Mock()
        mock_index.search.return_value = [
            {"path": "test-dataset", "name": "Test Dataset", "description": "Test"}
        ]
        mock_get_index.return_value = mock_index

        # Execute search
        results = search_indexed("test")

        # Verify
        assert len(results) == 1
        assert results[0]["name"] == "Test Dataset"
        mock_index.search.assert_called_once()


def test_search_indexed_with_project_filter():
    """Test search with project filter"""
    with patch("mini_datahub.services.fast_search.get_index_service") as mock_get_index:
        mock_index = Mock()
        mock_index.search.return_value = []
        mock_get_index.return_value = mock_index

        # Search with project filter
        results = search_indexed("climate project:research")

        # Verify project filter was extracted
        call_args = mock_index.search.call_args
        assert call_args[1]["project_filter"] == "research"


def test_search_indexed_empty_query():
    """Test search with empty query returns no results"""
    results = search_indexed("")
    assert results == []

    results = search_indexed("   ")  # Whitespace only
    assert results == []


def test_search_indexed_limit():
    """Test result limiting"""
    with patch("mini_datahub.services.fast_search.get_index_service") as mock_get_index:
        mock_index = Mock()
        mock_index.search.return_value = []
        mock_get_index.return_value = mock_index

        # Search with custom limit
        results = search_indexed("test", limit=10)

        # Verify limit was passed
        call_args = mock_index.search.call_args
        assert call_args[1]["limit"] == 10
```

---

### Infrastructure Module Tests

#### `test_index.py` - FTS5 Index Tests

**Purpose:** Test database index operations

**Example:**

```python
import tempfile
from pathlib import Path
import pytest

from mini_datahub.infra.index import upsert_dataset, search_datasets, delete_dataset
from mini_datahub.infra.db import get_connection


@pytest.fixture
def test_db():
    """Create temporary test database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Override DB_PATH for tests
        import mini_datahub.infra.db as db_module
        original_path = db_module.DB_PATH
        db_module.DB_PATH = db_path

        # Initialize schema
        db_module.ensure_database()

        yield db_path

        # Restore original path
        db_module.DB_PATH = original_path


def test_upsert_dataset(test_db):
    """Test dataset insertion"""
    metadata = {
        "id": "test-dataset",
        "dataset_name": "Test Dataset",
        "description": "Test description",
        "source": "test",
        "date_created": "2024-01-01",
        "storage_location": "/test"
    }

    # Insert
    upsert_dataset("test-dataset", metadata)

    # Verify stored
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets_store WHERE id = ?", ("test-dataset",))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["id"] == "test-dataset"


def test_search_datasets(test_db):
    """Test FTS5 search"""
    # Insert test data
    metadata = {
        "id": "climate-data",
        "dataset_name": "Climate Model Data",
        "description": "Historical climate model outputs",
        "source": "test",
        "date_created": "2024-01-01",
        "storage_location": "/test"
    }
    upsert_dataset("climate-data", metadata)

    # Search
    results = search_datasets("climate")

    assert len(results) > 0
    assert any(r["id"] == "climate-data" for r in results)


def test_delete_dataset(test_db):
    """Test dataset deletion"""
    # Insert
    metadata = {"id": "test", "dataset_name": "Test", ...}
    upsert_dataset("test", metadata)

    # Delete
    delete_dataset("test")

    # Verify deleted
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets_store WHERE id = ?", ("test",))
    row = cursor.fetchone()
    conn.close()

    assert row is None
```

---

## Integration Tests

### `test_search_flow.py` - End-to-End Search

**Purpose:** Test complete search workflow

**Example:**

```python
def test_search_flow_end_to_end(test_db):
    """Test complete search flow: index → search → results"""
    # 1. Index datasets
    datasets = [
        {"id": "climate-1", "dataset_name": "Climate Data", ...},
        {"id": "ocean-1", "dataset_name": "Ocean Temperature", ...},
        {"id": "climate-2", "dataset_name": "Climate Models", ...},
    ]

    for dataset in datasets:
        upsert_dataset(dataset["id"], dataset)

    # 2. Search
    results = search_indexed("climate")

    # 3. Verify results
    assert len(results) == 2
    assert all("climate" in r["id"] for r in results)

    # 4. Verify ranking (BM25)
    # Exact match in name should rank higher
    assert results[0]["name"] == "Climate Data"
```

---

### `test_dataset_lifecycle.py` - Dataset CRUD

**Purpose:** Test full dataset lifecycle

**Example:**

```python
def test_dataset_lifecycle(test_db):
    """Test create → read → update → delete"""
    # CREATE
    metadata = {"id": "test", "dataset_name": "Test", ...}
    upsert_dataset("test", metadata)

    # READ
    from mini_datahub.infra.store import get_dataset
    stored = get_dataset("test")
    assert stored is not None
    assert stored["dataset_name"] == "Test"

    # UPDATE
    metadata["dataset_name"] = "Updated Test"
    upsert_dataset("test", metadata)
    stored = get_dataset("test")
    assert stored["dataset_name"] == "Updated Test"

    # DELETE
    delete_dataset("test")
    stored = get_dataset("test")
    assert stored is None
```

---

## Manual Tests

### `manual/test_webdav.py` - WebDAV Connection Test

**Purpose:** Manually test WebDAV connectivity

**Usage:**

```bash
python tests/manual/test_webdav.py
```

**Script:**

```python
"""
Manual WebDAV connection test.
Requires credentials to be configured.
"""
from mini_datahub.services.config import load_config
from mini_datahub.auth.credentials import get_secret
from mini_datahub.services.webdav_storage import WebDAVStorage


def main():
    print("WebDAV Connection Test")
    print("=" * 40)

    # Load config
    config = load_config()
    webdav_config = config.get("webdav", {})

    url = webdav_config.get("url")
    library = webdav_config.get("library")
    key_id = webdav_config.get("key_id")

    if not all([url, library, key_id]):
        print("✗ WebDAV not configured. Run 'hei-datahub auth setup'")
        return

    # Get credentials
    token = get_secret(key_id)
    if not token:
        print("✗ Credentials not found in keyring")
        return

    print(f"URL: {url}")
    print(f"Library: {library}")
    print()

    # Test connection
    print("Testing connection...")
    storage = WebDAVStorage(url, library, token)

    try:
        files = storage.list_remote_files()
        print(f"✓ Connection successful!")
        print(f"✓ Found {len(files)} file(s)")

        for file in files[:5]:  # Show first 5
            print(f"  - {file['path']}")

    except Exception as e:
        print(f"✗ Connection failed: {e}")


if __name__ == "__main__":
    main()
```

---

## Fixtures

### `conftest.py` - Shared Pytest Fixtures

```python
import tempfile
from pathlib import Path
import pytest

@pytest.fixture
def test_db():
    """Temporary test database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        # Setup and teardown
        yield db_path

@pytest.fixture
def test_dataset():
    """Sample test dataset"""
    return {
        "id": "test-dataset",
        "dataset_name": "Test Dataset",
        "description": "Test description",
        "source": "test",
        "date_created": "2024-01-01",
        "storage_location": "/test/path"
    }

@pytest.fixture
def mock_index_service(mocker):
    """Mock IndexService"""
    return mocker.patch("mini_datahub.services.index_service.IndexService")
```

---

## Coverage

### Running Tests with Coverage

```bash
# Run all tests with coverage
pytest --cov=mini_datahub --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/core/test_models.py -v

# Run with markers
pytest -m "not slow"  # Skip slow tests
```

### Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| `core/` | >90% | 92% |
| `services/` | >80% | 85% |
| `infra/` | >70% | 78% |
| `utils/` | >85% | 88% |
| **Overall** | **>80%** | **83%** |

---

## Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_function():
    # Arrange: Set up test data
    data = {"key": "value"}

    # Act: Execute function under test
    result = function_under_test(data)

    # Assert: Verify results
    assert result == expected_value
```

### 2. Use Descriptive Names

```python
# ✅ GOOD
def test_search_returns_empty_list_for_no_matches():
    pass

# ❌ BAD
def test_search():
    pass
```

### 3. Test One Thing Per Test

```python
# ✅ GOOD
def test_dataset_creation():
    dataset = create_dataset()
    assert dataset.id is not None

def test_dataset_validation():
    with pytest.raises(ValidationError):
        create_dataset(id="Invalid ID")

# ❌ BAD
def test_dataset():
    # Tests multiple things
    dataset = create_dataset()
    assert dataset.id is not None
    with pytest.raises(ValidationError):
        create_dataset(id="Invalid ID")
```

### 4. Use Fixtures for Common Setup

```python
@pytest.fixture
def sample_dataset():
    return {"id": "test", "dataset_name": "Test"}

def test_with_fixture(sample_dataset):
    assert sample_dataset["id"] == "test"
```

---

## Related Documentation

- **[Contributing Workflow](../contributing/workflow.md)** - Development process
- **[Definition of Done](../contributing/definition-of-done.md)** - Completion criteria
- **[Code Review](../contributing/code-review.md)** - Review checklist

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
