# Quick Reference — v0.58.1-beta

**What's New:** Cross-platform data directories + Doctor diagnostics

---

## Data Directory Locations

### Default Paths (No Configuration Needed)

| OS | Default Path |
|---|---|
| **Linux** | `~/.local/share/Hei-DataHub` |
| **macOS** | `~/Library/Application Support/Hei-DataHub` |
| **Windows** | `%LOCALAPPDATA%\Hei-DataHub` |

### Override Precedence (Highest to Lowest)

1. **CLI flag:** `hei-datahub --data-dir /path/to/data`
2. **Environment variable:** `HEIDATAHUB_DATA_DIR=/path/to/data`
3. **OS default:** See table above

---

## Essential Commands

### Check System Health

```bash
hei-datahub doctor
```

**Shows:**
- ✓ Data directory location and reason
- ✓ Read/write permissions
- ✓ Dataset count
- ✓ Database status
- ✓ Migration needs (if any)
- ✓ Filename issues (Windows)

**Exit codes:**
- `0` = Healthy
- `1` = Directory issue
- `2` = Permission error
- `3` = Data issue

### Override Data Directory

**Temporary (one command):**
```bash
hei-datahub --data-dir /path/to/custom doctor
```

**Persistent (all commands):**
```bash
# Linux/macOS (add to ~/.bashrc or ~/.zshrc)
export HEIDATAHUB_DATA_DIR="$HOME/my-datahub"

# Windows PowerShell (add to profile)
$env:HEIDATAHUB_DATA_DIR = "C:\DataHub"
```

### Show All Paths

```bash
hei-datahub paths
```

---

## Troubleshooting

### "No datasets found"

1. **Check location:**
   ```bash
   hei-datahub doctor
   ```
   Look for the data directory line.

2. **Verify datasets exist:**
   - Linux/macOS: `ls ~/.local/share/Hei-DataHub/datasets/`
   - Windows: `dir %LOCALAPPDATA%\Hei-DataHub\datasets`

3. **Reindex:**
   ```bash
   hei-datahub reindex
   ```

### Permission Denied

```bash
# Check with doctor
hei-datahub doctor

# Use custom location if needed
hei-datahub --data-dir ~/Documents/datahub
```

### Migrating from Old Installation

**If you see this warning:**
```
⚠ Migration: Legacy Linux-style path detected
```

**Then run:**
```bash
# Copy datasets
cp -r ~/.hei-datahub/datasets/* ~/Library/Application\ Support/Hei-DataHub/datasets/

# Reindex
hei-datahub reindex

# Verify
hei-datahub doctor

# Clean up old
rm -rf ~/.hei-datahub
```

### Windows Filename Issues

**If you see this warning:**
```
⚠ Filename Sanitation: 2 name(s) need sanitation
  my:dataset → my_dataset
```

**Action:** Rename your datasets to avoid:
- Characters: `\ / : * ? " < > |`
- Names: `CON PRN AUX NUL COM1-9 LPT1-9`
- Trailing dots or spaces

**Better names:**
- ✓ `my-dataset` or `my_dataset`
- ✓ `data-query`
- ✓ `print-queue`

---

## Platform-Specific Tips

### Linux

✅ **Just works** with XDG standard paths
✅ **No special configuration needed**

```bash
# Datasets at
ls ~/.local/share/Hei-DataHub/datasets/

# Config at
ls ~/.config/hei-datahub/
```

### macOS

✅ **Uses Application Support** (standard macOS location)
⚠ **Case-insensitive** filesystem (avoid `MyData` and `mydata`)

```bash
# Datasets at
ls ~/Library/Application\ Support/Hei-DataHub/datasets/

# Config at (still XDG-style)
ls ~/.config/hei-datahub/
```

### Windows

⚠ **Filename restrictions** (see sanitation warnings)
⚠ **Long path limits** (260 chars by default)
⚠ **Case-insensitive** filesystem

```powershell
# Datasets at
dir $env:LOCALAPPDATA\Hei-DataHub\datasets

# Enable long paths (optional)
# Run as Administrator, then restart
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
```

---

## Examples

### Use Custom Directory for Team

```bash
# Set once
export HEIDATAHUB_DATA_DIR="/mnt/shared/team-data"

# Now all commands use this path
hei-datahub doctor
hei-datahub reindex
hei-datahub
```

### Test with Temporary Directory

```bash
hei-datahub --data-dir /tmp/test-data doctor
hei-datahub --data-dir /tmp/test-data reindex
hei-datahub --data-dir /tmp/test-data
```

### Multiple Data Directories

```bash
# Personal
hei-datahub --data-dir ~/personal-data

# Work
hei-datahub --data-dir ~/work-data

# Team (shared)
hei-datahub --data-dir /mnt/team-data
```

---

## Quick Diagnostics

### 1-Liner Health Check

```bash
hei-datahub doctor && echo "✓ System healthy" || echo "✗ Issues detected"
```

### Check Data Location

```bash
hei-datahub doctor | grep "Data Directory"
```

### Count Datasets

```bash
hei-datahub doctor | grep "dataset(s) available"
```

---

## Getting Help

### In-App Help

```bash
hei-datahub --help
hei-datahub doctor --help
```

### Documentation

- **CLI Reference:** [docs/13-cli-reference.md](docs/13-cli-reference.md)
- **Troubleshooting:** [docs/installation/troubleshooting.md](docs/installation/troubleshooting.md)
- **Full Manual:** [docs/index.md](docs/index.md)

### Version Info

```bash
hei-datahub --version
hei-datahub --version-info  # Detailed
```

---

## Common Workflows

### Daily Use

```bash
hei-datahub  # Launch TUI
```

### After Git Pull

```bash
hei-datahub reindex  # Refresh dataset index
```

### Verify Installation

```bash
hei-datahub doctor  # Check everything
```

### Export/Import Keybindings

```bash
# Export
hei-datahub keymap export my-keys.yaml

# Share with team

# Import (on other machine)
hei-datahub keymap import my-keys.yaml
```

---

**Version:** 0.58.1-beta
**Updated:** 2025-10-08
**For full details:** See [IMPLEMENTATION_v0.58.1-beta.md](IMPLEMENTATION_v0.58.1-beta.md)
