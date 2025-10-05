"""
Command Palette widget for quick action access.
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Input, ListItem, ListView, Static, Label
from textual.screen import ModalScreen
from textual import on
import logging

from mini_datahub.services.actions import get_action_registry, Action, ActionContext

logger = logging.getLogger(__name__)


class CommandPaletteItem(ListItem):
    """A single item in the command palette."""

    def __init__(self, action: Action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = action

    def compose(self) -> ComposeResult:
        """Compose the item layout."""
        with Container(classes="palette-item"):
            yield Label(self.action.label, classes="palette-item-label")
            yield Label(self.action.description, classes="palette-item-description")
            if self.action.default_keys:
                keys_str = " / ".join(self.action.default_keys[:2])  # Show max 2 keys
                yield Label(keys_str, classes="palette-item-keys")


class CommandPalette(ModalScreen):
    """
    Command palette modal for quick action access.

    Triggered by Ctrl+P, shows fuzzy-searchable list of all actions.
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("ctrl+p", "dismiss", "Close"),
    ]

    DEFAULT_CSS = """
    CommandPalette {
        align: center middle;
    }

    #palette-container {
        width: 80%;
        max-width: 100;
        height: auto;
        max-height: 30;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #palette-input {
        margin-bottom: 1;
        width: 100%;
    }

    #palette-list {
        height: 20;
        border: solid $accent;
    }

    .palette-item {
        layout: horizontal;
        height: auto;
        padding: 0 1;
    }

    .palette-item-label {
        width: 30%;
        color: $primary;
    }

    .palette-item-description {
        width: 50%;
        color: $text;
    }

    .palette-item-keys {
        width: 20%;
        color: $accent;
        text-align: right;
    }

    #palette-help {
        margin-top: 1;
        color: $text-muted;
        text-align: center;
    }
    """

    def __init__(self, context: ActionContext = ActionContext.GLOBAL):
        """
        Initialize command palette.

        Args:
            context: Current context for filtering actions
        """
        super().__init__()
        self.context = context
        self.registry = get_action_registry()
        self.all_actions = self.registry.get_for_context(context)

    def compose(self) -> ComposeResult:
        """Compose the command palette layout."""
        with Container(id="palette-container"):
            yield Static("Command Palette", id="palette-title")
            yield Input(placeholder="Type to search actions...", id="palette-input")
            yield ListView(id="palette-list")
            yield Static(
                "↑↓ navigate • Enter select • Esc close",
                id="palette-help"
            )

    def on_mount(self) -> None:
        """Set up the palette when mounted."""
        # Focus the search input
        self.query_one("#palette-input", Input).focus()

        # Show recent actions initially
        self._show_recent()

    def _show_recent(self) -> None:
        """Show recently used actions."""
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()

        recent = self.registry.get_recent(limit=10)
        if recent:
            for action in recent:
                item = CommandPaletteItem(action)
                list_view.append(item)
        else:
            # Show all actions if no recent
            self._show_all()

    def _show_all(self) -> None:
        """Show all available actions."""
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()

        for action in self.all_actions[:20]:  # Limit to 20 for performance
            item = CommandPaletteItem(action)
            list_view.append(item)

    @on(Input.Changed, "#palette-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        query = event.value.strip()

        if not query:
            self._show_recent()
            return

        # Search for matching actions
        matches = self.registry.search(query, context=self.context)

        # Update list view
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()

        for action in matches[:20]:  # Limit to 20 results
            item = CommandPaletteItem(action)
            list_view.append(item)

    @on(ListView.Selected, "#palette-list")
    def on_action_selected(self, event: ListView.Selected) -> None:
        """Handle action selection."""
        if isinstance(event.item, CommandPaletteItem):
            action = event.item.action

            # Track usage
            self.registry.track_recent(action.id)

            # Dismiss and execute action
            self.dismiss(action)

    def action_dismiss(self) -> None:
        """Dismiss the palette without selecting."""
        self.dismiss(None)
