# CLI Reference

**(req. Hei-DataHub 0.59-beta or later)**

Complete reference for Hei-DataHub command-line interface.

---

## Basic Usage

```bash
hei-datahub [OPTIONS] [COMMAND]
```

---

## Global Options

### `--version`

Show version number and exit.

```bash
hei-datahub --version
# Output: Hei-DataHub 0.59.0-beta
```

### `--version-info`

Show detailed version and system information.

```bash
hei-datahub --version-info
```

**Output example:**
```
╔══════════════════════════════════════════════════════════╗
║               Hei-DataHub Version Info                   ║
╚══════════════════════════════════════════════════════════╝

Version:        0.59.0-beta
Codename:       Privacy
Release Date:   2025-10-25
Compatibility:  Hei-DataHub v0.59.x (beta)

Python:         3.11.5
Platform:       Linux-6.5.0-15-generic-x86_64
Repository:     https://github.com/0xpix/Hei-DataHub
Documentation:  https://0xpix.github.io/Hei-DataHub/
```

### `--data-dir <PATH>` ⭐ New in v0.58.1

Override the data directory location for this session.

**Precedence (highest to lowest):**
1. `--data-dir` CLI flag
2. `HEIDATAHUB_DATA_DIR` environment variable
3. OS-specific default

**Examples:**

```bash
# Linux
hei-datahub --data-dir ~/.local/share/Hei-DataHub

# macOS
hei-datahub --data-dir ~/Library/Application\ Support/Hei-DataHub

# Windows (PowerShell)
hei-datahub --data-dir "$env:LOCALAPPDATA\Hei-DataHub"

# Windows (CMD)
hei-datahub --data-dir %LOCALAPPDATA%\Hei-DataHub

# Custom location
hei-datahub --data-dir /mnt/shared/team-datahub
```

**Use cases:**
- Testing with different data directories
- Using a network/shared drive
- Per-project data isolation
- Temporary override without changing environment variables

### `--set KEY=VALUE`

Set configuration override for this session. Can be used multiple times.

```bash
hei-datahub --set search.debounce_ms=200 --set ui.theme=dark
```

---

---

## Commands

### `hei-datahub` (default)

Launch the TUI (Terminal User Interface).

```bash
hei-datahub
```

**What it does:**
- Initializes local cache directory (~/.cache/hei-datahub/)
- Syncs index from Heibox cloud storage
- Launches interactive TUI

**Keyboard shortcuts:**
- See [Customize Keybindings](../how-to/08-customize-keybindings.md) for full reference

---

### `hei-datahub auth` ⭐ New in v0.59-beta

Manage Heibox/WebDAV authentication credentials.

#### `hei-datahub auth setup`

Interactive wizard to configure Heibox/WebDAV credentials.

```bash
hei-datahub auth setup
```

**Prompts:**

1. 📍 **Server URL:** `https://heibox.uni-heidelberg.de`
2. 👤 **Username:** Your Heibox username
3. 🔐 **Password:** Your WebDAV password
4. 📁 **Library ID:** UUID from Heibox library settings

**Example session:**

```
📍 Enter your Heibox/WebDAV server URL
   Example: https://heibox.uni-heidelberg.de
   → https://heibox.uni-heidelberg.de

👤 Enter your Heibox username
   → john.doe

🔐 Enter your WebDAV password
   (This is your WebDAV-specific password, not your web login password)
   → ••••••••••••

📁 Enter your Heibox library ID
   Find this in: Library Settings → Advanced
   → abc123-def456-ghi789

🔍 Testing connection...
✅ Connection successful!
✅ Credentials saved to system keyring

🎯 Setup complete! You can now use hei-datahub to sync with Heibox.
```

**What it does:**
- Validates each input
- Tests WebDAV connection
- Saves credentials to system keyring (encrypted)
- Updates config file with server URL and library ID

#### `hei-datahub auth status`

Check current Heibox connection status.

```bash
hei-datahub auth status
```

**Output examples:**

```
✅ Connected to Heibox
   Server: https://heibox.uni-heidelberg.de
   Username: john.doe
   Library: abc123-def456-ghi789
   Status: Online
```

```
⚠ Heibox configured but connection failed
   Server: https://heibox.uni-heidelberg.de
   Username: john.doe
   Error: Authentication failed (401)

   Run 'hei-datahub auth doctor' for troubleshooting
```

```
○ Heibox not configured
   Run 'hei-datahub auth setup' to configure
```

#### `hei-datahub auth doctor`

Troubleshoot Heibox connection issues.

```bash
hei-datahub auth doctor
```

**What it checks:**

- ✓ Credentials present in keyring
- ✓ Server URL reachable
- ✓ Authentication successful
- ✓ Library ID valid
- ✓ Read/write permissions
- ✓ Network connectivity
- ✓ TLS/SSL certificate valid

