"""
Debug console for developer commands.
Provides a command palette accessible via ':' key.
"""
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, Static

from hei_datahub import GITHUB_REPO, __app_name__, __version__


class DebugConsoleScreen(Screen):
    """Debug console for executing developer commands."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]

    CSS = """
    DebugConsoleScreen {
        align: center middle;
    }

    #console-container {
        width: 80;
        height: auto;
        max-height: 30;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }

    #console-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #command-input {
        margin-top: 1;
        margin-bottom: 1;
    }

    #output-container {
        height: auto;
        max-height: 20;
        overflow-y: auto;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }

    #help-text {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose console UI."""
        with Container(id="console-container"):
            yield Label("Debug Console", id="console-title")
            yield Input(placeholder="Enter command (type 'help' for commands)", id="command-input")
            with Vertical(id="output-container"):
                yield Static("", id="command-output")
            yield Label(
                "Available: reindex | version | logs | help",
                id="help-text"
            )

    def on_mount(self) -> None:
        """Focus input on mount."""
        self.query_one("#command-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission."""
        command = event.value.strip().lower()

        if not command:
            return

        # Clear input
        event.input.value = ""

        # Execute command
        output = self.execute_command(command)

        # Display output
        output_widget = self.query_one("#command-output", Static)
        output_widget.update(output)

    def execute_command(self, command: str) -> str:
        """
        Execute debug command.

        Args:
            command: Command string

        Returns:
            Command output
        """
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "help":
            return self._cmd_help()
        elif cmd == "reindex":
            return self._cmd_reindex()
        elif cmd == "version":
            return self._cmd_version()
        elif cmd == "logs":
            return self._cmd_logs(args)
        elif cmd == "clear":
            return ""
        else:
            return f"[red]Unknown command: {cmd}[/red]\nType 'help' for available commands."

    def _cmd_help(self) -> str:
        """Show help text."""
        return """[bold cyan]Available Commands:[/bold cyan]

[yellow]reindex[/yellow]    - Rebuild search index from catalog
[yellow]version[/yellow]    - Show version and repo info
[yellow]logs[/yellow]       - Show recent log entries
[yellow]clear[/yellow]      - Clear output
[yellow]help[/yellow]       - Show this help

Press [bold]Escape[/bold] or [bold]Ctrl+C[/bold] to close."""

    def _cmd_reindex(self) -> str:
        """Reindex database."""
        try:
            from hei_datahub.infra.index import reindex_all

            count = reindex_all()
            return f"[green]✓[/green] Reindex complete: {count} datasets indexed"
        except Exception as e:
            return f"[red]✗[/red] Reindex failed: {str(e)}"

    def _cmd_version(self) -> str:
        """Show version info."""
        output = f"[bold cyan]{__app_name__}[/bold cyan]\n"
        output += f"[bold]Version:[/bold] {__version__}\n"
        output += f"[bold]Repository:[/bold] {GITHUB_REPO}\n"

        return output

    def _cmd_logs(self, args: list) -> str:
        """Show recent log entries."""
        try:
            log_dir = Path.home() / ".hei-datahub" / "logs"
            log_file = log_dir / "datahub.log"

            if not log_file.exists():
                return "[yellow]⚠[/yellow] No log file found"

            # Get last N lines
            lines = 20
            if args and args[0].isdigit():
                lines = int(args[0])

            # Read last N lines
            with open(log_file) as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:]

            if not recent:
                return "[yellow]⚠[/yellow] Log file is empty"

            # Format output
            output = f"[bold]Last {len(recent)} log entries:[/bold]\n\n"
            output += "".join(recent)

            return output

        except Exception as e:
            return f"[red]✗[/red] Error reading logs: {str(e)}"

    def action_dismiss(self) -> None:
        """Close console."""
        self.app.pop_screen()
