# 🎯 FINAL FIX: UV Install Always Uses ~/.hei-datahub/

## Complete Solution

I've fixed **both** issues:

### Issue 1: Only 1 Template Dataset (FIXED ✅)
- **Problem:** Only `templates/data/` was packaged (1 dataset)
- **Solution:** Now packaging `src/mini_datahub/data/` with all 4 real datasets
- **Files Changed:** MANIFEST.in, pyproject.toml, paths.py

### Issue 2: Had to cd /tmp to See Data (FIXED ✅)
- **Problem:** Running from repo used repo's data, not ~/.hei-datahub/
- **Solution:** UV installs NOW ALWAYS use ~/.hei-datahub/ regardless of CWD
- **Detection:** Checks if `__file__` contains "site-packages" or ".local/share/uv"

## New Workspace Detection Logic

```python
def _get_workspace_root() -> Path:
    # 1. If installed via UV/pip → ALWAYS ~/.hei-datahub/
    if is_installed:
        return Path.home() / ".hei-datahub"

    # 2. Environment variable override
    if HEI_DATAHUB_WORKSPACE:
        return env_workspace

    # 3. Development mode (repo with src/)
    if is_dev_mode:
        return repo_root

    # 4. Custom workspace (CWD with data/)
    if (cwd / "data").exists():
        return cwd

    # 5. Default fallback
    return Path.home() / ".hei-datahub"
```

## What Changed

**Commit 1:** Package all 4 real datasets
- Added `src/mini_datahub/data/` with burned-area, land-cover, precipitation, testing-the-beta-version
- Updated MANIFEST.in to include data/
- Updated pyproject.toml package-data
- Changed initialize_workspace() to copy from data/ not templates/

**Commit 2:** UV installs always use ~/.hei-datahub/
- Added installed package detection
- UV users now get consistent behavior regardless of CWD
- Dev mode still works from repo

## Testing Instructions

### Step 1: Reinstall from GitHub

```bash
# Uninstall current version
uv tool uninstall hei-datahub

# Clean workspace
rm -rf ~/.hei-datahub

# Install updated version from your branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

### Step 2: Test from Repo Directory (No More cd /tmp Needed!)

```bash
# Run from your repo directory
cd /home/pix/Github/Hei-DataHub
hei-datahub
```

**Expected Result:**
- Opens TUI with **4 datasets**:
  - burned-area
  - land-cover
  - precipitation
  - testing-the-beta-version
- Uses `~/.hei-datahub/` workspace (NOT repo's data/)

### Step 3: Verify Workspace Location

```bash
ls ~/.hei-datahub/data/
# Should show all 4 datasets

find ~/.hei-datahub/data/ -name "metadata.yaml" | wc -l
# Should show: 4
```

### Step 4: Verify Database

```bash
# Check database has all datasets indexed
sqlite3 ~/.hei-datahub/db.sqlite "SELECT id FROM datasets_store;"
# Should show all 4 dataset IDs
```

## Before vs After

### Before ❌
```bash
cd /home/pix/Github/Hei-DataHub
hei-datahub
# Result: Shows repo data (might be different/incomplete)

cd /tmp
hei-datahub
# Result: Shows ~/.hei-datahub/ with 4 datasets
# Had to change directory!
```

### After ✅
```bash
cd /home/pix/Github/Hei-DataHub
hei-datahub
# Result: Shows ~/.hei-datahub/ with 4 datasets ✓

cd /tmp
hei-datahub
# Result: Shows ~/.hei-datahub/ with 4 datasets ✓

cd anywhere
hei-datahub
# Result: Shows ~/.hei-datahub/ with 4 datasets ✓
# ALWAYS THE SAME!
```

## Benefits

1. ✅ **Consistent behavior**: UV installs always use `~/.hei-datahub/`
2. ✅ **All 4 datasets**: burned-area, land-cover, precipitation, testing-the-beta-version
3. ✅ **No directory juggling**: Works from any directory
4. ✅ **Dev mode preserved**: Still works correctly for development
5. ✅ **User workspace supported**: Can still use custom workspaces

## What You Should See

After reinstalling and running `hei-datahub` from **anywhere**:

```
Hei-DataHub v0.58.0-beta

Datasets (4):
  □ burned-area
  □ land-cover
  □ precipitation
  □ testing-the-beta-version
```

## Troubleshooting

### If you still see old behavior:

1. **Check you reinstalled:**
   ```bash
   uv tool list | grep hei-datahub
   # Should show version 0.58.0-beta
   ```

2. **Check UV cache:**
   ```bash
   uv cache clean
   uv tool uninstall hei-datahub
   uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
   ```

3. **Verify installation path:**
   ```bash
   ~/.local/share/uv/tools/hei-datahub/bin/python -c "from mini_datahub.infra.paths import PROJECT_ROOT; print(PROJECT_ROOT)"
   # Should show: /home/pix/.hei-datahub (NOT the repo path!)
   ```

## Quick Test Command

```bash
# Complete fresh install and test
uv tool uninstall hei-datahub && \
rm -rf ~/.hei-datahub && \
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x" && \
cd /home/pix/Github/Hei-DataHub && \
hei-datahub
```

**Expected:** TUI opens with 4 datasets visible immediately!

---

**Status:** ✅ FIXED and pushed to GitHub
**Commits:** 77bf7ac (workspace detection) + 0f347d5 (package datasets)
**Next:** Reinstall and enjoy all 4 datasets from any directory! 🎉
