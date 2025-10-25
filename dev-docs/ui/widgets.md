# Widgets & Components

## Introduction

This document catalogs all custom widgets and reusable components in the Hei-DataHub TUI.

---

## Widget Overview

**Location:** `src/mini_datahub/ui/widgets/`

### Custom Widgets

| Widget | Purpose | Used In |
|--------|---------|---------|
| `AutocompleteInput` | Input with suggestions | SearchView |
| `DatasetTable` | Dataset list display | SearchView, CloudFilesView |
| `CommandPalette` | Quick actions (Ctrl+K) | Global |
| `SyncStatusIndicator` | Show sync status | Header |
| `LoadingSpinner` | Loading animation | All async operations |
| `ConfirmDialog` | Confirmation prompts | Delete operations |

---

## AutocompleteInput

**Purpose:** Input field with autocomplete dropdown

**Location:** `src/mini_datahub/ui/widgets/autocomplete_input.py`

### Usage

```python
from mini_datahub.ui.widgets import AutocompleteInput

class SearchView(Screen):
    def compose(self):
        yield AutocompleteInput(
            placeholder="Search datasets...",
            id="search-input"
        )

    def on_autocomplete_input_submitted(self, event: AutocompleteInput.Submitted) -> None:
        """Handle autocomplete selection"""
        selected_value = event.value
        self.perform_search(selected_value)
```

### Implementation

```python
from textual.widgets import Input
from textual.message import Message
from textual.containers import Container
from textual.widgets import ListView, ListItem, Label

class AutocompleteInput(Container):
    """Input with autocomplete suggestions"""

    class Submitted(Message):
        """Posted when user selects a suggestion"""
        def __init__(self, value: str):
            self.value = value
            super().__init__()

    def __init__(self, placeholder: str = "", **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self.suggestions = []

    def compose(self):
        yield Input(placeholder=self.placeholder, id="input")
        with ListView(id="suggestions", classes="hidden"):
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update suggestions as user types"""
        if len(event.value) < 2:
            self.hide_suggestions()
            return

        # Fetch suggestions
        from mini_datahub.services.autocomplete import get_suggestions
        self.suggestions = get_suggestions(event.value)

        if self.suggestions:
            self.show_suggestions()
        else:
            self.hide_suggestions()

    def show_suggestions(self) -> None:
        """Display suggestion dropdown"""
        suggestions_list = self.query_one("#suggestions", ListView)
        suggestions_list.clear()

        for suggestion in self.suggestions[:10]:
            suggestions_list.append(ListItem(Label(suggestion)))

        suggestions_list.remove_class("hidden")

    def hide_suggestions(self) -> None:
        """Hide suggestion dropdown"""
        self.query_one("#suggestions", ListView).add_class("hidden")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle suggestion selection"""
        selected_value = event.item.children[0].renderable
        self.query_one("#input", Input).value = selected_value
        self.hide_suggestions()
        self.post_message(self.Submitted(selected_value))
```

### Styling

```css
AutocompleteInput {
    height: auto;
}

AutocompleteInput #input {
    width: 100%;
}

AutocompleteInput #suggestions {
    height: auto;
    max-height: 10;
    background: $surface-lighten-1;
    border: solid $border;
}

AutocompleteInput #suggestions.hidden {
    display: none;
}

AutocompleteInput #suggestions ListItem {
    padding: 0 1;
}

AutocompleteInput #suggestions ListItem:hover {
    background: $accent;
}
```

---

## DatasetTable

**Purpose:** Specialized table for displaying datasets

**Location:** `src/mini_datahub/ui/widgets/dataset_table.py`

### Usage

```python
from mini_datahub.ui.widgets import DatasetTable

class SearchView(Screen):
    def compose(self):
        yield DatasetTable(id="results-table")

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DatasetTable)
        table.load_datasets(datasets)
```

### Implementation