**Example output:**

```
╔══════════════════════════════════════════════════════════╗
║          Heibox Connection Diagnostics                   ║
╚══════════════════════════════════════════════════════════╝

✓ Credentials: Found in system keyring
✓ Server: https://heibox.uni-heidelberg.de reachable
✓ Authentication: Successful (200 OK)
✓ Library: abc123-def456-ghi789 accessible
✓ Permissions: Read and write OK
✓ Network: HTTPS connection established
✓ Certificate: Valid until 2026-01-15

────────────────────────────────────────────────────────────
✓ All checks passed — connection healthy
```

**Exit codes:**
- `0`: Connection healthy
- `1`: Credentials missing
- `2`: Server unreachable
- `3`: Authentication failed
- `4`: Library not accessible
- `5`: Permission denied

#### `hei-datahub auth clear`

Remove Heibox credentials from system keyring.

```bash
hei-datahub auth clear
```

**Prompts for confirmation:**

```
⚠ This will remove your Heibox credentials from the system keyring.
   You will need to run 'hei-datahub auth setup' again to reconnect.

Continue? [y/N]: y

✅ Credentials cleared successfully
```

**Use cases:**
- Switching to different account
- Troubleshooting authentication issues
- Uninstalling/cleanup

---

### `hei-datahub doctor`

Run comprehensive system diagnostics and health checks.

```bash
hei-datahub doctor
```

**Exit codes:**
- `0`: System healthy
- `1`: Directory missing or cannot be created
- `2`: Permission error
- `3`: Heibox connection failed

**Sample output:**

```
╔════════════════════════════════════════════════════════════╗
║          Hei-DataHub Doctor — System Diagnostics           ║
╚════════════════════════════════════════════════════════════╝

✓ System Information: Running on linux
  OS: linux (posix)
  Python: 3.11.5
  Platform: linux

✓ Cache Directory: Cache directory accessible
  /home/user/.cache/hei-datahub/ (OS default)
  ✓ Directory exists
  ✓ Read access
  ✓ Write access

✓ Heibox Connection: Connected and synced
  Server: https://heibox.uni-heidelberg.de
  Library: abc123-def456-ghi789
  Status: ☁ Synced (12 datasets)

✓ Database: Initialized (156.3 KB)
  12 indexed dataset(s)
  Last sync: 2 minutes ago

────────────────────────────────────────────────────────────
✓ All checks passed — system healthy
```

**What it checks:**
- OS and Python runtime information
- Cache directory access (read/write/create)
- Heibox connection status
- Database initialization and indexed count
- Last sync timestamp

**Use cases:**
- Troubleshooting connection issues
- Verifying installation after setup
- Checking permissions
- Diagnosing sync problems

---

### `hei-datahub reindex`

Rebuild the search index from Heibox cloud storage.

```bash
hei-datahub reindex
```

**When to use:**
- After team members add/edit datasets in Heibox
- If search results seem stale or incorrect
- Database corruption recovery
- Force full sync from cloud

**Output example:**

```
Reindexing datasets from data directory...
  ✓ Indexed: burned-area
  ✓ Indexed: land-cover
  ✓ Indexed: precipitation
  ✓ Indexed: testing-the-beta-version

✓ Successfully indexed 4 dataset(s)
All datasets indexed successfully!
```

**Error handling:**

If some datasets fail:
```
Reindexing datasets from data directory...
  ✓ Indexed: burned-area
  ✓ Indexed: land-cover

⚠ Encountered 2 error(s):
  • precipitation: Could not read metadata
  • testing: YAML parse error
```

---

### `hei-datahub paths`

Show diagnostic information about application paths.

```bash
hei-datahub paths
```

**Output example:**

```
Hei-DataHub Paths Diagnostic
============================================================

Installation Mode:
  ✓ Installed package (standalone)

XDG Base Directories:
  XDG_CONFIG_HOME: /home/user/.config
  XDG_DATA_HOME:   /home/user/.local/share
  XDG_CACHE_HOME:  /home/user/.cache
  XDG_STATE_HOME:  /home/user/.local/state

Application Paths:
  Config:    /home/user/.config/hei-datahub
    Exists:  ✓
  Data:      /home/user/.local/share/Hei-DataHub/datasets
    Exists:  ✓
    Datasets: 4
  Cache:     /home/user/.cache/hei-datahub
    Exists:  ✓
  State:     /home/user/.local/state/hei-datahub
    Exists:  ✓
  Logs:      /home/user/.local/state/hei-datahub/logs
    Exists:  ✓

Important Files:
  Database:  /home/user/.local/share/Hei-DataHub/db.sqlite
    Exists:  ✓
    Size:    48.5 KB
  Schema:    /home/user/.local/share/Hei-DataHub/schema.json
    Exists:  ✓
  Config:    /home/user/.config/hei-datahub/config.json
    Exists:  ✓
  Keymap:    /home/user/.config/hei-datahub/keymap.json
    Exists:  ✗

Environment Variables:
  XDG_CONFIG_HOME: <not set>
  XDG_DATA_HOME:   <not set>
  XDG_CACHE_HOME:  <not set>
  XDG_STATE_HOME:  <not set>
============================================================
```

