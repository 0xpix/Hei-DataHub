# Branch Divergence Explanation

**Date:** October 4, 2025
**Status:** ℹ️ INFORMATIONAL

---

## Situation

You're on `re-structure` branch and want to pull from `main`, but they've diverged:

### Main Branch
- Has 3 data files
- Latest commit: `8efbd6f` (28 min ago)
- Contains: `burned-area`, `example-weather`, `land-cover`

### Re-structure Branch
- Has 2 data files
- Latest commit: `a4dd66a` (your commit on top of 8efbd6f)
- Contains: `burned-area`, `land-cover`
- **Removed:** `example-weather` in commit a4dd66a

### Visual
```
main:          8efbd6f ← (has example-weather)
                  |
re-structure:  8efbd6f ← a4dd66a (removed example-weather)
```

---

## Why Pull Says "Already Up to Date"

Your `re-structure` branch contains **all commits from main** plus one additional commit. Git considers this "ahead" not "behind", so there's nothing to pull.

The fast-forward pull logic sees:
- `main` has 0 commits that `re-structure` doesn't have
- `re-structure` has 1 commit that `main` doesn't have
- Result: Already up to date (can't fast-forward)

---

## Solutions

### Option 1: Merge Main Into Re-structure (Allows Conflicts)

This would bring back `example-weather` and create a merge commit:

```bash
git checkout re-structure
git merge main
# This will either:
# - Fast-forward if possible, OR
# - Create a merge commit if there are conflicts
```

**Result:** Re-structure will have `example-weather` again

### Option 2: Reset Re-structure to Main (Loses Your Commit)

This throws away your deletion commit:

```bash
git checkout re-structure
git reset --hard main
# WARNING: This deletes commit a4dd66a!
```

**Result:** Re-structure becomes identical to main

### Option 3: Cherry-pick Files from Main

Bring specific files without merging:

```bash
git checkout re-structure
git checkout main -- data/example-weather/metadata.yaml
git commit -m "feat: re-add example-weather dataset"
```

**Result:** Re-structure gets `example-weather` back with a new commit

### Option 4: Rebase Re-structure on Main

Apply your changes on top of main's latest:

```bash
git checkout re-structure
git rebase main
# Since main is behind, this does nothing
```

**Result:** No change (main is already the base)

---

## What I Changed in the Code

I added support for pulling from **local branches** (not just remote):

```python
pull_manager.pull_updates(branch="main", from_remote=False)
# Pulls from LOCAL main

pull_manager.pull_updates(branch="main", from_remote=True)
# Pulls from origin/main (remote)
```

But this still uses **fast-forward only** by default, which won't work when branches have diverged.

---

## Recommendation

Since you mentioned "I have more data there" (on main), and that file is `example-weather`, you probably want **Option 3** (cherry-pick the file):

```bash
# On re-structure branch
git checkout main -- data/example-weather/metadata.yaml
git add data/example-weather/metadata.yaml
git commit -m "feat: restore example-weather dataset from main"
```

This gives you the file without losing your other changes.

---

## Future Enhancement

I could add a parameter to allow merge commits:

```python
pull_manager.pull_updates(
    branch="main",
    from_remote=False,
    allow_merge=True  # NEW: Allow merge commits
)
```

This would work even when branches diverge. Let me know if you want this!

---

*Analysis completed October 4, 2025*
