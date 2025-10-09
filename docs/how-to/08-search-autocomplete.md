# Search Autocomplete Guide

**Available in:** Hei-DataHub {{ project_version }} and later

**Goal:** Use smart autocomplete to search faster with less typing.

**Time:** 2 minutes to learn

---

## Overview

The search field provides intelligent autocomplete suggestions as you type, helping you:

- ✅ Discover available search fields
- ✅ Find valid values from your datasets
- ✅ Build complex queries faster
- ✅ Avoid typos in field names

---

## How to Use

### 1. Start Typing

When you focus the search field (press `/`), start typing any field name:

```
Type: "for"
```

### 2. See the Suggestion

A gray suggestion appears showing the completion:

```
for|mat:
   └── Gray text suggests "format:"
```

### 3. Accept the Suggestion

Press one of these keys:

- **Tab** - Accept and continue
- **Right Arrow (→)** - Accept and continue

```
Result: "format:"
```

---

## What Gets Suggested

### Field Names

All supported search fields:

| Field | Description | Example Suggestion |
|-------|-------------|-------------------|
| `source:` | Dataset source | `source:github` |
| `format:` | File format | `format:csv` |
| `type:` | Data type | `type:time-series` |
| `tag:` | Tags | `tag:climate` |
| `project:` | Project name | `project:Gideon` |
| `name:` | Dataset name | `name:rainfall` |
| `id:` | Dataset ID | `id:burned-area` |
| `date_created:` | Creation date | `date_created:>=2025-01` |
| `size:` | File size | `size:>1000000` |

### Field Values

Autocomplete learns from your existing datasets:

**Format suggestions:**
- `csv`, `json`, `parquet`, `xlsx`, `geotiff`, `netcdf`, `hdf5`

**Type suggestions:**
- `time-series`, `geospatial`, `tabular`, `raster`, `vector`

**Project suggestions:**
- Project names from your `used_in_projects` fields

**Note:** The more datasets you have, the better the suggestions!

---

## Keyboard Shortcuts

| Action | Keys | Description |
|--------|------|-------------|
| **Accept suggestion** | Tab, → | Complete the current suggestion |
| **Ignore suggestion** | Keep typing | Type over the suggestion |
| **Focus search** | `/` | Enter search mode |
| **Exit search** | Escape | Return to results |

---

## Advanced Usage

### Custom Data Types

If you use custom data types in your datasets:

```yaml
# data/my-dataset/metadata.yaml
data_types:
  - custom-sensor-data
  - proprietary-format
```

These will appear in `type:` autocomplete suggestions!

### Source Domains

Autocomplete extracts domains from source URLs:

```yaml
source: https://data.example.com/dataset
```

Typing `source:` will suggest `data.example.com`

---

## Related Documentation

- [Advanced Search Guide](./07-search-advanced.md) - Full search syntax
- [Search Basics](../getting-started/03-the-basics.md#search) - Simple search
- [Search Syntax Reference](../reference/search-syntax.md) - Complete field list

---

## Feedback

Have suggestions for autocomplete improvements?

- Open an issue: [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- Join discussion: [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
