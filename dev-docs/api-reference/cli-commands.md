# CLI Commands Reference

> **Version:** 0.60.0-beta — "Clean-up"
> This documentation reflects the current CLI commands available in v0.60.

!!! info "What this section covers"
    Complete reference for all `hei-datahub` command-line interface commands. This page covers every subcommand, option, and flag available in v0.60.0-beta.

## Overview

Complete reference for all `hei-datahub` command-line interface commands.

!!! note "Command Name Change"
    **v0.60:** The `mini-datahub` alias has been removed. Use `hei-datahub` exclusively.

**Quick Reference:**

- [TUI Launch](#tui-launch) - Launch the terminal interface
- [Authentication](#authentication-commands) - WebDAV credential management
- [Search & Index](#search-index-commands) - Dataset indexing and search
- [Diagnostics](#diagnostic-commands) - Health checks and troubleshooting
- [System](#system-commands) - Updates, paths, and configuration
- [Desktop Integration](#desktop-integration-commands) - Linux desktop shortcuts
- [Keybindings](#keybinding-commands) - Custom key mapping

---

## Command Structure

```bash
# General syntax
hei-datahub [GLOBAL_OPTIONS] [COMMAND] [COMMAND_OPTIONS]
```

!!! warning "Legacy Alias Removed"
    The `mini-datahub` alias was removed in v0.60. Use `hei-datahub` instead.

### Global Options

Available for all commands:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--version` | Flag | Show version number and exit | - |
| `--version-info` | Flag | Show detailed version info with ASCII art | - |
| `--data-dir PATH` | Path | Override data directory location | Platform-specific |
| `--set KEY=VALUE` | Config | Set config override for session | - |

**Examples:**

```bash
# Show version
hei-datahub --version

# Show detailed version info
hei-datahub --version-info

# Override data directory
hei-datahub --data-dir ~/my-custom-data

# Set config override
hei-datahub --set search.debounce_ms=200
```

---

## TUI Launch

### Default Command (No Arguments)

**Syntax:**

```bash
hei-datahub
```

**Description:**

Launch the interactive Terminal User Interface (TUI) with the home screen.

**What it does:**

1. Initializes workspace directories (`~/.config`, `~/.cache`, `~/.local/share`)
2. Ensures SQLite database exists
3. Installs desktop assets (Linux only, first run)
4. Launches Textual TUI application

**Exit codes:**

- `0`: Normal exit
- `1`: Error during initialization or runtime

**Examples:**

```bash
# Launch TUI
hei-datahub

# Launch with custom data directory
hei-datahub --data-dir ~/my-datasets

# Launch with config override
hei-datahub --set ui.theme=dark
```

---

## Authentication Commands

### `auth setup`

**Syntax:**

```bash
hei-datahub auth setup [OPTIONS]
hei-datahub setup [OPTIONS]  # Alias
```

**Description:**

Interactive wizard to configure WebDAV authentication for HeiBox/Seafile cloud storage. **Linux only.**

**Options:**

| Option | Type | Description | Required | Default |
|--------|------|-------------|----------|---------|
| `--url URL` | String | WebDAV base URL | Non-interactive | Prompted |
| `--username USER` | String | Username (for password auth) | No | - |
| `--token TOKEN` | String | WebDAV app token | Yes* | Prompted |
| `--password PASS` | String | WebDAV password | Yes* | Prompted |
| `--library NAME` | String | Library/folder name | Yes | Prompted |
| `--store {keyring,env}` | Choice | Storage backend | No | `keyring` |
| `--no-validate` | Flag | Skip credential validation | No | `false` |
| `--overwrite` | Flag | Overwrite existing config | No | `false` |
| `--timeout SECS` | Integer | Validation timeout | No | `8` |
| `--non-interactive` | Flag | Non-interactive mode | No | `false` |

*Either `--token` or `--password` required.

**Interactive Mode (Default):**

```bash
hei-datahub auth setup
```

**Interactive Flow:**

```
🔐 Hei-DataHub WebDAV Authentication Setup (Linux)

Found config at ~/.config/hei-datahub/config.toml
  [O]verwrite, [S]kip, [T]est? O

Enter WebDAV URL (default: https://heibox.uni-heidelberg.de/seafdav):
> https://heibox.uni-heidelberg.de/seafdav

Enter library/folder name (e.g., testing-hei-datahub):
> my-datasets

Authentication method:
  [T]oken (recommended) or [P]assword? T

Enter WebDAV token (hidden):
> **********************

Validating connection...
✓ Connection successful
✓ Read permission verified
✓ Write permission verified

Saving configuration...
✓ Config saved to ~/.config/hei-datahub/config.toml
✓ Credentials stored in keyring

Setup complete!
```

**Non-Interactive Mode:**

```bash
# Token authentication (recommended)
hei-datahub auth setup \
  --url "https://heibox.uni-heidelberg.de/seafdav" \
  --token "your-webdav-token" \
  --library "my-datasets" \
  --store keyring \
  --non-interactive

# Password authentication
hei-datahub auth setup \
  --url "https://heibox.uni-heidelberg.de/seafdav" \
  --username "your-username" \
  --password "your-password" \
  --library "my-datasets" \
  --non-interactive

# With environment variable storage (less secure)
hei-datahub auth setup \
  --url "https://heibox.uni-heidelberg.de/seafdav" \
  --token "$WEBDAV_TOKEN" \
  --library "my-datasets" \
  --store env \
  --non-interactive
```

**Exit Codes:**

- `0`: Setup successful
- `1`: Validation failed or user aborted
- `2`: Usage error (missing required args in non-interactive mode)

**Files Modified:**

- `~/.config/hei-datahub/config.toml` - Created/updated
- OS keyring - Credentials stored (if `--store keyring`)

**See Also:**

- [Authentication & Sync](../architecture/auth-and-sync.md#hei-datahub-auth-setup)
- [Security & Privacy](../architecture/security-privacy.md#credential-management)

---

### `auth status`

**Syntax:**

```bash
hei-datahub auth status
```

**Description:**

Display current WebDAV authentication configuration (non-sensitive information only).

**Output Example:**

```
🔐 WebDAV Authentication Status

Method:     token
URL:        https://heibox.uni-heidelberg.de/seafdav
Username:   -
Storage:    keyring
Key ID:     webdav:token:-@heibox.uni-heidelberg.de

Config:     /home/user/.config/hei-datahub/config.toml
```

**Exit Codes:**

- `0`: Config exists and is valid
- `1`: No config or invalid config

**What is Shown:**

- ✅ Authentication method (token/password)
- ✅ WebDAV URL
- ✅ Username (if used)
- ✅ Storage backend (keyring/env)
- ✅ Key ID reference
- ✅ Config file path

**What is NOT Shown:**

- ❌ Actual credentials (password/token)
- ❌ Keyring contents

---

### `auth doctor`

**Syntax:**

```bash
hei-datahub auth doctor [OPTIONS]
```

**Description:**

Run comprehensive diagnostics on WebDAV authentication and connectivity. Tests connection, permissions, and configuration validity.

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--json` | Flag | Output results as JSON | `false` |
| `--no-write` | Flag | Skip write permission tests | `false` |
| `--timeout SECS` | Integer | Network timeout | `8` |

**Examples:**

```bash
# Full diagnostics (recommended)
hei-datahub auth doctor

# Read-only tests (skip write checks)
hei-datahub auth doctor --no-write

# JSON output for scripting
hei-datahub auth doctor --json

# Longer timeout for slow networks
hei-datahub auth doctor --timeout 15
```

**Output Example (Success):**

```
🔍 WebDAV Authentication Diagnostics

[1/7] Config file exists ............................ ✓ PASS
      Path: /home/user/.config/hei-datahub/config.toml

[2/7] Config has [auth] section .................... ✓ PASS

[3/7] Credentials found in keyring ................. ✓ PASS
      Key ID: webdav:token:-@heibox.uni-heidelberg.de

[4/7] WebDAV URL reachable ......................... ✓ PASS
      Response time: 142ms

[5/7] Authentication successful .................... ✓ PASS
      Method: token

[6/7] Read permission verified ..................... ✓ PASS
      Listed 3 files in library

[7/7] Write permission verified .................... ✓ PASS
      Created/deleted test file successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All checks passed! WebDAV authentication is working.
```

**Output Example (Failure):**

```
[4/7] WebDAV URL reachable ......................... ✗ FAIL
      Error: Connection timeout after 8s

[5/7] Authentication successful .................... ⊘ SKIP
[6/7] Read permission verified ..................... ⊘ SKIP
[7/7] Write permission verified .................... ⊘ SKIP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ Diagnostics failed. Check network connection and credentials.

Suggestions:
  • Verify internet connection
  • Check if HeiBox is accessible from your network
  • Try increasing timeout: hei-datahub auth doctor --timeout 15
```

**Checks Performed:**

1. Config file exists
2. Config has `[auth]` section
3. Credentials found in keyring
4. WebDAV URL reachable (network connectivity)
5. Authentication successful (401 check)
6. Read permissions (list files)
7. Write permissions (create/delete test file)

**Exit Codes:**

- `0`: All checks passed
- `1`: One or more checks failed

**See Also:**

- [Authentication & Sync](../architecture/auth-and-sync.md#hei-datahub-auth-doctor)
- [Troubleshooting](#troubleshooting)

---

### `auth clear`

**Syntax:**

```bash
hei-datahub auth clear [OPTIONS]
```

**Description:**

Remove stored WebDAV credentials, configuration, and search index. Use this to reset authentication state or switch accounts.

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--force` | Flag | Skip confirmation prompt | `false` |
| `--all` | Flag | Also remove cache files | `false` |

**Examples:**

```bash
# Interactive confirmation (default)
hei-datahub auth clear

# Force without confirmation
hei-datahub auth clear --force

# Remove everything including cache
hei-datahub auth clear --all --force
```

**Interactive Flow:**

```
⚠️  Clear WebDAV Authentication

This will remove:
  • Config file: /home/user/.config/hei-datahub/config.toml
  • Keyring entry: webdav:token:-@heibox.uni-heidelberg.de
  • Search index: /home/user/.local/share/Hei-DataHub/db.sqlite

Continue? [y/N] y

✓ Removed config file
✓ Removed keyring entry
✓ Removed search index

Authentication cleared. Run 'hei-datahub auth setup' to reconfigure.
```

**What Gets Removed:**

| Item | Default | With `--all` |
|------|---------|--------------|
| Config file (`config.toml`) | ✅ | ✅ |
| Keyring entry | ✅ | ✅ |
| Search index (`db.sqlite`) | ✅ | ✅ |
| Cached datasets (`~/.cache/hei-datahub/datasets/`) | ❌ | ✅ |
| Session cache (`~/.cache/hei-datahub/sessions/`) | ❌ | ✅ |

**Exit Codes:**

- `0`: Successfully cleared
- `1`: User aborted or error

**Warning:**

This operation **cannot be undone**. You will need to run `auth setup` again to reconfigure authentication.

---

## Search & Index Commands

### `reindex`

**Syntax:**

```bash
hei-datahub reindex
```

**Description:**

Rebuild the search index from all dataset YAML files in the data directory. Use this when search results are out of sync or after bulk dataset changes.

**What it does:**

1. Lists all datasets in data directory
2. Loads metadata from each `metadata.yaml`
3. Updates SQLite FTS5 search index
4. Optimizes index for performance

**Output Example:**

```
Reindexing datasets from data directory...
  ✓ Indexed: dataset-climate-2024
  ✓ Indexed: dataset-weather-records
  ✓ Indexed: dataset-temperature-data

✓ Successfully indexed 3 dataset(s)
All datasets indexed successfully!
```

**Error Example:**

```
Reindexing datasets from data directory...
  ✓ Indexed: dataset-climate-2024
  • dataset-invalid: Could not read metadata

✓ Successfully indexed 1 dataset(s)

⚠ Encountered 1 error(s):
  • dataset-invalid: YAML parsing error
```

**Performance:**

- ~100ms per 100 datasets (typical)
- ~2-3s for 1000 datasets
- Automatic index optimization after completion

**Exit Codes:**

- `0`: All datasets indexed successfully
- `1`: One or more errors encountered

**When to use:**

- After bulk dataset imports
- Search results missing or outdated
- After running `auth clear`
- After manual YAML edits

**See Also:**

- [Search & Autocomplete](../architecture/search-and-autocomplete.md#search-index-maintenance)

---

## Diagnostic Commands

### `doctor`

**Syntax:**

```bash
hei-datahub doctor [OPTIONS]
```

**Description:**

Run system health checks and diagnostics for the application. Verifies workspace setup, database connectivity, and configuration.

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--data-dir PATH` | Path | Override data directory | Platform-specific |

**Output Example:**

```
🔍 Hei-DataHub System Diagnostics

[1/5] Workspace directories exist .................. ✓ PASS
      Config:  ~/.config/hei-datahub/
      Cache:   ~/.cache/hei-datahub/
      Data:    ~/.local/share/Hei-DataHub/

[2/5] Database accessible .......................... ✓ PASS
      Path: ~/.local/share/Hei-DataHub/db.sqlite
      Size: 2.3 MB

[3/5] Search index healthy ......................... ✓ PASS
      Indexed: 42 datasets
      FTS5: Enabled

[4/5] Configuration valid .......................... ✓ PASS
      Config: ~/.config/hei-datahub/config.toml

[5/5] Permissions correct .......................... ✓ PASS
      All directories writable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ System health: GOOD
```

**Exit Codes:**

- `0`: All checks passed
- `1`: One or more issues detected

---

### `paths`

**Syntax:**

```bash
hei-datahub paths
```

**Description:**

Show diagnostic information about application paths and directories.

**Output Example:**

```
📁 Hei-DataHub Path Information

Config Directory:
  ~/.config/hei-datahub/

Cache Directory:
  ~/.cache/hei-datahub/

Data Directory:
  ~/.local/share/Hei-DataHub/

Database:
  ~/.local/share/Hei-DataHub/db.sqlite

Log Directory:
  ~/.cache/hei-datahub/logs/

Follows XDG Base Directory Specification: ✓ Yes
```

**Exit Codes:**

- `0`: Always succeeds

---

## System Commands

### `update`

**Syntax:**

```bash
hei-datahub update [OPTIONS]
```

**Description:**

Update Hei-DataHub to the latest version using atomic update strategy. **Never breaks existing installation** - rolls back on failure.

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--branch NAME` | String | Git branch to install | Interactive prompt |
| `--force` | Flag | Skip preflight safety checks | `false` |
| `--check` | Flag | Check installation health | `false` |
| `--repair` | Flag | Repair broken installation | `false` |

**Examples:**

```bash
# Interactive update (recommended)
hei-datahub update

# Update from specific branch
hei-datahub update --branch main

# Check installation health
hei-datahub update --check

# Repair broken installation
hei-datahub update --repair
```

**Interactive Flow:**

```
🔄 Hei-DataHub Update

Current version: 0.59.0-beta
Checking for updates...

Available branches:
  [1] main (stable)
  [2] release/0.60-beta (latest)
  [3] dev (experimental)

Select branch [1-3]: 2

Downloading release/0.60-beta...
Installing to temporary location...
Running tests...
✓ All tests passed

Atomically replacing current installation...
✓ Update complete!

New version: 0.60.0-beta
Restart required.
```

**Atomic Update Process:**

1. Download new version to temp location
2. Install and test in isolation
3. If successful: Atomically swap with current version
4. If failed: Rollback (current version untouched)

**Exit Codes:**

- `0`: Update successful
- `1`: Update failed (rollback performed)
- `2`: No update needed

**Platform-Specific:**

- **Linux:** Uses `linux_update.py`
- **Windows:** Uses `windows_update.py`
- **macOS:** Uses `macos_update.py`

---

## Desktop Integration Commands

**Linux only.** Manage desktop shortcuts and icon installation.

### `desktop install`

**Syntax:**

```bash
hei-datahub desktop install [OPTIONS]
```

**Description:**

Install desktop integration (`.desktop` launcher and application icons).

**Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--force` | Flag | Force reinstall if already installed | `false` |
| `--no-cache-refresh` | Flag | Skip refreshing icon caches | `false` |

**Examples:**

```bash
# Install desktop integration
hei-datahub desktop install

# Force reinstall
hei-datahub desktop install --force
```

**What it installs:**

- `~/.local/share/applications/hei-datahub.desktop` - Application launcher
- `~/.local/share/icons/hicolor/*/apps/hei-datahub.png` - Icons (multiple sizes)
- Updates desktop icon cache

**Exit Codes:**

- `0`: Installation successful
- `1`: Installation failed

---

### `desktop uninstall`

**Syntax:**

```bash
hei-datahub desktop uninstall
```

**Description:**

Remove desktop integration (launcher and icons).

**What it removes:**

- `.desktop` file
- All installed icons
- Updates icon cache

**Exit Codes:**

- `0`: Uninstallation successful
- `1`: Uninstallation failed

---

## Keybinding Commands

### `keymap export`

**Syntax:**

```bash
hei-datahub keymap export [OUTPUT]
```

**Description:**

Export current keybindings to a YAML file.

**Arguments:**

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `OUTPUT` | Path | Output file path | `~/.hei-datahub/keybindings.yaml` |

**Examples:**

```bash
# Export to default location
hei-datahub keymap export

# Export to custom file
hei-datahub keymap export ~/my-keybindings.yaml
```

**Output Example:**

```yaml
keybindings:
  global:
    quit: "q"
    help: "?"
    search: "/"
  search:
    next_result: "j"
    prev_result: "k"
    open: "enter"
```

**Exit Codes:**

- `0`: Export successful
- `1`: Export failed

---

### `keymap import`

**Syntax:**

```bash
hei-datahub keymap import INPUT
```

**Description:**

Import keybindings from a YAML file.

**Arguments:**

| Argument | Type | Description | Required |
|----------|------|-------------|----------|
| `INPUT` | Path | Input file path | Yes |

**Examples:**

```bash
# Import from file
hei-datahub keymap import ~/my-keybindings.yaml
```

**Exit Codes:**

- `0`: Import successful
- `1`: Import failed (invalid file or format)

---

## Exit Codes Summary

| Code | Meaning | Usage |
|------|---------|-------|
| `0` | Success | Command completed successfully |
| `1` | General error | Command failed, validation error, or user abort |
| `2` | Usage error | Invalid arguments or missing required options |

---

## Environment Variables

### Optional Overrides

| Variable | Purpose | Example |
|----------|---------|---------|
| `WEBDAV_URL` | WebDAV base URL | `https://heibox.uni-heidelberg.de/seafdav` |
| `WEBDAV_USERNAME` | Username (password auth) | `user@example.com` |
| `WEBDAV_TOKEN` | WebDAV token | `abc123...` |
| `WEBDAV_PASSWORD` | WebDAV password | `mypassword` |
| `WEBDAV_LIBRARY` | Library/folder name | `my-datasets` |
| `HEI_DATAHUB_DATA_DIR` | Override data directory | `/custom/path` |
| `HEI_DATAHUB_LOG_LEVEL` | Logging level | `DEBUG`, `INFO`, `WARNING` |

**Note:** Using environment variables for credentials is **less secure** than keyring storage. Use only for testing or CI/CD environments.

---

## Configuration Files

### TOML Config

**Location:** `~/.config/hei-datahub/config.toml`

**Structure:**

```toml
[auth]
method = "token"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "-"
library = "my-datasets"
stored_in = "keyring"
key_id = "webdav:token:-@heibox.uni-heidelberg.de"

[sync]
enabled = true
interval_seconds = 300
on_startup = true

[ui]
theme = "default"
debounce_ms = 300

[search]
max_results = 50
```

---

## Troubleshooting

### Common Issues

#### "No keyring backend available"

**Symptom:** `auth setup` fails with keyring error.

**Solution:**

```bash
# Install GNOME Keyring
sudo apt install gnome-keyring

# Or use environment variables (less secure)
hei-datahub auth setup --store env
```

#### "Connection timeout"

**Symptom:** `auth doctor` times out.

**Solutions:**

```bash
# Increase timeout
hei-datahub auth doctor --timeout 15

# Check network
ping heibox.uni-heidelberg.de

# Check VPN if required
```

#### "Search index out of sync"

**Symptom:** Search shows outdated results.

**Solution:**

```bash
# Rebuild index
hei-datahub reindex
```

---

## Examples & Workflows

### First-Time Setup

```bash
# 1. Install (via UV)
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# 2. Configure authentication
hei-datahub auth setup

# 3. Verify setup
hei-datahub auth doctor

# 4. Launch TUI
hei-datahub
```

### Daily Usage

```bash
# Launch TUI (most common)
hei-datahub

# Check for updates
hei-datahub update

# Rebuild index after changes
hei-datahub reindex
```

### Troubleshooting

```bash
# Run full diagnostics
hei-datahub doctor
hei-datahub auth doctor

# Check paths
hei-datahub paths

# Clear and reconfigure
hei-datahub auth clear --force
hei-datahub auth setup
```

### Automation/Scripting

```bash
# Non-interactive setup
hei-datahub auth setup \
  --url "$WEBDAV_URL" \
  --token "$WEBDAV_TOKEN" \
  --library "$LIBRARY_NAME" \
  --non-interactive \
  --force

# JSON output for parsing
hei-datahub auth doctor --json | jq '.checks[] | select(.status=="fail")'

# Automated reindex
hei-datahub reindex || echo "Reindex failed"
```

---

## Related Documentation

- **[Authentication & Sync](../architecture/auth-and-sync.md)** - Detailed auth documentation
- **[Search & Autocomplete](../architecture/search-and-autocomplete.md)** - Search system details
- **[Security & Privacy](../architecture/security-privacy.md)** - Security best practices
- **[Architecture Overview](../architecture/overview.md)** - System architecture
- **[Contributing Workflow](../contributing/workflow.md)** - Development guide

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│  HEI-DATAHUB CLI QUICK REFERENCE                            │
├─────────────────────────────────────────────────────────────┤
│  LAUNCH TUI                                                 │
│    hei-datahub                                              │
│                                                             │
│  AUTHENTICATION                                             │
│    hei-datahub auth setup      # Configure WebDAV          │
│    hei-datahub auth status     # Show config               │
│    hei-datahub auth doctor     # Test connection           │
│    hei-datahub auth clear      # Remove credentials        │
│                                                             │
│  SEARCH & INDEX                                             │
│    hei-datahub reindex         # Rebuild search index      │
│                                                             │
│  DIAGNOSTICS                                                │
│    hei-datahub doctor          # System health             │
│    hei-datahub paths           # Show directories          │
│                                                             │
│  SYSTEM                                                     │
│    hei-datahub update          # Update to latest          │
│    hei-datahub --version       # Show version              │
│                                                             │
│  DESKTOP (Linux)                                            │
│    hei-datahub desktop install   # Add launcher            │
│    hei-datahub desktop uninstall # Remove launcher         │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
