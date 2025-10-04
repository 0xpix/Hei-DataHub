# Hei-DataHub

> A local-first TUI for managing datasets with consistent metadata, fast full-text search, and clean file layout.

## Overview

**Hei-DataHub** is a inventory that lets us:
- **Search** existing datasets with fast full-text search (SQLite FTS5)
- **Add** new datasets with validated, consistent metadata
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

## Quick Start

```bash
# Clone or download this repository
git clone <your-repo-url>
cd Hei-DataHub

# Install using uv (recommended)
uv sync --python /usr/bin/python --dev
source .venv/bin/activate

# Launch the TUI
mini-datahub

# Or reindex from YAML files
mini-datahub reindex
```

### Alternative: Use the setup script

```bash
./scripts/setup_dev.sh
source .venv/bin/activate
mini-datahub
```

**Note:** We use [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management. Install it with:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Repository Structure

```
Hei-DataHub/
├── mini_datahub/          # Main source package
│   ├── __init__.py
│   ├── models.py          # Pydantic models mirroring JSON Schema
│   ├── storage.py         # YAML read/write, validation, dataset listing
│   ├── index.py           # SQLite FTS5 operations
│   ├── utils.py           # Path management, constants
│   ├── tui.py             # Textual TUI application
│   └── cli.py             # CLI entrypoint
├── data/                  # Dataset storage (one folder per dataset)
│   └── example-weather/
│       └── metadata.yaml
├── sql/                   # Database schema
│   └── schema.sql
├── tests/                 # Smoke tests
│   └── test_basic.py
├── scripts/               # Developer convenience scripts
│   └── setup_dev.sh
├── .github/
│   └── workflows/
│       └── ci.yml         # Minimal CI
├── schema.json            # JSON Schema for metadata validation
├── pyproject.toml         # Python build configuration
├── LICENSE                # MIT License
├── .gitignore
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
- **File Format**: CSV, JSON, Parquet, etc.
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

- **`P`** - **Publish as PR** (create PR for this dataset) 🆕
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
- `Ctrl+S` - Save dataset
- `q` / `Esc` - Cancel and return

**Insert Mode (in fields):**
- Type to edit
- `Esc` - Return to Normal mode

**Features:**
- **Fully scrollable**: Works on small terminals (24 rows)
- **Real-time validation**: Inline error feedback
- **Auto-generate ID**: From dataset name if not provided
- **URL probe**: HTTP HEAD request infers format/size

#### Help Screen

- `?` - Show help (from any screen)
- `q` / `Esc` - Close help

### CLI Commands

```bash
# Launch TUI (default)
mini-datahub

# Rebuild search index from YAML files
mini-datahub reindex

# Show version
mini-datahub --version
```

## GitHub PR Workflow (Optional)

**New in v3.0:** Automatically create Pull Requests when saving datasets!

### ✨ New: Publish from Details (`P` key)

You can now create PRs for any dataset directly from its Details view:

1. **Browse datasets** in Home screen
2. **Open Details** (press `Enter`)
3. **Press `P`** to publish as PR
   - Checks if dataset already exists remotely
   - Creates PR only if not published
   - Shows "Already published" if exists

See [PUBLISH_FROM_DETAILS.md](PUBLISH_FROM_DETAILS.md) for complete documentation.

### Quick Setup

1. **Create a catalog repository** on GitHub (e.g., `your-org/mini-datahub-catalog`)
2. **Clone it locally**: `git clone https://github.com/your-org/mini-datahub-catalog.git`
3. **Generate a GitHub PAT** with `Contents: R/W`, `Pull requests: R/W` permissions
4. **Configure the app**:
   - Launch: `mini-datahub`
   - Press `S` for Settings
   - Fill in GitHub host, owner, repo, username, token
   - Set catalog repository path (absolute path to local clone)
   - Test connection, then Save

5. **Save a dataset** (press `A`, fill form, press `Ctrl+S`)
   - ✨ PR created automatically!
   - 🎉 Success toast with PR URL

### What Happens Automatically

When you save a dataset with GitHub configured:

1. **Writes** `data/<id>/metadata.yaml` to your local catalog repo
2. **Creates** a git branch: `add/<dataset-id>-<timestamp>`
3. **Commits** with message: `feat(dataset): add <id> — <name>`
4. **Pushes** to GitHub (central repo if you have push access, or your fork)
5. **Opens** a Pull Request with formatted description
6. **Adds** labels and reviewers (configurable)
7. **Shows** success notification with PR link

### Offline Handling

If offline or PR creation fails:
- Dataset **saved locally** ✅
- PR task **queued in Outbox** 📮
- Press `P` to view outbox
- Press `R` to retry when back online

### For Teams

**Contributors:**
- Clone catalog repo once
- Configure GitHub settings once
- Add datasets through TUI
- PRs created automatically

**Maintainers:**
- Review PRs on GitHub
- Check metadata accuracy, source URLs
- Approve and merge
- Changes sync to all team members

**See [GITHUB_WORKFLOW.md](GITHUB_WORKFLOW.md) for detailed setup guide and troubleshooting.**

## Development

```bash
# Install with dev dependencies using uv
uv sync --python /usr/bin/python --dev
source .venv/bin/activate

# Run tests
pytest

# Format code
black mini_datahub tests
ruff check mini_datahub tests

# Type checking
mypy mini_datahub

# Add new dependencies
uv add <package-name>
uv add --dev <dev-package>

# Update lock file
uv lock
```

**CI/CD:** Use `uv sync --frozen --dev` in CI to ensure reproducible builds with the lock file.

## How It Works

1. **Storage**: Each dataset is a folder with `metadata.yaml`
2. **Validation**: Changes validated against JSON Schema + Pydantic model
3. **Indexing**: Metadata indexed into SQLite FTS5 for fast search
4. **Search**: BM25-ranked full-text search across all text fields
5. **TUI**: Textual-based interface for keyboard-driven workflow

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

- **Local-first**: No server, no network dependencies (except optional URL probes)
- **YAML**: Human-readable, git-friendly, easy to edit manually
- **SQLite FTS5**: Fast, embedded, proven full-text search
- **Textual TUI**: Modern terminal UI with keyboard-first design
- **Pydantic + JSON Schema**: Belt-and-suspenders validation
- **Single binary ready**: Code structured for later PyInstaller/PyApp packaging

## Quality Gates & Testing

The test suite covers:
- ✅ Slug generation and ID collision handling
- ✅ Metadata validation (JSON Schema + Pydantic)
- ✅ YAML read/write operations
- ✅ Database operations (upsert, search, delete)
- ✅ Full-text search with BM25 ranking
- ✅ Reindexing from disk

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
- ✅ No network traffic unless user triggers HEAD probe
- ✅ Keyboard-accessible interface (Tab, Enter, shortcuts)
- ✅ Copy-to-clipboard and URL opening functionality

## Roadmap

- [x] Core search and add functionality
- [x] Metadata validation
- [x] FTS5 indexing with BM25
- [x] URL HEAD probe for format/size inference
- [ ] CSV field inference from URL samples
- [ ] Export to markdown/HTML catalog
- [ ] Git integration for version history
- [ ] Team sync via git push/pull

## Troubleshooting

**Database errors on startup?**
- Delete `db.sqlite` and run `mini-datahub reindex`

**Search not finding datasets?**
- Run `mini-datahub reindex` to rebuild the search index

**Validation errors?**
- Check that all required fields are filled
- Ensure ID follows slug format (lowercase, alphanumeric, dashes/underscores)
- Verify dates are in YYYY-MM-DD format

**Clipboard not working?**
- Install xclip (Linux) or ensure proper clipboard support

## License

MIT License - see LICENSE file

## Contributing

This is an MVP. Contributions welcome! Please:
1. Open an issue to discuss major changes
2. Follow existing code style (black + ruff)
3. Add tests for new functionality
4. Update documentation

---

**Built for teams who want to organize data without the overhead.**
