# Data Seeding & Paths

Complete guide to understanding how Hei-DataHub manages data, where files live, and how first-run initialization works.

## Overview

Hei-DataHub follows the **XDG Base Directory Specification** (Linux standard) to organize configuration, data, cache, and logs in appropriate system locations.

## Path Organization

### XDG Base Directory Specification

The app uses these standardized base directories:

| XDG Variable | Default Linux Path | Purpose |
|--------------|-------------------|---------|
| `XDG_CONFIG_HOME` | `~/.config` | User-specific configuration |
| `XDG_DATA_HOME` | `~/.local/share` | User-specific data files |
| `XDG_CACHE_HOME` | `~/.cache` | User-specific cache files |
| `XDG_STATE_HOME` | `~/.local/state` | User-specific state files (logs, history) |

**Why XDG?**
- **Standard**: Follows Linux/Unix conventions
- **Clean**: Separates concerns (config vs data vs logs)
- **Discoverable**: Other tools know where to look
- **Backup-friendly**: Easy to identify what to back up

### Hei-DataHub Directory Structure

```
~/.config/hei-datahub/           # Configuration
├── config.json                  # User settings
└── keymap.json                  # Custom keybindings

~/.local/share/hei-datahub/      # Application data
├── db.sqlite                    # Dataset index (SQLite FTS5)
├── schema.json                  # Metadata schema definition
├── datasets/                    # Your datasets
│   ├── burned-area/
│   │   ├── metadata.yaml        # Dataset metadata
│   │   └── README.md            # (optional)
│   ├── land-cover/
│   ├── precipitation/
│   └── your-custom-dataset/
└── assets/
    └── templates/               # Default templates

~/.cache/hei-datahub/            # Cache (reserved for future use)

~/.local/state/hei-datahub/      # State & logs
├── logs/
│   └── app.log                  # Application logs
└── outbox/                      # Failed PR operations
```

## First-Run Initialization

### What Happens Automatically

When you run `hei-datahub` for the first time after installation, the app:

1. **Creates XDG directories** (if missing)
2. **Copies packaged defaults** to user-writable locations:
   - 4 example datasets (`burned-area`, `land-cover`, `precipitation`, `testing-the-beta-version`)
   - `schema.json` (metadata schema)
   - Default templates
3. **Initializes SQLite database** (`db.sqlite`)
4. **Indexes datasets** into the database
5. **Creates default config** (if missing)

**Output on first run:**
```
✓ Initialized schema at /home/user/.local/share/hei-datahub/schema.json
✓ Initialized 4 datasets in /home/user/.local/share/hei-datahub/datasets
  Indexing datasets...
  ✓ Indexed 4 datasets
✓ Initialized templates in /home/user/.local/share/hei-datahub/assets
```

### Idempotence

Subsequent runs are **no-ops**:
- Existing files are **never overwritten**
- Missing directories are created
- No duplicate datasets are copied

**This means:**
- ✅ Safe to run multiple times
- ✅ User edits are preserved
- ✅ Deleted files won't be restored (unless you manually trigger `initialize_workspace()`)

## Installation Modes

Hei-DataHub automatically detects how it's running and adjusts paths accordingly.

### Standalone Mode (Installed Package)

**Detection:** Running from `site-packages` or `.local/share/uv`

**Uses XDG paths:**
```
Config:  ~/.config/hei-datahub/
Data:    ~/.local/share/hei-datahub/
Cache:   ~/.cache/hei-datahub/
State:   ~/.local/state/hei-datahub/
```

