# UI/TUI Architecture

## Introduction

Hei-DataHub uses **Textual** for its Terminal User Interface (TUI). This document explains the UI architecture, design patterns, and how components interact.

---

## Technology Stack

### Textual Framework

**Version:** `^0.47.0`

**What is Textual?**
- Modern Python TUI framework
- Rich terminal graphics
- Reactive programming model
- CSS-like styling
- Event-driven architecture

**Why Textual?**
- ✅ Professional terminal UI
- ✅ Mouse and keyboard support
- ✅ Responsive layouts
- ✅ Built-in widgets (buttons, inputs, tables)
- ✅ Easy to test and maintain

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              Textual App                        │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │          Screen Manager                  │  │
│  │  (HomeView, CloudFilesView, etc.)       │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │          Widget Layer                    │  │
│  │  (AutocompleteInput, DatasetTable, etc.) │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │          Event System                    │  │
│  │  (Key bindings, Mouse events, Messages) │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
            │                      │
            ▼                      ▼
    ┌─────────────┐        ┌──────────────┐
    │  Services   │        │    State     │
    │  Layer      │        │  Management  │
    └─────────────┘        └──────────────┘
```

---

## Application Entry Point

**Location:** `src/mini_datahub/ui/app.py`

```python
from textual.app import App
from textual.binding import Binding
from mini_datahub.ui.views.home import HomeView

class MiniDataHubApp(App):
    """Main TUI application"""

    CSS_PATH = "theme.css"  # Load styles

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("/", "search", "Search"),
        Binding("n", "new_dataset", "New Dataset"),
        Binding("s", "sync", "Sync Now"),
    ]

    def on_mount(self) -> None:
        """Initialize application on startup"""
        self.push_screen(HomeView())

    def action_search(self) -> None:
        """Open search view"""
        from mini_datahub.ui.views.search import SearchView
        self.push_screen(SearchView())

    def action_new_dataset(self) -> None:
        """Open create dataset form"""
        from mini_datahub.ui.views.create_dataset import CreateDatasetView
        self.push_screen(CreateDatasetView())

    def action_sync(self) -> None:
        """Trigger manual sync"""
        from mini_datahub.services.sync import sync_now
        result = sync_now()
        self.notify(f"Synced: {result.downloads} ↓ {result.uploads} ↑")

def main():
    app = MiniDataHubApp()
    app.run()
```

---

## Screen/View Architecture

### Screen Hierarchy

```
MiniDataHubApp
├── HomeView (landing screen)
├── SearchView (search interface)
├── CloudFilesView (cloud file browser)
├── CreateDatasetView (new dataset form)
├── EditDatasetView (edit existing dataset)
├── SettingsView (app settings)
└── OutboxView (failed uploads queue)
```

---

### Base View Pattern

```python
from textual.screen import Screen
from textual.widgets import Header, Footer

class BaseView(Screen):
    """Base class for all views"""

    BINDINGS = [
        ("escape", "back", "Back"),
    ]

    def compose(self):
        """Layout widgets"""
        yield Header()
        # Subclass adds content here
        yield Footer()

    def action_back(self) -> None:
        """Navigate back to previous screen"""
        self.app.pop_screen()
```

---

### Example View: HomeView

```python
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Label
from textual.containers import Container, Vertical

class HomeView(Screen):
    """Home screen with main menu"""

    def compose(self):
        yield Header(show_clock=True)

        with Container(id="home-container"):
            yield Label("Welcome to Hei-DataHub", id="title")
            yield Label("Manage your research datasets", id="subtitle")

            with Vertical(id="menu"):
                yield Button("Search Datasets", id="btn-search")
                yield Button("Browse Cloud Files", id="btn-cloud")
                yield Button("Create New Dataset", id="btn-new")
                yield Button("View Outbox", id="btn-outbox")
                yield Button("Settings", id="btn-settings")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        button_id = event.button.id

        if button_id == "btn-search":
            self.app.push_screen(SearchView())
        elif button_id == "btn-cloud":
            self.app.push_screen(CloudFilesView())
        elif button_id == "btn-new":
            self.app.push_screen(CreateDatasetView())
        elif button_id == "btn-outbox":
            self.app.push_screen(OutboxView())
        elif button_id == "btn-settings":
            self.app.push_screen(SettingsView())
```

---

## Widget Layer

### Custom Widgets

**Location:** `src/mini_datahub/ui/widgets/`

#### AutocompleteInput

```python
from textual.widgets import Input
from textual.message import Message

