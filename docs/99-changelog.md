# Changelog

All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.55.5-beta] - 2025-10-04

### 🔧 Maintenance Release: "Fjord"

This release focuses on centralizing version management and improving documentation infrastructure.

### Added

- **Centralized Version Management:** Single source of truth via `version.yaml`
    - Auto-generates Python module (`src/mini_datahub/_version.py`)
    - Auto-generates docs version banner (`docs/_includes/version.md`)
    - Auto-generates build metadata (`build/version.json`)
    - Auto-updates `pyproject.toml` version field
- **Version Sync Script:** `scripts/sync_version.py` with `--dry-run` support
- **Pre-commit Hooks:** Automatically syncs version files when `version.yaml` changes
- **GitHub Actions:** CI workflow validates version sync on PRs
- **Documentation Banner:** Dynamic version notice on homepage using mkdocs-macros-plugin

### Changed

- **Version Module:** `src/mini_datahub/version.py` now imports from auto-generated `_version.py`
- **MkDocs Configuration:** Added macros plugin for Jinja2 template includes
- **Dependency Management:** Added `mkdocs-macros-plugin>=1.0.0` to dev dependencies

### Improved

- **Developer Experience:** Version bumps now require editing only `version.yaml`
- **Consistency:** Eliminates hardcoded version strings across codebase
- **Release Process:** Pre-commit hooks enforce version sync before commits

### Documentation

- **Version Banner:** Auto-generated version notice includes codename, release date, and compatibility notes
- **Versioning Policy:** Updated to reference centralized system

---

## [0.55.0-beta] - 2025-01-04

### 🎉 Major Release: "Clean Architecture"

This release represents a significant refactoring of Hei-DataHub's internal architecture, along with new features for improved PR workflows and developer experience.

### Added

- **Dual Command Support:** Both `hei-datahub` and `mini-datahub` commands now work interchangeably
- **Auto-Stash for PR Workflow:** Automatically stashes uncommitted changes before creating PRs, then restores them afterward
- **Improved Gitignore Handling:** Better detection and respect for `.gitignore` patterns during PR creation
- **Enhanced Version Information:** New `--version-info` flag shows detailed system and build information
- **Documentation System:** Comprehensive manual (this site!) with MkDocs + Material theme
- **Clean Architecture:** Layered design with clear separation:
    - **UI Layer:** Textual-based TUI screens and widgets
    - **Services Layer:** Business logic orchestration (search, catalog, publish, sync)
    - **Core Domain:** Pure models and validation rules (no I/O)
    - **Infrastructure Layer:** Adapters for SQLite, YAML, Git, GitHub API

### Changed

- **Repository Structure:** Moved from flat layout to `src/mini_datahub/` package structure
- **Settings Management:** Unified configuration via `GitHubConfig` class with keyring integration
- **Error Handling:** Custom exception hierarchy for better error messages
- **Logging:** Centralized logging configuration with debug mode support

### Fixed

- **Search Ranking:** BM25 scoring now correctly prioritizes name matches over description matches
- **Date Validation:** ISO 8601 date format enforced consistently across add/edit forms
- **Database Initialization:** More robust schema creation with proper error handling
- **Git Operations:** Better handling of edge cases (detached HEAD, merge conflicts, stale branches)

### Documentation

- **New Manual:** Complete documentation site with:
    - Getting Started guide
    - Keyboard shortcuts reference
    - Data & SQL deep dive
    - Configuration guide
    - 3 hands-on tutorials
    - FAQ & troubleshooting
    - Versioning policy
- **GitHub Pages:** Docs auto-deployed via GitHub Actions on merge to `main`

### Internal

- **Test Coverage:** Expanded test suite for core services
- **Type Hints:** Improved type annotations across codebase
- **Code Quality:** Linting with Ruff, formatting with Black
- **Dependency Management:** Migrated to `uv` for faster installs

---

## [0.55.1-beta] - TBD

### Fixed

- _(Placeholder for next patch release)_

---

## [0.54.0-beta] - 2024-12-15

### Added

- **Outbox System:** Failed PR tasks stored in `.outbox/` for manual retry
- **Update Check:** Weekly check for new releases (configurable)
- **GitHub Status Indicator:** Visual indicator of GitHub connection status in TUI

### Changed

- **Search Debounce:** Reduced from 200ms to 150ms for snappier response
- **Table Rendering:** Improved column width allocation for better readability

### Fixed

- **Keyring Integration:** Fixed PAT storage on Linux systems without GNOME Keyring
- **YAML Parsing:** Better handling of multi-line strings and special characters

---

## [0.53.0-beta] - 2024-11-20

### Added

- **Pull Updates Command:** Press `u` to pull latest changes from remote repo
- **Refresh Command:** Press `r` to reload dataset list without reindexing

### Fixed

- **Search Query Escaping:** Fixed crash when searching with special FTS5 operators
- **Dataset ID Validation:** Auto-generated IDs now handle edge cases (leading/trailing dashes)

---

## [0.52.0-beta] - 2024-10-30

### Added

- **Vim-style Navigation:** Added `j/k` for up/down, `gg/G` for top/bottom
- **Copy Source Shortcut:** Press `c` on Details Screen to copy source to clipboard
- **Open URL Shortcut:** Press `o` on Details Screen to open source URL in browser

### Changed

- **Footer Shortcuts:** More compact display of keyboard shortcuts

---

## [0.51.0-beta] - 2024-10-10

### Added

- **GitHub PR Integration:** Automated PR creation from TUI
- **Settings Screen:** Configure GitHub credentials and preferences

### Fixed

- **Database Locking:** Fixed concurrent access issues on multi-core systems

---

## [0.50.0-beta] - 2024-09-20

### Added

- **Initial Beta Release**
- **Full-Text Search:** SQLite FTS5 with BM25 ranking
- **Add Dataset Form:** TUI-based dataset creation with validation
- **Details Screen:** View complete dataset metadata
- **Reindex Command:** `hei-datahub reindex` to rebuild search index

---

## [0.40.0-alpha] - 2024-08-15

### Added

- **Alpha Release**
- Basic TUI with search functionality
- YAML-based metadata storage

---

## Unreleased

Features planned for future releases:

### 0.56.0-beta (Next Minor)

- **Inline Editing:** Edit datasets directly from Details Screen
- **Bulk Operations:** Add/edit multiple datasets at once
- **Field-Specific Search:** `source:github.com`, `format:CSV`, etc.
- **Export/Import:** Bulk export to JSON/CSV

### 0.60.0-beta (Future)

- **Dataset History:** Track changes to metadata over time
- **Tags System:** Tag datasets with custom labels
- **Advanced Filters:** Date ranges, size ranges, custom queries

### 1.0.0 (Stable)

- **Stable API:** No more breaking changes in MINOR releases
- **Comprehensive Docs:** Complete API reference
- **Plugin System:** Extend Hei-DataHub with custom plugins
- **Cloud Sync:** Optional sync with cloud storage (S3, GCS)

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

**Patch releases** update the same docs line (e.g., v0.55.x).

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

_Last updated: 2025-01-04 for v0.55.0-beta_
