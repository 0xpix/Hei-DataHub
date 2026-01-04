# Changelog

All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.60.1-beta] - 2026-01-04

**Hotfix Release** - Critical fixes for authentication, installation, and legacy code removal.

### Fixed

- **Authentication Wizard**: Resolved compatibility issues between GUI and CLI authentication.
- **Dataset Creation**: Fixed "Auth Setup Required" bug that persisted even after successful setup.
- **Desktop Integration**: Fixed issue where desktop shortcuts were installed even in development environments.
- **Version Reporting**: Fixed `hei-datahub --version` showing "0.0.0-dev" in installed packages.
- **Crash on Start**: Fixed crash caused by missing data directory on first run.

### Changed

- **Cloud-Only Mode**: Removed automatic dataset seeding on first run.
- **Legacy Removal**: Completely removed `mini-datahub` alias and legacy code references.
- **Installation**: `version.yaml` is now correctly bundled with the package.

## [0.60.0-beta] - 2025-10-28 - Clean-up

**UI polish and codebase cleanup!** This release focuses on refining the user experience, streamlining the TUI, and removing legacy code.

### Added

- **New About Screen** - Minimalistic retro-inspired About screen
  - Press `Ctrl+a` to access from home screen
  - Project story, GitHub links, and documentation
  - Full Vim navigation support (`j/k`, `gg/G`, `d/u`)
- **Enhanced Search Filters** - New metadata filters
  - `source:` filter (e.g., `source:kaggle`)
  - `format:` filter (e.g., `format:csv`)
  - `tags:` filter (e.g., `tags:climate`)
- **Vim-Style Navigation** - Power user keyboard shortcuts
  - `gg` - Jump to top of list
  - `G` - Jump to bottom of list
  - `Ctrl+a` - Show About screen
- **Stable Scrollbars** - Consistent scrollbar behavior across all screens
  - Settings screen, wizard, help screen
  - Dataset details, add data form, edit screen

### Changed

- **UI Layout Improvements** - Refined visual hierarchy
  - Header & Footer reduced to 1 line height
  - Optimized padding and spacing throughout
  - Simplified search input placeholder
  - Updated loading status messages
- **Filter Badges** - Visual enhancements
  - Hash-based consistent color assignment
  - Vertical overflow support
  - Improved minimum height and padding
- **Search & Indexing** - Better metadata handling
  - Fixed field name mappings in metadata extraction
  - Improved project list parsing
  - Enhanced dataset loading with better logging

### Removed

- **Outbox Feature** - No longer needed with direct WebDAV workflow
  - Removed outbox service and UI screen
  - Removed outbox keybindings
- **Legacy GitHub Integration** - Fully replaced by WebDAV in v0.59
  - Removed GitHub PR workflow
  - Removed GitHub API client
  - Removed Git stash/branch operations
  - Removed PR-related status indicators
- **UI Cleanup**
  - Removed HeiBox/GitHub/PR status indicators from Home screen
  - Removed Cloud File Preview screen styles
  - Removed unused keybinding configuration logic
- **Code Cleanup**
  - Removed deprecated `mini_datahub` package initialization
  - Removed unused imports across UI views
  - Removed unused action display maps (~500 lines of code removed)

### Fixed

- Search navigation `gg` sequence handling for jump-to-top
- Keybinding display labels in footer
- Scrollbar flickering in scrollable containers
- Badge color consistency

### Documentation

- **Developer Documentation Refactor** - Complete upgrade for v0.60-beta
  - Rebranded from `mini-datahub` → `hei-datahub` across all dev docs
  - Updated all code examples, import paths, and CLI commands
  - Added version banners and compatibility matrix
  - Created ADR-004 documenting the docs upgrade
  - Enhanced navigation with breadcrumbs and cross-links
  - Added visual improvements (callouts, tables, diagrams)
- Added comprehensive v0.60-beta release notes
- Updated README badges and version references
- Updated installation guides to reference v0.60
- Maintained all existing WebDAV setup documentation

---

## [0.59.0-beta] - 2025-10-25 - Privacy

**WebDAV migration complete!** This release replaces GitHub-based catalog with direct WebDAV (HeiBox) cloud storage for datasets.

### Added

- **WebDAV Cloud Storage** - Direct integration with HeiBox/WebDAV servers
  - Configure URL, library, username, and token in settings
  - Cloud-only workflow (no local git repo required)
  - Secure credential storage via Linux keyring
- **New Settings Screen** - WebDAV configuration interface (replaced GitHub settings)
  - Press `s` to configure WebDAV connection
  - Direct access (no intermediate menu)
  - Credentials stored securely in system keyring
