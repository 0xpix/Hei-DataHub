
All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 📝 Version History

### ✅ Current (0.55.1-beta — "Persistence")

**Bug Fix Release — Reliable GitHub Token Storage**

**Fixed:**
- **Critical:** Personal Access Token (PAT) now persists after system reboot
- Resolved keyring issue preventing permanent credential storage

**Improved:**
- Keyring reliability on Linux systems
- Clearer error messages when keyring backend is unavailable
- Settings screen now confirms successful credential storage

---

### [0.55.0-beta] - 2025-01-04 — “Clean Architecture”

**Major Release — Complete Architectural Refactoring**

**Highlights:**
- Introduced **layered architecture** (UI → Services → Core → Infrastructure)
- Added **dual CLI commands:** `hei-datahub` and `mini-datahub`
- New **version management system** (`version.yaml` + auto-generated files)
- Integrated **GitHub Actions CI**, **pre-commit hooks**, and **MkDocs** documentation site

**Added:**
- Auto-stash workflow for safe PR creation
- Centralized logging with debug mode
- `--version-info` flag for detailed build/system info
- Dynamic documentation banner and macros plugin

**Changed:**
- Migrated to `src/mini_datahub/` package structure
- Unified settings via `GitHubConfig`
- Refactored exception hierarchy for clearer error handling

**Fixed:**
- BM25 ranking (prioritizes name matches)
- ISO 8601 date validation
- Database initialization and Git edge cases

**Documentation:**
- Comprehensive manual (tutorials, API reference, FAQ)
- Automatic deployment to GitHub Pages
- Defined versioning and release policy

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