class AutocompleteInput(Input):
    """Input field with autocomplete suggestions"""

    class Suggested(Message):
        """Message when suggestion selected"""
        def __init__(self, value: str):
            self.value = value
            super().__init__()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show suggestions as user types"""
        if len(event.value) >= 2:
            suggestions = get_autocomplete_suggestions(event.value)
            self.show_suggestions(suggestions)

    def on_key(self, event: KeyEvent) -> None:
        """Handle keyboard navigation of suggestions"""
        if event.key == "down":
            self.select_next_suggestion()
        elif event.key == "up":
            self.select_previous_suggestion()
        elif event.key == "enter":
            self.apply_selected_suggestion()
```

---

#### DatasetTable

```python
from textual.widgets import DataTable

class DatasetTable(DataTable):
    """Table widget for displaying datasets"""

    def on_mount(self) -> None:
        """Setup table columns"""
        self.add_columns("Name", "Project", "Format", "Size")
        self.cursor_type = "row"

    def load_datasets(self, datasets: list[dict]) -> None:
        """Populate table with dataset data"""
        self.clear()
        for dataset in datasets:
            self.add_row(
                dataset["dataset_name"],
                dataset.get("used_in_projects", [""])[0],
                dataset.get("file_format", ""),
                format_size(dataset.get("data_size_gb", 0))
            )
```

---

#### CommandPalette

```python
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container

class CommandPalette(Container):
    """Quick action command palette (Ctrl+K)"""

    def compose(self):
        yield Input(placeholder="Type a command...", id="cmd-input")
        with ListView(id="cmd-list"):
            yield ListItem(Label("Search datasets"))
            yield ListItem(Label("Create new dataset"))
            yield ListItem(Label("Sync now"))
            yield ListItem(Label("View outbox"))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types"""
        query = event.value.lower()
        # Filter and update list view...
```

---

## Event System

### Event Flow

```
User Action (key press, mouse click)
         ↓
Textual Event System
         ↓
Event Handler (on_key, on_button_pressed, etc.)
         ↓
Business Logic (service calls)
         ↓
State Update
         ↓
UI Re-render (reactive)
```

---

### Key Bindings

**Global Bindings:**

```python
BINDINGS = [
    Binding("q", "quit", "Quit"),
    Binding("?", "help", "Help"),
    Binding("/", "search", "Search"),
    Binding("n", "new_dataset", "New"),
    Binding("s", "sync", "Sync"),
    Binding("ctrl+k", "command_palette", "Commands"),
]
```

**View-Specific Bindings:**

```python
class SearchView(Screen):
    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "select", "Select"),
        ("ctrl+f", "filter", "Filter"),
    ]
```

---

### Custom Messages

```python
from textual.message import Message

class DatasetSelected(Message):
    """Posted when user selects a dataset"""
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__()

class SyncCompleted(Message):
    """Posted when sync finishes"""
    def __init__(self, downloads: int, uploads: int):
        self.downloads = downloads
        self.uploads = uploads
        super().__init__()

# Usage in view
def on_dataset_table_row_selected(self, event) -> None:
    """Handle dataset selection"""
    dataset_id = self.get_selected_dataset_id()
    self.post_message(DatasetSelected(dataset_id))
```

---

## State Management

### Reactive State

Textual uses **reactive variables** for state management:

```python
from textual.reactive import reactive

class SearchView(Screen):
    # Reactive state - UI updates automatically when changed
    search_query = reactive("")
    results_count = reactive(0)
    is_loading = reactive(False)

    def watch_search_query(self, new_query: str) -> None:
        """Called when search_query changes"""
        self.is_loading = True
        results = perform_search(new_query)
        self.results_count = len(results)
        self.update_results_display(results)
        self.is_loading = False

    def watch_is_loading(self, loading: bool) -> None:
        """Show/hide loading indicator"""
        if loading:
            self.query_one("#loading").display = True
        else:
            self.query_one("#loading").display = False
```

---

### Application State

```python
class MiniDataHubApp(App):
    # Global app state
    current_user = reactive(None)
    sync_status = reactive("idle")  # idle, syncing, failed
    outbox_count = reactive(0)

    def watch_outbox_count(self, count: int) -> None:
        """Update UI when outbox count changes"""
        if count > 0:
            self.notify(f"{count} items in outbox", severity="warning")
```

---

## Styling (CSS)

**Location:** `src/mini_datahub/ui/theme.css`

```css
/* Global styles */
Screen {
    background: $surface;
    color: $text;
}

