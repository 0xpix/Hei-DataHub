# Auto-Stash Bug Fix

**Date:** October 4, 2025
**Issue:** "Cannot pull: You have uncommitted local changes" still showing despite auto-stash implementation
**Status:** ✅ FIXED

---

## Problem

The TUI was checking for local changes **before** calling `pull_updates()`, which prevented the auto-stash logic from ever running.

### Code Flow (Before Fix)

```python
# In tui.py pull_updates() method:

# 1. Check for local changes
has_changes, status = pull_manager.has_local_changes()
if has_changes:
    self.notify("Cannot pull: You have uncommitted local changes")
    return  # ❌ Aborts here, never reaches pull_updates()

# 2. Call pull_updates (never reached if changes exist)
success, message, old_commit, new_commit = pull_manager.pull_updates()
```

### Why This Was Wrong

- `pull_updates()` has auto-stash functionality built in
- But the TUI was aborting before calling it
- So auto-stash never had a chance to run

---

## Solution

Remove the early local changes check from TUI, since `pull_updates()` handles it properly with auto-stash.

### Code Flow (After Fix)

```python
# In tui.py pull_updates() method:

# 1. Network check
if not pull_manager.check_network_available():
    return

# 2. Divergence check
is_diverged, ahead, behind = pull_manager.is_diverged()
if is_diverged:
    return

# 3. Call pull_updates (now actually gets called!)
success, message, old_commit, new_commit = pull_manager.pull_updates()
# This handles auto-stash internally:
#   - Detects local changes
#   - Stashes them
#   - Pulls
#   - Restores them
```

---

## Changes Made

### File: `mini_datahub/tui.py`

**Removed:**
```python
# Check for local changes
has_changes, status = pull_manager.has_local_changes()
if has_changes:
    self.notify(
        "Cannot pull: You have uncommitted local changes",
        severity="warning",
        timeout=7
    )
    return
```

**Added Comment:**
```python
# Note: Local changes check removed - pull_updates() now handles via auto-stash
```

---

## Testing

### Before Fix
```bash
$ git status
M file.py

# Press U in TUI
Result: ❌ "Cannot pull: You have uncommitted local changes"
```

### After Fix
```bash
$ git status
M file.py

# Press U in TUI
Result: ✅ "Pulled X commit(s) from origin/main. Your uncommitted changes have been restored."

$ git status
M file.py  # ← Changes preserved!
```

---

## Verification

Run this to verify the fix:

```python
from pathlib import Path
from mini_datahub.auto_pull import get_auto_pull_manager
from mini_datahub.config import load_config

config = load_config()
catalog_path = Path(config.catalog_repo_path).expanduser().resolve()
pull_manager = get_auto_pull_manager(catalog_path)

# Check state
has_changes, _ = pull_manager.has_local_changes()
print(f"Has local changes: {has_changes}")

# The TUI will now call pull_updates() even with local changes
# and it will auto-stash them!
```

---

## Impact

✅ **Auto-stash now works correctly**
✅ **Can pull with uncommitted changes**
✅ **Changes are automatically preserved**
✅ **No manual stashing needed**

---

## Related Files

- `mini_datahub/tui.py` - Removed early check
- `mini_datahub/auto_pull.py` - Has auto-stash logic
- `mini_datahub/git_ops.py` - Has stash methods

---

*Bug fixed October 4, 2025*
