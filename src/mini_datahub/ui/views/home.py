"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging
import webbrowser
from datetime import date
from typing import Any, Optional
import random

import pyperclip
import requests

logger = logging.getLogger(__name__)
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TextArea,
)
from textual.reactive import reactive
from textual.timer import Timer

from mini_datahub.infra.db import ensure_database
from mini_datahub.infra.index import get_dataset_from_store as get_dataset_by_id, upsert_dataset
from mini_datahub.services.search import search_datasets
from mini_datahub.infra.index import list_all_datasets
from mini_datahub.infra.store import validate_metadata
from mini_datahub.services.catalog import save_dataset, generate_id as generate_unique_id
from mini_datahub.services.config import get_config


def _build_bindings_from_config() -> list[Binding]:
    """Build keybindings list from config file."""
    try:
        from mini_datahub.ui.keybindings import bind_actions_from_config, get_action_display_map_home

        config = get_config()
        keybindings = config.get_keybindings()
        action_map = get_action_display_map_home()

        bindings = bind_actions_from_config(action_map, keybindings)

        if not bindings:
            logger.warning("No bindings generated from config, using defaults")
            raise ValueError("Empty bindings")

        return bindings
    except Exception as e:
        logger.warning(f"Failed to load keybindings from config: {e}, using defaults")
        # Fallback to hardcoded defaults if config fails
        return [
            Binding("a", "add_dataset", "Add Dataset", key_display="a"),
            Binding("s", "settings", "Settings", key_display="s"),
            Binding("o", "open_details", "Open", show=False),
            Binding("enter", "open_details", "View Details", show=False),
            Binding("p", "outbox", "Outbox", key_display="p"),
            Binding("u", "pull_updates", "Pull", key_display="u"),
            Binding("r", "refresh_data", "Refresh", key_display="r"),
            Binding("q", "quit", "Quit", key_display="^q"),
            Binding("j", "move_down", "Down", show=False),
            Binding("k", "move_up", "Up", show=False),
            Binding("down", "move_down", "", show=False),
            Binding("up", "move_up", "", show=False),
            Binding("gg", "jump_top", "Top", key_display="gg", show=False),
            Binding("G", "jump_bottom", "Bottom", show=False),
            Binding("/", "focus_search", "Search", key_display="/"),
            Binding("escape", "clear_search", "Clear", show=False),
            Binding(":", "debug_console", "Debug", show=False),
            Binding("?", "show_help", "Help", key_display="?"),
        ]


