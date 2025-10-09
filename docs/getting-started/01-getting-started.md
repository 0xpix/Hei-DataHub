# Getting Started

This guide will help you install and run Hei-DataHub in minutes.

---

## Prerequisites

Before installing, ensure you have:

| Requirement | Version | Notes |
|------------|---------|-------|
| **Python** | 3.10+ | Check: `python --version` |
| **uv** | Latest | Fast Python package installer: [astral.sh/uv](https://astral.sh/uv) |
| **Git** | Any recent | Required for PR workflow (optional feature) |
| **Terminal** | Any | Works in any terminal emulator |
| **SSH/PAT** | - | GitHub access via SSH key or Personal Access Token |

**Platform Support (v0.58):**
- ✅ **Linux** — Full support with desktop integration
- 🚧 **macOS** — Coming in v0.59
- 🚧 **Windows** — Coming in v0.59

---

## Installation

### Option 1: UV Direct Install (Recommended — New in v0.58)

**No cloning required!** Install directly from GitHub.

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Hei-DataHub (SSH method)
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# Or with Personal Access Token
export GH_PAT=ghp_xxxxxxxxxxxxx
uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main"

# Launch from anywhere
hei-datahub
```

**Benefits:**
- ⚡ No repository cloning needed
- 📦 All dependencies handled automatically
- 🔒 Works with private repositories
- 🚀 Global command available system-wide
- 🔄 Easy updates with `uv tool upgrade hei-datahub`

**Desktop Integration (Linux):**
```bash
# Create application menu entry
bash scripts/create_desktop_entry.sh
```

**See also:** [Complete Installation Guide](../installation/README.md)

---

### Option 2: Development Setup (For Contributors)

For those who want to modify the code:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub

# Install with development dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate

# Launch the TUI
hei-datahub
```

---

### Option 3: Ephemeral Run (Testing)

Try without installing:

```bash
# One-time run (SSH)
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# Or with token
export GH_PAT=ghp_xxxxxxxxxxxxx
uvx "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main"
```

Perfect for testing before committing to installation.

---

## Command Reference

### Basic Commands
```bash
# Launch TUI (use either command)
hei-datahub
mini-datahub  # Alternative command

# Rebuild search index from YAML files
hei-datahub reindex

# Show version
hei-datahub --version

# Show detailed version and system info
hei-datahub --version-info
```

### New in v0.58
```bash
# Run system diagnostics
hei-datahub doctor

# Override data directory for single run
hei-datahub --data-dir /path/to/custom/location

# Show current paths
hei-datahub paths
```

### UV Tool Management
```bash
# Update to latest version
uv tool upgrade hei-datahub

# Uninstall
uv tool uninstall hei-datahub

# Install specific version
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1-beta"

# List installed UV tools
uv tool list
```

---

## First Launch Checklist

When you run `hei-datahub` for the first time (v0.58+), the app will:

1. ✅ Create workspace directory at `~/.local/share/Hei-DataHub/` (Linux)
2. ✅ Initialize `db.sqlite` database
3. ✅ Create FTS5 search index tables
4. ✅ Copy 4 sample datasets with complete metadata
5. ✅ Index all datasets for search
6. ✅ Open the Home screen with search functionality

**Workspace Location:**
- **Linux:** `~/.local/share/Hei-DataHub/` (XDG-compliant)
- **macOS:** `~/Library/Application Support/Hei-DataHub/` (coming soon)
- **Windows:** `%LOCALAPPDATA%\Hei-DataHub\` (coming soon)

**Override workspace location:**
```bash
# Temporary
hei-datahub --data-dir ~/my-custom-workspace

# Persistent (add to ~/.bashrc or ~/.zshrc)
export HEIDATAHUB_DATA_DIR=~/my-custom-workspace
```

**Expected output:**

<p align="center">
    <img src="/Hei-DataHub/assets/tui_homescreen.png" alt="Hei-DataHub homescreen"/>
</p>

---

## Ready to Find Data

### 1. Search Test

```
1. Press / to focus search
2. Type "test"
3. Press Enter to move to results
4. Use j/k or arrow keys to navigate
```

✅ **Expected:** Results update as you type (debounced 150ms)

### 2. Dataset Details Test

```
1. Navigate to any dataset in the results
2. Press Enter or o to open details
3. Press Escape or b to go back
```

✅ **Expected:** Details screen shows all metadata fields

---

## Next Steps

Now that Hei-DataHub is running:

1. **[Learn the keyboard shortcuts](02-navigation.md)** — Master the Vim-style navigation
2. **[Add your first dataset](../how-to/05-first-dataset.md)** — Step-by-step tutorial
3. **[Configure GitHub integration](../how-to/04-settings.md)** — Enable PR workflow with detailed PAT setup (optional)

---

## Troubleshooting

For common issues, see:

- **[FAQ & Troubleshooting](../help/90-faq.md)** — Solutions to frequent problems
- **[GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)** — Report bugs or get help
