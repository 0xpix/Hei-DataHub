"""
Basic smoke tests for Hei-DataHub.
"""
import tempfile
from datetime import date
from pathlib import Path

import pytest
import yaml

from mini_datahub.index import (
    delete_dataset,
    ensure_database,
    get_dataset_by_id,
    reindex_all,
    search_datasets,
    upsert_dataset,
)
from mini_datahub.models import DatasetMetadata
from mini_datahub.storage import (
    generate_unique_id,
    read_dataset,
    save_dataset,
    slugify,
    validate_metadata,
    write_dataset,
)


def test_slugify():
    """Test slug generation."""
    assert slugify("My Dataset Name") == "my-dataset-name"
    assert slugify("Test_Dataset 123") == "test-dataset-123"
    assert slugify("  spaces  ") == "spaces"
    assert slugify("Special!@#$%Characters") == "specialcharacters"


def test_generate_unique_id(tmp_path, monkeypatch):
    """Test unique ID generation with collision handling."""
    # Mock DATA_DIR to use temp directory
    from mini_datahub import storage
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)

    # First ID should be clean
    id1 = generate_unique_id("My Dataset")
    assert id1 == "my-dataset"

    # Create a dataset with that ID
    (tmp_path / "my-dataset").mkdir()
    (tmp_path / "my-dataset" / "metadata.yaml").touch()

    # Second ID should have suffix
    id2 = generate_unique_id("My Dataset")
    assert id2 == "my-dataset-1"


def test_validate_metadata_success():
    """Test successful metadata validation."""
    valid_data = {
        "id": "test-dataset",
        "dataset_name": "Test Dataset",
        "description": "A test dataset for validation",
        "source": "https://example.com/data.csv",
        "date_created": "2024-01-01",
        "storage_location": "/data/test",
    }

    success, error, model = validate_metadata(valid_data)
    assert success is True
    assert error is None
    assert model is not None
    assert model.id == "test-dataset"


def test_validate_metadata_missing_required():
    """Test validation failure for missing required fields."""
    invalid_data = {
        "id": "test-dataset",
        "dataset_name": "Test Dataset",
        # Missing description, source, date_created, storage_location
    }

    success, error, model = validate_metadata(invalid_data)
    assert success is False
    assert error is not None
    assert model is None


def test_validate_metadata_invalid_id():
    """Test validation failure for invalid ID format."""
    invalid_data = {
        "id": "Invalid ID!",  # Contains spaces and special chars
        "dataset_name": "Test Dataset",
        "description": "A test dataset",
        "source": "https://example.com",
        "date_created": "2024-01-01",
        "storage_location": "/data/test",
    }

    success, error, model = validate_metadata(invalid_data)
    assert success is False
    assert "id" in error.lower() or "pattern" in error.lower()


def test_pydantic_model():
    """Test Pydantic model instantiation."""
    data = {
        "id": "weather-data",
        "dataset_name": "Weather Dataset",
        "description": "Daily weather observations",
        "source": "https://weather.example.com",
        "date_created": date(2024, 1, 1),
        "storage_location": "/data/weather",
        "data_types": ["weather", "time-series"],
        "used_in_projects": ["project-a"],
    }

    model = DatasetMetadata(**data)
    assert model.id == "weather-data"
    assert model.dataset_name == "Weather Dataset"
    assert model.data_types == ["weather", "time-series"]
    assert model.used_in_projects == ["project-a"]


def test_read_write_dataset(tmp_path, monkeypatch):
    """Test reading and writing dataset metadata."""
    from mini_datahub import storage
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)

    metadata = {
        "id": "test-ds",
        "dataset_name": "Test Dataset",
        "description": "Test description",
        "source": "https://example.com",
        "date_created": "2024-01-01",
        "storage_location": "/test",
    }

    # Write
    write_dataset("test-ds", metadata)

    # Verify file exists
    yaml_path = tmp_path / "test-ds" / "metadata.yaml"
    assert yaml_path.exists()

    # Read back
    loaded = read_dataset("test-ds")
    assert loaded is not None
    assert loaded["id"] == "test-ds"
    assert loaded["dataset_name"] == "Test Dataset"


