# Views & Screens

## Introduction

This document details all views (screens) in the Hei-DataHub TUI, their purpose, layout, and interactions.

---

## View Architecture

### Screen Navigation

```
┌─────────────┐
│  HomeView   │ ← Entry point
└──────┬──────┘
       │
       ├──→ SearchView
       ├──→ CloudFilesView
       ├──→ CreateDatasetView
       ├──→ SettingsView
       └──→ OutboxView
```

**Navigation Pattern:**
- `push_screen()` - Navigate forward
- `pop_screen()` - Navigate back
- `switch_screen()` - Replace current screen

---

## HomeView

**Purpose:** Landing screen with main menu

**Location:** `src/mini_datahub/ui/views/home.py`

### Layout

```
┌────────────────────────────────────────┐
│ Hei-DataHub                    🕐 10:30 │ ← Header
├────────────────────────────────────────┤
│                                        │
│      Welcome to Hei-DataHub            │
│   Manage your research datasets        │
│                                        │
│    ┌──────────────────────────┐       │
│    │  🔍 Search Datasets      │       │
│    ├──────────────────────────┤       │
│    │  ☁️  Browse Cloud Files  │       │
│    ├──────────────────────────┤       │
│    │  ➕ Create New Dataset   │       │
│    ├──────────────────────────┤       │
│    │  📤 View Outbox          │       │
│    ├──────────────────────────┤       │
│    │  ⚙️  Settings            │       │
│    └──────────────────────────┘       │
│                                        │
├────────────────────────────────────────┤
│ q: Quit  /: Search  n: New  s: Sync   │ ← Footer
└────────────────────────────────────────┘
```

### Implementation

```python
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Container, Vertical

class HomeView(Screen):
    """Home screen with main menu"""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "search", "Search"),
        ("n", "new_dataset", "New"),
        ("s", "sync", "Sync"),
    ]

    def compose(self):
        yield Header(show_clock=True)

        with Container(id="home-container"):
            yield Static("Welcome to Hei-DataHub", id="title")
            yield Static("Manage your research datasets", id="subtitle")

            with Vertical(id="menu"):
                yield Button("🔍 Search Datasets", id="btn-search", variant="primary")
                yield Button("☁️  Browse Cloud Files", id="btn-cloud")
                yield Button("➕ Create New Dataset", id="btn-new")
                yield Button("📤 View Outbox", id="btn-outbox")
                yield Button("⚙️  Settings", id="btn-settings")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button clicks"""
        button_id = event.button.id

        if button_id == "btn-search":
            self.app.push_screen("search")
        elif button_id == "btn-cloud":
            self.app.push_screen("cloud_files")
        elif button_id == "btn-new":
            self.app.push_screen("create_dataset")
        elif button_id == "btn-outbox":
            self.app.push_screen("outbox")
        elif button_id == "btn-settings":
            self.app.push_screen("settings")

    def action_search(self) -> None:
        """Keyboard shortcut for search"""
        self.app.push_screen("search")

    def action_new_dataset(self) -> None:
        """Keyboard shortcut for new dataset"""
        self.app.push_screen("create_dataset")

    def action_sync(self) -> None:
        """Trigger manual sync"""
        from mini_datahub.services.sync import sync_now
        result = sync_now()
        self.notify(f"Synced: {result.downloads} ↓ {result.uploads} ↑")
```

---

## SearchView

**Purpose:** Search datasets with autocomplete

**Location:** `src/mini_datahub/ui/views/search.py`

### Layout

```
┌────────────────────────────────────────┐
│ Search Datasets                10:30   │
├────────────────────────────────────────┤
│ Search: [climate_____________]  🔍     │
│                                        │
│ ┌────────────────────────────────────┐│
│ │ Name          Project    Format    ││
│ ├────────────────────────────────────┤│
│ │ Climate Data  climate-s  NetCDF    ││ ← Selected
│ │ Ocean Temps   ocean-res  CSV       ││
│ │ Field Notes   field-stu  Markdown  ││
│ │ ...                                ││
│ └────────────────────────────────────┘│
│                                        │
│ Found 23 datasets                      │
├────────────────────────────────────────┤
│ ESC: Back  ↑↓: Navigate  Enter: View  │
└────────────────────────────────────────┘
```

