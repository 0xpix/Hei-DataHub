# Keybindings

> **Version:** 0.60.0-beta — "Clean-up"
> This documentation reflects the enhanced Vim-style navigation keybindings added in v0.60.

!!! info "What this section covers"
    This page describes all keyboard shortcuts in Hei-DataHub TUI and how they're implemented. Essential for understanding user interaction patterns and adding new keybindings.

## Introduction

This document describes all keyboard shortcuts in Hei-DataHub TUI and how to customize them.

!!! success "New in v0.60: Vim Navigation"
    **Enhanced keyboard navigation:**
    - `gg` - Jump to top of list
    - `G` - Jump to bottom of list
    - `Ctrl+a` - Show About screen
    - `j/k` - Scroll up/down
    - `d/u` - Page down/up (half page)

    All Vim-style bindings work in scrollable screens (About, Help, Dataset Details, Settings).

---

## Global Keybindings

### Application-Wide Shortcuts

| Key | Action | Description | Version |
|-----|--------|-------------|---------|
| `q` | Quit | Exit application | All |
| `Ctrl+C` | Quit | Force quit | All |
| `?` | Help | Show help screen | All |
| `/` | Search | Open search view | All |
| `n` | New Dataset | Create new dataset | All |
| `s` | Sync | Trigger manual sync | All |
| `Ctrl+a` | About | Show About screen | v0.60+ |
| `Ctrl+K` | Command Palette | Quick actions | All |
| `ESC` | Back | Go to previous screen | All |

**Vim-Style Navigation (v0.60+):**

| Key | Action | Description |
|-----|--------|-------------|
| `j` | Scroll Down | Move down one line |
| `k` | Scroll Up | Move up one line |
| `gg` | Jump to Top | Go to first item/line |
| `G` | Jump to Bottom | Go to last item/line |
| `d` | Page Down | Scroll down half page |
| `u` | Page Up | Scroll up half page |

**Implementation:**

```python
# src/hei_datahub/ui/app.py

from textual.app import App
from textual.binding import Binding

class MiniDataHubApp(App):
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("?", "help", "Help"),
        Binding("/", "search", "Search"),
        Binding("n", "new_dataset", "New Dataset"),
        Binding("s", "sync_now", "Sync"),
        Binding("ctrl+k", "command_palette", "Commands"),
    ]

    def action_search(self) -> None:
        """Open search view"""
        self.push_screen("search")

    def action_new_dataset(self) -> None:
        """Open create dataset form"""
        self.push_screen("create_dataset")

    def action_sync_now(self) -> None:
        """Trigger manual sync"""
        from hei_datahub.services.sync import sync_now
        result = sync_now()
        self.notify(f"Synced: {result.downloads} ↓ {result.uploads} ↑")

    def action_command_palette(self) -> None:
        """Show command palette"""
        self.push_screen(CommandPaletteScreen())
```

---

## View-Specific Keybindings

### SearchView

| Key | Action | Description |
|-----|--------|-------------|
| `ESC` | Back | Return to home |
| `Enter` | Select | View selected dataset |
| `Ctrl+F` | Focus Search | Focus search input |
| `↑` / `↓` | Navigate | Move up/down results |
| `PgUp` / `PgDn` | Page | Page up/down |
| `Home` / `End` | Jump | Jump to first/last |

```python
class SearchView(Screen):
    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "select_dataset", "Select"),
        ("ctrl+f", "focus_search", "Search"),
    ]

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_select_dataset(self) -> None:
        table = self.query_one(DatasetTable)
        selected_id = table.get_selected_dataset_id()
        if selected_id:
            self.app.push_screen(DatasetDetailView(selected_id))

    def action_focus_search(self) -> None:
        self.query_one(Input).focus()
```

---

### CreateDatasetView

| Key | Action | Description |
|-----|--------|-------------|
| `ESC` | Cancel | Cancel and go back |
| `Ctrl+S` | Save | Save dataset |
| `Tab` | Next Field | Move to next input |
| `Shift+Tab` | Previous Field | Move to previous input |

```python
class CreateDatasetView(Screen):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def action_save(self) -> None:
        # Validate and save dataset
        pass
```

---

### CloudFilesView

| Key | Action | Description |
|-----|--------|-------------|
| `ESC` | Back | Return to home |
| `Enter` | Open | Open file/folder |
| `r` | Refresh | Refresh file list |
| `d` | Download | Download selected file |
| `u` | Upload | Upload to cloud |

```python
class CloudFilesView(Screen):
    BINDINGS = [
        ("escape", "back", "Back"),
        ("r", "refresh", "Refresh"),
        ("d", "download", "Download"),
        ("u", "upload", "Upload"),
    ]
```

---

## Custom Keybindings

### Adding New Keybindings

```python
from textual.binding import Binding

class MyView(Screen):
    BINDINGS = [
        # Simple binding
        ("f", "filter", "Filter"),

        # With modifier keys
        ("ctrl+e", "edit", "Edit"),
        ("shift+d", "delete", "Delete"),

        # Multiple keys for same action
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit", {"show": False}),

        # Priority binding (overrides child bindings)
        Binding("escape", "back", "Back", priority=True),

        # Hidden binding (not shown in footer)
        Binding("ctrl+x", "debug", show=False),
    ]

    def action_filter(self) -> None:
        """Filter action"""
        pass

    def action_edit(self) -> None:
        """Edit action"""
        pass
```

