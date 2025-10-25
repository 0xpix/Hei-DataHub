# Keyboard Shortcuts & Events

**Learning Goal**: Master keyboard input handling and event-driven programming in Textual.

*(This page is under construction. Check back soon!)*

## Preview

This tutorial will cover:
- Defining keybindings with `Binding`
- Creating action methods (`action_*`)
- Handling widget events (`on_*`)
- Multi-key sequences (like `gg` for "go to top")
- Custom event classes
- Debouncing and throttling input

## Key Files to Study

- `src/mini_datahub/ui/views/home.py` — Lines 48-79 (keybindings)
- `src/mini_datahub/ui/keybindings.py` — Keybinding configuration
- `src/mini_datahub/services/config.py` — Loading keybindings from TOML

## Quick Example

```python
class HomeScreen(Screen):
    BINDINGS = [
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
        Binding("/", "focus_search", "Search"),
    ]

    def action_move_down(self):
        table = self.query_one(DataTable)
        table.action_cursor_down()

    def on_input_changed(self, event: Input.Changed):
        self.perform_search(event.value)
```

**Next:** [Adding Your Own UI Screen](05-custom-view.md)