**Use cases:**
- Verifying installation paths
- Debugging directory creation issues
- Checking environment variable overrides
- Documentation/support requests

---

### `hei-datahub update`

Update Hei-DataHub to the latest version from the repository.

```bash
hei-datahub update
# or specify branch:
hei-datahub update --branch main
```

**Options:**
- `--branch`: Git branch to install from (default: current beta branch)

**Requirements:**
- Must be installed via `uv tool install`
- Git credentials configured (SSH or token)

---

### `hei-datahub keymap`

Manage custom keybindings.

#### Export keybindings

```bash
hei-datahub keymap export [output_file]
```

**Examples:**

```bash
# Export to default location
hei-datahub keymap export

# Export to custom file
hei-datahub keymap export ~/my-keybindings.yaml
```

**Output format (YAML):**

```yaml
keybindings:
  global:
    quit: "q"
    help: "?"
    search: "/"
  home:
    new_dataset: "n"
    refresh: "r"
```

#### Import keybindings

```bash
hei-datahub keymap import <input_file>
```

**Example:**

```bash
hei-datahub keymap import ~/my-keybindings.yaml
```

---

## Environment Variables

### `HEIDATAHUB_DATA_DIR` ⭐ New in v0.58.1

Set default data directory location. Overrides OS default but is overridden by `--data-dir`.

**Examples:**

```bash
# Linux/macOS (add to ~/.bashrc or ~/.zshrc)
export HEIDATAHUB_DATA_DIR="$HOME/my-datahub"

# Windows PowerShell (add to profile)
$env:HEIDATAHUB_DATA_DIR = "C:\DataHub"

# Windows Command Prompt
set HEIDATAHUB_DATA_DIR=C:\DataHub
```

### XDG Base Directory Variables

Control config, cache, and state locations (all platforms):

```bash
# Config directory
export XDG_CONFIG_HOME="$HOME/.config"

# Data directory (Linux only - use HEIDATAHUB_DATA_DIR for cross-platform)
export XDG_DATA_HOME="$HOME/.local/share"

# Cache directory
export XDG_CACHE_HOME="$HOME/.cache"

# State directory (logs, outbox)
export XDG_STATE_HOME="$HOME/.local/state"
```

---

## OS-Specific Defaults

### Linux

```
Data:   ~/.local/share/Hei-DataHub
Config: ~/.config/hei-datahub
Cache:  ~/.cache/hei-datahub
State:  ~/.local/state/hei-datahub
```

### macOS

```
Data:   ~/Library/Application Support/Hei-DataHub
Config: ~/.config/hei-datahub
Cache:  ~/.cache/hei-datahub
State:  ~/.local/state/hei-datahub
```

### Windows

```
Data:   %LOCALAPPDATA%\Hei-DataHub
        (typically C:\Users\<User>\AppData\Local\Hei-DataHub)
Config: %USERPROFILE%\.config\hei-datahub
Cache:  %USERPROFILE%\.cache\hei-datahub
State:  %USERPROFILE%\.local\state\hei-datahub
```

---

## Exit Codes

| Code | Command | Meaning |
|------|---------|---------|
| `0` | All | Success |
| `1` | `doctor` | Directory missing/uncreatable |
| `1` | `reindex` | One or more datasets failed to index |
| `2` | `doctor` | Permission error |
| `3` | `doctor` | Data present but unreadable/invalid |

---

## Common Workflows

### Quick health check

```bash
hei-datahub doctor
```

### Force reindex after external changes

```bash
hei-datahub reindex
```

### Use custom data directory temporarily

```bash
hei-datahub --data-dir /mnt/shared/team-data
```

### Persistent custom data directory

```bash
# Set once
export HEIDATAHUB_DATA_DIR="/mnt/shared/team-data"

# Use normally
hei-datahub
```

### Share keybindings with team

```bash
# Export your keybindings
hei-datahub keymap export keybindings.yaml

# Team members import
hei-datahub keymap import keybindings.yaml
```

---

## See Also

- [Getting Started](../getting-started/01-getting-started.md) — Installation guide
- [Navigation](../getting-started/02-navigation.md) — Keyboard shortcuts in TUI
- [Troubleshooting](../installation/troubleshooting.md) — Common issues and solutions
- [Data & SQL](11-data-and-sql.md) — Understanding the data model
