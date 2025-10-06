# Your First Contribution

This guide walks you through making a simple contribution to get familiar with the codebase and workflow. We'll add a new keybinding to the TUI.

## Goal

Add a **`Ctrl+H`** keybinding that shows a "Hello from [Your Name]" message in the app.

**Time Estimate**: 30 minutes

## Prerequisites

- [x] Completed [Getting Started](getting-started.md)
- [x] App runs successfully
- [x] You have a GitHub account

## Step 1: Create a Feature Branch

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Create a new branch
git checkout -b feature/hello-keybinding
```

**Naming Convention**: Use `feature/`, `fix/`, or `docs/` prefix for branches.

## Step 2: Understand What We're Changing

We need to modify **two files**:

1. **`src/mini_datahub/ui/views/main_view.py`** - Add the keybinding handler
2. **`src/mini_datahub/ui/views/help_screen.py`** - Document the new key in help

### Find the Files

```bash
# View the main view file
cat src/mini_datahub/ui/views/main_view.py | head -50
```

## Step 3: Add the Keybinding Handler

Open `src/mini_datahub/ui/views/main_view.py` in your editor.

### Find the Bindings Section

Look for the `BINDINGS` list (around line 20-40):

```python
BINDINGS = [
    ("j", "move_down", "Down"),
    ("k", "move_up", "Up"),
    ("q", "quit", "Quit"),
    ("/", "search", "Search"),
    # ... more bindings
]
```

### Add Your Binding

Add this line to the `BINDINGS` list:

```python
BINDINGS = [
    # ... existing bindings ...
    ("ctrl+h", "say_hello", "Say Hello"),  # Add this line
]
```

### Add the Handler Method

Find the action methods (usually near the end of the class). Add this method:

```python
def action_say_hello(self) -> None:
    """Show a hello message."""
    from mini_datahub.ui.widgets.notification import show_notification

    # Replace "Developer" with your name!
    show_notification(
        self,
        "Hello from Developer!",
        severity="info"
    )
```

**What does this do?**

1. `action_say_hello`: Textual convention - methods named `action_*` are keybinding handlers
2. `show_notification`: Helper function to display messages in the TUI
3. `severity="info"`: Message type (could be "success", "warning", "error")

## Step 4: Test Your Change

```bash
# Run the app
hei-datahub

# In the TUI, press Ctrl+H
# You should see "Hello from Developer!" at the bottom
```

**Troubleshooting:**
- **Nothing happens?** Check for syntax errors: `python -m py_compile src/mini_datahub/ui/views/main_view.py`
- **Import error?** Make sure you're in the virtual environment: `which python`

## Step 5: Update the Help Screen (Optional but Good Practice)

Open `src/mini_datahub/ui/views/help_screen.py` and find the keybindings table.

Add your keybinding:

```python
KEYBINDINGS = [
    # ... existing bindings ...
    ("Ctrl+H", "Show hello message", "Development"),
]
```

Test the help screen by pressing `?` in the app.

## Step 6: Write a Test

Create a test file: `tests/ui/test_hello_keybinding.py`

```python
"""Test for the hello keybinding."""
import pytest
from mini_datahub.ui.views.main_view import MainView


def test_hello_action_exists():
    """Verify the say_hello action exists."""
    view = MainView()
    assert hasattr(view, 'action_say_hello')


def test_hello_action_callable():
    """Verify the say_hello action can be called."""
    view = MainView()
    # Should not raise an exception
    view.action_say_hello()
```

Run the test:

```bash
pytest tests/ui/test_hello_keybinding.py -v
```

## Step 7: Commit Your Changes

```bash
# Stage your changes
git add src/mini_datahub/ui/views/main_view.py
git add src/mini_datahub/ui/views/help_screen.py
git add tests/ui/test_hello_keybinding.py

# Check what you're committing
git status

# Commit with a descriptive message
git commit -m "feat(ui): Add Ctrl+H keybinding to show hello message

- Added action_say_hello handler in MainView
- Updated help screen with new keybinding
- Added basic test coverage"
```

**Commit Message Format:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes

Format: `type(scope): brief description`

## Step 8: Push and Create a Pull Request

```bash
# Push your branch to GitHub
git push origin feature/hello-keybinding
```

Then:

1. Go to https://github.com/0xpix/Hei-DataHub
2. You'll see a "Compare & pull request" button
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
