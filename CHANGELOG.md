# Changelog

All notable changes to Hei-DataHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.66.0-beta] - 2026-02-19

**Major update.**

### Added

- *(to be documented)*

### Changed

- *(to be documented)*

### Fixed

- *(to be documented)*

---

## [0.65.32b] - 2026-02-19 - Wide Search

### Fixed

- **AUR update inside AppImage** — cleaned AppImage env vars from subprocess calls so pacman detection works; added `/opt/hei-datahub/` path-based AUR fallback; AUR helpers (yay/paru) no longer wrapped in `sudo` (credentials cached via `sudo -v` instead); AppImage `PermissionError` at `/opt/` now redirects to AUR update flow
- **`auth doctor` false write failure** — write test was hitting WebDAV root (`/seafdav/`) instead of inside the library; now uses correct path
- **Deleted datasets reappearing in search** — `_DELETED_DATASETS` folder excluded from indexer via `SKIP_FOLDERS` filter
- **Delete notification** — now mentions recovery via Heibox

### Changed

- Update progress messages cleaned up — removed tool-specific references; generic wording for all install methods

---

## [0.65.29b] - 2026-02-19 - Wide Search (HotFix)

**Bug fixes** — schema validation and keybinding conflict.

### Fixed

- **JSON Schema validation rejecting `access_method`, `category`, `reference`, `tags`** — a stale `schema.json` copy in `~/.local/share/Hei-DataHub/` was missing these properties (added after initial install). Fixed schema loader to always prefer the packaged schema over user-data copies, preventing stale schemas from blocking dataset creation
- **`Ctrl+S` opening Settings instead of saving on Add/Edit screens** — the app-level `ctrl+s → settings` binding had `priority=True`, which intercepted the key before screen-level `ctrl+s → submit/save_edits` bindings could fire. Removed `priority=True` from the global binding so screen-level bindings take precedence when active
- **`required` fields in `schema.json` out of sync with Pydantic model** — added `category` and `access_method` to the JSON Schema `required` array to match `DatasetMetadata` where they are non-optional

---

## [0.65.28b] - 2026-02-18 - Wide Search (Bug Fixes)

**Bug fixes & UX improvements** — macOS Keychain, FTS5 robustness, search completeness, and mode indicator.

### Fixed

- **Windows CI extracting wrong version for artifacts** — the "Get version info" step only read `version.yaml` (which could be stale). Now prefers `github.ref_name` (the git tag) and falls back to `version.yaml` only for `workflow_dispatch` runs
- **macOS Keychain password prompt on every launch** — skipped the `get_password()` availability probe on macOS (it triggered a Keychain dialog just to test), cached the `KeyringAuthStore` as a singleton, and added in-memory secret caching so the Keychain is accessed at most once per session
- **FTS5 syntax errors from special characters** (`: / | , "`) — all FTS-breaking characters are now stripped from search tokens before building the MATCH query; if cleaning removes all content, falls through to filter-only search instead of crashing
- **Spatial/temporal info missing in search results** — `search_indexed()` and `get_all_indexed()` were missing `spatial_resolution`, `temporal_resolution`, and `access_method` in their metadata dicts (only `_search_all()` had them), so tag searches and free-text searches showed incomplete spatial/temporal info
- **`hdh` command not working on macOS** — the Homebrew build tarball only contained the `hei-datahub` binary; added an `hdh` symlink to the macOS build script so both commands work after `brew install`
- **Special-character-only queries showing all data** — typing `.`, `?`, `>`, etc. now immediately shows a helpful hint ("Type a keyword to search…") instead of triggering the indexer timer that refilled the table with all datasets
- **Mode indicator stuck on Normal while typing** — set `search_mode = True` on mount and on every input change so the indicator correctly shows "Insert" from the moment the app starts and while actively typing
- CI changes — Fix Linux artifact naming inconsistent with other platforms.

---

## [0.65.14-beta] - 2026-02-16 - Wide Search (Hotfix)

**Hotfix:** Fixes macOS restart after update — app closed but relaunched with old version.

### Fixed

