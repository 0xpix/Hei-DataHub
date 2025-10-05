"""
Storage service: Atomic write operations with SQLite reindexing.

Provides atomic YAML file writes with transactional SQLite updates.
"""
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from mini_datahub.infra.db import get_connection
from mini_datahub.infra.store import get_dataset_path, validate_metadata

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Error during storage operation."""
    pass


def write_yaml_atomic(dataset_id: str, metadata: Dict[str, Any]) -> None:
    """
    Write dataset metadata to YAML file atomically.

    Uses a temp file and atomic rename to ensure durability.

    Args:
        dataset_id: Dataset ID
        metadata: Metadata dictionary

    Raises:
        StorageError: If write fails
    """
    yaml_path = get_dataset_path(dataset_id)

    # Ensure directory exists
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing file if it exists
    backup_path = None
    if yaml_path.exists():
        backup_path = yaml_path.with_suffix('.yaml.backup')
        shutil.copy2(yaml_path, backup_path)

    try:
        # Write to temp file in same directory (for atomic rename)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=yaml_path.parent,
            prefix='.metadata_',
            suffix='.yaml.tmp'
        )

        try:
            # Convert metadata for YAML serialization
            metadata_copy = metadata.copy()

            # Write YAML
            with os.fdopen(temp_fd, 'w') as f:
                yaml.safe_dump(
                    metadata_copy,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename
            shutil.move(temp_path, yaml_path)

            # Remove backup on success
            if backup_path and backup_path.exists():
                backup_path.unlink()

            logger.info(f"Successfully wrote metadata for {dataset_id}")

        except Exception as e:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise StorageError(f"Failed to write temp file: {e}") from e

    except Exception as e:
        # Restore from backup if available
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, yaml_path)
            backup_path.unlink()
            logger.warning(f"Restored {dataset_id} from backup after write failure")
        raise StorageError(f"Atomic write failed for {dataset_id}: {e}") from e


def reindex_record(dataset_id: str, metadata: Dict[str, Any]) -> None:
    """
    Update SQLite index for a single dataset record.

    Args:
        dataset_id: Dataset ID
        metadata: Updated metadata dictionary

    Raises:
        StorageError: If reindex fails
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Serialize metadata
        payload = json.dumps(metadata)

        # Update datasets_store
        cursor.execute("""
            INSERT OR REPLACE INTO datasets_store (id, payload, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (dataset_id, payload))

        # Delete old FTS entry
        cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))

        # Update FTS5 index with correct schema
        # Schema: id, name, description, used_in_projects, data_types, source, file_format
        name = metadata.get('dataset_name', '')
        description = metadata.get('description', '')
        used_in_projects = ' '.join(metadata.get('used_in_projects', []))
        data_types = ' '.join(metadata.get('data_types', []))
        source = metadata.get('source', '')
        file_format = metadata.get('file_format', '')

        cursor.execute("""
            INSERT INTO datasets_fts (id, name, description, used_in_projects, data_types, source, file_format)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (dataset_id, name, description, used_in_projects, data_types, source, file_format))

        conn.commit()
        logger.info(f"Reindexed {dataset_id} in SQLite")

    except Exception as e:
        conn.rollback()
        raise StorageError(f"Failed to reindex {dataset_id}: {e}") from e
    finally:
        conn.close()


def save_dataset_atomic(dataset_id: str, metadata: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Save dataset with atomic write and reindex.

    This is the main entry point for persisting dataset changes.
    Validates, writes YAML atomically, then updates SQLite index.

    Args:
        dataset_id: Dataset ID
        metadata: Metadata dictionary

    Returns:
        Tuple of (success, error_message)
    """
    # Validate first
    success, error, model = validate_metadata(metadata)
    if not success:
        return False, f"Validation failed: {error}"

    # Backup paths for rollback
    yaml_path = get_dataset_path(dataset_id)
    backup_path = None

    try:
        # Write YAML atomically
        write_yaml_atomic(dataset_id, metadata)

        # Update SQLite index
        reindex_record(dataset_id, metadata)

        return True, None

    except Exception as e:
        error_msg = f"Save failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def validate_field(field_name: str, field_value: Any, metadata: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a single field value in context of full metadata.

    Args:
        field_name: Name of field to validate
        field_value: Value to validate
        metadata: Full metadata dict with field updated

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Create a copy with the updated field
    test_metadata = metadata.copy()
    test_metadata[field_name] = field_value

    # Run full validation
    success, error, model = validate_metadata(test_metadata)

    if success:
        return True, None

    # Extract field-specific error if available
    if error and field_name in error:
        return False, error

    # Return generic error
    return False, f"Invalid value for {field_name}"
