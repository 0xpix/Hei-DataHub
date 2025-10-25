# Advanced Search Guide

**Requirements:** Hei-DataHub 0.59-beta or later

**Goal:** Master search to find datasets instantly using field-specific filters, operators, and exact phrases.

**Time:** 5 minutes to learn, <1 second to search

---


## Quick Start

With **cloud-first storage**, all datasets live in Heibox and are indexed locally for **lightning-fast search**:

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

**Available in 0.59-beta:** The search field provides smart autocomplete suggestions powered by your cloud catalog!

### How It Works

As you type, Hei-DataHub suggests:

1. **Field names** - Type `for` → suggests `format:`
2. **Field values** - Type `format:` → suggests `csv`, `json`, `parquet` from your actual data
3. **Recent searches** - Common queries you've used before
4. **Multi-term** - After completing one filter, start typing the next

**Smart suggestions:** Autocomplete learns from your Heibox catalog, suggesting only formats/tags/sources that actually exist in your datasets.

### Accepting Suggestions

When you see a suggestion (shown in gray text), press:

- **`Tab`** - Accept suggestion and continue typing
- **`→` (Right Arrow)** - Accept suggestion
- **`Enter`** - Accept and execute search
- Keep typing to ignore the suggestion

### Examples

**Typing field names:**
```
Type: "for"
Autocomplete: "format:"
Press Tab → "format:"
```

**Typing field values (from your data):**
```
Type: "format:c"
Autocomplete: "format:csv" (if CSV datasets exist in catalog)
Press Tab → "format:csv "
Ready for next filter
```

**Building complex queries:**
```
Type: "format:csv sou"
Autocomplete: "format:csv source:"
Press Tab → "format:csv source:"
Type: "git"
Autocomplete: "format:csv source:github" (if you have GitHub datasets)
Press Enter → executes search
```

**Pro tip:** Autocomplete is context-aware. If you type `tag:`, it only suggests tags that exist in your Heibox catalog.

---

## Search Syntax

### Field Filters

Search specific fields with `field:value`:

| Filter | What it finds | Example | Notes |
|--------|--------------|---------|-------|
| `source:VALUE` | Source contains VALUE | `source:github` | URL or code reference |
| `format:VALUE` | Format equals VALUE | `format:parquet` | File format (csv, json, etc.) |
| `type:VALUE` | Data type equals VALUE | `type:raster` | Raster, vector, tabular, etc. |
| `project:VALUE` | Project name contains VALUE | `project:climate` | Associated projects |
| `storage:VALUE` | Storage location contains VALUE | `storage:heibox` | Where data files are stored |
| `tag:VALUE` | Tags contain VALUE | `tag:archived` | Metadata tags |
| `name:VALUE` | Dataset name contains VALUE | `name:weather` | Dataset identifier |
| `description:VALUE` | Description contains VALUE | `description:daily` | Full description text |

**Examples:**

```
format:csv
```
Shows only CSV datasets.

```
tag:climate tag:priority
```
Datasets with both "climate" AND "priority" tags.

```
storage:heibox source:github
```
Data stored in Heibox, sourced from GitHub.

---

### Numeric Operators

Use **`>`, `<`, `>=`, `<=`** with numeric fields for precise filtering:

| Operator | Meaning | Example | Use Case |
|----------|---------|---------|----------|
| `>` | Greater than | `size:>1000000` | Files larger than 1 MB |
| `<` | Less than | `size:<500000` | Files smaller than 500 KB |
| `>=` | Greater or equal | `size:>=1048576` | 1 MB or more |
| `<=` | Less or equal | `size:<=2097152` | 2 MB or less |

**Examples:**

```
size:>5000000
```
Finds datasets larger than 5 MB (5,000,000 bytes).

```
size:>100000 size:<1000000
```
Medium-sized datasets (100 KB - 1 MB).

**Common size values:**
- 1 KB = 1,024 bytes
- 1 MB = 1,048,576 bytes
- 1 GB = 1,073,741,824 bytes

**Pro tip:** Use `size:>0` to find datasets with size information (excludes datasets without size metadata).

---

### Date Operators

Filter by creation or modification dates (format: `YYYY-MM-DD`):

| Field | What it filters | Example | Use Case |
|-------|----------------|---------|----------|
| `date_created` | Dataset creation date | `date_created:>=2025-01-01` | New datasets this year |
| `date_modified` | Last update date | `date_modified:<2024-12-31` | Outdated datasets |
| `created` | Alias for date_created | `created:2025-10-25` | Created today |
| `modified` | Alias for date_modified | `modified:>=2025-10-01` | Updated this month |

**Examples:**

```
date_created:>=2025-01-01
```
All datasets created in 2025.

```
date_modified:<2024-01-01
```
Datasets not updated since 2024 (possibly stale).

```
created:2025-10-25
```
Datasets created today (exact match).

```
created:>=2025-01-01 modified:>=2025-10-01
```
Datasets created this year and updated recently.

**Date formats supported:**
- `YYYY-MM-DD` (e.g., `2025-10-25`)
- `YYYY-MM` (e.g., `2025-10` - matches entire month)
- `YYYY` (e.g., `2025` - matches entire year)

---

### Exact Phrase Match

Use **double quotes** for exact phrase matching:

```
"climate change"
```
Finds datasets with the exact phrase "climate change" (not just "climate" OR "change").

```
"machine learning model"
```
Exact match for the three-word phrase.

**Without quotes:**
```
climate change
```
Finds datasets containing "climate" OR "change" anywhere (less precise).

