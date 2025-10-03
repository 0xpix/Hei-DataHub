"""
TUI application using Textual framework.
"""
import webbrowser
from datetime import date
from typing import Optional

import pyperclip
import requests
from textual import on, work
from textual.app import App, ComposeResult
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

from mini_datahub.index import ensure_database, get_dataset_by_id, search_datasets, upsert_dataset
from mini_datahub.storage import (
    generate_unique_id,
    save_dataset,
    validate_metadata,
)


class HomeScreen(Screen):
    """Main screen with search functionality."""

    BINDINGS = [
        ("a", "add_dataset", "Add Dataset"),
        ("q", "quit", "Quit"),
        ("enter", "open_details", "View Details"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("🔍 Search Datasets", classes="title"),
            Input(placeholder="Type to search datasets...", id="search-input"),
            DataTable(id="results-table"),
            id="search-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when mounted."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("ID", "Name", "Description Snippet")
        table.cursor_type = "row"

        # Focus on search input
        self.query_one("#search-input", Input).focus()

    @on(Input.Changed, "#search-input")
    def on_search_input(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.perform_search(event.value)

    def perform_search(self, query: str) -> None:
        """Execute search and update results table."""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        if not query.strip():
            return

        try:
            results = search_datasets(query)
            for result in results:
                # Clean snippet of HTML tags for display
                snippet = result["snippet"].replace("<b>", "").replace("</b>", "")
                snippet = snippet[:100] + "..." if len(snippet) > 100 else snippet

                table.add_row(
                    result["id"],
                    result["name"],
                    snippet,
                    key=result["id"],
                )
        except Exception as e:
            self.app.notify(f"Search error: {str(e)}", severity="error", timeout=5)

    def action_add_dataset(self) -> None:
        """Navigate to Add Dataset screen."""
        self.app.push_screen(AddDataScreen())

    def action_open_details(self) -> None:
        """Open details for selected dataset."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.cursor_row < table.row_count:
            row_key = table.get_row_key_at(table.cursor_row)
            dataset_id = str(row_key)
            self.app.push_screen(DetailsScreen(dataset_id))

    @on(DataTable.RowSelected, "#results-table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in results table."""
        dataset_id = str(event.row_key)
        self.app.push_screen(DetailsScreen(dataset_id))


class DetailsScreen(Screen):
    """Screen to view dataset details."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("b", "back", "Back"),
        ("c", "copy_source", "Copy Source"),
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
        """Copy source to clipboard."""
        if self.metadata and self.metadata.get('source'):
            try:
                pyperclip.copy(self.metadata['source'])
                self.app.notify("Source copied to clipboard!", timeout=2)
            except Exception as e:
                self.app.notify(f"Failed to copy: {str(e)}", severity="error", timeout=3)

    def action_open_url(self) -> None:
        """Open source URL in browser if it's a URL."""
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
    """Screen to add a new dataset."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "submit", "Save Dataset"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("➕ Add New Dataset", classes="title"),
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
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus on first input."""
        self.query_one("#input-name", Input).focus()

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
            return
        if not description:
            error_label.update("[red]Error: Description is required[/red]")
            return
        if not source:
            error_label.update("[red]Error: Source is required[/red]")
            return
        if not storage:
            error_label.update("[red]Error: Storage Location is required[/red]")
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
    """Main TUI application."""

    CSS = """
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

    #form-container {
        padding: 1;
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
        margin: 1 1 1 0;
    }

    #error-message {
        color: $error;
        margin-top: 1;
    }

    #probe-status {
        margin-left: 1;
        align: center middle;
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
