# Your First Contribution

This guide walks you through making your first contribution to Hei-DataHub. Choose a path that matches your interest:

## Choose Your First Contribution

### Option 1: Fix a Typo in Documentation (Easiest)
**Time:** 10 minutes | **Difficulty:** ⭐

Perfect for learning the GitHub workflow without touching code.

[Jump to Documentation Fix](#option-1-fix-documentation)

---

### Option 2: Add a Test Case (Beginner-Friendly)
**Time:** 20 minutes | **Difficulty:** ⭐⭐

Learn the codebase by adding a test for existing functionality.

[Jump to Add Test](#option-2-add-a-test-case)

---

### Option 3: Fix a Simple Bug (Intermediate)
**Time:** 30-60 minutes | **Difficulty:** ⭐⭐⭐

Fix a real issue and make an immediate impact.

[Jump to Bug Fix](#option-3-fix-a-simple-bug)

---

### Option 4: Add a UI Keybinding (Fun!)
**Time:** 30 minutes | **Difficulty:** ⭐⭐

Make the TUI more powerful with a custom keyboard shortcut.

[Jump to Add Keybinding](#option-4-add-a-ui-keybinding)

---

## Prerequisites

For all options:

- [x] Completed [Getting Started](getting-started.md)
- [x] App runs successfully: `hei-datahub --version`
- [x] You have a GitHub account

---

## Option 1: Fix Documentation

**Goal:** Fix a typo or improve clarity in the documentation.

**What You'll Learn:** GitHub workflow, markdown, documentation structure

### Step 1: Find Something to Fix

Browse the documentation in `docs/` or `dev-docs/`:

```bash
# Look for typos, unclear explanations, or outdated info
ls docs/
ls dev-docs/
```

Common issues:
- Typos or grammar mistakes
- Broken links
- Outdated version numbers
- Missing examples
- Unclear instructions

### Step 2: Create a Branch

```bash
git checkout main
git pull origin main
git checkout -b docs/fix-typo-in-auth-guide
```

### Step 3: Make the Fix

Edit the file in your text editor:

```bash
# Example: Fix a typo in the auth guide
nano docs/installation/authentication.md
```

Make your change, save the file.

### Step 4: Commit and Push

```bash
git add docs/installation/authentication.md
git commit -m "docs: fix typo in authentication guide"
git push origin docs/fix-typo-in-auth-guide
```

### Step 5: Open Pull Request

1. Go to https://github.com/0xpix/Hei-DataHub
2. Click "Compare & pull request"
3. Describe your fix
4. Submit!

**You're done!** 🎉 You've made your first contribution.

---

## Option 2: Add a Test Case

**Goal:** Add a test for existing functionality to improve code coverage.

**What You'll Learn:** Testing with pytest, understanding the codebase, test-driven development

### Step 1: Find Untested Code

```bash
# Check current test coverage
make test-coverage

# Look for files with low coverage
# Example: auth module might need more tests
```

### Step 2: Create a Branch

```bash
git checkout -b test/add-auth-validation-tests
```

### Step 3: Write a Simple Test

Create or edit a test file in `tests/`:

```python
# tests/auth/test_validator.py
import pytest
from hei_datahub.auth.validator import validate_webdav_connection


def test_validate_with_valid_credentials_returns_true():
    """Test that valid credentials pass validation."""
    # This is a simple test - you can expand it
    result = validate_webdav_connection(
        url="https://heibox.uni-heidelberg.de/remote.php/dav",
        username="test_user",
        password="test_pass",
        timeout=5
    )
    # Add assertions based on expected behavior
    assert isinstance(result, bool)


def test_validate_with_empty_url_raises_error():
    """Test that empty URL raises ValueError."""
    with pytest.raises(ValueError):
        validate_webdav_connection(
            url="",
            username="user",
            password="pass"
        )
```

### Step 4: Run Your Test

```bash
pytest tests/auth/test_validator.py -v
```

### Step 5: Commit and Push

```bash
git add tests/auth/test_validator.py
git commit -m "test(auth): add validation tests for WebDAV credentials"
git push origin test/add-auth-validation-tests
```

### Step 6: Open Pull Request

Follow Step 5 from Option 1.

---

## Option 3: Fix a Simple Bug

**Goal:** Fix a real bug from the issue tracker.

**What You'll Learn:** Debugging, problem-solving, working with existing code

### Step 1: Find a Bug

1. Go to [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
2. Filter by `bug` and `good first issue` labels
3. Pick one that looks interesting
4. Comment: "I'd like to work on this"
5. Wait for maintainer confirmation

### Step 2: Reproduce the Bug

```bash
# Follow the reproduction steps in the issue
# Example: If it's a crash on empty search
hei-datahub
# Try the broken behavior
```

### Step 3: Find the Code

Use the codebase overview to locate relevant files:

```bash
# Example: Search crash might be in services/fast_search.py
grep -r "def search" src/hei_datahub/services/
```

### Step 4: Create a Branch

```bash
git checkout -b fix/search-crash-on-empty-query
```

### Step 5: Fix the Bug

```python
# Example fix in src/hei_datahub/services/fast_search.py

def search_datasets(query: str) -> list[Dataset]:
    """Search for datasets matching the query."""
    # Add validation to prevent crash
    if not query or not query.strip():
        return []  # Return empty list instead of crashing

    # Rest of the search logic...
```

### Step 6: Add a Regression Test

```python
# tests/services/test_fast_search.py

def test_search_with_empty_query_returns_empty_list():
    """Test that empty query doesn't crash and returns empty list."""
    result = search_datasets("")
    assert result == []

    result = search_datasets("   ")  # Whitespace only
    assert result == []
```

### Step 7: Test Your Fix

```bash
# Run all tests
make test

# Run the app manually to verify
hei-datahub
# Try the previously broken behavior
```

### Step 8: Commit and Push

```bash
git add src/hei_datahub/services/fast_search.py
git add tests/services/test_fast_search.py
git commit -m "fix(search): prevent crash on empty query

- Add validation for empty/whitespace queries
- Return empty list instead of crashing
- Add regression test

Fixes #123"

git push origin fix/search-crash-on-empty-query
```

### Step 9: Open Pull Request

1. Reference the issue: "Fixes #123"
2. Explain what caused the bug
3. Explain your fix
4. Show before/after behavior

---

## Option 4: Add a UI Keybinding

**Goal:** Add a **`Ctrl+H`** keybinding that shows a "Hello from [Your Name]" message.

**What You'll Learn:** UI development with Textual, event handling, keybindings

### Step 1: Create a Branch

```bash
git checkout main
git pull origin main
git checkout -b ui/add-hello-keybinding
```

### Step 2: Understand What We're Changing

We need to modify **two files**:

1. **`src/hei_datahub/ui/views/main_view.py`** - Add the keybinding handler
2. **`src/hei_datahub/ui/views/help_screen.py`** - Document the new key in help

### Step 3: Add the Keybinding Handler

Open `src/hei_datahub/ui/views/main_view.py`:

```python
# Find the BINDINGS list (around line 20-40)
BINDINGS = [
    ("j", "move_down", "Down"),
    ("k", "move_up", "Up"),
    ("q", "quit", "Quit"),
    ("/", "search", "Search"),
    ("ctrl+h", "say_hello", "Say Hello"),  # Add this line
]
```

Add the handler method:

```python
def action_say_hello(self) -> None:
    """Show a hello message."""
    from hei_datahub.ui.widgets.notification import show_notification

    # Replace "Developer" with your name!
    show_notification(
        self,
        "Hello from Developer!",
        severity="info"
    )
```

### Step 4: Update Help Screen

Open `src/hei_datahub/ui/views/help_screen.py`:

```python
KEYBINDINGS = [
    # ... existing bindings ...
    ("Ctrl+H", "Show hello message", "General"),
]
```

### Step 5: Test Your Change

```bash
# Run the app
hei-datahub

# Press Ctrl+H to see the message
# Press ? to check the help screen
```

### Step 6: Write a Test

Create `tests/ui/test_hello_keybinding.py`:

```python
"""Test for the hello keybinding."""
from hei_datahub.ui.views.main_view import MainView


def test_hello_action_exists():
    """Verify the say_hello action exists."""
    view = MainView()
    assert hasattr(view, 'action_say_hello')
```

Run it:

```bash
pytest tests/ui/test_hello_keybinding.py -v
```

### Step 7: Commit and Push

```bash
git add src/hei_datahub/ui/views/main_view.py
git add src/hei_datahub/ui/views/help_screen.py
git add tests/ui/test_hello_keybinding.py

git commit -m "feat(ui): add Ctrl+H keybinding for hello message

- Added action_say_hello handler in MainView
- Updated help screen with new keybinding
- Added test coverage"

git push origin ui/add-hello-keybinding
```

### Step 8: Open Pull Request

1. Go to https://github.com/0xpix/Hei-DataHub
2. Click "Compare & pull request"
3. Fill in the template:
   - **What**: Added Ctrl+H keybinding
   - **Why**: Learning exercise for first contribution
   - **How**: Added handler method and updated help
4. Submit!

---

## What's Next?

After your first contribution:

1. **Explore Issues**: Look for `good first issue` labels
2. **Read the Codebase**: Check out [Module Walkthrough](../codebase/module-walkthrough.md)
3. **Join Discussions**: Ask questions, share ideas
4. **Improve Your Skills**: Try more complex contributions

### Contribution Ideas

**Easy:**
- Fix typos in documentation
- Add missing docstrings
- Improve error messages
- Add more test cases

**Intermediate:**
- Add CLI command aliases
- Improve autocomplete suggestions
- Add new export formats
- Optimize slow queries

**Advanced:**
- Implement new data sources
- Add plugin system
- Improve sync algorithm
- Performance optimizations

---

## Getting Help

**Stuck?** No problem!

- **Documentation**: Read [Architecture Overview](../architecture/overview.md)
- **Code Questions**: Comment on the issue
- **Setup Issues**: Check [Development Setup](development-setup.md)
- **General Help**: [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
3. Click it and fill in the PR template:
   - **Title**: `feat(ui): Add Ctrl+H keybinding for hello message`
   - **Description**: Explain what you changed and why
   - **Screenshots**: (Optional) Show the notification in action
4. Click "Create Pull Request"

## Step 9: Code Review

A maintainer will review your PR and might:

- ✅ **Approve**: Your changes are merged! 🎉
- 💬 **Request Changes**: Make the suggested changes and push again
- ❌ **Close**: Rare, usually if duplicate or doesn't fit project direction

## What You Learned

- ✅ How to navigate the codebase
- ✅ Textual's action/keybinding system
- ✅ Project commit conventions
- ✅ Testing workflow
- ✅ Git workflow (branch, commit, push, PR)

## Next Challenges

Want to do more? Try:

1. **Add a counter**: Make the hello message show "Hello #1", "Hello #2", etc.
2. **Make it configurable**: Let users set their name in config
3. **Add a timestamp**: Show when the message was triggered
4. **Different messages**: Randomize the greeting

## Common Mistakes to Avoid

- ❌ **Not testing**: Always run the app and tests before committing
- ❌ **Too many changes**: Keep PRs focused on one thing
- ❌ **No description**: Explain *why* you made the change
- ❌ **Pushing to main**: Always use feature branches

---

**Next**: [Common Development Tasks →](common-tasks.md)
