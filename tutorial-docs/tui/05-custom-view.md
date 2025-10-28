# Adding Your Own UI Screen

**Learning Goal**: Build a complete custom screen from scratch with navigation, data loading, and lifecycle management.

By the end of this page, you'll:
- Create new screen classes
- Design layouts with `compose()`
- Load data with `on_mount()`
- Navigate between screens
- Handle errors gracefully
- Style custom screens with TCSS
- Build a real **Statistics Screen**

---

## Understanding Screens

### What is a Screen?

A **Screen** is a full-page view in Textual:

```
┌─ HomeScreen ───────────────┐
│ Search: _                  │
│ Results: [...]             │
│                            │
└────────────────────────────┘
     │ User presses Enter
     ↓
┌─ DetailsScreen ────────────┐
│ Dataset: climate-data-2023 │
│ Name: ...                  │
│ Source: ...                │
└────────────────────────────┘
     │ User presses Escape
     ↓
┌─ HomeScreen ───────────────┐
│ Search: _                  │
│ Results: [...]             │
│                            │
└────────────────────────────┘
```

**Screens form a stack:**
- `push_screen()` — Add a new screen on top
- `pop_screen()` — Remove top screen, return to previous

---

## Screen Lifecycle

### The Four Phases

```python
class MyScreen(Screen):
    """Screen lifecycle example."""

    def __init__(self, some_id: str):
        """1. INITIALIZATION - Create the screen object."""
        super().__init__()
        self.some_id = some_id
        print(f"Screen created for {some_id}")

    def compose(self) -> ComposeResult:
        """2. COMPOSITION - Build the widget tree."""
        print("Building widgets...")
        yield Header()
        yield Label(f"Viewing {self.some_id}")
        yield Footer()

    def on_mount(self) -> None:
        """3. MOUNTING - Setup after widgets are added to DOM."""
        print("Screen mounted, widgets are ready")
        # ✅ Safe to query widgets here
        # ✅ Load data here
        # ✅ Set up timers here

    def on_unmount(self) -> None:
        """4. UNMOUNTING - Cleanup before screen is removed."""
        print("Screen is being removed")
        # ✅ Cancel timers here
        # ✅ Close file handles here
```

**Flow:**
1. `__init__()` → Create object, store parameters
2. `compose()` → Define widget tree
3. `on_mount()` → Setup, load data (widgets exist now!)
4. User interacts with screen...
5. `on_unmount()` → Cleanup before removal

---

## Building Your First Screen

### Step 1: Create the Class

**File:** `src/hei_datahub/ui/views/stats.py`

```python
"""Statistics screen showing dataset metrics."""
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Label, Static
from textual.containers import VerticalScroll
from textual.binding import Binding

class StatsScreen(Screen):
    """Display statistics about datasets."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back", show=False),
        Binding("r", "refresh", "Refresh", key_display="r"),
    ]

    def __init__(self):
        super().__init__()
        self.stats = {}  # Will store computed statistics
```

---

### Step 2: Define the Layout

```python
    def compose(self) -> ComposeResult:
        """Build the screen layout."""
        yield Header()
        yield VerticalScroll(
            Label("📊 Dataset Statistics", classes="title"),
            Static(id="stats-content"),  # Stats will go here
            id="stats-container"
        )
        yield Footer()
```

**What's happening:**
- `Header()` — Shows screen title
- `VerticalScroll()` — Scrollable container
- `Label()` with `classes="title"` — Page heading
- `Static(id="stats-content")` — Content area (updated later)
- `Footer()` — Shows keybindings

---

### Step 3: Load Data on Mount

