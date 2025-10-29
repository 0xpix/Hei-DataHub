# Theming & Styling

## Introduction

Hei-DataHub uses Textual's CSS system for styling the TUI. This document covers themes, colors, and customization.

---

## CSS Architecture

### File Structure

```
src/hei_datahub/ui/
├── tcss/
│   ├── base.tcss           # Base styles
│   ├── themes/
│   │   ├── default.tcss    # Default theme
│   │   ├── dark.tcss       # Dark theme
│   │   └── light.tcss      # Light theme
│   ├── components/
│   │   ├── table.tcss      # Table styles
│   │   ├── input.tcss      # Input styles
│   │   └── buttons.tcss    # Button styles
│   └── views/
│       ├── home.tcss       # Home view styles
│       └── search.tcss     # Search view styles
```

---

## Default Theme

### Color Palette

```css
/* tcss/themes/default.tcss */

:root {
    /* Primary colors */
    --primary: #0178D4;
    --primary-darken-1: #015A9C;
    --primary-darken-2: #013E6B;
    --primary-lighten-1: #4AA8E8;

    /* Accent colors */
    --accent: #00D4AA;
    --accent-darken-1: #00A886;

    /* Background colors */
    --surface: #1E1E1E;
    --surface-lighten-1: #2D2D2D;
    --surface-lighten-2: #3C3C3C;

    /* Text colors */
    --text: #E0E0E0;
    --text-muted: #A0A0A0;
    --text-disabled: #666666;

    /* Status colors */
    --success: #10B981;
    --warning: #F59E0B;
    --error: #EF4444;
    --info: #3B82F6;
}
```

---

### Typography

```css
/* tcss/base.tcss */

* {
    /* Default text */
    color: $text;
    text-style: none;
}

.title {
    text-style: bold;
    color: $primary;
}

.subtitle {
    text-style: italic;
    color: $text-muted;
}

.code {
    text-style: bold;
    color: $accent;
}

.error-text {
    color: $error;
    text-style: bold;
}
```

---

## Component Styling

### Tables

```css
/* tcss/components/table.tcss */

DataTable {
    height: 100%;
    width: 100%;
}

DataTable > .datatable--header {
    background: $surface-lighten-1;
    color: $primary;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: $primary;
    color: white;
}

DataTable > .datatable--odd-row {
    background: $surface;
}

DataTable > .datatable--even-row {
    background: $surface-lighten-1;
}

DataTable:focus > .datatable--cursor {
    background: $primary-lighten-1;
}
```

**Usage:**

```python
class DatasetTable(DataTable):
    """Custom styled table"""

    DEFAULT_CSS = """
    DatasetTable {
        border: solid $primary;
    }

    DatasetTable > .datatable--header {
        text-align: left;
        padding: 0 2;
    }
    """
```

---

### Input Fields

```css
/* tcss/components/input.tcss */

Input {
    border: solid $surface-lighten-2;
    background: $surface;
    color: $text;
}

Input:focus {
    border: solid $primary;
}

Input.-invalid {
    border: solid $error;
}

Input.-valid {
    border: solid $success;
}
```

**Implementation:**

```python
class StyledInput(Input):
    """Input with validation styling"""

    def watch_value(self, value: str) -> None:
        """Update styling based on validation"""
        if self.validate(value):
            self.remove_class("-invalid")
            self.add_class("-valid")
        else:
            self.remove_class("-valid")
            self.add_class("-invalid")
```

---

### Buttons

```css
/* tcss/components/buttons.tcss */

Button {
    background: $primary;
    color: white;
    border: none;
    text-style: bold;
    min-width: 16;
    height: 3;
}

Button:hover {
    background: $primary-lighten-1;
}

Button:focus {
    border: solid white;
}

Button.-primary {
    background: $primary;
}

Button.-success {
    background: $success;
}

Button.-warning {
    background: $warning;
}

Button.-danger {
    background: $error;
}

Button.-ghost {
    background: transparent;
    border: solid $primary;
    color: $primary;
}
```

---

## View Styling

### HomeView

