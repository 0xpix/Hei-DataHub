# Contributing to Hei-DataHub

Thank you for your interest in contributing to Hei-DataHub! This guide will help you understand our development workflow, coding standards, and release process.

---

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Pull Request Workflow](#pull-request-workflow)
- [Bumping Version](#bumping-version)
- [Release Checklist](#release-checklist)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.9+** (Python 3.11+ recommended)
- **Git** with SSH key configured for GitHub
- **uv** (recommended) or pip for dependency management

### Quick Setup

```bash
# Clone the repository
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub

# Install dependencies (using uv)
uv sync

# Or using pip
pip install -e ".[dev]"

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install

# Verify installation
mini-datahub --version-info
```

For detailed setup instructions, see the [QUICKSTART.md](QUICKSTART.md) guide.

---

## 🔀 Pull Request Workflow

We use feature branches and the PR workflow documented in [PR_WORKFLOW_QUICKREF.md](PR_WORKFLOW_QUICKREF.md).

### Basic Steps

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   # Open PR on GitHub
   ```

4. **Address review feedback:**
   ```bash
   # Make changes
   git add .
   git commit -m "fix: address review comments"
   git push
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

---

## 🔢 Bumping Version

Hei-DataHub uses a **centralized version management system** with `version.yaml` as the single source of truth.

### Version Format

We follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH-PRERELEASE
```

Example: `0.55.5-beta`

- **MAJOR:** Breaking changes (rarely changed in beta)
- **MINOR:** New features, significant changes
- **PATCH:** Bug fixes, minor improvements
- **PRERELEASE:** `alpha`, `beta`, `rc1`, etc.

### How to Bump Version

**Step 1:** Edit `version.yaml`

```yaml
version: "0.56.0-beta"  # Update this line
codename: "Glacier"     # Optional: change codename
release_date: "2025-11-15"  # Update release date
# ... rest of file
```

**Step 2:** Run the sync script

```bash
python scripts/sync_version.py
```

This will automatically update:
- `src/mini_datahub/_version.py` (Python module)
- `docs/_includes/version.md` (Docs version banner)
- `build/version.json` (Build metadata)
- `pyproject.toml` (Package version)
- `src/mini_datahub/version.py` (Legacy wrapper)

**Step 3:** Verify changes

```bash
# Check what files changed
git status

# View generated version module
cat src/mini_datahub/_version.py

# Test import
python -c "from src.mini_datahub._version import __version__; print(__version__)"
```

**Step 4:** Update changelog

Add a new section to `docs/99-changelog.md`:

```markdown
## [0.56.0-beta] - 2025-11-15

### Added
- Your new features here

### Changed
- Your changes here

### Fixed
- Your bug fixes here
```

**Step 5:** Commit changes

```bash
git add version.yaml src/ docs/ build/ pyproject.toml
git commit -m "chore: bump version to 0.56.0-beta"
```

### Dry-Run Mode

To preview what would be updated without making changes:

```bash
python scripts/sync_version.py --dry-run
```

### Pre-commit Hook

If you've installed pre-commit hooks, the version sync will run automatically when you commit changes to `version.yaml`:

```bash
git add version.yaml
git commit -m "chore: bump version"
# Pre-commit hook runs sync_version.py automatically
```

---

## ✅ Release Checklist

Before creating a release PR, ensure:

- [ ] Version bumped in `version.yaml`
- [ ] `scripts/sync_version.py` executed successfully
- [ ] All generated version files committed
- [ ] `docs/99-changelog.md` updated with release notes
- [ ] Version banner renders correctly in docs (run `mkdocs serve`)
- [ ] All tests pass (run `pytest`)
- [ ] Documentation builds without errors (run `mkdocs build --strict`)
- [ ] PR includes summary of changes in description

### Release Types

**Patch Release (0.55.X):**
- Bug fixes
- Documentation improvements
- Performance improvements
- No new features

**Minor Release (0.X.0):**
- New features
- Non-breaking API changes
- Significant improvements

**Major Release (X.0.0):**
- Breaking changes
- Complete rewrites
- API incompatibilities

---

## 📝 Coding Standards

### Python Style

- **PEP 8** compliant (enforced by pre-commit hooks)
- **Type hints** for function signatures (Python 3.9+ syntax)
- **Docstrings** for public functions/classes (Google style)

Example:

```python
def validate_dataset(metadata: dict[str, Any]) -> ValidationResult:
    """Validate dataset metadata against schema.

    Args:
        metadata: Dataset metadata dictionary from YAML file

    Returns:
        ValidationResult with errors/warnings if validation fails

    Raises:
        ValidationError: If metadata structure is invalid
    """
    pass
```

### Import Organization

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import yaml
from textual.app import App

# Local application
from mini_datahub.core.models import Dataset
from mini_datahub.infra.db import Database
```

### Error Handling

Use custom exceptions from `core.errors`:

```python
from mini_datahub.core.errors import DatasetNotFoundError

def get_dataset(dataset_id: str) -> Dataset:
    dataset = db.find_by_id(dataset_id)
    if not dataset:
        raise DatasetNotFoundError(f"Dataset '{dataset_id}' not found")
    return dataset
```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mini_datahub

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v
```

### Test Structure

```python
import pytest
from mini_datahub.core.models import Dataset

def test_dataset_validation():
    """Test dataset metadata validation."""
    dataset = Dataset(
        id="test-data",
        name="Test Dataset",
        description="Test description"
    )
    assert dataset.validate() is True

def test_invalid_dataset_id():
    """Test that invalid IDs raise ValidationError."""
    with pytest.raises(ValidationError):
        Dataset(id="Invalid ID!", name="Test")
```

### Test Coverage

- Aim for **80%+ coverage** for core modules
- All public API functions should have tests
- Edge cases and error handling must be tested

---

## 🆘 Getting Help

- **Issues:** [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Discussions:** [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
- **Documentation:** [Hei-DataHub Manual](https://0xpix.github.io/Hei-DataHub/)

---

## 📄 License

By contributing to Hei-DataHub, you agree that your contributions will be licensed under the MIT License.
