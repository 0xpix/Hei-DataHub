# How to Use Advanced Search

Requirements: Hei-DataHub 0.56-beta or later

**Goal:** Find datasets quickly using field-specific filters, operators, and exact phrases.

**Time:** 5 minutes to learn, seconds to use

---

## Quick Start

### Basic Search (Free Text)

Just type normally to search all fields:

```
climate
```
Finds any dataset with "climate" in name, description, tags, or other fields.

---

### Field-Specific Search

Use **`field:value`** to search a specific field:

```
source:github
```
Finds datasets where the `source` field contains "github".

---

### Combine Multiple Filters

Add spaces between filters:

```
format:csv source:s3
```
Finds CSV files stored in S3.

---

## Search Autocomplete

**New in 0.57.1-beta:** The search field now provides smart autocomplete suggestions!

### How It Works

As you type, Hei-DataHub suggests:

1. **Field names** - Type `for` → suggests `format:`
2. **Field values** - Type `format:` → suggests `csv`, `json`, `parquet`, etc.
3. **Multi-term** - After completing one filter, start typing the next

### Accepting Suggestions

When you see a suggestion (shown in gray text), press:

- **Tab** - Accept suggestion
- **Right Arrow (→)** - Accept suggestion
- Keep typing to ignore the suggestion

### Examples

**Typing field names:**
```
Type: "for"
Suggests: "format:"
Press Tab → "format:"
```

**Typing field values:**
```
Type: "format:c"
Suggests: "format:csv"
Press Tab → "format:csv "
```

**Multi-term queries:**
```
Type: "format:csv ty"
Suggests: "format:csv type:"
Press Tab → continues building query
```

### What Gets Suggested

- **Field names:** All supported fields (source, format, type, tag, etc.)

Coming soon in [0.57.2-beta]:

- **Project names:** Projects referenced in your datasets
- **Format values:** Common formats from your datasets (csv, json, parquet, xlsx, etc.)
- **Type values:** Data types from your catalog (time-series, geospatial, tabular, etc.)

**Note:** Value suggestions are learned from your existing datasets. The more datasets you have, the better the suggestions!

---

## Search Syntax

### Field Filters

Search a specific field with `field:value`:

| Filter | What it finds | Example |
|--------|--------------|---------|
| `source:VALUE` | Source contains VALUE | `source:github` |
| `format:VALUE` | Format equals VALUE | `format:parquet` |
| `type:VALUE` | Data type equals VALUE | `type:raster` |
| `project:VALUE` | Project name contains VALUE | `project:climate` |
| `storage:VALUE` | Storage location contains VALUE | `storage:s3` |
| `tag:VALUE` | Tags contain VALUE | `tag:archived` |

**Example:**
```
format:csv
```
Shows only CSV datasets.

---

### Numeric Operators

Use **`>`, `<`, `>=`, `<=`** with numeric fields:

| Operator | Meaning | Example |
|----------|---------|---------|
| `>` | Greater than | `size:>1000000` (larger than 1 MB) |
| `<` | Less than | `size:<500000` (smaller than 500 KB) |
| `>=` | Greater or equal | `size:>=1048576` (1 MB or more) |
| `<=` | Less or equal | `size:<=2097152` (2 MB or less) |

**Example:**
```
size:>5000000
```
Finds datasets larger than 5 MB.

---

### Date Operators

Use operators with date fields (format: `YYYY-MM-DD`):

| Field | What it filters | Example |
|-------|----------------|---------|
| `date_created` | When dataset was created | `date_created:>=2025-01-01` |
| `date_modified` | Last update date | `date_modified:<2024-12-31` |

**Example:**
```
date_created:>=2025-01-01
```
Finds datasets created this year.

---

### Exact Phrase Match

Use **quotes** for exact matches:

```
"climate change"
```
Finds datasets with the exact phrase "climate change" (not just "climate" OR "change").

---

### Mix and Match

Combine field filters, operators, and free text:

```
source:github format:csv size:>1000000 "production data"
```

This finds:
- Datasets from GitHub
- In CSV format
- Larger than 1 MB
- Containing the phrase "production data"

---

## Visual Filter Badges

When you use filters, **colored badges** appear below the search box:

- **🏷 source:github** (field filter)
- **🏷 size:>1000000** (numeric filter)
- **📝 rainfall** (free-text term)
- **📝 temp** (free-text term)
- **📝 "exact phrase"** (quoted phrase)

**Since v0.57.1-beta:** Each search term gets its own badge, making it clear what you're searching for. Multiple terms (e.g., "rainfall temp rice") display as separate badges instead of one combined badge.

---

## Pro Tips

### ✅ Unknown Fields Fall Back to Free Text

If you type a filter that doesn't exist, it searches everywhere:

```
banana:split
```
Since "banana" isn't a real field, this searches for "banana" and "split" in all fields.

**Why this matters:** You'll never get zero results by mistyping a field name.

---

### ✅ Partial Matches Work

Most text fields use **"contains"** matching:

```
source:git
```
Finds `github.com`, `gitlab.com`, `git.example.org`, etc.

---

### ✅ Case-Insensitive

All searches ignore case:
```
format:CSV
format:csv
format:Csv
```
All work the same.

---

### ✅ No Need to Remember Field Names

Press **`?`** to see available fields and example queries.

---

## Troubleshooting

### No Results

**Problem:** Your search returns nothing.

**Solutions:**

1. Remove one filter at a time to find the culprit
2. Check for typos in field values
3. Try a simpler query first

---

### Too Many Results

**Problem:** Search returns hundreds of datasets.

**Solutions:**

1. Add more specific filters
2. Use exact phrases: `"specific term"`
3. Use numeric operators to narrow by size or date

---

### Unexpected Results

**Problem:** You get datasets that don't seem to match.

**Cause:** Unknown field names fall back to free-text search.

**Solution:** Check spelling of field names (use `?` for help).

---

## Example Workflows

### Scenario 1: Find Old CSV Files

**Goal:** Clean up CSV files created before 2024.

**Query:**
```
format:csv date_created:<2024-01-01
```

---

### Scenario 2: Find GitHub Datasets Larger Than 2 MB

**Goal:** Review large datasets stored on GitHub.

**Query:**
```
source:github size:>2000000
```

---

### Scenario 3: Find Climate Project Data

**Goal:** See all datasets related to "climate" project.

**Query:**
```
project:climate
```

or combine with tags:
```
project:climate tag:priority
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **`/`** | Focus search box |
| **`Esc`** | Clear search |
| **`?`** | Show syntax help |
| **`Enter`** | Open selected result |

---

## Limitations

### Fields You Can't Search (Yet)

- **Individual schema columns** – Can't search `schema_fields` array items
- **Custom metadata** – Only built-in fields are indexed

These are planned for future versions.

---

### No Autocomplete (Yet)

As you type, field names don't auto-suggest. Autocomplete is planned for 0.59-beta.

---

## Next Steps

- **[Learn all search syntax](../reference/search-syntax.md)** (complete reference)
- **[Edit datasets](06-edit-datasets.md)** to fix search results
- **[Customize keybindings](08-customize-keybindings.md)** (change search key from `/`)

---

## Related

- [Search syntax reference](../reference/search-syntax.md)
- [UI guide](../reference/10-ui.md)
- [FAQ](../help/90-faq.md)
- [What's New](../whats-new/0.57-beta.md)