- **macOS restart after Homebrew update launching old binary** — `_restart_app` used `sys.executable` directly for frozen (PyInstaller) builds, which points to the old Cellar path (e.g. `.../Cellar/hei-datahub/0.65.12/bin/hei-datahub`) that Homebrew deletes during upgrade. Now resolves `shutil.which("hei-datahub")` first for all install types (frozen and non-frozen), which follows the updated `/opt/homebrew/bin/hei-datahub` symlink to the new version

---

## [0.65.13-beta] - 2026-02-16 - Wide Search (Hotfix)

**Hotfix:** Fixes the update badge not appearing on any platform (Windows, Linux, macOS).

### Fixed

- **Update badge never showing** — `_update_home_screen_badge` and `_hide_home_screen_badge` were mutating the DOM from a `@work(thread=True)` background thread; Textual silently drops UI mutations from non-main threads. Wrapped both in `call_from_thread()` so the badge toggle is dispatched to the main event loop

---

## [0.65.12-beta] - 2026-02-16 - Wide Search (Hotfix)

**Hotfix:** Fixes macOS Homebrew update not taking effect — app stayed on old version after `brew upgrade` and restart.

### Fixed

- **macOS update not applying** — the update overlay was missing `brew update` before `brew upgrade`, so Homebrew didn't know about the new formula and the upgrade was a silent no-op
- **Restart launching old binary** — `_restart_app` used `os.execv(sys.executable, ...)` which re-launched the old Python/binary path cached in the current process; now resolves the entry-point via `shutil.which("hei-datahub")` to pick up the freshly-linked binary after upgrade
- `os.execv` is now called before `app.exit()` (it replaces the process entirely, so exit was unreachable and could race on failure)

---

## [0.65.11-beta] - 2026-02-16 - Wide Search (Hotfix)

**Hotfix:** Fixes Windows update crashing with `'NoneType' object is not subscriptable` when the GitHub release has no description.

### Fixed

- **Windows update crash** — `release_data.get("body", "")[:500]` returns `None` (not `""`) when the GitHub release body is `null`, causing `TypeError: 'NoneType' object is not subscriptable`. Changed all `.get(key, "")` patterns to `(x.get(key) or "")` to correctly coalesce `null` values
- Same `None` safety applied to `tag_name`, `html_url`, and `body` fields across `windows_updater.py`, `update_check.py`, and `update_service.py`

---

## [0.65.10-beta] - 2026-02-16 - Wide Search (Hotfix)

**Hotfix:** Fixes Windows auto-update failing to launch the installer due to missing UAC elevation.

### Fixed

- **Windows update installer not launching** — replaced `subprocess.Popen` with `ShellExecuteW` + `runas` verb so the NSIS installer correctly triggers the UAC elevation prompt instead of silently failing with `ERROR_ELEVATION_REQUIRED` (740)
- Installer launch failure now shows actionable error message with UAC guidance and the downloaded installer path as manual fallback
- Silent exception swallowing in `install_update` — errors are now logged with full traceback

---

## [0.65.0-beta] - 2026-02-12 - Wide Search

**Extended Search & UX Improvements!** This release brings a powerful structured-tag search system with 10 filter tags, smart autocomplete, AND-accumulation for multiple filters, a redesigned About screen, and many bug fixes.

### Added

- **Structured search tags** — 10 short tags: `project`, `source`, `category`, `method`, `format`, `size`, `sr`, `sc`, `tr`, `tc`
- **Search autocomplete** — context-aware field name + field value suggestions ranked by frequency/recency
- **Tags help overlay** (`F3` in search mode) — shows all tag names, aliases, and descriptions
- **`all` keyword** — type `all` to list every dataset (no colon needed)
- **FTS fallback** — when structured tag filters return no results, falls back to free-text search
- `h`/`l` vim-style horizontal scroll in DataTable
- Operator-pending open-link mode in About screen (`o` → `g`:GitHub / `d`:Docs)
- Redesigned About screen — new origin/philosophy/links layout
- Version control for data backups (read-only unless modified directly in Heibox)

### Changed

