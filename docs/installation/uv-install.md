# UV Installation Guide (Private Repository)

Complete guide to installing Hei-DataHub from a private GitHub repository using **uv**.

## What is UV?

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver written in Rust. It's a drop-in replacement for `pip` and `pip-tools`.

## Prerequisites

- **Python 3.10+** installed
- **uv** installed ([installation guide](https://github.com/astral-sh/uv#installation))
- **GitHub account** with access to the private repository
- Either **SSH key** configured for GitHub or **Personal Access Token (PAT)**

### Install UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Verify installation
uv --version
```

## Installation Methods

### Method 1: SSH (Recommended for Development)

**Prerequisites:**
- SSH key added to GitHub account
- SSH agent running with key loaded

```bash
# Global installation (recommended)
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"

# Ephemeral run (no installation, just run once)
uv tool run --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub" hei-datahub
```

**Verify SSH access first:**
```bash
ssh -T git@github.com
# Expected: Hi username! You've successfully authenticated...
```

### Method 2: Personal Access Token (Recommended for CI/CD)

**Prerequisites:**
- GitHub Personal Access Token with `repo` scope
- [Generate token here](https://github.com/settings/tokens/new)

```bash
# Set token as environment variable (temporary)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Global installation
uv tool install "git+https://${GITHUB_TOKEN}@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"

# Or embed token directly (not recommended for security)
uv tool install "git+https://ghp_xxxxx@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"
```

**For persistent token storage (Git credential helper):**
```bash
# Configure Git to cache credentials
git config --global credential.helper store

# Clone once to cache token
git clone https://github.com/0xpix/Hei-DataHub.git /tmp/test-clone
# Enter username: your-github-username
# Enter password: ghp_xxxxxxxxxxxxx

# Now uv can use cached credentials
uv tool install "git+https://github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"
```

## Version Pinning

### Install Specific Branch

```bash
# Install from specific branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=hei-datahub"
```

### Install Specific Tag/Release

```bash
# Install from tag
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.0-beta#egg=hei-datahub"
```

### Install Specific Commit

```bash
# Install from commit hash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@89a39d9#egg=hei-datahub"
```

## First Run

After installation, launch the app from **any directory**:

```bash
hei-datahub
```

### What Happens on First Run?

The app automatically initializes XDG-compliant directories:

```
~/.config/hei-datahub/          # Config & keybindings
  ├── config.json               # (created if missing)
  └── keymap.json               # (created if missing)

~/.local/share/hei-datahub/     # Application data
  ├── db.sqlite                 # Dataset index
  ├── schema.json               # Metadata schema
  ├── datasets/                 # 4 example datasets
  │   ├── burned-area/
  │   ├── land-cover/
  │   ├── precipitation/
  │   └── testing-the-beta-version/
  └── assets/
      └── templates/            # Default templates

~/.cache/hei-datahub/           # Cache (currently unused)

~/.local/state/hei-datahub/     # Logs
  └── logs/
```

## Verify Installation

### Check Paths

```bash
hei-datahub paths
```

**Expected output:**
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
  ...

Important Files:
  Database:  /home/user/.local/share/hei-datahub/db.sqlite
    Exists:  ✓
    Size:    12.5 KB
  ...
```

### Check Version

```bash
hei-datahub --version
# Output: Hei-DataHub 0.58.0-beta

hei-datahub --version-info
# Output: Detailed version, Python version, OS, etc.
```

### List Datasets

```bash
hei-datahub reindex
# Output:
#   ✓ Indexed: burned-area
#   ✓ Indexed: land-cover
#   ✓ Indexed: precipitation
#   ✓ Indexed: testing-the-beta-version
#   ✓ Successfully indexed 4 dataset(s)
```

## Updating

### Update to Latest Main Branch

```bash
# Uninstall current version
uv tool uninstall hei-datahub

# Reinstall latest
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"
```

### Update to Specific Version

```bash
uv tool uninstall hei-datahub
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.59.0-beta#egg=hei-datahub"
```

## Uninstallation

### Complete Removal

```bash
# Remove installed package
uv tool uninstall hei-datahub

# Remove all data (CAUTION: deletes your datasets!)
rm -rf ~/.config/hei-datahub \
       ~/.local/share/hei-datahub \
       ~/.cache/hei-datahub \
       ~/.local/state/hei-datahub
```

### Keep Data, Remove App Only

```bash
# Remove app only (keeps datasets and config)
uv tool uninstall hei-datahub
```

## Platform-Specific Notes

### Linux

- **PATH**: UV installs to `~/.local/bin` by default
- Add to PATH if needed:
  ```bash
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  source ~/.bashrc
  ```

### macOS

- **PATH**: Same as Linux (`~/.local/bin`)
- **zsh users**: Update `~/.zshrc` instead of `~/.bashrc`

### Windows

- **PATH**: UV installs to `%USERPROFILE%\.local\bin`
- **Git Bash**: Works the same as Linux/macOS
- **PowerShell**:
  ```powershell
  # Install from PowerShell
  uv tool install "git+https://github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"

  # Run
  hei-datahub
  ```
- **XDG directories**: Windows uses different paths:
  - Config: `%APPDATA%\hei-datahub\`
  - Data: `%LOCALAPPDATA%\hei-datahub\`
  - Cache: `%LOCALAPPDATA%\hei-datahub\Cache\`
  - Logs: `%LOCALAPPDATA%\hei-datahub\Logs\`

**Note:** Windows support is experimental. The app is primarily designed for Unix-like systems.

## Troubleshooting

### Command Not Found: `hei-datahub`

**Problem:** `zsh: command not found: hei-datahub`

**Solution:**
```bash
# Find where uv installed it
uv tool list
# Look for: hei-datahub

# Check UV bin path
echo $PATH | grep -o "$HOME/.local/bin"

# If missing, add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Authentication Failed (SSH)

**Problem:** `Permission denied (publickey)`

**Solution:**
```bash
# Check SSH key is loaded
ssh-add -l

# If empty, add key
ssh-add ~/.ssh/id_ed25519  # or id_rsa

# Test GitHub connection
ssh -T git@github.com
```

### Authentication Failed (Token)

**Problem:** `fatal: Authentication failed for 'https://github.com/0xpix/Hei-DataHub.git/'`

**Solutions:**

1. **Check token scope:**
   - Go to https://github.com/settings/tokens
   - Ensure token has `repo` scope (full control of private repositories)

2. **Verify token:**
   ```bash
   curl -H "Authorization: token ghp_xxxxx" https://api.github.com/user
   # Should return your user info
   ```

3. **Clear cached credentials:**
   ```bash
   # Remove cached token
   rm ~/.git-credentials

   # Or use credential helper to erase
   git credential-cache exit
   ```

### No Datasets After Install

**Problem:** App launches but shows "No datasets found"

**Diagnostic:**
```bash
hei-datahub paths
# Check if Data directory exists and has datasets
```

**Solution:**
```bash
# Manually trigger initialization
python -c "from mini_datahub.infra.paths import initialize_workspace; initialize_workspace()"

# Reindex
hei-datahub reindex
```

### Permission Errors

**Problem:** `PermissionError: [Errno 13] Permission denied: '/home/user/.local/share/hei-datahub/db.sqlite'`

**Solution:**
```bash
# Fix permissions
chmod -R u+w ~/.config/hei-datahub ~/.local/share/hei-datahub ~/.local/state/hei-datahub
```

### Large File Download Timeout

**Problem:** Installation hangs or fails on large files

**Note:** This shouldn't happen with `hei-datahub` as example datasets are small (<1MB each).

**If it occurs:**
```bash
# Increase Git timeout
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# Retry installation
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"
```

## Advanced: Custom XDG Paths

Override default XDG directories with environment variables:

```bash
# Custom config location
export XDG_CONFIG_HOME=~/my-configs
hei-datahub  # Uses ~/my-configs/hei-datahub/

# Custom data location
export XDG_DATA_HOME=~/my-data
hei-datahub  # Uses ~/my-data/hei-datahub/

# Persistent override (add to ~/.bashrc)
echo 'export XDG_DATA_HOME=~/my-data' >> ~/.bashrc
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Hei-DataHub

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install Hei-DataHub
        env:
          GITHUB_TOKEN: ${% raw %}{{ secrets.GH_PAT }}{% endraw %}
        run: |
          uv tool install "git+https://${GITHUB_TOKEN}@github.com/0xpix/Hei-DataHub.git#egg=hei-datahub"

      - name: Verify Installation
        run: |
          hei-datahub --version
          hei-datahub paths
          hei-datahub reindex
```

**Required Secret:**
- `GH_PAT`: Personal Access Token with `repo` scope

## Comparison: UV vs pip

| Feature | UV | pip |
|---------|-----|-----|
| **Speed** | ~10-100x faster | Baseline |
| **Dependency resolution** | Comprehensive | Limited |
| **Virtual environment** | Managed automatically | Manual (`venv`) |
| **Private repos** | SSH & token support | Same |
| **Lock files** | Built-in (`uv.lock`) | Separate tool (`pip-tools`) |

**When to use pip:**
- Corporate environments with `pip` infrastructure
- Existing `requirements.txt` workflows
- Python 2.7 support needed (uv is Python 3+ only)

**When to use uv:**
- Faster installs
- Better dependency resolution
- Modern Python 3.10+ projects
- Development workflows

## Related Documentation

- [Desktop Integration (Linux)](./desktop-version.md) - Add Hei-DataHub to application menu
- [Troubleshooting](./troubleshooting.md) - Common issues and fixes
- [Windows Notes](./windows-notes.md) - Windows-specific guidance
- [Private Repo Access](./private-repo-access.md) - Detailed authentication guide

## Support

- **Issues**: [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
- **Version**: This guide is for v0.58.0-beta

---

**Version:** v0.58.0-beta
**Last Updated:** 2025-10-07
**Compatibility:** Linux (primary), macOS (supported), Windows (experimental)
