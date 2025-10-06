
This hands-on tutorial will walk you through adding your first dataset to Hei-DataHub, from launching the TUI to verifying it appears in search results.

---

## What You'll Learn

- How to launch Hei-DataHub TUI
- How to navigate the Add Dataset form
- How to fill in required and optional fields
- How to save and verify a new dataset
- How to find your dataset via search

**Time:** ~10 minutes

---

## Prerequisites

- Hei-DataHub installed ([Installation Tutorial](01-installation.md))
- Virtual environment activated
- Basic familiarity with terminal

---

## Step 1: Launch Hei-DataHub

Open your terminal and run:

```bash
cd /path/to/Hei-DataHub
source .venv/bin/activate
hei-datahub
```

**Expected:** Home screen with search box and dataset list.

---

## Step 2: Open Add Dataset Form

Press ++a++ (the "Add Dataset" shortcut).

**Expected:** Add Dataset form appears.

```
┌────────────────────────────────────────────────┐
│  HEI DATAHUB - Add Dataset                     │
├────────────────────────────────────────────────┤
│  Dataset ID:                                   │
│  [                    ] (auto-generated)       │
│  ...                                           │
└────────────────────────────────────────────────┘
```

---

## Step 3: Fill in Required Fields

Required fields are marked with an asterisk (*).

### Dataset Name *

**What:** Human-readable name for your dataset.

**Example:** `Global Weather Stations 2024`

**Tips:**

- Use title case
- Be specific and descriptive
- Include time range if applicable

**Enter:**

```
Global Weather Stations 2024
```

Press ++tab++ to move to the next field.

---

### Description *

**What:** Detailed description of the dataset contents.

**Example:**

```
Daily weather observations from 10,000+ stations worldwide.
Includes temperature, precipitation, wind speed, and humidity.
Data quality-controlled and gap-filled where possible.
```

**Tips:**

- 2-4 sentences is ideal
- Mention data source, coverage, and format
- Include any important caveats

**Enter:**

```
Daily weather observations from 10,000+ stations worldwide.
Includes temperature, precipitation, wind speed, and humidity.
Data quality-controlled and gap-filled where possible.
```

Press ++tab++ to move to the next field.

---

### Source *

**What:** URL or code snippet showing where the data came from.

**Example (URL):**

```
https://github.com/weatherdata/global-stations
```

**Example (Code snippet):**

```python
import pandas as pd
df = pd.read_csv("https://data.example.com/weather.csv")
```

**Tips:**

- Prefer URLs when available
- For library/API data, include import statements
- Multi-line snippets are fine

**Enter:**

```
https://github.com/weatherdata/global-stations
```

Press ++tab++ to move to the next field.

---

### Date Created

**What:** Date the dataset was created (ISO 8601 format: `YYYY-MM-DD`).

**Default:** Today's date (auto-filled).

**Example:** `2024-10-04`

**Enter:** Leave as-is or modify if needed.

Press ++tab++ to move to the next field.

---

### Storage Location *

**What:** Where the actual data files are stored.

**Examples:**

- `s3://my-bucket/weather/global-stations/`
- `local` (stored on your machine)
- `/data/weather/global-stations/`
- `gs://cloud-bucket/weather/`

**Tips:**

- Be specific (include full path/URL)
- Use `local` if data is on your machine

**Enter:**

```
local
```

Press ++tab++ to move to the next field.

---

## Step 4: Fill in Optional Fields

Optional fields provide richer metadata but aren't required to save.

### File Format

**What:** Format of the data files.

**Examples:** `CSV`, `GeoTIFF`, `NetCDF`, `Parquet`, `JSON`

**Enter:**

```
CSV
```

---

### Size

**What:** Approximate size of the dataset (human-readable).

**Examples:** `2.5 GB`, `150 MB`, `~10 TB`

**Enter:**

```
1.2 GB
```

---

### Data Types

**What:** List of data types or variables included.

**Format:** One per line or comma-separated.

**Enter:**

```
Temperature (°C), Precipitation (mm), Wind Speed (m/s), Humidity (%)
```

---

### Used In Projects

**What:** Projects that use this dataset.

**Format:** One per line or comma-separated.

**Enter:**

```
Climate Dashboard, Weather Analysis 2024
```

---

## Step 5: Review and Save

Before saving, review your entries:

- **Dataset Name:** Global Weather Stations 2024
- **Description:** Daily weather observations...
- **Source:** https://github.com/weatherdata/global-stations
- **Date Created:** 2024-10-04
- **Storage Location:** local
- **File Format:** CSV
- **Size:** 1.2 GB
- **Data Types:** Temperature, Precipitation, Wind Speed, Humidity
- **Used In Projects:** Climate Dashboard, Weather Analysis 2024

**Save:** Press ++ctrl+s++.

**Expected:**

- Form closes
- You return to Home screen
- Notification: "Dataset saved successfully!"

---

## Step 6: Verify Dataset Appears

### Check All Datasets

On the Home screen, you should see your new dataset in the results table:

