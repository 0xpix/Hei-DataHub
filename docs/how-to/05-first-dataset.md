# Add Your First Dataset

**Requirements:** Hei-DataHub 0.59-beta or later, WebDAV configured

Learn how to add a dataset to Hei-DataHub, understand the metadata fields, and follow best practices for creating high-quality catalog entries.

---

## Overview

Adding a dataset in Hei-DataHub creates a metadata record that is **instantly synced to Heibox** (if configured), making it available to your team immediately. This guide covers:

- Opening the Add Dataset form
- Understanding required vs. optional fields
- What happens when you save (cloud sync)
- Best practices for each field
- Verifying your dataset

**Time:** 5-10 minutes per dataset

---

## Quick Start

### 1. Launch Hei-DataHub

```bash
hei-datahub
```

**Expected:** Home screen with search bar and Heibox status indicator:
- ` Synced to Hei-box` (green) - Ready to add datasets
- `⚠ Hei-box Configured (connection failed)` (yellow) - Check auth
- `○ Hei-box Not Connected` (gray) - Run `hei-datahub auth setup`

**First time?** Configure WebDAV:
```bash
hei-datahub auth setup  # Interactive wizard (3 minutes)
```
See [Settings Guide](04-settings.md) for detailed setup instructions.

---

### 2. Open Add Dataset Form

Press **`a`** to open the Add Dataset form.

**Expected:** A modal form appears with multiple input fields.

**Keyboard shortcuts:**

- `Tab` / `Shift+Tab` - Move between fields
- `Ctrl+s` - Save dataset and upload to Heibox
- `Escape` - Cancel and close form

**What happens when you save:**
1. Metadata saved locally as `metadata.yaml`
2. **Instantly uploaded to Heibox** (if connected)
3. Search index updated automatically
4. Dataset appears in team's catalog immediately
5. No pull requests or approvals needed!

---

## Understanding the Form Fields - Everything will change in future releases (probably in v0.60-beta)

### Required Fields (*)

These fields must be filled in to save a dataset.

#### 1. Dataset Name *

**What it is:** Human-readable name for your dataset.

**Best practices:**

- ✅ Use descriptive, specific names: "Global Daily Temperature 2020-2024"
- ✅ Include temporal scope: "MODIS Burned Area 2023"
- ✅ Include spatial scope: "European Precipitation Records"
- ✅ Use title case for readability
- ❌ Avoid vague names: "Data", "Dataset 1", "Test"

**Examples:**

- `Global Weather Stations 2024`
- `MODIS Land Cover 500m Annual`
- `Amazon Basin Precipitation 1990-2020`

**Note:** The Dataset ID is auto-generated from this name (lowercase, with dashes).

---

#### 2. Description *

**What it is:** Detailed explanation of what the dataset contains.

**Best practices:**

- ✅ Write 2-4 complete sentences
- ✅ Mention what's included: variables, coverage, resolution
- ✅ Include data quality notes: "quality-controlled", "gap-filled", "raw"
- ✅ Add important caveats: "limited to urban areas", "beta version"
- ❌ Don't just repeat the name

**Example:**
```
Daily weather observations from 10,000+ stations worldwide.
Includes temperature, precipitation, wind speed, and humidity.
Data is quality-controlled and gap-filled where possible.
Coverage: 1990-2024, with higher density in North America and Europe.
```

---

#### 3. Source *

**What it is:** URL or code showing where the data originates.

**Best practices:**

- ✅ Provide direct URLs when available
- ✅ Include code snippets for API/library data
- ✅ Add DOIs for published datasets
- ✅ Multi-line code is fine
- ❌ Don't use "unknown" or "internal" without explanation

**Examples:**

**URL:**
```
https://github.com/weatherdata/global-stations
```

**API/Code:**
```python
import earthengine as ee
collection = ee.ImageCollection("MODIS/061/MCD64A1")
```

**DOI:**
```
https://doi.org/10.5067/MODIS/MCD64A1.061
```

**Multiple sources:**
```
Primary: https://data.worldbank.org/indicator/SP.POP.TOTL
Secondary: https://unstats.un.org/unsd/demographic-social/
```

---

#### 4. Date Created

**What it is:** When the dataset was created or acquired (ISO 8601: `YYYY-MM-DD`).

**Best practices:**

- ✅ Use today's date for new acquisitions (auto-filled)
- ✅ Use original publication date for historical datasets
- ✅ Format: `YYYY-MM-DD` (e.g., `2025-10-07`)

**Default:** Today's date (auto-filled, modify if needed)

---

#### 5. Storage Location *

**What it is:** Where the actual data files are stored.

**Best practices:**

