# State Management

## Introduction

This document explains how state is managed in the Hei-DataHub TUI using Textual's reactive programming model.

---

## Reactive Programming

### What is Reactive State?

Reactive variables automatically trigger updates when their values change:

```python
from textual.reactive import reactive

class MyView(Screen):
    count = reactive(0)  # Reactive variable

    def watch_count(self, new_value: int) -> None:
        """Called automatically when count changes"""
        self.update_display(new_value)

    def increment(self) -> None:
        self.count += 1  # Triggers watch_count automatically
```

---

## Application State

### Global App State

**Location:** `src/mini_datahub/ui/app.py`

```python
from textual.app import App
from textual.reactive import reactive

class MiniDataHubApp(App):
    """Main application with global state"""

    # Authentication state
    is_authenticated = reactive(False)
    current_user = reactive(None)

    # Sync state
    sync_status = reactive("idle")  # idle, syncing, success, error
    last_sync_time = reactive("")
    outbox_count = reactive(0)

    # UI state
    current_theme = reactive("nord")
    show_notifications = reactive(True)

    def watch_is_authenticated(self, authenticated: bool) -> None:
        """React to authentication changes"""
        if authenticated:
            self.notify("Logged in successfully")
            self.start_background_sync()
        else:
            self.notify("Logged out")
            self.stop_background_sync()

    def watch_sync_status(self, status: str) -> None:
        """Update UI when sync status changes"""
        header = self.query_one(Header)
        if status == "syncing":
            header.sync_indicator.start_animation()
        else:
            header.sync_indicator.stop_animation()

    def watch_outbox_count(self, count: int) -> None:
        """Notify when items in outbox"""
        if count > 0:
            self.notify(
                f"{count} items waiting in outbox",
                severity="warning"
            )
```

---

## View State

### Local View State

```python
class SearchView(Screen):
    """Search view with local state"""

    # Search state
    search_query = reactive("")
    results = reactive([])
    is_loading = reactive(False)

    # UI state
    selected_row = reactive(None)
    results_per_page = reactive(20)
    current_page = reactive(1)

    def watch_search_query(self, query: str) -> None:
        """Perform search when query changes"""
        if len(query) < 2:
            self.results = []
            return

        self.is_loading = True
        self.perform_search(query)

    def watch_results(self, results: list) -> None:
        """Update table when results change"""
        self.is_loading = False
        table = self.query_one(DatasetTable)
        table.load_datasets(results)

    def watch_is_loading(self, loading: bool) -> None:
        """Show/hide loading indicator"""
        spinner = self.query_one(LoadingSpinner)
        if loading:
            spinner.remove_class("hidden")
        else:
            spinner.add_class("hidden")

    def watch_current_page(self, page: int) -> None:
        """Load page data when page changes"""
        self.load_page(page)
```

---

## State Patterns

### 1. Computed State

**Derived from other reactive variables:**

```python
class DataView(Screen):
    datasets = reactive([])
    filter_text = reactive("")

    @property
    def filtered_datasets(self) -> list:
        """Computed: filtered based on current state"""
        if not self.filter_text:
            return self.datasets

        return [
            d for d in self.datasets
            if self.filter_text.lower() in d["name"].lower()
        ]

    def watch_filter_text(self, text: str) -> None:
        """Re-render when filter changes"""
        self.update_table(self.filtered_datasets)
```

---

### 2. Validation in Watchers

```python
class CreateDatasetView(Screen):
    dataset_name = reactive("")
    description = reactive("")

    def watch_dataset_name(self, name: str) -> None:
        """Validate name as user types"""
        name_input = self.query_one("#input-name", Input)

        if not name:
            name_input.add_class("invalid")
            self.show_error("Name is required")
        elif len(name) < 3:
            name_input.add_class("invalid")
            self.show_error("Name too short")
        else:
            name_input.remove_class("invalid")
            self.clear_error()
```

---

### 3. State Synchronization

**Sync reactive state with services:**

```python
class SyncView(Screen):
    sync_status = reactive("idle")

    async def start_sync(self) -> None:
        """Start sync and update state"""
        self.sync_status = "syncing"

        try:
            result = await sync_now_async()
            self.sync_status = "success"
            self.last_sync_result = result
        except Exception as e:
            self.sync_status = "error"
            self.error_message = str(e)

    def watch_sync_status(self, status: str) -> None:
        """Update UI based on sync status"""
        if status == "syncing":
            self.query_one("#btn-sync").disabled = True
        else:
            self.query_one("#btn-sync").disabled = False
```

---

## State Management Patterns

### Lifting State Up

**When multiple components need same state:**

```python
# ❌ BAD: Duplicate state in each component
class SearchInput(Widget):
    query = reactive("")

class ResultsTable(Widget):
    query = reactive("")  # Duplicate!

# ✅ GOOD: State in parent, passed to children
class SearchView(Screen):
    query = reactive("")  # Single source of truth

    def compose(self):
        yield SearchInput()
        yield ResultsTable()

    def watch_query(self, query: str) -> None:
        """Update both children"""
        self.query_one(SearchInput).set_query(query)
        self.query_one(ResultsTable).filter_by(query)
```