```css
/* tcss/views/home.tcss */

HomeView {
    background: $surface;
}

HomeView .header {
    dock: top;
    height: 5;
    background: $primary;
    color: white;
    content-align: center middle;
}

HomeView .main-container {
    height: 1fr;
    layout: grid;
    grid-size: 2 1;
    grid-gutter: 1 1;
    padding: 1;
}

HomeView .stats-panel {
    border: solid $primary;
    padding: 1;
    height: 100%;
}

HomeView .quick-actions {
    border: solid $accent;
    padding: 1;
    height: 100%;
}

HomeView .footer {
    dock: bottom;
    height: 3;
    background: $surface-lighten-1;
    content-align: center middle;
}
```

---

### SearchView

```css
/* tcss/views/search.tcss */

SearchView {
    background: $surface;
}

SearchView .search-header {
    dock: top;
    height: 5;
    padding: 1;
}

SearchView Input {
    width: 100%;
    border: solid $primary;
}

SearchView .results-container {
    height: 1fr;
    padding: 1;
}

SearchView .no-results {
    color: $text-muted;
    text-align: center;
    text-style: italic;
}
```

---

## Custom Themes

### Creating a New Theme

**1. Define Color Variables:**

```css
/* tcss/themes/custom.tcss */

:root {
    --primary: #8B5CF6;        /* Purple */
    --accent: #F59E0B;          /* Amber */
    --surface: #111827;         /* Dark gray */
    --text: #F3F4F6;            /* Light gray */
    --success: #10B981;
    --warning: #F59E0B;
    --error: #EF4444;
}
```

**2. Apply Theme:**

```python
# src/hei_datahub/ui/app.py

class MiniDataHubApp(App):
    # Load custom theme
    CSS_PATH = "tcss/themes/custom.tcss"

    def __init__(self, theme: str = "default"):
        super().__init__()
        self.theme = theme
        self.load_theme(theme)

    def load_theme(self, theme: str) -> None:
        """Load theme CSS"""
        theme_path = Path(__file__).parent / f"tcss/themes/{theme}.tcss"
        if theme_path.exists():
            self.stylesheet.load(theme_path)
```

---

### Light Theme

```css
/* tcss/themes/light.tcss */

:root {
    --primary: #0178D4;
    --accent: #00B894;

    /* Light backgrounds */
    --surface: #FFFFFF;
    --surface-lighten-1: #F5F5F5;
    --surface-lighten-2: #E0E0E0;

    /* Dark text */
    --text: #1E1E1E;
    --text-muted: #666666;
    --text-disabled: #999999;

    --success: #10B981;
    --warning: #F59E0B;
    --error: #EF4444;
}

/* Adjust component styles for light theme */
DataTable {
    border: solid #E0E0E0;
}

Input {
    border: solid #CCCCCC;
    background: #FFFFFF;
}
```

---

## Dynamic Styling

### Reactive Styles

```python
from textual.reactive import reactive
from textual.widget import Widget

class SyncStatus(Widget):
    """Widget with reactive styling"""

    status: reactive[str] = reactive("idle")

    DEFAULT_CSS = """
    SyncStatus {
        height: 3;
        padding: 1;
        border: solid;
    }

    SyncStatus.-idle {
        border: solid $text-muted;
        color: $text-muted;
    }

    SyncStatus.-syncing {
        border: solid $info;
        color: $info;
    }

    SyncStatus.-success {
        border: solid $success;
        color: $success;
    }

    SyncStatus.-error {
        border: solid $error;
        color: $error;
    }
    """

    def watch_status(self, new_status: str) -> None:
        """Update CSS class based on status"""
        # Remove all status classes
        self.remove_class("-idle", "-syncing", "-success", "-error")
        # Add new status class
        self.add_class(f"-{new_status}")
```

---

### Conditional Styling

```python
class DatasetRow(Widget):
    """Row with conditional styling"""

    is_synced: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    DatasetRow {
        height: 3;
        padding: 1;
    }

    DatasetRow.-synced {
        color: $success;
    }

    DatasetRow.-not-synced {
        color: $warning;
    }
    """

    def watch_is_synced(self, synced: bool) -> None:
        """Update style based on sync status"""
        if synced:
            self.remove_class("-not-synced")
            self.add_class("-synced")
        else:
            self.remove_class("-synced")
            self.add_class("-not-synced")
```