**How to install:**
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"
```

### Development Mode (Repository)

**Detection:** Running from repository with `src/mini_datahub/` and `pyproject.toml`

**Uses repo paths:**
```
Config:  /path/to/Hei-DataHub/
Data:    /path/to/Hei-DataHub/data/
Cache:   /path/to/Hei-DataHub/.cache/
State:   /path/to/Hei-DataHub/
DB:      /path/to/Hei-DataHub/db.sqlite
```

**How to run:**
```bash
cd /path/to/Hei-DataHub
python -m mini_datahub
# or
hei-datahub  # (if installed with `pip install -e .`)
```

## Diagnostic Command

Check where the app is reading/writing files:

```bash
hei-datahub paths
```

**Example output:**
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
  Data:      /home/user/.local/share/hei-datahub/datasets
    Exists:  ✓
    Datasets: 4
  Cache:     /home/user/.cache/hei-datahub
    Exists:  ✓
  State:     /home/user/.local/state/hei-datahub
    Exists:  ✓
  Logs:      /home/user/.local/state/hei-datahub/logs
    Exists:  ✓

Important Files:
  Database:  /home/user/.local/share/hei-datahub/db.sqlite
    Exists:  ✓
    Size:    12.5 KB
  Schema:    /home/user/.local/share/hei-datahub/schema.json
    Exists:  ✓
  Config:    /home/user/.config/hei-datahub/config.json
    Exists:  ✓
  Keymap:    /home/user/.config/hei-datahub/keymap.json
    Exists:  ✓

Environment Variables:
  XDG_CONFIG_HOME: <not set>
  XDG_DATA_HOME: <not set>
  XDG_CACHE_HOME: <not set>
  XDG_STATE_HOME: <not set>

============================================================
```

## Customizing Paths

### Override XDG Directories

You can customize where the app stores files by setting XDG environment variables:

```bash
# Custom config location
export XDG_CONFIG_HOME=~/my-config
hei-datahub  # Uses ~/my-config/hei-datahub/

# Custom data location (e.g., external drive)
export XDG_DATA_HOME=/mnt/external/share
hei-datahub  # Uses /mnt/external/share/hei-datahub/

# Custom cache location
export XDG_CACHE_HOME=~/my-cache
hei-datahub  # Uses ~/my-cache/hei-datahub/
```

**Make it persistent:**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export XDG_DATA_HOME=/mnt/external/share' >> ~/.bashrc
source ~/.bashrc
```

### Use Case: Move Datasets to External Drive

If your datasets are large:

```bash
# 1. Set custom data location
export XDG_DATA_HOME=/mnt/external/share

# 2. (Optional) Move existing data
mv ~/.local/share/hei-datahub /mnt/external/share/

# 3. Run app
hei-datahub
```

## Managing Datasets

### Add a New Dataset

```bash
# Option 1: TUI (interactive)
hei-datahub
# Press 'a' to add dataset

# Option 2: Manual (advanced)
mkdir -p ~/.local/share/hei-datahub/datasets/my-dataset
cat > ~/.local/share/hei-datahub/datasets/my-dataset/metadata.yaml <<EOF
id: my-dataset
dataset_name: My Dataset
description: Description of my dataset
source: https://example.com/data
storage_location: local
date_created: "2025-10-07"
EOF

# Reindex
hei-datahub reindex
```

### Remove a Dataset

```bash
# Delete directory
rm -rf ~/.local/share/hei-datahub/datasets/my-dataset

# Reindex
hei-datahub reindex
```

### Backup Datasets

```bash
# Backup all datasets
tar -czf hei-datahub-backup-$(date +%Y%m%d).tar.gz \
  ~/.config/hei-datahub \
  ~/.local/share/hei-datahub

# Restore
tar -xzf hei-datahub-backup-20251007.tar.gz -C ~/
hei-datahub reindex
```

## Database Management

### Rebuild Database

If the database gets corrupted or out of sync:

```bash
# Remove database
rm ~/.local/share/hei-datahub/db.sqlite

# Reindex (recreates database)
hei-datahub reindex
```

### Database Location

- **Standalone:** `~/.local/share/hei-datahub/db.sqlite`
- **Dev mode:** `<repo>/db.sqlite`

The database is a **SQLite file** with FTS5 (Full-Text Search) extension.

**Inspect it:**
```bash
sqlite3 ~/.local/share/hei-datahub/db.sqlite

sqlite> .tables
datasets_fts  datasets_store

sqlite> SELECT id, dataset_name FROM datasets_store;
burned-area|Burned Area
land-cover|Land Cover
...

