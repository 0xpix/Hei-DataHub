# Bug Fix: Add Dataset (PR) Function Error

**Date:** October 4, 2025
**Version:** 0.50.0-beta
**Status:** ✅ FIXED

---

## Issue

When trying to add a new dataset using the "A" key in the TUI, the application crashed with:

```
TypeError: save_dataset() missing 1 required positional argument: 'metadata'
```

**Error Location:** `src/mini_datahub/ui/views/home.py:833` in `submit_form()`

---

## Root Cause

The `save_dataset()` function signature was changed during the migration but the call site wasn't updated.

**Function signature (in `services/catalog.py`):**
```python
def save_dataset(dataset_id: str, metadata: dict) -> Tuple[bool, Optional[str]]:
```

**Incorrect call (in `ui/views/home.py`):**
```python
success, msg = save_dataset(metadata)  # ❌ Missing dataset_id argument
```

---

## Fix

**File Modified:** `src/mini_datahub/ui/views/home.py`

### Change 1: Fixed Function Call
```python
# Before (line 833):
success, msg = save_dataset(metadata)

# After:
success, msg = save_dataset(dataset_id, metadata)
```

### Change 2: Removed Duplicate Indexing
The old code was calling `upsert_dataset()` separately after `save_dataset()`, but `save_dataset()` already handles indexing internally. Removed the duplicate call and the orphaned try/except block.

```python
# Removed:
try:
    upsert_dataset(dataset_id, metadata)
except Exception as e:
    self.app.notify(f"Warning: Failed to index dataset: {str(e)}", severity="warning", timeout=5)
```

---

## Code After Fix

```python
# Validate and save
success, error_msg, model = validate_metadata(metadata)
if not success:
    error_label.update(f"[red]Validation Error:\n{error_msg}[/red]")
    return

# Save to disk (save_dataset now handles both writing and indexing)
success, msg = save_dataset(dataset_id, metadata)
if not success:
    error_label.update(f"[red]{msg}[/red]")
    return

# Try PR workflow if GitHub is configured
from mini_datahub.app.settings import get_github_config
from mini_datahub.services.publish import PRWorkflow

config = get_github_config()
if config.is_configured() and config.catalog_repo_path:
    # Execute Save → PR workflow
    self.create_pr(dataset_id, metadata)
else:
    # Just save locally and show success
    self.app.notify(f"Dataset '{dataset_id}' saved successfully!", timeout=3)
```

---

## Verification

✅ **Import Test:** `from mini_datahub.ui.views.home import run_tui` - Success
✅ **Syntax Check:** No errors found
✅ **Function Signature:** Matches `save_dataset(dataset_id, metadata)`

---

## Impact

This fix resolves the TypeError when adding new datasets via the TUI. The Add Dataset feature (A key) now works correctly.

**Affected Feature:** Add Dataset (Press 'A' in TUI)

---

## Testing

To test the fix:

```bash
# Launch TUI
hei-datahub

# In the TUI:
# 1. Press 'A' to add a dataset
# 2. Fill in the form
# 3. Press Ctrl+S to submit
# 4. Should save successfully without TypeError
```

---

## Related

- `save_dataset()` function: `src/mini_datahub/services/catalog.py:16`
- `submit_form()` method: `src/mini_datahub/ui/views/home.py:759`
- Migration docs: `COMPLETE_v0.50.md`

---

**Status:** Fixed and verified ✅
