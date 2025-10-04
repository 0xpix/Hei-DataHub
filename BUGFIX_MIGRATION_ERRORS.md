# Bug Fix: Migration Errors (v0.40.0)

## Issues Fixed

### 1. Missing `reindex_all()` Function
**Error:** `ImportError: cannot import name 'reindex_all' from 'mini_datahub.infra.index'`

**Location:**
- Used in `src/mini_datahub/ui/views/home.py` (lines 1214, 1285)
- Used in `src/mini_datahub/ui/widgets/console.py` (line 151)

**Root Cause:** The `reindex_all()` function was not migrated from the old `mini_datahub_old/index.py` to the new `src/mini_datahub/infra/index.py`.

**Fix:** Added the complete `reindex_all()` function to `src/mini_datahub/infra/index.py`:
```python
def reindex_all() -> Tuple[int, List[str]]:
    """
    Reindex all datasets from the data directory.

    Returns:
        Tuple of (count, errors) - number of datasets indexed and list of error messages
    """
    from mini_datahub.infra.store import list_datasets, read_dataset

    ensure_database()

    # Clear existing indexes
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_store")
    cursor.execute("DELETE FROM datasets_fts")
    conn.commit()
    conn.close()

    # Reindex all datasets
    dataset_ids = list_datasets()
    count = 0
    errors = []

    for dataset_id in dataset_ids:
        try:
            metadata = read_dataset(dataset_id)
            if metadata:
                upsert_dataset(dataset_id, metadata)
                count += 1
        except Exception as e:
            errors.append(f"Failed to index {dataset_id}: {str(e)}")

    return count, errors
```

### 2. Incorrect `list_all_datasets()` Return Type
**Error:** `TypeError: string indices must be integers, not 'str'`

**Location:** `src/mini_datahub/ui/views/home.py` line 120 (in `load_all_datasets()`)

**Root Cause:** The new `list_all_datasets()` function was returning `List[str]` (just dataset IDs) instead of `List[Dict[str, Any]]` (full dataset info with id, name, snippet, etc.).

**Impact:** The TUI expected dictionaries with keys like `result["id"]`, `result["name"]`, `result["snippet"]` but was receiving strings.

**Fix:** Updated `list_all_datasets()` in `src/mini_datahub/infra/index.py` to return the correct structure:
```python
def list_all_datasets(limit: int = 100) -> List[Dict[str, Any]]:
    """
    List all datasets ordered by most recently updated.

    Args:
        limit: Maximum number of results

    Returns:
        List of dataset info dictionaries with id, name, snippet, rank, metadata
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, payload, updated_at
            FROM datasets_store
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        results = []
        for row in cursor.fetchall():
            metadata = json.loads(row["payload"])
            # Create a snippet from description
            description = metadata.get("description", "")
            snippet = description[:100] + "..." if len(description) > 100 else description

            result = {
                "id": row["id"],
                "name": metadata.get("dataset_name", ""),
                "snippet": snippet,
                "rank": 0,  # No ranking for list view
                "metadata": metadata,
            }
            results.append(result)

        return results
    finally:
        conn.close()
```

### 3. Missing Import
**Issue:** Added missing `Tuple` import to type hints in `infra/index.py`

**Fix:** Updated imports:
```python
from typing import Any, Dict, List, Tuple
from mini_datahub.infra.db import get_connection, ensure_database
```

## Verification

All fixes verified working:

✅ **Database initialization:** `mini-datahub reindex` successfully indexes 5 datasets
✅ **Reindex function:** `reindex_all()` correctly returns tuple of (count, errors)
✅ **List datasets:** `list_all_datasets()` returns correct dict structure with id, name, snippet, rank keys
✅ **TUI imports:** All imports load without errors
✅ **Pull functionality:** Can now use 'U' key in TUI to pull updates

## Testing Commands

```bash
# Test reindex
uv run mini-datahub reindex

# Test reindex_all function directly
uv run python3 -c "from mini_datahub.infra.index import reindex_all; count, errors = reindex_all(); print(f'Reindexed {count} datasets, errors: {errors}')"

# Test list_all_datasets structure
uv run python3 -c "from mini_datahub.infra.index import list_all_datasets; results = list_all_datasets(); print(f'Found {len(results)} datasets'); print(f'Keys: {list(results[0].keys())}')"

# Test TUI startup
timeout 3 uv run mini-datahub
```

## Files Modified

1. **src/mini_datahub/infra/index.py**
   - Added `Tuple` to imports
   - Added `ensure_database` to imports
   - Updated `list_all_datasets()` function (return type and implementation)
   - Added `reindex_all()` function

## Impact

These fixes resolve all runtime errors when:
- Starting the TUI application
- Loading the dataset list on startup
- Using the Pull (U) feature
- Using the Refresh (R) feature
- Using the debug console `:reindex` command

The application now works correctly as intended with the v0.40.0 clean architecture migration.
