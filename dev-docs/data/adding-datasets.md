# Adding Datasets

## Introduction

This guide explains how to add new datasets to Hei-DataHub's catalog system. It covers both manual entry and programmatic approaches.

---

## Manual Dataset Entry

### Via TUI

#### 1. Launch Application

```bash
mini-datahub
```

#### 2. Create New Dataset

**Keyboard shortcuts:**
- Press `n` - Create new dataset
- Or navigate to "Create Dataset" button and press Enter

#### 3. Fill Metadata Form

**Required Fields:**
- **Dataset Name:** Descriptive name
- **Description:** What the dataset contains
- **Storage Location:** Path or URL to data

**Optional Fields:**
- **Source:** Original source URL
- **Projects:** Which projects use this dataset
- **Data Types:** Type tags (time-series, geospatial, etc.)
- **File Format:** NetCDF, CSV, HDF5, etc.
- **Keywords:** Searchable tags
- **Access Level:** public, restricted, private
- **Contact Person:** Email address

#### 4. Save Dataset

- Press `Ctrl+S` or click "Save" button
- Dataset saved locally and synced to cloud

---

### Via CLI

```bash
# Interactive mode
mini-datahub create-dataset

# Follow prompts:
# Dataset Name: Climate Model Data
# Description: Historical climate outputs
# Storage Location: /data/climate/cmip6
# ...
```

---

## Programmatic Dataset Entry

### Python API

```python
from mini_datahub.services.dataset_service import save_dataset

# Define metadata
metadata = {
    "id": "climate-data",
    "dataset_name": "Climate Model Data",
    "description": "Historical climate model outputs from CMIP6",
    "source": "https://esgf-node.llnl.gov/",
    "date_created": "2024-01-15",
    "storage_location": "/data/climate/cmip6",
    "file_format": "NetCDF",
    "used_in_projects": ["climate-study", "future-projections"],
    "data_types": ["time-series", "geospatial"],
    "keywords": ["climate", "temperature", "precipitation"],
    "access_level": "public",
    "contact_person": "jane.doe@uni-heidelberg.de",
    "data_size_gb": 150.5,
    "documentation_url": "https://docs.example.com/climate-data"
}

# Save dataset (local + cloud sync)
save_dataset(metadata)
```

---

### Batch Import

```python
from mini_datahub.services.dataset_service import save_dataset
import json

# Load from JSON file
with open("datasets.json") as f:
    datasets = json.load(f)

# Import all datasets
for dataset in datasets:
    try:
        save_dataset(dataset)
        print(f"✓ Imported: {dataset['dataset_name']}")
    except Exception as e:
        print(f"✗ Failed: {dataset.get('dataset_name', 'unknown')} - {e}")
```

**Example datasets.json:**

```json
[
  {
    "id": "climate-data",
    "dataset_name": "Climate Model Data",
    "description": "Historical climate outputs",
    "storage_location": "/data/climate/cmip6",
    "file_format": "NetCDF",
    "used_in_projects": ["climate-study"],
    "keywords": ["climate", "temperature"]
  },
  {
    "id": "ocean-temp",
    "dataset_name": "Ocean Temperature Records",
    "description": "Ocean temperature measurements 1980-2024",
    "storage_location": "/data/ocean/temperature",
    "file_format": "CSV",
    "used_in_projects": ["ocean-research"],
    "keywords": ["ocean", "temperature"]
  }
]
```

---

### From CSV

```python
import csv
from mini_datahub.services.dataset_service import save_dataset

# Read from CSV
with open("datasets.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:
        metadata = {
            "id": row["id"],
            "dataset_name": row["name"],
            "description": row["description"],
            "storage_location": row["location"],
            "file_format": row["format"],
            "used_in_projects": row["projects"].split(";"),
            "keywords": row["keywords"].split(";")
        }

        save_dataset(metadata)
        print(f"✓ Imported: {metadata['dataset_name']}")
```

**Example datasets.csv:**

```csv
id,name,description,location,format,projects,keywords
climate-data,Climate Model Data,Historical climate outputs,/data/climate/cmip6,NetCDF,climate-study,climate;temperature
ocean-temp,Ocean Temperature Records,Ocean temps 1980-2024,/data/ocean/temperature,CSV,ocean-research,ocean;temperature
```

---

