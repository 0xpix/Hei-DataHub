# ✅ Workspace Detection Fix - Testing Guide

## What Was Fixed

The app was showing empty because workspace detection was using the repository's `data/` directory instead of the packaged template data in `~/.hei-datahub/`.

### Root Cause
```python
# OLD BUGGY CODE (line 15)
if (cwd / "data").exists() or (cwd / "pyproject.toml").exists():
    return cwd  # ← Always preferred repo data
```

When you ran the app from the repository directory, it found `pyproject.toml` and used the repo root, which meant:
- Using `data/` outside `src/` (the old repo data)
- **Not** using `~/.hei-datahub/data/` with packaged template
- Template initialization never ran because repo's `data/` wasn't empty

### The Fix

Rewrote workspace detection with **smart development mode detection**:

```python
# NEW FIXED CODE
is_dev_mode = (cwd / "src" / "mini_datahub").exists() and (cwd / "pyproject.toml").exists()

# Priority:
1. Environment variable: HEI_DATAHUB_WORKSPACE
2. Dev mode: CWD with src/mini_datahub/ AND data/
3. Custom workspace: CWD with data/ (but not dev mode)
4. Default: ~/.hei-datahub/
```

Also fixed template path resolution (was looking in `infra/templates/` instead of `mini_datahub/templates/`).

---

## Testing Instructions

### Test 1: Fresh Install (Most Important!)

This simulates a real user installing from UV.

```bash
# 1. Clean slate
rm -rf ~/.hei-datahub
uv tool uninstall hei-datahub

# 2. Reinstall from your feature branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# 3. Run from ANY directory (not the repo!)
cd /tmp
hei-datahub
```

**✅ Expected Results:**
- App launches successfully
- Shows **1 dataset**: "testing-the-beta-version"
- Workspace created at `~/.hei-datahub/`
- Files created:
  - `~/.hei-datahub/data/testing-the-beta-version/metadata.yaml`
  - `~/.hei-datahub/db.sqlite` (contains indexed data)

**❌ If it fails:**
- Check: `ls -la ~/.hei-datahub/data/`
- Check database: `sqlite3 ~/.hei-datahub/db.sqlite "SELECT id FROM datasets_store;"`
- Share any error messages

---

### Test 2: Development Mode Still Works

This ensures we didn't break developer workflow.

```bash
# 1. Navigate to your repo
cd /home/pix/Github/Hei-DataHub

# 2. Run in dev mode (not from UV)
python -m mini_datahub
```

**✅ Expected Results:**
- Uses repo's `data/` directory (your original datasets)
- Uses repo's `schema.json`
- Database at `/home/pix/Github/Hei-DataHub/db.sqlite`

---

### Test 3: Custom Workspace

This tests running from a different project directory.

```bash
# 1. Create a custom workspace
mkdir -p ~/my-test-catalog/data
cd ~/my-test-catalog

# 2. Run hei-datahub from there
hei-datahub
```

**✅ Expected Results:**
- Uses `~/my-test-catalog/` as workspace
- Creates files there (not in repo or ~/.hei-datahub/)
- Empty data directory (no sample data since we created our own)

---

### Test 4: Environment Variable Override

```bash
# 1. Set custom workspace location
export HEI_DATAHUB_WORKSPACE=/tmp/test-workspace

# 2. Run from anywhere
cd ~
hei-datahub
```

**✅ Expected Results:**
- Uses `/tmp/test-workspace/` as workspace
- Creates `data/` there with sample dataset
- Ignores `~/.hei-datahub/`

---

## Verification Commands

After Test 1 (the most important one):

```bash
# Check workspace was created
ls -la ~/.hei-datahub/

# Check data directory
ls -la ~/.hei-datahub/data/
# Should show: testing-the-beta-version/

# Check sample dataset
cat ~/.hei-datahub/data/testing-the-beta-version/metadata.yaml
# Should show YAML metadata

# Check database
sqlite3 ~/.hei-datahub/db.sqlite "SELECT id FROM datasets_store;"
# Should show: testing-the-beta-version

# Check workspace detection (debug)
cd /tmp
python -c "import sys; sys.path.insert(0, '/home/pix/.local/bin'); \
from mini_datahub.infra.paths import PROJECT_ROOT; \
print('Workspace:', PROJECT_ROOT)"
# Should show: /home/pix/.hei-datahub
```

---

## What Changed (Files)

### Modified:
1. **src/mini_datahub/infra/paths.py** (CRITICAL)
   - `_get_workspace_root()`: Rewrote with dev mode detection
   - `initialize_workspace()`: Fixed template path resolution

2. **MANIFEST.in**
   - Removed `src/mini_datahub/data` (doesn't exist)

3. **pyproject.toml**
   - Removed `data/**/*` from package-data

4. **DATA_PATHS_FIX_v0.58.md**
   - Updated with whitespace fixes

---

## Success Criteria

✅ **Test 1 passes**: UV install shows sample dataset
✅ **No errors** during initialization
✅ **Files created** in `~/.hei-datahub/`
✅ **Database indexed** with sample data
✅ **Dev mode** still works from repo

If all tests pass, the fix is complete and ready for PR! 🎉

---

## Commit Information

**Branch:** `chore/uv-install-data-desktop-v0.58.x`
**Commit:** `050564d` - "fix(install): correct workspace detection and template data paths for UV installs"
**Pushed:** Yes (already on GitHub)

**Next Steps:**
1. ✅ Test the UV install (Test 1 above)
2. If working: Create pull request to main
3. Merge and release v0.58.0-beta

---

## Quick Test (Copy-Paste Ready)

```bash
# Complete fresh test
rm -rf ~/.hei-datahub && \
uv tool uninstall hei-datahub && \
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x" && \
cd /tmp && \
hei-datahub
```

Expected: App opens with "testing-the-beta-version" dataset visible.
