# Hei-DataHub

[![Version](https://img.shields.io/badge/version-0.55.0--beta-blue.svg)](SUMMARY_v0.55.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

> A local-first TUI for managing datasets with consistent metadata, fast full-text search, and automated PR workflows.

**📦 Latest Release:** [v0.55.0-beta "Auto-Stash & Clean Architecture"](SUMMARY_v0.55.md) - Enhanced PR workflow with automatic stashing, improved gitignore handling, dual command support

## Overview

**Hei-DataHub** is a dataset inventory that lets you:
- **Search** existing datasets with fast full-text search (SQLite FTS5)
- **Add** new datasets with validated, consistent metadata
- **Publish** datasets as Pull Requests with automatic git operations
- Work entirely locally with YAML files and SQLite—no network required (network required only at first when cloning)

Think of it as a lightweight data catalog for teams who want to organize datasets without complex infrastructure.

## Features

- 🏠 **Local-First**: Everything stored in YAML files + SQLite database
- 🔍 **Fast Search**: Full-text search powered by SQLite FTS5 with BM25 ranking
- ✅ **Validated Metadata**: JSON Schema + Pydantic validation
- 🖥️ **Clean TUI**: Terminal interface built with Textual with Neovim-style keybindings
- 📦 **Simple Storage**: One folder per dataset with `metadata.yaml`
- 🚀 **Easy Setup**: Install and run immediately
- 🔄 **Automated PRs**: Save → PR workflow with GitHub integration (optional)
- 🎯 **Auto-Stash**: Automatically handles uncommitted changes during PR workflow
- 🏗️ **Clean Architecture**: Layered design with clear separation of concerns

## Quick Start

```bash
# Clone or download this repository
git clone <your-repo-url>
cd Hei-DataHub

# Install using uv (recommended)
uv sync --dev
source .venv/bin/activate

# Launch the TUI (use either command)
hei-datahub
# or
mini-datahub

# Or reindex from YAML files
hei-datahub reindex

# Check version
hei-datahub --version
hei-datahub --version-info  # Detailed version information
```

### Alternative: Use the setup script

```bash
./scripts/setup_dev.sh
source .venv/bin/activate
hei-datahub
```

**Note:** We use [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management. Install it with:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Repository Structure

```
Hei-DataHub/
├── src/
│   └── mini_datahub/          # Main source package
│       ├── __init__.py        # Package initialization with version
│       ├── version.py         # Version management (0.55.0-beta)
│       ├── app/               # Application runtime & settings
│       │   ├── runtime.py     # Startup, logging, DI wiring
│       │   └── settings.py    # Config load/persist (non-secrets)
│       ├── core/              # Domain logic (no I/O)
│       │   ├── models.py      # Pydantic models
│       │   ├── rules.py       # Business rules
│       │   └── errors.py      # Custom exceptions
│       ├── infra/             # Infrastructure adapters
│       │   ├── paths.py       # Path management
│       │   ├── db.py          # SQLite connection
│       │   ├── index.py       # FTS5 operations
│       │   ├── store.py       # YAML I/O
│       │   ├── git.py         # Git operations with auto-stash
│       │   ├── github_api.py  # GitHub API integration
│       │   ├── auth.py        # Keyring (PAT storage)
│       │   └── sql/
│       │       └── schema.sql # Database schema
│       ├── services/          # Business logic orchestration
│       │   ├── search.py      # Query policy
│       │   ├── catalog.py     # Add/update datasets
│       │   ├── sync.py        # Pull + reindex
│       │   ├── publish.py     # Save→PR with auto-stash
│       │   ├── autocomplete.py
│       │   ├── outbox.py      # Queued PRs on failure
│       │   └── update_check.py
│       ├── ui/                # Textual UI
│       │   ├── views/         # Screen components
│       │   │   ├── home.py
│       │   │   ├── details.py
│       │   │   ├── settings.py
│       │   │   └── outbox.py
│       │   ├── widgets/       # Reusable UI components
│       │   └── keys.py        # Keybinding definitions
│       ├── cli/               # CLI entrypoint
│       │   └── main.py
│       └── utils/             # Utilities
│           └── text.py
├── data/                      # Dataset storage (one folder per dataset)
│   └── example-weather/
│       └── metadata.yaml
├── tests/                     # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                   # Developer convenience scripts
│   ├── setup_dev.sh
│   └── setup_pr_workflow.sh
├── .github/
│   └── workflows/
│       └── ci.yaml            # CI/CD pipeline
├── schema.json                # JSON Schema for metadata validation
├── pyproject.toml             # Python build configuration
├── uv.lock                    # Locked dependencies
├── .gitignore                 # Git ignore rules (data files only, keeps metadata)
├── LICENSE                    # MIT License
├── CHANGELOG.md               # Version history
└── README.md
```

## Data Model

Each dataset is stored as a folder under `data/<id>/metadata.yaml` with:

### Required Fields
- **ID**: Unique slug (lowercase, alphanumeric, dashes, underscores)
- **Dataset Name**: Human-readable name
- **Description**: What this dataset contains
- **Source**: URL or library snippet showing where it came from
- **Date Created**: ISO date (defaults to today)
- **Storage Location**: Where the actual data files are stored

### Optional Fields
- **File Format**: CSV, JSON, Parquet, NetCDF, GeoTIFF, etc.
- **Size**: File size or row count
- **Data Types**: Categories/domains (e.g., "weather", "finance")
- **Used In Projects**: List of projects using this dataset
- **Schema/Fields**: Field definitions with name, type, description
- **Last Updated**: When the dataset was last modified
- **Dependencies/Tools Needed**: Required libraries or tools
- **Preprocessing Steps**: Data cleaning or transformation applied
- **Linked Documentation**: URLs to docs or papers
- **Cite**: Citation information
- **Spatial/Temporal Resolution**: For geographic/time-series data
- **Temporal/Spatial Coverage**: Date ranges or geographic bounds
- **Codes**: Related code snippets or links
- **extras**: Free-form object for custom fields

## Usage

### TUI Interface

The TUI features **Neovim-style keybindings** with Normal and Insert modes for efficient keyboard-driven workflows.

#### Modes

- **Normal Mode** (cyan indicator): Navigate and command
- **Insert Mode** (green indicator): Edit fields and search

#### Home / Search Screen

**Normal Mode:**
- `/` - Focus search (enter Insert mode)
- `j` / `k` - Move selection down/up in results
- `gg` - Jump to first dataset
- `G` - Jump to last dataset
- `o` or `Enter` - Open details for selected dataset
- `A` - Add new dataset
- `S` - Settings (configure GitHub integration)
- `P` - Outbox (retry failed PRs)
- `U` - Pull updates from catalog repository
- `R` - Refresh/reindex datasets
- `?` - Show help with all keybindings
- `q` - Quit application

**Insert Mode (in search bar):**
- Type to search - results update live with 150ms debounce
- Partial words work: "wea" finds "weather", "wealth", etc.
- `Esc` - Return to Normal mode
- `Enter` - Move focus to results table

**Features:**
- **Zero-query list**: Shows all datasets before typing
- **Incremental search**: Results update as you type
- **Focus retention**: Search input keeps focus while typing (no interruption)
- **BM25 ranking**: Most relevant results first

#### Details Screen

- **`P`** - **Publish as PR** (create PR for this dataset) ✨ **Auto-stash enabled!**
- `y` - Copy source to clipboard ("yank")
- `o` - Open source URL in browser (if valid URL)
- `q` / `Esc` - Back to search

#### Add Data Form

**Normal Mode:**
- `j` / `k` - Move focus to next/previous field
- `gg` - Jump to first field
- `G` - Jump to last field
- `Ctrl+d` / `Ctrl+u` - Scroll half-page down/up
- `Page Down` / `Page Up` - Scroll half-page down/up (alternative)
- **Mouse wheel** - Scroll up/down
- `Tab` / `Shift+Tab` - Standard field navigation
- `Ctrl+S` - Save dataset and create PR automatically (if configured)
- `q` / `Esc` - Cancel and return

**Insert Mode (in fields):**
- Type to edit
- `Esc` - Return to Normal mode

**Features:**
- **Fully scrollable**: Works on small terminals (24 rows)
- **Real-time validation**: Inline error feedback
- **Auto-generate ID**: From dataset name if not provided
- **URL probe**: HTTP HEAD request infers format/size
- **Auto-PR on save**: Creates pull request automatically (if GitHub configured)

#### Help Screen

- `?` - Show help (from any screen)
- `q` / `Esc` - Close help

### CLI Commands

```bash
# Launch TUI (default) - use either command
hei-datahub
mini-datahub

# Rebuild search index from YAML files
hei-datahub reindex

# Show version
hei-datahub --version
# Output: Hei-DataHub 0.55.0-beta

# Show detailed version info
hei-datahub --version-info
# Shows: version, build number, release date, codename, Python version, platform
```

## GitHub PR Workflow (Optional)

**Enhanced in v0.55.0:** Automatic stashing of uncommitted changes during PR workflow!

### ✨ New: Auto-Stash Feature

The PR workflow now automatically handles uncommitted changes:

- **Before:** Manual `git stash` required if you had uncommitted changes
- **Now:** Automatically stashes changes, creates PR, then restores your changes
- **Safe:** Uses `finally` block to ensure restoration even if PR fails
- **No data loss:** Changes preserved as stash if restoration fails

### Quick Setup

1. **Create a catalog repository** on GitHub (e.g., `your-org/mini-datahub-catalog`)
2. **Clone it locally**: `git clone https://github.com/your-org/mini-datahub-catalog.git`
3. **Generate a GitHub PAT** with `Contents: R/W`, `Pull requests: R/W` permissions
   - See [GITHUB_TOKEN_GUIDE.md](GITHUB_TOKEN_GUIDE.md) for detailed instructions
4. **Configure the app**:
   - Launch: `hei-datahub`
   - Press `S` for Settings
   - Fill in GitHub host, owner, repo, username, token
   - Set catalog repository path (absolute path to local clone)
   - Test connection, then Save

5. **Save a dataset** (press `A`, fill form, press `Ctrl+S`)
   - ✨ PR created automatically!
   - 🎯 Uncommitted changes? Auto-stashed and restored!
   - 🎉 Success toast with PR URL

### What Happens Automatically

When you save a dataset with GitHub configured:

1. **Checks** for uncommitted changes in catalog repo
2. **Auto-stashes** if needed (labeled with dataset ID)
3. **Writes** `data/<id>/metadata.yaml` to your local catalog repo
4. **Creates** a git branch: `add/<dataset-id>-<timestamp>`
5. **Commits** with message: `feat(dataset): add <id> — <name>`
6. **Pushes** to GitHub (central repo if you have push access, or your fork)
7. **Opens** a Pull Request with formatted description
8. **Restores** stashed changes (if any were stashed)
9. **Shows** success notification with PR link

### Offline Handling

If offline or PR creation fails:
- Dataset **saved locally** ✅
- Stash **restored** (if created) ✅
- PR task **queued in Outbox** 📮
- Press `P` to view outbox
- Press `R` to retry when back online

### Git Operations

The PR workflow includes robust git operations:
- ✅ Auto-deletes existing branches with same name
- ✅ Checks working tree status before operations
- ✅ Automatically stashes uncommitted changes
- ✅ Restores stashed changes after PR (even on failure)
- ✅ Provides clear error messages with actionable guidance

### For Teams

**Contributors:**
- Clone catalog repo once
- Configure GitHub settings once
- Add datasets through TUI
- PRs created automatically
- Your uncommitted work is safe (auto-stashed)

**Maintainers:**
- Review PRs on GitHub
- Check metadata accuracy, source URLs
- Approve and merge
- Changes sync to all team members

**See [GITHUB_WORKFLOW.md](GITHUB_WORKFLOW.md) for detailed setup guide and troubleshooting.**

## Git Ignore Configuration

The repository uses a **smart gitignore pattern** that:
- ✅ **Tracks** `metadata.yaml` files (essential for catalog)
- ✅ **Tracks** `README.md` and `images/` (optional documentation)
- ❌ **Ignores** actual data files (.csv, .parquet, .json, .nc, .tif, etc.)

This means you can commit dataset metadata to git while keeping large data files local or in separate storage.

## Development

```bash
# Install with dev dependencies using uv
uv sync --dev
source .venv/bin/activate

# Run tests
pytest

# Format code
black src/mini_datahub tests
ruff check src/mini_datahub tests

# Type checking
mypy src/mini_datahub

# Add new dependencies
uv add <package-name>
uv add --dev <dev-package>

# Update lock file
uv lock
```

**CI/CD:** Use `uv sync --frozen --dev` in CI to ensure reproducible builds with the lock file.

## Architecture

The codebase follows a **clean, layered architecture**:

### Dependency Rules

- **UI** → may import **services**, **core**, **utils**, **app.settings**
- **Services** → may import **infra**, **core**, **utils**
- **Infra** → may import **utils** only (no UI/Services/Core)
- **Core** → **pure** domain logic (no dependencies)
- **CLI** → calls into **app**/**services**

This ensures:
- ✅ No cyclic dependencies
- ✅ Testable components
- ✅ Clear separation of concerns
- ✅ Easy to maintain and extend

## How It Works

1. **Storage**: Each dataset is a folder with `metadata.yaml`
2. **Validation**: Changes validated against JSON Schema + Pydantic model
3. **Indexing**: Metadata indexed into SQLite FTS5 for fast search
4. **Search**: BM25-ranked full-text search across all text fields
5. **TUI**: Textual-based interface for keyboard-driven workflow
6. **PR Workflow**: Git operations with automatic stashing for seamless experience

## Example Dataset

```yaml
id: example-weather
dataset_name: "Global Weather Stations 2024"
description: "Hourly weather observations from 10,000+ stations worldwide"
source: "https://example.com/weather-data.csv"
date_created: "2024-01-15"
storage_location: "s3://my-bucket/weather/"
file_format: "CSV"
size: "2.5 GB"
data_types:
  - weather
  - time-series
used_in_projects:
  - climate-analysis
  - weather-forecasting
schema_fields:
  - name: station_id
    type: string
    description: Unique station identifier
  - name: timestamp
    type: datetime
    description: Observation time (UTC)
  - name: temperature
    type: float
    description: Temperature in Celsius
```

## Design Decisions

- **Local-first**: No server, no network dependencies (except optional URL probes and GitHub)
- **YAML**: Human-readable, git-friendly, easy to edit manually
- **SQLite FTS5**: Fast, embedded, proven full-text search
- **Textual TUI**: Modern terminal UI with keyboard-first design
- **Pydantic + JSON Schema**: Belt-and-suspenders validation
- **Clean Architecture**: Layered design for maintainability
- **Auto-stash**: Git operations that handle uncommitted changes gracefully

## Quality Gates & Testing

The test suite covers:
- ✅ Slug generation and ID collision handling
- ✅ Metadata validation (JSON Schema + Pydantic)
- ✅ YAML read/write operations
- ✅ Database operations (upsert, search, delete)
- ✅ Full-text search with BM25 ranking
- ✅ Reindexing from disk
- ✅ Git operations with stashing
- ✅ PR workflow end-to-end

Run tests with:
```bash
pytest tests/ -v
```

## Acceptance Criteria (All Met ✓)

- ✅ Adding a new dataset with only required fields completes without errors
- ✅ New dataset immediately appears in search
- ✅ Searching for keywords returns relevant results ranked by BM25
- ✅ Validation rejects malformed IDs, missing fields with clear messages
- ✅ Reindexing from data directory restores DB state
- ✅ Example dataset is visible on first run
- ✅ No network traffic unless user triggers HEAD probe or GitHub operations
- ✅ Keyboard-accessible interface (Tab, Enter, shortcuts)
- ✅ Copy-to-clipboard and URL opening functionality
- ✅ PR workflow handles uncommitted changes automatically
- ✅ Both `hei-datahub` and `mini-datahub` commands work

## Version History

- **v0.55.0-beta** (Current) - Auto-stash PR workflow, improved gitignore, enhanced version system
- **v0.50.0-beta** - Clean architecture refactoring, dual command support
- **v0.40.0-beta** - Restructured to src/ layout
- Earlier versions - See [CHANGELOG.md](CHANGELOG.md)

## Troubleshooting

**Database errors on startup?**
- Delete `db.sqlite` and run `hei-datahub reindex`

**Search not finding datasets?**
- Run `hei-datahub reindex` to rebuild the search index

**Validation errors?**
- Check that all required fields are filled
- Ensure ID follows slug format (lowercase, alphanumeric, dashes/underscores)
- Verify dates are in YYYY-MM-DD format

**Clipboard not working?**
- Install xclip (Linux) or ensure proper clipboard support

**PR creation fails?**
- Check GitHub token has correct permissions
- Verify catalog repository path is correct
- Check internet connection
- View outbox (`P`) to retry failed PRs

**Git says "paths are ignored"?**
- The `.gitignore` is configured to track metadata.yaml files
- If you're still having issues, check that your catalog repo's .gitignore allows metadata files
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions

**Command not found?**
```bash
# Activate virtual environment
source .venv/bin/activate

# Or use uv run
uv run hei-datahub
```

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please:
1. Open an issue to discuss major changes
2. Follow existing code style (black + ruff)
3. Add tests for new functionality
4. Update documentation
5. Ensure CI passes

## Quick Reference

See [QUICKSTART.md](QUICKSTART.md) for a comprehensive quick reference guide.

---

**Built for teams who want to organize data without the overhead.**

**v0.55.0-beta** brings seamless PR workflows with automatic git stash handling! 🚀
