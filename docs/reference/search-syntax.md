# Search Syntax Reference

Complete guide to search filters, operators, and query syntax in Hei-DataHub.

**Version:** 0.56-beta or later

---

## Overview

Hei-DataHub uses a **structured query parser** that supports:
- Field-specific filters
- Numeric and date operators
- Exact phrase matching
- Mixed free-text and structured queries

---

## Basic Syntax

### Free Text Search
Type normally to search all fields:
```
climate data
```

### Field Filter
Search a specific field:
```
field:value
```

### Multiple Filters
Separate with spaces:
```
field1:value1 field2:value2
```

---

## Searchable Fields

### Text Fields

| Field | Description | Example |
|-------|-------------|---------|
| `source` | Dataset source URL | `source:github` |
| `storage` | Storage location | `storage:s3` |
| `format` | File format | `format:csv` |
| `type` | Data type | `type:raster` |
| `project` | Project name | `project:research` |
| `tag` | Dataset tags | `tag:archived` |
| `name` | Dataset name | `name:climate` |
| `description` | Dataset description | `description:temperature` |

**Match behavior:** Text fields use **"contains"** matching (partial match allowed).

---

### Numeric Fields

| Field | Description | Example |
|-------|-------------|---------|
| `size` | File size in bytes | `size:>1000000` |

**Supported operators:** `>`, `<`, `>=`, `<=`, `=`

---

### Date Fields

| Field | Description | Format | Example |
|-------|-------------|--------|---------|
| `date_created` | Creation date | `YYYY-MM-DD` | `date_created:>=2025-01-01` |
| `date_modified` | Last modified | `YYYY-MM-DD` | `date_modified:<2024-12-31` |

**Supported operators:** `>`, `<`, `>=`, `<=`, `=`

---

## Operators

### Text Operator

**`:` (contains)**
- Default for text fields
- Partial match
- Case-insensitive

```
source:github
```
Matches: `github.com`, `github.example.org`, `my-github-repo`

---

### Numeric Operators

**`>` (greater than)**
```
size:>1000000
```
Files larger than 1 MB

**`<` (less than)**
```
size:<500000
```
Files smaller than 500 KB

**`>=` (greater or equal)**
```
size:>=1048576
```
Files 1 MB or larger

**`<=` (less or equal)**
```
size:<=2097152
```
Files 2 MB or smaller

**`=` (exactly equal)**
```
size:=1048576
```
Files exactly 1 MB

---

### Date Operators

Same as numeric operators:

**`>=` (on or after)**
```
date_created:>=2025-01-01
```
Created in 2025 or later

**`<` (before)**
```
date_modified:<2024-01-01
```
Modified before 2024

**`=` (exactly on)**
```
date_created:=2025-10-05
```
Created on October 5, 2025

---

## Exact Phrases

Use **double quotes** for exact matches:

```
"machine learning"
```
Finds datasets with the exact phrase "machine learning" (not just "machine" OR "learning").

---

## Query Examples

### Simple Filters

**Find CSV files:**
```
format:csv
```

**Find GitHub datasets:**
```
source:github
```

**Find archived data:**
```
tag:archived
```

---

### Numeric Filters

**Large files (>10 MB):**
```
size:>10000000
```

**Small files (<1 MB):**
```
size:<1000000
```

**Files between 1-5 MB:**
```
size:>=1000000 size:<=5000000
```

---

### Date Filters

**Created this year:**
```
date_created:>=2025-01-01
```

**Created before 2024:**
```
date_created:<2024-01-01
```

**Modified in October 2025:**
```
date_modified:>=2025-10-01 date_modified:<2025-11-01
```

---

### Combined Filters

**Large CSV files from GitHub:**
```
format:csv source:github size:>1000000
```

**Recent vector data in GeoJSON:**
```
type:vector format:geojson date_created:>=2025-01-01
```

**S3 Parquet files in climate project:**
```
storage:s3 format:parquet project:climate
```

---

### With Exact Phrases

**Find "climate change" datasets in CSV:**
```
"climate change" format:csv
```

**Find "production data" on GitHub:**
```
"production data" source:github
```

---

## Advanced Patterns

### Range Queries

**Files between 1-10 MB:**
```
size:>=1000000 size:<=10000000
```

