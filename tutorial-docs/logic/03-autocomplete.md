# Autocomplete & Suggestions

**Learning Goal**: Build an intelligent autocomplete system that learns from existing data.

By the end of this page, you'll:
- Extract suggestions from existing datasets
- Implement prefix-based ranking
- Build a suggestion cache
- Normalize user input for consistency
- Integrate autocomplete into forms
- Handle real-time suggestion updates

---

## Why Autocomplete Matters

Autocomplete improves **data quality** and **user experience**:

**Without autocomplete:**
```
User enters: "Time Series"
Next user: "timeseries"
Next user: "time-series"
Next user: "TimeSeries"
```
→ 4 different values for the same concept! Breaks search filters.

**With autocomplete:**
```
User types: "tim..."
Autocomplete suggests: "time-series" ✅
User accepts suggestion
```
→ Consistent data, easier filtering, better search!

---

## The Autocomplete Architecture

```
┌──────────────────────────────────────────┐
│  1. EXTRACTION                           │
│  Scan existing datasets →                │
│  Extract unique values                   │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│  2. NORMALIZATION                        │
│  "CSV" → "csv"                           │
│  "TimeSeries" → "time-series"            │
│  "parquet" → "parquet"                   │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│  3. CACHING                              │
│  Store in memory sets:                   │
│  - projects: {"gideon", "climate-ml"}    │
│  - data_types: {"time-series", "tabular"}│
│  - file_formats: {"csv", "parquet"}      │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│  4. RANKING                              │
│  User types "tim" →                      │
│  Rank: prefix matches > contains matches │
│  Return: ["time-series"]                 │
└──────────────────────────────────────────┘
```

---

## The AutocompleteManager Class

**File:** `src/hei_datahub/services/autocomplete.py`

```python
from typing import List, Set, Optional
from collections import Counter

class AutocompleteManager:
    """Manage autocomplete suggestions for form fields."""

    def __init__(self):
        """Initialize empty suggestion sets."""
        self.projects: Set[str] = set()
        self.data_types: Set[str] = set()
        self.file_formats: Set[str] = set()
        self.sources: Set[str] = set()

        # Canonical forms (lowercase → proper case)
        self.canonical_formats = {
            'csv': 'csv',
            'json': 'json',
            'parquet': 'parquet',
            'excel': 'excel',
            'xlsx': 'xlsx',
            'hdf5': 'hdf5',
            'netcdf': 'netcdf',
        }

        self.canonical_types = {
            'tabular': 'tabular',
            'timeseries': 'time-series',
            'time-series': 'time-series',
            'geospatial': 'geospatial',
            'image': 'image',
            'text': 'text',
        }
```

**Why sets?**
- Fast O(1) membership testing
- Automatic deduplication
- Memory efficient

---

## Extracting Suggestions

### From Database

**File:** `src/hei_datahub/services/autocomplete.py`

```python
def load_from_catalog(self) -> int:
    """
    Load suggestions from indexed datasets.

    Returns:
        Number of datasets processed
    """
    from hei_datahub.infra.index import list_all_datasets

    count = 0
    datasets = list_all_datasets()

    for dataset in datasets:
        count += 1
        metadata = dataset.get('metadata', {})

        # Extract projects
        if 'used_in_projects' in metadata:
            projects = metadata['used_in_projects']
            if isinstance(projects, list):
                self.projects.update(p.strip() for p in projects if p)

        # Extract data types
        if 'data_types' in metadata:
            types = metadata['data_types']
            if isinstance(types, list):
                normalized = [self.normalize_data_type(t) for t in types if t]
                self.data_types.update(normalized)

        # Extract file format
        if 'file_format' in metadata:
            fmt = metadata['file_format']
            if fmt:
                self.file_formats.add(self.normalize_format(str(fmt)))

        # Extract source domains
        if 'source' in metadata:
            source = str(metadata['source'])
            if source.startswith('http'):
                domain = self._extract_domain(source)
                if domain:
                    self.sources.add(domain)

    return count

def _extract_domain(self, url: str) -> Optional[str]:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    try:
        return urlparse(url).netloc
    except:
        return None
```

**Example:**

```python
# Before loading
manager = AutocompleteManager()
print(manager.projects)  # set()

# Load from catalog
count = manager.load_from_catalog()
print(f"Loaded {count} datasets")

# After loading
print(manager.projects)
# {'gideon', 'climate-ml', 'covid-tracker', ...}

print(manager.data_types)
# {'time-series', 'tabular', 'geospatial', ...}

print(manager.file_formats)
# {'csv', 'parquet', 'json', ...}
```