**Pro tip:** Use quotes when searching for:
- Multi-word technical terms: `"random forest"`
- Project names: `"Climate Dashboard 2024"`
- Specific phrases: `"quality controlled data"`

---

### Combine Everything

Build powerful queries by combining field filters, operators, and free text:

**Example 1: Find large GitHub CSVs**
```
source:github format:csv size:>1000000
```
- Datasets from GitHub
- In CSV format
- Larger than 1 MB

**Example 2: Recent climate data**
```
tag:climate created:>=2025-01-01 "quality controlled"
```
- Tagged with "climate"
- Created this year
- Contains exact phrase "quality controlled"

**Example 3: Outdated Heibox datasets**
```
storage:heibox modified:<2024-01-01 size:>10000000
```
- Stored in Heibox
- Not updated since 2024
- Larger than 10 MB (candidates for cleanup)

**Example 4: Project-specific parquet files**
```
project:"ML Weather" format:parquet source:s3
```
- Project name contains "ML Weather"
- Parquet format
- Stored in S3

**Tip:** Start simple and add filters one by one until you get the exact results you need.

---

## Visual Filter Badges

When you use filters, **colored badges** appear below the search box showing exactly what you're searching for:

**Badge types:**
- 🏷️ **Field filters** - `source:github`, `format:csv`
- 🔢 **Numeric filters** - `size:>1000000`
- 📅 **Date filters** - `created:>=2025-01-01`
- 📝 **Free-text terms** - `rainfall`, `temperature`
- 💬 **Exact phrases** - `"quality controlled"`

**Example search:**
```
format:csv size:>1000000 tag:climate "production ready"
```

**Shows badges:**
```
🏷️ format:csv   🔢 size:>1000000   🏷️ tag:climate   💬 "production ready"
```

**Benefits:**
- ✅ See all active filters at a glance
- ✅ Understand complex queries visually
- ✅ Identify which filters to remove if too restrictive
- ✅ Each term is separate for clarity

**Since v0.59:** Enhanced badge styling and clearer visual separation between filter types.

---

## Pro Tips & Best Practices

### ✅ Search is Local & Instant

**How it works:**
- All metadata synced from Heibox to local SQLite index
- Search runs locally (no network calls)
- Results in <80ms
- Works offline (searches last synced data)

**When index updates:**
- Automatically on app launch
- Every 15 minutes in background
- After adding/editing datasets
- Can force: `hei-datahub reindex`

### ✅ Unknown Fields Fall Back to Free Text

If you type a filter that doesn't exist, it searches everywhere:

```
banana:split
```
Since "banana" isn't a real field, this searches for "banana" and "split" in all fields.

**Why this matters:** You'll never get zero results by mistyping a field name.

### ✅ Partial Matches Work

Most text fields use **"contains"** matching:

```
source:git
```
Finds `github.com`, `gitlab.com`, `git.example.org`, etc.

```
tag:clim
```
Finds tags like `climate`, `climatology`, `climatic`.

### ✅ Case-Insensitive

All searches ignore case:
```
format:CSV
format:csv
format:Csv
```
All produce identical results.

### ✅ Search Team's Datasets

With Heibox integration, you search the entire team catalog:
- Datasets you added
- Datasets teammates added
- All synced from cloud storage
- Updates visible within 15 minutes (or on next launch)

### ✅ Use Keyboard Shortcuts

Press **`?`** in the TUI to see:
- Available search fields
- Example queries
- Keyboard shortcuts
- Search syntax reference

---

## Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| **`/`** | Focus search box | Quick access to search from anywhere |
| **`Esc`** | Clear search | Remove all filters and show all datasets |
| **`?`** | Show syntax help | Display available fields and examples |
| **`Enter`** | Open selected dataset | View full details |
| **`Tab`** | Accept autocomplete | Use suggested field or value |
| **`→`** | Accept autocomplete | Alternative to Tab |
| **`j` / `↓`** | Move down results | Navigate search results |
| **`k` / `↑`** | Move up results | Navigate search results |

**Pro tip:** Press `/` from anywhere in the TUI to instantly start searching!

---

### 🚧 Planned for future releases

#### Fields You Can't Search (Yet)

- **Individual schema columns** – Can't search inside `schema_fields` array
- **Custom metadata** – Only built-in fields are indexed
- **Nested objects** – Complex nested structures not fully indexed

**Planned for future versions.**

#### Boolean Operations Not Supported

Currently no support for:
- OR operators: `format:csv OR format:json`
- NOT operators: `-tag:archived` (may work in some versions)
- Parentheses: `(format:csv OR format:json) tag:climate`

**Workaround:** Run multiple searches or use broader filters.

#### Autocomplete Limitations

- Only suggests values from synced catalog (not all possible values)
- No suggestion for free-text search terms (only field names/values)
- Limited to most common 100 values per field

---

## Next Steps

**Customize your workflow:**
- ⌨️ **[Customize keybindings](08-customize-keybindings.md)** - Change search hotkey from `/`
- 🎨 **[Change theme](09-change-theme.md)** - Personalize the interface

**Need help?**
- 🔍 **[Troubleshooting](../help/troubleshooting.md)** - Solve search issues

---

## Related Documentation

- **[Search Syntax Reference](../reference/search-syntax.md)** - Complete query language specification
- **[Privacy & Security](../privacy-and-security.md)** - How search index is stored
- **[UI Guide](../reference/10-ui.md)** - TUI navigation and features
- **[FAQ: Search Questions](../help/90-faq.md#search)** - Common search questions
- **[What's New in 0.59-beta](../whats-new/0.59-beta.md)** - Latest search improvements
