
This guide will help you install and run Hei-DataHub in minutes.

---

## Prerequisites

Before installing, ensure you have:

| Requirement | Version | Notes |
|------------|---------|-------|
| **Python** | 3.9+ | Check: `python --version` |
| **uv** (recommended) | Latest | Fast Python package installer: [astral.sh/uv](https://astral.sh/uv) |
| **Git** | Any recent | Required for PR workflow (optional feature) |
| **Terminal** | Any | Works in any terminal emulator |

---

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub

# Run setup script
./scripts/setup_dev.sh

# Activate virtual environment
source .venv/bin/activate

# Launch the TUI
hei-datahub
```

### Option 2: Manual Setup with uv

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub

# Install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate

# Launch the TUI
hei-datahub
```

---

## Verify Installation

Run the verification script:

```bash
./scripts/verify_installation.sh
```

This checks:

- ✅ Python version
- ✅ Virtual environment
- ✅ Package installation
- ✅ Database initialization
- ✅ Dataset indexing

---

## Command Reference

```bash
# Launch TUI (use either command)
hei-datahub
mini-datahub # Will be deprecated in future

# Rebuild search index from YAML files
hei-datahub reindex

# Show version
hei-datahub --version

# Show detailed version and system info
hei-datahub --version-info
```

---

## First Launch Checklist

When you run `hei-datahub` for the first time, the app will:

1. ✅ Create `.cache/` directory for temporary files
2. ✅ Initialize `db.sqlite` database at project root
3. ✅ Create FTS5 search index tables
4. ✅ Index example datasets from `data/` folder
5. ✅ Open the Home screen with search functionality

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
2. **[Add your first dataset](how-to/02-first-dataset.md)** — Step-by-step tutorial
3. **[Configure GitHub integration](12-config.md#github-configuration)** — Enable PR workflow (optional)

---

## Troubleshooting

For common issues, see:

- **[FAQ & Troubleshooting](90-faq.md)** — Solutions to frequent problems
- **[GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)** — Report bugs or get help
