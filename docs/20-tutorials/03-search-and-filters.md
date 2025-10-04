# Tutorial: Search & Filters

Master Hei-DataHub's search capabilities with this hands-on tutorial covering basic search, advanced techniques, and search best practices.

---

## What You'll Learn

- How full-text search works in Hei-DataHub
- Search syntax and operators
- Tips for finding datasets quickly
- Understanding search results and ranking

**Time:** ~15 minutes

---

## Prerequisites

- Hei-DataHub installed with example datasets
- Familiarity with basic navigation (see [Navigation Guide](../02-navigation.md))

---

## How Search Works

Hei-DataHub uses **SQLite FTS5** (Full-Text Search) with:

- **Porter stemming:** "running" matches "run", "runs"
- **BM25 ranking:** Results ranked by relevance
- **Prefix matching:** "cli" matches "climate"
- **Multi-field indexing:** Searches name, description, source, projects, data types

---

## Step 1: Launch and Focus Search

Start Hei-DataHub:

```bash
hei-datahub
```

Press ++slash++ to focus the search box.

**Mode indicator changes:** "Mode: Insert"

---

## Step 2: Basic Single-Word Search

### Search: "weather"

Type:

```
weather
```

**Results update in real-time** (150ms debounce).

**Expected matches:**

- Datasets with "weather" in name, description, or source
- E.g., "Weather Q1 Data", "Global Weather Stations"

**Ranking:** Datasets with "weather" in the name rank higher than those with it only in the description.

---

### Search: "modis"

Clear search (++escape++ twice) and type:

```
modis
```

**Expected matches:**

- Datasets mentioning "MODIS" satellite data
- E.g., "Burned Area MODIS 500m"

---

## Step 3: Multi-Word Search

### Search: "burned area"

Type:

```
burned area
```

**How it works:**

- Searches for datasets containing **both** "burned" **AND** "area"
- Order doesn't matter: "area burned" yields same results

**Expected matches:**

- "Burned Area MODIS 500m"
- Datasets with both words in description or name

---

### Search: "global temperature"

Type:

```
global temperature
```

**Expected matches:**

- Datasets with both "global" and "temperature"
- E.g., "Global Surface Temperature 2020-2024"

---

## Step 4: Partial Matching (Prefixes)

### Search: "clim"

Type:

```
clim
```

**Expected matches:**

- "climate"
- "climatic"
- "climatology"

**Why?** Prefix matching enabled for 2-4 character prefixes.

---

### Search: "geo"

Type:

```
geo
```

**Expected matches:**

- "GeoTIFF"
- "geospatial"
- "geographic"

---

## Step 5: Search by Project

Hei-DataHub indexes the `used_in_projects` field, so you can search by project name.

### Search: "Gideon"

Type:

```
Gideon
```

**Expected matches:**

- All datasets where `used_in_projects` includes "Gideon"

**Use case:** "Show me all datasets used in my Climate Dashboard project."

---

## Step 6: Search by Data Type

The `data_types` field is also indexed.

### Search: "raster"

Type:

```
raster
```

**Expected matches:**

- Datasets with "raster" in `data_types` field
- E.g., datasets with `data_types: ["Raster (GeoTIFF)"]`

---

## Step 7: Case Insensitivity

Search is **case-insensitive**.

### Try These

All return the same results:

```
MODIS
modis
Modis
MoDiS
```

---

## Step 8: Stemming Examples

Porter stemming normalizes word forms.

### Search: "burn"

Type:

```
burn
```

**Matches:**

- "burn"
- "burning"
- "burned"
- "burns"

---

### Search: "analyze"

Type:

```
analyze
```

**Matches:**

- "analyze"
- "analyzing"
- "analyzed"
- "analysis" (stem: "analyz")

---

## Step 9: Understanding Ranking

Results are ranked by **BM25** algorithm, which considers:

1. **Term frequency:** How often query terms appear in the document
2. **Inverse document frequency:** Rare terms (e.g., "MODIS") rank higher than common terms (e.g., "data")
3. **Field weighting:** Matches in `name` rank higher than matches in `description`

### Example

**Query:** "climate"

**Ranking:**

1. Dataset with "Climate" in **name** + multiple mentions in **description**
2. Dataset with "climate" in **description** only
3. Dataset with "climatic" in **source** field

---

## Step 10: Empty Search

Clear search (++escape++ twice) or delete all text.

**Result:** Shows **all datasets** (sorted by most recently updated).

---

## Step 11: Search Navigation

After typing a query:

1. Press ++enter++ to move focus to results table
2. Use ++j++ / ++k++ to navigate results
3. Press ++enter++ to open selected dataset
4. Press ++escape++ to return to search

---

## Advanced Techniques

### Rapid Exploration

**Workflow:**

1. Type partial query (e.g., "wea")
2. Scan results as you type
3. Press ++enter++ → ++j++ / ++k++ → ++enter++ to open details
4. Press ++escape++ to return
5. Repeat