sqlite> .quit
```

## Legacy Migration (Pre-v0.58)

If you used Hei-DataHub before v0.58 (which used `~/.hei-datahub/`):

### Automatic Migration

**Not implemented yet.** Manual migration required.

### Manual Migration

```bash
# 1. Backup old data
cp -r ~/.hei-datahub ~/hei-datahub-backup

# 2. Copy datasets
mkdir -p ~/.local/share/hei-datahub/datasets
cp -r ~/.hei-datahub/data/* ~/.local/share/hei-datahub/datasets/

# 3. Copy config (if exists)
mkdir -p ~/.config/hei-datahub
cp ~/.hei-datahub/.datahub_config.json ~/.config/hei-datahub/config.json

# 4. Remove old directory
rm -rf ~/.hei-datahub

# 5. Reindex
hei-datahub reindex
```

## Troubleshooting

### No Datasets Appear After Install

**Problem:** App shows "No datasets (0 total)"

**Diagnostic:**
```bash
hei-datahub paths
# Check:
# - Data directory exists?
# - Datasets count shows 0?
```

**Solution:**
```bash
# Manually trigger initialization
python -c "from mini_datahub.infra.paths import initialize_workspace; initialize_workspace()"

# Or reinstall
uv tool uninstall hei-datahub
rm -rf ~/.local/share/hei-datahub
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"
hei-datahub
```

### Database Locked Error

**Problem:** `sqlite3.OperationalError: database is locked`

**Cause:** Another instance of the app is running

**Solution:**
```bash
# Kill other instances
pkill -f hei-datahub

# Or restart
hei-datahub
```

### Permission Denied

**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Fix ownership
chmod -R u+w ~/.config/hei-datahub \
             ~/.local/share/hei-datahub \
             ~/.local/state/hei-datahub
```

### Wrong Directory Used

**Problem:** App is using repo paths instead of XDG paths (or vice versa)

**Diagnostic:**
```bash
hei-datahub paths
# Check "Installation Mode"
```

**Solution:**

If in **standalone mode** but using repo paths:
```bash
# Check if running from repo directory
pwd
# If in /path/to/Hei-DataHub, cd elsewhere:
cd ~
hei-datahub
```

If in **dev mode** but want standalone:
```bash
# Install properly
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"

# Run from outside repo
cd ~
hei-datahub
```

## Advanced: Programmatic Access

Access paths from Python:

```python
from mini_datahub.infra.paths import (
    CONFIG_DIR,
    DATA_DIR,
    CACHE_DIR,
    STATE_DIR,
    DB_PATH,
    SCHEMA_JSON,
    CONFIG_FILE,
    KEYMAP_FILE,
)

print(f"Datasets: {DATA_DIR}")
print(f"Database: {DB_PATH}")

# Check if running in dev mode
from mini_datahub.infra.paths import _is_dev_mode, _is_installed_package

if _is_installed_package():
    print("Running as installed package")
elif _is_dev_mode():
    print("Running in development mode")
```

## Related Documentation

- [UV Installation](./uv-install.md) - Install Hei-DataHub
- [Troubleshooting](./troubleshooting.md) - Common issues
- [Configuration](../12-config.md) - Configure the app

## FAQ

**Q: Can I change the app name from "hei-datahub" to something else?**

A: Yes, but you'd need to fork and modify paths.py. The app uses `"hei-datahub"` as the directory name consistently.

**Q: Can I have multiple isolated installations?**

A: Yes, use different XDG paths:
```bash
XDG_DATA_HOME=~/project-a/.local/share hei-datahub
XDG_DATA_HOME=~/project-b/.local/share hei-datahub
```

**Q: What happens if I delete `~/.local/share/hei-datahub/datasets`?**

A: The app will recreate it with the 4 default example datasets on next run.

**Q: Can I disable automatic seeding?**

A: Not currently. The app always ensures base directories exist and seeds defaults if `datasets/` is empty.

**Q: Are the example datasets required?**

A: No. You can delete them and add your own:
```bash
rm -rf ~/.local/share/hei-datahub/datasets/*
# Add your own datasets
hei-datahub reindex
```

---

**Version:** v0.58.0-beta
**Last Updated:** 2025-10-07