---

## Layout Patterns

### Grid Layout

```css
.grid-container {
    layout: grid;
    grid-size: 3 2;          /* 3 columns, 2 rows */
    grid-gutter: 1 1;        /* Horizontal, vertical gaps */
    padding: 1;
}

.grid-item {
    border: solid $primary;
    padding: 1;
}

/* Spanning cells */
.grid-item-wide {
    column-span: 2;          /* Span 2 columns */
}

.grid-item-tall {
    row-span: 2;             /* Span 2 rows */
}
```

---

### Horizontal/Vertical Layout

```css
.horizontal-container {
    layout: horizontal;
    height: auto;
}

.horizontal-container > * {
    width: 1fr;              /* Equal width */
    margin: 0 1;
}

.vertical-container {
    layout: vertical;
    width: auto;
}

.vertical-container > * {
    height: auto;
    margin: 1 0;
}
```

---

### Docking

```css
.header {
    dock: top;
    height: 5;
    background: $primary;
}

.sidebar {
    dock: left;
    width: 30;
    background: $surface-lighten-1;
}

.footer {
    dock: bottom;
    height: 3;
    background: $surface-lighten-1;
}

.main-content {
    /* Fills remaining space */
    height: 1fr;
    width: 1fr;
}
```

---

## Best Practices

### 1. Use CSS Variables

```css
/* ✅ GOOD: Use variables for consistency */
.my-widget {
    background: $surface;
    color: $text;
    border: solid $primary;
}

/* ❌ BAD: Hard-coded colors */
.my-widget {
    background: #1E1E1E;
    color: #E0E0E0;
    border: solid #0178D4;
}
```

---

### 2. Semantic Class Names

```css
/* ✅ GOOD: Semantic names */
.-success { color: $success; }
.-error { color: $error; }
.-loading { color: $info; }

/* ❌ BAD: Style-based names */
.-green { color: green; }
.-red { color: red; }
.-blue { color: blue; }
```

---

### 3. Component-Scoped Styles

```python
# ✅ GOOD: Scoped to component
class MyWidget(Widget):
    DEFAULT_CSS = """
    MyWidget {
        border: solid $primary;
    }

    MyWidget .title {
        text-style: bold;
    }
    """

# ❌ BAD: Global styles
class MyWidget(Widget):
    DEFAULT_CSS = """
    * {
        border: solid $primary;
    }
    """
```

---

### 4. Reusable Styles

```css
/* ✅ GOOD: Reusable utility classes */
.text-center { text-align: center; }
.text-bold { text-style: bold; }
.text-muted { color: $text-muted; }

.border-primary { border: solid $primary; }
.border-success { border: solid $success; }

.p-1 { padding: 1; }
.p-2 { padding: 2; }
.m-1 { margin: 1; }
```

---

## Testing Themes

### Snapshot Testing

```python
# tests/ui/test_theming.py

async def test_default_theme():
    """Test default theme rendering"""
    app = MiniDataHubApp(theme="default")

    async with app.run_test() as pilot:
        # Take snapshot
        snapshot = pilot.screenshot()
        # Compare with baseline
        assert_snapshot_matches(snapshot, "default_theme.txt")

async def test_light_theme():
    """Test light theme rendering"""
    app = MiniDataHubApp(theme="light")

    async with app.run_test() as pilot:
        snapshot = pilot.screenshot()
        assert_snapshot_matches(snapshot, "light_theme.txt")
```

---

### Color Contrast Testing

```python
def test_color_contrast():
    """Ensure sufficient color contrast"""
    from wcag_contrast_ratio import passes_AAA

    # Test primary text on primary background
    assert passes_AAA("#E0E0E0", "#1E1E1E")  # Light on dark

    # Test error text
    assert passes_AAA("#EF4444", "#1E1E1E")  # Error on dark
```

---

## Related Documentation

- **[UI Architecture](architecture.md)** - UI design overview
- **[Widgets & Components](widgets.md)** - Custom widgets
- **[Configuration Files](../config/files.md)** - Theme config

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