- ✅ Be specific with full paths/URLs
- ✅ Include bucket/container names for cloud storage
- ✅ Use `local` if data is on your machine
- ❌ Avoid vague locations like "server" or "cloud"

**Examples:**

- `s3://my-bucket/climate/temperature/`
- `gs://earth-engine-exports/modis/`
- `/data/projects/climate-analysis/weather/`
- `local` (stored on this machine)
- `Google Earth Engine` (for GEE collections)
- `https://data.example.com/datasets/weather/`

---

### Optional Fields

These fields enrich your metadata but aren't required to save.

#### 6. File Format

**What it is:** Format of the data files.

**Examples:** `CSV`, `GeoTIFF`, `NetCDF`, `Parquet`, `JSON`, `Shapefile`, `HDF5`, `Zarr`

**Tip:** Include version if relevant: `GeoTIFF (COG)`, `NetCDF4`, `Parquet 2.0`

---

#### 7. Size

**What it is:** Approximate size of the dataset.

**Best practices:**

- ✅ Use human-readable units: `2.5 GB`, `150 MB`, `~10 TB`
- ✅ Approximate is fine: `~500 MB`
- ✅ Include compressed vs. uncompressed if relevant: `1.2 GB (3.5 GB uncompressed)`

---

#### 8. Tags

**What it is:** Comma-separated keywords for categorization.

**Best practices:**

- ✅ Use lowercase for consistency
- ✅ Include domain: `climate`, `satellite`, `demographics`
- ✅ Include data type: `raster`, `vector`, `timeseries`
- ✅ Include source: `modis`, `landsat`, `worldbank`
- ✅ 3-7 tags is ideal

**Example:** `climate, precipitation, timeseries, daily, quality-controlled`

**Search tip:** Tags enable field-specific search: `tag:climate`

---

#### 9. Data Types

**What it is:** List of variables, fields, or columns in the dataset.

**Best practices:**

- ✅ One per line or comma-separated
- ✅ Include units in parentheses: `Temperature (°C)`
- ✅ Be specific: `Mean Daily Temperature` not just `Temperature`

**Example:**
```
Temperature (°C), Precipitation (mm), Wind Speed (m/s), Humidity (%), Pressure (hPa)
```

---

#### 10. Used In Projects

**What it is:** Projects or analyses that use this dataset.

**Best practices:**

- ✅ List project names for traceability
- ✅ Update as new projects use the data
- ✅ Helps find related datasets by project

**Example:**
```
Climate Dashboard 2024, ML Weather Prediction, Research Paper: Climate Trends
```

**Search tip:** Find all project datasets: `project:Climate Dashboard 2024`

---

#### 11. Notes

**What it is:** Any additional context, warnings, or documentation.

**Best practices:**

- ✅ Mention known issues: "Missing data for January 2023"
- ✅ Add preprocessing notes: "Outliers removed using 3-sigma rule"
- ✅ Include access requirements: "Requires authentication to download"
- ✅ Reference documentation: "See README.md in storage location"

**Example:**
```
Data quality varies by region. North America and Europe have <1% missing values.
Africa and South Asia have 5-10% gaps. All gaps are flagged with QA=-1.
See quality control report: https://example.com/qc-report.pdf
```

---

## Step-by-Step Example

Let's add a real dataset together.

### Example: Global Weather Stations 2024

**1. Open the form:** Press `a`

**2. Fill in required fields:**

| Field | Value |
|-------|-------|
| **Dataset Name** | `Global Weather Stations 2024` |
| **Description** | `Daily weather observations from 10,000+ stations worldwide. Includes temperature, precipitation, wind speed, and humidity. Data is quality-controlled and gap-filled where possible. Coverage: 1990-2024.` |
| **Source** | `https://github.com/weatherdata/global-stations` |
| **Date Created** | `2025-10-07` (today, auto-filled) |
| **Storage Location** | `s3://weather-data/stations/2024/` |

**3. Fill in optional fields:**

| Field | Value |
|-------|-------|
| **File Format** | `CSV` |
| **Size** | `1.2 GB` |
| **Tags** | `weather, climate, temperature, timeseries, quality-controlled` |
| **Data Types** | `Temperature (°C), Precipitation (mm), Wind Speed (m/s), Humidity (%), Pressure (hPa)` |
| **Used In Projects** | `Climate Dashboard 2024, ML Weather Prediction` |
| **Notes** | `Station density higher in North America and Europe. See quality report: https://example.com/qc-report.pdf` |

**4. Save:** Press `Ctrl+S`

**Expected:**

- ✅ "Dataset saved successfully!" notification
- ✅ "Uploading to Heibox..." progress indicator
- ✅ "✓ Synced to Hei-box" confirmation
- ✅ Form closes, returns to Home screen
- ✅ New dataset appears in results
- ✅ **Team members see it immediately** (no waiting for PR merge)

