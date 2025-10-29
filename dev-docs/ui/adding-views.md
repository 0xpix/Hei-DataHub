# Adding New Views

## Introduction

This guide walks you through creating new views/screens in the Hei-DataHub TUI.

---

## Overview

**What is a View?**
- A view is a full-screen UI component (Textual `Screen`)
- Handles user interaction for a specific feature
- Can be pushed/popped from the screen stack

**When to Create a New View:**
- New major feature requiring full screen
- Complex form or workflow
- Modal dialog or overlay

---

## Step-by-Step Guide

### Step 1: Define View Requirements

**Example:** Let's create a `StatisticsView` to show dataset statistics.

**Requirements:**
- Display total datasets, sync status, storage usage
- Show charts/graphs
- Refresh button
- Back navigation

---

### Step 2: Create View File

```bash
# Create file
touch src/hei_datahub/ui/views/statistics_view.py
```

**Basic Structure:**

```python
# src/hei_datahub/ui/views/statistics_view.py

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Container, Vertical, Horizontal

class StatisticsView(Screen):
    """View for displaying dataset statistics"""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Compose view layout"""
        yield Header()
        yield Container(
            Static("Statistics", classes="title"),
            Vertical(
                self._create_stats_panel(),
                self._create_charts_panel(),
                classes="main-content",
            ),
            Horizontal(
                Button("Refresh", id="refresh-btn"),
                Button("Back", id="back-btn"),
                classes="button-bar",
            ),
        )
        yield Footer()

    def _create_stats_panel(self) -> Container:
        """Create statistics panel"""
        return Container(
            Static("Total Datasets: 0", id="total-datasets"),
            Static("Synced: 0", id="synced-count"),
            Static("Storage: 0 MB", id="storage-usage"),
            classes="stats-panel",
        )

    def _create_charts_panel(self) -> Container:
        """Create charts panel"""
        return Container(
            Static("Chart placeholder", id="chart"),
            classes="charts-panel",
        )

    def on_mount(self) -> None:
        """Called when view is mounted"""
        self.load_statistics()

    def load_statistics(self) -> None:
        """Load and display statistics"""
        from hei_datahub.services.catalog import get_catalog_service

        catalog = get_catalog_service()
        stats = catalog.get_statistics()

        self.query_one("#total-datasets", Static).update(
            f"Total Datasets: {stats['total']}"
        )
        self.query_one("#synced-count", Static).update(
            f"Synced: {stats['synced']}"
        )
        self.query_one("#storage-usage", Static).update(
            f"Storage: {stats['storage_mb']} MB"
        )

    def action_back(self) -> None:
        """Navigate back"""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh statistics"""
        self.load_statistics()
        self.notify("Statistics refreshed")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "refresh-btn":
            self.action_refresh()
        elif event.button.id == "back-btn":
            self.action_back()
```

---

### Step 3: Create View Stylesheet

```css
/* src/hei_datahub/ui/tcss/views/statistics.tcss */

StatisticsView {
    background: $surface;
}

StatisticsView .title {
    text-style: bold;
    color: $primary;
    text-align: center;
    height: 3;
    content-align: center middle;
}

StatisticsView .main-content {
    height: 1fr;
    padding: 1;
}

StatisticsView .stats-panel {
    border: solid $primary;
    padding: 1;
    height: auto;
    margin-bottom: 1;
}

StatisticsView .stats-panel Static {
    height: auto;
    padding: 1;
}

StatisticsView .charts-panel {
    border: solid $accent;
    padding: 1;
    height: 1fr;
}

StatisticsView .button-bar {
    dock: bottom;
    height: 5;
    padding: 1;
    background: $surface-lighten-1;
    align: center middle;
}

StatisticsView Button {
    margin: 0 1;
}
```

---

### Step 4: Register View in App

