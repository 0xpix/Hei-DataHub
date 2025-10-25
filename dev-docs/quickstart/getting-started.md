# Getting Started with Hei-DataHub Development

Welcome! This guide assumes you've **never seen this codebase before** and will walk you through everything step by step.

## What is Hei-DataHub?

Hei-DataHub is a **Terminal User Interface (TUI) application** for managing and exploring geospatial datasets. Think of it like a file manager, but specifically designed for scientific data with metadata, search capabilities, and cloud sync.

### Key Features
- 📁 **Catalog Management**: Browse and organize datasets locally
- 🔍 **Search**: Fast full-text search across datasets
- 🌐 **WebDAV Sync**: Sync datasets from cloud storage (HeiBox/Seafile)
- 🎨 **TUI Interface**: Beautiful terminal interface using Textual framework
- ⚡ **SQLite Backend**: Fast, local-first data storage

## Prerequisites

Before you start, make sure you have:

```bash
# Required
- Python 3.9 or higher
- Git
- uv (Python package installer)

# Optional but recommended
- VSCode or PyCharm
- WebDAV account (HeiBox/Seafile for testing sync features)
```

## Installation Steps

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub
```

### 2. Set Up Development Environment

We use `uv` for dependency management (it's like pip but faster):

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### 3. Verify Installation

```bash
# Check if the CLI works
hei-datahub --version

# Should output something like: v0.56.0-beta
```

### 4. Initialize the Database

The first time you run Hei-DataHub, it needs to create its SQLite database:

```bash
# Run the app (it will create db.sqlite automatically)
hei-datahub

# You should see the TUI interface load
```

**What just happened?**
- Created `~/.config/hei-datahub/config.yaml` (user config)
- Created `db.sqlite` in your current directory (local database)
- Indexed any datasets in the `data/` folder

## Understanding the Project Structure

```
Hei-DataHub/
├── src/mini_datahub/       # Main Python package
│   ├── app/                # Application runtime & settings
│   ├── cli/                # Command-line interface entry point
│   ├── core/               # Domain models, rules, queries
│   ├── infra/              # Infrastructure (DB, WebDAV)
│   ├── services/           # Business logic (search, catalog, sync)
│   ├── ui/                 # TUI screens, widgets, theme
│   └── utils/              # Helper functions
├── data/                   # Sample datasets (for testing)
├── tests/                  # Unit and integration tests
├── docs/                   # User documentation (main branch)
├── dev-docs/               # Developer docs (this site, docs/devs branch)
├── scripts/                # Dev tools & automation
├── pyproject.toml          # Project metadata & dependencies
└── db.sqlite               # Local SQLite database (created on first run)
```

## Your First Run

Let's explore the app:

```bash
# Start the TUI
hei-datahub
```

### TUI Navigation Basics

- **`j`/`k`** or **↓/↑**: Navigate up/down
- **`/`**: Open search
- **`q`**: Quit
- **`?`**: Help screen (shows all keybindings)
- **`Tab`**: Switch between panels

### What You're Looking At

1. **Left Panel**: Dataset list (catalog view)
2. **Right Panel**: Details for selected dataset
3. **Bottom**: Status bar with hints

## Next Steps

Now that you're set up:

1. **[Make Your First Contribution](first-contribution.md)** - Start with a simple change
2. **[Common Development Tasks](common-tasks.md)** - Learn the workflow
3. **[Codebase Tour](../codebase/overview.md)** - Deep dive into the code

## Troubleshooting

### App Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
uv sync --reinstall

# Check for errors
hei-datahub --verbose
```

### Import Errors

```bash
# Make sure virtual environment is activated
which python  # Should point to .venv/bin/python

# Reinstall in development mode
uv pip install -e .
```

### Database Errors

```bash
# Delete and recreate the database
rm db.sqlite
hei-datahub  # Will recreate on startup
```

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions
- **Discord**: (Coming soon) Real-time chat
- **This Documentation**: You're in the right place!

---

**Next**: [First Contribution →](first-contribution.md)