- Tags help shortcut changed from `?` to `F3` (printable chars can't be intercepted in Input widget)
- `all` changed from `all:*` syntax to plain `all` keyword
- Tag generator deduplicated into shared `tag_generator.py` — keeps hyphenated words (e.g. ERA5-Land), extracts from source/access_method/temporal, caps description to 3 words, broad stop-word list
- Autocomplete suggests first word only for cleaner values (e.g. `sr:500` not `sr:"500 m"`)
- Multiple same-field tags are now AND-accumulated — `sr:0.5 sr:500` narrows results progressively instead of only using the last value

### Fixed

- **Critical:** Data not appearing after setting up auth until restart — settings save now calls `reload_configuration()` to trigger re-index
- Incremental sync wiping spatial_resolution, temporal_resolution, access_method, storage_location, reference
- Tag suggestions using DB column names (`spatial_resolution:500`) instead of short aliases (`sr:500`)
- `access_method` prefix not stripped in suggestions (`FILE: CSV` → `method:CSV`)
- Mode indicator stuck on "Normal" — now syncs with Input focus
- Tag comma handling — edit screen now lowercases tags consistently with add screen

### KNOWN ISSUES

- FTS5 syntax errors from special characters (`: / | , "`) — quoted phrases now cleaned

---

## [0.64.25-beta] - 2026-02-12 - Hotfix

**Hotfix:** Fixes the update badge not appearing on app launch after a new release is published.

### Fixed

- Update badge no longer hidden by 8-hour throttle cache on startup — every app launch now performs a fresh network check (non-blocking)
- Stale update badge is automatically hidden when a fresh check confirms no update is available

---

## [0.64.24-beta] - 2026-02-12 - Hotfix

**Hotfix:** Fixes Report Issue shortcut, update detection order, cross-platform URL opening, and redesigns the update overlay.

### Changed

- Update UI with improved user feedback during updates
- Update service with improved logging and error handling
- Installation method detection with improved logging

### Fixed

- Report Issue shortcut changed from `Ctrl+I` to `F2` (`Ctrl+I` is aliased to Tab in terminals and never fired)
- Update detection order — UV and pipx installs are now correctly detected before AUR/Homebrew
- Update badge only appears when a new update is genuinely available
- `xdg-open` on Linux no longer causes TTY issues (double-forking fix)
- URL opening refactored to shared cross-platform utility with browser fallback

**PS: The app hasn't been extensivly tested in Windows/MacOS**

---

## [0.64.15-beta] - 2026-02-04 - Silent Updates

**Silent Update Check & Bug Fixes!** This release adds automatic background update checking on app launch with a visual badge notification.

## Fixed

  - Fixed the update badge not showing up
  - Fixed "Change Theme" command not working from command palette (`Ctrl+P`)
  - Fixed `undefined symbol: rl_print_keybinding` error when using Ctrl+I on AUR-installed package

---

## [0.64.1-beta] - 2026-01-20 - macOS Auth Hotfix

**Hotfix:** Enables settings and authentication on macOS.

### Fixed

- **macOS Authentication Support**
  - Fixed settings wizard not working on macOS (was showing "only supported on Windows and Linux")
  - Added Darwin (macOS) to supported platforms for `auth setup`, `auth clear`, and `auth doctor` commands
  - macOS now uses the native Keychain for secure credential storage

---

## [0.64.0-beta] - 2026-01-16 - macOS Support & UI Refinements

**macOS Support & UX Improvements!** This release adds official macOS support via Homebrew and significantly improves the UI responsiveness and navigation.

### Added

- **macOS Support**
  - Official Homebrew Tap available (`brew tap 0xpix/homebrew-tap`)
  - Native `arm64` and `x86_64` builds
- Improved rendering on smaller terminal screens
- Minimalistic copy buttons added to dataset details fields
- **VIM-like Yanking**: Press multiple keys to copy specific fields in details view
- Dynamic footer showing available yank shortcuts
- Dedicated shortcut to report issues directly

### Changed

- ID is now auto-generated from the title (manual entry removed)
- Category field is now optional
- Empty fields display as "Not specified" instead of blank
- Improved column layout in the dataset table

### Fixed

- **Navigation & Shortcuts**
  - Fixed `o` shortcut in details view (now opens Access/Location link correctly)
  - Fixed `Esc` navigation flow (Search -> Home)
  - Fixed `Ctrl+T` (Theme) focus issues interfering with search bar
  - Fixed Windows-specific `Shift+Ctrl+S` shortcut issue
- **State Management**
  - Fixed data updates not reflecting immediately (save/delete no longer requires restart)
  - Fixed search results being cleared when navigating back from details
  - Fixed focus loss when returning to the list view

---

## [0.63.0-beta] - 2026-01-14 - Multi-Platform CI/CD

**Full CI/CD Pipeline & Cross-Platform Distribution!** This release introduces automated builds and distribution for Windows and Linux, MacOS coming soon.

### Added

- **GitHub Actions CI/CD Workflows**
  - `windows-build.yml` - Builds Windows `.exe` and NSIS installer
  - `linux-build.yml` - Builds Linux binary, `.deb` package, and `.AppImage`
  - `aur-publish.yml` - Automatic AUR package updates on new releases

- **Build Scripts**
  - `scripts/build_linux.sh` - Linux build with PyInstaller, creates `.deb` and `.AppImage`

- **AUR Package** - Hei-DataHub is now available on Arch Linux via AUR
  - Install with: `yay -S hei-datahub`
  - System-wide installation with desktop integration
  - Automatic updates when new versions are released

- **Release Automation**
  - All artifacts automatically uploaded to GitHub Releases on tag push
  - Support for any tag format (not just `v*` prefixed tags)

### Distribution Formats

| Platform | Formats |
|----------|---------|
| Windows  | `.exe` (portable), `.exe` (NSIS installer) |
| Linux    | Binary, `.deb`, `.AppImage` |
| Arch     | AUR package (`hei-datahub`) |

---

## [0.62.0-beta] - 2026-01-13 - Re-design

**UI Overhaul & Keyboard Navigation!** This release brings a redesigned interface with improved keyboard navigation.

### Added

- New `Ctrl+P` command palette for quick access to all actions
- Custom theme selector replacing Textual's default (`Ctrl+T`)
- Confirmation dialog when pressing `Esc` on the main page
- Dynamic shortcuts that change based on current screen/context
  - Home: Add, Commands, Settings, Theme
  - Results: Navigate (j/k), Top (gg), Bottom (G), Open, Clear
  - Details: Edit, Delete, Copy URL, Open URL, Back
  - Edit/Add: Save, Next/Prev Field, Cancel
- Run the app with `hdh` or `hei-datahub`

### Changed

- Cleaner layout with improved visual
- Enhanced metadata presentation
- **New Keyboard Shortcuts**
  - `Ctrl+N` Add Dataset, `Ctrl+Shift+S` Settings, `Ctrl+U` Check Updates
  - `Ctrl+R` Refresh, `Ctrl+Q` Quit, `Ctrl+I` About
- Removed `Ctrl+H` help shortcut (replaced by command palette)

### Fixed

- Search bar focus issues after pressing `Esc` or `Enter`
- Accidental dataset selection when pressing `Enter` with unfocused search
- Footer shortcuts persisting incorrectly after navigating between screens
- Command palette not showing all shortcuts on home screen
- About page footer shortcuts
- Logo display on small terminal screens

## [0.61.0-beta] - 2026-01-07 - Windows-Compatibility

**Windows Support Arrives!** This release brings full Windows compatibility to Hei-DataHub.

### Added

- **Windows Support** - Fully functional Windows executable (`.exe`).
  - Automated build scripts (`scripts/build_windows_exe.ps1`).
  - Windows credential management integration.
  - Cross-platform path handling for data directories.

### Changed

- Updated authentication backend to support both Linux Keyring and Windows Credential Locker.
- Refactored platform-specific checks in CLI tools to allow Windows execution.
- Move the documentations to the main website.

## [0.60.1-beta] - 2026-01-04

**Hotfix Release** - Critical fixes for authentication, installation, and legacy code removal.

### Fixed

- Fixed issue where desktop integration was installed.
- Fixed crash caused by missing data directory on first run.
- Resolved multiple issues with Authentication Wizard:
  - Explicitly asks for HeiBox WebDAV credentials instead of generic username/password.
  - Fixed compatibility between GUI and CLI authentication.
  - Fixed "Auth Setup Required" bug that persisted even after successful in-app setup.
- Fixed save function failure in dataset creation.
- Fixed `hei-datahub --version` showing "0.0.0-dev" in installed packages.

### Changed

- Removed automatic dataset seeding on first run (Cloud-Only Mode).
- Completely removed `mini-datahub` alias and legacy code references.
- `version.yaml` is now correctly bundled with the package.

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