```python
# src/hei_datahub/ui/app.py

from hei_datahub.ui.views.statistics_view import StatisticsView

class MiniDataHubApp(App):
    # Load stylesheet
    CSS_PATH = [
        "tcss/base.tcss",
        "tcss/views/statistics.tcss",  # Add new stylesheet
    ]

    # Add keybinding
    BINDINGS = [
        # ... existing bindings ...
        ("ctrl+t", "show_statistics", "Statistics"),
    ]

    def action_show_statistics(self) -> None:
        """Show statistics view"""
        self.push_screen(StatisticsView())
```

---

### Step 5: Add Navigation

**From HomeView:**

```python
# src/hei_datahub/ui/views/home_view.py

class HomeView(Screen):
    def compose(self) -> ComposeResult:
        yield Container(
            # ... existing widgets ...
            Button("Statistics", id="stats-btn"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "stats-btn":
            from hei_datahub.ui.views.statistics_view import StatisticsView
            self.app.push_screen(StatisticsView())
```

---

## Advanced Patterns

### View with Form Input

```python
class CreateDatasetView(Screen):
    """View with form inputs"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Create New Dataset", classes="title"),
            Vertical(
                Label("Title:"),
                Input(placeholder="Dataset title", id="title-input"),

                Label("Description:"),
                TextArea(id="description-input"),

                Label("Category:"),
                Select(
                    options=[
                        ("Research", "research"),
                        ("Teaching", "teaching"),
                        ("Admin", "admin"),
                    ],
                    id="category-select",
                ),

                Horizontal(
                    Button("Save", variant="primary", id="save-btn"),
                    Button("Cancel", id="cancel-btn"),
                    classes="button-bar",
                ),
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.save_dataset()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def save_dataset(self) -> None:
        """Validate and save dataset"""
        title = self.query_one("#title-input", Input).value
        description = self.query_one("#description-input", TextArea).text
        category = self.query_one("#category-select", Select).value

        # Validation
        if not title:
            self.notify("Title is required", severity="error")
            return

        # Save dataset
        from hei_datahub.services.catalog import get_catalog_service
        catalog = get_catalog_service()

        dataset = catalog.create_dataset(
            title=title,
            description=description,
            category=category,
        )

        self.notify(f"Dataset '{title}' created!", severity="success")
        self.app.pop_screen()
```

---

### View with Async Data Loading

```python
class CloudFilesView(Screen):
    """View with async data loading"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Cloud Files", classes="title"),
            LoadingIndicator(id="loading"),
            DataTable(id="files-table"),
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load data asynchronously"""
        await self.load_files()

    async def load_files(self) -> None:
        """Load files from cloud"""
        # Show loading indicator
        self.query_one("#loading").display = True
        self.query_one("#files-table").display = False

        try:
            # Async API call
            from hei_datahub.services.webdav_storage import get_webdav_storage
            storage = get_webdav_storage()

            files = await storage.list_files_async("/")

            # Update table
            table = self.query_one("#files-table", DataTable)
            table.clear()
            table.add_columns("Name", "Size", "Modified")

            for file in files:
                table.add_row(
                    file.name,
                    f"{file.size / 1024:.1f} KB",
                    file.modified.strftime("%Y-%m-%d %H:%M"),
                )

        except Exception as e:
            self.notify(f"Error loading files: {e}", severity="error")

        finally:
            # Hide loading, show table
            self.query_one("#loading").display = False
            self.query_one("#files-table").display = True
```

---

### Modal Dialog View

```python
class ConfirmDialog(Screen):
    """Modal confirmation dialog"""

    def __init__(self, message: str, on_confirm: callable):
        super().__init__()
        self.message = message
        self.on_confirm = on_confirm

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.message, classes="message"),
            Horizontal(
                Button("Confirm", variant="primary", id="confirm-btn"),
                Button("Cancel", id="cancel-btn"),
                classes="button-bar",
            ),
            classes="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self.on_confirm()
        self.app.pop_screen()

# Usage
def delete_dataset(dataset_id: str) -> None:
    """Delete with confirmation"""
    def confirm():
        # Actually delete
        catalog.delete_dataset(dataset_id)
        app.notify("Dataset deleted")

    app.push_screen(
        ConfirmDialog(
            "Are you sure you want to delete this dataset?",
            on_confirm=confirm,
        )
    )
```