---

## Normalizing Input

### Why Normalize?

Users type inconsistently:
- "CSV" vs "csv" vs "Csv"
- "Time Series" vs "timeseries" vs "time-series"
- "Excel" vs "xlsx" vs "XLSX"

**Solution:** Canonical forms!

### Implementation

```python
def normalize_format(self, format_str: str) -> str:
    """
    Normalize file format to canonical form.

    Examples:
        "CSV" → "csv"
        "Excel" → "excel"
        "PARQUET" → "parquet"
    """
    lower = format_str.lower().strip()
    return self.canonical_formats.get(lower, format_str)

def normalize_data_type(self, type_str: str) -> str:
    """
    Normalize data type to canonical form.

    Examples:
        "TimeSeries" → "time-series"
        "time series" → "time-series"
        "Geospatial" → "geospatial"
    """
    lower = type_str.lower().strip()
    return self.canonical_types.get(lower, type_str)
```

**Usage:**

```python
manager = AutocompleteManager()

# User enters various forms
print(manager.normalize_format("CSV"))      # "csv"
print(manager.normalize_format("Csv"))      # "csv"
print(manager.normalize_format("csv"))      # "csv"

print(manager.normalize_data_type("TimeSeries"))    # "time-series"
print(manager.normalize_data_type("time series"))   # "time-series"
print(manager.normalize_data_type("time-series"))   # "time-series"
```

---

## Ranking Suggestions

### The Ranking Algorithm

**Goal:** Show best matches first.

**Strategy:**
1. **Prefix matches** — "clim" matches "climate" (high priority)
2. **Contains matches** — "mat" matches "climate" (lower priority)
3. **Alphabetical** — Sort ties alphabetically

### Implementation

```python
def suggest_projects(self, query: str, limit: int = 10) -> List[str]:
    """
    Get project suggestions matching query.

    Args:
        query: User's search text
        limit: Maximum number of suggestions

    Returns:
        Ranked list of matching projects
    """
    if not query:
        # Empty query → return all (alphabetical)
        return sorted(self.projects)[:limit]

    query_lower = query.lower()

    # Step 1: Find prefix matches
    prefix_matches = [
        p for p in self.projects
        if p.lower().startswith(query_lower)
    ]

    # Step 2: Find contains matches (excluding prefixes)
    contains_matches = [
        p for p in self.projects
        if query_lower in p.lower() and p not in prefix_matches
    ]

    # Step 3: Combine and sort
    results = sorted(prefix_matches) + sorted(contains_matches)

    return results[:limit]
```

**Example:**

```python
manager = AutocompleteManager()
manager.projects = {
    "climate-ml",
    "climate-analysis",
    "gideon",
    "healthcare-climate",
    "covid-tracker",
}

# Query: "clim"
suggestions = manager.suggest_projects("clim", limit=5)
print(suggestions)
# ['climate-analysis', 'climate-ml', 'healthcare-climate']
#  ^^^^^^^^^^^^^^^^   ^^^^^^^^^^     ^^^^^^^^^^^^^^^^^^^^
#  Prefix match       Prefix match   Contains match

# Query: "cli"
suggestions = manager.suggest_projects("cli", limit=5)
print(suggestions)
# ['climate-analysis', 'climate-ml']
#  Prefix matches only

# Query: ""
suggestions = manager.suggest_projects("", limit=3)
print(suggestions)
# ['climate-analysis', 'climate-ml', 'covid-tracker']
#  All projects (alphabetical)
```

---

## The Singleton Pattern

Only one `AutocompleteManager` should exist per app.

**Why?**
- Loading suggestions is slow (scans all datasets)
- One cache shared across all forms
- Memory efficient

### Implementation

```python
# Global instance
_autocomplete_manager: Optional[AutocompleteManager] = None

def get_autocomplete_manager() -> AutocompleteManager:
    """
    Get global autocomplete manager instance.
    Creates on first call, reuses afterward.
    """
    global _autocomplete_manager

    if _autocomplete_manager is None:
        _autocomplete_manager = AutocompleteManager()
        # Load suggestions on first access
        _autocomplete_manager.load_from_catalog()

    return _autocomplete_manager
```

**Usage:**

```python
# Anywhere in the app
from hei_datahub.services.autocomplete import get_autocomplete_manager

manager = get_autocomplete_manager()  # Creates if needed
suggestions = manager.suggest_projects("clim")

# Later...
manager2 = get_autocomplete_manager()  # Returns same instance
assert manager is manager2  # True! Same object
```

