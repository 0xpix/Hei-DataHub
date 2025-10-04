# Auto-Stash Feature Documentation

**Date:** October 4, 2025
**Status:** ✅ IMPLEMENTED
**Feature:** Automatic stash/unstash when pulling with uncommitted changes

---

## Overview

The auto-pull system now **automatically stashes uncommitted changes** before pulling and **restores them afterward**. This eliminates the "Cannot pull: You have uncommitted local changes" error.

### Before (Old Behavior)
```
You have uncommitted changes
Press U → ❌ Error: "Cannot pull: You have uncommitted local changes"
Manual fix needed: git stash → pull → git stash pop
```

### After (New Behavior)
```
You have uncommitted changes
Press U → ✅ Auto-stash → Pull → Auto-restore changes
Everything happens automatically!
```

---

## How It Works

### Workflow

1. **Press U to pull**
2. System detects uncommitted changes
3. **Automatically stashes** changes with message "Auto-stash before pull"
4. Pulls from origin/main (or specified branch)
5. **Automatically restores** stashed changes
6. You continue working with updated code + your changes

### Safety Features

✅ **Only stashes if pulling**
✅ **Automatic restore after successful pull**
✅ **Preserves changes on pull failure**
✅ **Clear error messages if restore fails**
✅ **Works with cross-branch pulling**

---

## Implementation

### 1. New Methods in `git_ops.py`

#### `stash_push()`
```python
def stash_push(self, message: str = "Auto-stash before pull") -> bool:
    """
    Stash uncommitted changes.

    Args:
        message: Stash description message

    Returns:
        True if changes were stashed, False if nothing to stash

    Raises:
        GitOperationError: If stash operation fails
    """
```

#### `stash_pop()`
```python
def stash_pop(self) -> bool:
    """
    Apply and remove most recent stash.

    Returns:
        True if stash was applied successfully, False if no stash to pop

    Raises:
        GitOperationError: If stash pop fails (e.g., conflicts)
    """
```

#### `has_stash()`
```python
def has_stash(self) -> bool:
    """
    Check if there are any stashes.

    Returns:
        True if stash list is not empty
    """
```

### 2. Updated `pull_updates()` in `auto_pull.py`

#### New Signature
```python
def pull_updates(
    self,
    branch: str = "main",
    auto_stash: bool = True  # NEW parameter
) -> Tuple[bool, str, Optional[str], Optional[str]]:
```

#### Stash Logic Flow
```python
# 1. Check for local changes
has_changes, status = self.has_local_changes()

# 2. If changes exist and auto_stash=True
if has_changes and auto_stash:
    # Stash changes
    stashed = self.git_ops.stash_push("Auto-stash before pull")

# 3. Perform pull
self.git_ops.merge_remote_branch(branch, strategy="ff-only")

# 4. Restore changes if stashed
if stashed:
    self.git_ops.stash_pop()
```

---

## Usage Examples

### Example 1: Pull with Uncommitted Changes

**Scenario:** You've been editing files and want to pull latest changes

```bash
# Your current state
$ git status
M mini_datahub/tui.py
M mini_datahub/config.py

# In TUI, press U
# Result: ✅ Success
# Message: "Pulled 3 commit(s) from origin/main. Your uncommitted changes have been restored."

# After pull
$ git status
M mini_datahub/tui.py      # ← Still there!
M mini_datahub/config.py   # ← Still there!
```

### Example 2: Pull on Different Branch with Changes

```bash
# Current state
$ git branch
* feature-xyz

$ git status
M some_file.py

# Press U in TUI
# Result: ✅ Success
# Message: "Pulled 2 commit(s) from origin/main into feature-xyz. Your uncommitted changes have been restored."
```

### Example 3: Pull with No Changes

```bash
# Current state
$ git status
nothing to commit, working tree clean

# Press U in TUI
# Result: ✅ Success (no stashing needed)
# Message: "Pulled 1 commit(s) from origin/main."
```

---

## Error Handling

### Scenario 1: Stash Conflicts on Restore

If the pulled changes conflict with your stashed changes:

```bash
# Press U
# Pull succeeds, but stash pop fails
# Message: "Pulled 5 commit(s) from origin/main.
#          ⚠️  Warning: Failed to restore stashed changes: merge conflict
#          Run 'git stash pop' manually to restore them."
```

**Resolution:**
```bash
# Check stash
git stash list
# stash@{0}: On re-structure: Auto-stash before pull

# Manually resolve
git stash pop
# Fix conflicts in files
git add <conflicted-files>
# Stash will be automatically dropped after resolution
```

### Scenario 2: Pull Fails

If the pull itself fails (e.g., cannot fast-forward):

```bash
# Press U
# Pull fails
# Message: "Pull failed: Unable to fast-forward merge
#          ⚠️  Your changes were stashed. Run 'git stash pop' to restore them."
```

**Resolution:**
```bash
# Restore your changes
git stash pop

# Then manually resolve pull issue
git pull --rebase origin main
# or
git merge origin/main
```

### Scenario 3: Stash Fails

If stashing fails (rare):

```bash
# Press U
# Message: "Failed to stash changes: <error>
#          Path: /path/to/repo"
```

**Resolution:**
```bash
# Manually stash or commit
git stash
# or
git add .
git commit -m "WIP"

# Then try pull again
```

---

## Configuration

### Enable/Disable Auto-Stash

By default, `auto_stash=True`. To disable:

**In TUI (future enhancement):**
- Settings → Auto-Pull → Disable Auto-Stash

**In code:**
```python
# With auto-stash (default)
pull_manager.pull_updates(branch="main")

# Without auto-stash (old behavior)
pull_manager.pull_updates(branch="main", auto_stash=False)
```