---

### Conditional Keybindings

```python
class SearchView(Screen):
    def check_action(self, action: str, _) -> bool | None:
        """Conditionally enable actions"""
        if action == "delete_dataset":
            # Only enable if dataset selected
            return self.has_selection()
        return True

    BINDINGS = [
        Binding("d", "delete_dataset", "Delete"),
    ]

    def action_delete_dataset(self) -> None:
        """Delete selected dataset"""
        if self.has_selection():
            # Delete logic
            pass
```

---

## Keybinding Conflicts

### Resolving Conflicts

**Priority System:**
1. View-specific bindings (highest)
2. App-level bindings
3. Textual default bindings (lowest)

```python
# Child view overrides app binding
class MyView(Screen):
    BINDINGS = [
        ("s", "save", "Save"),  # Overrides app's "sync" binding
    ]

# App binding (lower priority)
class App:
    BINDINGS = [
        ("s", "sync", "Sync"),  # Only active when MyView not shown
    ]
```

---

### Using Priority Flag

```python
class MyView(Screen):
    BINDINGS = [
        # High priority - always active
        Binding("escape", "back", "Back", priority=True),

        # Normal priority
        ("s", "save", "Save"),
    ]
```

---

## Dynamic Keybindings

### Changing Bindings at Runtime

```python
class SearchView(Screen):
    def on_mount(self) -> None:
        """Setup dynamic bindings"""
        if self.app.is_admin:
            self.bind("ctrl+d", "delete_all", "Delete All")
        else:
            self.unbind("ctrl+d")
```

---

### Context-Sensitive Bindings

```python
class DatasetTable(DataTable):
    def watch_cursor_row(self, row: int) -> None:
        """Update bindings based on selection"""
        if row is not None:
            # Enable delete when row selected
            self.screen.bind("d", "delete", "Delete")
        else:
            # Disable delete when nothing selected
            self.screen.unbind("d")
```

---

## Keybinding Best Practices

### 1. Follow Conventions

```python
# ✅ GOOD: Standard conventions
BINDINGS = [
    ("q", "quit", "Quit"),              # Standard quit
    ("?", "help", "Help"),              # Standard help
    ("ctrl+s", "save", "Save"),         # Standard save
    ("escape", "back", "Back"),         # Standard back
]

# ❌ BAD: Non-standard
BINDINGS = [
    ("x", "quit", "Quit"),              # Unexpected
    ("h", "help", "Help"),              # Conflicts with vim
]
```

---

### 2. Avoid Conflicts

```python
# ✅ GOOD: Unique, non-conflicting keys
BINDINGS = [
    ("f", "filter", "Filter"),
    ("s", "search", "Search"),
    ("r", "refresh", "Refresh"),
]

# ❌ BAD: Similar keys, easy to mispress
BINDINGS = [
    ("d", "delete", "Delete"),
    ("e", "edit", "Edit"),              # Too close to 'd'
]
```

---

### 3. Provide Alternatives

```python
# ✅ GOOD: Multiple ways to quit
BINDINGS = [
    ("q", "quit", "Quit"),
    ("ctrl+c", "quit", show=False),     # Alternative
    ("ctrl+q", "quit", show=False),     # Another alternative
]
```

---

### 4. Use Meaningful Mnemonics

```python
# ✅ GOOD: Memorable mnemonics
BINDINGS = [
    ("s", "search", "Search"),          # s for search
    ("n", "new", "New"),                # n for new
    ("r", "refresh", "Refresh"),        # r for refresh
]

# ❌ BAD: Random assignments
BINDINGS = [
    ("x", "search", "Search"),
    ("z", "new", "New"),
]
```

---

## Testing Keybindings

### Unit Tests

```python
# tests/ui/test_keybindings.py

async def test_search_keybinding():
    """Test / opens search view"""
    app = MiniDataHubApp()

    async with app.run_test() as pilot:
        # Press / key
        await pilot.press("/")

        # Verify SearchView is shown
        assert isinstance(app.screen, SearchView)

async def test_save_keybinding():
    """Test Ctrl+S saves dataset"""
    app = MiniDataHubApp()

    async with app.run_test() as pilot:
        app.push_screen(CreateDatasetView())

        # Fill form...

        # Press Ctrl+S
        await pilot.press("ctrl+s")

        # Verify save was called
        # (using mocks or checking database)
```

---

## Keybinding Reference

### Complete List

**Global:**
- `q` - Quit
- `Ctrl+C` - Force quit
- `?` - Help
- `/` - Search
- `n` - New dataset
- `s` - Sync now
- `Ctrl+K` - Command palette
- `ESC` - Back/Cancel

**Navigation:**
- `↑` / `k` - Move up
- `↓` / `j` - Move down
- `←` / `h` - Move left
- `→` / `l` - Move right
- `Home` / `g` - First item
- `End` / `G` - Last item
- `PgUp` - Page up
- `PgDn` - Page down

**Actions:**
- `Enter` - Select/Open
- `Space` - Toggle
- `Tab` - Next field
- `Shift+Tab` - Previous field
- `Ctrl+S` - Save
- `Ctrl+F` - Focus search
- `r` - Refresh
- `d` - Delete
- `e` - Edit

---

## Related Documentation

- **[UI Architecture](architecture.md)** - UI design patterns
- **[Views & Screens](views.md)** - Screen documentation
- **[Widgets & Components](widgets.md)** - Custom widgets

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
