# Contributor Workflow

## End-to-End Contribution Process

This guide walks you through contributing code to Hei-DataHub, from picking an issue to getting your PR merged.

---

## Prerequisites

Before you start:

- ✅ Read [System Overview](../architecture/overview.md) to understand the architecture
- ✅ Read [Module Map](../architecture/module-map.md) to know where code lives
- ✅ Have Python 3.9+ installed
- ✅ Have `uv` installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- ✅ Have Git configured with your name and email

---

## Step 1: Find or Create an Issue

### Browse Existing Issues

Visit [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)

**Good first issues:**
- Filter by label: `good first issue`
- Look for: Small bug fixes, documentation improvements, test additions

**Before starting work:**
- Comment on the issue: "I'd like to work on this"
- Wait for maintainer confirmation (avoid duplicate work)

### Create a New Issue

If you found a bug or want to propose a feature:

1. Search existing issues first (avoid duplicates)
2. Use issue template (bug report or feature request)
3. Provide context: What? Why? How?
4. Wait for triage and feedback

---

## Step 2: Fork and Clone

### Fork the Repository

1. Go to [github.com/0xpix/Hei-DataHub](https://github.com/0xpix/Hei-DataHub)
2. Click **Fork** button (top-right)
3. Wait for fork to complete

### Clone Your Fork

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Hei-DataHub.git
cd Hei-DataHub

# Add upstream remote
git remote add upstream https://github.com/0xpix/Hei-DataHub.git

# Verify remotes
git remote -v
# origin    https://github.com/YOUR_USERNAME/Hei-DataHub.git (fetch)
# upstream  https://github.com/0xpix/Hei-DataHub.git (fetch)
```

---

## Step 3: Set Up Development Environment

### Install Dependencies

```bash
# Install dependencies using uv (fast and reproducible)
uv sync --dev

# Activate virtual environment
source .venv/bin/activate

# Verify installation
hei-datahub --version
```

### Alternative: Traditional pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Verify Setup

```bash
# Run tests to ensure everything works
make test

# Run linters
make lint

# Try the TUI
hei-datahub
```

---

## Step 4: Create a Feature Branch

**Never work directly on `main` or `docs/devs`.**

### Branch Naming Convention

```bash
# Format: <type>/<short-description>
git checkout -b feature/add-dataset-export
git checkout -b fix/search-crash-on-empty-query
git checkout -b docs/api-reference-for-search
git checkout -b refactor/extract-git-operations
```

**Branch prefixes:**
- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation only
- `refactor/` — Code refactoring (no behavior change)
- `test/` — Adding/fixing tests
- `chore/` — Maintenance (deps, tooling, etc.)

---

## Step 5: Make Your Changes

### Understand the Module

Before coding:

1. **Find the relevant module:** Check [Module Map](../architecture/module-map.md)
2. **Read the API reference:** See [API Reference](../api-reference/overview.md)
3. **Trace data flow:** See [Data Flow](../architecture/data-flow.md)
4. **Check tests:** Look at existing tests in `tests/`

### Write Code

**Follow these principles:**

- ✅ **Follow Clean Architecture:** Core has no I/O, Services orchestrate, Infrastructure handles I/O
- ✅ **Type hints:** Use type annotations for all functions
- ✅ **Docstrings:** Document public functions (Google style)
- ✅ **Error handling:** Use explicit exceptions or Result types
- ✅ **Immutability:** Prefer immutable data structures (Pydantic models)

**Example:**

```python
# Good
def search_datasets(query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dataset]:
    """
    Search datasets using FTS5 full-text search.
    
    Args:
        query: Search query string (FTS5 syntax)
        filters: Optional filters (tags, date range, etc.)
    
    Returns:
        List of matching datasets, sorted by relevance
        
    Raises:
        SearchError: If query syntax is invalid
        DatabaseError: If database connection fails
    """
    # Implementation...
```

### Write Tests

**Every code change must include tests.**

#### Test Strategy

| Layer | Test Type | Example |
|-------|-----------|---------|
| Core | Unit tests (pure functions) | `test_validate_dataset_name()` |
| Services | Integration tests (with mocks) | `test_search_service_with_filters()` |
| Infrastructure | Integration tests (with fixtures) | `test_db_connection()` |
| UI | Integration tests (Textual pilot) | `test_home_view_navigation()` |

#### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/services/test_search.py -v

# Run with coverage
make test-coverage

# Run only fast tests (skip integration)
pytest -m "not integration"
```

#### Writing Tests

```python
# tests/services/test_search.py
import pytest
from mini_datahub.services import search
from mini_datahub.core.models import Dataset

def test_search_with_query_returns_matching_datasets():
    """Test that search returns datasets matching the query."""
    # Arrange
    query = "precipitation"
    
    # Act
    results = search.search_datasets(query)
    
    # Assert
    assert len(results) > 0
    assert all("precipitation" in d.title.lower() for d in results)

def test_search_with_invalid_query_raises_error():
    """Test that invalid query syntax raises SearchError."""
    with pytest.raises(search.SearchError):
        search.search_datasets("invalid: query:")
```

---

## Step 6: Run Quality Checks

Before committing:

```bash
# Format code (auto-fix)
make format

# Run linters
make lint

# Run tests
make test

# Check test coverage (aim for 80%+)
make test-coverage
```

**Fix all issues before proceeding.**

---

## Step 7: Commit Your Changes

### Commit Message Convention

We use **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code refactoring
- `test`: Adding/fixing tests
- `chore`: Maintenance

**Examples:**

```bash
# Good commits
git commit -m "feat(search): add support for date range filters"
git commit -m "fix(db): prevent connection leak on error"
git commit -m "docs(api): add reference for services.publish"

# With body and footer
git commit -m "feat(ui): add dataset export to CSV

- Add export_to_csv method in services
- Add 'Export' button in details view
- Add keybinding Ctrl+E for export

Closes #123"
```

### Commit Best Practices

- ✅ **Atomic commits:** One logical change per commit
- ✅ **Test before committing:** All tests pass
- ✅ **Write descriptive messages:** Explain *what* and *why*, not *how*
- ✅ **Reference issues:** Use `Closes #123` or `Fixes #456`

---

## Step 8: Push to Your Fork

```bash
# Push your branch
git push origin feature/add-dataset-export

# If you've already pushed and need to update
git push origin feature/add-dataset-export --force-with-lease
```

---

## Step 9: Open a Pull Request

### Create the PR

1. Go to [github.com/0xpix/Hei-DataHub/pulls](https://github.com/0xpix/Hei-DataHub/pulls)
2. Click **New Pull Request**
3. Click **compare across forks**
4. Select:
   - **Base repository:** `0xpix/Hei-DataHub`
   - **Base branch:** `main`
   - **Head repository:** `YOUR_USERNAME/Hei-DataHub`
   - **Compare branch:** `feature/add-dataset-export`
5. Click **Create Pull Request**

### PR Title and Description

**Title format:** Same as commit convention

```
feat(search): add support for date range filters
```

**Description template:**

```markdown
## What
Brief summary of what this PR does.

## Why
Explain the motivation (reference issue if applicable).

## How
High-level overview of implementation approach.

## Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Manual testing done
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Docstrings added for new functions
- [ ] Updated relevant documentation
- [ ] Changelog updated (if applicable)

## Screenshots (if UI change)
(Optional)

## Related Issues
Closes #123
```

---

## Step 10: Code Review

### What to Expect

- **Maintainers will review** within 1-3 business days
- **CI checks will run:** Tests, linting, build verification
- **Feedback:** Suggestions for improvements

### Responding to Feedback

```bash
# Make requested changes
git checkout feature/add-dataset-export

# Edit code
# Run tests
make test

# Commit changes
git commit -m "refactor: extract date parsing logic"

# Push updates
git push origin feature/add-dataset-export
```

**PR will auto-update with new commits.**

### Review Checklist (Maintainers Check)

See [Code Review Guide](code-review.md) for full checklist.

---

## Step 11: Merge

Once approved:

1. **Maintainer merges** your PR (squash or merge commit)
2. **Your contribution is live!** 🎉
3. **Delete your branch:**
   ```bash
   git branch -d feature/add-dataset-export
   git push origin --delete feature/add-dataset-export
   ```

---

## Step 12: Stay Synced

### Keep Your Fork Updated

```bash
# Fetch upstream changes
git checkout main
git fetch upstream
git merge upstream/main

# Push to your fork
git push origin main
```

### Rebasing Your Branch (If Needed)

If `main` has moved forward while you were working:

```bash
git checkout feature/add-dataset-export
git rebase main

# Resolve conflicts if any
# Then force-push (safe because it's your branch)
git push origin feature/add-dataset-export --force-with-lease
```

---

## Common Scenarios

### Scenario 1: I Want to Work on Multiple Issues

Create separate branches:

```bash
git checkout main
git pull upstream main
git checkout -b fix/issue-123

# Work, commit, push, open PR

# Start second issue
git checkout main
git checkout -b feature/issue-456
```

### Scenario 2: My PR Has Merge Conflicts

```bash
git checkout feature/my-branch
git fetch upstream
git rebase upstream/main

# Resolve conflicts
# Edit conflicting files
git add <resolved-files>
git rebase --continue

# Force-push
git push origin feature/my-branch --force-with-lease
```

### Scenario 3: I Want to Update My PR After Review

Just commit and push to the same branch:

```bash
git checkout feature/my-branch
# Make changes
git commit -m "address review feedback"
git push origin feature/my-branch
```

---

## Getting Help

- **Stuck on setup?** → [Installation Guide](../../docs/20-tutorials/01-installation.md)
- **Confused about architecture?** → [System Overview](../architecture/overview.md)
- **Not sure where code goes?** → [Module Map](../architecture/module-map.md)
- **Questions?** → [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)

---

## Next Steps

- Read [Code Review Guide](code-review.md) to understand review criteria
- Check [Definition of Done](definition-of-done.md) to know when a feature is complete
- Review [Commit Conventions](commits.md) for detailed commit message guidelines

---

**Thank you for contributing!** 🙏
