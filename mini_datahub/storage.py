"""
Storage module: YAML read/write, validation, and dataset listing.
"""
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate as json_schema_validate
from pydantic import ValidationError as PydanticValidationError

from mini_datahub.models import DatasetMetadata
from mini_datahub.utils import DATA_DIR, SCHEMA_PATH


def slugify(text: str) -> str:
    """
    Convert text to a valid slug for use as dataset ID.

    Args:
        text: Input text (e.g., dataset name)

    Returns:
        A lowercase slug with hyphens
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove any character that isn't alphanumeric, hyphen, or underscore
    text = re.sub(r"[^a-z0-9-_]", "", text)
    # Remove leading/trailing hyphens
    text = text.strip("-_")
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    return text


def generate_unique_id(base_name: str) -> str:
    """
    Generate a unique dataset ID from a base name, handling collisions.

    Args:
        base_name: Base name to convert to ID (usually dataset name)

    Returns:
        A unique ID (slug)
    """
    slug = slugify(base_name)
    if not slug:
        slug = "dataset"

    # Check if this ID already exists
    original_slug = slug
    counter = 1
    while dataset_exists(slug):
        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug


def dataset_exists(dataset_id: str) -> bool:
    """Check if a dataset with the given ID exists."""
    dataset_path = DATA_DIR / dataset_id / "metadata.yaml"
    return dataset_path.exists()


def get_dataset_path(dataset_id: str) -> Path:
    """Get the path to a dataset's metadata file."""
    return DATA_DIR / dataset_id / "metadata.yaml"


def load_json_schema() -> dict:
    """Load the JSON Schema for validation."""
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


def validate_with_json_schema(data: dict) -> None:
    """
    Validate data against JSON Schema.

    Args:
        data: Dataset metadata dictionary

    Raises:
        JSONSchemaValidationError: If validation fails
    """
    schema = load_json_schema()
    json_schema_validate(instance=data, schema=schema)


def validate_with_pydantic(data: dict) -> DatasetMetadata:
    """
    Validate data with Pydantic model.

    Args:
        data: Dataset metadata dictionary

    Returns:
        Validated DatasetMetadata instance

    Raises:
        PydanticValidationError: If validation fails
    """
    return DatasetMetadata(**data)


def validate_metadata(data: dict) -> tuple[bool, Optional[str], Optional[DatasetMetadata]]:
    """
    Validate metadata with both JSON Schema and Pydantic.

    Args:
        data: Dataset metadata dictionary

    Returns:
        Tuple of (success, error_message, validated_model)
    """
    try:
        # First validate with JSON Schema
        validate_with_json_schema(data)
        # Then validate with Pydantic for additional type checking
        model = validate_with_pydantic(data)
        return True, None, model
    except JSONSchemaValidationError as e:
        return False, f"JSON Schema validation failed: {e.message}", None
    except PydanticValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            msg = error["msg"]
            errors.append(f"{field}: {msg}")
        return False, "Validation failed:\n" + "\n".join(errors), None
    except Exception as e:
        return False, f"Unexpected validation error: {str(e)}", None


def read_dataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    """
    Read dataset metadata from YAML file.

    Args:
        dataset_id: Dataset ID

    Returns:
        Dictionary of metadata, or None if not found
    """
    path = get_dataset_path(dataset_id)
    if not path.exists():
        return None

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Convert date objects to strings for consistency
    if isinstance(data.get("date_created"), date):
        data["date_created"] = data["date_created"].isoformat()
    if isinstance(data.get("last_updated"), date):
        data["last_updated"] = data["last_updated"].isoformat()

    return data


def write_dataset(dataset_id: str, metadata: dict) -> None:
    """
    Write dataset metadata to YAML file.

    Args:
        dataset_id: Dataset ID
        metadata: Metadata dictionary
    """
    dataset_dir = DATA_DIR / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    path = get_dataset_path(dataset_id)

    # Convert date objects to strings for YAML serialization
    metadata_copy = metadata.copy()
    if isinstance(metadata_copy.get("date_created"), date):
        metadata_copy["date_created"] = metadata_copy["date_created"].isoformat()
    if isinstance(metadata_copy.get("last_updated"), date):
        metadata_copy["last_updated"] = metadata_copy["last_updated"].isoformat()

    with open(path, "w") as f:
        yaml.safe_dump(metadata_copy, f, default_flow_style=False, sort_keys=False)


def list_datasets() -> List[str]:
    """
    List all dataset IDs (subdirectories with metadata.yaml).

    Returns:
        List of dataset IDs
    """
    if not DATA_DIR.exists():
        return []

    datasets = []
    for item in DATA_DIR.iterdir():
        if item.is_dir() and (item / "metadata.yaml").exists():
            datasets.append(item.name)

    return sorted(datasets)


def save_dataset(metadata: dict) -> tuple[bool, str]:
    """
    Validate and save a dataset.

    Args:
        metadata: Dataset metadata dictionary

    Returns:
        Tuple of (success, message)
    """
    # Validate first
    success, error_msg, model = validate_metadata(metadata)
    if not success:
        return False, error_msg

    # Write to disk
    try:
        dataset_id = metadata["id"]
        write_dataset(dataset_id, metadata)
        return True, f"Dataset '{dataset_id}' saved successfully"
    except Exception as e:
        return False, f"Failed to write dataset: {str(e)}"
