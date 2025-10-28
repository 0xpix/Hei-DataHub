# Keyboard Shortcuts & Events

**Learning Goal**: Master keyboard input handling and event-driven programming in Textual.

By the end of this page, you'll:
- Define keybindings with `Binding` objects
- Create action methods (`action_*`)
- Handle widget events (`on_*`)
- Implement multi-key sequences (like `gg`)
- Debounce and throttle input
- Load keybindings from configuration files

---

## Why Keyboard Shortcuts Matter

TUI apps are **keyboard-driven**. Unlike GUIs where users click buttons, TUI users press keys:

- ✅ **Fast** — No mouse movement needed
- ✅ **Efficient** — Power users love keyboard workflows
- ✅ **Accessible** — Works over SSH, on remote servers
- ✅ **Familiar** — Like Vim, Emacs, or tmux

---

## The Two Types of Input Handling

### 1. **Keybindings** (Global Shortcuts)

Defined in the `BINDINGS` class attribute:

```python
class HomeScreen(Screen):
    BINDINGS = [
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
        Binding("/", "focus_search", "Search"),
    ]
```

- Triggers: `action_move_down()`, `action_move_up()`, `action_focus_search()`
- Works anywhere on the screen
- Shown in footer

---

### 2. **Widget Events** (Focused Input)

Handled with `on_*` methods:

```python
def on_input_changed(self, event: Input.Changed):
    """Called when Input widget text changes."""
    self.perform_search(event.value)

def on_data_table_row_selected(self, event: DataTable.RowSelected):
    """Called when user selects a table row."""
    dataset_id = event.row_key.value
    self.view_details(dataset_id)
```

- Triggers: When widget state changes
- Only fires when widget is focused
- Event-driven architecture

---

## Defining Keybindings

### Basic Syntax

```python
from textual.binding import Binding

class MyScreen(Screen):
    BINDINGS = [
        Binding(
            key="a",              # Key to press
            action="add_dataset", # Action name (calls action_add_dataset)
            description="Add",    # Text shown in footer
            key_display="a",      # How to display the key
            show=True             # Show in footer?
        ),
    ]
```

---

### Simple Keybinding

```python
Binding("j", "move_down", "Down")
```

**What happens:**
1. User presses `j`
2. Textual calls `self.action_move_down()`
3. Footer shows: `[j] Down`

---

### Hidden Keybinding

```python
Binding("enter", "open_details", "Open", show=False)
```

**What happens:**
1. User presses `Enter`
2. Textual calls `self.action_open_details()`
3. **Not shown in footer** (show=False)

---

### Multiple Keys, Same Action

```python
BINDINGS = [
    Binding("j", "move_down", "Down"),
    Binding("down", "move_down", "", show=False),  # Arrow key also works
]
```

Both `j` and `↓` trigger `action_move_down()`.

---

## Action Methods

**Convention:** Action methods start with `action_` prefix.

### Example: Move Down

```python
class HomeScreen(Screen):
    BINDINGS = [
        Binding("j", "move_down", "Down"),
    ]

    def action_move_down(self):
        """Move cursor down in table."""
        table = self.query_one(DataTable)
        table.action_cursor_down()  # Call table's built-in action
```

**Flow:**
1. User presses `j`
2. Textual looks for `action_move_down()`
3. Method executes
4. Table cursor moves down

---

### Example: Focus Search

```python
BINDINGS = [
    Binding("/", "focus_search", "Search"),
]

def action_focus_search(self):
    """Focus the search input field."""
    search_input = self.query_one("#search-input", Input)
    search_input.focus()
```

**Flow:**
1. User presses `/`
2. `action_focus_search()` executes
3. Search input gets focus
4. User can start typing

---

### Example: Quit

```python
BINDINGS = [
    Binding("q", "quit", "Quit", key_display="^q"),
]

def action_quit(self):
    """Exit the application."""
    self.app.exit()
```

---

## Multi-Key Sequences

