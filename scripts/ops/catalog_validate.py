#!/usr/bin/env python3
"""
Validate all catalog metadata files against the JSON Schema.
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import ValidationError, validate

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCHEMA_FILE = PROJECT_ROOT / "schema.json"


def load_schema():
    """Load the JSON Schema."""
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)


def validate_metadata_file(metadata_path: Path, schema: dict) -> tuple[bool, str]:
    """
    Validate a single metadata file.

    Returns:
        (success, error_message)
    """
    try:
        with open(metadata_path, "r") as f:
            data = yaml.safe_load(f)

        # Validate against schema
        validate(instance=data, schema=schema)

        # Check required fields
        if not data.get("id"):
            return False, "Missing required field: id"

        # Check that ID matches directory name
        expected_id = metadata_path.parent.name
        if data["id"] != expected_id:
            return False, f"ID mismatch: {data['id']} != {expected_id}"

        return True, ""

    except ValidationError as e:
        return False, f"Schema validation error: {e.message}"
    except Exception as e:
        return False, f"Error loading file: {str(e)}"


def main():
    """Main validation routine."""
    if not DATA_DIR.exists():
        print("✓ No data directory found, skipping validation")
        sys.exit(0)

    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)

    print(f"📋 Validating catalog metadata...")
    print(f"Schema: {SCHEMA_FILE}")
    print(f"Data dir: {DATA_DIR}")
    print()

    schema = load_schema()

    # Find all metadata.yaml files
    metadata_files = list(DATA_DIR.glob("*/metadata.yaml"))

    if not metadata_files:
        print("✓ No metadata files found")
        sys.exit(0)

    print(f"Found {len(metadata_files)} metadata file(s)\n")

    errors = []
    for metadata_file in metadata_files:
        dataset_id = metadata_file.parent.name
        success, error = validate_metadata_file(metadata_file, schema)

        if success:
            print(f"  ✓ {dataset_id}")
        else:
            print(f"  ❌ {dataset_id}: {error}")
            errors.append((dataset_id, error))

    print()

    if errors:
        print(f"❌ Validation failed for {len(errors)} dataset(s):")
        for dataset_id, error in errors:
            print(f"  • {dataset_id}: {error}")
        sys.exit(1)
    else:
        print(f"✓ All {len(metadata_files)} datasets validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
