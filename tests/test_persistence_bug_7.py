"""
Integration test for Bug #7: Dataset edits revert after app restart.

This test verifies that edits persist across app restarts.
"""
import json
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from mini_datahub.infra.db import init_database
from mini_datahub.infra.paths import DATA_DIR
from mini_datahub.services.storage import save_dataset_atomic
from mini_datahub.infra.store import read_dataset


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Create temporary data directory for isolated testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / "data"
        temp_path.mkdir()

        # Monkey patch DATA_DIR in paths and store modules
        import mini_datahub.infra.paths as paths_module
        import mini_datahub.infra.store as store_module

        monkeypatch.setattr(paths_module, 'DATA_DIR', temp_path)
        monkeypatch.setattr(store_module, 'DATA_DIR', temp_path)

        # Initialize database in temp location
        db_path = Path(tmpdir) / "test.db"
        import mini_datahub.infra.db as db_module
        monkeypatch.setattr(db_module, 'DB_PATH', db_path)
        init_database()

        yield temp_path


def test_edit_persists_after_restart(temp_data_dir):
    """
    Test that dataset edits persist across "restarts" (reload from disk).

    Reproduces Bug #7:
    1. Create dataset
    2. Edit and save
    3. Simulate restart by reading from disk
    4. Verify edited data persists
    """
    dataset_id = "test-dataset"

    # Step 1: Create initial dataset
    initial_metadata = {
        "id": dataset_id,
        "dataset_name": "Initial Name",
        "description": "Initial description",
        "source": "https://example.com/initial",
        "storage_location": "s3://bucket/initial.csv",
        "file_format": "csv",
        "size": "1 KB",
        "data_types": ["tabular"],
        "used_in_projects": ["project-a"],
        "date_created": "2025-10-01",
        "last_updated": "2025-10-01",
    }

    success, error = save_dataset_atomic(dataset_id, initial_metadata)
    assert success, f"Initial save failed: {error}"

    # Verify initial state persists to disk
    yaml_path = temp_data_dir / dataset_id / "metadata.yaml"
    assert yaml_path.exists(), "YAML file not created"

    with open(yaml_path) as f:
        disk_data = yaml.safe_load(f)
    assert disk_data["dataset_name"] == "Initial Name"
    assert disk_data["description"] == "Initial description"

    # Step 2: Edit the dataset (simulate user editing in TUI)
    edited_metadata = initial_metadata.copy()
    edited_metadata["dataset_name"] = "EDITED Name"
    edited_metadata["description"] = "EDITED description - this is the new content"
    edited_metadata["source"] = "https://example.com/EDITED"
    edited_metadata["last_updated"] = "2025-10-08"

    success, error = save_dataset_atomic(dataset_id, edited_metadata)
    assert success, f"Edit save failed: {error}"

    # Step 3: Simulate app restart - read from disk (cold load)
    # Clear any in-memory cache
    reloaded_metadata = read_dataset(dataset_id)

    # Step 4: CRITICAL ASSERTION - edited data must persist
    assert reloaded_metadata is not None, "Dataset not found after reload"
    assert reloaded_metadata["dataset_name"] == "EDITED Name", \
        f"BUG #7 REPRODUCED: Name reverted to {reloaded_metadata['dataset_name']}"
    assert reloaded_metadata["description"] == "EDITED description - this is the new content", \
        f"BUG #7 REPRODUCED: Description reverted"
    assert reloaded_metadata["source"] == "https://example.com/EDITED", \
        f"BUG #7 REPRODUCED: Source reverted"

    # Verify YAML file on disk has edited data
    with open(yaml_path) as f:
        final_disk_data = yaml.safe_load(f)

    assert final_disk_data["dataset_name"] == "EDITED Name", \
        "YAML file does not contain edited data"
    assert final_disk_data["description"] == "EDITED description - this is the new content", \
        "YAML file description not updated"


def test_multiple_edits_persist(temp_data_dir):
    """Test multiple sequential edits all persist correctly."""
    dataset_id = "test-multi-edit"

    # Create initial dataset
    metadata = {
        "id": dataset_id,
        "dataset_name": "Version 1",
        "description": "Description v1",
        "source": "source-v1",
        "storage_location": "storage-v1",
        "file_format": "csv",
        "size": "1 KB",
        "data_types": ["tabular"],
        "used_in_projects": [],
        "date_created": "2025-10-01",
        "last_updated": "2025-10-01",
    }

    save_dataset_atomic(dataset_id, metadata)

    # Edit 1
    metadata["dataset_name"] = "Version 2"
    metadata["description"] = "Description v2"
    success, _ = save_dataset_atomic(dataset_id, metadata)
    assert success

    reloaded = read_dataset(dataset_id)
    assert reloaded["dataset_name"] == "Version 2"
    assert reloaded["description"] == "Description v2"

    # Edit 2
    metadata["dataset_name"] = "Version 3"
    metadata["description"] = "Description v3"
    success, _ = save_dataset_atomic(dataset_id, metadata)
    assert success

    reloaded = read_dataset(dataset_id)
    assert reloaded["dataset_name"] == "Version 3"
    assert reloaded["description"] == "Description v3"

    # Edit 3
    metadata["dataset_name"] = "Final Version"
    metadata["description"] = "Final description"
    success, _ = save_dataset_atomic(dataset_id, metadata)
    assert success

    reloaded = read_dataset(dataset_id)
    assert reloaded["dataset_name"] == "Final Version", \
        "Last edit did not persist"
    assert reloaded["description"] == "Final description", \
        "Last edit description did not persist"


def test_backup_created_on_edit(temp_data_dir):
    """Test that backup file is created when editing existing dataset."""
    dataset_id = "test-backup"

    # Create initial
    metadata = {
        "id": dataset_id,
        "dataset_name": "Original",
        "description": "Original description",
        "source": "source",
        "storage_location": "storage",
        "file_format": "csv",
        "size": "1 KB",
        "data_types": ["tabular"],
        "used_in_projects": [],
        "date_created": "2025-10-01",
        "last_updated": "2025-10-01",
    }

    save_dataset_atomic(dataset_id, metadata)

    # Edit - should create backup
    metadata["dataset_name"] = "Edited"
    save_dataset_atomic(dataset_id, metadata)

    # Check for backup file
    backup_path = temp_data_dir / dataset_id / "metadata.yaml.backup"
    assert backup_path.exists(), "Backup file not created"

    # Backup should contain original data
    with open(backup_path) as f:
        backup_data = yaml.safe_load(f)
    assert backup_data["dataset_name"] == "Original", \
        "Backup does not contain original data"


def test_atomic_write_on_failure(temp_data_dir):
    """Test that failed saves don't corrupt existing data."""
    dataset_id = "test-atomic"

    # Create valid initial dataset
    metadata = {
        "id": dataset_id,
        "dataset_name": "Valid Name",
        "description": "Valid description",
        "source": "source",
        "storage_location": "storage",
        "file_format": "csv",
        "size": "1 KB",
        "data_types": ["tabular"],
        "used_in_projects": [],
        "date_created": "2025-10-01",
        "last_updated": "2025-10-01",
    }

    success, _ = save_dataset_atomic(dataset_id, metadata)
    assert success

    # Attempt invalid edit (missing required field)
    invalid_metadata = metadata.copy()
    del invalid_metadata["dataset_name"]  # Required field

    success, error = save_dataset_atomic(dataset_id, invalid_metadata)
    assert not success, "Invalid save should fail"

    # Original data should still be intact
    reloaded = read_dataset(dataset_id)
    assert reloaded["dataset_name"] == "Valid Name", \
        "Original data corrupted by failed save"
