# 🚀 Release: Hei-DataHub v0.50.0-beta
**Codename:** Clean Architecture
**Release Date:** October 4, 2025

---

## 📋 Executive Summary

Version 0.50.0-beta represents a **major milestone** in the Hei-DataHub project. This release completes the migration to a clean, layered architecture with proper separation of concerns, fixes all migration-related bugs, introduces enhanced version management, and provides dual command support for maximum flexibility.

### Key Highlights

✅ **Complete clean architecture migration**
✅ **All migration bugs fixed** (database, loading, pull)
✅ **Enhanced version system** with detailed info
✅ **Dual command support** (`hei-datahub` + `mini-datahub`)
✅ **Comprehensive cleanup** (removed 40+ old files)
✅ **Production-ready** with full verification

---

## 🎯 What's New

### 1. Clean Architecture (Fully Implemented)

```
src/mini_datahub/
├── core/         # Pure domain logic (models, rules, errors)
├── infra/        # I/O adapters (db, git, github, store)
├── services/     # Business logic orchestration
├── ui/           # Textual TUI (views, widgets)
├── cli/          # Command-line interface
├── app/          # Application layer (settings, runtime)
└── utils/        # Shared utilities
```

**Benefits:**
- Clear separation of concerns
- Easier testing and maintenance
- Better code organization
- Scalable architecture

### 2. Enhanced Version Management

New `version.py` module with rich features:

```python
from mini_datahub.version import (
    __version__,              # "0.50.0-beta"
    get_version_info(),       # Dict with system info
    print_version_info(),     # Pretty print
    get_banner(),             # ASCII art banner
    check_version_compatibility(),  # Version checking
)
```

**CLI Commands:**
```bash
hei-datahub --version        # Quick version
hei-datahub --version-info   # Detailed system info
```

**Output Example:**
```
Hei-DataHub v0.50.0-beta
Codename: Clean Architecture
Released: 2025-10-04
Build: 005000

System Information:
  Python: 3.13.0 (CPython)
  Platform: Linux-6.16.10-arch1-1-x86_64-with-glibc2.42
  System: Linux (x86_64)

Repository: https://github.com/0xpix/Hei-DataHub
License: MIT
```

### 3. Dual Command Support

Choose your preferred command:

```bash
hei-datahub       # Primary command (shorter, cleaner)
mini-datahub      # Alternative (backward compatible)
```

Both commands are **identical** and work from:
- Virtual environment (after `source .venv/bin/activate`)
- Direct path (`./.venv/bin/hei-datahub`)
- Wrapper script (`./hei-datahub.sh`)
- Make commands (`make run`)

### 4. Bug Fixes

#### Fixed: Database Initialization Error
**Problem:** Missing `reindex_all()` function
**Impact:** Pull updates (U key) failed
**Solution:** Added complete function to `infra/index.py`

#### Fixed: Dataset Loading Error
**Problem:** `list_all_datasets()` returned wrong structure
**Error:** "string indices must be integers, not 'str'"
**Solution:** Updated to return proper dict with id, name, snippet, rank

#### Fixed: Import Errors
**Problem:** Various import path issues from migration
**Solution:** Updated all imports to new structure

### 5. Comprehensive Cleanup

**Removed:**
- `mini_datahub_old/` (23 files)
- 15+ old migration docs
- Old test files
- Temporary backups
- Obsolete egg-info

**Result:** Cleaner repository, faster navigation, easier maintenance

---

## 📦 Installation & Upgrade

### New Installation

```bash
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub
uv sync
source .venv/bin/activate
hei-datahub --version-info
```

### Upgrade from v0.40.0

```bash
cd Hei-DataHub
git pull
uv sync --reinstall-package mini-datahub
bash scripts/cleanup_v050.sh
hei-datahub --version-info
```

---

## 🎮 Usage

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Launch TUI
hei-datahub