### Stash Message

The stash message is always: **"Auto-stash before pull"**

View stashes:
```bash
git stash list
# Output:
# stash@{0}: On re-structure: Auto-stash before pull
```

---

## Testing

### Manual Test: Stash Operations

```bash
# Create test changes
echo "test" >> test_file.txt

# Test stash
git stash push -m "Auto-stash before pull"
# Changes are stashed

# Verify
git status
# nothing to commit

# Restore
git stash pop
# Changes are back

# Verify
git status
# M test_file.txt
```

### Integration Test: Pull with Auto-Stash

```bash
# 1. Make local changes
echo "test" >> some_file.py

# 2. In TUI, press U
# Should see: "Your uncommitted changes have been restored"

# 3. Verify changes still exist
git status
# M some_file.py ← Still there!

# 4. Verify pull succeeded
git log -1
# Should show latest commit from origin/main
```

### Programmatic Test

```python
from pathlib import Path
from mini_datahub.git_ops import GitOperations

git_ops = GitOperations(Path.cwd())

# Test 1: Stash methods exist
assert hasattr(git_ops, 'stash_push')
assert hasattr(git_ops, 'stash_pop')
assert hasattr(git_ops, 'has_stash')

# Test 2: Check stash state
has_stash = git_ops.has_stash()
print(f'Has existing stashes: {has_stash}')

# Test 3: Test stash (if you have changes)
# stashed = git_ops.stash_push("Test stash")
# popped = git_ops.stash_pop()
```

---

## User Experience

### Message Examples

#### Success (No Changes)
```
Pulled 3 commit(s) from origin/main.
```

#### Success (With Auto-Stash)
```
Pulled 3 commit(s) from origin/main. Your uncommitted changes have been restored.
```

#### Success (Cross-Branch + Auto-Stash)
```
Pulled 2 commit(s) from origin/main into feature-xyz. Your uncommitted changes have been restored.
```

#### Warning (Restore Failed)
```
Pulled 5 commit(s) from origin/main.
⚠️  Warning: Failed to restore stashed changes: merge conflict
Run 'git stash pop' manually to restore them.
```

#### Error (Pull Failed)
```
Pull failed: Unable to fast-forward merge
⚠️  Your changes were stashed. Run 'git stash pop' to restore them.
```

---

## Benefits

✅ **No More Errors:** "Cannot pull" error is eliminated
✅ **Seamless Workflow:** Work → Pull → Continue
✅ **Safe:** Changes preserved even if pull fails
✅ **Automatic:** No manual git commands needed
✅ **Clear Feedback:** Know exactly what happened
✅ **Cross-Branch:** Works with cross-branch pulling

---

## Limitations

⚠️ **Stash Conflicts:** If pulled changes conflict with your changes, manual resolution needed
⚠️ **Untracked Files:** By default, untracked files are NOT stashed (can be enhanced)
⚠️ **Large Stashes:** Very large stashes may be slow

---

## Advanced Features (Future Enhancements)

### Include Untracked Files
```python
# Current: Only stashes tracked files
git stash push -m "message"

# Enhancement: Stash untracked files too
git stash push -u -m "message"
```

### Stash History UI
- Show list of all stashes in debug console
- Allow manual stash/pop/apply/drop
- View stash contents

### Smart Conflict Detection
- Pre-check if stash pop will conflict
- Offer to abort pull if conflicts likely
- Show diff preview before popping

---

## Git Commands Used

### Stash Push
```bash
git stash push -m "Auto-stash before pull"
```

### Stash Pop
```bash
git stash pop
```

### List Stashes
```bash
git stash list
```

### Check if Stash Exists
```bash
git stash list  # Check if output is non-empty
```

---

## Comparison with Other Approaches

### Approach 1: Manual Stash (Old)
```bash
git stash           # User does this
# Press U in TUI
git stash pop       # User does this
```
❌ Requires 3 steps
❌ User must remember

### Approach 2: Force Pull (Dangerous)
```bash
git reset --hard origin/main
```
❌ Loses uncommitted changes
❌ Destructive

### Approach 3: Auto-Stash (Our Solution)
```bash
# Press U in TUI → Everything automatic
```
✅ One step
✅ Safe
✅ Automatic

---

## Troubleshooting

### Problem: Stash pop fails with conflicts

**Solution:**
```bash
# 1. View stash
git stash show -p

# 2. Pop manually
git stash pop

# 3. Resolve conflicts
# Edit conflicted files
git add <files>

# Stash is automatically dropped after resolution
```

### Problem: Multiple stashes accumulate

**Check stashes:**
```bash
git stash list
# stash@{0}: On re-structure: Auto-stash before pull
# stash@{1}: On main: Auto-stash before pull
```

**Clean up:**
```bash
# Drop specific stash
git stash drop stash@{1}

# Clear all stashes (careful!)
git stash clear
```

### Problem: Want to disable auto-stash temporarily

**In code:**
```python
pull_manager.pull_updates(branch="main", auto_stash=False)
```

**Or commit changes:**
```bash
git add .
git commit -m "WIP: work in progress"
# Now pull will work without stashing
```

---

## Status

✅ **Implemented and tested**
✅ **No syntax errors**
✅ **Backward compatible**
✅ **Works with cross-branch pulling**
✅ **Clear user feedback**
✅ **Safe error handling**

---

## Summary

Auto-stash makes pulling **effortless and safe**. You never have to worry about uncommitted changes blocking a pull again. Just press **U** and everything is handled automatically.

**Key Message:** Work freely, pull anytime! 🎉

---

*Feature completed October 4, 2025*