### Implementation

```python
from textual.screen import Screen
from textual.widgets import Input, DataTable, Static
from textual.reactive import reactive

class SearchView(Screen):
    """Search datasets view"""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "view_dataset", "View"),
        ("ctrl+f", "focus_search", "Search"),
    ]

    search_query = reactive("")
    results_count = reactive(0)

    def compose(self):
        yield Header()
        yield Input(placeholder="Search datasets...", id="search-input")
        yield DataTable(id="results-table")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize view"""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Name", "Project", "Format", "Size")
        table.cursor_type = "row"

        # Focus search input
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Search as user types"""
        self.search_query = event.value
        self.perform_search()

    def perform_search(self) -> None:
        """Execute search and update results"""
        from mini_datahub.services.fast_search import search_indexed

        results = search_indexed(self.search_query) if self.search_query else []
        self.results_count = len(results)

        # Update table
        table = self.query_one("#results-table", DataTable)
        table.clear()

        for result in results:
            table.add_row(
                result["name"],
                result.get("project", ""),
                result.get("format", ""),
                self.format_size(result.get("size_gb", 0))
            )

        # Update status
        status = self.query_one("#status-bar", Static)
        status.update(f"Found {self.results_count} datasets")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle dataset selection"""
        dataset_id = self.get_selected_dataset_id(event.row_key)
        self.app.push_screen(DatasetDetailView(dataset_id))

    @staticmethod
    def format_size(size_gb: float) -> str:
        """Format size for display"""
        if size_gb < 1:
            return f"{size_gb * 1024:.1f} MB"
        return f"{size_gb:.1f} GB"
```

---

## CloudFilesView

**Purpose:** Browse WebDAV cloud files

**Location:** `src/mini_datahub/ui/views/cloud_files.py`

### Layout

```
┌────────────────────────────────────────┐
│ Cloud Files                    10:30   │
├────────────────────────────────────────┤
│ Path: /research-datasets/datasets/     │
│                                        │
│ ┌────────────────────────────────────┐│
│ │ 📁 climate-data/                   ││
│ │ 📁 ocean-temp/                     ││
│ │ 📁 research-notes/                 ││
│ │ ...                                ││
│ └────────────────────────────────────┘│
│                                        │
│ 156 items | Last sync: 2 min ago      │
├────────────────────────────────────────┤
│ ESC: Back  Enter: Open  r: Refresh    │
└────────────────────────────────────────┘
```

### Implementation

```python
from textual.screen import Screen
from textual.widgets import DirectoryTree, Static
from textual.reactive import reactive

class CloudFilesView(Screen):
    """Browse cloud files"""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("r", "refresh", "Refresh"),
        ("d", "download", "Download"),
    ]

    current_path = reactive("")

    def compose(self):
        yield Header()
        yield Static("", id="path-display")
        yield DirectoryTree("/", id="file-tree")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load cloud files"""
        self.load_cloud_files()

    def load_cloud_files(self) -> None:
        """Fetch files from WebDAV"""
        from mini_datahub.services.webdav_storage import list_remote_files

        self.query_one("#status-bar", Static).update("Loading...")

        try:
            files = list_remote_files(path="datasets/")
            self.update_file_tree(files)

            status = f"{len(files)} items | Last sync: just now"
            self.query_one("#status-bar", Static).update(status)
        except Exception as e:
            self.notify(f"Failed to load files: {e}", severity="error")

    def action_refresh(self) -> None:
        """Refresh file list"""
        self.load_cloud_files()

    def on_directory_tree_file_selected(self, event) -> None:
        """Handle file selection"""
        file_path = event.path
        # Show file details or download options
```

---

## CreateDatasetView

