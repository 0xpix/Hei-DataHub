"""
Tags help overlay showing available search tags and their descriptions.
"""
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


# Canonical list of supported search tags
SEARCH_TAGS = [
    ("all", "Show all datasets (keyword, no colon)"),
    ("project", "Related projects"),
    ("source", "Source / origin"),
    ("category", "Category"),
    ("method", "Access method"),
    ("format", "Format & structure"),
    ("size", "Dataset size"),
    ("sr", "Spatial resolution"),
    ("sc", "Spatial coverage"),
    ("tr", "Temporal resolution"),
    ("tc", "Temporal coverage"),
]


class TagsHelpScreen(ModalScreen[None]):
    """Modal overlay listing all search tags with descriptions."""

    CSS = """
    TagsHelpScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }

    #tags-help-container {
        width: 52;
        height: auto;
        max-height: 24;
        background: $surface;
        border: wide $accent;
        padding: 1 2;
    }

    #tags-help-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        width: 100%;
        margin-bottom: 1;
    }

    .tag-row {
        width: 100%;
        height: 1;
        color: $text;
    }

    .tag-name {
        text-style: bold;
        color: $warning;
    }

    #tags-help-hint {
        text-align: center;
        color: $text-muted;
        width: 100%;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("f3", "close", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="tags-help-container"):
            yield Static("Search Tags", id="tags-help-title")
            for tag, description in SEARCH_TAGS:
                # Right-pad tag name so descriptions line up
                padded = f"  {tag + ':':<12}{description}"
                yield Static(padded, classes="tag-row")
            yield Static("Usage: tag:value (e.g. format:csv) or 'all'", id="tags-help-hint")

    def action_close(self) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        """Dismiss on any key press."""
        self.dismiss(None)
        event.stop()