```python
    def on_mount(self) -> None:
        """Load statistics when screen mounts."""
        self.load_statistics()

    def load_statistics(self) -> None:
        """Compute and display statistics."""
        try:
            from hei_datahub.infra.index import list_all_datasets

            # Get all datasets
            datasets = list_all_datasets()

            # Compute stats
            total_count = len(datasets)

            # Count by data type
            type_counts = {}
            for ds in datasets:
                data_types = ds.get('metadata', {}).get('data_types', [])
                for dt in data_types:
                    type_counts[dt] = type_counts.get(dt, 0) + 1

            # Sort by count
            top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # Format output
            lines = []
            lines.append(f"[bold]Total Datasets:[/bold] {total_count}")
            lines.append("")
            lines.append("[bold]Top 5 Data Types:[/bold]")
            for dtype, count in top_types:
                lines.append(f"  • {dtype}: {count}")

            # Update the Static widget
            content = self.query_one("#stats-content", Static)
            content.update("\n".join(lines))

        except Exception as e:
            # Show error message
            content = self.query_one("#stats-content", Static)
            content.update(f"[red]Error loading stats: {str(e)}[/red]")
            self.app.notify(f"Stats failed: {str(e)}", severity="error", timeout=5)
```

**Key concepts:**
- `on_mount()` — Runs after widgets exist
- `query_one("#stats-content", Static)` — Find widget by ID
- `content.update(text)` — Change widget content
- Error handling — Show user-friendly messages

---

### Step 4: Add Navigation Actions

```python
    def action_back(self) -> None:
        """Return to previous screen (Escape or q)."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Reload statistics (r key)."""
        self.app.notify("Refreshing statistics...", timeout=1)
        self.load_statistics()
```

---

### Step 5: Add Styling

**File:** `src/hei_datahub/ui/styles/stats.tcss`

```css
#stats-container {
    padding: 1 2;
}

.title {
    text-align: center;
    text-style: bold;
    margin: 1 0;
    color: $primary;
}

#stats-content {
    margin: 1 0;
    padding: 1 2;
    background: $surface;
    border: solid $primary;
}
```

**Load it in the screen:**

```python
class StatsScreen(Screen):
    """Display statistics about datasets."""

    CSS_PATH = "../styles/stats.tcss"  # ← Add this

    # ... rest of class
```

---

## Navigating to Your Screen

### From the Home Screen

**File:** `src/hei_datahub/ui/views/home.py`

```python
class HomeScreen(Screen):
    BINDINGS = [
        # ... existing bindings ...
        Binding("S", "show_stats", "Statistics", key_display="S"),
    ]

    def action_show_stats(self) -> None:
        """Open statistics screen (Shift+S)."""
        from hei_datahub.ui.views.stats import StatsScreen
        self.app.push_screen(StatsScreen())
```

**Flow:**
1. User presses `Shift+S` on home screen
2. `action_show_stats()` fires
3. Imports `StatsScreen`
4. Calls `self.app.push_screen(StatsScreen())`
5. Stats screen appears
6. User presses `Escape`
7. `action_back()` calls `self.app.pop_screen()`
8. Returns to home screen

---

## Complete Example: Statistics Screen

**File:** `src/hei_datahub/ui/views/stats.py`