class HomeScreen(Screen):
    """Main screen with search functionality and Neovim-style navigation."""

    # Load bindings from config file
    BINDINGS = _build_bindings_from_config()

    # Load CSS from styles directory
    CSS_PATH = "../styles/home.tcss"

    search_mode = reactive(False)
    _debounce_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        from mini_datahub.ui.assets.loader import get_logo_widget_text

        # Load logo from config
        logo_text = get_logo_widget_text(get_config())

        yield Header()
        yield Container(
            Static(logo_text, id="banner"),
            Static("", id="update-status", classes="hidden"),
            Static("🔍 Search Datasets  |  Mode: [bold cyan]Normal[/bold cyan]", id="mode-indicator"),
            Static(id="github-status"),
            Input(placeholder="Type / to search | Tab/→/Ctrl+F for autocomplete | Enter to view", id="search-input"),
            Horizontal(id="filter-badges-container", classes="filter-badges"),
            Label("All Datasets", id="results-label"),
            DataTable(id="results-table", cursor_type="row"),
            id="search-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when mounted."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("ID", "Name", "Description")
        table.cursor_type = "row"
        # Start with table focused, but don't refocus it during searches
        table.focus()

        # Setup search autocomplete
        self._setup_search_autocomplete()

        # Update GitHub status indicator
        self.update_github_status()

        # Load all datasets initially
        self.load_all_datasets()

    def _setup_search_autocomplete(self) -> None:
        """Setup autocomplete suggester for search input."""
        try:
            from mini_datahub.ui.widgets.autocomplete import SearchSuggester

            search_input = self.query_one("#search-input", Input)
            search_input.suggester = SearchSuggester()
        except Exception as e:
            logger.warning(f"Failed to setup search autocomplete: {e}")

    def update_github_status(self) -> None:
        """Update GitHub connection status display."""
        from mini_datahub.app.settings import get_github_config

        status_widget = self.query_one("#github-status", Static)
        config = get_github_config()

        if config.has_credentials() and self.app.github_connected:
            status_widget.update(f"[green]● GitHub Connected[/green] ({config.username}@{config.owner}/{config.repo})")
        elif config.has_credentials():
            status_widget.update("[yellow]⚠ GitHub Configured (connection failed)[/yellow] [dim]Press S for Settings[/dim]")
        else:
            status_widget.update("[dim]○ GitHub Not Connected[/dim] [dim]Press S to configure[/dim]")

    def load_all_datasets(self) -> None:
        """Load and display all available datasets."""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        try:
            results = list_all_datasets()
            label = self.query_one("#results-label", Label)
            label.update(f"All Datasets ({len(results)} total)")

            for result in results:
                # Get description from metadata or use snippet
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    # Use description from metadata if snippet is empty
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:80] + "..." if len(description) > 80 else description
                else:
                    # Clean snippet of HTML tags for display
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:80] + "..." if len(snippet) > 80 else snippet

                table.add_row(
                    result["id"],
                    result["name"][:40],
                    snippet,
                    key=result["id"],
                )

            # Don't steal focus - let user continue typing

        except Exception as e:
            self.app.notify(f"Error loading datasets: {str(e)}", severity="error", timeout=5)

    def watch_search_mode(self, mode: bool) -> None:
        """Update mode indicator when search mode changes."""
        indicator = self.query_one("#mode-indicator", Static)
        if mode:
            indicator.update("🔍 Search Datasets  |  Mode: [bold green]Insert[/bold green]")
        else:
            indicator.update("🔍 Search Datasets  |  Mode: [bold cyan]Normal[/bold cyan]")

    @on(Input.Changed, "#search-input")
    def on_search_input(self, event: Input.Changed) -> None:
        """Handle search input changes with debouncing."""
        # Cancel existing timer
        if self._debounce_timer:
            self._debounce_timer.stop()

        # Get debounce from config or use default
        debounce_ms = 150  # default
        if hasattr(self.app, 'config') and self.app.config:
            debounce_ms = self.app.config.get("search.debounce_ms", 150)

        # Set new timer for debounced search
        self._debounce_timer = self.set_timer(debounce_ms / 1000.0, lambda: self.perform_search(event.value))

    def perform_search(self, query: str) -> None:
        """Execute search and update results table."""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        # If query is empty or very short, show all datasets
        if not query.strip() or len(query.strip()) < 2:
            self._update_filter_badges("")
            self.load_all_datasets()
            return

        try:
            # Update filter badges
            self._update_filter_badges(query)

            results = search_datasets(query)
            label = self.query_one("#results-label", Label)
            label.update(f"Search Results ({len(results)} found)")

            if not results:
                label.update(f"No results for '{query}'")
                return

            for result in results:
                # Get description from metadata or use snippet
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    # Use description from metadata if snippet is empty
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:80] + "..." if len(description) > 80 else description
                else:
                    # Clean snippet of HTML tags for display
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:80] + "..." if len(snippet) > 80 else snippet

                table.add_row(
                    result["id"],
                    result["name"][:40],
                    snippet,
                    key=result["id"],
                )

            # Don't steal focus from search input

        except Exception as e:
            self.app.notify(f"Search error: {str(e)}", severity="error", timeout=5)

    def _get_badge_color_class(self, text: str) -> str:
        """Get a retro background color class for a badge based on text hash."""
        # Use hash for consistent color per term
        color_seed = hash(text) % 100

        # Retro color palette (muted, vintage colors)
        color_classes = [
            "badge-retro-teal",
            "badge-retro-coral",
            "badge-retro-sage",
            "badge-retro-mauve",
            "badge-retro-amber",
            "badge-retro-slate",
        ]

        return color_classes[color_seed % len(color_classes)]

    def _update_filter_badges(self, query: str) -> None:
        """Update visual badges showing active search filters."""
        from mini_datahub.core.queries import QueryParser

        badges_container = self.query_one("#filter-badges-container", Horizontal)
        badges_container.remove_children()

        if not query.strip():
            return

        try:
            parser = QueryParser()
            parsed = parser.parse(query)

            # Show badges for field filters
            for term in parsed.terms:
                if not term.is_free_text:
                    operator_symbols = {
                        'CONTAINS': ':',
                        'GT': '>',
                        'LT': '<',
                        'GTE': '>=',
                        'LTE': '<=',
                        'EQ': '='
                    }
                    op_symbol = operator_symbols.get(term.operator.name, ':')
                    badge_text = f"{term.field}{op_symbol}{term.value}"
                    color_class = self._get_badge_color_class(badge_text)
                    badges_container.mount(Static(f"🏷 {badge_text}", classes=f"filter-badge {color_class}"))

            # Show individual badges for each free text term
            # Fix for Bug #10: Display separate tags instead of one combined token
            free_text_terms = [term for term in parsed.terms if term.is_free_text]
            logger.debug(f"DEBUG Bug #10: Found {len(free_text_terms)} free text terms: {[t.value for t in free_text_terms]}")

            for term in free_text_terms:
                badge = Static(f"[dim]📝 {term.value}[/dim]", classes="filter-badge")
                badges_container.mount(badge)
                logger.debug(f"DEBUG Bug #10: Mounted badge for term: {term.value}")

        except Exception as e:
            # If parsing fails, just show the raw query
            badges_container.mount(Static(f"[dim]🔍 {query}[/dim]", classes="filter-badge"))

    def action_focus_search(self) -> None:
        """Focus search input and enter insert mode."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
        self.search_mode = True

    def on_key(self, event) -> None:
        """Handle key events for autocomplete and navigation."""
        # Only handle when search input is focused
        search_input = self.query_one("#search-input", Input)

        if search_input.has_focus:
            # Tab accepts autocomplete and prevents navigation to table
            if event.key == "tab":
                # Manually accept the suggestion by moving cursor to end
                # This is what Textual does internally for Right Arrow with suggester
                if hasattr(search_input, 'suggester') and search_input.suggester:
                    # Move cursor to end to accept suggestion
                    search_input.cursor_position = len(search_input.value)
                    # Trigger cursor_right action which accepts the suggestion
                    search_input.action_cursor_right()
                # Prevent Tab from navigating away
                event.prevent_default()
                event.stop()

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self) -> None:
        """Handle search submission - move focus to table."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0:
            table.focus()
            self.search_mode = False

    def action_clear_search(self) -> None:
        """Clear search or exit insert mode."""
        search_input = self.query_one("#search-input", Input)

        if self.search_mode:
            # Exit insert mode
            table = self.query_one("#results-table", DataTable)
            table.focus()
            self.search_mode = False
        elif search_input.value:
            # Clear search
            search_input.value = ""
            self.load_all_datasets()
        else:
            # Focus table
            table = self.query_one("#results-table", DataTable)
            table.focus()

    def action_move_down(self) -> None:
        """Move selection down (j key)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.has_focus:
            table.action_cursor_down()

    def action_move_up(self) -> None:
        """Move selection up (k key)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.has_focus:
            table.action_cursor_up()

    def action_jump_top(self) -> None:
        """Jump to first row (gg)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0:
            table.cursor_coordinate = (0, 0)

    def action_jump_bottom(self) -> None:
        """Jump to last row (G)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0:
            table.cursor_coordinate = (table.row_count - 1, 0)

    def action_add_dataset(self) -> None:
        """Navigate to Add Dataset screen."""
        self.app.push_screen(AddDataScreen())

    def action_open_details(self) -> None:
        """Open details for selected dataset."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.cursor_row < table.row_count:
            # Get the row key properly
            try:
                row_key = table.get_row_at(table.cursor_row)[0]
                if row_key:
                    self.app.push_screen(DetailsScreen(str(row_key)))
            except Exception as e:
                self.app.notify(f"Error opening details: {str(e)}", severity="error", timeout=3)

    @on(DataTable.RowSelected, "#results-table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in results table."""
        try:
            # Get the ID from the first column of the selected row
            row = event.data_table.get_row_at(event.cursor_row)
            dataset_id = str(row[0])
            self.app.push_screen(DetailsScreen(dataset_id))
        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error", timeout=3)

    def action_show_help(self) -> None:
        """Show help overlay with keybindings (? key)."""
        from mini_datahub.ui.widgets.help_overlay import HelpOverlay
        from mini_datahub.services.actions import ActionContext
        self.app.push_screen(HelpOverlay(ActionContext.HOME))

    def action_settings(self) -> None:
        """Open settings menu (S key)."""
        from mini_datahub.ui.views.settings_menu import SettingsMenuScreen
        self.app.push_screen(SettingsMenuScreen())

    def action_outbox(self) -> None:
        """Open outbox screen (P key)."""
        from mini_datahub.ui.views.outbox import OutboxScreen
        self.app.push_screen(OutboxScreen())

    def action_pull_updates(self) -> None:
        """Start pull updates task."""
        self.app.pull_updates()

    def action_refresh_data(self) -> None:
        """Refresh/reload all datasets."""
        self.notify("Refreshing datasets...", timeout=2)
        self.load_all_datasets()
        self.notify("✓ Datasets refreshed", timeout=3)

    def action_debug_console(self) -> None:
        """Open debug console (: key)."""
        from mini_datahub.ui.widgets.console import DebugConsoleScreen
        self.app.push_screen(DebugConsoleScreen())


