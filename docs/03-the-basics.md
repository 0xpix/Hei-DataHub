
This guide covers the core concepts of Hei-DataHub: projects, datasets, fields, search, and metadata management.

---

## Core Concepts

### Datasets

A **dataset** is the fundamental unit in Hei-DataHub. Each dataset represents a collection of data files with associated metadata.

**Key properties:**

- **Unique ID:** Lowercase slug (e.g., `global-temperature-2024`)
- **Metadata:** Stored in `data/<dataset-id>/metadata.yaml`
- **Searchable:** Indexed in SQLite FTS5 for fast full-text search
- **Validated:** JSON Schema ensures consistency

**Example dataset structure:**

```
data/
└── global-temperature-2024/
    ├── metadata.yaml       ← Required metadata file
    └── README.md           ← Optional documentation
```

---

### Projects

**Projects** are organizational units that group related datasets. In Hei-DataHub, projects are tracked via the `used_in_projects` field.

**Example:**

```yaml
used_in_projects:
  - Climate Analysis 2024
  - Weather Dashboard
```

**Search by project:**

Type the project name in search—Hei-DataHub indexes this field for fast lookups.

---

### Fields (Metadata Schema)

Every dataset must include these **required fields**:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | String | Unique identifier (slug) | `global-temp-2024` |
| `dataset_name` | String | Human-readable name | `Global Temperature Data 2024` |
| `description` | String | Detailed description | `Monthly average temperatures...` |
| `source` | String | URL or library snippet | `https://example.com/data` or `ee.ImageCollection(...)` |
| `date_created` | Date | ISO 8601 date | `2024-10-04` |
| `storage_location` | String | Where data files live | `s3://bucket/path` or `local` |

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| `file_format` | String | Format (CSV, GeoTIFF, etc.) |
| `size` | String | Approximate size |
| `data_types` | List[String] | Data type descriptions |
| `used_in_projects` | List[String] | Projects using this dataset |

---

### Metadata Validation

Hei-DataHub validates metadata using **JSON Schema** + **Pydantic models**.

**Validation happens:**

1. When adding a dataset in the TUI (live validation)
2. When saving via `catalog.save_dataset()`
3. During reindexing (`hei-datahub reindex`)

**Common validation errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| `id: must match pattern` | ID contains uppercase or spaces | Use lowercase, dashes, underscores |
| `description: required field` | Missing description | Add a description |
| `date_created: invalid format` | Not ISO 8601 | Use `YYYY-MM-DD` format |
| `source: required field` | Missing source | Add URL or snippet |

---

## Search

Hei-DataHub uses **SQLite FTS5** (Full-Text Search) for fast, ranked results.

### How Search Works

1. **Indexing:** When you save a dataset, Hei-DataHub extracts searchable text:
    - `dataset_name`
    - `description`
    - `used_in_projects` (joined)
    - `data_types` (joined)
    - `source`
    - `file_format`

2. **Tokenization:** Text is tokenized using Porter stemming + Unicode normalization

3. **Ranking:** Results ranked by **BM25** algorithm (term frequency + inverse document frequency)

4. **Prefix matching:** Enabled for 2-, 3-, and 4-character prefixes

### Search Examples

**Basic search:**

```
Query: "climate"
Matches: "climate", "climatic", "climatology"
```

**Multi-word search:**

```
Query: "burned area"
Matches: Datasets with both "burned" AND "area" in searchable fields
```

**Project search:**

```
Query: "Gideon"
Matches: Datasets where used_in_projects contains "Gideon"
```

**Partial matching:**

```
Query: "geo"
Matches: "GeoTIFF", "geospatial", "geometry"
```

---

## Filters

Currently, Hei-DataHub supports **text-based search** across all indexed fields. Future versions may add:

- Field-specific filters (e.g., `source:github.com`)
- Date range filters
- Size filters
- Project filters

---

## Saved Views

**Not yet implemented** in v0.55.x beta. Planned for future releases:

- Save frequently used search queries
- Pin important datasets
- Custom result ordering

---

## Dataset Lifecycle

### 1. Create

**Via TUI:**

```
1. Press a from Home screen
2. Fill required fields
3. Press Ctrl+S to save
```

**Result:**

