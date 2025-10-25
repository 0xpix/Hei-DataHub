# Root Files Guide

## Overview

This document explains the purpose and configuration of key files in the repository root. Understanding these files is essential for building, testing, and deploying Hei-DataHub.

---

## pyproject.toml

**Purpose:** Python project configuration (PEP 518/621)

**Location:** `/pyproject.toml`

**Key Sections:**

### Project Metadata

```toml
[project]
name = "hei-datahub"
version = "0.59.0-beta"
description = "Lightweight local data hub with TUI for managing datasets"
requires-python = ">=3.10"
```

**Versioning Strategy:**
- **Format:** `MAJOR.MINOR.PATCH-STAGE`
- **Example:** `0.59.0-beta`
- **Stages:** `alpha` → `beta` → `rc` → (release)

**Python Compatibility:**
- **Minimum:** 3.10 (for modern type hints)
- **Tested:** 3.10, 3.11, 3.12
- **Features used:** `match/case`, `|` for unions, `Self` type

### Dependencies

```toml
dependencies = [
    "textual>=0.47.0",        # TUI framework
    "pydantic>=2.0.0",        # Data validation
    "pyyaml>=6.0",            # YAML parsing
    "requests>=2.31.0",       # HTTP (WebDAV)
    "keyring>=24.0.0",        # Credential storage
    "tomli-w>=1.0.0",         # TOML writing
]
```

**Why These Dependencies?**

| Package | Purpose | Alternatives Considered |
|---------|---------|------------------------|
| `textual` | Terminal UI framework | `curses` (too low-level), `urwid` (less modern) |
| `pydantic` | Data validation with type hints | `marshmallow` (more verbose), `attrs` (no validation) |
| `keyring` | Secure credential storage | Direct Secret Service (too platform-specific) |
| `requests` | WebDAV HTTP client | `httpx` (async not needed), `urllib` (too low-level) |

### Optional Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",     # Testing framework
    "black>=23.0.0",     # Code formatting
    "ruff>=0.1.0",       # Fast linting
    "mypy>=1.7.0",       # Type checking
]
```

**Install dev dependencies:**
```bash
uv pip install -e ".[dev]"
```

### Scripts (Entry Points)

```toml
[project.scripts]
mini-datahub = "mini_datahub.cli.main:main"
hei-datahub = "mini_datahub.cli.main:main"
```

**Both commands** point to the same entry point (aliases for convenience).

**Usage:**
```bash
hei-datahub --help       # Preferred name
mini-datahub --help      # Legacy alias
```

### Package Data

```toml
[tool.setuptools.package-data]
mini_datahub = [
    "infra/sql/*.sql",       # Schema migrations
    "schema.json",           # JSON schema
    "version.yaml",          # Version metadata
    "ui/views/*.tcss",       # Textual CSS
    "ui/widgets/*.tcss",     # Widget styles
]
```

**Why include these?**
- `.sql` files: Database schema definitions
- `.tcss` files: Textual UI styles (like CSS for TUI)
- `schema.json`: Dataset metadata validation
- `version.yaml`: Runtime version checking

### Tool Configuration

#### Ruff (Linter)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

**What Ruff Checks:**
- `E`: PEP 8 errors
- `F`: Pyflakes errors (unused imports, undefined names)
- `I`: Import sorting (isort rules)
- `N`: Naming conventions
- `W`: Warnings

**Run linting:**
```bash
make lint
# or directly:
ruff check src/mini_datahub
```

#### Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**Test Discovery:**
- Searches `tests/` directory
- Files matching `test_*.py` or `*_test.py`
- Classes starting with `Test`
- Functions starting with `test_`

**Run tests:**
```bash
make test
# or with coverage:
make test-coverage
```

#### MyPy (Type Checker)

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Gradual typing
```

**Type Checking Strategy:**
- **Gradual typing:** Not all functions require types
- **Strict for new code:** Add types to new modules
- **Existing code:** Add types incrementally

**Run type checking:**
```bash
make lint  # Includes mypy
# or directly:
mypy src/mini_datahub
```

---

## Makefile

