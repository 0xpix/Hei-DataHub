# Getting Started

This guide will help you install and run Hei-DataHub in minutes.

---

## Prerequisites

Before installing, ensure you have:

| Requirement | Version | Notes |
|------------|---------|-------|
| **Python** | 3.10+ | Check: `python --version` |
| **uv** | Latest | Fast Python package installer: [astral.sh/uv](https://astral.sh/uv) |
| **Terminal** | Any | Works in any terminal emulator |

**Platform Support (v0.59):**

- ✅ **Linux** — Full support with desktop integration
- 🚧 **macOS** — Coming in v0.61
- 🚧 **Windows** — Coming in v0.61

---

## Installation

### Option 1: UV Direct Install (Recommended)

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
- 🚀 Global command available system-wide
- 🔄 Easy updates with `uv tool upgrade hei-datahub`

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
mini-datahub  # Will be DEPRECATED in v0.60

# Update to latest version
hei-datahub update

# Uninstall
hei-datahub uninstall

# Show version
hei-datahub --version

# Show detailed version and system info
hei-datahub --version-info
```

### New in v0.59
```bash
# Connect to the Cloud (HeiBox)
hei-datahub auth setup
```

---

## First Launch Checklist

When you run `hei-datahub` for the first time (v0.59+), the app will:

1. ✅ Load configuration – Reads or creates your settings in ~/.config/hei-datahub/config.toml
2. ✅ Prepare workspace – Ensures ~/.local/share/Hei-DataHub/ exists for app data
3. ✅ Initialize database – Creates db.sqlite and the FTS5 search index for instant lookups
4. ✅ Index datasets – Scans existing entries and updates the search catalog
5. ✅ Connect to HeiBox – Tests your WebDAV connection and syncs metadata
6. ✅ Start background sync – Periodically updates search and cloud data (non-blocking)
7. ✅ Launch interface – Opens the TUI with fast search and dataset browsing

**Workspace Location:**

- **Linux:** `~/.local/share/Hei-DataHub/` (XDG-compliant)
- **macOS:** `~/Library/Application Support/Hei-DataHub/` (coming in v0.61)
- **Windows:** `%LOCALAPPDATA%\Hei-DataHub\` (coming soon in v0.61)

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