**Purpose:** Form to create new dataset

**Location:** `src/mini_datahub/ui/views/create_dataset.py`

### Layout

```
┌────────────────────────────────────────┐
│ Create New Dataset             10:30   │
├────────────────────────────────────────┤
│                                        │
│ Dataset Name: *                        │
│ [Climate Model Data_______________]   │
│                                        │
│ Description: *                         │
│ ┌────────────────────────────────────┐│
│ │Historical climate model outputs    ││
│ │from CMIP6...                       ││
│ └────────────────────────────────────┘│
│                                        │
│ Storage Location:                      │
│ [/data/climate/cmip6______________]   │
│                                        │
│ File Format:                           │
│ [NetCDF▼]                             │
│                                        │
│ Projects: (comma-separated)            │
│ [climate-study, future-projections]   │
│                                        │
│ Keywords:                              │
│ [climate, temperature, precipitation] │
│                                        │
│  [Cancel]  [Save (Ctrl+S)]            │
├────────────────────────────────────────┤
│ ESC: Cancel  Ctrl+S: Save              │
└────────────────────────────────────────┘
```

### Implementation

```python
from textual.screen import Screen
from textual.widgets import Input, TextArea, Button, Select
from textual.containers import Vertical, Horizontal

class CreateDatasetView(Screen):
    """Create new dataset form"""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    def compose(self):
        yield Header()

        with Vertical(id="form-container"):
            yield Static("Dataset Name: *")
            yield Input(id="input-name")

            yield Static("Description: *")
            yield TextArea(id="input-description")

            yield Static("Storage Location:")
            yield Input(id="input-location")

            yield Static("File Format:")
            yield Select([
                ("NetCDF", "netcdf"),
                ("CSV", "csv"),
                ("HDF5", "hdf5"),
                ("JSON", "json"),
                ("Other", "other"),
            ], id="select-format")

            yield Static("Projects: (comma-separated)")
            yield Input(id="input-projects")

            yield Static("Keywords:")
            yield Input(id="input-keywords")

            with Horizontal(id="button-bar"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save (Ctrl+S)", id="btn-save", variant="primary")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self.action_save()

    def action_save(self) -> None:
        """Save new dataset"""
        # Collect form data
        name = self.query_one("#input-name", Input).value
        description = self.query_one("#input-description", TextArea).text
        location = self.query_one("#input-location", Input).value
        file_format = self.query_one("#select-format", Select).value
        projects = self.query_one("#input-projects", Input).value.split(",")
        keywords = self.query_one("#input-keywords", Input).value.split(",")

        # Validate
        if not name or not description:
            self.notify("Name and description are required", severity="error")
            return

        # Save dataset
        from mini_datahub.services.dataset_service import save_dataset

        metadata = {
            "id": name.lower().replace(" ", "-"),
            "dataset_name": name,
            "description": description,
            "storage_location": location,
            "file_format": file_format,
            "used_in_projects": [p.strip() for p in projects if p.strip()],
            "keywords": [k.strip() for k in keywords if k.strip()],
        }

        try:
            save_dataset(metadata)
            self.notify(f"Created dataset: {name}", severity="success")
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"Failed to save: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel and go back"""
        self.app.pop_screen()
```

---

## SettingsView

**Purpose:** Application settings

**Location:** `src/mini_datahub/ui/views/settings.py`

### Layout

```
┌────────────────────────────────────────┐
│ Settings                       10:30   │
├────────────────────────────────────────┤
│                                        │
│ Sync Settings                          │
│ ┌────────────────────────────────────┐│
│ │ [x] Auto-sync enabled              ││
│ │ Sync interval: [300] seconds       ││
│ │ Max retries: [3]                   ││
│ └────────────────────────────────────┘│
│                                        │
│ Search Settings                        │
│ ┌────────────────────────────────────┐│
│ │ Max results: [50]                  ││
│ │ [x] Enable fuzzy search            ││
│ │ [x] Enable stemming                ││
│ └────────────────────────────────────┘│
│                                        │
│ UI Settings                            │
│ ┌────────────────────────────────────┐│
│ │ Theme: [Nord▼]                     ││
│ │ [x] Show welcome screen            ││
│ └────────────────────────────────────┘│
│                                        │
│  [Cancel]  [Save]                     │
├────────────────────────────────────────┤
│ ESC: Back  Ctrl+S: Save                │
└────────────────────────────────────────┘
```