```
All Datasets (X total)
┌────────────────────────────────────────────────────┐
│ ID                          │ Name              │ Description        │
├────────────────────────────────────────────────────┤
│ global-weather-stations-... │ Global Weather... │ Daily weather o... │
│ ...                         │ ...               │ ...                │
└────────────────────────────────────────────────────┘
```

**Note:** The ID is auto-generated from the name: `global-weather-stations-2024`.

---

### Search Test

Press ++slash++ to focus search, then type:

```
weather
```

**Expected:** Your new dataset appears in the results.

---

### View Details

1. Navigate to your dataset with ++j++ / ++k++
2. Press ++enter++ to open Details screen

**Expected:** Full metadata displayed.

```
Dataset: Global Weather Stations 2024

ID: global-weather-stations-2024
Name: Global Weather Stations 2024
Description:
  Daily weather observations from 10,000+ stations worldwide.
  Includes temperature, precipitation, wind speed, and humidity.
  Data quality-controlled and gap-filled where possible.

Source: https://github.com/weatherdata/global-stations
Date Created: 2024-10-04
Storage Location: local
File Format: CSV
Size: 1.2 GB

Data Types:
  - Temperature (°C)
  - Precipitation (mm)
  - Wind Speed (m/s)
  - Humidity (%)

Used In Projects:
  - Climate Dashboard
  - Weather Analysis 2024
```

Press ++escape++ to go back.

---

## Step 7: Find the YAML File

Hei-DataHub stores metadata as YAML files in the `data/` directory.

**Check the file:**

```bash
cat data/global-weather-stations-2024/metadata.yaml
```

**Expected output:**

```yaml
id: global-weather-stations-2024
dataset_name: Global Weather Stations 2024
description: |
  Daily weather observations from 10,000+ stations worldwide.
  Includes temperature, precipitation, wind speed, and humidity.
  Data quality-controlled and gap-filled where possible.
source: https://github.com/weatherdata/global-stations
date_created: '2024-10-04'
storage_location: local
file_format: CSV
size: 1.2 GB
data_types:
  - Temperature (°C)
  - Precipitation (mm)
  - Wind Speed (m/s)
  - Humidity (%)
used_in_projects:
  - Climate Dashboard
  - Weather Analysis 2024
```

---

## Common Issues

### Validation Error: "ID must match pattern"

**Cause:** ID contains uppercase letters or invalid characters.

**Fix:**

- Leave ID field **empty** to auto-generate
- Or use only lowercase, digits, dashes, underscores

---

### "Required field missing"

**Cause:** One or more required fields (*) left empty.

**Fix:** Fill in all fields marked with *.

---

### Dataset Not Appearing in Search

**Cause:** Search index not updated.

**Fix:**

```bash
hei-datahub reindex
```

Then relaunch the TUI.

---

## Next Steps

Now that you've added your first dataset:

1. **[Tutorial: Search & Filters](03-search-and-filters.md)** — Learn advanced search techniques
2. **[Edit Your Dataset](#editing-datasets)** — Modify metadata
3. **[Set Up GitHub Integration](../12-config.md#github-configuration)** — Enable PR workflow

---

## Editing Datasets

To edit a dataset after creation:

1. **Manual Edit:**
    ```bash
    vim data/global-weather-stations-2024/metadata.yaml
    ```

2. **Reindex:**
    ```bash
    hei-datahub reindex
    ```

**Future versions** will support inline editing from the TUI.

---

## Deleting Datasets

To remove a dataset:

1. **Delete Directory:**
    ```bash
    rm -rf data/global-weather-stations-2024/
    ```

2. **Reindex:**
    ```bash
    hei-datahub reindex
    ```

---

## Tips for Real Datasets

### Be Specific

❌ **Vague:** "Temperature Data"

✅ **Specific:** "Global Daily Surface Temperature 2020-2024"

---

### Include Provenance

Always document where data came from:

- **URL:** Direct link to source
- **API:** Library + method (e.g., `ee.ImageCollection(...)`)
- **Paper:** DOI or citation

---

### Use Projects for Organization

Group related datasets under project names:

```yaml
used_in_projects:
  - Climate Dashboard
  - ML Model Training
  - Research Paper 2024
```

Then search by project name to find all related datasets.

---

## Practice Exercise

Try adding another dataset with these details:

- **Name:** "Burned Area MODIS 500m"
- **Description:** "Monthly global burned area from MODIS satellite data at 500m resolution"
- **Source:** `ee.ImageCollection("MODIS/061/MCD64A1")`
- **Storage Location:** `Google Earth Engine`
- **File Format:** `GeoTIFF`
- **Data Types:** `Burned area (binary), Burn date (ordinal day), QA flags`
- **Used In Projects:** `Wildfire Analysis`

**Time:** ~5 minutes

---

## Getting Help

- **FAQ:** [Common dataset issues](../90-faq.md#dataset-management)
- **Issues:** [Report bugs or get help](https://github.com/0xpix/Hei-DataHub/issues)
