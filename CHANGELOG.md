# Changelog

All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.58.3-beta] - 2025-10-10

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

---

[0.58.2-beta]: https://github.com/0xpix/Hei-DataHub/compare/v0.58.1-beta...v0.58.2-beta
[0.58.1-beta]: https://github.com/0xpix/Hei-DataHub/compare/v0.58.0-beta...v0.58.1-beta
[0.58.0-beta]: https://github.com/0xpix/Hei-DataHub/releases/tag/v0.58.0-beta