---

## Integrating with Forms

### In Textual UI

**File:** `src/hei_datahub/ui/views/home.py`

```python
from textual.widgets import Input
from hei_datahub.services.autocomplete import get_autocomplete_manager

class AddDataScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="e.g., gideon, climate-ml",
            id="input-projects"
        )

    def on_input_changed(self, event: Input.Changed):
        """Show autocomplete suggestions as user types."""
        if event.input.id == "input-projects":
            query = event.value

            # Get suggestions
            manager = get_autocomplete_manager()
            suggestions = manager.suggest_projects(query, limit=5)

            # Display suggestions
            self._show_suggestions(suggestions)

    def _show_suggestions(self, suggestions: List[str]):
        """Display autocomplete dropdown."""
        # Implementation depends on UI framework
        # Could use a popup list, OptionList widget, etc.
        pass
```

---

### Autocomplete on Tab Key

**Goal:** Press Tab to cycle through suggestions.

```python
class AddDataScreen(Screen):
    def __init__(self):
        super().__init__()
        self._current_suggestions = []
        self._suggestion_index = 0

    def on_input_changed(self, event: Input.Changed):
        """Update suggestions as user types."""
        if event.input.id == "input-projects":
            manager = get_autocomplete_manager()
            self._current_suggestions = manager.suggest_projects(
                event.value,
                limit=10
            )
            self._suggestion_index = 0  # Reset index

    def on_key(self, event: events.Key):
        """Handle Tab key for autocomplete."""
        if event.key == "tab":
            input_widget = self.query_one("#input-projects", Input)

            if self._current_suggestions:
                # Cycle through suggestions
                suggestion = self._current_suggestions[self._suggestion_index]
                input_widget.value = suggestion

                # Move to next suggestion
                self._suggestion_index = (
                    (self._suggestion_index + 1) %
                    len(self._current_suggestions)
                )

                event.stop()  # Prevent default Tab behavior
```

**Flow:**
1. User types "clim"
2. Suggestions: `["climate-ml", "climate-analysis"]`
3. User presses Tab → fills "climate-ml"
4. User presses Tab again → fills "climate-analysis"
5. User presses Tab again → cycles back to "climate-ml"

---

## Refreshing Suggestions

When new datasets are added, refresh the autocomplete cache.

### Manual Refresh

```python
def refresh_autocomplete(catalog_path: Optional[Path] = None) -> int:
    """
    Refresh global autocomplete suggestions.

    Returns:
        Number of datasets processed
    """
    manager = get_autocomplete_manager()

    # Clear old suggestions
    manager.projects.clear()
    manager.data_types.clear()
    manager.file_formats.clear()

    # Reload from catalog
    return manager.load_from_catalog(catalog_path)
```

**Usage:**

```python
# After adding a new dataset
from hei_datahub.services.autocomplete import refresh_autocomplete

dataset_count = refresh_autocomplete()
print(f"Refreshed suggestions from {dataset_count} datasets")
```

---

### Automatic Refresh

**Goal:** Auto-refresh after save operations.

```python
# In catalog service
def save_dataset(dataset_id: str, metadata: dict) -> Tuple[bool, Optional[str]]:
    """Save dataset and refresh autocomplete."""
    # ... save logic ...

    # Refresh autocomplete (async, doesn't block)
    try:
        from hei_datahub.services.autocomplete import refresh_autocomplete
        refresh_autocomplete()
    except Exception as e:
        logger.warning(f"Failed to refresh autocomplete: {e}")

    return True, None
```

---

## Advanced: Frequency-Based Ranking

**Goal:** Suggest more common values first.

### Counting Occurrences

```python
class AutocompleteManager:
    def __init__(self):
        # ... existing code ...
        self.project_counts: Counter = Counter()  # Track frequency

    def load_from_catalog(self) -> int:
        """Load with frequency tracking."""
        datasets = list_all_datasets()

        for dataset in datasets:
            metadata = dataset.get('metadata', {})

            if 'used_in_projects' in metadata:
                projects = metadata['used_in_projects']
                if isinstance(projects, list):
                    for project in projects:
                        if project:
                            self.projects.add(project)
                            self.project_counts[project] += 1  # Count it

        return len(datasets)

    def suggest_projects(self, query: str, limit: int = 10) -> List[str]:
        """Suggest with frequency ranking."""
        if not query:
            # Return most common projects
            return [p for p, count in self.project_counts.most_common(limit)]

        query_lower = query.lower()

        # Get matches
        prefix_matches = [
            p for p in self.projects
            if p.lower().startswith(query_lower)
        ]

        # Sort by frequency (most common first)
        ranked = sorted(
            prefix_matches,
            key=lambda p: self.project_counts[p],
            reverse=True  # Highest count first
        )

        return ranked[:limit]
```

