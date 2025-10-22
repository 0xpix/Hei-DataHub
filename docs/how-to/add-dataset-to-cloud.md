# Add Datasets Directly to Cloud Storage

**Requirements:** Hei-DataHub 0.59-beta or later with WebDAV/Heibox configured

Learn how to add datasets directly to your cloud storage (Heibox/Seafile) so everyone with access can immediately see and use them in Hei-DataHub.

---

## Overview

Instead of creating GitHub Pull Requests, you can add datasets directly to your cloud storage (Heibox/Seafile). This approach:

✅ **Immediate access** - No PR review needed, datasets appear instantly
✅ **Simple workflow** - Just upload a folder with metadata.yaml
✅ **Team collaboration** - Everyone with Heibox access can add datasets
✅ **No GitHub account** - No need for tokens or repository permissions

**Time:** 5 minutes per dataset

---

## Prerequisites

### 1. WebDAV Storage Configured

Ensure Hei-DataHub is configured to use cloud storage:

```bash
# Check your config
cat ~/.config/hei-datahub/config.yaml
```

Should contain:

```yaml
storage:
  backend: webdav
  base_url: https://heibox.uni-heidelberg.de/seafdav
  library: DATA-CATALOG-DIRECTORY-NAME
  username: your-username@auth.local
  password_env: HEIBOX_WEBDAV_TOKEN
```

👉 [Setup WebDAV guide](../installation/cloud-storage-setup.md)

### 2. Access to Heibox Library

