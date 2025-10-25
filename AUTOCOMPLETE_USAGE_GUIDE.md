# Smart Autocomplete & Badge System - Quick Start Guide

## 🚀 How to Use

### Autocomplete While Searching

The autocomplete system activates automatically as you type in the search bar:

#### Field-Based Autocomplete

**1. Project Suggestions**
```
Type: project:
→ Shows all known projects from your datasets

Type: project:ML
→ Shows projects starting with/containing "ML"
→ Ranked by: how often you use them + how recently + alphabetical
```

**2. Source Suggestions**
```
Type: source:
→ Shows all known sources (heibox, external, instrument, etc.)

Type: source:hei
→ Suggests "heibox" if it exists
```

**3. Tag Suggestions**
```
Type: tag:
→ Shows all tags used across datasets

Type: tag:neural
→ Shows tags containing "neural" (neural-network, neural-ml, etc.)
```

**4. Size Bucket Suggestions**
```
Type: size:
→ Shows: tiny, small, medium, large, xl

Type: size:s
→ Suggests "small" (with count of how many datasets)
```

**5. Format & Type Suggestions**
```
Type: format:
→ Shows known file formats (CSV, JSON, Parquet, etc.)

Type: type:
→ Shows known data types (tabular, image, text, etc.)
```

### Size Buckets Explained

| Bucket | Size Range | Example |
|--------|-----------|---------|
| `tiny` | < 10MB | Small config files |
| `small` | 10MB - 100MB | Medium datasets |
| `medium` | 100MB - 1GB | Large CSV files |
| `large` | 1GB - 10GB | Big datasets |
| `xl` | > 10GB | Huge archives |

**Usage:**
```
size:small          → Find datasets between 10-100MB
size:large          → Find datasets between 1-10GB
project:ML size:xl  → Find large ML datasets
```

### Keyboard Shortcuts

- **Tab** or **→ (Right Arrow)**: Accept the highlighted suggestion
- **Esc**: Close suggestion popup
- **Continue typing**: Refines suggestions in real-time

### Badge System

Badges appear below the search bar showing your active filters:

**Color Coding:**
- 📁 **Blue**: Project filters (`project:DataScience`)
- 🔗 **Purple**: Source filters (`source:heibox`)
- 🏷️ **Teal**: Tag filters (`tag:ml`)
- 👤 **Orange**: Owner filters (`owner:alice`)
- 📏 **Gray**: Size filters (`size:medium`)
- 📄 **Coral**: Format filters (`format:CSV`)
- 📊 **Sage**: Type filters (`type:tabular`)
- 📝 **Neutral**: Free text search terms

**Example Query:**
```
project:DeepLearning tag:neural source:heibox size:large model
```

**Badges Displayed:**
```
📁 project:DeepLearning  📏 size:large  🏷️ tag:neural  🔗 source:heibox  📝 model
 (Blue)                  (Gray)         (Teal)          (Purple)         (Neutral)
```

### Smart Ranking

Suggestions are ranked by:

1. **Prefix Match** (2.0x weight): Exact prefix matches rank highest
2. **Frequency** (1.5x weight): Filters you use often rank higher
3. **Recency** (1.2x weight): Recently used filters rank higher
4. **Alphabetical** (0.5x weight): Slight boost for earlier alphabet

**Example:**
If you frequently search for `project:ML-Research`, it will appear at the top when you type `project:M`, even if other projects also start with "M".

### Usage Tracking

Every time you execute a search, the system tracks which filters you used. This improves suggestions over time:

- **First use**: Alphabetical ordering
- **After 5 uses**: Frequency starts influencing ranking
- **Regular use**: Your most-used filters appear first

### Advanced Features

#### Multiple Filters
```
project:ML tag:neural tag:audio size:medium
```
Each filter gets its own colored badge!

#### Operators in Badges
```
size>100MB      → Shows: 📏 size>100MB
year>=2020      → Shows: 📊 year>=2020
project:ML      → Shows: 📁 project:ML
```

## 🛠️ For Developers

### Accessing Suggestion Service

```python
from mini_datahub.services.suggestion_service import get_suggestion_service

service = get_suggestion_service()

# Get suggestions for a field
suggestions = service.get_suggestions(
    key="project",      # Field type
    typed="ML",         # What user typed
    max_suggestions=10  # How many to return
)

# Track usage
service.track_usage("project", "ML-Research")

# Invalidate cache (call after reindex)
service.invalidate_cache()
```

### Adding New Suggestion Sources

Edit `suggestion_service.py`:

```python
def get_suggestions(self, key, typed, max_suggestions):
    if key == "your_new_field":
        return self._get_your_field_suggestions(typed, max_suggestions)
    # ... existing code
```

### Customizing Badge Colors

Edit `home.py` → `_get_badge_color_class()`:

```python
key_colors = {
    "your_field": "badge-custom-color",
    # ... existing mappings
}
```

## 📊 Performance

- **Cache Duration**: 5 minutes (refreshes automatically)
- **Query Speed**: < 10ms for suggestions (indexed SQLite)
- **Database**: Uses existing `index.db`, adds one small table
- **Memory**: Minimal (only caches distinct values)

## 🔍 Troubleshooting

### "No suggestions appearing"

1. Check that datasets are indexed: `hei-datahub index status`
2. Try typing more characters (minimum 1 char after `:`)
3. Verify field name is correct (project, source, tag, owner, size, format, type)

### "Suggestions seem wrong"

1. The system learns from usage - use filters a few times
2. Cache might be stale - wait 5 minutes or restart app
3. Check metadata in datasets (suggestions come from actual data)

### "Want to reset suggestion rankings"

Delete usage data:
```bash
sqlite3 ~/.cache/hei-datahub/index.db "DELETE FROM suggestion_usage"
```

## 🎯 Tips for Best Results

1. **Use filters consistently**: The system learns your patterns
2. **Type full filter names**: `project:` not just `proj:`
3. **Combine filters**: More specific = better results
4. **Check badge colors**: Quickly verify your query is correct
5. **Use size buckets**: Faster than typing exact sizes

## 🎨 Visual Reference

### Badge Examples

```
Input: project:DataScience

Badge: 📁 project:DataScience
       └── Blue background, project emoji
```

```
Input: source:heibox tag:ml size:large neural network

Badges:
🔗 source:heibox  🏷️ tag:ml  📏 size:large  📝 neural  📝 network
 (Purple)         (Teal)     (Gray)         (Neutral)  (Neutral)
```

---

**Enjoy faster, smarter searching!** 🚀