class HelpScreen(Screen):
    """Help screen showing keybindings."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
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
  [cyan]S[/cyan]           Settings (GitHub config)
  [cyan]P[/cyan]           Outbox (retry failed PRs)
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
        )
        yield Footer()

    def action_dismiss(self) -> None:
        """Close help screen."""
        self.app.pop_screen()


class DetailsScreen(Screen):
    """Screen to view dataset details with Neovim-style keys."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
        Binding("b", "back", "Back", show=False),
        ("e", "enter_edit_mode", "Edit"),
        ("y", "copy_source", "Copy Source"),
        ("o", "open_url", "Open URL"),
        Binding("P", "publish_pr", "Publish as PR", key_display="P"),
    ]

    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id
        self.metadata = None
        self._exists_remotely = None  # Cache for remote existence check

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label(f"Dataset: {self.dataset_id}", classes="title"),
            Static(id="details-content"),
            Static(id="pr-status", classes="pr-status"),
            id="details-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load and display dataset details."""
        try:
            self.metadata = get_dataset_by_id(self.dataset_id)
            if not self.metadata:
                content = self.query_one("#details-content", Static)
                content.update("Dataset not found.")
                return

            # Format metadata for display
            lines = []
            lines.append(f"[bold]ID:[/bold] {self.metadata.get('id', 'N/A')}")
            lines.append(f"[bold]Name:[/bold] {self.metadata.get('dataset_name', 'N/A')}")
            lines.append(f"[bold]Description:[/bold] {self.metadata.get('description', 'N/A')}")
            lines.append(f"[bold]Source:[/bold] {self.metadata.get('source', 'N/A')}")
            lines.append(f"[bold]Date Created:[/bold] {self.metadata.get('date_created', 'N/A')}")
            lines.append(f"[bold]Storage Location:[/bold] {self.metadata.get('storage_location', 'N/A')}")

            if self.metadata.get('file_format'):
                lines.append(f"[bold]File Format:[/bold] {self.metadata['file_format']}")
            if self.metadata.get('size'):
                lines.append(f"[bold]Size:[/bold] {self.metadata['size']}")
            if self.metadata.get('data_types'):
                lines.append(f"[bold]Data Types:[/bold] {', '.join(self.metadata['data_types'])}")
            if self.metadata.get('used_in_projects'):
                lines.append(f"[bold]Used In Projects:[/bold] {', '.join(self.metadata['used_in_projects'])}")
            if self.metadata.get('last_updated'):
                lines.append(f"[bold]Last Updated:[/bold] {self.metadata['last_updated']}")
            if self.metadata.get('dependencies'):
                lines.append(f"[bold]Dependencies:[/bold] {self.metadata['dependencies']}")
            if self.metadata.get('preprocessing_steps'):
                lines.append(f"[bold]Preprocessing:[/bold] {self.metadata['preprocessing_steps']}")
            if self.metadata.get('temporal_coverage'):
                lines.append(f"[bold]Temporal Coverage:[/bold] {self.metadata['temporal_coverage']}")
            if self.metadata.get('spatial_coverage'):
                lines.append(f"[bold]Spatial Coverage:[/bold] {self.metadata['spatial_coverage']}")

            if self.metadata.get('schema_fields'):
                lines.append("\n[bold]Schema Fields:[/bold]")
                for field in self.metadata['schema_fields']:
                    lines.append(f"  • {field['name']} ({field['type']}): {field.get('description', '')}")

            if self.metadata.get('linked_documentation'):
                lines.append("\n[bold]Documentation:[/bold]")
                for doc in self.metadata['linked_documentation']:
                    lines.append(f"  • {doc}")

            content = self.query_one("#details-content", Static)
            content.update("\n".join(lines))

            # Check remote status asynchronously
            self.check_remote_status()

        except Exception as e:
            self.app.notify(f"Error loading details: {str(e)}", severity="error", timeout=5)

    def _rebuild_details_display(self) -> None:
        """Rebuild the details display using current metadata without reloading from disk."""
        if not self.metadata:
            return

        try:
            # Format metadata for display
            lines = []
            lines.append(f"[bold]ID:[/bold] {self.metadata.get('id', 'N/A')}")
            lines.append(f"[bold]Name:[/bold] {self.metadata.get('dataset_name', 'N/A')}")
            lines.append(f"[bold]Description:[/bold] {self.metadata.get('description', 'N/A')}")
            lines.append(f"[bold]Source:[/bold] {self.metadata.get('source', 'N/A')}")
            lines.append(f"[bold]Date Created:[/bold] {self.metadata.get('date_created', 'N/A')}")
            lines.append(f"[bold]Storage Location:[/bold] {self.metadata.get('storage_location', 'N/A')}")

            if self.metadata.get('file_format'):
                lines.append(f"[bold]File Format:[/bold] {self.metadata['file_format']}")
            if self.metadata.get('size'):
                lines.append(f"[bold]Size:[/bold] {self.metadata['size']}")
            if self.metadata.get('data_types'):
                lines.append(f"[bold]Data Types:[/bold] {', '.join(self.metadata['data_types'])}")
            if self.metadata.get('used_in_projects'):
                lines.append(f"[bold]Used In Projects:[/bold] {', '.join(self.metadata['used_in_projects'])}")
            if self.metadata.get('last_updated'):
                lines.append(f"[bold]Last Updated:[/bold] {self.metadata['last_updated']}")
            if self.metadata.get('dependencies'):
                lines.append(f"[bold]Dependencies:[/bold] {self.metadata['dependencies']}")
            if self.metadata.get('preprocessing_steps'):
                lines.append(f"[bold]Preprocessing:[/bold] {self.metadata['preprocessing_steps']}")
            if self.metadata.get('temporal_coverage'):
                lines.append(f"[bold]Temporal Coverage:[/bold] {self.metadata['temporal_coverage']}")
            if self.metadata.get('spatial_coverage'):
                lines.append(f"[bold]Spatial Coverage:[/bold] {self.metadata['spatial_coverage']}")

            if self.metadata.get('schema_fields'):
                lines.append("\n[bold]Schema Fields:[/bold]")
                for field in self.metadata['schema_fields']:
                    lines.append(f"  • {field['name']} ({field['type']}): {field.get('description', '')}")

            if self.metadata.get('linked_documentation'):
                lines.append("\n[bold]Documentation:[/bold]")
                for doc in self.metadata['linked_documentation']:
                    lines.append(f"  • {doc}")

            content = self.query_one("#details-content", Static)
            content.update("\n".join(lines))

            # Check remote status asynchronously to update PR button
            self.check_remote_status()

        except Exception as e:
            logger.warning(f"Error rebuilding details display: {e}")

    @work(exclusive=True)
    async def check_remote_status(self) -> None:
        """Check if dataset exists in remote repository."""
        from mini_datahub.app.settings import get_github_config
        from mini_datahub.infra.github_api import GitHubIntegration

        config = get_github_config()
        pr_status = self.query_one("#pr-status", Static)

        if not config.has_credentials():
            pr_status.update("[dim]💡 Configure GitHub in Settings (S) to publish PRs[/dim]")
            return

        try:
            github = GitHubIntegration(config)
            exists, msg = github.check_file_exists_remote(f"data/{self.dataset_id}/metadata.yaml")
            self._exists_remotely = exists

            if exists:
                pr_status.update("[green]✓ Already in catalog repo[/green]  [bold cyan]Press P to create Update PR![/bold cyan]")
            else:
                pr_status.update("[yellow]📤 Not yet in catalog repo[/yellow]  [bold cyan]Press P to Publish as PR![/bold cyan]")

        except Exception as e:
            pr_status.update(f"[dim]⚠ Could not check remote status: {str(e)}[/dim]")

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()

    def action_copy_source(self) -> None:
        """Copy source to clipboard (y key)."""
        if self.metadata and self.metadata.get('source'):
            try:
                pyperclip.copy(self.metadata['source'])
                self.app.notify("✓ Source copied to clipboard!", timeout=2)
            except Exception as e:
                self.app.notify(f"Failed to copy: {str(e)}", severity="error", timeout=3)

    def action_open_url(self) -> None:
        """Open source URL in browser if it's a URL (o key)."""
        if self.metadata and self.metadata.get('source'):
            source = self.metadata['source']
            if source.startswith('http://') or source.startswith('https://'):
                try:
                    webbrowser.open(source)
                    self.app.notify("Opening URL in browser...", timeout=2)
                except Exception as e:
                    self.app.notify(f"Failed to open URL: {str(e)}", severity="error", timeout=3)
            else:
                self.app.notify("Source is not a URL", severity="warning", timeout=2)

    def action_enter_edit_mode(self) -> None:
        """Enter edit mode (e key)."""
        if not self.metadata:
            self.app.notify("No metadata loaded", severity="error", timeout=3)
            return

        # Push the edit screen
        self.app.push_screen(EditDetailsScreen(self.dataset_id, self.metadata.copy()))

    def action_publish_pr(self) -> None:
        """Publish dataset as PR (P key)."""
        if not self.metadata:
            self.app.notify("No metadata loaded", severity="error", timeout=3)
            return

        # Determine if this is an update or new dataset
        is_update = self._exists_remotely is True

        # Start async PR creation
        self.create_pr(is_update=is_update)

    @work(exclusive=True)
    async def create_pr(self, is_update: bool = False) -> None:
        """Create PR for this dataset.

        Args:
            is_update: True if updating existing dataset, False if new dataset
        """
        from mini_datahub.app.settings import get_github_config
        from mini_datahub.services.publish import PRWorkflow
        from pathlib import Path

        config = get_github_config()
        pr_status = self.query_one("#pr-status", Static)

        # Validate configuration
        if not config.has_credentials():
            pr_status.update("[red]✗ GitHub not configured. Press S to open Settings.[/red]")
            self.app.notify("GitHub not configured. Open Settings (S) to connect.", severity="error", timeout=5)
            return

        if not config.catalog_repo_path:
            pr_status.update("[red]✗ Catalog repository path not set. Update in Settings (S).[/red]")
            self.app.notify("Catalog path not configured. Update in Settings (S).", severity="error", timeout=5)
            return

        catalog_path = Path(config.catalog_repo_path).expanduser().resolve()
        if not catalog_path.exists():
            pr_status.update(f"[red]✗ Catalog path does not exist: {catalog_path}[/red]")
            self.app.notify(f"Catalog path not found: {catalog_path}", severity="error", timeout=5)
            return

        action_verb = "Updating" if is_update else "Creating"
        pr_status.update(f"[yellow]📤 {action_verb} PR...[/yellow]")
        self.app.notify(f"{action_verb} pull request...", timeout=3)

        try:
            # Execute PR workflow
            workflow = PRWorkflow()
            success, message, pr_url, pr_number = workflow.execute(
                metadata=self.metadata,
                dataset_id=self.dataset_id,
                is_update=is_update,
            )

            if success:
                pr_status.update(f"[green]✓ PR #{pr_number} created successfully![/green]")
                self.app.notify(f"✓ PR created: #{pr_number}", timeout=5)

                # Offer to open PR in browser
                if pr_url:
                    try:
                        webbrowser.open(pr_url)
                    except Exception:
                        pass  # Silently fail if browser opening doesn't work

                # Update remote existence flag
                self._exists_remotely = True

            else:
                pr_status.update(f"[red]✗ PR creation failed[/red]")
                self.app.notify(f"✗ {message}", severity="error", timeout=10)

        except Exception as e:
            pr_status.update(f"[red]✗ Error: {str(e)}[/red]")
            self.app.notify(f"Error creating PR: {str(e)}", severity="error", timeout=10)


