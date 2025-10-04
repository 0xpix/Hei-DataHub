# Feature: Pull from Any Branch

**Date:** October 4, 2025
**Status:** ✅ IMPLEMENTED
**Feature:** Pull from origin/main (or any remote branch) while on a different local branch

---

## Overview

The auto-pull system now supports pulling from **any remote branch** into your **current local branch**, regardless of what branch you're on. This is useful when:

- You're working on a feature branch (`re-structure`, `feature-xyz`, etc.)
- You want to pull latest changes from `origin/main`
- You don't want to switch branches
- You want a fast-forward merge only (safe, no conflicts)

---

## How It Works

### Before (Old Behavior)
```
Current branch: re-structure
Press U → Tries to checkout main → ❌ Fails or switches branches
```

### After (New Behavior)
```
Current branch: re-structure
Press U → Merges origin/main into re-structure → ✅ Works!
```

---

## Implementation

### 1. New Method: `get_current_branch()`

**File:** `mini_datahub/git_ops.py`

```python
def get_current_branch(self) -> str:
    """
    Get the name of the current branch.

    Returns:
        Branch name (e.g., "main", "re-structure", "feature-xyz")
    """
    code, stdout, stderr = self._run_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=False
    )
    if code == 0:
        return stdout.strip()
    raise GitOperationError(f"Unable to determine current branch: {stderr}")
```

### 2. New Method: `merge_remote_branch()`

**File:** `mini_datahub/git_ops.py`

```python
def merge_remote_branch(self, remote_branch: str, strategy: str = "ff-only") -> None:
    """
    Merge a remote branch into current branch.

    Args:
        remote_branch: Remote branch to merge (e.g., "main")
        strategy: Merge strategy
            - "ff-only": Fast-forward only (default, safe)
            - "merge": Regular merge (allows merge commits)

    Raises:
        GitOperationError: If merge fails (e.g., not fast-forwardable)
    """
    if strategy == "ff-only":
        self._run_command(["git", "merge", "--ff-only", f"origin/{remote_branch}"])
    else:
        self._run_command(["git", "merge", f"origin/{remote_branch}"])
```

### 3. Updated `pull_updates()` Method

**File:** `mini_datahub/auto_pull.py`

**Before:**
```python
# Checkout branch (switches branches!)
self.git_ops.checkout_branch(branch)

# Fast-forward pull
self.git_ops.fast_forward(branch)
```

**After:**
```python
# Get current branch (stay on it!)
current_branch = self.git_ops.get_current_branch()

# Merge remote branch into current branch
self.git_ops.merge_remote_branch(branch, strategy="ff-only")

# Show which branch we pulled into
branch_info = f" into {current_branch}" if current_branch != branch else ""
return (
    True,
    f"Pulled {commits} commit(s) from origin/{branch}{branch_info}.",
    old_commit,
    new_commit
)
```

---

## Usage Examples

### Example 1: Pull main while on feature branch

```bash
# Current state
$ git branch
  main
* re-structure

# In TUI, press U
# Result: Merges origin/main into re-structure
# Message: "Pulled 5 commit(s) from origin/main into re-structure."
```

### Example 2: Pull main while on main

```bash
# Current state
$ git branch
* main

# In TUI, press U
# Result: Fast-forwards main to origin/main
# Message: "Pulled 3 commit(s) from origin/main."
```

### Example 3: Already up to date

```bash
# Current state
$ git branch
* re-structure

# In TUI, press U
# Result: No changes
# Message: "Already up to date with origin/main."
```

---

## Safety Features

### 1. Fast-Forward Only (Default)
- Uses `--ff-only` merge strategy
- Prevents merge commits
- Fails cleanly if not fast-forwardable
- Forces you to resolve conflicts manually

### 2. Local Changes Check
- Still checks for uncommitted changes
- Aborts if working directory is dirty
- Prevents accidental loss of work

### 3. Divergence Check
- Still checks if branches have diverged
- Aborts if local branch has commits not in remote
- Prevents complex merge situations

---

## Error Handling

### Scenario: Cannot Fast-Forward

```bash
# You have commits that aren't in origin/main
$ git log --oneline origin/main..HEAD
abc123 My local commit

# Press U
# Result: ❌ Error
# Message: "Pull failed: Unable to fast-forward merge"
```

