# Quick Start Guide for Hei-DataHub

This guide will help you get Hei-DataHub up and running in minutes.

## Prerequisites

- Python 3.9 or later
- UV (Python package installer)
- Terminal/Command line access

## Installation Steps

### Option 1: Automated Setup (Recommended)

```bash
# Navigate to the project directory
cd Hei-DataHub

# Run the setup script
./scripts/setup_dev.sh

# Activate the virtual environment
source .venv/bin/activate

# Launch the TUI
hei-datahub
```

### Option 2: Manual Setup

```bash
# Navigate to the project directory
cd Hei-DataHub

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install the package
pip install -e .

# Launch the TUI
hei-datahub
```

## First Run

When you first launch `hei-datahub`, the application will:

1. Initialize the SQLite database (`db.sqlite`)
2. Create the necessary tables (FTS5 search index)
3. Index the example dataset(s) from the `data/` folder
4. Open the Home screen with search functionality

## Using the TUI

### Home Screen (Search)
- **Type to search**: Just start typing in the search box
- **Navigate results**: Use arrow keys or Tab
- **Open details**: Press Enter on a selected result
- **Add new dataset**: Press `a`
- **Quit**: Press `q`

### Add Dataset Screen
- **Fill the form**: Use Tab to move between fields
- **Required fields** (marked):
  - Dataset Name
  - Description
  - Source (URL or snippet)
  - Storage Location
- **Auto-generate ID**: Leave ID field empty to auto-generate from name
- **URL Probe**: Click "Probe URL" to auto-detect format and size
- **Save**: Press Ctrl+S or click "Save Dataset"
- **Cancel**: Press Escape or click "Cancel"

### Details Screen
- **View metadata**: See all dataset information
- **Copy source**: Press `c` to copy source to clipboard
- **Open URL**: Press `o` to open source URL in browser
- **Go back**: Press Escape or `b`

## Command Line Usage

```bash
# Launch TUI (default)
hei-datahub

# Rebuild search index from YAML files
hei-datahub reindex

# Show version
hei-datahub --version
```

## Verify Installation

### Check that files exist:
```bash
# Python package modules
ls mini_datahub/*.py

# Example dataset
ls data/example-weather/metadata.yaml

# Schema files
ls schema.json sql/schema.sql
```

### Run tests:
```bash
# Install dev dependencies if not already installed
pip install -e ".[dev]"

# Run the test suite
pytest tests/ -v
```

Expected output: All tests should pass ✓

## Example Workflow

### 1. Search for the example dataset
```bash
hei-datahub
# Type "weather" in the search box
# Press Enter on the result
```

### 2. Add a new dataset
```bash
# Press 'a' from the home screen
# Fill in:
#   Name: "My Test Dataset"
#   Description: "A test dataset for learning"
#   Source: "https://example.com/data.csv"
#   Storage: "/local/data/test"
# Press Ctrl+S to save
```

### 3. Search for your new dataset
```bash
# You'll be taken to the details screen
# Press 'b' to go back
# Search for "test" - your dataset should appear
```

### 4. Reindex if needed
```bash
# Exit the TUI (press 'q')
hei-datahub reindex
# Should show: "✓ Successfully indexed N dataset(s)"
```

## Troubleshooting

### "Command not found: hei-datahub"
- Make sure you activated the virtual environment
- Run: `source .venv/bin/activate`

### Database errors on startup
- Delete the database: `rm db.sqlite`
- Reindex: `hei-datahub reindex`

### Search returns no results
- Reindex: `hei-datahub reindex`
- Check that datasets exist: `ls data/*/metadata.yaml`

### Import errors (pydantic, textual, etc.)
- Reinstall dependencies: `pip install -e .`
- Or use the setup script: `./scripts/setup_dev.sh`

### Clipboard doesn't work (Linux)
- Install xclip: `sudo apt-get install xclip`
- Or xsel: `sudo apt-get install xsel`

## Next Steps

1. **Explore the example dataset**: Search for "weather" and view its details
2. **Add your own datasets**: Press `a` and fill in the form
3. **Edit metadata manually**: Open `data/<id>/metadata.yaml` in your editor
4. **Reindex after manual edits**: Run `hei-datahub reindex`
5. **Customize**: Modify the JSON schema to add custom fields
6. **Run tests**: Use `pytest tests/ -v` to verify functionality

## File Locations

- **Configuration**: `pyproject.toml`
- **Database**: `db.sqlite` (created on first run)
- **Datasets**: `data/<dataset-id>/metadata.yaml`
- **Schema**: `schema.json`
- **SQL Schema**: `sql/schema.sql`
- **Tests**: `tests/test_basic.py`

## Support

- Check the README.md for detailed documentation
- Review the test suite for usage examples
- Open an issue on GitHub for bugs or feature requests

---

**Happy data organizing! 🎉**