**Purpose:** Automation for common development tasks

**Location:** `/Makefile`

**Key Targets:**

### Installation

```makefile
install:  ## Install package in editable mode
	pip install -e .

dev-install:  ## Install with dev dependencies
	pip install -e ".[dev]"
```

**Usage:**
```bash
make install      # Production install
make dev-install  # Development install
```

**Why editable mode (`-e`)?**
- Changes to source code are immediately reflected
- No need to reinstall after each change
- Ideal for development

### Testing

```makefile
test:  ## Run tests
	pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	pytest tests/ -v --cov=mini_datahub --cov-report=html --cov-report=term
```

**Coverage reports:**
- **Terminal:** Summary in console
- **HTML:** Detailed report in `htmlcov/index.html`

**Usage:**
```bash
make test                # Run all tests
make test-coverage       # Run with coverage
open htmlcov/index.html  # View coverage report
```

### Code Quality

```makefile
lint:  ## Run linters (ruff + mypy)
	ruff check mini_datahub tests
	mypy mini_datahub || true

format:  ## Format code with black
	black mini_datahub tests
```

**Format before committing:**
```bash
make format   # Auto-format code
make lint     # Check for issues
```

### Cleanup

```makefile
clean:  ## Clean up generated files
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

clean-db:  ## Remove database
	rm -f db.sqlite db.sqlite-journal
```

**When to use:**
- `make clean`: After builds, before commits
- `make clean-db`: To reset search index

### Running the App

```makefile
run:  ## Launch the TUI
	hei-datahub

reindex:  ## Rebuild search index
	hei-datahub reindex
```

**Quick workflow:**
```bash
make dev-install   # Initial setup
make run           # Launch app
# Make changes...
make format        # Format code
make test          # Run tests
```

---

## schema.json

**Purpose:** JSON Schema for dataset metadata validation

**Location:** `/schema.json`

**Schema Version:** JSON Schema Draft 07

### Required Fields

```json
{
  "required": [
    "id",
    "dataset_name",
    "description",
    "source",
    "date_created",
    "storage_location"
  ]
}
```

**Why these fields are required:**

| Field | Reason |
|-------|--------|
| `id` | Unique identifier for indexing/storage |
| `dataset_name` | Human-readable name for display |
| `description` | Essential metadata for understanding data |
| `source` | Provenance tracking |
| `date_created` | Temporal tracking |
| `storage_location` | Where to find the actual data |

### Field Validation Rules

#### ID Field

```json
{
  "id": {
    "type": "string",
    "pattern": "^[a-z0-9][a-z0-9_-]*$",
    "minLength": 1,
    "maxLength": 100
  }
}
```

**Valid IDs:**
- `climate-data` ✅
- `ocean_temp_2024` ✅
- `dataset123` ✅

**Invalid IDs:**
- `Climate-Data` ❌ (uppercase)
- `-dataset` ❌ (starts with dash)
- `data set` ❌ (contains space)

#### Date Field

```json
{
  "date_created": {
    "type": "string",
    "format": "date"
  }
}
```

**Format:** ISO 8601 date (`YYYY-MM-DD`)

**Examples:**
- `2024-01-15` ✅
- `2024-12-31` ✅
- `01/15/2024` ❌ (wrong format)

### Optional Fields

```json
{
  "file_format": {
    "type": "string",
    "description": "CSV, JSON, Parquet, etc."
  },
  "tags": {
    "type": "array",
    "items": {"type": "string"}
  },
  "project": {
    "type": "string",
    "description": "Associated project name"
  }
}
```

**Usage in Pydantic:**

The schema is **mirrored** in `src/mini_datahub/core/models.py`:

```python
class DatasetMetadata(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$", max_length=100)
    dataset_name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    source: str
    date_created: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    storage_location: str
    file_format: str | None = None
    tags: list[str] = Field(default_factory=list)
    project: str | None = None
```

**Why duplicate?**
- `schema.json`: For external tools, documentation
- Pydantic model: For runtime validation in Python

---

## version.yaml

**Purpose:** Version metadata for runtime checks

**Location:** `/version.yaml`

