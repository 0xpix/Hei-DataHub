# Changelog - v0.50-beta

## Version 0.50.0-beta (2025-10-04)
**Codename:** Clean Architecture

### 🎉 Major Changes

#### Complete Migration to Clean Architecture
- **Migrated to `src/` layout** - All code now lives in `src/mini_datahub/`
- **Layered architecture** - Separated concerns into core, infra, services, ui, cli, app
- **Fixed all migration bugs** - Database initialization, dataset loading, pull functionality
- **Both commands available** - `hei-datahub` and `mini-datahub` work identically

#### Enhanced Version System
- **New `version.py` module** - Centralized version management with rich metadata
- **Detailed version info** - New `--version-info` flag shows system details
- **Build metadata** - Includes build number, release date, and codename
- **Version utilities** - Helper functions for version checking and display

### ✨ New Features

1. **Dual Command Support**
   - `hei-datahub` - Primary command name
   - `mini-datahub` - Alternative command (backward compatible)
   - Both point to the same application

2. **Enhanced CLI**
   - `--version` - Shows clean version string: `Hei-DataHub 0.50.0-beta`
   - `--version-info` - Shows detailed system and build information
   - Better error messages and help text

3. **Improved Version Module**
   - `get_version_string()` - Formatted version with optional build number
   - `get_version_info()` - Comprehensive system information dictionary
   - `print_version_info()` - Pretty-printed version details
   - `get_banner()` - ASCII art application banner
   - `check_version_compatibility()` - Version requirement checking

4. **Convenience Scripts**
   - `hei-datahub.sh` - Wrapper script for easy execution
   - `scripts/cleanup_v050.sh` - Automated cleanup of old files

### 🐛 Bug Fixes

1. **Fixed missing `reindex_all()` function**
   - Added to `infra/index.py`
   - Pull functionality (U key) now works correctly
   - Refresh command works properly

2. **Fixed `list_all_datasets()` return type**
   - Now returns proper dict structure with id, name, snippet, rank
   - Resolved "string indices must be integers" error
   - Dataset loading works correctly on startup

3. **Fixed database initialization**
   - Database properly initializes on first run
   - Schema creation works reliably
   - FTS5 search index builds correctly

### 🗑️ Cleanup

Removed old files and directories:
- `mini_datahub_old/` - Old code backup (23 files)
- `sql/` - Old SQL directory (moved to `src/mini_datahub/infra/sql/`)
- `mini_datahub.egg-info/` - Old egg-info
- 15+ old migration documentation files
- Old test files (moved to `tests/`)
- Temporary backup archives

### 📦 Package Changes

- **Version**: `0.40.0` → `0.50.0-beta`
- **App Name**: `Mini Hei-DataHub` → `Hei-DataHub`
- **Structure**: Flat layout → src/ layout with clean architecture
- **Entry Points**: Added `hei-datahub` command alongside `mini-datahub`

### 📚 Documentation

New/Updated:
- `BUGFIX_MIGRATION_ERRORS.md` - Documents all migration bug fixes
- `COMMAND_SETUP.md` - Complete guide for running without `uv run`
- `scripts/cleanup_v050.sh` - Automated cleanup script with instructions
- `src/mini_datahub/version.py` - Comprehensive version module with examples

### 🔧 Technical Improvements

1. **Import Structure**
   - All version info imported from `mini_datahub.version`
   - Cleaner `__init__.py` with minimal re-exports
   - Better separation of concerns

2. **CLI Architecture**
   - Imports moved to lazy loading where appropriate
   - Better error handling and user feedback
   - Support for new version flags

3. **Code Organization**
   ```
   src/mini_datahub/
   ├── __init__.py          # Package entry point
   ├── version.py           # Version metadata and utilities
   ├── core/                # Pure domain logic
   ├── infra/               # I/O adapters (db, git, github, store)
   ├── services/            # Business logic orchestration
   ├── ui/                  # Textual TUI (views, widgets)
   ├── cli/                 # Command-line interface
   ├── app/                 # Application layer (settings, runtime)
   └── utils/               # Utilities
   ```

### ⚡ Performance

- No performance regression from migration
- Database queries remain fast with FTS5
- TUI startup time unchanged

### 🧪 Testing

All functionality verified:
- ✅ `hei-datahub --version`
- ✅ `hei-datahub --version-info`
- ✅ `hei-datahub reindex`
- ✅ `hei-datahub` (TUI launch)
- ✅ Dataset loading and display
- ✅ Pull updates (U key)
- ✅ Refresh (R key)
- ✅ Search functionality
- ✅ All TUI navigation

### 🔄 Migration Path

From v0.40.0 to v0.50.0-beta:
1. Pull latest code
2. Run: `uv sync --reinstall-package mini-datahub`
3. Run: `bash scripts/cleanup_v050.sh`
4. Test: `hei-datahub --version-info`
5. Launch: `hei-datahub`

### 📋 Breaking Changes

1. **Package structure changed** - Code moved from root to `src/`
2. **Import paths updated** - All imports use new structure
3. **Version string format** - Changed from `v0.40-beta` to `0.50.0-beta`
4. **App name simplified** - `Mini Hei-DataHub` → `Hei-DataHub`

### 🚀 Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Check version
hei-datahub --version-info

# Launch TUI
hei-datahub

# Or use make
make run
```

### 🔮 What's Next

Future versions will focus on:
- Additional TUI features
- Enhanced PR workflow
- Auto-sync improvements
- Plugin system
- Advanced search features

---

## Previous Versions

### v0.40.0 (2025-10-04)
- Initial clean architecture migration
- Migrated 13 files to new structure
- Updated 50+ import statements
- Version 0.40.0 active

### Earlier Versions
See `CHANGELOG.md` for complete history.
