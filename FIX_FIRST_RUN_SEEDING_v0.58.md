# First-Run Dataset Seeding Fix (v0.58.0-beta)

## Issues

### Issue 1: Datasets Not Copied on First Run
When installing Hei-DataHub via `uv tool install`, the TUI showed **no datasets** despite the data being packaged correctly. The `hei-datahub paths` diagnostic showed `Datasets: 0`.

**Root Cause:** The `initialize_workspace()` function was only being called in `handle_tui()`, not when running other commands like `hei-datahub paths` or `hei-datahub reindex`.

### Issue 2: Wrong Environment Detection When Running from Repo
When running the installed `hei-datahub` command from within the repository directory, it would show "⚠ Fallback mode" and fail to find datasets.

**Root Cause:** The `_is_dev_mode()` function checked `Path.cwd()` (current working directory) instead of `Path(__file__)` (where the code is actually located). This caused the installed package to be incorrectly detected as "dev mode" when run from the repo directory.

## Solutions

### Fix 1: Global Workspace Initialization
**Moved `initialize_workspace()` call to run BEFORE any command is processed** in the `main()` function. This ensures that on first run:

1. **Any command** triggers initialization
2. Datasets are copied from package to `~/.local/share/hei-datahub/datasets/`
3. Schema and templates are also copied
4. Subsequent commands find the data ready to use

### Fix 2: Use `__file__` for Environment Detection
**Changed `_is_dev_mode()` and dev path resolution to use `Path(__file__)` instead of `Path.cwd()`**. This ensures correct environment detection regardless of where the command is run from.

## Changes Made

### `src/mini_datahub/cli/main.py`
```python
def main():
    # ... argument parsing ...

    args = parser.parse_args()

    # Handle --version-info flag
    if hasattr(args, 'version_info') and args.version_info:
        print_version_info(verbose=True)
        sys.exit(0)

    # ✨ NEW: Initialize workspace on first run (creates dirs, copies packaged datasets)
    # This happens BEFORE any command to ensure data is always available
    from mini_datahub.infra.paths import initialize_workspace
    initialize_workspace()

    # ... rest of command handling ...
```

Also removed redundant call from `handle_tui()` since it now happens globally.

### `src/mini_datahub/infra/paths.py`

**Before (broken):**
```python
def _is_dev_mode() -> bool:
    """Check if running from repository (development mode)."""
    cwd = Path.cwd()  # ← WRONG: Uses current working directory
    return (cwd / "src" / "mini_datahub").exists() and (cwd / "pyproject.toml").exists()

# ...

elif _is_dev_mode():
    PROJECT_ROOT = Path.cwd()  # ← WRONG: Uses cwd
```

**After (fixed):**
```python
def _is_dev_mode() -> bool:
    """Check if running from repository (development mode)."""
    package_path = Path(__file__).resolve()  # ← CORRECT: Uses package location
    # Go up 4 levels: infra -> mini_datahub -> src -> repo_root
    potential_repo = package_path.parent.parent.parent.parent
    return (
        (potential_repo / "src" / "mini_datahub").exists() and
        (potential_repo / "pyproject.toml").exists() and
        "site-packages" not in str(package_path)  # ← Extra check
    )

# ...

elif _is_dev_mode():
    package_path = Path(__file__).resolve()
    PROJECT_ROOT = package_path.parent.parent.parent.parent  # ← CORRECT: Derived from __file__
```

**Why this matters:**
- **Old behavior:** If you `cd` into the repo and run installed `hei-datahub`, it would see `cwd` has `src/mini_datahub` and think it's dev mode
- **New behavior:** Uses where the **code is actually located** (`__file__`), not where you're running from (`cwd`)
- **Result:** Installed package always detected correctly, even when run from repo directory

## Verification Steps