- YAML file created at `data/<id>/metadata.yaml`
- Dataset indexed in SQLite FTS5
- Appears in search results immediately

---

### 2. Edit

**Manual editing:**

```bash
# Edit YAML file directly
vim data/<dataset-id>/metadata.yaml

# Reindex to update search index
hei-datahub reindex
```

**TUI editing (✅ Available since v0.56-beta):**

Inline editing from Details Screen. Press `e` to enter Edit Mode, modify fields, then `s` to save or `ESC` to cancel. See [How-To: Edit Datasets](how-to/edit-datasets.md) for full guide.

---

### 3. Delete

**Manual deletion:**

```bash
# Remove dataset folder
rm -rf data/<dataset-id>/

# Reindex to update search index
hei-datahub reindex
```

**Future TUI deletion:**

Planned for v0.58.x—delete from Details Screen with confirmation.

---

### 4. Share (PR Workflow)

**Enable GitHub integration:**

1. Press ++s++ to open Settings
2. Configure:
    - GitHub Owner
    - Repository Name
    - GitHub Username
    - Personal Access Token (PAT)
3. Save with ++ctrl+s++

**Create PR from dataset:**

```
1. Add or edit a dataset
2. Press Ctrl+S to save
3. App automatically:
   - Stashes uncommitted changes (if any)
   - Creates a new branch
   - Commits metadata.yaml
   - Pushes to GitHub
   - Opens a Pull Request
   - Restores stashed changes
```

---

## Data Organization

### Directory Structure

```
Hei-DataHub/
├── data/                       ← All datasets live here
│   ├── dataset-one/
│   │   ├── metadata.yaml       ← Required
│   │   └── README.md           ← Optional
│   ├── dataset-two/
│   │   └── metadata.yaml
│   └── ...
├── db.sqlite                   ← Search index (auto-generated)
├── .cache/                     ← Temporary files
└── .outbox/                    ← Failed PR tasks
```

### metadata.yaml Format

```yaml
id: global-temperature-2024
dataset_name: Global Temperature Data 2024
description: |
  Monthly average surface temperatures from weather stations worldwide.
  Covers 2020-2024 with quality-controlled data.
source: https://example.com/weather/global-temp
date_created: '2024-10-04'
storage_location: s3://climate-data/temperature/
file_format: CSV
size: 2.5 GB
data_types:
  - Time series data (monthly averages)
  - Station metadata (lat/lon, elevation)
used_in_projects:
  - Climate Dashboard
  - Research Paper 2024
```

---

## Best Practices

### ID Naming

✅ **Good:**

- `global-temperature-2024`
- `burned_area_modis_500m`
- `weather-q1-2024`

❌ **Bad:**

- `GlobalTemperature2024` (uppercase not allowed)
- `global temperature 2024` (spaces not allowed)
- `-temperature` (must start with alphanumeric)

---

### Descriptions

✅ **Good:**

```yaml
description: |
  Monthly global gridded burned area product at 500m resolution.
  Derived using MODIS Surface Reflectance and Active Fire data.
  Includes per-pixel burn dates and quality assurance indicators.
```

❌ **Bad:**

```yaml
description: Burned area data
```

**Tip:** Aim for 2-4 sentences. Include:

- What the dataset contains
- Data source/methodology
- Temporal/spatial coverage

---

### Source Field

✅ **Good:**

```yaml
# URL
source: https://github.com/owner/repo/tree/main/data

# Library snippet
source: ee.ImageCollection("MODIS/061/MCD64A1")

# Multi-line snippet
source: |
  import earthengine as ee
  dataset = ee.ImageCollection("MODIS/061/MCD64A1")
```

❌ **Bad:**

```yaml
source: "Not sure"
source: "See README"
```

---

### Projects

✅ **Good:**

```yaml
used_in_projects:
  - Climate Analysis Dashboard
  - Research: Wildfire Trends
  - ML Model Training (2024)
```

**Tip:** Use descriptive project names. These are searchable, so use names you'll remember.

---

## Next Steps

- **[UI Guide](10-ui.md)** — Deep dive into TUI structure and customization
- **[Data & SQL](11-data-and-sql.md)** — Understanding the storage layer
- **[Tutorial: Your First Dataset](20-tutorials/02-first-dataset.md)** — Hands-on walkthrough