## Metadata Schema

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier | `"climate-data"` |
| `dataset_name` | string | Human-readable name | `"Climate Model Data"` |
| `description` | string | Detailed description | `"Historical climate..."` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `source` | string | Origin URL | `"https://esgf-node.llnl.gov/"` |
| `date_created` | string | Creation date (ISO 8601) | `"2024-01-15"` |
| `storage_location` | string | Data path/URL | `"/data/climate/cmip6"` |
| `file_format` | string | File format | `"NetCDF"`, `"CSV"`, `"HDF5"` |
| `used_in_projects` | list[string] | Project names | `["climate-study"]` |
| `data_types` | list[string] | Type tags | `["time-series", "geospatial"]` |
| `keywords` | list[string] | Search keywords | `["climate", "temperature"]` |
| `access_level` | string | Access control | `"public"`, `"restricted"`, `"private"` |
| `contact_person` | string | Email address | `"jane.doe@example.com"` |
| `data_size_gb` | float | Size in GB | `150.5` |
| `documentation_url` | string | Docs URL | `"https://docs.example.com/"` |
| `license` | string | Data license | `"CC-BY-4.0"`, `"Proprietary"` |
| `version` | string | Dataset version | `"v1.0"`, `"2024-01-15"` |
| `last_updated` | string | Last update date | `"2024-03-10"` |

---

### Field Validation

**ID Format:**
- Lowercase alphanumeric and hyphens only
- No spaces or special characters
- Example: `climate-data`, `ocean-temp-2024`

```python
import re

def validate_id(dataset_id: str) -> bool:
    """Validate dataset ID format"""
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, dataset_id))
```

**Date Format:**
- ISO 8601: `YYYY-MM-DD`
- Example: `2024-01-15`

**Email Format:**
- Valid email address for `contact_person`
- Example: `jane.doe@uni-heidelberg.de`

---

## Cloud Sync

### Automatic Sync

Datasets are automatically synced to WebDAV cloud storage:

```python
save_dataset(metadata)
# 1. Saved to local SQLite
# 2. Indexed in FTS5
# 3. Uploaded to WebDAV (async)
# 4. If upload fails → saved to outbox
```

---

### Manual Sync Trigger

```bash
# Sync all datasets
mini-datahub sync now

# Sync specific dataset
mini-datahub sync --dataset climate-data
```

---

### Outbox Management

Failed uploads are queued in outbox:

**Location:** `~/.local/share/mini-datahub/outbox/`

```bash
# List outbox contents
mini-datahub outbox list

# Retry failed uploads
mini-datahub outbox retry

# Clear outbox (after manual sync)
mini-datahub outbox clear
```

---

## Bulk Import from External Sources

### From DSpace Repository

```python
import requests
from mini_datahub.services.dataset_service import save_dataset

# Fetch from DSpace REST API
response = requests.get("https://dspace.example.org/rest/items")
items = response.json()

for item in items:
    metadata = {
        "id": item["handle"].replace("/", "-"),
        "dataset_name": item["name"],
        "description": item["metadata"].get("dc.description", ""),
        "source": f"https://dspace.example.org/handle/{item['handle']}",
        "date_created": item["metadata"].get("dc.date.issued", ""),
        "keywords": item["metadata"].get("dc.subject", "").split("; ")
    }

    save_dataset(metadata)
```

---

### From CKAN API

```python
import requests
from mini_datahub.services.dataset_service import save_dataset

# Fetch from CKAN API
response = requests.get("https://data.gov.uk/api/3/action/package_list")
package_ids = response.json()["result"]

for package_id in package_ids[:10]:  # First 10
    pkg_response = requests.get(
        f"https://data.gov.uk/api/3/action/package_show?id={package_id}"
    )
    pkg = pkg_response.json()["result"]

    metadata = {
        "id": pkg["name"],
        "dataset_name": pkg["title"],
        "description": pkg["notes"],
        "source": f"https://data.gov.uk/dataset/{pkg['name']}",
        "keywords": [tag["name"] for tag in pkg["tags"]],
        "license": pkg.get("license_title", "Unknown")
    }

    save_dataset(metadata)
```

---

### From File System Scan

```python
from pathlib import Path
from mini_datahub.services.dataset_service import save_dataset

# Scan directory for NetCDF files
data_dir = Path("/data/climate")

for nc_file in data_dir.rglob("*.nc"):
    # Extract metadata from filename
    dataset_id = nc_file.stem.lower().replace("_", "-")

    metadata = {
        "id": dataset_id,
        "dataset_name": nc_file.stem.replace("_", " ").title(),
        "description": f"NetCDF file: {nc_file.name}",
        "storage_location": str(nc_file),
        "file_format": "NetCDF",
        "data_size_gb": nc_file.stat().st_size / (1024**3)
    }

    save_dataset(metadata)
    print(f"✓ Added: {metadata['dataset_name']}")
```