def test_save_dataset_validation(tmp_path, monkeypatch):
    """Test save_dataset with validation."""
    from mini_datahub import storage
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)

    # Valid dataset
    valid = {
        "id": "valid-ds",
        "dataset_name": "Valid Dataset",
        "description": "Valid description",
        "source": "https://example.com",
        "date_created": "2024-01-01",
        "storage_location": "/valid",
    }

    success, msg = save_dataset(valid)
    assert success is True
    assert "successfully" in msg.lower()

    # Invalid dataset (missing required fields)
    invalid = {
        "id": "invalid-ds",
        "dataset_name": "Invalid Dataset",
    }

    success, msg = save_dataset(invalid)
    assert success is False
    assert msg is not None


def test_database_operations(tmp_path, monkeypatch):
    """Test database initialization and operations."""
    from mini_datahub import index

    # Use temp database
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(index, "DB_PATH", db_path)

    # Initialize database
    ensure_database()
    assert db_path.exists()

    # Upsert a dataset
    metadata = {
        "id": "db-test",
        "dataset_name": "Database Test",
        "description": "Testing database operations with full-text search",
        "source": "https://example.com",
        "date_created": "2024-01-01",
        "storage_location": "/test",
        "data_types": ["test", "demo"],
        "used_in_projects": ["test-project"],
    }

    upsert_dataset("db-test", metadata)

    # Retrieve by ID
    retrieved = get_dataset_by_id("db-test")
    assert retrieved is not None
    assert retrieved["id"] == "db-test"
    assert retrieved["dataset_name"] == "Database Test"

    # Search
    results = search_datasets("database")
    assert len(results) > 0
    assert any(r["id"] == "db-test" for r in results)

    # Delete
    delete_dataset("db-test")
    retrieved_after = get_dataset_by_id("db-test")
    assert retrieved_after is None


def test_reindex(tmp_path, monkeypatch):
    """Test reindexing from data directory."""
    from mini_datahub import index, storage

    # Setup temp paths
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db_path = tmp_path / "test.db"

    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(index, "DB_PATH", db_path)

    # Create some test datasets
    for i in range(3):
        ds_id = f"dataset-{i}"
        ds_dir = data_dir / ds_id
        ds_dir.mkdir()

        metadata = {
            "id": ds_id,
            "dataset_name": f"Dataset {i}",
            "description": f"Test dataset number {i}",
            "source": f"https://example.com/ds{i}",
            "date_created": "2024-01-01",
            "storage_location": f"/data/ds{i}",
        }

        with open(ds_dir / "metadata.yaml", "w") as f:
            yaml.safe_dump(metadata, f)

    # Initialize database
    ensure_database()

    # Reindex
    count, errors = reindex_all()
    assert count == 3
    assert len(errors) == 0

    # Verify all datasets are searchable
    for i in range(3):
        result = get_dataset_by_id(f"dataset-{i}")
        assert result is not None
        assert result["dataset_name"] == f"Dataset {i}"


def test_search_ranking(tmp_path, monkeypatch):
    """Test that search results are ranked properly."""
    from mini_datahub import index

    db_path = tmp_path / "test.db"
    monkeypatch.setattr(index, "DB_PATH", db_path)

    ensure_database()

    # Add datasets with different relevance to query "weather"
    datasets = [
        {
            "id": "weather-main",
            "dataset_name": "Weather Data",
            "description": "Weather weather weather observations",  # High relevance
            "source": "https://example.com",
            "date_created": "2024-01-01",
            "storage_location": "/data1",
        },
        {
            "id": "climate-data",
            "dataset_name": "Climate Patterns",
            "description": "Long-term climate analysis",  # Low relevance
            "source": "https://example.com",
            "date_created": "2024-01-01",
            "storage_location": "/data2",
        },
        {
            "id": "temp-weather",
            "dataset_name": "Temperature and Weather",
            "description": "Daily temperature and weather records",  # Medium relevance
            "source": "https://example.com",
            "date_created": "2024-01-01",
            "storage_location": "/data3",
        },
    ]

    for ds in datasets:
        upsert_dataset(ds["id"], ds)

    # Search for "weather"
    results = search_datasets("weather")

    # Should return at least 2 results (weather-main and temp-weather)
    assert len(results) >= 2

    # The first result should be the most relevant (weather-main)
    assert results[0]["id"] == "weather-main"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
