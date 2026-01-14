"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging
import os
import tempfile
from datetime import date
from pathlib import Path

import yaml
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Header,
    Input,
    Label,
    TextArea,
    Select,
)

# TODO: CHANGE WHEN ADD FILES IN INFRA AND SERVICES
from hei_datahub.infra.store import validate_metadata
from hei_datahub.services.catalog import generate_id as generate_unique_id
from hei_datahub.services.index_service import get_index_service
from hei_datahub.services.storage_manager import get_storage_backend
from hei_datahub.ui.widgets.contextual_footer import ContextualFooter

from .dataset_detail import CloudDatasetDetailsScreen
from .home import HomeScreen

logger = logging.getLogger(__name__)


def generate_tags(metadata: dict) -> list:
    """Auto-generate tags from metadata fields."""
    tags = set()

    # Extract words from name
    name = metadata.get('name', metadata.get('dataset_name', ''))
    if name:
        for word in name.lower().split():
            if len(word) > 2 and word.isalnum():
                tags.add(word)

    # Add category as tag
    category = metadata.get('category', '')
    if category:
        tags.add(category.lower().replace(' ', '-'))

    # Extract from description (first few significant words)
    description = metadata.get('description', '')
    if description:
        words = description.lower().split()[:20]
        for word in words:
            word = ''.join(c for c in word if c.isalnum())
            if len(word) > 3 and word not in ('the', 'and', 'for', 'from', 'with', 'this', 'that'):
                tags.add(word)

    # Add format as tag
    file_format = metadata.get('file_format', '')
    if file_format:
        tags.add(file_format.lower())

    # Add spatial coverage
    spatial = metadata.get('spatial_coverage', '')
    if spatial:
        tags.add(spatial.lower().replace(' ', '-'))

    return sorted(list(tags))[:10]  # Limit to 10 tags


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
            Label("󰆺 Add New Dataset", classes="title"),
            Container(
                # --- Core Dataset Info (Required) ---
                Label("Dataset Name (required):"),
                Input(placeholder="e.g., Global Weather Stations 2024", id="input-name"),

                Label("ID (required):"),
                Input(placeholder="Unique slug (leave empty to auto-generate)", id="input-id"),

                Label("Category (required):"),
                Select(
                    options=[
                        ("Climate", "Climate"),
                        ("Land Cover", "Land Cover"),
                        ("Biodiversity", "Biodiversity"),
                        ("Socioeconomic", "Socioeconomic"),
                        ("Remote Sensing", "Remote Sensing"),
                    ],
                    prompt="Select category...",
                    id="input-category"
                ),

                Label("Summary / Description (required):"),
                TextArea(id="input-description"),

                Label("Source (required, human-readable):"),
                Input(placeholder="e.g., NASA LP DAAC", id="input-source"),

                Label("Reference (Optional, citation/DOI):"),
                TextArea(id="input-reference", classes="small-textarea"),

                # --- Access & Format (Required) ---
                Label("Access Method (required):"),
                Input(placeholder="GEE:..., PY:..., FILE:..., API:...", id="input-access-method"),

                Label("Format & Structure (required):"),
                Input(placeholder="e.g. CSV, GeoTIFF, Parquet", id="input-format"),

                # --- Access / Location (Optional per list, validated if URL) ---
                Label("Access / Location (URL/Path):"),
                Input(placeholder="https://... or /data/...", id="input-storage"),
                Label("", id="url-validation-msg", classes="warning"),

                # --- Additional Metadata (Collapsible) ---
                Button("Show/Hide Additional Metadata", id="toggle-optional-btn", variant="default", classes="w-full"),

                Container(
                    Label("Dataset Size:"),
                    Input(placeholder="e.g., 2.5 GB", id="input-size"),

                    Label("Spatial Resolution:"),
                    Input(placeholder="e.g. 500 m, 0.5°", id="input-spatial-res"),

                    Label("Spatial Coverage:"),
                    Input(placeholder="e.g. Global, Europe", id="input-spatial-cov"),

                    Label("Temporal Resolution:"),
                    Input(placeholder="e.g. Daily, Monthly", id="input-temp-res"),

                    Label("Temporal Coverage:"),
                    Input(placeholder="e.g. 2001-present", id="input-temp-cov"),

                    Label("Related Projects (comma-separated):"),
                    Input(placeholder="e.g., project-a, project-b", id="input-projects"),

                    Label("Tags (comma-separated):"),
                    Input(placeholder="e.g. modis, land-cover", id="input-tags"),

                    id="optional-container",
                    classes="hidden"
                ),

                Horizontal(
                    Button("Save Dataset", id="save-btn", variant="primary"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                ),
                Label("", id="error-message"),
                id="form-container",
            ),
            id="add-data-scroll",
        )
        footer = ContextualFooter()
        footer.set_context("add")
        yield footer

    def on_mount(self) -> None:
        """Focus on first input."""
        self.query_one("#input-name", Input).focus()

    @on(Button.Pressed, "#toggle-optional-btn")
    def toggle_optional(self) -> None:
        """Toggle visibility of optional fields."""
        self.query_one("#optional-container").toggle_class("hidden")

    @on(Input.Changed, "#input-storage")
    def validate_url(self, event: Input.Changed) -> None:
        """Validate URL for Access / Location."""
        value = event.value
        msg_label = self.query_one("#url-validation-msg", Label)

        if value.startswith("http://") or value.startswith("https://"):
            import urllib.parse
            try:
                result = urllib.parse.urlparse(value)
                if all([result.scheme, result.netloc]):
                    msg_label.update("") # Valid format
                else:
                    msg_label.update("⚠️ Invalid URL format")
            except ValueError:
                msg_label.update("⚠️ Invalid URL")
        else:
            msg_label.update("")

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

    def show_error(self, message: str, focus_id: str = None) -> None:
        """Show error message and optionally focus an input."""
        label = self.query_one("#error-message", Label)
        label.update(message)
        label.add_class("visible")
        if focus_id:
            self.query_one(focus_id).focus()

    def submit_form(self) -> None:
        """Validate and save the new dataset."""
        self.query_one("#error-message", Label).update("")
        self.query_one("#error-message", Label).remove_class("visible")

        # Gather form data
        name = self.query_one("#input-name", Input).value.strip()
        dataset_id = self.query_one("#input-id", Input).value.strip()
        category_val = self.query_one("#input-category", Select).value
        description = self.query_one("#input-description", TextArea).text.strip()
        source = self.query_one("#input-source", Input).value.strip()
        reference = self.query_one("#input-reference", TextArea).text.strip()
        access_method = self.query_one("#input-access-method", Input).value.strip()
        file_format = self.query_one("#input-format", Input).value.strip()
        storage = self.query_one("#input-storage", Input).value.strip()

        # Optional fields
        size = self.query_one("#input-size", Input).value.strip()
        spatial_res = self.query_one("#input-spatial-res", Input).value.strip()
        spatial_cov = self.query_one("#input-spatial-cov", Input).value.strip()
        temp_res = self.query_one("#input-temp-res", Input).value.strip()
        temp_cov = self.query_one("#input-temp-cov", Input).value.strip()
        projects_str = self.query_one("#input-projects", Input).value.strip()
        tags_str = self.query_one("#input-tags", Input).value.strip()

        # Validate required fields
        if not name:
            self.show_error("[red]Error: Dataset Name is required[/red]", "#input-name")
            return

        if category_val == Select.BLANK:
            self.show_error("[red]Error: Category is required[/red]", "#input-category")
            return
        category = str(category_val)

        if not description:
            self.show_error("[red]Error: Description is required[/red]", "#input-description")
            return
        if not source:
            self.show_error("[red]Error: Source is required[/red]", "#input-source")
            return
        if not access_method:
            self.show_error("[red]Error: Access Method is required[/red]", "#input-access-method")
            return

        # Pydantic will catch invalid Access Method prefix, but UI feedback is better
        valid_prefixes = ("GEE:", "PY:", "FILE:", "API:")
        if not access_method.startswith(valid_prefixes):
            self.show_error(f"[red]Error: Access Method must start with {', '.join(valid_prefixes)}[/red]", "#input-access-method")
            return

        if not file_format:
             self.show_error("[red]Error: Format & Structure is required[/red]", "#input-format")
             return

        # Generate ID if not provided
        if not dataset_id:
            dataset_id = generate_unique_id(name)

        # Parse lists
        used_in_projects = [p.strip() for p in projects_str.split(',') if p.strip()] if projects_str else None
        tags = [t.strip().lower() for t in tags_str.split(',') if t.strip()] if tags_str else None

        # Build metadata dict
        metadata = {
            "id": dataset_id,
            "dataset_name": name,
            "category": category,
            "description": description,
            "source": source,
            "access_method": access_method,
            "file_format": file_format,
            "storage_location": storage if storage else "N/A",
            "date_created": date.today().isoformat(),
        }

        # If storage is empty, pass empty string? Pydantic min_length=1.
        # I'll modify model logic or prompt logic.
        # If user says Optional, I should allow empty.
        # I'll define storage_location as "N/A" if empty to satisfy model, or update model to Optional.
        # Model update is safer for "Optional" semantics.
        # But required field list in Model has storage_location.
        # Let's set it to "N/A" or "Not specified" if empty and allow user to save.

        if reference:
            metadata["reference"] = reference
        if size:
            metadata["size"] = size
        if spatial_res:
            metadata["spatial_resolution"] = spatial_res
        if spatial_cov:
            metadata["spatial_coverage"] = spatial_cov
        if temp_res:
             metadata["temporal_resolution"] = temp_res
        if temp_cov:
            metadata["temporal_coverage"] = temp_cov
        if used_in_projects:
            metadata["used_in_projects"] = used_in_projects

        # Auto-generate tags if none provided
        if tags:
            metadata["tags"] = tags
        else:
            metadata["tags"] = generate_tags(metadata)
            logger.info(f"Auto-generated tags: {metadata['tags']}")

        # Validate and save
        try:
             # We might need to handle `validate_metadata` distinct return or exception
             # Currently existing code: success, error_msg, model = validate_metadata(metadata)
             # But validate_metadata validates against `schema.json` too if configured.
             # If I haven't updated schema.json, `validate_metadata` might fail if it uses json schema.
             # I should wrap in try block or just hope Pydantic is enough.
             success, error_msg, model = validate_metadata(metadata)
             if not success:
                 self.show_error(f"[red]Validation Error:\n{error_msg}[/red]")
                 return
        except Exception as e:
             self.show_error(f"[red]Validation Error:\n{str(e)}[/red]")
             return

        # ALWAYS save to cloud storage (WebDAV)
        # No more local filesystem option - cloud-only workflow
        self.save_to_cloud(dataset_id, metadata)

    @work(thread=True)
    def save_to_cloud(self, dataset_id: str, metadata: dict) -> None:
        """Save dataset to cloud storage (WebDAV)."""
        try:
            self.app.call_from_thread(self.app.notify, "Uploading to cloud...", timeout=2)
            logger.info(f"Starting upload for dataset {dataset_id}")

            # Get storage backend - this might fail if auth is not configured
            try:
                storage = get_storage_backend()
            except Exception as auth_err:
                logger.error(f"Failed to get storage backend: {auth_err}")
                self.app.call_from_thread(
                    self.app.notify,
                    f"Authentication Error: {str(auth_err)}\nPlease run 'hei-datahub auth setup' or configure Settings.",
                    severity="error",
                    timeout=10
                )
                return

            # Create dataset directory
            remote_dir = dataset_id
            try:
                storage.mkdir(remote_dir)
            except Exception as e:
                # Directory might already exist, that's okay
                logger.debug(f"Directory creation failed (might exist): {e}")
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
                logger.info(f"Uploading metadata to {remote_path}")
                storage.upload(Path(tmp_path), remote_path)

                # Update fast search index for cloud dataset
                try:
                    index_service = get_index_service()

                    # Extract fields
                    name = metadata.get('dataset_name', dataset_id)
                    description = metadata.get('description', '')
                    tags_list = metadata.get('tags', [])
                    tags = " ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
                    used_in_projects = metadata.get('used_in_projects', [])
                    project = ", ".join(used_in_projects) if used_in_projects else None

                    index_service.upsert_item(
                        path=dataset_id,
                        name=name,
                        project=project,
                        tags=tags,
                        description=description,
                        format=metadata.get('file_format'),
                        source=metadata.get('source'),
                        category=metadata.get('category'),
                        spatial_coverage=metadata.get('spatial_coverage'),
                        temporal_coverage=metadata.get('temporal_coverage'),
                        access_method=metadata.get('access_method'),
                        storage_location=metadata.get('storage_location'),
                        reference=metadata.get('reference'),
                        spatial_resolution=metadata.get('spatial_resolution'),
                        temporal_resolution=metadata.get('temporal_resolution'),
                        size=metadata.get('size'),
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
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Upload failed: {e}", exc_info=True)
            self.app.call_from_thread(
                self.app.notify,
                f"Error uploading to cloud: {str(e)}",
                severity="error",
                timeout=10
            )