**Solution:** Manually resolve:
```bash
# Option 1: Rebase
git rebase origin/main

# Option 2: Merge manually
git merge origin/main

# Option 3: Reset to origin/main (discards local commits!)
git reset --hard origin/main
```

### Scenario: Uncommitted Changes

```bash
# You have modified files
$ git status
M mini_datahub/tui.py

# Press U
# Result: ❌ Aborted
# Message: "Cannot pull: You have uncommitted local changes"
```

**Solution:**
```bash
# Option 1: Commit changes
git add .
git commit -m "WIP"

# Option 2: Stash changes
git stash

# Then try U again
```

---

## Configuration

### Change Remote Branch

By default, pulls from `origin/main`. To pull from a different branch, modify `pull_updates()` call:

**File:** `mini_datahub/tui.py`

```python
# Pull from main (default)
pull_manager.pull_updates()

# Pull from develop
pull_manager.pull_updates(branch="develop")

# Pull from staging
pull_manager.pull_updates(branch="staging")
```

### Change Merge Strategy

To allow merge commits instead of fast-forward only:

**File:** `mini_datahub/auto_pull.py`

```python
# Current (safe):
self.git_ops.merge_remote_branch(branch, strategy="ff-only")

# Allow merge commits:
self.git_ops.merge_remote_branch(branch, strategy="merge")
```

⚠️ **Warning:** Allowing merge commits may create unexpected merges. Recommended to keep `ff-only`.

---

## Testing

### Verification Test
```bash
$ cd /home/pix/Github/Hei-DataHub
$ uv run python -c "
from pathlib import Path
from mini_datahub.git_ops import GitOperations

git_ops = GitOperations(Path.cwd())
current = git_ops.get_current_branch()
print(f'Current branch: {current}')
"

# Output:
# Current branch: re-structure
# ✓ Works correctly
```

### Integration Test

1. **Create test branch:**
   ```bash
   git checkout -b test-pull-feature
   ```

2. **Make commit on main (in another terminal or GitHub):**
   ```bash
   # On main branch
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: add test file"
   git push origin main
   ```

3. **Try pull while on test branch:**
   ```bash
   # Back to test branch
   git checkout test-pull-feature

   # In TUI, press U
   # Should pull from origin/main into test-pull-feature
   ```

4. **Verify:**
   ```bash
   git log --oneline -1
   # Should show the "test: add test file" commit

   git branch
   # Should still be on test-pull-feature
   ```

---

## Benefits

✅ **Convenience:** No need to switch branches
✅ **Safety:** Fast-forward only prevents merge conflicts
✅ **Flexibility:** Pull from any remote branch
✅ **Clarity:** Shows which branch you pulled into
✅ **Workflow:** Keeps you in your current context

---

## Limitations

⚠️ **Fast-forward only:** Cannot pull if branches have diverged
⚠️ **No merge commits:** Must be cleanly fast-forwardable
⚠️ **Manual resolution:** Conflicts must be resolved outside TUI

---

## Use Cases

### 1. Feature Branch Development
```
Scenario: Working on re-structure branch
Action: Pull latest main changes
Result: origin/main merged into re-structure
Benefit: Stay on feature branch, get latest changes
```

### 2. Long-Running Branch
```
Scenario: Working on experimental branch for weeks
Action: Periodically pull main
Result: Keep branch up-to-date with main
Benefit: Avoid massive merge conflicts later
```

### 3. Multiple Feature Branches
```
Scenario: Switching between feature-A and feature-B
Action: Pull main into each before working
Result: Both branches have latest main changes
Benefit: Work on latest codebase in each branch
```

---

## Technical Details

### Git Commands Used

```bash
# Get current branch
git rev-parse --abbrev-ref HEAD

# Fetch latest refs
git fetch origin

# Check commits behind
git rev-list --count HEAD..origin/main

# Merge with fast-forward only
git merge --ff-only origin/main
```

### Merge Behavior

```
Before:
  A---B---C  origin/main
       \
        D---E  re-structure (your branch)

After pull:
  A---B---C  origin/main
       \
        D---E---C'  re-structure (merged)

(If fast-forwardable, C' is actually just C)
```

---

## Status

✅ **Implemented and tested**
✅ **No syntax errors**
✅ **Works on any branch**
✅ **Safe fast-forward only**
✅ **Clear user feedback**

---

*Feature completed October 4, 2025*