```python
from textual.widgets import DataTable
from textual.message import Message

class DatasetTable(DataTable):
    """Table widget for datasets"""

    class DatasetSelected(Message):
        """Posted when dataset is selected"""
        def __init__(self, dataset_id: str):
            self.dataset_id = dataset_id
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset_ids = []  # Track IDs by row

    def on_mount(self) -> None:
        """Setup table columns"""
        self.add_columns(
            "Name",
            "Project",
            "Format",
            "Size",
            "Updated"
        )
        self.cursor_type = "row"
        self.zebra_stripes = True

    def load_datasets(self, datasets: list[dict]) -> None:
        """Populate table with datasets"""
        self.clear()
        self.dataset_ids.clear()

        for dataset in datasets:
            row_key = self.add_row(
                dataset["dataset_name"],
                dataset.get("used_in_projects", [""])[0],
                dataset.get("file_format", ""),
                self._format_size(dataset.get("data_size_gb", 0)),
                self._format_date(dataset.get("last_updated", ""))
            )
            self.dataset_ids.append((row_key, dataset["id"]))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        # Find dataset ID for selected row
        for row_key, dataset_id in self.dataset_ids:
            if row_key == event.row_key:
                self.post_message(self.DatasetSelected(dataset_id))
                break

    @staticmethod
    def _format_size(size_gb: float) -> str:
        """Format size for display"""
        if size_gb < 1:
            return f"{size_gb * 1024:.1f} MB"
        elif size_gb < 1024:
            return f"{size_gb:.1f} GB"
        else:
            return f"{size_gb / 1024:.1f} TB"

    @staticmethod
    def _format_date(date_str: str) -> str:
        """Format date for display"""
        if not date_str:
            return ""

        from datetime import datetime
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d")
        except:
            return date_str
```

---

## CommandPalette

**Purpose:** Quick action launcher (Ctrl+K style)

**Location:** `src/mini_datahub/ui/widgets/command_palette.py`

### Usage

```python
# In App
class MiniDataHubApp(App):
    BINDINGS = [
        ("ctrl+k", "command_palette", "Commands"),
    ]

    def action_command_palette(self) -> None:
        """Show command palette"""
        self.push_screen(CommandPaletteScreen())
```

### Implementation

```python
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical

class CommandPaletteScreen(ModalScreen):
    """Modal command palette"""

    COMMANDS = [
        ("search", "🔍 Search datasets", "search"),
        ("new", "➕ Create new dataset", "new_dataset"),
        ("sync", "🔄 Sync now", "sync"),
        ("cloud", "☁️  Browse cloud files", "cloud_files"),
        ("outbox", "📤 View outbox", "outbox"),
        ("settings", "⚙️  Settings", "settings"),
    ]

    def compose(self):
        with Vertical(id="palette-container"):
            yield Input(placeholder="Type a command...", id="cmd-input")
            with ListView(id="cmd-list"):
                for cmd_id, label, action in self.COMMANDS:
                    yield ListItem(Label(label), id=cmd_id)

    def on_mount(self) -> None:
        """Focus input on mount"""
        self.query_one("#cmd-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types"""
        query = event.value.lower()
        cmd_list = self.query_one("#cmd-list", ListView)

        for item in cmd_list.children:
            label = item.children[0].renderable
            if query in label.lower():
                item.remove_class("hidden")
            else:
                item.add_class("hidden")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Execute selected command"""
        cmd_id = event.item.id

        # Find action for command
        for cmd_id_, _, action in self.COMMANDS:
            if cmd_id_ == cmd_id:
                self.dismiss()
                self.app.call_after_refresh(self._execute_command, action)
                break

    def _execute_command(self, action: str) -> None:
        """Execute command action"""
        if action == "search":
            self.app.push_screen("search")
        elif action == "new_dataset":
            self.app.push_screen("create_dataset")
        elif action == "sync":
            from mini_datahub.services.sync import sync_now
            result = sync_now()
            self.app.notify(f"Synced: {result.downloads} ↓ {result.uploads} ↑")
        # ... other actions
```

### Styling

```css
CommandPaletteScreen {
    align: center middle;
}

#palette-container {
    width: 60;
    height: auto;
    max-height: 20;
    background: $surface;
    border: thick $primary;
    padding: 1;
}

#cmd-input {
    margin-bottom: 1;
}

#cmd-list {
    height: auto;
    max-height: 15;
}

#cmd-list ListItem {
    padding: 0 1;
}

#cmd-list ListItem.hidden {
    display: none;
}
```

---

## SyncStatusIndicator

**Purpose:** Show sync status in header

**Location:** `src/mini_datahub/ui/widgets/sync_status.py`

### Implementation

```python
from textual.widgets import Static
from textual.reactive import reactive

class SyncStatusIndicator(Static):
    """Displays current sync status"""

    status = reactive("idle")  # idle, syncing, success, error
    last_sync = reactive("")

    def watch_status(self, new_status: str) -> None:
        """Update display when status changes"""
        self.update_display()

    def watch_last_sync(self, new_time: str) -> None:
        """Update display when sync time changes"""
        self.update_display()

    def update_display(self) -> None:
        """Render status indicator"""
        if self.status == "idle":
            icon = "⏸️"
            text = "Idle"
        elif self.status == "syncing":
            icon = "🔄"
            text = "Syncing..."
        elif self.status == "success":
            icon = "✅"
            text = f"Synced {self.last_sync}"
        else:  # error
            icon = "❌"
            text = "Sync failed"

        self.update(f"{icon} {text}")
```