---

## OutboxView

**Purpose:** View and manage failed uploads

**Location:** `src/mini_datahub/ui/views/outbox.py`

### Layout

```
┌────────────────────────────────────────┐
│ Outbox - Failed Uploads        10:30   │
├────────────────────────────────────────┤
│                                        │
│ ┌────────────────────────────────────┐│
│ │ Dataset Name         Failed At     ││
│ ├────────────────────────────────────┤│
│ │ Climate Data         2 hours ago   ││
│ │ Ocean Temps          1 day ago     ││
│ └────────────────────────────────────┘│
│                                        │
│ 2 items in outbox                      │
│                                        │
│  [Retry All]  [Clear All]             │
├────────────────────────────────────────┤
│ ESC: Back  r: Retry  d: Delete         │
└────────────────────────────────────────┘
```

---

## DatasetDetailView

**Purpose:** View detailed dataset information

**Location:** `src/mini_datahub/ui/views/dataset_detail.py`

### Layout

```
┌────────────────────────────────────────┐
│ Climate Model Data             10:30   │
├────────────────────────────────────────┤
│                                        │
│ Description:                           │
│ Historical climate model outputs from  │
│ CMIP6 experiment. Includes temp...     │
│                                        │
│ Details:                               │
│ ├ Storage: /data/climate/cmip6        │
│ ├ Format: NetCDF                      │
│ ├ Size: 150.5 GB                      │
│ ├ Created: 2024-01-15                 │
│ └ Updated: 2024-03-10                 │
│                                        │
│ Projects:                              │
│ • climate-study                        │
│ • future-projections                   │
│                                        │
│ Keywords:                              │
│ climate, temperature, precipitation    │
│                                        │
│  [Edit]  [Delete]  [Close]            │
├────────────────────────────────────────┤
│ ESC: Close  e: Edit  d: Delete         │
└────────────────────────────────────────┘
```

---

## View Lifecycle

### Lifecycle Methods

```python
class MyView(Screen):
    def on_mount(self) -> None:
        """Called when view is mounted (after widgets created)"""
        # Initialize data, focus widgets, etc.
        pass

    def on_show(self) -> None:
        """Called when view becomes visible"""
        # Refresh data, start timers, etc.
        pass

    def on_hide(self) -> None:
        """Called when view is hidden"""
        # Stop timers, save state, etc.
        pass

    def on_unmount(self) -> None:
        """Called when view is removed"""
        # Cleanup resources
        pass
```

---

## Best Practices

### 1. Keep Views Focused

```python
# ✅ GOOD: Single responsibility
class SearchView(Screen):
    """Only handles search UI"""
    pass

# ❌ BAD: Too many responsibilities
class MegaView(Screen):
    """Search, create, edit, settings..."""
    pass
```

---

### 2. Extract Common Layouts

```python
# ✅ GOOD: Reusable base class
class FormView(Screen):
    """Base class for form views"""
    def compose_form(self, fields):
        # Common form layout
        pass

class CreateDatasetView(FormView):
    def compose(self):
        yield from self.compose_form(self.get_fields())
```

---

### 3. Use Reactive State

```python
# ✅ GOOD: Reactive updates
class SearchView(Screen):
    results = reactive([])

    def watch_results(self, new_results):
        self.update_table(new_results)
```

---

## Related Documentation

- **[UI Architecture](architecture.md)** - Overall UI design
- **[Widgets & Components](widgets.md)** - Custom widgets
- **[State Management](state.md)** - State patterns
- **[Adding New Views](adding-views.md)** - Create views

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