/* Header */
Header {
    background: $primary;
    color: $text-on-primary;
}

/* Buttons */
Button {
    background: $accent;
    color: $text-on-accent;
    border: solid $border;
}

Button:hover {
    background: $accent-lighten-1;
}

Button:focus {
    border: solid $focus;
}

/* Tables */
DataTable {
    background: $surface;
}

DataTable > .datatable--header {
    background: $primary-darken-1;
    color: $text-on-primary;
}

DataTable > .datatable--cursor {
    background: $accent;
}

/* Custom widgets */
#home-container {
    align: center middle;
    padding: 2 4;
}

#title {
    text-style: bold;
    color: $primary;
    text-align: center;
}

#subtitle {
    color: $text-muted;
    text-align: center;
    padding: 0 0 2 0;
}

#menu {
    width: 40;
    padding: 1 2;
}

#menu Button {
    width: 100%;
    margin: 1 0;
}
```

---

## Layout System

### Containers

```python
from textual.containers import Container, Horizontal, Vertical, Grid

def compose(self):
    # Horizontal layout (side-by-side)
    with Horizontal():
        yield Button("Left")
        yield Button("Right")

    # Vertical layout (stacked)
    with Vertical():
        yield Button("Top")
        yield Button("Bottom")

    # Grid layout (2x2)
    with Grid(classes="grid-2x2"):
        yield Button("1")
        yield Button("2")
        yield Button("3")
        yield Button("4")
```

---

### Responsive Layouts

```css
/* Adapt layout based on terminal size */
@media (max-width: 80) {
    #sidebar {
        display: none;
    }

    #main-content {
        width: 100%;
    }
}

@media (min-width: 120) {
    #sidebar {
        display: block;
        width: 30;
    }

    #main-content {
        width: 1fr;
    }
}
```

---

## Component Communication

### Parent-Child Communication

```python
# Parent sends data to child
class ParentView(Screen):
    def compose(self):
        yield ChildWidget(data={"key": "value"})

# Child receives data via init
class ChildWidget(Widget):
    def __init__(self, data: dict):
        self.data = data
        super().__init__()
```

---

### Child-Parent Communication (Messages)

```python
# Child posts message
class ChildWidget(Widget):
    def on_button_pressed(self) -> None:
        self.post_message(DataChanged(new_value))

# Parent handles message
class ParentView(Screen):
    def on_data_changed(self, message: DataChanged) -> None:
        self.handle_data_change(message.new_value)
```

---

## Performance Optimization

### Lazy Loading

```python
class CloudFilesView(Screen):
    def on_mount(self) -> None:
        """Load data after screen is mounted"""
        self.call_later(self.load_files)

    async def load_files(self) -> None:
        """Load files asynchronously"""
        files = await fetch_cloud_files()
        self.update_file_list(files)
```

---

### Virtual Scrolling

```python
from textual.widgets import DataTable

class LargeDatasetTable(DataTable):
    """Table with virtual scrolling for large datasets"""

    def on_mount(self) -> None:
        # Only render visible rows
        self.show_cursor = True
        self.zebra_stripes = True
```

---

## Testing UI Components

### Widget Testing

```python
# tests/ui/test_widgets.py

from textual.app import App
from mini_datahub.ui.widgets import AutocompleteInput

async def test_autocomplete_input():
    """Test autocomplete widget"""
    app = App()
    async with app.run_test() as pilot:
        widget = AutocompleteInput()
        app.mount(widget)

        # Type into input
        await pilot.press("c", "l", "i")

        # Check suggestions appear
        assert widget.has_suggestions()
        assert "climate" in widget.get_suggestions()
```

---

### View Testing

```python
from mini_datahub.ui.views.home import HomeView

async def test_home_view_navigation():
    """Test home view button navigation"""
    app = MiniDataHubApp()
    async with app.run_test() as pilot:
        # Click search button
        await pilot.click("#btn-search")

        # Verify SearchView is pushed
        assert isinstance(app.screen, SearchView)
```

---

## Related Documentation

- **[Views & Screens](views.md)** - Detailed view documentation
- **[Widgets & Components](widgets.md)** - Custom widget reference
- **[State Management](state.md)** - State handling patterns
- **[Keybindings](keybindings.md)** - Keyboard shortcuts
- **[Theming](theming.md)** - Styling and themes
- **[Adding New Views](adding-views.md)** - Create new views

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