**Note:** If Heibox is not configured, dataset is saved locally only. Configure with `hei-datahub auth setup`.

---

## Verifying Your Dataset

### 1. Check the Home Screen

Your new dataset should appear in the results table:

```
All Datasets (45 total)
┌─────────────────────────────────────────────────────────────────┐
│ ID                            │ Name                  │ Tags    │
├─────────────────────────────────────────────────────────────────┤
│ global-weather-stations-2024  │ Global Weather St...  │ weath...│
│ ...                           │ ...                   │ ...     │
└─────────────────────────────────────────────────────────────────┘
```

**Note:** The Dataset ID is auto-generated from the name:

- "Global Weather Stations 2024" → `global-weather-stations-2024`
- Lowercase, spaces→dashes, special characters removed

---

### 2. Search for Your Dataset

👉 [Learn more about search](07-search-advanced.md)

---

### 3. View Full Details

1. Navigate to your dataset using `j`/`k` (or arrow keys)
2. Press `Enter` or `o` to open Details screen

**Expected:** Full metadata displayed with all fields you entered.

3. Press `Escape` to go back

---

### 4. View Dataset in Heibox

Hei-DataHub stores metadata **directly in Heibox** (cloud-only, no local copies).

**Heibox location:**
```
https://heibox.uni-heidelberg.de/library/your-library-name/global-weather-stations-2024/metadata.yaml
```

**To view locally, you can download it:**
```bash
# Download from Heibox via WebDAV
curl -u "username@auth.local:your-webdav-password" \
  https://heibox.uni-heidelberg.de/seafdav/your-library/global-weather-stations-2024/metadata.yaml
```

**Or use the TUI:**
1. Navigate to the dataset
2. Press `Enter` or `o` to view full details
3. All metadata is displayed from cloud storage

**Expected YAML format:**

```yaml
id: global-weather-stations-2024
dataset_name: Global Weather Stations 2024
description: |
  Daily weather observations from 10,000+ stations worldwide.
  Includes temperature, precipitation, wind speed, and humidity.
  Data is quality-controlled and gap-filled where possible.
  Coverage: 1990-2024.
source: https://github.com/weatherdata/global-stations
date_created: '2025-10-07'
storage_location: s3://weather-data/stations/2024/
file_format: CSV
size: 1.2 GB
tags:
  - weather
  - climate
  - temperature
  - timeseries
  - quality-controlled
data_types:
  - Temperature (°C)
  - Precipitation (mm)
  - Wind Speed (m/s)
  - Humidity (%)
  - Pressure (hPa)
used_in_projects:
  - Climate Dashboard 2024
  - ML Weather Prediction
notes: |
  Station density higher in North America and Europe.
  See quality report: https://example.com/qc-report.pdf
```

**Tip:** Datasets are stored **cloud-only** in Heibox. The local SQLite index caches metadata for fast search, but the source of truth is always in the cloud. Edits made in Heibox will sync automatically when you launch the TUI.

---

## Best Practices Guide

### 1. Naming Conventions

**✅ Good names:**

- Descriptive: `European Precipitation Records 1950-2020`
- Specific: `MODIS Burned Area MCD64A1 500m Monthly`
- Scoped: `California Wildfire Perimeters 2020-2024`

**❌ Avoid:**

- Generic: `Dataset 1`, `Test`, `Data`
- Unclear: `New Folder`, `Downloaded Data`
- Too short: `Temp`, `DB`, `Files`

---

### 2. Writing Descriptions

**Formula:** What + Coverage + Quality + Context

**Example:**
```
[What] Daily surface temperature measurements
[Coverage] from 5,000 weather stations across Europe
[Quality] Quality-controlled and validated against ERA5
[Context] Used for climate trend analysis and model validation
```

**Length:** 2-4 sentences (50-200 words)

---

### 3. Source Documentation

**Best:** Provide reproducible access

```python
# Good: Exact code to reproduce
import earthengine as ee
collection = ee.ImageCollection("MODIS/061/MCD64A1") \
  .filterDate("2020-01-01", "2024-12-31")
```

**Better than:** "Downloaded from Google Earth Engine"

**Also good:** Direct URLs, DOIs, API endpoints

---

### 4. Tags for Discoverability

**Strategy:** Include tags for:

- Domain: `climate`, `ecology`, `demographics`
- Data type: `raster`, `vector`, `timeseries`, `tabular`
- Source: `modis`, `landsat`, `sentinel`, `worldbank`
- Theme: `temperature`, `precipitation`, `population`
- Quality: `quality-controlled`, `raw`, `processed`

