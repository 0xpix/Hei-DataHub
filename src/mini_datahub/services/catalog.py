"""
Catalog service: Orchestrates dataset operations (add, update, validate).
"""
from typing import Optional, Tuple

from mini_datahub.core.models import DatasetMetadata
from mini_datahub.infra.store import (
    validate_metadata,
    read_dataset,
    write_dataset,
    make_unique_id,
)
from mini_datahub.infra.index import upsert_dataset


def save_dataset(dataset_id: str, metadata: dict) -> Tuple[bool, Optional[str]]:
    """
    Save dataset: validate, write to YAML, and index.

    Args:
        dataset_id: Dataset ID
        metadata: Metadata dictionary

    Returns:
        Tuple of (success, error_message)
    """
    # Validate
    success, error, model = validate_metadata(metadata)
    if not success:
        return False, error

    try:
        # Write to YAML
        write_dataset(dataset_id, metadata)

        # Index for search
        upsert_dataset(dataset_id, metadata)

        return True, None
    except Exception as e:
        return False, f"Failed to save dataset: {str(e)}"


def get_dataset(dataset_id: str) -> Optional[dict]:
    """
    Get dataset metadata.

    Args:
        dataset_id: Dataset ID

    Returns:
        Metadata dictionary or None
    """
    return read_dataset(dataset_id)


def generate_id(base_name: str) -> str:
    """
    Generate a unique dataset ID.

    Args:
        base_name: Base name (usually dataset_name)

    Returns:
        Unique ID
    """
    return make_unique_id(base_name)