**Use case:** Quickly review multiple datasets matching a keyword.

---

### Project-Specific Search

**Goal:** Find all datasets for a specific project.

**Steps:**

1. Type project name (e.g., "Climate Dashboard")
2. Results show all datasets with that project in `used_in_projects`

**Tip:** Use consistent project names when adding datasets.

---

### Source-Based Search

**Goal:** Find all datasets from a specific source (e.g., GitHub, Earth Engine).

**Examples:**

- **Query:** "github.com" → Finds datasets with GitHub sources
- **Query:** "ee.ImageCollection" → Finds Earth Engine datasets
- **Query:** "s3://" → Finds datasets stored in S3

---

## Search Best Practices

### Be Specific

❌ **Too broad:** "data"

✅ **Specific:** "weather temperature 2024"

---

### Use Unique Terms

**Rare terms rank higher:**

- "MODIS" (unique) > "temperature" (common)
- "GeoTIFF" (unique) > "file" (common)

---

### Search by Project Early

If you know the project, start there:

```
Climate Dashboard
```

Then refine:

```
Climate Dashboard temperature
```

---

### Check Empty Search First

If you're not sure what you're looking for:

1. Clear search (++escape++ twice)
2. Browse all datasets
3. Notice patterns (project names, data types)
4. Then search

---

## Common Search Patterns

### "What datasets do I have from [source]?"

**Query:** `github.com`

---

### "What datasets are used in [project]?"

**Query:** `Climate Dashboard`

---

### "What weather-related datasets do I have?"

**Query:** `weather`

---

### "What satellite datasets do I have?"

**Query:** `MODIS` or `Landsat` or `Sentinel`

---

### "What datasets cover [topic]?"

**Query:** `wildfire` or `ocean` or `urban`

---

## Troubleshooting

### No Results for Common Word

**Problem:** Searching "data" returns nothing.

**Cause:** "data" appears in almost every dataset, so BM25 ranks it low.

**Fix:** Add more specific terms:

```
data temperature
```

---

### Too Many Results

**Problem:** 100+ results for "temperature".

**Fix:** Narrow with additional terms:

```
temperature daily 2024
```

---

### Expected Dataset Not Found

**Problem:** You know a dataset exists but it doesn't appear in results.

**Possible causes:**

1. **Not indexed:** Run `hei-datahub reindex`
2. **Different wording:** Try synonyms (e.g., "temp" vs. "temperature")
3. **Typo in metadata:** Check the YAML file

---

### Search Feels Slow

**Problem:** Noticeable lag when typing.

**Cause:** Large dataset count (>10,000).

**Fix:**

- Optimize FTS5 index:
    ```bash
    sqlite3 db.sqlite "INSERT INTO datasets_fts(datasets_fts) VALUES('optimize')"
    ```

---

## Practice Exercises

### Exercise 1: Find Climate Datasets

**Goal:** Find all datasets related to climate analysis.

**Steps:**

1. Search: `climate`
2. Note how many results
3. Refine: `climate temperature`
4. Compare results

---

### Exercise 2: Project-Specific Search

**Goal:** Find all datasets for "Gideon" project.

**Steps:**

1. Search: `Gideon`
2. Count results
3. Open one dataset and verify `used_in_projects` field

---

### Exercise 3: Source-Based Search

**Goal:** Find all Earth Engine datasets.

**Steps:**

1. Search: `ee.ImageCollection`
2. Verify source field in details

---

### Exercise 4: Wildcard Prefix Search

**Goal:** Find datasets with "geo*" prefix.

**Steps:**

1. Search: `geo`
2. Note matches: "GeoTIFF", "geospatial", "geographic"

---

## Future Search Features

Not yet available in v0.55.x but planned:

### Field-Specific Search

```
source:github.com
format:CSV
project:"Climate Dashboard"
```

---

### Date Range Filters

```
created:2024-01-01..2024-12-31
```

---

### Size Filters

```
size:>1GB
```

---

### Boolean Operators

```
temperature AND precipitation
climate OR weather
NOT test
```

---

## Tips for Power Users

### Use Keyboard Exclusively

**Workflow:**

1. ++slash++ → Type query
2. ++enter++ → Focus results
3. ++j++ / ++k++ → Navigate
4. ++enter++ → Open details
5. ++escape++ → Back to search

**No mouse needed!**

---

### Jump to Top/Bottom

After search:

- ++g+g++ → First result
- ++shift+g++ → Last result

---

### Copy Source Quickly

On Details Screen:

- ++c++ → Copy source to clipboard

Paste into notebook/terminal.

---

## Next Steps

- **[The Basics](../03-the-basics.md)** — Understand datasets, fields, metadata
- **[Configuration](../12-config.md)** — Set up GitHub integration
- **[FAQ](../90-faq.md)** — Troubleshooting search issues

---

## Getting Help

- **FAQ:** [Common search issues](../90-faq.md#search-issues)
- **Issues:** [Report bugs or request features](https://github.com/0xpix/Hei-DataHub/issues)