```python
"""Statistics screen showing dataset metrics."""
import logging
from typing import Dict, List, Any

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Label, Static, DataTable
from textual.containers import VerticalScroll, Container
from textual.binding import Binding

logger = logging.getLogger(__name__)


class StatsScreen(Screen):
    """Display statistics about datasets."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back", show=False),
        Binding("r", "refresh", "Refresh", key_display="r"),
    ]

    CSS_PATH = "../styles/stats.tcss"

    def __init__(self):
        super().__init__()
        self.stats: Dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Build the screen layout."""
        yield Header()
        yield VerticalScroll(
            Label("📊 Dataset Statistics", classes="title"),
            Container(
                Static(id="summary-stats"),
                Static(id="type-breakdown"),
                Static(id="recent-activity"),
                id="stats-container"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load statistics when screen mounts."""
        self.load_statistics()

    def load_statistics(self) -> None:
        """Compute and display statistics."""
        try:
            from hei_datahub.infra.index import list_all_datasets
            from datetime import datetime, date

            # Get all datasets
            datasets = list_all_datasets()

            # 1. Summary Stats
            total_count = len(datasets)
            local_count = sum(1 for ds in datasets
                            if not ds.get('metadata', {}).get('is_remote', False))
            cloud_count = sum(1 for ds in datasets
                            if ds.get('metadata', {}).get('is_remote', False))

            summary_lines = [
                "[bold cyan]Summary[/bold cyan]",
                "",
                f"Total Datasets: [bold]{total_count}[/bold]",
                f"  • Local: {local_count}",
                f"  • Cloud: {cloud_count}",
            ]

            summary = self.query_one("#summary-stats", Static)
            summary.update("\n".join(summary_lines))

            # 2. Data Type Breakdown
            type_counts: Dict[str, int] = {}
            for ds in datasets:
                data_types = ds.get('metadata', {}).get('data_types', [])
                for dt in data_types:
                    type_counts[dt] = type_counts.get(dt, 0) + 1

            top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            type_lines = [
                "[bold cyan]Top Data Types[/bold cyan]",
                "",
            ]
            for dtype, count in top_types:
                type_lines.append(f"  {dtype}: {count}")

            if not top_types:
                type_lines.append("  [dim]No data types recorded[/dim]")

            types_widget = self.query_one("#type-breakdown", Static)
            types_widget.update("\n".join(type_lines))

            # 3. Recent Activity
            recent_datasets = sorted(
                datasets,
                key=lambda x: x.get('metadata', {}).get('date_created', ''),
                reverse=True
            )[:3]

            activity_lines = [
                "[bold cyan]Recently Added[/bold cyan]",
                "",
            ]
            for ds in recent_datasets:
                name = ds.get('metadata', {}).get('dataset_name', 'Unknown')
                date_created = ds.get('metadata', {}).get('date_created', 'N/A')
                activity_lines.append(f"  • {name} ({date_created})")

            if not recent_datasets:
                activity_lines.append("  [dim]No datasets found[/dim]")

            activity_widget = self.query_one("#recent-activity", Static)
            activity_widget.update("\n".join(activity_lines))

            self.app.notify("Statistics loaded", timeout=1)

        except Exception as e:
            logger.error(f"Failed to load statistics: {e}", exc_info=True)

            # Show error in summary widget
            summary = self.query_one("#summary-stats", Static)
            summary.update(f"[red]Error: {str(e)}[/red]")

            self.app.notify(f"Stats failed: {str(e)}", severity="error", timeout=5)

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Reload statistics."""
        self.app.notify("Refreshing...", timeout=1)
        self.load_statistics()
```

**TCSS File:** `src/hei_datahub/ui/styles/stats.tcss`

```css
#stats-container {
    padding: 1 2;
}

.title {
    text-align: center;
    text-style: bold;
    margin: 1 0;
    color: $primary;
}

#summary-stats, #type-breakdown, #recent-activity {
    margin: 1 0;
    padding: 1 2;
    background: $surface;
    border: solid $accent;
}
```

---

## Passing Data to Screens

### Example: Details Screen with ID

**File:** `src/hei_datahub/ui/views/home.py` (Lines 913-930)

```python
class DetailsScreen(Screen):
    """View dataset details."""

    def __init__(self, dataset_id: str):
        """
        Create details screen for a specific dataset.

        Args:
            dataset_id: ID of the dataset to display
        """
        super().__init__()
        self.dataset_id = dataset_id  # Store parameter
        self.metadata = None

    def on_mount(self) -> None:
        """Load dataset details."""
        from hei_datahub.infra.index import get_dataset_from_store

        self.metadata = get_dataset_from_store(self.dataset_id)
        # ... display metadata
```

**Opening it:**

```python
def action_open_details(self) -> None:
    """Open details for selected dataset."""
    table = self.query_one("#results-table", DataTable)
    if table.cursor_row is not None:
        row_key = table.get_row_key_at(table.cursor_row)
        dataset_id = row_key.value

        # Pass dataset_id to screen
        self.app.push_screen(DetailsScreen(dataset_id))
```