- **Auth Management Commands**:
  - `hei-datahub auth setup` - Configure WebDAV credentials
  - `hei-datahub auth doctor` - Diagnose auth issues
  - `hei-datahub auth clear` - Remove stored credentials
- **Smart Autocomplete** - Intelligent search suggestions
  - Column name completion
  - Value completion from index
  - Operator suggestions
- **Enhanced Filter Badges** - Visual query representation
  - Better visual hierarchy
  - Easier to understand complex queries
- **New Logo Design** - HeiPlanet brand colors
  - Main, H, inline, and round variants
  - Gradient and solid color versions

### Changed

- **"Pull" renamed to "Update"** - Press `U` to update datasets from cloud
- **Cloud-Only Architecture** - No more local git repository requirement
- **Simplified Settings** - Focused on WebDAV configuration only

### Removed

- **GitHub Integration** - Replaced with WebDAV
- **Outbox Feature** - No longer needed with direct WebDAV workflow
- **Theme Settings UI** - Still configurable via config.yaml

### Fixed

- Cloud dataset synchronization with WebDAV
- Settings screen now loads configuration correctly
- Direct settings access (no intermediate menu)

### Documentation

- Added comprehensive v0.59-beta release notes
- Updated all installation and configuration guides
- Added WebDAV setup documentation

---

## [0.58.3-beta] - 2025-10-10 - Windows Update Fix

**The Windows update nightmare is finally over!** This release completely solves the "Failed to install entrypoint" error that plagued Windows users.

### Added

- Each OS now has its own dedicated, maintainable update script!
- **Interactive Branch Selection** - Windows users can now choose update branch

### Fixed

- **Critical: "Failed to install entrypoint" Error** - The root cause and solution:
  - **Problem**: Windows locks `.exe` files while they're running (OS error 32)
  - **Previous Issue**: Running `uv tool install` while `hei-datahub.exe` was active
  - **Solution**: External batch script + new terminal strategy
  - **Result**: Python exits completely before update runs = no file lock! ✨

### Documentation

- Updated all Windows-related documentation
- Added inline comments explaining the Windows workaround
- Documented the OS-specific architecture

---

## [0.58.2-beta] - 2025-10-10

### Added

- **Update Repair Tool** - New `hei-datahub update --repair` command to fix broken installations
- **Installation Health Check** - Pre-flight check for file locks before attempting update
- **Better Error Recovery** - Specific error messages for "failed to remove directory" errors

### Changed
- **Update Preflight Checks** - Now includes installation lock detection

### Fixed
- Broken installations after failed updates (now detectable and repairable)
- Better error messages when update fails due to file locks
- Improved guidance for fixing corrupted installations

### Documentation
- Added update troubleshooting guide (`docs/help/update-troubleshooting.md`)

## [0.58.2-beta] - 2025-10-10

### Added
- **Desktop Integration (Linux)** - Automatic installation of desktop launcher and icons on first run
  - Full-color launcher icon (SVG + PNG fallback)
  - Symbolic tray icon (auto-adapts to dark/light themes)
  - XDG-compliant installation to `~/.local/share/` (no root required)
  - Idempotent and versioned (fast path when already installed)
  - CLI commands: `hei-datahub desktop install` and `hei-datahub desktop uninstall`
- **Packaged Assets** - All desktop assets (icons, .desktop entry) now ship inside the Python wheel
- **Atomic Desktop Updates** - Desktop integration updates automatically when app version changes
- **Icon Cache Refresh** - Best-effort refresh of GTK and KDE icon caches after installation

### Changed
- **CLI Command Structure** - Desktop integration commands now grouped under `hei-datahub desktop`:
  - `hei-datahub desktop install` - Install desktop integration
  - `hei-datahub desktop uninstall` - Remove desktop integration
- **Package Data** - Added `hei_datahub` package with desktop assets

### Fixed
- Desktop launcher icon not appearing on Linux (now installs properly to XDG paths)

### Documentation
- Added comprehensive desktop integration documentation (`docs/installation/desktop-integration.md`)
- Added implementation details (`DESKTOP_INTEGRATION.md`)
- Added CLI command update guide (`CLI_COMMAND_UPDATE.md`)

---

## [0.58.1-beta] - 2025-10-09

### Added
- Atomic update manager with multi-phase update process
- Windows-specific update helpers and troubleshooting
- Multi-stage progress bars during updates

### Changed
- Update command now uses atomic strategy (never breaks existing installation)

### Fixed
- Windows update failures that left users without working app
- Update process detection (no longer detects itself as running)

---

## [0.58.0-beta] - 2025-10-XX

Initial release of 0.58.x series "Streamline".
