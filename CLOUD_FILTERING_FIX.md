# Cloud-Only Filtering Update

## Issues Fixed

### Issue 1: Local datasets still showing in TUI
**Problem**: Even with cloud-only workflow, local datasets from the `data/` directory were still appearing in the search results and dataset list.

**Root Cause**: The `load_all_datasets()` and `perform_search()` methods were displaying ALL datasets from the index (both local and remote).

**Solution**: Added filtering to show ONLY cloud datasets (where `is_remote=True`).

### Issue 2: Cloud data not updating in HeiBox
**Problem**: When editing a cloud dataset, the name wasn't being updated in HeiBox WebDAV storage.

**Root Cause**: Likely a silent failure or the upload wasn't properly overwriting the existing file.

**Solution**: Added extensive logging to `CloudEditDetailsScreen.save_to_cloud()` to track:
- What metadata is being saved
- The conversion from `dataset_name` → `name` field
- The temp file creation
- The upload path
- Upload success/failure
- Index update status

## Changes Made

### 1. Filter Cloud-Only Datasets in `load_all_datasets()`

**File**: `src/mini_datahub/ui/views/home.py`

**Before**:
```python
results = get_all_indexed()
# ... shows all results (local + cloud)
```

**After**:
```python
results = get_all_indexed()

# CLOUD-ONLY: Filter to show only remote datasets
cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]

# ... shows only cloud_results
```

**Effect**:
- UI now shows "☁️ Cloud Datasets (N total)" instead of "All Datasets"
- Local datasets from `data/` directory are hidden
- Only WebDAV-stored datasets appear in the list

### 2. Filter Cloud-Only Datasets in `perform_search()`

**File**: `src/mini_datahub/ui/views/home.py`

**Before**:
```python
results = search_indexed(query)
# ... shows all matching results (local + cloud)
```

**After**:
```python
results = search_indexed(query)

# CLOUD-ONLY: Filter to show only remote datasets
cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]

# ... shows only cloud_results
```

**Effect**:
- Search shows "☁️ Cloud Results (N found)"
- Local datasets excluded from search results
- Consistent cloud-only experience

### 3. Enhanced Logging in `CloudEditDetailsScreen.save_to_cloud()`

**File**: `src/mini_datahub/ui/views/home.py`

**Added Logging**:
```python
logger.info(f"CloudEditDetailsScreen: Saving {self.dataset_id} to cloud")
logger.debug(f"Metadata to save: {self.metadata}")
logger.debug(f"Converting dataset_name '{value}' to name field")
logger.debug(f"Created temp file: {tmp_path}")
logger.info(f"Uploading to: {remote_path}")
logger.info(f"✓ Successfully uploaded {remote_path}")
logger.debug(f"Updating index with name='{name}'")
logger.info("✓ Search index updated")
logger.info(f"Refreshing CloudDatasetDetailsScreen for {self.dataset_id}")
logger.error(f"Error uploading to cloud: {e}", exc_info=True)
```

**How to Use**:
1. Check logs at `logs/` directory (or `~/.local/share/Hei-DataHub/logs/`)
2. Look for upload errors or warnings
3. Verify the name conversion is happening correctly
4. Check if upload is actually succeeding

### 4. Updated Validation Tests

**File**: `scripts/validate_cloud_only.py`

Added new test: `test_cloud_only_filtering()`
- Verifies `load_all_datasets` has cloud filtering
- Verifies `perform_search` has cloud filtering
- All 5 tests now pass ✅

## Testing the Fix

### Test 1: Verify Local Datasets are Hidden

1. Run the app: `python -m mini_datahub`
2. You should see "☁️ Cloud Datasets (N total)"
3. Only datasets from HeiBox should appear
4. Local datasets in `data/` should NOT appear

### Test 2: Verify Search is Cloud-Only

1. Search for a dataset
2. Label should show "☁️ Cloud Results (N found)"
3. Only cloud datasets should match
4. Local datasets should be excluded

### Test 3: Verify Edit Updates Cloud

1. Open a cloud dataset
2. Press `e` to edit
3. Change the name
4. Press `Ctrl+S` to save
5. Check logs for upload confirmation
6. Verify in HeiBox WebDAV that `metadata.yaml` was updated

### Where to Check Logs

**Linux**:
```bash
tail -f ~/.local/share/Hei-DataHub/logs/mini-datahub.log
```

**Look for**:
```
INFO: CloudEditDetailsScreen: Saving dataset-id to cloud
DEBUG: Converting dataset_name 'New Name' to name field
INFO: Uploading to: dataset-id/metadata.yaml
INFO: ✓ Successfully uploaded dataset-id/metadata.yaml
```

## Troubleshooting

### If Edit Still Doesn't Update HeiBox:

1. **Check WebDAV Permissions**:
   - Verify you have WRITE permissions (not just READ)
   - Check HeiBox folder permissions

2. **Check Auth**:
   ```bash
   python -m mini_datahub auth doctor
   ```
   - Look for "WRITE" status (should be "OK" not "403")

3. **Check Logs**:
   - Look for `StorageAuthError` or `403 Forbidden`
   - May need to re-authenticate or update permissions

4. **Manual Verification**:
   - Log into HeiBox web interface
   - Navigate to the dataset folder
   - Download `metadata.yaml`
   - Check if `name:` field has the new value

### If Local Datasets Still Appear:

1. **Rebuild Index**:
   ```bash
   python scripts/rebuild_index.py
   ```

2. **Clear Cache**:
   ```bash
   rm -rf ~/.cache/hei-datahub/index.db
   ```
   - Restart app to rebuild index

3. **Check Index Contents**:
   ```bash
   sqlite3 ~/.cache/hei-datahub/index.db "SELECT path, is_remote FROM items;"
   ```
   - Verify `is_remote` is 1 for cloud datasets

## Summary

**Fixed:**
- ✅ Local datasets no longer appear in TUI (cloud-only filtering)
- ✅ Added extensive logging for debugging cloud upload issues
- ✅ Updated validation tests (5/5 passing)

**Next Steps:**
- Test editing a cloud dataset
- Check logs to verify upload is working
- Verify HeiBox has the updated `metadata.yaml`
- If issues persist, check auth permissions (WRITE access needed)
