"""
Help screen showing keybindings.
"""
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from hei_datahub.ui.utils.actions import NavActionsMixin


class HelpScreen(NavActionsMixin, Screen):
    """Help screen showing keybindings."""

    CSS_PATH = "../styles/help.tcss"

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Static("""
[bold cyan]Hei-DataHub Keybindings[/bold cyan]

[bold yellow]Home / Search Screen:[/bold yellow]
  [cyan]/[/cyan]           Focus search (Insert mode)
  [cyan]j / k[/cyan]       Move selection down/up
  [cyan]gg[/cyan]          Jump to first dataset
  [cyan]G[/cyan]           Jump to last dataset
  [cyan]o / Enter[/cyan]   Open selected dataset details
  [cyan]A[/cyan]           Add new dataset
  [cyan]S[/cyan]           Settings
  [cyan]Esc[/cyan]         Exit Insert mode / Clear search
  [cyan]q[/cyan]           Quit application
  [cyan]?[/cyan]           Show this help

[bold yellow]Details Screen:[/bold yellow]
  [cyan]y[/cyan]           Copy source to clipboard
  [cyan]o[/cyan]           Open source URL in browser
  [cyan]q / Esc[/cyan]     Back to search

[bold yellow]Add Data Form:[/bold yellow]
  [cyan]j / k[/cyan]       Move focus down/up
  [cyan]Ctrl+d/u[/cyan]    Scroll half-page down/up
  [cyan]gg[/cyan]          Jump to first field
  [cyan]G[/cyan]           Jump to last field
  [cyan]Tab[/cyan]         Next field
  [cyan]Shift+Tab[/cyan]   Previous field
  [cyan]Ctrl+s[/cyan]      Save dataset
  [cyan]q / Esc[/cyan]     Cancel and return

[bold green]Modes:[/bold green]
  [yellow]Normal[/yellow]  - Navigation mode (default)
  [yellow]Insert[/yellow]  - Editing mode (in search/forms)

Press [cyan]Esc[/cyan] or [cyan]q[/cyan] to close this help.
            """, id="help-content"),
            id="help-scroll",
        )

    # Use action_back from NavActionsMixin, but keep dismiss binding working
    def action_dismiss(self) -> None:
        """Close help screen (calls action_back from mixin)."""
        self.action_back()