# Or use make
make run
```

### All Commands

```bash
hei-datahub                    # Launch TUI
hei-datahub --version          # Show version
hei-datahub --version-info     # Show detailed info
hei-datahub reindex            # Rebuild search index
hei-datahub --help             # Show help
```

### TUI Keybindings

| Key | Action | Description |
|-----|--------|-------------|
| `/` | Search | Focus search box |
| `j/k` | Navigate | Move down/up |
| `Enter` | Open | View dataset details |
| `A` | Add | Add new dataset |
| `S` | Settings | GitHub settings |
| `P` | Outbox | Failed PR queue |
| `U` | Pull | Pull updates from catalog |
| `R` | Refresh | Refresh dataset list |
| `q` | Quit | Exit application |

---

## 🧪 Verification

All tests passing:

```bash
✅ Version commands work
✅ Database initializes correctly
✅ Datasets load on startup
✅ Search functionality works
✅ Pull updates works (U key)
✅ Refresh works (R key)
✅ All navigation works
✅ GitHub integration works
✅ PR workflow works
✅ Reindex command works
```

**Tested on:**
- ✅ Linux x86_64
- ✅ Python 3.13
- ✅ Fresh install
- ✅ Upgrade from v0.40.0

---

## 📚 Documentation

### New Documentation
- `CHANGELOG_v0.50.md` - Complete changelog
- `BUGFIX_MIGRATION_ERRORS.md` - Bug fix details
- `COMMAND_SETUP.md` - Running without uv
- `src/mini_datahub/version.py` - Version module docs

### Updated Documentation
- `pyproject.toml` - Version 0.50.0
- `Makefile` - Uses hei-datahub
- `README.md` - Updated examples

### Scripts
- `scripts/cleanup_v050.sh` - Automated cleanup
- `hei-datahub.sh` - Convenience wrapper

---

## 🔧 Technical Details

### Package Structure

```
mini-datahub==0.50.0
├── Entry points:
│   ├── hei-datahub → mini_datahub.cli.main:main
│   └── mini-datahub → mini_datahub.cli.main:main
├── Dependencies:
│   ├── textual>=0.47.0
│   ├── pydantic>=2.0.0
│   ├── pyyaml>=6.0
│   ├── jsonschema>=4.20.0
│   ├── requests>=2.31.0
│   ├── pyperclip>=1.8.2
│   └── keyring>=24.0.0
└── Python: >=3.9
```

### File Count
- **Removed:** 40+ old files
- **Added:** 3 new files (version.py, cleanup script, docs)
- **Modified:** 10+ core files
- **Net reduction:** ~37 files

### Code Quality
- ✅ All imports use new structure
- ✅ Proper separation of concerns
- ✅ Consistent naming conventions
- ✅ Comprehensive docstrings
- ✅ Type hints throughout

---

## 🚦 Breaking Changes

1. **Package structure** - Code in `src/` instead of root
2. **Import paths** - All imports updated to new structure
3. **Version format** - Changed from `v0.40-beta` to `0.50.0-beta`
4. **App name** - `Mini Hei-DataHub` → `Hei-DataHub`

**Migration:** Automatic via cleanup script

---

## 🐛 Known Issues

None currently. All migration bugs resolved.

---

## 🔮 Future Roadmap

### v0.60 (Planned)
- Enhanced search with filters
- Dataset templates
- Bulk operations
- Export functionality

### v0.70 (Planned)
- Plugin system
- Custom metadata fields
- Advanced GitHub integration
- API support

### v1.0 (Goal)
- Production-ready release
- Full test coverage
- Complete documentation
- Performance optimizations

---

## 🙏 Acknowledgments

This release represents significant architectural improvements that will make the project more maintainable and extensible going forward. The clean architecture pattern ensures the codebase can scale effectively.

---

## 📞 Support

- **Repository:** https://github.com/0xpix/Hei-DataHub
- **Issues:** https://github.com/0xpix/Hei-DataHub/issues
- **Discussions:** https://github.com/0xpix/Hei-DataHub/discussions

---

## 📄 License

MIT License - See `LICENSE` file for details

---

**Released with ❤️ by 0xpix**
