# Common Development Tasks

Quick reference for everyday development tasks.

## Running the Application

### Standard Run
```bash
hei-datahub
```

### With Debug Logging
```bash
hei-datahub --verbose
```

### With Specific Config
```bash
hei-datahub --config /path/to/config.yaml
```

### In Development Mode (Auto-reload)
```bash
# Install watchdog first
uv add --dev watchdog

# Run with auto-reload
watchmedo auto-restart --patterns="*.py" --recursive -- python -m hei_datahub.cli.main
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_search_integration.py
```

### Run Tests with Coverage
```bash
pytest --cov=hei_datahub --cov-report=html
# Open htmlcov/index.html to see coverage report
```

### Run Tests in Watch Mode
```bash
pytest-watch
```

### Run Only Failed Tests
```bash
pytest --lf  # last failed
```

## Code Quality

### Format Code (Black)
```bash
black src/ tests/
```

### Sort Imports (isort)
```bash
isort src/ tests/
```

### Lint (Ruff)
```bash
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Checking (mypy)
```bash
mypy src/hei_datahub
```

### Run All Quality Checks
```bash
make lint  # or
./scripts/lint.sh
```

## Database Operations

### Reset Database
```bash
rm db.sqlite
hei-datahub  # Will recreate on startup
```

### Inspect Database
```bash
sqlite3 db.sqlite

# Inside SQLite shell:
.tables          # List all tables
.schema datasets # Show table schema
SELECT * FROM datasets LIMIT 5;  # Query data
.exit            # Exit
```

### Backup Database
```bash
cp db.sqlite db.sqlite.backup
```

### Run Migrations (if needed)
```bash
# Migrations are auto-applied on startup
# To manually run:
python -m hei_datahub.infra.db migrate
```

## Working with Datasets

### Add a Test Dataset
```bash
mkdir -p data/my-test-dataset
cat > data/my-test-dataset/metadata.yaml << 'EOF'
name: my-test-dataset
title: My Test Dataset
description: Testing dataset functionality
tags:
  - test
  - development
EOF

# Re-index
hei-datahub
# Press 'r' to refresh catalog
```

### Validate Dataset Metadata
```bash
python scripts/ops/catalog_validate.py data/my-test-dataset
```

## Git Workflow

### Create Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

### Commit Changes
```bash
# Stage specific files
git add src/hei_datahub/services/search.py

# Or stage all changes
git add .

# Commit with conventional commit format
git commit -m "feat(search): Add fuzzy matching support"
```

### Sync with Main
```bash
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main  # or git merge main
```

### Push Branch
```bash
git push origin feature/my-feature
```

## Debugging

### Print Debug Info
```python
# Add anywhere in the code
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {my_var}")
```

### Use Textual Console
```bash
# Terminal 1: Start console
textual console

# Terminal 2: Run app
hei-datahub

# Console will show Textual debug output
```

### Use pdb (Python Debugger)
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or in Python 3.7+
breakpoint()
```

### Debug Tests
```bash
pytest --pdb  # Drop into debugger on failure
pytest -s     # Show print statements
```

## Documentation

### Build User Docs (main branch)
```bash
git checkout main
cd docs
mkdocs serve
# Open http://127.0.0.1:8000
```

### Build Dev Docs (docs/devs branch)
```bash
git checkout docs/devs
mkdocs serve -f mkdocs-dev.yml
# Open http://127.0.0.1:8000
```

### Update Version
```bash
# Edit version.yaml
python scripts/sync_version.py
# Commits automatically updated
```

## Performance Profiling

### Profile Startup Time
```bash
python bench/startup_bench.py
```

### Profile Specific Function
```python
import cProfile
import pstats

cProfile.run('my_function()', 'profile_output')
stats = pstats.Stats('profile_output')
stats.sort_stats('cumtime')
stats.print_stats(20)  # Top 20 functions
```

### Memory Profiling
```bash
pip install memory_profiler

# Add @profile decorator to function
python -m memory_profiler src/hei_datahub/services/search.py
```

## Useful Scripts

### Show Current Config
```bash
python scripts/show_config.py
```

### Verify Installation
```bash
bash scripts/verify_installation.sh
```

### Project Overview
```bash
bash scripts/project_overview.sh
```

## Environment Variables

### Useful Dev Variables
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Use different config location
export HEI_DATAHUB_CONFIG=/tmp/test-config.yaml

# Use different database
export HEI_DATAHUB_DB=/tmp/test.db
```

## IDE Setup

### VSCode Tasks
Press `Ctrl+Shift+P` and search for "Tasks: Run Task":

- **Run Application**: Start hei-datahub
- **Run Tests**: Execute pytest
- **Format Code**: Run black + isort
- **Lint**: Run ruff

### PyCharm Run Configurations
1. Add Python configuration
2. Script path: `src/hei_datahub/cli/main.py`
3. Working directory: project root
4. Python interpreter: `.venv/bin/python`

## Troubleshooting Common Issues

### "ModuleNotFoundError: No module named 'hei_datahub'"
```bash
# Reinstall in editable mode
uv sync --dev
```

### "Permission denied" on scripts
```bash
chmod +x scripts/*.sh
```

### "Database is locked"
```bash
# Close all running instances
pkill -f hei-datahub

# Or delete the lock file
rm db.sqlite-journal
```

### Tests Failing After Rebase
```bash
# Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear
```

## Quick Reference Card

| Task | Command |
|------|---------|
| Run app | `hei-datahub` |
| Run tests | `pytest` |
| Format code | `black src/ tests/` |
| Lint | `ruff check src/` |
| New branch | `git checkout -b feature/name` |
| Commit | `git commit -m "type(scope): msg"` |
| Reset DB | `rm db.sqlite` |
| Debug console | `textual console` |

---

**Next**: [Codebase Tour →](../codebase/overview.md)
