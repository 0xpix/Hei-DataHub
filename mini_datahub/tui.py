"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import webbrowser
from datetime import date
from typing import Optional

import pyperclip
import requests
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

from mini_datahub.index import (
    ensure_database,
    get_dataset_by_id,
    search_datasets,
    upsert_dataset,
    list_all_datasets,
)
from mini_datahub.storage import (
    generate_unique_id,
    save_dataset,
    validate_metadata,
)


class HomeScreen(Screen):
    """Main screen with search functionality and Neovim-style navigation."""

    BINDINGS = [
        Binding("a", "add_dataset", "Add Dataset", key_display="A"),
        Binding("q", "quit", "Quit"),
        Binding("enter", "open_details", "View Details"),
        Binding("o", "open_details", "Open", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("g", "jump_top", "Top", key_display="gg", show=False),
        Binding("G", "jump_bottom", "Bottom", show=False),
        Binding("/", "focus_search", "Search", show=False),
        Binding("escape", "clear_search", "Clear", show=False),
        Binding("?", "show_help", "Help"),
    ]

    search_mode = reactive(False)
    _debounce_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🔍 Search Datasets  |  Mode: [bold cyan]Normal[/bold cyan]", id="mode-indicator"),
            Input(placeholder="Type / to search, j/k to navigate, Enter to open...", id="search-input"),
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

        # Load all datasets initially
        self.load_all_datasets()

    def load_all_datasets(self) -> None:
        """Load and display all available datasets."""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        try:
            results = list_all_datasets()
            label = self.query_one("#results-label", Label)
            label.update(f"All Datasets ({len(results)} total)")

            for result in results:
                # Clean snippet of HTML tags for display
                snippet = result["snippet"].replace("<b>", "").replace("</b>", "")
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

        # Set new timer for debounced search
        self._debounce_timer = self.set_timer(0.15, lambda: self.perform_search(event.value))

    def perform_search(self, query: str) -> None:
        """Execute search and update results table."""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        # If query is empty or very short, show all datasets
        if not query.strip() or len(query.strip()) < 2:
            self.load_all_datasets()
            return

        try:
            results = search_datasets(query)
            label = self.query_one("#results-label", Label)
            label.update(f"Search Results ({len(results)} found)")

            if not results:
                label.update(f"No results for '{query}'")
                return

            for result in results:
                # Clean snippet of HTML tags for display
                snippet = result["snippet"].replace("<b>", "").replace("</b>", "")
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

    def action_focus_search(self) -> None:
        """Focus search input and enter insert mode."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
        self.search_mode = True

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
        """Show help overlay."""
        self.app.push_screen(HelpScreen())


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
        ("y", "copy_source", "Copy Source"),
        ("o", "open_url", "Open URL"),
    ]

    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id
        self.metadata = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label(f"Dataset: {self.dataset_id}", classes="title"),
            Static(id="details-content"),
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

        except Exception as e:
            self.app.notify(f"Error loading details: {str(e)}", severity="error", timeout=5)

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


class AddDataScreen(Screen):
    """Screen to add a new dataset with scrolling support and Neovim keys."""

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

        # Save to disk
        success, msg = save_dataset(metadata)
        if not success:
            error_label.update(f"[red]{msg}[/red]")
            return

        # Upsert to index
        try:
            upsert_dataset(dataset_id, metadata)
        except Exception as e:
            self.app.notify(f"Warning: Failed to index dataset: {str(e)}", severity="warning", timeout=5)

        # Success! Navigate to details
        self.app.notify(f"Dataset '{dataset_id}' saved successfully!", timeout=3)
        self.app.pop_screen()
        self.app.push_screen(DetailsScreen(dataset_id))


class DataHubApp(App):
    """Main TUI application with Neovim-style keybindings."""

    CSS = """
    #mode-indicator {
        text-align: center;
        padding: 1 0;
        background: $panel;
    }

    .title {
        text-align: center;
        text-style: bold;
        padding: 1;
        background: $primary;
    }

    #search-container {
        height: 100%;
        padding: 1;
    }

    #results-label {
        padding: 1 0;
        text-style: bold;
    }

    #results-table {
        height: 1fr;
        margin-top: 1;
    }

    #details-container {
        height: 100%;
        padding: 1;
    }

    #details-content {
        padding: 1;
    }

    #add-data-scroll {
        height: 100%;
        overflow-y: auto;
        scrollbar-size: 1 1;
    }

    #form-container {
        padding: 1;
        padding-bottom: 3;
        height: auto;
        min-height: 100%;
    }

    #form-container Label {
        margin-top: 1;
    }

    #form-container Input,
    #form-container TextArea {
        margin-bottom: 1;
    }

    #form-container TextArea {
        height: 5;
    }

    #form-container Button {
        margin: 1 1 2 0;
    }

    #form-container Horizontal {
        margin-bottom: 2;
    }

    #error-message {
        color: $error;
        margin-top: 1;
        margin-bottom: 2;
    }

    #probe-status {
        margin-left: 1;
        align: center middle;
    }

    #help-content {
        padding: 2;
    }
    """

    def on_mount(self) -> None:
        """Initialize the app."""
        # Ensure database is set up
        try:
            ensure_database()

            # Check if we need to do initial indexing
            from mini_datahub.index import reindex_all
            from mini_datahub.storage import list_datasets

            datasets = list_datasets()
            if datasets:
                # Reindex on startup to ensure consistency
                count, errors = reindex_all()
                if errors:
                    self.notify(f"Indexed {count} datasets with {len(errors)} errors", severity="warning", timeout=5)
        except Exception as e:
            self.notify(f"Database initialization error: {str(e)}", severity="error", timeout=10)

        # Push home screen
        self.push_screen(HomeScreen())


def run_tui():
    """Launch the TUI application."""
    app = DataHubApp()
    app.run()