class ConfirmCancelDialog(Screen):
    """Modal dialog to confirm canceling edits with unsaved changes."""

    CSS = """
    #dialog-overlay {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    .dialog-box {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .dialog-title {
        text-align: center;
        width: 100%;
    }

    .dialog-text {
        text-align: center;
        width: 100%;
        padding: 1;
    }
    """

    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
        ("escape", "cancel", "No"),
    ]

    def __init__(self, dataset_id: str, dirty_count: int):
        super().__init__()
        self.dataset_id = dataset_id
        self.dirty_count = dirty_count

    def compose(self) -> ComposeResult:
        from textual.containers import Container, Vertical
        yield Container(
            Vertical(
                Static(f"[bold yellow]Discard Changes?[/bold yellow]", classes="dialog-title"),
                Static(f"\nYou have {self.dirty_count} unsaved change(s) to [cyan]{self.dataset_id}[/cyan].\n", classes="dialog-text"),
                Static("Press [bold]Y[/bold] to discard changes or [bold]N[/bold] to keep editing.", classes="dialog-text"),
                id="confirm-dialog",
                classes="dialog-box",
            ),
            id="dialog-overlay",
        )

    def action_confirm(self) -> None:
        """User confirmed - discard changes."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """User canceled - keep editing."""
        self.dismiss(False)


class EditDetailsScreen(Screen):
    """Screen for inline editing of dataset metadata with undo/redo support."""

    CSS = """
    #edit-scroll {
        height: 1fr;
        overflow-y: auto;
    }

    #edit-form-container {
        height: auto;
        padding: 1 2;
    }

    #edit-form-container Label {
        margin-top: 1;
    }

    #edit-form-container Input, #edit-form-container TextArea {
        margin-bottom: 0;
    }

    .field-error {
        color: $error;
        margin-bottom: 1;
    }

    .edit-status {
        margin-top: 2;
        padding: 1;
        background: $surface;
        text-align: center;
    }

    #edit-description {
        height: 8;
    }
    """

    BINDINGS = [
        ("ctrl+s", "save_edits", "Save"),
        ("escape", "cancel_edits", "Cancel"),
        ("ctrl+z", "undo_edit", "Undo"),
        ("ctrl+shift+z", "redo_edit", "Redo"),
    ]

    def __init__(self, dataset_id: str, metadata: dict):
        super().__init__()
        self.dataset_id = dataset_id
        self.original_metadata = metadata.copy()
        self.metadata = metadata.copy()

        # Undo/redo stacks
        self._undo_stack = []  # List of (field, old_value, new_value)
        self._redo_stack = []
        self._max_undo = 50

        # Track dirty fields
        self._dirty_fields = set()

        # Field validation errors
        self._field_errors = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label(f"✏️ Editing: {self.dataset_id}  |  [italic]Ctrl+S to save, Esc to cancel[/italic]", classes="title"),
            Container(
                Label("Dataset Name:"),
                Input(value=self.metadata.get('dataset_name', ''), id="edit-name"),
                Static(id="error-name", classes="field-error"),

                Label("Description:"),
                TextArea(id="edit-description"),
                Static(id="error-description", classes="field-error"),

                Label("Source:"),
                Input(value=self.metadata.get('source', ''), id="edit-source"),
                Static(id="error-source", classes="field-error"),

                Label("Storage Location:"),
                Input(value=self.metadata.get('storage_location', ''), id="edit-storage"),
                Static(id="error-storage", classes="field-error"),

                Label("Date Created (YYYY-MM-DD):"),
                Input(value=str(self.metadata.get('date_created', '')), id="edit-date"),
                Static(id="error-date", classes="field-error"),

                Label("File Format:"),
                Input(value=self.metadata.get('file_format', ''), id="edit-format"),
                Static(id="error-format", classes="field-error"),

                Label("Size:"),
                Input(value=self.metadata.get('size', ''), id="edit-size"),
                Static(id="error-size", classes="field-error"),

                Label("Data Types (comma-separated):"),
                Input(value=', '.join(self.metadata.get('data_types', [])), id="edit-types"),
                Static(id="error-types", classes="field-error"),

                Label("Used In Projects (comma-separated):"),
                Input(value=', '.join(self.metadata.get('used_in_projects', [])), id="edit-projects"),
                Static(id="error-projects", classes="field-error"),

                Static(id="edit-status", classes="edit-status"),

                id="edit-form-container",
            ),
            id="edit-scroll",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize field values after mounting."""
        # Set TextArea value (can't be done in compose)
        desc_area = self.query_one("#edit-description", TextArea)
        desc_area.text = self.metadata.get('description', '')

        # Focus first field
        self.query_one("#edit-name", Input).focus()

        self._update_status()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        """Track field changes, mark as dirty, and validate on blur."""
        if not event.input.id or not event.input.id.startswith('edit-'):
            return

        field_name = event.input.id.replace('edit-', '')
        old_value = self._get_field_value(field_name)
        new_value = event.value

        # Track in undo stack
        if old_value != new_value:
            self._push_undo(field_name, old_value, new_value)
            self._mark_dirty(field_name)
            self._update_metadata_from_field(field_name, new_value)
            self._update_status()

    @on(TextArea.Changed, "#edit-description")
    def on_textarea_changed(self, event: TextArea.Changed) -> None:
        """Track TextArea changes."""
        field_name = 'description'
        old_value = self.metadata.get(field_name, '')
        new_value = event.text_area.text

        if old_value != new_value:
            self._push_undo(field_name, old_value, new_value)
            self._mark_dirty(field_name)
            self.metadata[field_name] = new_value
            self._update_status()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Validate field on Enter key or blur."""
        if not event.input.id or not event.input.id.startswith('edit-'):
            return

        field_name = event.input.id.replace('edit-', '')
        self._validate_field(field_name)

    def _get_field_value(self, field_name: str) -> Any:
        """Get current field value from metadata."""
        field_map = {
            'name': 'dataset_name',
            'description': 'description',
            'source': 'source',
            'storage': 'storage_location',
            'date': 'date_created',
            'format': 'file_format',
            'size': 'size',
            'types': 'data_types',
            'projects': 'used_in_projects',
        }

        meta_field = field_map.get(field_name, field_name)
        value = self.metadata.get(meta_field, '')

        # Convert lists to strings for display
        if isinstance(value, list):
            return ', '.join(value)
        return str(value) if value else ''

    def _update_metadata_from_field(self, field_name: str, value: str) -> None:
        """Update metadata dict from field value."""
        field_map = {
            'name': 'dataset_name',
            'description': 'description',
            'source': 'source',
            'storage': 'storage_location',
            'date': 'date_created',
            'format': 'file_format',
            'size': 'size',
            'types': 'data_types',
            'projects': 'used_in_projects',
        }

        meta_field = field_map.get(field_name, field_name)

        # Handle list fields
        if field_name in ('types', 'projects'):
            if value.strip():
                self.metadata[meta_field] = [v.strip() for v in value.split(',') if v.strip()]
            else:
                self.metadata[meta_field] = []
        else:
            self.metadata[meta_field] = value

    def _validate_field(self, field_name: str) -> bool:
        """Validate a single field and show error."""
        from mini_datahub.services.storage import validate_field

        field_map = {
            'name': 'dataset_name',
            'description': 'description',
            'source': 'source',
            'storage': 'storage_location',
            'date': 'date_created',
            'format': 'file_format',
            'size': 'size',
            'types': 'data_types',
            'projects': 'used_in_projects',
        }

        meta_field = field_map.get(field_name, field_name)
        field_value = self.metadata.get(meta_field)

        # Validate
        is_valid, error_msg = validate_field(meta_field, field_value, self.metadata)

        # Update error display
        error_widget_id = f"error-{field_name}"
        try:
            error_widget = self.query_one(f"#{error_widget_id}", Static)
            if is_valid:
                error_widget.update("")
                self._field_errors.pop(field_name, None)
            else:
                error_widget.update(f"[red]⚠ {error_msg}[/red]")
                self._field_errors[field_name] = error_msg
        except Exception:
            pass

        return is_valid

    def _mark_dirty(self, field_name: str) -> None:
        """Mark a field as modified."""
        self._dirty_fields.add(field_name)

    def _push_undo(self, field: str, old_value: Any, new_value: Any) -> None:
        """Push change to undo stack."""
        self._undo_stack.append((field, old_value, new_value))

        # Trim stack if too large
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)

        # Clear redo stack on new change
        self._redo_stack.clear()

    def _update_status(self) -> None:
        """Update status bar with dirty field count and undo/redo availability."""
        status = self.query_one("#edit-status", Static)

        dirty_count = len(self._dirty_fields)
        error_count = len(self._field_errors)
        undo_available = len(self._undo_stack) > 0
        redo_available = len(self._redo_stack) > 0

        parts = []
        if dirty_count > 0:
            parts.append(f"[yellow]• {dirty_count} field(s) modified[/yellow]")
        if error_count > 0:
            parts.append(f"[red]⚠ {error_count} error(s)[/red]")
        if undo_available:
            parts.append("[dim]Ctrl+Z: Undo[/dim]")
        if redo_available:
            parts.append("[dim]Ctrl+Shift+Z: Redo[/dim]")

        if not parts:
            parts.append("[dim]No changes[/dim]")

        status.update("  |  ".join(parts))

    def action_save_edits(self) -> None:
        """Save changes (Ctrl+S)."""
        from mini_datahub.services.storage import save_dataset_atomic

        # Validate all fields first
        has_errors = False
        for field_name in ['name', 'description', 'source', 'storage']:
            if not self._validate_field(field_name):
                has_errors = True

        if has_errors:
            self.app.notify("Please fix validation errors before saving", severity="error", timeout=5)
            return

        # Ensure metadata has 'id' field (critical for persistence)
        if 'id' not in self.metadata:
            self.metadata['id'] = self.dataset_id

        # Convert date objects to strings if needed for serialization
        from datetime import date
        metadata_to_save = self.metadata.copy()
        if isinstance(metadata_to_save.get('date_created'), date):
            metadata_to_save['date_created'] = metadata_to_save['date_created'].isoformat()
        if isinstance(metadata_to_save.get('last_updated'), date):
            metadata_to_save['last_updated'] = metadata_to_save['last_updated'].isoformat()

        # Attempt atomic save to LOCAL data/ directory
        self.app.notify("Saving changes...", timeout=2)
        logger.info(f"Saving edits for {self.dataset_id} to local data/ directory")
        success, error_msg = save_dataset_atomic(self.dataset_id, metadata_to_save)

        if success:
            # Update our in-memory copy to match what was saved
            self.metadata = metadata_to_save.copy()
            logger.info(f"✓ Successfully saved {self.dataset_id} to data/{self.dataset_id}/metadata.yaml")
            self.app.notify("✓ Dataset saved successfully!", timeout=3)

            # Refresh the parent DetailsScreen if it exists
            parent_screen = None
            try:
                # Find parent DetailsScreen and refresh it with the updated metadata
                for screen in self.app.screen_stack:
                    if isinstance(screen, DetailsScreen) and screen.dataset_id == self.dataset_id:
                        # Directly set the updated metadata
                        screen.metadata = self.metadata.copy()
                        # Rebuild the display with the new metadata
                        screen._rebuild_details_display()
                        parent_screen = screen
                        break
            except Exception as e:
                logger.warning(f"Could not refresh parent DetailsScreen: {e}")

            self.app.pop_screen()

            # Automatically trigger PR publishing (works for both new and updates)
            # Note: We call this via app.call_later to ensure the screen transition completes first
            if parent_screen:
                def trigger_auto_publish():
                    is_update = parent_screen._exists_remotely is True
                    action = "update" if is_update else "publish"
                    logger.info(f"Auto-{action} check: _exists_remotely={parent_screen._exists_remotely}")
                    logger.info(f"Triggering automatic PR {action}...")
                    self.app.notify(f"📤 Creating {action} pull request to catalog...", timeout=3)
                    parent_screen.action_publish_pr()

                # Delay the publish trigger slightly to let the screen pop complete
                self.app.call_later(trigger_auto_publish)
        else:
            self.app.notify(f"✗ Save failed: {error_msg}", severity="error", timeout=10)
            status = self.query_one("#edit-status", Static)
            status.update(f"[red]✗ Save failed: {error_msg}[/red]")

    def action_cancel_edits(self) -> None:
        """Cancel editing and discard changes (Esc)."""
        if len(self._dirty_fields) > 0:
            # Show confirmation dialog
            self.app.push_screen(
                ConfirmCancelDialog(self.dataset_id, len(self._dirty_fields)),
                self._handle_cancel_confirmation
            )
        else:
            self.app.pop_screen()

    def _handle_cancel_confirmation(self, confirmed: bool) -> None:
        """Handle confirmation dialog response."""
        if confirmed:
            self.app.notify("Changes discarded", timeout=2)
            self.app.pop_screen()

    def action_undo_edit(self) -> None:
        """Undo last edit (Ctrl+Z)."""
        if not self._undo_stack:
            self.app.notify("Nothing to undo", timeout=2)
            return

        # Pop from undo stack
        field, old_value, new_value = self._undo_stack.pop()

        # Push to redo stack
        self._redo_stack.append((field, old_value, new_value))

        # Restore old value
        self._restore_field_value(field, old_value)
        self._update_status()
        self.app.notify(f"Undid change to {field}", timeout=2)

    def action_redo_edit(self) -> None:
        """Redo last undone edit (Ctrl+Shift+Z)."""
        if not self._redo_stack:
            self.app.notify("Nothing to redo", timeout=2)
            return

        # Pop from redo stack
        field, old_value, new_value = self._redo_stack.pop()

        # Push back to undo stack
        self._undo_stack.append((field, old_value, new_value))

        # Restore new value
        self._restore_field_value(field, new_value)
        self._update_status()
        self.app.notify(f"Redid change to {field}", timeout=2)

    def _restore_field_value(self, field_name: str, value: Any) -> None:
        """Restore a field's value in the UI and metadata."""
        field_id_map = {
            'name': 'edit-name',
            'description': 'edit-description',
            'source': 'edit-source',
            'storage': 'edit-storage',
            'date': 'edit-date',
            'format': 'edit-format',
            'size': 'edit-size',
            'types': 'edit-types',
            'projects': 'edit-projects',
        }

        widget_id = field_id_map.get(field_name)
        if not widget_id:
            return

        # Update widget
        try:
            if widget_id == 'edit-description':
                widget = self.query_one(f"#{widget_id}", TextArea)
                widget.text = str(value)
            else:
                widget = self.query_one(f"#{widget_id}", Input)
                widget.value = str(value)
        except Exception:
            pass

        # Update metadata
        self._update_metadata_from_field(field_name, str(value))