### 1. Clean Installation Test
```bash
# Remove existing installation
uv tool uninstall hei-datahub
rm -rf ~/.local/share/hei-datahub ~/.config/hei-datahub ~/.cache/hei-datahub

# Fresh install
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=hei-datahub"

# Verify paths (triggers first-run initialization)
hei-datahub paths
# Should show: "Datasets: 4" and "✓ Initialized 4 datasets..."
```

### 2. Expected Output on First Run
```
✓ Initialized schema at /home/user/.local/share/hei-datahub/schema.json
✓ Initialized 4 datasets in /home/user/.local/share/hei-datahub/datasets
  Indexing datasets...
  ✓ Indexed 4 datasets
✓ Initialized templates in /home/user/.local/share/hei-datahub/assets
```

### 3. Verify Datasets Appear in TUI
```bash
# Launch TUI
hei-datahub

# Should show all 4 datasets:
# - burned-area
# - land-cover
# - precipitation
# - testing-the-beta-version
```

### 4. Verify Database Contents
```bash
sqlite3 ~/.local/share/hei-datahub/db.sqlite "SELECT COUNT(*) FROM datasets_store;"
# Should output: 4
```

## What Gets Packaged and Copied

### Package Contents (in UV installation)
Located at: `~/.local/share/uv/tools/hei-datahub/lib/python3.13/site-packages/mini_datahub/`

```
mini_datahub/
├── data/                  # ← Packaged datasets
│   ├── burned-area/
│   │   └── metadata.yaml
│   ├── land-cover/
│   │   └── metadata.yaml
│   ├── precipitation/
│   │   └── metadata.yaml
│   └── testing-the-beta-version/
│       └── metadata.yaml
├── schema.json            # ← Database schema
└── templates/             # ← Optional templates
```

### User Data Directory (after first run)
Located at: `~/.local/share/hei-datahub/`

```
~/.local/share/hei-datahub/
├── datasets/              # ← Copied on first run
│   ├── burned-area/
│   ├── land-cover/
│   ├── precipitation/
│   └── testing-the-beta-version/
├── db.sqlite              # ← Created by ensure_database()
├── schema.json            # ← Copied on first run
└── assets/
    └── templates/         # ← Copied on first run
```

## Key Behaviors

### First Run (Empty Datasets Directory)
1. `initialize_workspace()` detects empty `~/.local/share/hei-datahub/datasets/`
2. Copies all datasets from package `data/` to user directory
3. Calls `DatasetStore().reindex()` to populate database
4. Prints success message

### Subsequent Runs (Datasets Already Exist)
1. `initialize_workspace()` detects existing datasets
2. **Skips copying** (idempotent behavior)
3. No output (silent success)
4. Continues with command

### Development Mode
1. `_is_installed_package()` returns `False` (not in site-packages or uv paths)
2. `initialize_workspace()` only ensures directories exist
3. **Does NOT copy datasets** (uses repo `data/` directly)

## Testing Checklist

- [x] Fresh install shows "✓ Initialized 4 datasets"
- [x] `hei-datahub paths` shows "Datasets: 4"
- [x] `hei-datahub reindex` finds and indexes all datasets
- [x] TUI displays all 4 datasets on launch
- [x] Database contains 4 rows in `datasets_store`
- [x] Second run doesn't re-copy datasets (idempotent)
- [x] Development mode still works correctly (uses repo data/)
- [x] **Running installed package from repo directory works** (shows "Installed package" not "Fallback mode")
- [x] Uninstall/reinstall preserves user data and datasets remain accessible

## Related Files
- `src/mini_datahub/cli/main.py` - Added global initialization
- `src/mini_datahub/infra/paths.py` - Fixed environment detection and initialization logic
- `MANIFEST.in` - Ensures data files are packaged
- `pyproject.toml` - Package data configuration

## Commits
- `9ae48d5` - fix: Call initialize_workspace() before all commands to ensure first-run dataset seeding
- `b019e27` - chore: Remove debug output from initialize_workspace()
- `9ed6587` - fix: Use __file__ instead of cwd() for environment detection