---

## LoadingSpinner

**Purpose:** Animated loading indicator

**Location:** `src/mini_datahub/ui/widgets/loading_spinner.py`

### Usage

```python
class MyView(Screen):
    def compose(self):
        yield LoadingSpinner(id="spinner", classes="hidden")

    async def load_data(self):
        spinner = self.query_one("#spinner", LoadingSpinner)
        spinner.remove_class("hidden")

        data = await fetch_data()

        spinner.add_class("hidden")
```

### Implementation

```python
from textual.widgets import Static
import asyncio

class LoadingSpinner(Static):
    """Animated loading spinner"""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def on_mount(self) -> None:
        """Start animation"""
        self.frame_index = 0
        self.set_interval(0.1, self.next_frame)

    def next_frame(self) -> None:
        """Update to next animation frame"""
        self.frame_index = (self.frame_index + 1) % len(self.FRAMES)
        self.update(self.FRAMES[self.frame_index])
```

---

## ConfirmDialog

**Purpose:** Confirmation modal dialog

**Location:** `src/mini_datahub/ui/widgets/confirm_dialog.py`

### Usage

```python
async def delete_dataset(self):
    confirmed = await self.app.push_screen_wait(
        ConfirmDialog("Delete this dataset?", "This cannot be undone.")
    )

    if confirmed:
        # Perform deletion
        pass
```

### Implementation

```python
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Vertical, Horizontal

class ConfirmDialog(ModalScreen[bool]):
    """Confirmation dialog"""

    def __init__(self, title: str, message: str):
        super().__init__()
        self.title_text = title
        self.message_text = message

    def compose(self):
        with Vertical(id="dialog"):
            yield Static(self.title_text, id="dialog-title")
            yield Static(self.message_text, id="dialog-message")

            with Horizontal(id="dialog-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Confirm", id="btn-confirm", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)
```

### Styling

```css
ConfirmDialog {
    align: center middle;
}

#dialog {
    width: 50;
    height: auto;
    background: $surface;
    border: thick $error;
    padding: 2;
}

#dialog-title {
    text-style: bold;
    color: $error;
    text-align: center;
    margin-bottom: 1;
}

#dialog-message {
    text-align: center;
    margin-bottom: 2;
}

#dialog-buttons {
    align: center middle;
}

#dialog-buttons Button {
    margin: 0 1;
}
```

---

## Widget Testing

### Unit Tests

```python
# tests/ui/test_widgets.py

from textual.app import App
from mini_datahub.ui.widgets import AutocompleteInput

async def test_autocomplete_input_suggestions():
    """Test autocomplete shows suggestions"""
    app = App()

    async with app.run_test() as pilot:
        widget = AutocompleteInput(placeholder="Search")
        app.mount(widget)

        # Type into input
        input_widget = widget.query_one("#input")
        input_widget.value = "cli"

        # Wait for suggestions to appear
        await pilot.pause()

        # Verify suggestions shown
        suggestions = widget.query_one("#suggestions")
        assert not suggestions.has_class("hidden")
        assert len(suggestions.children) > 0
```

---

## Best Practices

### 1. Use Messages for Communication

```python
# ✅ GOOD: Post message for parent to handle
class MyWidget(Widget):
    def on_click(self):
        self.post_message(self.ItemSelected(item_id))

# ❌ BAD: Directly call parent methods
class MyWidget(Widget):
    def on_click(self):
        self.parent.handle_selection(item_id)
```

---

### 2. Make Widgets Reusable

```python
# ✅ GOOD: Configurable widget
class DatasetTable(DataTable):
    def __init__(self, show_size: bool = True, **kwargs):
        self.show_size = show_size
        super().__init__(**kwargs)

# ❌ BAD: Hardcoded behavior
class DatasetTable(DataTable):
    # Always shows size column
    pass
```

---

### 3. Use Reactive for State

```python
# ✅ GOOD: Reactive state
class MyWidget(Widget):
    count = reactive(0)

    def watch_count(self, new_count):
        self.update_display()

# ❌ BAD: Manual updates
class MyWidget(Widget):
    def set_count(self, count):
        self.count = count
        self.update_display()  # Easy to forget
```

---

## Related Documentation

- **[UI Architecture](architecture.md)** - UI design patterns
- **[Views & Screens](views.md)** - Screen documentation
- **[State Management](state.md)** - State patterns
- **[Theming](theming.md)** - Styling widgets

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
