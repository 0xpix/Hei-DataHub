# Fix: Dataset Name Not Updating After Edit

## Problem

When editing a cloud dataset and changing its name (e.g., "weather" → "weather (edited)"), the changes were saved to HeiBox but:
1. The HomeScreen table (dataset list) still showed the old name
2. The CloudDatasetDetailsScreen was refreshed but the table wasn't

## Root Cause

After saving edits in `CloudEditDetailsScreen.save_to_cloud()`:
- ✅ Metadata was correctly uploaded to HeiBox WebDAV
- ✅ Search index was updated with new name
- ✅ CloudDatasetDetailsScreen was refreshed to show new name
- ❌ **HomeScreen table was NOT refreshed** - still showed cached old name from index

The table was displaying stale data because it wasn't being told to reload.

## Solution

Added HomeScreen table refresh after:
1. Editing a dataset (in `CloudEditDetailsScreen.save_to_cloud()`)
2. Adding a new dataset (in `AddDataScreen.save_to_cloud()`)

### Changes Made

**File**: `src/mini_datahub/ui/views/home.py`

#### 1. CloudEditDetailsScreen.save_to_cloud() - After Edit

```python
# Refresh the parent CloudDatasetDetailsScreen
def refresh_parent():
    for screen in self.app.screen_stack:
        if isinstance(screen, CloudDatasetDetailsScreen) and screen.dataset_id == self.dataset_id:
            # Reload metadata from cloud
            logger.info(f"Refreshing CloudDatasetDetailsScreen for {self.dataset_id}")
            screen.load_metadata()
            break

    # ADDED: Also refresh the HomeScreen table to show updated name
    for screen in self.app.screen_stack:
        if isinstance(screen, HomeScreen):
            logger.info("Refreshing HomeScreen table with updated dataset")
            screen.load_all_datasets()
            break

self.app.call_from_thread(refresh_parent)
```

#### 2. AddDataScreen.save_to_cloud() - After Add

```python
# Close form and show details
self.app.call_from_thread(self.app.pop_screen)
self.app.call_from_thread(self.app.push_screen, CloudDatasetDetailsScreen(dataset_id))

# ADDED: Refresh the HomeScreen table to show new dataset
def refresh_home():
    for screen in self.app.screen_stack:
        if isinstance(screen, HomeScreen):
            logger.info("Refreshing HomeScreen table with new dataset")
            screen.load_all_datasets()
            break

self.app.call_from_thread(refresh_home)
```

## How It Works

1. **User edits dataset name** (e.g., "weather" → "weather (edited)")
2. **Save to cloud**: Upload metadata.yaml to HeiBox with new name
3. **Update search index**: FTS5 index gets new name
4. **Refresh detail screen**: CloudDatasetDetailsScreen reloads metadata
5. **Refresh home screen**: HomeScreen table reloads from updated index ✨
6. **User sees**: Updated name in both detail view AND table list

## Testing

### Before Fix:
```
1. Edit dataset name: "weather" → "weather (edited)"
2. Press Ctrl+S
3. Detail view shows: "weather (edited)" ✓
4. Go back to home screen
5. Table still shows: "weather" ✗ (stale!)
```

### After Fix:
```
1. Edit dataset name: "weather" → "weather (edited)"
2. Press Ctrl+S
3. Detail view shows: "weather (edited)" ✓
4. Go back to home screen
5. Table shows: "weather (edited)" ✓ (refreshed!)
```

## Notes

- The index is updated correctly (verified by checking index directly)
- The table just wasn't being told to reload from the updated index
- This fix makes the UI immediately reflect changes
- Same pattern applied to both edit and add operations for consistency

## Related Files

- `src/mini_datahub/ui/views/home.py` - CloudEditDetailsScreen, AddDataScreen, HomeScreen
- `src/mini_datahub/services/index_service.py` - FTS5 index (already working correctly)