- You need **write access** to the Seafile library (e.g., `Testing-hei-datahub`)
- Access through: [https://heibox.uni-heidelberg.de](https://heibox.uni-heidelberg.de)

---

## Dataset Structure

Each dataset is a **directory** containing a `metadata.yaml` file:

```
Testing-hei-datahub/          # Your Seafile library
├── precipitation/            # Dataset 1
│   ├── metadata.yaml        # ← Required metadata
│   ├── data.nc              # Optional: actual data files
│   └── README.md            # Optional: additional docs
├── land-cover/              # Dataset 2
│   ├── metadata.yaml
│   └── data.tif
└── temperature/             # Dataset 3
    └── metadata.yaml
```

**Key points:**

- Directory name = Dataset ID (use lowercase with dashes: `my-dataset`)
- `metadata.yaml` is **required** in each directory
- Additional files (data, docs) are optional but recommended

---

## Quick Start: Add Your First Dataset

### Option 1: Via Web Interface (Easiest)

#### 1. Open Heibox

Navigate to your Seafile library:
```
https://heibox.uni-heidelberg.de/library/<library-id>/Testing-hei-datahub/
```

#### 2. Create New Folder

1. Click **"New Folder"** button
2. Name it using lowercase with dashes: `global-temperature-2024`
3. Press Enter to create

#### 3. Upload metadata.yaml

1. Click into your new folder: `global-temperature-2024/`
2. Click **"Upload"** button
3. Select your prepared `metadata.yaml` file
4. Wait for upload to complete

#### 4. (Optional) Upload Data Files

Upload any additional files:
- Data files (`.nc`, `.tif`, `.csv`, etc.)
- Documentation (`README.md`, `CHANGELOG.md`)
- Scripts or notebooks

#### 5. Verify in Hei-DataHub

```bash
# Launch the TUI
hei-datahub
```

Your new dataset should appear immediately in the main screen! 🎉

---

### Option 2: Via WebDAV (Advanced)

If you prefer command-line access:

#### 1. Mount WebDAV as Drive

**Linux (davfs2):**
```bash
# Install davfs2
sudo apt install davfs2  # Ubuntu/Debian
sudo dnf install davfs2  # Fedora

# Create mount point
mkdir -p ~/heibox-mount

# Mount
echo "your-token" > ~/.davfs2/secrets
chmod 600 ~/.davfs2/secrets
mount -t davfs https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub ~/heibox-mount
```

**macOS (Finder):**
```
1. Finder → Go → Connect to Server (⌘K)
2. Server: https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub
3. Connect with your credentials
```

**Windows (Network Drive):**
```
1. Right-click "This PC" → Map network drive
2. Folder: https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub
3. Check "Connect using different credentials"
4. Enter username and token
```

#### 2. Create Dataset Directory

```bash
# Navigate to mounted drive
cd ~/heibox-mount  # Linux
cd /Volumes/Testing-hei-datahub  # macOS

# Create dataset folder
mkdir -p global-temperature-2024
cd global-temperature-2024
```

#### 3. Create metadata.yaml

```bash
cat > metadata.yaml << 'EOF'
name: Global Temperature Dataset 2024
description: |
  Daily temperature measurements from weather stations worldwide.
  Quality-controlled and gap-filled. Coverage: 2020-2024.
  Spatial resolution: point data from 10,000+ stations.

source: https://github.com/example/temperature-data
license: CC BY 4.0
date_created: '2024-10-22'

temporal_coverage:
  start: '2020-01-01'
  end: '2024-10-22'

spatial_coverage:
  type: global
  description: Worldwide coverage with higher density in North America and Europe

keywords:
  - climate
  - temperature
  - weather
  - timeseries
  - quality-controlled

file_format: NetCDF
size: ~2.5 GB

storage_location: heibox://Testing-hei-datahub/global-temperature-2024/

data_types:
  - Daily Mean Temperature (°C)
  - Daily Min Temperature (°C)
  - Daily Max Temperature (°C)

used_in_projects:
  - Climate Trends Analysis
  - Weather Prediction Model

notes: |
  Station density varies by region. QA flags included.
  See README.md for processing details.
EOF
```

#### 4. Upload Data Files (Optional)

```bash
# Copy your data files
cp /path/to/temperature_data.nc .
cp /path/to/README.md .
```

#### 5. Sync and Verify

```bash
# Ensure files are synced (WebDAV may cache)
sync

# Check in Hei-DataHub
hei-datahub
```

---

## metadata.yaml Template

Use this template for new datasets:

```yaml
# Required fields
name: Your Dataset Name Here
description: |
  Detailed description of what this dataset contains.
  Include coverage, quality, and important context.
  Multiple lines are fine.

source: https://source-url-or-citation-here
license: CC BY 4.0  # or CC0, MIT, proprietary, etc.
date_created: '2024-10-22'  # YYYY-MM-DD format

# Temporal coverage (recommended)
temporal_coverage:
  start: '2020-01-01'
  end: '2024-12-31'
  resolution: daily  # or monthly, yearly, etc.

# Spatial coverage (recommended)
spatial_coverage:
  type: global  # or regional, national, local
  description: Geographic extent and any important spatial notes
  # Optional: add bounding box
  # bbox: [-180, -90, 180, 90]  # [west, south, east, north]

# Keywords for search (recommended)
keywords:
  - domain-keyword
  - data-type-keyword
  - source-keyword
  - theme-keyword

# File information (recommended)
file_format: NetCDF  # or GeoTIFF, CSV, Parquet, etc.
size: ~2.5 GB  # approximate size

# Storage location (recommended)
storage_location: heibox://Testing-hei-datahub/your-dataset-name/
# Or: s3://bucket/path/, /mnt/data/path/, etc.

# Data variables (optional)
data_types:
  - Variable 1 (units)
  - Variable 2 (units)
  - Variable 3 (units)

# Project links (optional)
used_in_projects:
  - Project Name 1
  - Project Name 2

# Additional notes (optional)
notes: |
  Any additional context, warnings, or documentation.
  Known issues, processing notes, access requirements, etc.

# Contact info (optional)
contact:
  name: Your Name
  email: your.email@example.com
  organization: Your Institution

# Version info (optional)
version: 1.0.0
last_updated: '2024-10-22'
```

---

## Best Practices

### 1. Naming Conventions

**Directory names** (dataset IDs):
- ✅ Use lowercase: `my-dataset` not `My-Dataset`
- ✅ Use hyphens for spaces: `land-cover-data`
- ✅ Be descriptive: `modis-burned-area-2023`
- ❌ Avoid: `dataset1`, `test`, `new-folder`

**Dataset names** (in metadata.yaml):
- ✅ Use title case: `MODIS Burned Area 2023`
- ✅ Include scope: `European Precipitation Records`
- ✅ Be specific: `Global Daily Temperature 0.5° 2020-2024`

### 2. Required Metadata

Minimum viable metadata.yaml:

```yaml
name: Dataset Name
description: What this dataset contains
source: Where it came from
license: License type
date_created: '2024-10-22'
```

But **strongly recommended** to include:
- `temporal_coverage` - when the data is from
- `spatial_coverage` - where the data covers
- `keywords` - for searchability
- `file_format` - what format the data is in
- `storage_location` - where files are stored

### 3. Documentation Files

Consider adding alongside `metadata.yaml`:

- **README.md** - Processing details, usage instructions
- **CHANGELOG.md** - Version history
- **LICENSE.txt** - Full license text
- **CITATION.cff** - Citation information
- **quality_report.pdf** - Quality assessment docs

### 4. Data Organization

For datasets with many files:

```
your-dataset/
├── metadata.yaml           # Required
├── README.md              # Recommended
├── data/                  # Organize by subdirs
│   ├── 2020/
│   ├── 2021/
│   └── 2022/
├── docs/                  # Documentation
│   └── processing.md
└── scripts/               # Processing code
    └── process.py
```

### 5. Keep It Updated

When you update data files:
- Update `last_updated` field in metadata.yaml
- Update `version` if you use semantic versioning
- Document changes in `notes` or CHANGELOG.md

---

## Search Your Datasets

Once added, search using field queries:

```bash
# Launch TUI
hei-datahub

# Press / to search
```

**Example queries:**

- `project:Gideon` - Find datasets used in project "Gideon"
- `license:CC BY` - Find openly licensed datasets
- `keyword:climate` - Find climate-related datasets
- `temporal:2024` - Find datasets covering 2024

👉 [Advanced search guide](07-search-advanced.md)

---

## View and Manage

### View Dataset Details

1. Navigate to dataset in main screen (use `j`/`k`)
2. Press `Enter` to open details
3. See all metadata fields formatted nicely
4. Press `y` to copy storage location

### Edit Dataset

To update metadata:

**Option 1: Edit via Heibox Web**
1. Navigate to dataset folder
2. Click on `metadata.yaml`
3. Click "Edit" button
4. Make changes
5. Save
6. Relaunch `hei-datahub` to see updates

**Option 2: Edit via WebDAV mount**
```bash
cd ~/heibox-mount/your-dataset
nano metadata.yaml  # or vim, emacs, etc.
# Make changes, save
```

**Option 3: Edit locally and upload**
```bash
# Download current metadata
curl -u "username:token" \
  https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub/your-dataset/metadata.yaml \
  -o metadata.yaml

# Edit
nano metadata.yaml

# Upload back
curl -u "username:token" \
  -T metadata.yaml \
  https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub/your-dataset/metadata.yaml
```

### Delete Dataset

Simply delete the folder from Heibox (web interface or WebDAV).

**Warning:** This is permanent! Consider archiving instead:
```bash
# Rename to archive
mv precipitation precipitation-archived-2024-10-22
```

---

## Team Collaboration

### Share Library Access

1. Open Seafile library settings
2. Click "Share" button
3. Add team members by email
4. Set permissions:
   - **Read-only** - Can view datasets in Hei-DataHub
   - **Read-Write** - Can add/edit datasets

### Workflow Example

**For a research group:**

1. **Data Owner** creates dataset folder with metadata.yaml
2. **Team Members** can immediately browse via Hei-DataHub
3. **Collaborators** add their projects to `used_in_projects`
4. **Data Manager** reviews and updates `notes` field

No GitHub, no PRs, no delays! ⚡

---

## Troubleshooting

### "No datasets showing"

**Check:**
1. Storage backend configured correctly:
   ```bash
   cat ~/.config/hei-datahub/config.yaml | grep backend
   # Should show: backend: webdav
   ```

2. Environment variable set:
   ```bash
   echo $HEIBOX_WEBDAV_TOKEN
   # Should show your token
   ```

3. Library name matches:
   ```bash
   # In config.yaml, should match Seafile library name exactly
   library: Testing-hei-datahub
   ```

4. Restart Hei-DataHub:
   ```bash
   hei-datahub
   ```

### "Permission denied"

**Cause:** No write access to Seafile library

**Solution:** Ask library owner to grant you write permissions

### "metadata.yaml not found"

**Cause:** Dataset folder missing metadata.yaml

**Solution:** Every dataset folder **must** have a metadata.yaml file. Add one using the template above.

### "Invalid YAML syntax"

**Cause:** Syntax error in metadata.yaml

**Validate:**
```bash
# Install yamllint
pip install yamllint

# Check syntax
yamllint metadata.yaml
```

**Common mistakes:**
- Missing quotes around dates: `date_created: 2024-10-22` ❌ → `date_created: '2024-10-22'` ✅
- Wrong indentation (use 2 spaces)
- Forgot pipe `|` for multi-line strings

---

## Migration from GitHub

If you have existing datasets in a GitHub repository:

### 1. Export from GitHub

```bash
# Clone your dataset repo
git clone https://github.com/your-org/datasets.git
cd datasets/data
```

### 2. Upload to Heibox

**Via Web:**
- Drag and drop each dataset folder to Heibox web interface

**Via WebDAV:**
```bash
# Mount Heibox
mount -t davfs https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub ~/heibox-mount

# Copy all datasets
cp -r * ~/heibox-mount/

# Sync
sync
```

### 3. Update Config

Switch Hei-DataHub to use WebDAV:

```bash
# Edit config
nano ~/.config/hei-datahub/config.yaml
```

Change:
```yaml
storage:
  backend: webdav  # was: filesystem
  base_url: https://heibox.uni-heidelberg.de/seafdav
  library: Testing-hei-datahub
  username: your-username@auth.local
  password_env: HEIBOX_WEBDAV_TOKEN
```

### 4. Verify

```bash
hei-datahub
```

All your datasets should now load from Heibox! 🎉

---

## Advanced: Programmatic Upload

For bulk operations or CI/CD:

### Python Script

```python
#!/usr/bin/env python3
"""Upload dataset to Heibox programmatically."""

import requests
import os
import yaml

# Configuration
BASE_URL = "https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub"
USERNAME = "your-username@auth.local"
TOKEN = os.environ["HEIBOX_WEBDAV_TOKEN"]

def create_dataset(dataset_id: str, metadata: dict):
    """Create dataset folder and upload metadata."""

    # Create directory (MKCOL method)
    url = f"{BASE_URL}/{dataset_id}"
    response = requests.request(
        "MKCOL",
        url,
        auth=(USERNAME, TOKEN)
    )

    if response.status_code not in [201, 405]:  # 405 = already exists
        raise Exception(f"Failed to create folder: {response.status_code}")

    # Upload metadata.yaml
    metadata_yaml = yaml.dump(metadata, sort_keys=False)
    url = f"{BASE_URL}/{dataset_id}/metadata.yaml"
    response = requests.put(
        url,
        data=metadata_yaml.encode('utf-8'),
        auth=(USERNAME, TOKEN),
        headers={'Content-Type': 'text/yaml'}
    )

    if response.status_code not in [201, 204]:
        raise Exception(f"Failed to upload metadata: {response.status_code}")

    print(f"✅ Created dataset: {dataset_id}")

# Example usage
metadata = {
    'name': 'My New Dataset',
    'description': 'Dataset created programmatically',
    'source': 'https://example.com/data',
    'license': 'CC BY 4.0',
    'date_created': '2024-10-22',
    'keywords': ['example', 'test'],
}

create_dataset('my-new-dataset', metadata)
```

### Bash Script

```bash
#!/bin/bash
# upload_dataset.sh - Upload dataset to Heibox

DATASET_ID="$1"
METADATA_FILE="$2"

BASE_URL="https://heibox.uni-heidelberg.de/seafdav/Testing-hei-datahub"
USERNAME="your-username@auth.local"
TOKEN="$HEIBOX_WEBDAV_TOKEN"

# Create folder
curl -X MKCOL \
  -u "${USERNAME}:${TOKEN}" \
  "${BASE_URL}/${DATASET_ID}"

# Upload metadata
curl -X PUT \
  -u "${USERNAME}:${TOKEN}" \
  -T "${METADATA_FILE}" \
  "${BASE_URL}/${DATASET_ID}/metadata.yaml"

echo "✅ Uploaded dataset: ${DATASET_ID}"
```

Usage:
```bash
./upload_dataset.sh precipitation ./precipitation/metadata.yaml
```

---

## Next Steps

- 👉 [Search your datasets](07-search-advanced.md)
- 👉 [Customize metadata fields](../reference/metadata-schema.md)
- 👉 [Configure cloud storage](../installation/cloud-storage-setup.md)
- 👉 [Team collaboration guide](../reference/collaboration.md)

---

## Summary

**To add a dataset to Heibox:**

1. ✅ Create folder in Seafile library (lowercase-with-dashes)
2. ✅ Add `metadata.yaml` with required fields
3. ✅ (Optional) Upload data files and docs
4. ✅ Launch `hei-datahub` - dataset appears immediately!

**No GitHub, no PRs, instant collaboration!** 🚀
