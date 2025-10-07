# 🔧 CRITICAL FIX: Data Paths for UV Installation

## 🎯 Problem Identified

**Issue:** When installed via UV, the app runs from UV's cache directory, not the repository root. Therefore:
- ❌ `data/` doesn't exist
- ❌ `schema.json` doesn't exist  
- ❌ `config/`, `assets/` etc. don't exist
- ✅ Only `infra/sql/` is packaged (inside the Python package)

## 🏗️ Architecture Understanding

Hei-DataHub is a **workspace-based application**. It expects to run in a directory with:
```
workspace/
├── data/                    # User's datasets
├── schema.json              # Metadata schema
├── .datahub_config.json     # Config
├── db.sqlite                # Index database
└── .cache/                  # Cache files
```

This is **by design** - it's a data catalog for managing local datasets.

## ✅ Solution Implemented

### 1. Smart Workspace Detection

Updated `src/mini_datahub/infra/paths.py`:

```python
def _get_workspace_root() -> Path:
    """Get the workspace root directory."""
    cwd = Path.cwd()
    
    # If CWD has data/ directory, use it (development mode)
    if (cwd / "data").exists() or (cwd / "pyproject.toml").exists():
        return cwd
    
    # Otherwise use user's home directory workspace
    home_workspace = Path.home() / ".hei-datahub"
    home_workspace.mkdir(parents=True, exist_ok=True)
    return home_workspace
```

**Behavior:**
- **Dev mode:** Run from repo → uses repo's `data/`
- **UV install:** Run from anywhere → uses `~/.hei-datahub/`

### 2. Package Schema and Templates

**Added to package:**
- `src/mini_datahub/schema.json` - Metadata schema
- `src/mini_datahub/templates/data/` - Sample dataset

**Updated `MANIFEST.in`:**
```
include src/mini_datahub/schema.json
recursive-include src/mini_datahub/templates *
```

**Updated `pyproject.toml`:**
```toml
[tool.setuptools.package-data]
mini_datahub = [
    "infra/sql/*.sql",
    "schema.json",
    "templates/**/*"
]
```

### 3. Auto-Initialize Workspace

Added `initialize_workspace()` function that:
1. Creates required directories
2. Copies `schema.json` from package if missing
3. Copies sample data if `data/` is empty

Called on every TUI launch (fast if already initialized).

---

## 🧪 Testing

### Test 1: Fresh UV Install

```bash
# Clean slate
uv tool uninstall hei-datahub

# Install from feature branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# Run it
hei-datahub
```

**Expected:**
1. Creates `~/.hei-datahub/`
2. Copies `schema.json` there
3. Creates `~/.hei-datahub/data/` with sample dataset
4. Shows sample dataset in TUI

### Test 2: Run in Existing Workspace

```bash
# Create workspace
mkdir ~/my-data-catalog
cd ~/my-data-catalog

# Create data directory
mkdir data

# Run hei-datahub
hei-datahub
```

**Expected:**
- Uses `~/my-data-catalog/` as workspace
- Creates files there (not in ~/.hei-datahub/)

### Test 3: Development Mode

```bash
# From repository
cd /path/to/Hei-DataHub
source .venv/bin/activate
hei-datahub
```

**Expected:**
- Uses repository's `data/` directory
- Uses repository's `schema.json`

---

## 📁 File Locations After Install

### Development (from repo):
```
/path/to/Hei-DataHub/
├── data/                    # ← Used
├── schema.json              # ← Used
├── db.sqlite                # ← Created here
└── .cache/                  # ← Created here
```

### UV Install (from anywhere):
```
~/.hei-datahub/
├── data/                    # ← Auto-created with sample
│   └── testing-the-beta-version/
├── schema.json              # ← Copied from package
├── db.sqlite                # ← Created here
└── .cache/                  # ← Created here
```

### UV Install (from existing workspace):
```
~/my-workspace/
├── data/                    # ← Your datasets
│   ├── dataset1/
│   └── dataset2/
├── schema.json              # ← Copied if missing
├── db.sqlite                # ← Created here
└── .cache/                  # ← Created here
```

---

## 🎯 User Workflows

### Workflow 1: Quick Start (Empty Data)

```bash
# Install
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git"

# Run
hei-datahub
```

**Result:** 
- Workspace at `~/.hei-datahub/`
- Sample dataset available
- Ready to add more datasets

### Workflow 2: Use Existing Data Directory

```bash
# Go to your data directory
cd ~/my-existing-data

# Ensure it has data/ subdirectory
mkdir -p data

# Run hei-datahub
hei-datahub
```

**Result:**
- Uses `~/my-existing-data/` as workspace
- Manages datasets in `~/my-existing-data/data/`

### Workflow 3: Collaborative Team Use

```bash
# Clone team's data catalog
git clone git@github.com:team/data-catalog.git
cd data-catalog

# Install hei-datahub globally
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git"

# Run from catalog directory
hei-datahub
```

**Result:**
- Uses `data-catalog/` as workspace
- Team shares `data/` via Git
- Each member indexes locally

---

## 🔍 Troubleshooting

### "No datasets found"

**Check workspace location:**
```bash
hei-datahub
# Look at the logs or add debug info
```

**Solution 1:** Run from a directory with `data/`
```bash
mkdir -p ~/my-catalog/data
cd ~/my-catalog
hei-datahub
```

**Solution 2:** Use default workspace
```bash
cd ~/.hei-datahub
ls data/  # Should show sample dataset
```

### "schema.json not found"

**Should auto-fix on launch**, but manual fix:
```bash
cd ~/.hei-datahub
# Schema will be created automatically on next run
hei-datahub
```

### Want to use different workspace

**Option 1:** Change directory
```bash
cd /path/to/my/workspace
hei-datahub
```

**Option 2:** Set environment variable (future enhancement)
```bash
export HEI_DATAHUB_WORKSPACE=/path/to/workspace
hei-datahub
```

---

## 📝 Files Changed

### Modified:
1. `src/mini_datahub/infra/paths.py`
   - Added `_get_workspace_root()` for smart detection
   - Added `_get_schema_path()` for schema fallback
   - Added `initialize_workspace()` for auto-setup

2. `src/mini_datahub/cli/main.py`
   - Changed `ensure_directories()` → `initialize_workspace()`

3. `MANIFEST.in`
   - Simplified, only include what's needed
   - Added `schema.json`
   - Added `templates/`

4. `pyproject.toml`
   - Simplified `package-data`
   - Only include packaged files

### Added:
1. `src/mini_datahub/schema.json` - Copied from root
2. `src/mini_datahub/templates/data/testing-the-beta-version/` - Sample data

---

## ✅ Verification

After rebuild and install:

```bash
# Reinstall
uv tool uninstall hei-datahub
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# Should show workspace info
hei-datahub --version

# Should work with sample data
hei-datahub
# Look for "testing-the-beta-version" dataset
```

---

## 🎉 Benefits

1. ✅ **Works from UV install** - No repository needed
2. ✅ **Smart workspace detection** - Uses CWD or ~/.hei-datahub/
3. ✅ **Auto-initialization** - Sets up on first run
4. ✅ **Sample data included** - Users see something immediately
5. ✅ **Backward compatible** - Dev mode still works
6. ✅ **Team-friendly** - Can run from shared Git repos

---

**Status:** ✅ FIXED - Ready to test!
