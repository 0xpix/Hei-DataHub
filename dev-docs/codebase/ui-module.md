# UI Module

## Overview

The **UI Module** provides the Terminal User Interface (TUI) built with [Textual](https://textual.textualize.io/). It includes full-screen views, reusable widgets, keybindings, themes, and styling.

---

## Architecture

**Layer Position:**

```
UI Layer ← YOU ARE HERE
     ↓
Services Layer
     ↓
Core + Infrastructure
```

**Framework:** [Textual](https://textual.textualize.io/) - Modern Python TUI framework

**Dependencies:**
- ✅ Can import from `services` and `core`
- ❌ Should not import from `infra` directly (use services)
- ✅ Handles all user interaction and display

---

## Directory Structure

```
ui/
├── __init__.py
├── app.py                    # Main TUI application
├── theme.py                  # Color themes
├── keybindings.py            # Global keybindings
│
├── views/                    # Full-screen views
│   ├── home.py               # Home dashboard
│   ├── cloud_files.py        # Cloud file browser
│   ├── settings.py           # Settings editor
│   ├── settings_menu.py      # Settings navigation
│   ├── user_config.py        # User config editor
│   └── outbox.py             # Failed upload queue
│
├── widgets/                  # Reusable components
│   ├── autocomplete.py       # Search autocomplete
│   ├── command_palette.py    # Quick commands (Ctrl+P)
│   ├── console.py            # Debug console
│   └── help_overlay.py       # Help screen (F1)
│
├── styles/                   # Textual CSS files
│   ├── app.tcss              # Global app styles
│   ├── home.tcss             # Home view styles
│   └── widgets.tcss          # Widget styles
│
└── assets/                   # Images, icons (ASCII art)
    └── logo.txt              # ASCII logo
```

---

## Core Concepts

### Textual Framework Basics

#### App → Screen → Widget Hierarchy

```
App (mini_datahub.ui.app.DataHubApp)
 ├── HomeView (Screen)
 │   ├── Header (Widget)
 │   ├── SearchBar (Widget)
 │   ├── ResultList (Widget)
 │   └── Footer (Widget)
 │
 ├── CloudFilesView (Screen)
 │   ├── FileTree (Widget)
 │   └── FileDetails (Widget)
 │
 └── SettingsView (Screen)
     └── SettingsForm (Widget)
```

#### Widget Lifecycle

```python
class MyWidget(Widget):
    def on_mount(self) -> None:
        """Called when widget is added to the DOM"""
        self.border_title = "My Widget"

    def on_resize(self, event) -> None:
        """Called when widget is resized"""
        pass

    def on_unmount(self) -> None:
        """Called when widget is removed"""
        pass
```

#### Reactive Properties

```python
from textual.reactive import reactive

class SearchBar(Input):
    """Search input with reactive query"""

    query = reactive("")  # Reactive property

    def watch_query(self, new_value: str) -> None:
        """Called when query changes"""
        self.post_message(SearchChanged(new_value))
```

---

## Views (Screens)

### `home.py` - Home Dashboard

**Purpose:** Main landing screen with search interface

**Layout:**

```
┌─────────────────────────────────────────────────┐
│ Hei-DataHub v0.59.0                             │
├─────────────────────────────────────────────────┤
│ Search: [climate data                    ] 🔍   │
├─────────────────────────────────────────────────┤
│ Results:                                        │
│  ☐ climate-model-data                           │
│  ☐ climate-observations-2024                    │
│  ☐ historical-climate-records                   │
├─────────────────────────────────────────────────┤
│ F1: Help | Ctrl+P: Commands | Ctrl+Q: Quit     │
└─────────────────────────────────────────────────┘
```

**Key Components:**

```python
class HomeView(Screen):
    """Home dashboard with search"""

    def compose(self) -> ComposeResult:
        """Build widget tree"""
        yield Header()
        yield SearchBar(id="search-bar")
        yield ResultList(id="results")
        yield Footer()

    def on_search_changed(self, event: SearchChanged) -> None:
        """Handle search query changes"""
        results = search_indexed(event.query)
        self.query_one("#results").update(results)
```

**Keybindings:**

| Key | Action |
|-----|--------|
| `/` | Focus search bar |
| `↓` `↑` | Navigate results |
| `Enter` | Open selected dataset |
| `Ctrl+N` | New dataset |
| `Ctrl+R` | Refresh |

---

### `cloud_files.py` - Cloud File Browser

**Purpose:** Browse and manage files on WebDAV storage

**Layout:**

```
┌─────────────────────────────────────────────────┐
│ Cloud Files (HeiBox)                            │
├─────────────────────────────────────────────────┤
│ 📁 datasets/                                    │
│   📁 climate-data/                              │
│     📄 metadata.yaml                  2.1 KB    │
│   📁 ocean-temp/                                │
│     📄 metadata.yaml                  1.8 KB    │
│   📁 research-notes/                            │
│     📄 metadata.yaml                  3.2 KB    │
├─────────────────────────────────────────────────┤
│ ↑↓: Navigate | Enter: View | D: Download       │
└─────────────────────────────────────────────────┘
```

**Key Features:**

- List remote files (WebDAV PROPFIND)
- Show file sizes and modification times
- Download files to local cache
- Upload local files to cloud
- Delete remote files

**Implementation:**

```python
class CloudFilesView(Screen):
    """Browse WebDAV cloud files"""

    def on_mount(self) -> None:
        """Load remote file list on mount"""
        self.load_remote_files()

    async def load_remote_files(self) -> None:
        """Async file listing"""
        files = await self.run_in_thread(list_remote_files)
        self.query_one("#file-tree").update(files)

    def on_tree_item_selected(self, event) -> None:
        """Handle file selection"""
        file_path = event.item.data
        self.show_file_details(file_path)
```

---

### `settings.py` - Settings Editor

**Purpose:** Edit application configuration

**Layout:**

```
┌─────────────────────────────────────────────────┐
│ Settings                                        │
├─────────────────────────────────────────────────┤
│ ┌─ WebDAV Configuration ────────────────────┐  │
│ │ URL: [https://heibox.uni-heidelberg.de  ]│  │
│ │ Library: [research-datasets             ]│  │
│ │ Auth Method: [Token ▼]                   │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ ┌─ Sync Settings ──────────────────────────┐  │
│ │ ☑ Enable background sync                 │  │
│ │ Interval: [5] minutes                    │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ ┌─ Search Settings ────────────────────────┐  │
│ │ Debounce: [300] ms                       │  │
│ │ Max results: [50]                        │  │
│ └───────────────────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│ Ctrl+S: Save | Esc: Cancel                     │
└─────────────────────────────────────────────────┘
```

**Key Features:**

- Load settings from `config.toml`
- Validate input (e.g., URL format, positive integers)
- Save settings on Ctrl+S
- Discard changes on Esc

**Implementation:**

```python
class SettingsView(Screen):
    """Settings editor"""

    def on_mount(self) -> None:
        """Load current settings"""
        config = load_config()
        self.populate_form(config)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle save/cancel buttons"""
        if event.button.id == "save":
            self.save_settings()
        elif event.button.id == "cancel":
            self.app.pop_screen()

    def save_settings(self) -> None:
        """Validate and save settings"""
        config = self.collect_form_data()
        try:
            validate_config(config)
            save_config(config)
            self.notify("Settings saved!")
        except ValidationError as e:
            self.notify(str(e), severity="error")
```

---

### `outbox.py` - Failed Upload Queue

**Purpose:** View and retry failed uploads

**Layout:**

```
┌─────────────────────────────────────────────────┐
│ Outbox (2 pending uploads)                      │
├─────────────────────────────────────────────────┤
│ ☐ climate-data          Failed: Network timeout │
│   Attempts: 3/5        Last: 2024-10-25 14:32   │
│                                                  │
│ ☐ ocean-temp           Failed: Auth error       │
│   Attempts: 1/5        Last: 2024-10-25 14:15   │
├─────────────────────────────────────────────────┤
│ Enter: Retry | D: Delete | Ctrl+R: Retry All   │
└─────────────────────────────────────────────────┘
```

**Key Features:**

- List failed uploads with error details
- Retry individual uploads
- Retry all with exponential backoff
- Delete failed items (give up)

---

## Widgets

### `autocomplete.py` - Search Autocomplete

**Purpose:** Dropdown suggestions as user types

**Visual:**

```
Search: [clim▌              ]
         ┌────────────────────┐
         │ climate-data       │ ← Selected
         │ climate-models     │
         │ climate-study      │
         └────────────────────┘
```

**Implementation:**

```python
class AutocompleteWidget(Widget):
    """Autocomplete dropdown for search"""

    suggestions = reactive([])  # Reactive list
    selected_index = reactive(0)

    def watch_suggestions(self, new_suggestions: list[str]) -> None:
        """Update dropdown when suggestions change"""
        self.update_dropdown(new_suggestions)

    def on_key(self, event: Key) -> None:
        """Handle arrow keys for navigation"""
        if event.key == "down":
            self.selected_index = min(
                self.selected_index + 1,
                len(self.suggestions) - 1
            )
        elif event.key == "up":
            self.selected_index = max(self.selected_index - 1, 0)
        elif event.key == "enter":
            self.select_suggestion(self.suggestions[self.selected_index])
```

**Debouncing:**

```python
def on_input_changed(self, event: Input.Changed) -> None:
    """Debounce input to avoid excessive queries"""
    if hasattr(self, "_debounce_timer"):
        self._debounce_timer.cancel()

    self._debounce_timer = self.set_timer(
        0.3,  # 300ms debounce
        lambda: self.fetch_suggestions(event.value)
    )
```

---

### `command_palette.py` - Quick Commands (Ctrl+P)

**Purpose:** VSCode-style command palette for quick actions

**Visual:**

```
┌─────────────────────────────────────────────────┐
│ Commands                                        │
├─────────────────────────────────────────────────┤
│ > new▌                                          │
├─────────────────────────────────────────────────┤
│ ► New Dataset                         Ctrl+N    │
│   New Project                                   │
│   New Tag                                       │
│   Sync Now                            Ctrl+S    │
│   Open Settings                       Ctrl+,    │
│   Toggle Dark Mode                    Ctrl+D    │
└─────────────────────────────────────────────────┘
```

**Commands:**

```python
COMMANDS = [
    Command("New Dataset", "new_dataset", "Ctrl+N"),
    Command("Sync Now", "sync_now", "Ctrl+S"),
    Command("Open Settings", "open_settings", "Ctrl+,"),
    Command("Toggle Theme", "toggle_theme", "Ctrl+D"),
    Command("Show Help", "show_help", "F1"),
]
```

**Fuzzy Matching:**

```python
def filter_commands(query: str) -> list[Command]:
    """Filter commands by fuzzy matching"""
    return [
        cmd for cmd in COMMANDS
        if fuzzy_match(query.lower(), cmd.name.lower())
    ]

def fuzzy_match(query: str, text: str) -> bool:
    """Simple fuzzy matching"""
    query_chars = list(query)
    for char in query_chars:
        if char not in text:
            return False
        text = text[text.index(char) + 1:]  # Consume char
    return True
```

---

### `help_overlay.py` - Help Screen (F1)

**Purpose:** Show keybindings and quick help

**Visual:**

```
┌─────────────────────────────────────────────────┐
│ Help                                            │
├─────────────────────────────────────────────────┤
│ Global Keybindings:                             │
│   F1              Show this help screen         │
│   Ctrl+P          Open command palette          │
│   Ctrl+Q          Quit application              │
│   Ctrl+,          Open settings                 │
│                                                 │
│ Search View:                                    │
│   /               Focus search bar              │
│   ↓ / ↑           Navigate results              │
│   Enter           Open selected dataset         │
│   Ctrl+N          Create new dataset            │
│                                                 │
│ Press Esc to close this help screen             │
└─────────────────────────────────────────────────┘
```

---

### `console.py` - Debug Console

**Purpose:** Developer console for debugging (hidden by default)

**Toggle:** `Ctrl+Shift+C`

**Visual:**

```
┌─────────────────────────────────────────────────┐
│ Debug Console                                   │
├─────────────────────────────────────────────────┤
│ >>> search_indexed("climate")                   │
│ [{'id': 'climate-data', 'name': 'Climate Data'}]│
│ >>> get_config()                                │
│ {'webdav': {...}, 'sync': {...}}                │
│ >>>▌                                            │
└─────────────────────────────────────────────────┘
```

**Features:**

- Execute Python code in app context
- Inspect app state
- Test services directly
- View logs

---

## Theming & Styling

### `theme.py` - Color Themes

**Built-in Themes:**

```python
THEMES = {
    "dark": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "primary": "#569cd6",
        "secondary": "#4ec9b0",
        "accent": "#ce9178",
        "error": "#f48771",
        "success": "#b5cea8",
    },
    "light": {
        "background": "#ffffff",
        "foreground": "#000000",
        "primary": "#0066cc",
        "secondary": "#00aa88",
        "accent": "#ff6600",
        "error": "#cc0000",
        "success": "#00aa00",
    },
}
```

**Switching Themes:**

```python
def apply_theme(theme_name: str) -> None:
    """Apply color theme to app"""
    theme = THEMES[theme_name]
    for key, color in theme.items():
        app.set_css_variable(f"--{key}", color)
```

---

### Textual CSS (`.tcss`)

**Example: `styles/app.tcss`**

```tcss
/* Global app styles */
Screen {
    background: $background;
    color: $foreground;
}

Header {
    background: $primary;
    color: white;
    dock: top;
    height: 3;
}

Footer {
    background: $secondary;
    color: white;
    dock: bottom;
    height: 1;
}

Input {
    border: solid $primary;
    background: $background;
}

Button {
    background: $primary;
    color: white;
    border: none;
}

Button:hover {
    background: $accent;
}
```

---

## Keybindings

### Global Keybindings (`keybindings.py`)

```python
GLOBAL_KEYBINDINGS = {
    "f1": "show_help",
    "ctrl+p": "command_palette",
    "ctrl+q": "quit",
    "ctrl+,": "open_settings",
    "ctrl+s": "sync_now",
    "ctrl+d": "toggle_theme",
}
```

### View-Specific Keybindings

```python
class HomeView(Screen):
    BINDINGS = [
        ("slash", "focus_search", "Search"),
        ("ctrl+n", "new_dataset", "New"),
        ("ctrl+r", "refresh", "Refresh"),
        ("down", "next_result", "Next"),
        ("up", "prev_result", "Previous"),
    ]
```

---

## Related Documentation

- **[CLI Module](cli-module.md)** - Command-line interface
- **[Services Module](services-module.md)** - Business logic
- **[UI/TUI Documentation](../ui-tui/overview.md)** - Detailed UI guide

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
