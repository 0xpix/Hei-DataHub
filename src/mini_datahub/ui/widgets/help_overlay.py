"""
Help overlay widget for displaying keybindings and shortcuts.
"""
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Label
from textual.screen import ModalScreen
from typing import Dict, List

from mini_datahub.services.actions import get_action_registry, ActionContext


class HelpOverlay(ModalScreen):
    """
    Modal overlay displaying current keybindings and help.
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("?", "dismiss", "Close"),
    ]

    DEFAULT_CSS = """
    HelpOverlay {
        align: center middle;
    }

    #help-container {
        width: 90%;
        max-width: 120;
        height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #help-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #help-content {
        height: 100%;
        border: solid $accent;
        padding: 1;
    }

    .help-section {
        margin-bottom: 1;
    }

    .help-section-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }

    .help-binding {
        layout: horizontal;
        height: auto;
        padding: 0 1;
    }

    .help-keys {
        width: 30%;
        color: $primary;
    }

    .help-action {
        width: 70%;
        color: $text;
    }

    #help-footer {
        margin-top: 1;
        text-align: center;
        color: $text-muted;
    }
    """

    def __init__(self, context: ActionContext = ActionContext.GLOBAL):
        """
        Initialize help overlay.

        Args:
            context: Current context for filtering keybindings
        """
        super().__init__()
        self.context = context
        self.registry = get_action_registry()

    def compose(self) -> ComposeResult:
        """Compose the help overlay layout."""
        with Container(id="help-container"):
            yield Static("⌨️  Keybindings & Shortcuts", id="help-title")
            with VerticalScroll(id="help-content"):
                yield from self._build_help_sections()
            yield Static(
                "Press ? or Esc to close",
                id="help-footer"
            )

    def _build_help_sections(self) -> ComposeResult:
        """Build help sections for different action contexts."""
        # Group actions by context
        context_actions: Dict[str, List] = {
            "Global": [],
            "Navigation": [],
            "Search & Filter": [],
            "Dataset Management": [],
            "Editing": [],
            "Query Syntax": [],  # Special section for search syntax
        }

        # Get all actions for current and global context
        actions = self.registry.get_for_context(self.context)

        # Categorize actions
        for action in actions:
            if not action.default_keys:
                continue

            # Categorize based on action ID or context
            if action.id in ("quit", "help", "command_palette", "settings", "home"):
                context_actions["Global"].append(action)
            elif action.id in ("nav_up", "nav_down", "nav_top", "nav_bottom"):
                context_actions["Navigation"].append(action)
            elif action.id in ("search", "clear_search"):
                context_actions["Search & Filter"].append(action)
            elif action.id in ("add_dataset", "view_details", "delete_dataset", "reindex", "refresh", "sync_pull"):
                context_actions["Dataset Management"].append(action)
            elif action.id in ("edit_dataset", "save", "cancel", "undo", "redo", "copy_source", "open_url"):
                context_actions["Editing"].append(action)

        # Render each section
        for section_name, section_actions in context_actions.items():
            # Special handling for Query Syntax section
            if section_name == "Query Syntax" and self.context in (ActionContext.HOME, ActionContext.GLOBAL):
                with Container(classes="help-section"):
                    yield Static(f"═══ {section_name} ═══", classes="help-section-title")

                    # Query syntax examples
                    examples = [
                        ("source:github", "Filter by source field"),
                        ("format:csv", "Filter by file format"),
                        ("size:>1000", "Size greater than (>, <, >=, <=)"),
                        ("date:>2024-01", "Date comparison"),
                        ('"exact phrase"', "Search for exact phrase"),
                        ("source:usgs water", "Combine filters with free text"),
                    ]

                    for query, description in examples:
                        with Container(classes="help-binding"):
                            yield Label(query, classes="help-keys")
                            yield Label(description, classes="help-action")
                continue

            if not section_actions:
                continue

            with Container(classes="help-section"):
                yield Static(f"═══ {section_name} ═══", classes="help-section-title")

                for action in section_actions:
                    keys_str = " / ".join(action.default_keys[:3])  # Show max 3 keys
                    with Container(classes="help-binding"):
                        yield Label(keys_str, classes="help-keys")
                        yield Label(action.description, classes="help-action")

    def action_dismiss(self) -> None:
        """Dismiss the help overlay."""
        self.dismiss()