---

### State Reset on Navigation

```python
class SearchView(Screen):
    search_query = reactive("")
    results = reactive([])

    def on_show(self) -> None:
        """Reset state when view becomes visible"""
        self.search_query = ""
        self.results = []
        self.query_one(Input).value = ""
```

---

### Persisting State

```python
class SettingsView(Screen):
    theme = reactive("nord")
    auto_sync = reactive(True)

    def on_mount(self) -> None:
        """Load saved state"""
        config = load_config()
        self.theme = config.ui.theme
        self.auto_sync = config.sync.auto_sync

    def on_hide(self) -> None:
        """Save state when leaving view"""
        config = load_config()
        config.ui.theme = self.theme
        config.sync.auto_sync = self.auto_sync
        save_config(config)
```

---

## Message Passing

### Custom Messages

```python
from textual.message import Message

class DatasetSelected(Message):
    """Message: dataset was selected"""
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__()

class SyncCompleted(Message):
    """Message: sync completed"""
    def __init__(self, downloads: int, uploads: int):
        self.downloads = downloads
        self.uploads = uploads
        super().__init__()

# Post message
class DatasetTable(Widget):
    def on_row_selected(self, event) -> None:
        self.post_message(DatasetSelected(dataset_id))

# Handle message
class SearchView(Screen):
    def on_dataset_selected(self, message: DatasetSelected) -> None:
        """Handle dataset selection"""
        self.show_dataset_detail(message.dataset_id)
```

---

## Async State Updates

### Background Data Loading

```python
class CloudFilesView(Screen):
    files = reactive([])
    is_loading = reactive(False)

    def on_mount(self) -> None:
        """Load data asynchronously"""
        self.load_files()

    @work(thread=True)  # Run in background thread
    async def load_files(self) -> None:
        """Fetch files from WebDAV"""
        self.is_loading = True

        try:
            files = await fetch_cloud_files()
            self.files = files
        except Exception as e:
            self.notify(f"Failed to load: {e}", severity="error")
        finally:
            self.is_loading = False
```

---

### Debounced Updates

```python
from textual import work

class SearchView(Screen):
    search_query = reactive("")

    def watch_search_query(self, query: str) -> None:
        """Debounce search to avoid too many requests"""
        self.search_debounced(query)

    @work(exclusive=True)  # Cancel previous work
    async def search_debounced(self, query: str) -> None:
        """Perform search with debounce"""
        await asyncio.sleep(0.3)  # Wait 300ms

        results = await perform_search(query)
        self.results = results
```

---

## State Debugging

### Logging State Changes

```python
class MyView(Screen):
    count = reactive(0, init=False)  # init=False prevents watch on init

    def watch_count(self, old_value: int, new_value: int) -> None:
        """Log state changes"""
        self.log(f"count changed: {old_value} → {new_value}")
```

---

### State Inspection

```python
# In Textual console (Ctrl+T in dev mode)
>>> app.screen.search_query
"climate"

>>> app.sync_status
"idle"

>>> app.screen.results
[{...}, {...}, ...]
```

---

## Best Practices

### 1. Initialize with Defaults

```python
# ✅ GOOD: Explicit defaults
class MyView(Screen):
    count = reactive(0)
    items = reactive([])
    status = reactive("idle")

# ❌ BAD: No defaults (will be None)
class MyView(Screen):
    count = reactive()  # None, may cause errors
```

---

### 2. Use Type Hints

```python
# ✅ GOOD: Type hints for clarity
class MyView(Screen):
    count: reactive[int] = reactive(0)
    items: reactive[list] = reactive([])

# ❌ BAD: No type hints
class MyView(Screen):
    count = reactive(0)
```

---

### 3. Avoid Side Effects in Watchers

```python
# ✅ GOOD: Pure watcher, minimal side effects
def watch_query(self, query: str) -> None:
    self.update_display(query)

# ❌ BAD: Complex logic in watcher
def watch_query(self, query: str) -> None:
    # Too much logic here
    results = search(query)
    filtered = filter_results(results)
    sorted_results = sort(filtered)
    self.update_table(sorted_results)
    self.save_to_cache(sorted_results)
    self.log_search(query)
```

---

### 4. One Source of Truth

```python
# ✅ GOOD: Single state variable
class SearchView(Screen):
    datasets = reactive([])  # Single source

    @property
    def visible_datasets(self):
        return self.datasets[:20]  # Computed from single source

# ❌ BAD: Duplicate state
class SearchView(Screen):
    all_datasets = reactive([])
    visible_datasets = reactive([])  # Duplicate!
```

---

## Related Documentation

- **[UI Architecture](architecture.md)** - UI design patterns
- **[Views & Screens](views.md)** - Screen documentation
- **[Widgets & Components](widgets.md)** - Custom widgets

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