class AddDataScreen(Screen):
    """Screen to add a new dataset with scrolling support and Neovim keys."""

    CSS = """
    #add-data-scroll {
        height: 1fr;
        overflow-y: auto;
    }

    #form-container {
        height: auto;
        padding: 1 2;
    }

    #form-container Label {
        margin-top: 1;
    }

    #form-container Input, #form-container TextArea {
        margin-bottom: 0;
    }

    #form-container Button {
        margin: 1 1 0 0;
    }

    #error-message {
        color: $error;
        margin-top: 1;
    }

    #probe-status {
        margin-left: 1;
    }

    #input-description {
        height: 8;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        Binding("q", "cancel", "Cancel (q)", show=False),
        ("ctrl+s", "submit", "Save"),
        Binding("j", "next_field", "Next", show=False),
        Binding("k", "prev_field", "Prev", show=False),
        Binding("ctrl+d", "scroll_down", "Scroll Down", show=False, priority=True),
        Binding("ctrl+u", "scroll_up", "Scroll Up", show=False, priority=True),
        Binding("pagedown", "scroll_down", "Scroll Down", show=False),
        Binding("pageup", "scroll_up", "Scroll Up", show=False),
        Binding("g", "jump_first", "First", show=False),
        Binding("G", "jump_last", "Last", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("➕ Add New Dataset  |  [italic]Ctrl+S to save, Esc/q to cancel[/italic]", classes="title"),
            Container(
                Label("Dataset Name (required):"),
                Input(placeholder="e.g., Global Weather Stations 2024", id="input-name"),
                Label("Description (required):"),
                TextArea(id="input-description"),
                Label("Source URL or snippet (required):"),
                Input(placeholder="e.g., https://example.com/data.csv", id="input-source"),
                Horizontal(
                    Button("Probe URL", id="probe-btn", variant="default"),
                    Label("", id="probe-status"),
                ),
                Label("Storage Location (required):"),
                Input(placeholder="e.g., s3://bucket/path/ or /local/path", id="input-storage"),
                Label("Date Created (optional, defaults to today):"),
                Input(placeholder="YYYY-MM-DD", id="input-date"),
                Label("File Format (optional):"),
                Input(placeholder="e.g., CSV, JSON, Parquet", id="input-format"),
                Label("Size (optional):"),
                Input(placeholder="e.g., 2.5 GB, 1M rows", id="input-size"),
                Label("Data Types (comma-separated, optional):"),
                Input(placeholder="e.g., weather, time-series", id="input-types"),
                Label("Used In Projects (comma-separated, optional):"),
                Input(placeholder="e.g., project-a, project-b", id="input-projects"),
                Label("ID (optional, auto-generated if empty):"),
                Input(placeholder="Leave empty to auto-generate", id="input-id"),
                Horizontal(
                    Button("Save Dataset", id="save-btn", variant="primary"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                ),
                Label("", id="error-message"),
                id="form-container",
            ),
            id="add-data-scroll",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus on first input."""
        self.query_one("#input-name", Input).focus()

    def action_next_field(self) -> None:
        """Move focus to next field (j key)."""
        self.screen.focus_next()
        # Scroll focused widget into view
        if self.screen.focused:
            self.screen.focused.scroll_visible()

    def action_prev_field(self) -> None:
        """Move focus to previous field (k key)."""
        self.screen.focus_previous()
        # Scroll focused widget into view
        if self.screen.focused:
            self.screen.focused.scroll_visible()

    def action_scroll_down(self) -> None:
        """Scroll down half page (Ctrl+d or Page Down)."""
        scroll = self.query_one("#add-data-scroll", VerticalScroll)
        # Use scroll_relative for more reliable scrolling
        scroll.scroll_relative(y=scroll.size.height // 2, animate=False)

    def action_scroll_up(self) -> None:
        """Scroll up half page (Ctrl+u or Page Up)."""
        scroll = self.query_one("#add-data-scroll", VerticalScroll)
        # Use scroll_relative for more reliable scrolling
        scroll.scroll_relative(y=-(scroll.size.height // 2), animate=False)

    def action_jump_first(self) -> None:
        """Jump to first field (gg)."""
        self.query_one("#input-name", Input).focus()

    def action_jump_last(self) -> None:
        """Jump to last button (G)."""
        self.query_one("#save-btn", Button).focus()

    @on(Button.Pressed, "#probe-btn")
    def on_probe_button(self) -> None:
        """Handle URL probe button press."""
        source_input = self.query_one("#input-source", Input)
        source = source_input.value.strip()

        if not source:
            self.app.notify("Please enter a source URL first", severity="warning", timeout=3)
            return

        if not (source.startswith('http://') or source.startswith('https://')):
            self.app.notify("Source must be an HTTP(S) URL to probe", severity="warning", timeout=3)
            return

        # Run probe in background
        self.probe_url(source)

    @work(exclusive=True)
    async def probe_url(self, url: str) -> None:
        """Probe URL for content type and size."""
        status_label = self.query_one("#probe-status", Label)
        status_label.update("Probing...")

        try:
            # HEAD request with timeout
            response = requests.head(url, timeout=10, allow_redirects=True)

            # Extract info
            content_type = response.headers.get('Content-Type', '')
            content_length = response.headers.get('Content-Length', '')

            # Guess format from content type
            format_guess = ""
            if 'csv' in content_type.lower():
                format_guess = "CSV"
            elif 'json' in content_type.lower():
                format_guess = "JSON"
            elif 'parquet' in content_type.lower():
                format_guess = "Parquet"
            elif 'excel' in content_type.lower() or 'spreadsheet' in content_type.lower():
                format_guess = "Excel"

            # Format size
            size_guess = ""
            if content_length:
                try:
                    size_bytes = int(content_length)
                    if size_bytes < 1024:
                        size_guess = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        size_guess = f"{size_bytes / 1024:.1f} KB"
                    elif size_bytes < 1024 * 1024 * 1024:
                        size_guess = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_guess = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
                except ValueError:
                    pass

            # Update fields with suggestions
            if format_guess:
                format_input = self.query_one("#input-format", Input)
                if not format_input.value:
                    format_input.value = format_guess

            if size_guess:
                size_input = self.query_one("#input-size", Input)
                if not size_input.value:
                    size_input.value = size_guess

            status_label.update(f"✓ Probed: {content_type[:30]}")
            self.app.notify("URL probed successfully!", timeout=3)

        except requests.Timeout:
            status_label.update("⚠ Timeout")
            self.app.notify("URL probe timed out", severity="warning", timeout=3)
        except Exception as e:
            status_label.update("✗ Failed")
            self.app.notify(f"Probe failed: {str(e)}", severity="error", timeout=3)

    @on(Button.Pressed, "#save-btn")
    def on_save_button(self) -> None:
        """Handle save button press."""
        self.submit_form()

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.action_cancel()

    def action_submit(self) -> None:
        """Submit the form."""
        self.submit_form()

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()

    def submit_form(self) -> None:
        """Validate and save the new dataset."""
        error_label = self.query_one("#error-message", Label)
        error_label.update("")

        # Gather form data
        name = self.query_one("#input-name", Input).value.strip()
        description = self.query_one("#input-description", TextArea).text.strip()
        source = self.query_one("#input-source", Input).value.strip()
        storage = self.query_one("#input-storage", Input).value.strip()
        date_str = self.query_one("#input-date", Input).value.strip()
        file_format = self.query_one("#input-format", Input).value.strip()
        size = self.query_one("#input-size", Input).value.strip()
        types_str = self.query_one("#input-types", Input).value.strip()
        projects_str = self.query_one("#input-projects", Input).value.strip()
        dataset_id = self.query_one("#input-id", Input).value.strip()

        # Validate required fields
        if not name:
            error_label.update("[red]Error: Dataset Name is required[/red]")
            self.query_one("#input-name", Input).focus()
            return
        if not description:
            error_label.update("[red]Error: Description is required[/red]")
            self.query_one("#input-description", TextArea).focus()
            return
        if not source:
            error_label.update("[red]Error: Source is required[/red]")
            self.query_one("#input-source", Input).focus()
            return
        if not storage:
            error_label.update("[red]Error: Storage Location is required[/red]")
            self.query_one("#input-storage", Input).focus()
            return

        # Generate ID if not provided
        if not dataset_id:
            dataset_id = generate_unique_id(name)

        # Parse date
        date_created = date_str if date_str else date.today().isoformat()

        # Parse lists
        data_types = [t.strip() for t in types_str.split(',') if t.strip()] if types_str else None
        used_in_projects = [p.strip() for p in projects_str.split(',') if p.strip()] if projects_str else None

        # Build metadata dict
        metadata = {
            "id": dataset_id,
            "dataset_name": name,
            "description": description,
            "source": source,
            "date_created": date_created,
            "storage_location": storage,
        }

        if file_format:
            metadata["file_format"] = file_format
        if size:
            metadata["size"] = size
        if data_types:
            metadata["data_types"] = data_types
        if used_in_projects:
            metadata["used_in_projects"] = used_in_projects

        # Validate and save
        success, error_msg, model = validate_metadata(metadata)
        if not success:
            error_label.update(f"[red]Validation Error:\n{error_msg}[/red]")
            return

        # Fix for issue #7: ALWAYS save to local data/ directory first
        # This ensures changes persist even if PR workflow fails
        success, msg = save_dataset(dataset_id, metadata)
        if not success:
            error_label.update(f"[red]{msg}[/red]")
            return

        # Try PR workflow if GitHub is configured (catalog repo is separate)
        from mini_datahub.app.settings import get_github_config
        from mini_datahub.services.publish import PRWorkflow

        config = get_github_config()
        if config.is_configured() and config.catalog_repo_path:
            # Execute Save → PR workflow
            self.create_pr(dataset_id, metadata)
        else:
            # Just save locally and show success
            self.app.notify(f"Dataset '{dataset_id}' saved successfully!", timeout=3)
            # Show one-time nudge about GitHub integration
            if not hasattr(self.app, '_github_nudge_shown'):
                self.app.notify(
                    "💡 Tip: Connect GitHub in Settings (S) to auto-create PRs",
                    severity="information",
                    timeout=5,
                )
                self.app._github_nudge_shown = True

        self.app.pop_screen()
        self.app.push_screen(DetailsScreen(dataset_id))

    @work(exclusive=True)
    async def create_pr(self, dataset_id: str, metadata: dict) -> None:
        """Create PR in background."""
        from mini_datahub.services.publish import PRWorkflow

        self.app.notify("Creating PR...", timeout=2)

        workflow = PRWorkflow()
        success, message, pr_url, pr_number = workflow.execute(metadata, dataset_id)

        if success and pr_url:
            self.app.notify(f"✓ PR #{pr_number} created!", timeout=5)
        elif success and message == "github_not_configured":
            # Fallback case (shouldn't reach here)
            pass
        else:
            self.app.notify(f"⚠ PR failed (saved to outbox): {message}", severity="warning", timeout=5)


class DataHubApp(App):
    """Main TUI application with Neovim-style keybindings."""

    # Track GitHub connection status
    github_connected = reactive(False)

    def on_mount(self) -> None:
        """Initialize the app."""
        # Initialize logging
        from mini_datahub.app.runtime import setup_logging, log_startup
        from mini_datahub import __version__
        from mini_datahub.app.settings import get_github_config

        config = get_github_config()
        setup_logging(debug=config.debug_logging)
        log_startup(__version__)

        # Load user configuration
        self._load_config()

        # Ensure database is set up
        try:
            ensure_database()

            # Check if we need to do initial indexing
            from mini_datahub.infra.index import reindex_all
            from mini_datahub.infra.store import list_datasets

            datasets = list_datasets()
            if datasets:
                # Reindex on startup to ensure consistency
                count, errors = reindex_all()
                if errors:
                    self.notify(f"Indexed {count} datasets with {len(errors)} errors", severity="warning", timeout=5)
        except Exception as e:
            self.notify(f"Database initialization error: {str(e)}", severity="error", timeout=10)

        # Check GitHub connection status
        self.check_github_connection()

        # Apply theme from config
        theme_name = self.config.get("theme.name", "gruvbox")
        self.theme = theme_name

        # Initialize autocomplete from catalog
        if config.suggest_from_catalog_values:
            from mini_datahub.services.autocomplete import refresh_autocomplete
            refresh_autocomplete()

        # Push home screen first
        self.push_screen(HomeScreen())

        # Check for updates (async) - after screen is mounted
        if config.auto_check_updates:
            self.check_for_updates_async()

        # Startup pull prompt (async) - after screen is mounted
        self.startup_pull_check()

    def check_github_connection(self) -> None:
        """Check GitHub connection status on startup."""
        from mini_datahub.app.settings import get_github_config
        from mini_datahub.infra.github_api import GitHubIntegration

        try:
            config = get_github_config()

            if not config.has_credentials():
                self.github_connected = False
                return

            # Test connection quickly
            github = GitHubIntegration(config)
            success, message = github.test_connection()
            self.github_connected = success

            if not success:
                # Subtle notification about disconnected state
                self.notify(f"GitHub: {message} (configure in Settings)", severity="warning", timeout=5)

        except Exception:
            self.github_connected = False

    def refresh_github_status(self) -> None:
        """Refresh GitHub connection status (called after settings save)."""
        self.check_github_connection()

        # Update home screen if it exists
        try:
            for screen in self.screen_stack:
                if isinstance(screen, HomeScreen):
                    screen.update_github_status()
        except Exception:
            pass

    @work(exclusive=True, thread=True)
    async def check_for_updates_async(self) -> None:
        """Check for updates asynchronously (background)."""
        from mini_datahub.services.update_check import check_for_updates, format_update_message

        update_info = check_for_updates(force=False)
        if update_info and update_info.get("has_update"):
            message = format_update_message(update_info)
            self.notify(message, severity="information", timeout=10)

    @work(exclusive=True, thread=True)
    async def startup_pull_check(self) -> None:
        """Check if we should prompt for pull on startup."""
        from mini_datahub.services.sync import get_auto_pull_manager
        from mini_datahub.services.state import get_state_manager
        from mini_datahub.app.settings import get_github_config
        from pathlib import Path
        import asyncio

        # Wait a bit for screen to be fully mounted
        await asyncio.sleep(0.5)

        state = get_state_manager()

        # Skip if user doesn't want prompts this session
        if not state.should_prompt_pull():
            return

        try:
            config = get_github_config()
            if not config.catalog_repo_path:
                return

            pull_manager = get_auto_pull_manager(Path(config.catalog_repo_path))

            # Quick network check
            if not pull_manager.check_network_available():
                return

            # Fetch to check if behind
            pull_manager.git_ops.fetch()

            is_behind, commits_behind = pull_manager.is_behind_remote()

            if is_behind:
                plural = "s" if commits_behind > 1 else ""

                # Find the HomeScreen and update its widgets
                try:
                    # Get the active screen (should be HomeScreen)
                    for screen in self.screen_stack:
                        if isinstance(screen, HomeScreen):
                            # Show status indicator below main banner
                            try:
                                update_status = screen.query_one("#update-status", Static)
                                update_status.update(
                                    f"[bold]⬇ {commits_behind} Update{plural} Available[/bold]  •  Press [bold]U[/bold] to pull updates"
                                )
                                update_status.remove_class("hidden")
                            except Exception:
                                pass
                            break
                except Exception:
                    pass

                # Show persistent notification (no timeout)
                self.notify(
                    f"⬇ {commits_behind} update{plural} available. Press [bold]U[/bold] to pull.",
                    severity="information"
                )
        except Exception:
            pass

    def _load_config(self) -> None:
        """Load and apply configuration settings."""
        try:
            self.config = get_config()
            # Config is now available for use throughout the app
            # Keybindings are already loaded when HomeScreen class is defined
            # Settings like search debounce, auto_sync, etc. can be accessed via self.config.get()
        except Exception as e:
            # Config system optional - app works without it
            self.config = None

    def apply_theme(self, theme_name: str) -> None:
        """
        Apply a theme dynamically without restart.

        Args:
            theme_name: Name of the theme to apply
        """
        try:
            # Reload config to pick up the latest changes
            from mini_datahub.services.config import reload_config
            self.config = reload_config()

            # Update the app's theme attribute (Textual built-in)
            self.theme = theme_name

            # Reload the theme manager to pick up new theme
            from mini_datahub.ui.theme import reload_theme
            reload_theme()

            # Refresh all screens to apply new theme
            self.refresh()

            # Force refresh of CSS variables if needed
            for screen in self.screen_stack:
                screen.refresh()

            self.notify(f"Theme '{theme_name}' applied successfully!", timeout=3)

        except Exception as e:
            self.notify(f"Failed to apply theme: {str(e)}", severity="error", timeout=5)

    def reload_keybindings(self) -> None:
        """
        Reload keybindings dynamically without restart.

        This recreates the HomeScreen with new bindings from the config file.
        """
        try:
            # Reload config to pick up the latest changes
            from mini_datahub.services.config import reload_config
            self.config = reload_config()

            # Check if we're currently on the HomeScreen
            is_on_home = isinstance(self.screen, HomeScreen)

            if is_on_home:
                # Pop the current HomeScreen and push a new one with updated bindings
                # This is necessary because BINDINGS is a class attribute set at definition time

                # First, we need to reload the HomeScreen class with new bindings
                # Since Python doesn't easily allow class redefinition, we'll use a workaround:
                # Create a new HomeScreen instance which will pick up the updated bindings

                # Store current state if needed (search text, etc.)
                old_screen = self.screen

                # Pop current home screen
                self.pop_screen()

                # Reload the module to pick up new bindings
                import importlib
                import mini_datahub.ui.views.home as home_module
                importlib.reload(home_module)

                # Push new home screen with updated bindings
                from mini_datahub.ui.views.home import HomeScreen as NewHomeScreen
                self.push_screen(NewHomeScreen())

                self.notify("Keybindings reloaded successfully!", timeout=3)
            else:
                # Not on home screen, just notify that changes will apply on next visit
                self.notify(
                    "Keybindings updated! Changes will apply when you return to home screen.",
                    timeout=5
                )

        except Exception as e:
            self.notify(f"Failed to reload keybindings: {str(e)}", severity="error", timeout=5)

    @work(exclusive=True, thread=True)
    async def pull_updates(self) -> None:
        """Pull updates from catalog repository."""
        from mini_datahub.services.sync import get_auto_pull_manager
        from mini_datahub.app.runtime import log_pull_update, log_reindex
        from mini_datahub.infra.index import reindex_all
        from mini_datahub.app.settings import get_github_config
        from pathlib import Path

        try:
            config = get_github_config()
            if not config.catalog_repo_path:
                self.notify("Catalog path not configured", severity="error", timeout=5)
                return

            pull_manager = get_auto_pull_manager(Path(config.catalog_repo_path))

            # Check network
            if not pull_manager.check_network_available():
                self.notify("No network connection", severity="warning", timeout=5)
                return

            # Note: Local changes check removed - pull_updates() now handles via auto-stash

            # Check divergence
            is_diverged, ahead, behind = pull_manager.is_diverged()
            if is_diverged:
                self.notify(
                    "Cannot pull: Local branch has diverged from remote",
                    severity="error",
                    timeout=7
                )
                return

            # Fetch first
            self.notify("Fetching updates...", timeout=3)
            pull_manager.git_ops.fetch()

            # Check if actually behind
            is_behind, commits_behind = pull_manager.is_behind_remote()
            if not is_behind:
                self.notify("Already up to date", timeout=3)
                return

            # Pull
            self.notify("Pulling updates...", timeout=3)
            success, message, old_commit, new_commit = pull_manager.pull_updates(
                branch="main",
                from_remote=True,   # Pull from REMOTE origin/main
                allow_merge=True,   # Allow merge commits (handles divergence)
                auto_stash=True     # Auto-stash uncommitted changes
            )

            if not success:
                self.notify(f"Pull failed: {message}", severity="error", timeout=7)
                log_pull_update(success=False, error=message)
                return

            # Hide update status after successful pull
            try:
                for screen in self.screen_stack:
                    if isinstance(screen, HomeScreen):
                        try:
                            update_status = screen.query_one("#update-status", Static)
                            update_status.add_class("hidden")
                        except Exception:
                            pass
                        break
            except Exception:
                pass

            # Check for metadata changes
            if old_commit and new_commit and old_commit != new_commit:
                has_metadata, metadata_count = pull_manager.has_metadata_changes(old_commit, new_commit)
                if has_metadata:
                    self.notify("Reindexing datasets...", timeout=3)
                    dataset_count, errors = reindex_all()

                    if errors:
                        self.notify(
                            f"Pull complete. Reindexed {dataset_count} datasets with {len(errors)} errors",
                            severity="warning",
                            timeout=7
                        )
                        log_reindex(success=False, datasets_count=dataset_count, error=f"{len(errors)} errors")
                    else:
                        self.notify(
                            f"Pull complete. Reindexed {dataset_count} datasets",
                            severity="information",
                            timeout=5
                        )
                        log_reindex(success=True, datasets_count=dataset_count)

                    log_pull_update(success=True, files_changed=metadata_count)
                else:
                    self.notify("Pull complete (no metadata changes)", timeout=5)
                    log_pull_update(success=True, files_changed=0)
            else:
                self.notify("Pull complete (already up to date)", timeout=5)
                log_pull_update(success=True, files_changed=0)

        except Exception as e:
            self.notify(f"Pull failed: {str(e)}", severity="error", timeout=7)
            log_pull_update(success=False, error=str(e))


def run_tui():
    """Launch the TUI application."""
    app = DataHubApp()
    app.run()
