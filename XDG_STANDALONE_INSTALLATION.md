# 🎉 COMPLETE SOLUTION: XDG-Compliant Standalone Installation

## What You Asked For

> "i want to install the app without having a repo at all, like a new app that gets the data config assets everything"
>
> "i don't want to cd anywhere, i just want to type hei-datahub and it runs it doesn't matter from where"

## ✅ DONE! Here's What Changed

### XDG Base Directory Specification (Linux Standard)

Your app now follows proper Linux conventions:

```
~/.config/hei-datahub/           # Config & keybindings
├── config.json
└── keymap.json

~/.local/share/hei-datahub/      # DB, datasets, schema, assets
├── db.sqlite
├── schema.json
├── datasets/
│   ├── burned-area/
│   ├── land-cover/
│   ├── precipitation/
│   └── testing-the-beta-version/
└── assets/
    └── templates/

~/.cache/hei-datahub/            # Caches

~/.local/state/hei-datahub/      # Logs & outbox
├── logs/
└── outbox/
```

### How It Works

1. **Install detection**: Checks if running from UV/pip install (not repo)
2. **Standalone mode**: Uses XDG directories, no repo needed
3. **Works everywhere**: Type `hei-datahub` from ANY directory
4. **First run initialization**: Auto-copies all 4 datasets, schema, templates

## Installation & Testing

### Step 1: Clean Reinstall

```bash
# Remove old installations
uv tool uninstall hei-datahub
rm -rf ~/.hei-datahub ~/.config/hei-datahub ~/.local/share/hei-datahub ~/.cache/hei-datahub ~/.local/state/hei-datahub

# Install fresh from GitHub
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

### Step 2: Run from ANYWHERE

```bash
# From home
cd ~
hei-datahub

# From /tmp
cd /tmp
hei-datahub

# From your Documents
cd ~/Documents
hei-datahub

# From your repo (if you have one)
cd /home/pix/Github/Hei-DataHub
hei-datahub

# ALL WORK THE SAME! ✅
```

### Step 3: Verify XDG Directories

```bash
# Check all directories were created
ls ~/.config/hei-datahub/
ls ~/.local/share/hei-datahub/
ls ~/.local/share/hei-datahub/datasets/
ls ~/.cache/hei-datahub/
ls ~/.local/state/hei-datahub/

# Count datasets
ls ~/.local/share/hei-datahub/datasets/ | wc -l
# Should show: 4

# Check database
sqlite3 ~/.local/share/hei-datahub/db.sqlite "SELECT id FROM datasets_store;"
# Should list all 4 datasets
```

## What You'll See

### First Run

```bash
hei-datahub
# Output:
# ✓ Initialized schema at /home/pix/.local/share/hei-datahub/schema.json
# ✓ Initialized 4 datasets in /home/pix/.local/share/hei-datahub/datasets
# ✓ Initialized templates in /home/pix/.local/share/hei-datahub/assets
# [TUI launches with 4 datasets]
```

### Subsequent Runs

```bash
hei-datahub
# [TUI launches immediately - no initialization messages]
```

### In the TUI

```
Hei-DataHub v0.58.0-beta

Datasets (4):
  □ burned-area
  □ land-cover
  □ precipitation
  □ testing-the-beta-version

Press ? for help
```

## Benefits

### For Users

✅ **Zero configuration**: Just install and run
✅ **Works everywhere**: No cd needed, run from any directory
✅ **No repo clutter**: Completely standalone
✅ **Clean organization**: Config, data, cache, state properly separated
✅ **Linux standard**: Follows XDG Base Directory Specification

### For You (Developer)

✅ **Dev mode still works**: Repository automatically detected
✅ **No breaking changes**: All existing functionality preserved
✅ **Easy testing**: Just `uv tool install` from GitHub
✅ **Proper packaging**: All 4 datasets included

## Directory Structure Breakdown

| XDG Directory | Hei-DataHub Files | Purpose |
|---------------|-------------------|---------|
| `~/.config/hei-datahub/` | config.json, keymap.json | User preferences, keybindings |
| `~/.local/share/hei-datahub/` | db.sqlite, datasets/, schema.json, assets/ | Application data, persistent storage |
| `~/.cache/hei-datahub/` | cache files | Temporary cached data |
| `~/.local/state/hei-datahub/` | logs/, outbox/ | Log files, failed operations |

## Environment Variables (Optional)

You can override XDG directories if needed:

```bash
# Custom config location
export XDG_CONFIG_HOME=~/my-config
hei-datahub  # Uses ~/my-config/hei-datahub/

# Custom data location
export XDG_DATA_HOME=~/my-data
hei-datahub  # Uses ~/my-data/hei-datahub/
```

## Development Mode

If you're working on the code:

```bash
cd /home/pix/Github/Hei-DataHub
python -m mini_datahub
# Auto-detects dev mode, uses repo directories
```

## Migration from Old Version

If you had the old `~/.hei-datahub/` installation:

```bash
# Old data (if you want to keep it)
cp -r ~/.hei-datahub/data/* ~/.local/share/hei-datahub/datasets/

# Old config (if exists)
cp ~/.hei-datahub/.datahub_config.json ~/.config/hei-datahub/config.json

# Clean up old directory
rm -rf ~/.hei-datahub
```

## Quick Test (One-Liner)

```bash
# Complete fresh install and test
uv tool uninstall hei-datahub 2>/dev/null; \
rm -rf ~/.config/hei-datahub ~/.local/share/hei-datahub ~/.cache/hei-datahub ~/.local/state/hei-datahub; \
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x" && \
cd ~ && \
hei-datahub
```

## Troubleshooting

### "No datasets found"

Check if initialization ran:
```bash
ls ~/.local/share/hei-datahub/datasets/
# Should show 4 directories
```

If empty, manually trigger:
```bash
python -c "from mini_datahub.infra.paths import initialize_workspace; initialize_workspace()"
```

### "Database error"

Check database location:
```bash
ls -lh ~/.local/share/hei-datahub/db.sqlite
# Should exist and have size > 0
```

### "Config not found"

Directories created on first run:
```bash
hei-datahub  # First run creates all directories
```

## Summary

**Before:**
- ❌ Had to cd to specific directory
- ❌ Needed repository files
- ❌ Mixed everything in one location
- ❌ Only 1 template dataset

**After:**
- ✅ Run from ANYWHERE
- ✅ No repository needed
- ✅ XDG-compliant organization
- ✅ All 4 datasets included
- ✅ Completely standalone

---

**Status:** ✅ IMPLEMENTED and pushed to GitHub
**Commit:** 89a39d9 - "feat(install): XDG-compliant standalone installation"
**Branch:** chore/uv-install-data-desktop-v0.58.x

**Next:** Install and enjoy! Just type `hei-datahub` from anywhere! 🚀