**Goal:** Press `g` twice quickly to jump to top (like Vim's `gg`).

### Implementation

```python
from textual.reactive import reactive

class HomeScreen(Screen):
    _last_key = reactive("")  # Track last key pressed
    _last_key_time = 0

    BINDINGS = [
        Binding("g", "handle_g", "", show=False),
        Binding("G", "jump_bottom", "Bottom"),
    ]

    def action_handle_g(self):
        """Handle 'g' key - check for 'gg' sequence."""
        import time

        current_time = time.time()

        # If 'g' was pressed recently (within 500ms), it's 'gg'
        if self._last_key == "g" and (current_time - self._last_key_time) < 0.5:
            self.action_jump_top()
            self._last_key = ""  # Reset
        else:
            # First 'g' press - wait for second
            self._last_key = "g"
            self._last_key_time = current_time

    def action_jump_top(self):
        """Jump to top of table."""
        table = self.query_one(DataTable)
        table.cursor_coordinate = (0, 0)  # Move to first row

    def action_jump_bottom(self):
        """Jump to bottom of table."""
        table = self.query_one(DataTable)
        table.cursor_coordinate = (table.row_count - 1, 0)
```

**How it works:**
1. User presses `g` → `action_handle_g()` fires
2. Method records: "g pressed at time T"
3. User presses `g` again within 500ms
4. Method detects: "gg sequence!" → calls `action_jump_top()`
5. Cursor jumps to top

**In Hei-DataHub:** See `home.py` lines 48-79 for real implementation.

---

## Widget Events

### Common Events

```python
def on_input_changed(self, event: Input.Changed):
    """Input widget text changed."""
    pass

def on_input_submitted(self, event: Input.Submitted):
    """User pressed Enter in input."""
    pass

def on_button_pressed(self, event: Button.Pressed):
    """Button was clicked."""
    pass

def on_data_table_row_selected(self, event: DataTable.RowSelected):
    """Table row selected (Enter pressed)."""
    pass

def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
    """Table cursor moved to a row."""
    pass
```

---

### Example: Search on Input Change

```python
def on_input_changed(self, event: Input.Changed):
    """
    Called every time the search input text changes.

    Args:
        event: Contains event.value (current text)
    """
    query = event.value
    self.perform_search(query)
```

**Flow:**
1. User types "climate" → 8 events fire (one per character)
2. Each event calls `on_input_changed()`
3. Search runs 8 times

**Problem:** Too many searches!

**Solution:** Debouncing (see next section).

---

## Debouncing Input

**Problem:** Searching on every keystroke is wasteful.

**Solution:** Wait until user stops typing.

### Simple Debounce

```python
from textual.timer import Timer

class HomeScreen(Screen):
    _debounce_timer: Optional[Timer] = None

    def on_input_changed(self, event: Input.Changed):
        """Debounced search - wait 300ms after typing stops."""
        # Cancel previous timer
        if self._debounce_timer:
            self._debounce_timer.stop()

        # Set new timer
        self._debounce_timer = self.set_timer(
            0.3,  # 300ms delay
            lambda: self.perform_search(event.value)
        )

    def perform_search(self, query: str):
        """Actually execute the search."""
        # ... search logic
```

**How it works:**
1. User types `c` → timer starts (300ms)
2. User types `l` → cancel old timer, start new (300ms)
3. User types `i` → cancel old timer, start new (300ms)
4. User types `m` → cancel old timer, start new (300ms)
5. User types `a` → cancel old timer, start new (300ms)
6. User types `t` → cancel old timer, start new (300ms)
7. User types `e` → cancel old timer, start new (300ms)
8. **User stops typing**
9. Timer expires after 300ms
10. Search executes **once** with "climate"

**Result:** 1 search instead of 7!

---

### Hei-DataHub Implementation

**File:** `src/hei_datahub/ui/views/home.py` (Lines 380-410)

```python
def on_input_changed(self, event: Input.Changed):
    """Debounced search with configurable delay."""
    if self._debounce_timer:
        self._debounce_timer.stop()

    # Get debounce delay from environment (default: 200ms)
    import os
    debounce_ms = int(os.environ.get("HEI_DATAHUB_SEARCH_DEBOUNCE_MS", "200"))

    # Set new timer
    self._debounce_timer = self.set_timer(
        debounce_ms / 1000.0,
        lambda: self.perform_search(event.value)
    )
```

**Configurable:** Set `HEI_DATAHUB_SEARCH_DEBOUNCE_MS=500` for slower delay.

---

## Loading Keybindings from Config

Hei-DataHub loads keybindings from `config.toml`:

**File:** `~/.config/hei-datahub/config.toml`

```toml
[keybindings]
quit = ["q", "ctrl+q"]
search = ["/", "ctrl+f"]
add_dataset = ["a", "ctrl+n"]
move_down = ["j", "down"]
move_up = ["k", "up"]
```

### How It Works

**Step 1: Define Action Map**

**File:** `src/hei_datahub/ui/keybindings.py`

```python
def get_action_display_map_home() -> Dict[str, tuple]:
    """
    Map action names to display info.

    Returns:
        Dict[action_name] = (display_name, key_display, show_in_footer)
    """
    return {
        "add_dataset": ("Add Dataset", "a", True),
        "quit": ("Quit", "q", True),
        "move_down": ("Down", "j", False),
        "focus_search": ("Search", "/", True),
    }
```

---

**Step 2: Load Config**

```python
from hei_datahub.services.config import get_config

config = get_config()
keybindings = config.get_keybindings()  # Loads from TOML
```

**Result:**
```python
{
    "quit": ["q", "ctrl+q"],
    "search": ["/", "ctrl+f"],
    # ...
}
```

---

**Step 3: Build Bindings**

```python
from hei_datahub.ui.keybindings import bind_actions_from_config

action_map = get_action_display_map_home()
bindings = bind_actions_from_config(action_map, keybindings)
```

**Result:**
```python
[
    Binding("q", "quit", "Quit", key_display="q", show=True),
    Binding("ctrl+q", "quit", "", show=False),  # Second binding hidden
    Binding("/", "focus_search", "Search", key_display="/", show=True),
    Binding("ctrl+f", "focus_search", "", show=False),
]
```

---

**Step 4: Use in Screen**

```python
def _build_bindings_from_config() -> list[Binding]:
    """Build keybindings list from config file."""
    try:
        from hei_datahub.ui.keybindings import (
            bind_actions_from_config,
            get_action_display_map_home
        )
        from hei_datahub.services.config import get_config

        config = get_config()
        keybindings = config.get_keybindings()
        action_map = get_action_display_map_home()

        return bind_actions_from_config(action_map, keybindings)
    except Exception as e:
        logger.warning(f"Failed to load keybindings: {e}")
        return []  # Fallback to defaults

class HomeScreen(Screen):
    BINDINGS = _build_bindings_from_config()
```

**Now users can customize keybindings in `config.toml`!**

---

## Modifier Keys

### Available Modifiers

```python
Binding("ctrl+s", "save", "Save")        # Ctrl+S
Binding("shift+j", "fast_down", "Fast")  # Shift+J
Binding("alt+enter", "new_window", "")   # Alt+Enter
Binding("ctrl+shift+p", "palette", "")   # Ctrl+Shift+P
```

### Platform Differences

```python
# Ctrl on Linux/Windows, Cmd on macOS
Binding("ctrl+q", "quit", "Quit")
```

Textual handles platform differences automatically!

---

## Event Bubbling

Events **bubble up** from child to parent widgets.

### Example: Stopping Propagation

```python
def on_key(self, event: events.Key):
    """
    Intercept all key presses.

    Args:
        event: Contains event.key (the key pressed)
    """
    if event.key == "escape":
        self.clear_search()
        event.stop()  # Don't let parent widgets handle this

    # Let other keys bubble up
```

---

## Real Example: Home Screen Keybindings

**File:** `src/hei_datahub/ui/views/home.py`

```python
class HomeScreen(Screen):
    BINDINGS = [
        # Navigation
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("gg", "jump_top", "Top", show=False),
        Binding("G", "jump_bottom", "Bottom", show=False),

        # Search
        Binding("/", "focus_search", "Search", key_display="/"),
        Binding("escape", "clear_search", "Clear", show=False),

        # Actions
        Binding("a", "add_dataset", "Add Dataset", key_display="a"),
        Binding("enter", "open_details", "View Details", show=False),
        Binding("u", "pull_updates", "Update", key_display="u"),
        Binding("r", "refresh_data", "Refresh", key_display="r"),

        # App
        Binding("s", "settings", "Settings", key_display="s"),
        Binding("?", "show_help", "Help", key_display="?"),
        Binding("q", "quit", "Quit", key_display="^q"),
    ]

    def action_move_down(self):
        table = self.query_one("#results-table", DataTable)
        table.action_cursor_down()

    def action_move_up(self):
        table = self.query_one("#results-table", DataTable)
        table.action_cursor_up()

    def action_focus_search(self):
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_clear_search(self):
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        self.load_all_datasets()

    def action_open_details(self):
        table = self.query_one("#results-table", DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_key_at(table.cursor_row)
            dataset_id = row_key.value
            # Open details screen
            from hei_datahub.ui.views.details import DatasetDetailsScreen
            self.app.push_screen(DatasetDetailsScreen(dataset_id))

    def action_quit(self):
        self.app.exit()
```

---

## What You've Learned

✅ **Keybindings** trigger `action_*` methods
✅ **Widget events** use `on_*` methods
✅ **Multi-key sequences** track key press timing
✅ **Debouncing** prevents excessive event handling
✅ **Config loading** allows user customization
✅ **Modifier keys** (Ctrl, Shift, Alt) work cross-platform
✅ **Event bubbling** can be stopped with `event.stop()`

---

## Try It Yourself

### Exercise 1: Add a Custom Keybinding

**Goal:** Add `Ctrl+R` as an alternative to `r` for refresh.

**Steps:**

1. Open `~/.config/hei-datahub/config.toml`

2. Find `[keybindings]` section:
```toml
[keybindings]
refresh_data = ["r"]  # ← Change this
```

3. Add `ctrl+r`:
```toml
refresh_data = ["r", "ctrl+r"]
```

4. Restart the app and press `Ctrl+R` — it refreshes!

---

### Exercise 2: Create a Debug Action

**Goal:** Add a `d` key that prints debug info.

**Steps:**

1. Edit `src/hei_datahub/ui/views/home.py`

2. Add to `BINDINGS`:
```python
Binding("d", "debug_info", "Debug", show=False),
```

3. Add action method:
```python
def action_debug_info(self):
    """Print debug information."""
    table = self.query_one("#results-table", DataTable)
    self.app.notify(f"Rows: {table.row_count}, Cursor: {table.cursor_row}")
```

4. Restart and press `d` — shows debug info!

---

### Exercise 3: Implement Debounced Input

**Goal:** Create a debounced counter.

**File:** `test_debounce.py`

```python
from textual.app import App
from textual.widgets import Input, Label
from textual.containers import Vertical

class DebounceApp(App):
    def compose(self):
        yield Vertical(
            Input(placeholder="Type something..."),
            Label("Debounced: ", id="debounced"),
        )

    def on_mount(self):
        self._debounce_timer = None

    def on_input_changed(self, event: Input.Changed):
        if self._debounce_timer:
            self._debounce_timer.stop()

        self._debounce_timer = self.set_timer(
            0.5,  # 500ms
            lambda: self.update_label(event.value)
        )

    def update_label(self, text: str):
        label = self.query_one("#debounced", Label)
        label.update(f"Debounced: {text}")

if __name__ == "__main__":
    DebounceApp().run()
```

**Run it:** Notice the label only updates 500ms after you stop typing!

---

## Next Steps

Now that you understand keyboard input, let's build a **complete custom screen**!

**Next:** [Adding Your Own UI Screen](05-custom-view.md)

---

## Further Reading

- [Textual Bindings Guide](https://textual.textualize.io/guide/actions/)
- [Textual Events Reference](https://textual.textualize.io/events/)
- [Hei-DataHub Keybinding Config](../../ui/keybindings.md)
- [Input Widget Docs](https://textual.textualize.io/widgets/input/)
