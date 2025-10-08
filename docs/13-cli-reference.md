# CLI Reference

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
# Output: Hei-DataHub 0.58.1-beta
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

Version:        0.58.1-beta
Codename:       Streamline
Release Date:   2025-10-08
Compatibility:  Hei-DataHub v0.58.x (beta)

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

## Commands

### `hei-datahub` (default)

Launch the TUI (Terminal User Interface).

```bash
hei-datahub
# or with data directory override:
hei-datahub --data-dir ~/my-data
```

**What it does:**
- Initializes workspace (creates directories if needed)
- Ensures database is created and indexed
- Launches interactive TUI

**Keyboard shortcuts:**
- See [Navigation Guide](02-navigation.md) for full keybindings

---

### `hei-datahub doctor` ⭐ New in v0.58.1

Run comprehensive system diagnostics and health checks.

```bash
hei-datahub doctor
# or with data directory override:
hei-datahub doctor --data-dir ~/my-data
```

**Exit codes:**
- `0`: System healthy
- `1`: Directory missing or cannot be created
- `2`: Permission error
- `3`: Data present but unreadable/invalid

**Sample output:**

```
╔════════════════════════════════════════════════════════════╗
║          Hei-DataHub Doctor — System Diagnostics           ║
╚════════════════════════════════════════════════════════════╝

✓ System Information: Running on linux
  OS: linux (posix)
  Python: 3.11.5
  Platform: linux

✓ Data Directory: Data directory accessible
  /home/user/.local/share/Hei-DataHub (OS default (linux))
  ✓ Directory exists
  ✓ Read access
  ✓ Write access

✓ Datasets: 4 dataset(s) available
  Found 4 dataset(s):
  ✓ burned-area
  ✓ land-cover
  ✓ precipitation
  ✓ testing-the-beta-version

✓ Database: Initialized (48.5 KB)
  4 indexed dataset(s)

✓ Migration: Not applicable (Linux)

✓ Filename Sanitation: Not applicable (not Windows)

────────────────────────────────────────────────────────────
✓ All checks passed — system healthy
```

**What it checks:**
- OS and Python runtime information
- Data directory resolution and access (read/write/create)
- Dataset count and metadata health
- Database initialization and indexed count
- Legacy path migration needs (Windows/macOS)
- Windows filename sanitation issues

**Use cases:**
- Troubleshooting "data not found" issues
- Verifying installation after setup
- Checking permissions before team deployment
- Diagnosing cross-platform issues

---

### `hei-datahub reindex`

Rebuild the search index from YAML metadata files.

```bash
hei-datahub reindex
```

**When to use:**
- After manually editing `metadata.yaml` files outside the TUI
- After git pull/merge that changed datasets
- If search results seem stale or incorrect
- Database corruption recovery

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

- [Getting Started](01-getting-started.md) — Installation guide
- [Navigation](02-navigation.md) — Keyboard shortcuts in TUI
- [Troubleshooting](installation/troubleshooting.md) — Common issues and solutions
- [Data & SQL](11-data-and-sql.md) — Understanding the data model