---

## Updating Datasets

### Update Existing Dataset

```python
from mini_datahub.services.dataset_service import get_dataset, save_dataset

# Fetch existing dataset
dataset = get_dataset("climate-data")

# Update fields
dataset["description"] = "Updated description with more details"
dataset["keywords"].append("CMIP6")
dataset["last_updated"] = "2024-03-10"

# Save (overwrites existing)
save_dataset(dataset)
```

---

### Partial Update

```python
from mini_datahub.services.dataset_service import update_dataset_fields

# Update specific fields only
update_dataset_fields(
    dataset_id="climate-data",
    fields={
        "description": "New description",
        "keywords": ["climate", "temperature", "CMIP6"]
    }
)
```

---

## Deleting Datasets

### Delete via TUI

1. Navigate to dataset in list
2. Press `d` (delete key)
3. Confirm deletion

### Delete via CLI

```bash
mini-datahub delete-dataset climate-data
```

### Delete via API

```python
from mini_datahub.services.dataset_service import delete_dataset

delete_dataset("climate-data")
# Deletes from local index AND cloud storage
```

---

## Validation

### Schema Validation

```python
from mini_datahub.core.models import DatasetMetadata
from pydantic import ValidationError

try:
    # Validate metadata
    validated = DatasetMetadata.model_validate(metadata)
    print("✓ Metadata valid")
except ValidationError as e:
    print(f"✗ Validation errors:")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg']}")
```

---

### Custom Validation

```python
def validate_dataset(metadata: dict) -> list[str]:
    """Custom validation with detailed errors"""
    errors = []

    # Required fields
    if not metadata.get("id"):
        errors.append("ID is required")
    elif not re.match(r'^[a-z0-9-]+$', metadata["id"]):
        errors.append("ID must be lowercase alphanumeric with hyphens")

    if not metadata.get("dataset_name"):
        errors.append("Dataset name is required")

    # Optional field validation
    if "data_size_gb" in metadata:
        if not isinstance(metadata["data_size_gb"], (int, float)):
            errors.append("data_size_gb must be a number")
        elif metadata["data_size_gb"] < 0:
            errors.append("data_size_gb cannot be negative")

    if "access_level" in metadata:
        valid_levels = {"public", "restricted", "private"}
        if metadata["access_level"] not in valid_levels:
            errors.append(f"access_level must be one of: {valid_levels}")

    return errors

# Usage
errors = validate_dataset(metadata)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    save_dataset(metadata)
```

---

## Best Practices

### 1. Use Descriptive IDs

```python
# ✅ GOOD: Descriptive, readable IDs
"climate-model-cmip6-historical"
"ocean-temperature-pacific-2024"

# ❌ BAD: Generic, unclear IDs
"dataset1"
"data"
"temp"
```

---

### 2. Provide Detailed Descriptions

```python
# ✅ GOOD: Comprehensive description
description = """
Historical climate model outputs from CMIP6 experiment.
Includes temperature, precipitation, and wind data for
1850-2014 period. Resolution: 1°x1° global grid.
Variables: tas, pr, uas, vas.
"""

# ❌ BAD: Vague description
description = "Climate data"
```

---

### 3. Use Consistent Keywords

```python
# ✅ GOOD: Consistent, specific tags
keywords = ["climate", "temperature", "CMIP6", "historical", "global"]

# ❌ BAD: Inconsistent, too generic
keywords = ["Climate", "TEMP", "data", "stuff"]
```

---

### 4. Include Contact Information

```python
# ✅ GOOD: Actual contact
contact_person = "jane.doe@uni-heidelberg.de"

# ❌ BAD: No contact or generic
contact_person = "admin@example.com"
```

---

## Troubleshooting

### Dataset Not Appearing in Search

**Possible causes:**
1. Index not updated
2. Sync failed
3. Invalid metadata

**Solutions:**

```bash
# Rebuild search index
mini-datahub rebuild-index

# Force sync
mini-datahub sync now --force

# Check dataset exists
mini-datahub get-dataset climate-data
```

---

### Upload to Cloud Failed

**Check outbox:**

```bash
mini-datahub outbox list
```

**Retry upload:**

```bash
mini-datahub outbox retry
```

**Check network connection:**

```bash
mini-datahub auth doctor
```

---

## Related Documentation

- **[Data Layer Overview](overview.md)** - Data architecture
- **[Schema](schema.md)** - Database schema
- **[Storage](storage.md)** - Storage mechanisms
- **[Core Module](../codebase/core-module.md)** - Data models

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