---

## Async Data Loading

### Using @work Decorator

For long-running tasks (API calls, slow queries):

```python
from textual import work

class MyScreen(Screen):
    def on_mount(self) -> None:
        """Start async data load."""
        self.load_data_async()

    @work(exclusive=True)
    async def load_data_async(self) -> None:
        """
        Load data asynchronously.

        Args:
            exclusive: Only one instance runs at a time
        """
        content = self.query_one("#content", Static)
        content.update("Loading...")

        # Simulate slow operation
        import asyncio
        await asyncio.sleep(2)

        # Update UI on main thread
        content.update("Data loaded!")
        self.app.notify("Done!", timeout=1)
```

**Benefits:**
- UI stays responsive
- User can still press keys
- Loading indicator shows progress

---

## Error Handling Patterns

### 1. Try/Except in on_mount

```python
def on_mount(self) -> None:
    """Load data with error handling."""
    try:
        self.load_data()
    except FileNotFoundError:
        self.show_error("Data file not found")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        self.show_error(f"Failed to load: {str(e)}")

def show_error(self, message: str) -> None:
    """Display error message to user."""
    content = self.query_one("#content", Static)
    content.update(f"[red]{message}[/red]")
    self.app.notify(message, severity="error", timeout=5)
```

---

### 2. Graceful Degradation

```python
def load_stats(self) -> None:
    """Load stats with fallbacks."""
    try:
        datasets = list_all_datasets()
    except Exception as e:
        logger.warning(f"Failed to load datasets: {e}")
        datasets = []  # Fallback to empty list

    # Continue with empty data
    if not datasets:
        self.show_empty_state()
    else:
        self.show_stats(datasets)

def show_empty_state(self) -> None:
    """Show friendly message when no data."""
    content = self.query_one("#content", Static)
    content.update("[dim]No datasets found. Press 'a' to add one![/dim]")
```

---

## Screen Communication

### Returning Data to Previous Screen

**Problem:** User edits a dataset, parent screen needs to refresh.

**Solution:** Use `push_screen()` callback:

```python
# Parent screen (HomeScreen)
def action_edit_dataset(self, dataset_id: str) -> None:
    """Open edit screen and refresh on return."""
    def on_edit_complete(result: bool) -> None:
        """Called when edit screen is popped."""
        if result:
            self.app.notify("Dataset updated!", timeout=2)
            self.load_all_datasets()  # Refresh table

    self.app.push_screen(
        EditScreen(dataset_id),
        callback=on_edit_complete  # Pass callback
    )

# Child screen (EditScreen)
def action_save(self) -> None:
    """Save changes and return."""
    # ... save logic ...
    self.dismiss(True)  # Return True to callback

def action_cancel(self) -> None:
    """Cancel and return."""
    self.dismiss(False)  # Return False to callback
```

**Flow:**
1. Parent calls `push_screen(EditScreen, callback=on_edit_complete)`
2. User edits dataset
3. User presses Save → `dismiss(True)`
4. `on_edit_complete(True)` fires
5. Parent refreshes data

---

## Real Example: Settings Screen

**File:** `src/hei_datahub/ui/views/settings.py` (Lines 1-60)

