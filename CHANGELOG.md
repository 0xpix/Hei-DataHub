# Changelog

All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.58.0-beta] - 2025-10-07 "Streamline"

### ✨ Added

#### UV-Based Installation
- **Direct installation from private repository** without cloning
  - SSH authentication support (`git+ssh://`)
  - HTTPS + token authentication support
  - Ephemeral runs via `uvx`
  - Persistent installs via `uv tool install`
  - Version pinning support (tags, branches, commits)
- **Cross-platform support**
  - Linux installation guide
  - macOS installation guide
  - Windows PowerShell instructions

#### Data & Asset Packaging
- **Complete package data inclusion**
  - All data files, configs, schemas, assets now bundled
  - Added `MANIFEST.in` for source distributions
  - Updated `pyproject.toml` with proper package data configuration
  - Created `hei_datahub` alias package for consistent naming
  - Fixed "missing data files" issue from previous versions

#### Linux Desktop Integration
- **Desktop launcher script** (`scripts/create_desktop_entry.sh`)
  - Creates `.desktop` entry for application menu
  - Automatic executable path detection
  - XDG desktop database integration
  - Works with GNOME, KDE, XFCE, and other desktop environments
- **PyInstaller build script** (`scripts/build_desktop_binary.sh`)
  - Creates standalone binary (no Python required)
  - Bundles all dependencies
  - Semi-portable Linux executable
  - Optional AppImage creation support

#### Comprehensive Documentation
- **New installation documentation directory** (`docs/installation/`)
  - `README.md` - Overview and quick start
  - `uv-quickstart.md` - Complete UV installation guide
  - `private-repo-access.md` - SSH and token setup
  - `windows-notes.md` - Windows-specific instructions
  - `desktop-version.md` - Desktop launcher and binary guide
  - `troubleshooting.md` - Common issues and solutions
- **Updated main README** with UV installation quickstart
- **Step-by-step guides** for all installation methods

### 🔧 Changed
- **Package name**: Now published as `hei-datahub` (primary), `mini-datahub` still works
- **Minimum Python version**: Bumped to 3.10+ (from 3.9+)
- **Project structure**: Added `src/hei_datahub/` for better package consistency
- **Entry points**: Both `hei-datahub` and `mini-datahub` commands available

### 🐛 Fixed
- **Data files missing in installed package** - All assets now properly included
- **Import errors** after pip/UV installation - Package structure corrected
- **Module not found** errors for data/config directories

### 📚 Documentation
- Added **6 new documentation pages** covering all installation methods
- Windows installation guide with PowerShell examples
- Private repository authentication (SSH + PAT)
- Desktop integration for Linux users
- Comprehensive troubleshooting guide
- Quick reference commands and one-liners

### 🎯 Installation Methods (New)

**Ephemeral (one-time use):**
```bash
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub"
```

**Persistent (global install):**
```bash
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

**Desktop launcher:**
```bash
bash scripts/create_desktop_entry.sh
```

---

## [0.56.0-beta] - 2025-10-05 "Precision"

### Added
- Structured search with field-specific queries
- Inline editing capabilities
- Enhanced query parser

### Changed
- Improved TUI navigation
- Better search results ranking

---

## [0.55.2-beta] - Previous

### Added
- Auto-stash functionality for git operations
- Clean architecture refactoring
- Improved PR workflow

---

**Note**: For detailed version history before 0.55.x, see git commit history.
