
All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 📝 Version History

### ✅ Current (0.55.1-beta — "Persistence")

**Bug Fix Release: GitHub PAT Persistence**

**Changed:**
- **Critical: GitHub PAT not persisting after PC restart**
  - Fixed keyring storage issue where Personal Access Token was not being saved permanently
  - GitHub credentials now persist correctly across system reboots
  - Users no longer need to re-enter PAT after restarting their computer

**Improved:**
- Keyring integration reliability in Linux (haven't tested windows/MacOS)
- Better error messages when keyring backend is unavailable
- Settings screen now shows confirmation when credentials are stored

---

### [0.55.0-beta] - 2025-01-04 — "Clean Architecture"

**Major Release: Architectural Refactoring**

**Added:**
- Dual command support: `hei-datahub` and `mini-datahub`
- Auto-stash for PR workflow (saves uncommitted changes)
- Improved gitignore handling during PR creation
- `--version-info` flag for detailed system information
- Comprehensive documentation site (MkDocs + Material theme)
- Clean layered architecture (UI → Services → Core → Infrastructure)
- Centralized version management via `version.yaml`
- Auto-generation of version files (`_version.py`, `version.md`, `version.json`)
- Version sync script with dry-run support
- Pre-commit hooks for version consistency
- GitHub Actions CI validation for version sync
- Dynamic documentation banner with version info

**Changed:**
- Migrated to `src/mini_datahub/` package structure
- Unified settings management via `GitHubConfig` class
- Centralized logging configuration with debug mode
- Custom exception hierarchy for better error messages
- Version module now imports from auto-generated `_version.py`
- MkDocs configuration includes macros plugin

**Improved:**
- Developer experience: single file to edit for version bumps
- Consistency: eliminates hardcoded version strings
- Release process: pre-commit hooks enforce version sync

**Fixed:**
- BM25 search ranking (name matches prioritized)
- ISO 8601 date validation consistency
- Database initialization error handling
- Git operations edge cases (detached HEAD, merge conflicts)

**Documentation:**
- Complete manual with tutorials, API reference, and FAQ
- GitHub Pages auto-deployment
- Versioning policy document

---

### [0.54.0-beta] - 2025-10-03

**Added:**
- Outbox system for failed PR tasks (`.outbox/` directory)
- Weekly update check for new releases
- GitHub status indicator in TUI

**Changed:**
- Search debounce reduced to 150ms (faster response)
- Improved table column width allocation

**Fixed:**
- Keyring integration on Linux without GNOME Keyring
- YAML parsing for multi-line strings and special characters

---

### [0.53.0-beta] - 2025-10-03

**Added:**
- Pull updates command (`u` keybinding)
- Refresh command (`r` keybinding) without reindexing

**Fixed:**
- Search query escaping for FTS5 special operators
- Dataset ID validation for auto-generated IDs

---

### [0.52.0-beta] - 2025-10-03

**Added:**
- Vim-style navigation (`j`/`k`, `gg`/`G`)
- Copy source shortcut (`c` on Details Screen)
- Open URL shortcut (`o` on Details Screen)

**Changed:**
- More compact footer shortcuts display

---

### [0.51.0-beta] - 2025-10-03

**Added:**
- GitHub PR integration with automated workflow
- Settings screen for GitHub credentials

**Fixed:**
- Database locking issues on multi-core systems

---

### [0.50.0-beta] - 2025-10-02

**Initial Beta Release**

**Added:**
- Full-text search with SQLite FTS5 and BM25 ranking
- Add Dataset form with TUI validation
- Details screen for complete metadata view
- Reindex command: `hei-datahub reindex`

---

### [0.40.0-alpha] - 2025-10-02

**Alpha Release**

**Added:**
- Basic TUI with search functionality
- YAML-based metadata storage

---
## 🚧 Unreleased — Upcoming Features
### 🧭 0.57.0-beta — "Navigator"

**Theme:** Discovery & Navigation

#### Proposed Features

- **🏷️ Tags System**
  - Tag datasets with custom labels (e.g., "climate", "high-priority", "archived")
  - Tag-based filtering and search
  - Tag management screen
  - Color-coded tags in table view
  - Tag autocomplete during dataset creation

- **📂 Collections/Groups**
  - Organize datasets into logical collections
  - Hierarchical groups (projects → datasets)
  - Collection-specific views
  - Drag-and-drop dataset organization

- **🔗 Dataset Relationships**
  - Link related datasets (derived-from, supplements, replaces)
  - Relationship graph visualization
  - Navigate between related datasets
  - Dependency tracking

- **🌍 Spatial Search**
  - Geographic bounding box search for raster/vector datasets
  - Map-based dataset discovery (optional)
  - Coordinate-based filtering

- **📊 Advanced Filters**
  - Date range filters (created, modified)
  - Size range filters
  - Multi-criteria filter builder
  - Save filter presets

---

### 📜 0.58.0-beta — "Archivist"

**Theme:** History & Versioning

#### Proposed Features

- **🕰️ Dataset History Tracking**
  - Track all changes to dataset metadata over time
  - Git-backed history log per dataset
  - View diff between versions
  - Restore previous metadata versions
  - Audit trail with timestamps and authors

- **📝 Change Annotations**
  - Add comments/notes when editing datasets
  - Change reason tracking
  - Review history in TUI

- **🔄 Version Comparison**
  - Side-by-side diff view for metadata changes
  - Highlight added/removed/modified fields
  - Export change history to Markdown

- **🗂️ Archive/Unarchive Datasets**
  - Mark datasets as archived (hidden from default view)
  - Archived datasets remain searchable
  - Restore archived datasets
  - Bulk archive operations

- **🔔 Change Notifications**
  - Subscribe to dataset updates
  - Email or webhook notifications (optional)
  - RSS feed for catalog changes

---

### 🤖 0.59.0-beta — "AutoPilot"

**Theme:** Automation & Intelligence

#### Proposed Features

- **🧠 Smart Metadata Suggestions**
  - AI-powered metadata field suggestions based on source URLs
  - Auto-detect data format from file extensions
  - Suggest tags based on description content
  - Pre-fill common fields (date_created, storage_location)

- **🔗 External Catalog Integration**
  - Import datasets from CKAN, Socrata, or other catalogs
  - Sync with remote catalogs (one-way or bi-directional)
  - Convert external metadata schemas to Hei-DataHub format

- **📊 Bulk Operations**
  - Select multiple datasets in table view
  - Bulk edit common fields
  - Batch tag assignment
  - Bulk export and delete

- **🕷️ Automated Discovery**
  - Crawl directories for dataset files
  - Auto-generate metadata from file headers (CSV, Parquet, etc.)
  - Schedule periodic scans

- **📈 Usage Analytics**
  - Track dataset access frequency
  - Popular datasets dashboard
  - Search query analytics
  - Export usage reports

---

### 🔌 0.60.0-beta — "Nexus"

**Theme:** Integration & Extension

#### Proposed Features

- **🔌 Plugin System**
  - Extensible architecture for custom features
  - Plugin API for adding data sources
  - Custom validators and formatters
  - Community plugin registry

- **🌐 RESTful API**
  - HTTP API for programmatic access
  - JSON responses for dataset queries
  - Authentication via API keys
  - OpenAPI/Swagger documentation

- **💾 Cloud Sync (Optional)**
  - Optional sync with S3, GCS, or Azure Blob Storage
  - Encrypt metadata before upload
  - Multi-device sync for teams
  - Conflict resolution strategies

- **🔗 Webhook Support**
  - Trigger webhooks on dataset events (add, edit, delete)
  - Integrate with Slack, Discord, or custom endpoints
  - Configurable webhook payloads

- **📦 Data Preview**
  - Preview CSV, JSON, Parquet files directly in TUI
  - Sample rows display
  - Column statistics (min, max, mean for numeric data)
  - Integration with DuckDB for large file previews

- **🐍 Python API**
  - Programmatic dataset management via Python library
  - Jupyter notebook integration
  - Pandas DataFrame export
  - Example notebooks for common workflows

---

### 🎯 1.0.0-stable — "Foundation"

**Theme:** Stability & Maturity

#### Proposed Features

- **🔒 Stable API**
  - No breaking changes in MINOR releases (1.x.y)
  - Long-term support (LTS) for 1.0.x line
  - Comprehensive API reference documentation

- **📚 Complete Documentation**
  - API reference for all modules
  - Architecture decision records (ADRs)
  - Contribution guidelines
  - Developer handbook

- **🧪 Comprehensive Testing**
  - 90%+ test coverage
  - Integration tests for all workflows
  - Performance benchmarks
  - End-to-end TUI testing

- **🌍 Internationalization (i18n)**
  - Multi-language UI support (English, French, Spanish, etc.)
  - Localized documentation
  - Configurable locale in Settings

- **♿ Accessibility Improvements**
  - Screen reader support
  - High-contrast themes
  - Keyboard-only navigation enhancements
  - WCAG compliance

- **📦 Distribution**
  - PyPI package distribution
  - Docker container images
  - Homebrew formula (macOS)
  - APT/RPM packages (Linux)
  - Windows installer
---

## Version Naming

Hei-DataHub follows [Semantic Versioning](https://semver.org/):

- **MAJOR:** Incompatible API changes (after 1.0.0)
- **MINOR:** New features, may include breaking changes during beta (0.x.y)
- **PATCH:** Backward-compatible bug fixes

**Prerelease Labels:**

- **-alpha:** Early testing, unstable
- **-beta:** Feature-complete, testing for bugs
- **-rc.X:** Release candidate, nearly stable

---

## How to Upgrade

See [Versioning Policy](98-versioning.md#upgrade-strategy) for detailed upgrade instructions.

**Quick upgrade (patch releases):**

```bash
cd Hei-DataHub
git pull origin main
source .venv/bin/activate
pip install -e .
```

---

## Changelog Policy

**Every release must:**

1. Update this file with a new version entry
2. List all user-visible changes under categories:
    - **Added:** New features
    - **Changed:** Changes to existing functionality
    - **Deprecated:** Soon-to-be-removed features
    - **Removed:** Removed features
    - **Fixed:** Bug fixes
    - **Security:** Vulnerability fixes
3. Link to relevant GitHub issues/PRs where applicable

**Patch releases** update the same docs line (e.g., 0.55.x).

**Minor releases** may introduce new docs or major updates.

---

## Related Links

- **[Versioning Policy](98-versioning.md)** — Understanding SemVer and Hei-DataHub's approach
- **[GitHub Releases](https://github.com/0xpix/Hei-DataHub/releases)** — Download releases
- **[Milestones](https://github.com/0xpix/Hei-DataHub/milestones)** — Upcoming features

---

## Questions?

- **What's new in the latest release?** → See the most recent entry above
- **When will feature X ship?** → Check GitHub Milestones
- **Where can I report bugs?** → [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)

---

_Last updated: 2025-01-04 for 0.55.0-beta_
