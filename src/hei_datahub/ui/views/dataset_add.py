"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import os
import yaml
import logging
import tempfile
from pathlib import Path
from datetime import date

logger = logging.getLogger(__name__)
from textual import on, work
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    TextArea,
)

from .dataset_detail import CloudDatasetDetailsScreen
from .home import HomeScreen

# TODO: CHANGE WHEN ADD FILES IN INFRA AND SERVICES
from mini_datahub.infra.store import validate_metadata
from mini_datahub.services.catalog import generate_id as generate_unique_id
from mini_datahub.services.storage_manager import get_storage_backend
from mini_datahub.services.index_service import get_index_service

class AddDataScreen(Screen):
    """Screen to add a new dataset with scrolling support and Neovim keys."""

    CSS_PATH = "../styles/dataset_add.tcss"

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "submit", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("➕ Add New Dataset  |  [italic]Ctrl+S to save, Esc to cancel[/italic]", classes="title"),
            Container(
                Label("Dataset Name (required):"),
                Input(placeholder="e.g., Global Weather Stations 2024", id="input-name"),
                Label("Description (required):"),
                TextArea(id="input-description"),
                Label("Source URL or snippet (required):"),
                Input(placeholder="e.g., https://example.com/data.csv", id="input-source"),
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

        # ALWAYS save to cloud storage (WebDAV)
        # No more local filesystem option - cloud-only workflow
        self.save_to_cloud(dataset_id, metadata)

    @work(thread=True)
    def save_to_cloud(self, dataset_id: str, metadata: dict) -> None:
        """Save dataset to cloud storage (WebDAV)."""
        try:
            self.app.call_from_thread(self.app.notify, "Uploading to cloud...", timeout=2)
            storage = get_storage_backend()

            # Create dataset directory
            remote_dir = dataset_id
            try:
                storage.mkdir(remote_dir)
            except Exception as e:
                # Directory might already exist, that's okay
                pass

            # Create metadata.yaml in temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as tmp:
                # Convert metadata to YAML-friendly format
                yaml_metadata = {}
                for key, value in metadata.items():
                    # Convert dataset_name to name for consistency
                    if key == 'dataset_name':
                        yaml_metadata['name'] = value
                    elif key != 'id':  # Skip id field, it's implicit from directory name
                        yaml_metadata[key] = value

                yaml.dump(yaml_metadata, tmp, sort_keys=False, allow_unicode=True)
                tmp_path = tmp.name

            try:
                # Upload metadata.yaml
                remote_path = f"{dataset_id}/metadata.yaml"
                storage.upload(Path(tmp_path), remote_path)

                # Update fast search index for cloud dataset
                try:
                    index_service = get_index_service()

                    # Extract fields
                    name = metadata.get('dataset_name', dataset_id)
                    description = metadata.get('description', '')
                    keywords = metadata.get('keywords', [])
                    tags = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
                    used_in_projects = metadata.get('used_in_projects', [])
                    project = used_in_projects[0] if used_in_projects else None

                    index_service.upsert_item(
                        path=dataset_id,
                        name=name,
                        project=project,
                        tags=tags,
                        description=description,
                        format=metadata.get('file_format'),
                        source=metadata.get('source'),
                        is_remote=True,  # This is a cloud dataset
                    )
                except Exception as idx_err:
                    # Don't fail upload if index update fails
                    logger.warning(f"Failed to update search index: {idx_err}")

                self.app.call_from_thread(
                    self.app.notify,
                    f"✓ Dataset '{dataset_id}' uploaded to cloud!",
                    timeout=5
                )

                # Close form and show details
                self.app.call_from_thread(self.app.pop_screen)
                self.app.call_from_thread(self.app.push_screen, CloudDatasetDetailsScreen(dataset_id))

                # Refresh the HomeScreen table to show new dataset
                def refresh_home():
                    for screen in self.app.screen_stack:
                        if isinstance(screen, HomeScreen):
                            logger.info("Refreshing HomeScreen table with new dataset (force refresh)")
                            screen.load_all_datasets(force_refresh=True)
                            break

                self.app.call_from_thread(refresh_home)

            finally:
                # Cleanup temp file
                os.unlink(tmp_path)

        except Exception as e:
            self.app.call_from_thread(
                self.app.notify,
                f"Error uploading to cloud: {str(e)}",
                severity="error",
                timeout=5
            )
            import traceback
            traceback.print_exc()