```python
class SettingsScreen(Screen):
    """Configure WebDAV cloud storage."""

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("q", "cancel", "Back"),
        Binding("ctrl+s", "save", "Save", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("☁️ WebDAV Settings", classes="title"),
            Container(
                Label("WebDAV URL:"),
                Input(placeholder="https://heibox.uni-heidelberg.de/seafdav", id="input-url"),
                Label("Library Name:"),
                Input(placeholder="testing-hei-datahub", id="input-library"),
                Label("Username:"),
                Input(placeholder="your-username", id="input-username"),
                Label("Password:"),
                Input(placeholder="your-password", password=True, id="input-token"),
                Horizontal(
                    Button("Test Connection", id="test-btn"),
                    Button("Save", id="save-btn", variant="primary"),
                    Button("Cancel", id="cancel-btn"),
                ),
                Label("", id="status-message"),
                id="settings-container",
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load current settings from config file."""
        try:
            from hei_datahub.infra.config_paths import get_config_path
            import tomllib as tomli

            config_path = get_config_path()
            if config_path.exists():
                with open(config_path, "rb") as f:
                    config = tomli.load(f)

                # Pre-fill form
                auth_config = config.get("auth", {})
                self.query_one("#input-url", Input).value = auth_config.get("url", "")
                self.query_one("#input-username", Input).value = auth_config.get("username", "")

            # Focus first input
            self.query_one("#input-url", Input).focus()

        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
```

**Key features:**
- Pre-fills form from config file
- Has "Test Connection" button
- Saves to TOML config
- Uses `password=True` for sensitive inputs

---

## What You've Learned

✅ **Screen lifecycle** — `__init__` → `compose` → `on_mount` → `on_unmount`
✅ **Navigation** — `push_screen()` and `pop_screen()`
✅ **Data loading** — Load in `on_mount()`, async with `@work`
✅ **Error handling** — Try/except, fallbacks, user-friendly messages
✅ **Passing parameters** — `__init__(self, some_id: str)`
✅ **Screen communication** — Callbacks with `dismiss(result)`
✅ **Styling** — CSS_PATH and TCSS files

---

## Try It Yourself

### Exercise 1: Build the Stats Screen

**Steps:**

1. Create `src/hei_datahub/ui/views/stats.py` with the complete example above

2. Create `src/hei_datahub/ui/styles/stats.tcss` with the CSS above

3. Add keybinding to `HomeScreen`:
```python
Binding("S", "show_stats", "Stats", key_display="S")
```

4. Add action method:
```python
def action_show_stats(self) -> None:
    from hei_datahub.ui.views.stats import StatsScreen
    self.app.push_screen(StatsScreen())
```

5. Run the app and press `Shift+S` — your stats screen appears!

---

### Exercise 2: Add a Search Filter

**Goal:** Add a "Show only cloud datasets" checkbox to Stats screen.

**Hint:** Use a `Checkbox` widget and filter datasets:

```python
from textual.widgets import Checkbox

def compose(self) -> ComposeResult:
    yield Checkbox("Show only cloud datasets", id="cloud-filter")

def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
    self.load_statistics()  # Reload with filter

def load_statistics(self) -> None:
    datasets = list_all_datasets()

    # Apply filter
    checkbox = self.query_one("#cloud-filter", Checkbox)
    if checkbox.value:
        datasets = [ds for ds in datasets
                   if ds.get('metadata', {}).get('is_remote', False)]

    # ... rest of stats logic
```

---

### Exercise 3: Add Export Button

**Goal:** Export stats to a JSON file.

**Hint:**

```python
from textual.widgets import Button
import json

def compose(self) -> ComposeResult:
    # ... existing layout ...
    yield Button("Export to JSON", id="export-btn")

@on(Button.Pressed, "#export-btn")
def on_export_button(self) -> None:
    from pathlib import Path

    output_file = Path.home() / "hei-datahub-stats.json"
    with open(output_file, "w") as f:
        json.dump(self.stats, f, indent=2)

    self.app.notify(f"Exported to {output_file}", timeout=3)
```

---

## Next Steps

Now you understand the **UI layer**! Time to dive deeper into the **Logic layer** — how data flows from UI to Services to Infrastructure.

**Next:** [Understanding Data Flow](../logic/01-ui-actions.md)

---


## Further Reading

- [Textual Screens Guide](https://textual.textualize.io/guide/screens/)
- [Screen API Reference](https://textual.textualize.io/api/screen/)
- [Workers (@work)](https://textual.textualize.io/guide/workers/)
- [Hei-DataHub UI Architecture](../../ui/architecture.md)