**Datasets from Q1 2025:**
```
date_created:>=2025-01-01 date_created:<2025-04-01
```

---

### Project-Specific Search

**All datasets in "mapping" project:**
```
project:mapping
```

**Large datasets in "climate" project:**
```
project:climate size:>5000000
```

---

### Format-Specific Search

**All Parquet files:**
```
format:parquet
```

**CSV or JSON files:**
```
format:csv
```
(Then search again with `format:json` – OR operator coming in v0.57)

---

### Storage Location Search

**All S3 datasets:**
```
storage:s3
```

**Local files:**
```
storage:/data
```

**HTTPS URLs:**
```
source:https
```

---

## Special Behaviors

### Unknown Fields Fall Back to Free Text

If you type a field that doesn't exist:
```
banana:yellow
```

The query searches for "banana" and "yellow" in **all fields** (free-text search).

**Why this matters:** You'll never get zero results from a typo.

---

### Case-Insensitive Matching

All searches ignore case:
```
format:CSV
format:csv
format:Csv
```
All produce the same results.

---

### Partial Matching for Text

Text fields match **substrings**:
```
source:git
```
Matches: `github.com`, `gitlab.com`, `git.example.org`

---

## Limitations

### No OR Operator (Yet)

You can't search "CSV OR JSON" in one query. Coming in v0.57.

**Workaround:** Run two separate searches.

---

### No Wildcards

You can't use `*` or `?` wildcards.

**Workaround:** Use partial matching (built-in).

---

### No Regex

Regular expressions are not supported.

**Workaround:** Use multiple queries or free-text search.

---

### No Field Autocomplete (Yet)

Field names don't auto-suggest as you type. Coming in v0.57-beta.

**Workaround:** Press `?` to see available fields.

---

### Can't Search Array Fields

You can't search inside arrays like `schema_fields` or `tags` individually.

**Example (won't work):**
```
schema_fields.name:temperature
```

**Workaround:** Use tag search or free-text.

---

## Performance Notes

### Fast Queries (<20ms)

These are optimized:
- Single field filters: `format:csv`
- Simple numeric filters: `size:>1000`
- Date filters: `date_created:>=2025-01-01`

---

### Slower Queries (20-100ms)

These take longer:
- Multiple field filters: `format:csv source:github size:>1000`
- Exact phrases: `"long exact phrase here"`
- Complex combinations

**Target:** P50 < 120ms for 2,000 datasets

---

## Field Reference Table

| Field | Type | Operators | Example |
|-------|------|-----------|---------|
| `name` | Text | `:` | `name:weather` |
| `description` | Text | `:` | `description:temperature` |
| `source` | Text | `:` | `source:github` |
| `storage` | Text | `:` | `storage:s3` |
| `format` | Text | `:` | `format:parquet` |
| `size` | Numeric | `>`, `<`, `>=`, `<=`, `=` | `size:>1000000` |
| `type` | Text | `:` | `type:vector` |
| `project` | Text | `:` | `project:mapping` |
| `tag` | Text | `:` | `tag:archived` |
| `date_created` | Date | `>`, `<`, `>=`, `<=`, `=` | `date_created:>=2025-01-01` |
| `date_modified` | Date | `>`, `<`, `>=`, `<=`, `=` | `date_modified:<2024-12-31` |

---

## Grammar (Technical)

For developers interested in the query parser:

```
query        ::= term*
term         ::= field_filter | phrase | word
field_filter ::= field operator value
field        ::= [a-z_]+
operator     ::= ":" | ">" | "<" | ">=" | "<=" | "="
value        ::= [^ ]+
phrase       ::= '"' [^"]* '"'
word         ::= [^ ]+
```

---

## Help in the App

Press **`?`** at any time to see:
- Available fields
- Operator examples
- Query syntax guide

---

## Next Steps

- **[Advanced search tutorial](../how-to/07-search-advanced.md)** – Learn by example
- **[Edit datasets](../how-to/06-edit-datasets.md)** – Change searchable fields
- **[UI guide](10-ui.md)** – Understand the interface

---

## Related

- [How-to: Advanced Search](../how-to/07-search-advanced.md)
- [FAQ](../help/90-faq.md)
- [What's New](../whats-new/0.57-beta.md)