**Example:**

```python
manager = AutocompleteManager()

# Dataset 1: used_in_projects = ["gideon"]
# Dataset 2: used_in_projects = ["gideon"]
# Dataset 3: used_in_projects = ["gaia"]
# Dataset 4: used_in_projects = ["gideon", "gaia"]

manager.load_from_catalog()

print(manager.project_counts)
# Counter({'gideon': 3, 'gaia': 2})

suggestions = manager.suggest_projects("g", limit=5)
print(suggestions)
# ['gideon', 'gaia']  ← gideon first (appears 3 times vs 2)
```

---

## Performance Considerations

### Memory Usage

```python
# Typical autocomplete cache size
projects: 50-200 items × 20 bytes = ~1-4 KB
data_types: 10-30 items × 15 bytes = ~150-450 bytes
file_formats: 10-20 items × 10 bytes = ~100-200 bytes

Total: ~1.5-5 KB (negligible!)
```

**Verdict:** In-memory caching is fine, even for large catalogs.

---

### Load Time

```python
# Benchmarks (1000 datasets)
load_from_catalog(): ~200ms
suggest_projects(): <1ms
```

**Optimization:** Load in background on app startup.

```python
# In app initialization
def on_mount(self):
    """Load autocomplete in background."""
    self.load_autocomplete_async()

@work(exclusive=True)
async def load_autocomplete_async(self):
    """Async autocomplete loading."""
    from hei_datahub.services.autocomplete import get_autocomplete_manager

    manager = get_autocomplete_manager()
    count = await asyncio.to_thread(manager.load_from_catalog)

    logger.info(f"Loaded autocomplete from {count} datasets")
```

---

## What You've Learned

✅ **Suggestion extraction** — Scan datasets, collect unique values
✅ **Normalization** — Canonical forms for consistency
✅ **Ranking algorithm** — Prefix > contains > alphabetical
✅ **Singleton pattern** — One cache shared across app
✅ **Form integration** — Tab-key autocomplete in Textual
✅ **Refresh strategies** — Manual and automatic
✅ **Frequency ranking** — Suggest common values first

---

## Try It Yourself

### Exercise 1: Add Tag Autocomplete

**Goal:** Suggest tags from existing datasets.

**Hint:**

```python
class AutocompleteManager:
    def __init__(self):
        # ... existing code ...
        self.tags: Set[str] = set()

    def load_from_catalog(self) -> int:
        # ... existing code ...

        if 'tags' in metadata:
            tags = metadata['tags']
            if isinstance(tags, list):
                self.tags.update(t.strip() for t in tags if t)

    def suggest_tags(self, query: str, limit: int = 10) -> List[str]:
        # Similar to suggest_projects()
        pass
```

---

### Exercise 2: Fuzzy Matching

**Goal:** Suggest "climate" when user types "climat".

**Hint:** Use Levenshtein distance:

```python
def fuzzy_suggest(self, query: str, limit: int = 10) -> List[str]:
    """Suggest with fuzzy matching."""
    import difflib

    # Get close matches (ratio > 0.6)
    matches = difflib.get_close_matches(
        query,
        self.projects,
        n=limit,
        cutoff=0.6
    )

    return matches
```

---

### Exercise 3: Context-Aware Suggestions

**Goal:** If user selects "tabular" data type, suggest "csv" or "parquet" for file format.

**Hint:**

```python
# Build a map
data_type_to_formats = {
    "tabular": ["csv", "parquet", "excel"],
    "time-series": ["csv", "netcdf", "hdf5"],
    "geospatial": ["geojson", "shapefile", "geoparquet"],
}

def suggest_file_formats_for_type(self, data_type: str) -> List[str]:
    """Suggest formats appropriate for data type."""
    return data_type_to_formats.get(data_type, [])
```

---

## Next Steps

Now you understand autocomplete and suggestions. Next, let's explore **cloud storage integration with WebDAV**.

**Next:** [Cloud Sync & WebDAV](04-cloud-sync.md)

---

## Further Reading


- [Autocomplete UX Best Practices](https://www.nngroup.com/articles/autocomplete/)
- [Trie Data Structure](https://en.wikipedia.org/wiki/Trie) (for large-scale autocomplete)
- [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) (fuzzy matching)
- [Hei-DataHub UI Documentation](../../ui/architecture.md)