---

## View Testing

### Unit Tests

```python
# tests/ui/views/test_statistics_view.py

from hei_datahub.ui.app import MiniDataHubApp
from hei_datahub.ui.views.statistics_view import StatisticsView

async def test_statistics_view_renders():
    """Test view renders correctly"""
    app = MiniDataHubApp()

    async with app.run_test() as pilot:
        app.push_screen(StatisticsView())

        # Verify widgets exist
        assert app.screen.query_one("#total-datasets")
        assert app.screen.query_one("#synced-count")
        assert app.screen.query_one("#storage-usage")

async def test_statistics_refresh():
    """Test refresh button"""
    app = MiniDataHubApp()

    async with app.run_test() as pilot:
        app.push_screen(StatisticsView())

        # Click refresh button
        await pilot.click("#refresh-btn")

        # Verify notification shown
        assert "refreshed" in app.notifications[-1].message

async def test_statistics_back_navigation():
    """Test back button"""
    app = MiniDataHubApp()

    async with app.run_test() as pilot:
        initial_screen = app.screen
        app.push_screen(StatisticsView())

        # Click back button
        await pilot.click("#back-btn")

        # Verify returned to initial screen
        assert app.screen == initial_screen
```

---

## Best Practices

### 1. Single Responsibility

```python
# ✅ GOOD: Focused view
class SearchView(Screen):
    """Handles search functionality only"""
    pass

# ❌ BAD: Kitchen sink view
class MegaView(Screen):
    """Handles search, create, edit, delete, settings..."""
    pass
```

---

### 2. Composition over Inheritance

```python
# ✅ GOOD: Compose widgets
class MyView(Screen):
    def compose(self) -> ComposeResult:
        yield CustomHeader()
        yield CustomTable()
        yield CustomFooter()

# ❌ BAD: Deep inheritance
class BaseView(Screen):
    pass

class MiddleView(BaseView):
    pass

class MyView(MiddleView):
    pass
```

---

### 3. Async Operations

```python
# ✅ GOOD: Non-blocking async
async def on_mount(self) -> None:
    await self.load_data()

async def load_data(self) -> None:
    data = await api.fetch_async()
    self.update_ui(data)

# ❌ BAD: Blocking sync
def on_mount(self) -> None:
    data = api.fetch_blocking()  # Freezes UI!
    self.update_ui(data)
```

---

### 4. Error Handling

```python
# ✅ GOOD: Graceful error handling
async def load_data(self) -> None:
    try:
        data = await api.fetch()
        self.update_ui(data)
    except NetworkError as e:
        self.notify(f"Network error: {e}", severity="error")
        self.show_error_state()
    except Exception as e:
        self.notify("Unexpected error", severity="error")
        logger.exception(e)

# ❌ BAD: Unhandled errors
async def load_data(self) -> None:
    data = await api.fetch()  # May crash!
    self.update_ui(data)
```

---

## Checklist for New Views

- [ ] View file created in `src/hei_datahub/ui/views/`
- [ ] Stylesheet created in `src/hei_datahub/ui/tcss/views/`
- [ ] Registered in `MiniDataHubApp`
- [ ] Keybindings defined
- [ ] Navigation added from other views
- [ ] Unit tests written
- [ ] Error handling implemented
- [ ] Async operations (if needed)
- [ ] Documentation updated
- [ ] Screenshot/demo added

---

## Related Documentation

- **[UI Architecture](architecture.md)** - Overall UI design
- **[Widgets & Components](widgets.md)** - Custom widgets
- **[Theming & Styling](theming.md)** - CSS styling
- **[State Management](state.md)** - Reactive state

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