**Example:** `climate, temperature, raster, modis, quality-controlled, global`

**Tip:** 5-7 tags balances discoverability and specificity.

---

### 5. Temporal and Spatial Scope

Include in **Name** or **Description**:

- Time range: `1990-2020`, `Monthly 2024`, `Historical`
- Geography: `Global`, `North America`, `Sub-Saharan Africa`
- Resolution: `500m`, `1km`, `Daily`, `Annual`

**Example:** `Global Daily Sea Surface Temperature 0.25° 2000-2024`

---

### 6. Data Quality Indicators

Document in **Description** or **Notes**:

- Processing level: `L1`, `L2`, `Raw`, `Processed`
- QA/QC: `Quality-controlled`, `Validated`, `Preliminary`
- Completeness: `95% complete`, `Gaps filled`, `Missing Jan 2023`
- Uncertainty: `±0.5°C accuracy`, `90% confidence intervals`

---

### 7. Project Linking

Use **Used In Projects** to create dataset clusters:

```yaml
used_in_projects:
  - Climate Dashboard 2024
  - ML Weather Prediction
  - Research Paper: Extreme Events
```

**Benefits:**

- Find all project datasets: `project:"Climate Dashboard"`
- Track data lineage
- Identify dataset reuse

---

### 8. Storage Location Best Practices

**Cloud-first workflow (v0.59+):**

All datasets are automatically synced to Heibox when you save. The storage location field describes where your **actual data files** are stored (not the metadata).

**Be specific:**

- ✅ `heibox://library-name/folder/` (stored in your Heibox library)
- ✅ `s3://my-bucket/climate/temperature/v2/`
- ✅ `/mnt/data/projects/climate/processed/`
- ✅ `Google Earth Engine: MODIS/061/MCD64A1`
- ❌ Avoid vague locations like "server" or "cloud"

**Add context in Notes if needed:**
```
Storage: heibox://climate-data/temperature/
Access: Team members with library access
Structure: /YYYY/MM/DD/filename_YYYYMMDD.tif
Metadata: Auto-synced to Heibox
```

**Note:** Metadata is always synced to Heibox. Storage location refers to your data files.

---

## Editing Datasets (v0.56+)

You can edit datasets directly in the TUI using inline editing:

👉 [Complete editing guide](06-edit-datasets.md)

---

## Deleting Datasets

### Option 1: Via TUI (Recommended)

1. Navigate to the dataset
2. Press `d` to delete
3. Confirm deletion
4. **Metadata removed from Heibox immediately**

### Option 2: Via Heibox Web Interface

1. Log in to Heibox
2. Navigate to your library
3. Find the dataset folder
4. Delete it
5. **Changes sync automatically** on next TUI launch

**Note:** There are no local files to delete. All data is stored in Heibox cloud storage only. The local SQLite index updates automatically.

---

## Practice Exercise

Try adding another dataset to build muscle memory:

**Dataset details:**
- **Name:** `MODIS Burned Area MCD64A1 500m`
- **Description:** `Monthly global burned area from MODIS satellite at 500m resolution. Includes burn date, burned area, and quality flags. Data from Terra and Aqua satellites. Coverage: 2001-present.`
- **Source:** `https://doi.org/10.5067/MODIS/MCD64A1.061`
- **Storage Location:** `Google Earth Engine: MODIS/061/MCD64A1`
- **File Format:** `GeoTIFF (Cloud-Optimized)`
- **Size:** `~500 GB (full archive)`
- **Tags:** `satellite, modis, burned-area, wildfire, monthly, global`
- **Data Types:** `Burned area (binary), Burn date (ordinal day), QA flags (0-5)`
- **Used In Projects:** `Wildfire Analysis 2024, Global Fire Trends`

**Time:** ~5 minutes

**Goal:** Practice filling out the form efficiently and following best practices.

---

## Next Steps

✅ **You can now add datasets!** Here's what to explore next:

1. **[Edit Datasets](06-edit-datasets.md)** — Modify metadata using inline editing
2. **[Search & Filters](07-search-advanced.md)** — Find datasets with field-specific queries

---

## Related Documentation

- **[Settings Guide](04-settings.md)** - Configure Heibox/WebDAV integration
- **[The Basics](../getting-started/03-the-basics.md)** - Core concepts and workflows
- **[Search Syntax Reference](../reference/search-syntax.md)** - Complete query grammar
- **[Privacy & Security](../privacy-and-security.md)** - How credentials are stored
- **[FAQ](../help/90-faq.md#dataset-management)** - Common dataset questions
- **[Troubleshooting](../help/troubleshooting.md)** - Solve common issues
