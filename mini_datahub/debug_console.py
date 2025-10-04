"""
Debug console for developer commands.
Provides a command palette accessible via ':' key.
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Input, Static, Label
from textual.binding import Binding
from rich.syntax import Syntax
from rich.text import Text

from mini_datahub.version import __version__, __app_name__, GITHUB_REPO
from mini_datahub.git_ops import GitOperations
from mini_datahub.config import load_config
from mini_datahub.auto_pull import get_auto_pull_manager
from pathlib import Path
import subprocess


class DebugConsoleScreen(Screen):
    """Debug console for executing developer commands."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("ctrl+c", "dismiss", "Close"),
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
                "Available: reindex | sync | whoami | version | logs | help",
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
        elif cmd == "sync":
            return self._cmd_sync()
        elif cmd == "whoami":
            return self._cmd_whoami()
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
[yellow]sync[/yellow]       - Fetch and pull latest changes
[yellow]whoami[/yellow]     - Show GitHub user info
[yellow]version[/yellow]    - Show version and repo info
[yellow]logs[/yellow]       - Show recent log entries
[yellow]clear[/yellow]      - Clear output
[yellow]help[/yellow]       - Show this help

Press [bold]Escape[/bold] or [bold]Ctrl+C[/bold] to close."""

    def _cmd_reindex(self) -> str:
        """Reindex database."""
        try:
            from mini_datahub.index import reindex_all

            count = reindex_all()
            return f"[green]✓[/green] Reindex complete: {count} datasets indexed"
        except Exception as e:
            return f"[red]✗[/red] Reindex failed: {str(e)}"

    def _cmd_sync(self) -> str:
        """Sync with upstream."""
        try:
            config = load_config()
            if not config.catalog_repo_path:
                return "[red]✗[/red] Catalog path not configured"

            from pathlib import Path
            pull_manager = get_auto_pull_manager(Path(config.catalog_repo_path))

            # Check network
            if not pull_manager.check_network_available():
                return "[yellow]⚠[/yellow] No network connection"

            # Fetch first
            git_ops = pull_manager.git_ops
            git_ops.fetch()

            # Check if behind
            is_behind, commits_behind = pull_manager.is_behind_remote()
            if not is_behind:
                return "[green]✓[/green] Already up to date"

            # Pull
            success, message, old_commit, new_commit = pull_manager.pull_updates()

            if success:
                return "[green]✓[/green] Sync complete - please reindex"
            else:
                return "[red]✗[/red] Sync failed - check for local changes"

        except Exception as e:
            return f"[red]✗[/red] Sync failed: {str(e)}"

    def _cmd_whoami(self) -> str:
        """Show GitHub user info."""
        try:
            config = load_config()

            if not config.github_username:
                return "[yellow]⚠[/yellow] GitHub not configured"

            output = f"[bold]GitHub User:[/bold] {config.github_username}\n"
            output += f"[bold]Catalog Repo:[/bold] {config.github_catalog_repo}\n"

            # Get current branch
            try:
                git_ops = GitOperations(Path(config.catalog_path))
                branch = git_ops.get_current_branch()
                output += f"[bold]Branch:[/bold] {branch}\n"
            except Exception:
                pass

            return output

        except Exception as e:
            return f"[red]✗[/red] Error: {str(e)}"

    def _cmd_version(self) -> str:
        """Show version info."""
        output = f"[bold cyan]{__app_name__}[/bold cyan]\n"
        output += f"[bold]Version:[/bold] {__version__}\n"
        output += f"[bold]Repository:[/bold] {GITHUB_REPO}\n"

        # Get git info
        try:
            config = load_config()
            git_ops = GitOperations(Path(config.catalog_path))

            branch = git_ops.get_current_branch()
            commit = git_ops.get_current_commit()[:8]

            output += f"[bold]Branch:[/bold] {branch}\n"
            output += f"[bold]Commit:[/bold] {commit}\n"
        except Exception:
            pass

        return output

    def _cmd_logs(self, args: list) -> str:
        """Show recent log entries."""
        try:
            log_dir = Path.home() / ".mini-datahub" / "logs"
            log_file = log_dir / "datahub.log"

            if not log_file.exists():
                return "[yellow]⚠[/yellow] No log file found"

            # Get last N lines
            lines = 20
            if args and args[0].isdigit():
                lines = int(args[0])

            # Read last N lines
            with open(log_file, 'r') as f:
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
