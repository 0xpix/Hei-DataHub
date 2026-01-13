"""
Contextual footer that shows different shortcuts based on current focus/state.
"""
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class ContextualFooter(Widget):
    """A footer that shows context-sensitive shortcuts."""

    DEFAULT_CSS = """
    ContextualFooter {
        dock: bottom;
        height: 1;
        background: $surface;
    }

    ContextualFooter .footer-container {
        width: 100%;
        height: 1;
        background: $surface;
        align: center middle;
    }

    ContextualFooter .footer-key {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    ContextualFooter .footer-label {
        color: $text-muted;
        padding: 0 1;
    }

    ContextualFooter .footer-separator {
        color: $text-disabled;
    }

    ContextualFooter.hidden-footer {
        display: none;
    }
    """

    # Current context: "home", "results", "details", etc.
    context = reactive("home")

    # Shortcut definitions for each context
    SHORTCUTS = {
        "home": [],  # No shortcuts on home screen
        "search": [],  # No shortcuts while typing in search
        "results": [
            ("j/k", "Navigate"),
            ("gg", "Top"),
            ("G", "Bottom"),
            ("Enter", "Open"),
            ("Esc", "Back"),
        ],
        "details": [
            ("d", "Delete"),
            ("e", "Edit"),
            ("Esc", "Back"),
        ],
        "edit": [
            ("Ctrl+S", "Save"),
            ("Esc", "Cancel"),
        ],
        "add": [
            ("Ctrl+S", "Save"),
            ("Esc", "Cancel"),
        ],
    }

    def compose(self) -> ComposeResult:
        yield Horizontal(id="footer-content", classes="footer-container")

    def on_mount(self) -> None:
        """Initial render."""
        self._update_shortcuts()

    def watch_context(self, new_context: str) -> None:
        """React to context changes."""
        # Only update if widget is mounted
        if self.is_mounted:
            self._update_shortcuts()

    def _update_shortcuts(self) -> None:
        """Update the footer with shortcuts for current context."""
        try:
            container = self.query_one("#footer-content", Horizontal)
        except Exception:
            return  # Not mounted yet

        container.remove_children()

        shortcuts = self.SHORTCUTS.get(self.context, [])

        # Hide footer if no shortcuts
        if not shortcuts:
            self.add_class("hidden-footer")
            return
        else:
            self.remove_class("hidden-footer")

        for i, (key, label) in enumerate(shortcuts):
            if i > 0:
                container.mount(Static(" │ ", classes="footer-separator"))
            container.mount(Static(f" {key} ", classes="footer-key"))
            container.mount(Static(label, classes="footer-label"))

    def set_context(self, context: str) -> None:
        """Set the current context."""
        self.context = context