**Format:**

```yaml
version: "0.59.0-beta"
release_name: "Privacy"
release_date: "2024-10-25"
minimum_db_version: "0.58.0"
```

**Usage:**

```python
from mini_datahub.utils.version import get_version

version = get_version()
print(f"Running Hei-DataHub v{version}")
```

**Version Compatibility Checks:**

```python
if db_version < minimum_db_version:
    print("Database schema outdated. Run migrations.")
```

---

## CHANGELOG.md

**Purpose:** Track all notable changes between versions

**Location:** `/CHANGELOG.md`

**Format:** [Keep a Changelog](https://keepachangelog.com/)

**Structure:**

```markdown
# Changelog

## [0.59.0-beta] - 2024-10-25

### Added
- New features

### Changed
- Modifications to existing features

### Deprecated
- Features being phased out

### Removed
- Deleted features

### Fixed
- Bug fixes

### Security
- Security improvements
```

**Entry Guidelines:**
- Use past tense ("Added", not "Add")
- Be specific, not vague
- Group by type (Added, Fixed, etc.)
- Link to issue numbers (#123)

**Example Entry:**

```markdown
### Added
- WebDAV authentication via Linux keyring (#145)
- Read-only mode for shared datasets (#152)

### Changed
- Search now uses FTS5 instead of FTS3 for better ranking (#148)

### Fixed
- Fix crash when WebDAV connection times out (#150)
```

---

## README.md

**Purpose:** Repository overview and quick start guide

**Location:** `/README.md`

**Sections:**

1. **Overview:** What is Hei-DataHub?
2. **Features:** Key capabilities
3. **Installation:** Quick install instructions
4. **Quick Start:** Minimal example
5. **Documentation:** Link to full docs
6. **Contributing:** How to contribute
7. **License:** MIT License

**Target Audience:**
- First-time visitors to the repo
- Users deciding whether to use the tool
- Contributors looking to get started

**Keep it concise:**
- Overview: 2-3 paragraphs
- Installation: 3-5 commands
- Quick Start: Minimal working example

---

## LICENSE

**Purpose:** Legal terms for using and distributing the software

**Location:** `/LICENSE`

**License Type:** MIT License

**Key Permissions:**
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Conditions:**
- Include license and copyright notice

**Limitations:**
- No liability
- No warranty

---

## .gitignore

**Purpose:** Specify files Git should ignore

**Location:** `/.gitignore`

**Key Patterns:**

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Virtual environments
venv/
.venv/

# IDE
.vscode/
.idea/

# Build artifacts
build/
dist/

# Testing
.pytest_cache/
htmlcov/
.coverage

# Local data
db.sqlite
db.sqlite-journal
*.log
```

**Why ignore these?**
- **Bytecode:** Generated, not source
- **Virtual envs:** User-specific
- **IDE files:** Personal preferences
- **Build artifacts:** Reproducible from source
- **Local data:** May contain sensitive info

---

## Development Workflow Files

### .pre-commit-config.yaml (Optional)

**Purpose:** Run checks before commits

**Example:**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
```

**Install:**
```bash
pip install pre-commit
pre-commit install
```

**Benefits:**
- Catch errors before CI
- Automatic formatting
- Consistent code style

### .github/workflows/ (CI/CD)

**Purpose:** Automated testing and deployment

**Example workflow:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - run: pip install -e ".[dev]"
      - run: make test
```

---

## Quick Reference

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `pyproject.toml` | Project config | Every feature (dependencies) |
| `Makefile` | Dev automation | Rarely |
| `schema.json` | Data validation | When adding fields |
| `version.yaml` | Version info | Every release |
| `CHANGELOG.md` | Change tracking | Every commit |
| `README.md` | User-facing docs | Every major feature |
| `LICENSE` | Legal terms | Never (set once) |
| `.gitignore` | Ignore patterns | When adding file types |

---

## Related Documentation

- **[Package Structure](package-structure.md)** - Source code organization
- **[Build Pipeline](../build/pipeline.md)** - Build and release process
- **[Contributing Workflow](../contributing/workflow.md)** - Development process

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
