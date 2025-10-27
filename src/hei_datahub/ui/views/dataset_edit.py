"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Button,
    Header,
    Input,
    Label,
    Static,
    TextArea,
)

from hei_datahub.ui.views.dataset_detail import CloudDatasetDetailsScreen

class CloudEditDetailsScreen(Screen):
    """Screen for editing cloud dataset metadata with WebDAV storage."""

    CSS_PATH = "../styles/dataset_edit.tcss"

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

        # Track previous field values for undo
        self._previous_values = {}

        self._dirty_fields = set()
        self._field_errors = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label(f"󱘫 Editing Dataset: {self.dataset_id}", classes="title"),
            Container(
                Static(id="edit-status", classes="edit-status"),

                Label("Dataset Name:"),
                Input(value=self.metadata.get('dataset_name', self.metadata.get('name', '')), id="edit-name"),
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
                Input(value=str(self.metadata.get('file_format', '')), id="edit-format"),
                Static(id="error-format", classes="field-error"),

                Label("Size:"),
                Input(value=str(self.metadata.get('size', '')), id="edit-size"),
                Static(id="error-size", classes="field-error"),

                Label("Keywords (comma-separated):"),
                Input(value=', '.join(self.metadata.get('keywords', [])) if isinstance(self.metadata.get('keywords'), list) else str(self.metadata.get('keywords', '')), id="edit-keywords"),
                Static(id="error-keywords", classes="field-error"),

                Label("License:"),
                Input(value=str(self.metadata.get('license', '')), id="edit-license"),
                Static(id="error-license", classes="field-error"),

                Horizontal(
                    Button("Save Dataset", id="save-btn", variant="primary"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                ),
                Label("", id="error-message"),
                id="edit-form-container",
            ),
            id="edit-scroll",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize field values after mounting."""
        # Pre-populate previous values to prevent false dirty marking
        self._previous_values = {
            'name': self.metadata.get('dataset_name', self.metadata.get('name', '')),
            'description': self.metadata.get('description', ''),
            'source': self.metadata.get('source', ''),
            'storage': self.metadata.get('storage_location', ''),
            'date': str(self.metadata.get('date_created', '')),
            'format': str(self.metadata.get('file_format', '')),
            'size': str(self.metadata.get('size', '')),
            'keywords': ', '.join(self.metadata.get('keywords', [])) if isinstance(self.metadata.get('keywords'), list) else str(self.metadata.get('keywords', '')),
            'license': str(self.metadata.get('license', '')),
        }

        desc_area = self.query_one("#edit-description", TextArea)
        desc_area.text = self.metadata.get('description', '')
        self.query_one("#edit-name", Input).focus()
        self._update_status()

    @on(Button.Pressed, "#save-btn")
    def on_save_button_pressed(self) -> None:
        """Handle Save button click."""
        self.action_save_edits()

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_button_pressed(self) -> None:
        """Handle Cancel button click."""
        self.action_cancel_edits()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        """Track field changes and mark as dirty."""
        if not event.input.id or not event.input.id.startswith('edit-'):
            return

        field_name = event.input.id.replace('edit-', '')
        new_value = event.value

        # Get previous value from cache or metadata
        if field_name not in self._previous_values:
            # First time changing this field
            self._previous_values[field_name] = self._get_field_value(field_name)

        old_value = self._previous_values[field_name]

        # Only track if actually changed from previous value
        if old_value != new_value:
            # Push to undo stack
            self._push_undo(field_name, old_value, new_value)

            # Update cache with new value
            self._previous_values[field_name] = new_value

            # Update metadata
            self._update_metadata_from_field(field_name, new_value)
            self._mark_dirty(field_name)
            self._update_status()

    @on(TextArea.Changed, "#edit-description")
    def on_textarea_changed(self, event: TextArea.Changed) -> None:
        """Track TextArea changes."""
        field_name = 'description'
        new_value = event.text_area.text

        # Get previous value from cache or metadata
        if field_name not in self._previous_values:
            # First time changing this field
            self._previous_values[field_name] = self.metadata.get(field_name, '')

        old_value = self._previous_values[field_name]

        # Only track if actually changed from previous value
        if old_value != new_value:
            # Push to undo stack
            self._push_undo(field_name, old_value, new_value)

            # Update cache with new value
            self._previous_values[field_name] = new_value

            # Update metadata
            self.metadata[field_name] = new_value
            self._mark_dirty(field_name)
            self._update_status()

    def _update_metadata_from_field(self, field_name: str, value: str) -> None:
        """Update metadata dict from field value."""
        field_map = {
            'name': 'name',  # Cloud uses 'name' not 'dataset_name'
            'description': 'description',
            'source': 'source',
            'storage': 'storage_location',
            'date': 'date_created',
            'format': 'file_format',
            'size': 'size',
            'keywords': 'keywords',
            'license': 'license',
        }

        meta_field = field_map.get(field_name, field_name)

        # Handle list fields
        if field_name in ('keywords',):
            if value.strip():
                self.metadata[meta_field] = [v.strip() for v in value.split(',') if v.strip()]
            else:
                self.metadata[meta_field] = []
        else:
            self.metadata[meta_field] = value

        # Also update dataset_name for compatibility
        if field_name == 'name':
            self.metadata['dataset_name'] = value

    def _mark_dirty(self, field_name: str) -> None:
        """Mark a field as modified."""
        self._dirty_fields.add(field_name)

    def _get_field_value(self, field_name: str) -> Any:
        """Get current field value from metadata."""
        field_map = {
            'name': 'name',
            'description': 'description',
            'source': 'source',
            'storage': 'storage_location',
            'date': 'date_created',
            'format': 'file_format',
            'size': 'size',
            'keywords': 'keywords',
            'license': 'license',
        }

        meta_field = field_map.get(field_name, field_name)
        value = self.metadata.get(meta_field, '')

        # Handle list fields
        if field_name == 'keywords' and isinstance(value, list):
            return ', '.join(value)

        return str(value) if value else ''

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
        """Save changes to cloud storage (Ctrl+S)."""
        # Basic validation
        if not self.metadata.get('name') and not self.metadata.get('dataset_name'):
            self.app.notify("Dataset name is required", severity="error", timeout=3)
            return

        if not self.metadata.get('description'):
            self.app.notify("Description is required", severity="error", timeout=3)
            return

        # Save to cloud
        self.save_to_cloud()

    @work(thread=True)
    def save_to_cloud(self) -> None:
        """Save dataset to cloud storage (WebDAV)."""
        try:
            from hei_datahub.services.storage_manager import get_storage_backend
            import yaml
            import tempfile
            import os

            self.app.call_from_thread(self.app.notify, "Uploading changes to cloud...", timeout=2)

            storage = get_storage_backend()

            logger.info(f"CloudEditDetailsScreen: Saving {self.dataset_id} to cloud")
            logger.debug(f"Metadata to save: {self.metadata}")

            # Create metadata.yaml in temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as tmp:
                # Convert metadata to cloud YAML format
                yaml_metadata = {}
                for key, value in self.metadata.items():
                    # Use 'name' instead of 'dataset_name' for cloud
                    if key == 'dataset_name':
                        yaml_metadata['name'] = value
                        logger.debug(f"Converting dataset_name '{value}' to name field")
                    elif key != 'id':  # Skip id field
                        yaml_metadata[key] = value

                yaml.dump(yaml_metadata, tmp, sort_keys=False, allow_unicode=True)
                tmp_path = tmp.name
                logger.debug(f"Created temp file: {tmp_path}")

            try:
                # Check if name changed - rename the folder on HeiBox to match
                new_name = self.metadata.get('dataset_name') or self.metadata.get('name')
                old_folder_path = self.dataset_id

                # Folder rename: if name changed, rename folder to match the new name
                if new_name and new_name != old_folder_path:
                    logger.info(f"Name changed to '{new_name}' - renaming folder from '{old_folder_path}'")

                    try:
                        # Rename the folder on HeiBox
                        storage.move(old_folder_path, new_name)
                        logger.info(f"✓ Renamed folder from '{old_folder_path}' to '{new_name}'")
                        new_folder_path = new_name
                    except Exception as rename_err:
                        logger.error(f"Failed to rename folder: {rename_err}")
                        self.app.call_from_thread(
                            self.app.notify,
                            f"Warning: Folder rename failed: {str(rename_err)}. Updating metadata only.",
                            severity="warning",
                            timeout=5
                        )
                        # Continue with upload to old folder if rename failed
                        new_folder_path = old_folder_path
                else:
                    new_folder_path = old_folder_path

                # Upload metadata.yaml to the (possibly renamed) folder
                remote_path = f"{new_folder_path}/metadata.yaml"
                logger.info(f"Uploading to: {remote_path}")

                storage.upload(Path(tmp_path), remote_path)

                logger.info(f"✓ Successfully uploaded {remote_path}")

                # Update fast search index for cloud dataset
                try:
                    from hei_datahub.services.index_service import get_index_service

                    index_service = get_index_service()

                    # Extract fields
                    name = self.metadata.get('dataset_name') or self.metadata.get('name', new_folder_path)
                    description = self.metadata.get('description', '')
                    keywords = self.metadata.get('keywords', [])
                    tags = " ".join(keywords) if isinstance(keywords, list) else str(keywords)

                    logger.info(f"Updating index for '{new_folder_path}': name='{name}', description='{description[:50]}...'")

                    # If folder was renamed, delete the old index entry first
                    if new_folder_path != old_folder_path:
                        logger.info(f"Folder renamed: deleting old index entry for '{old_folder_path}'")
                        index_service.delete_item(old_folder_path)
                        logger.info(f"✓ Deleted old index entry for '{old_folder_path}'")

                    index_service.upsert_item(
                        path=new_folder_path,  # Use new folder path
                        name=name,
                        project=None,
                        tags=tags,
                        description=description,
                        format=self.metadata.get('file_format'),
                        source=self.metadata.get('source'),
                        is_remote=True,
                    )
                    logger.info(f"✓ Search index updated successfully for '{new_folder_path}'")
                except Exception as idx_err:
                    logger.warning(f"Failed to update search index: {idx_err}")

                self.app.call_from_thread(
                    self.app.notify,
                    f"✓ Dataset '{name}' updated in cloud!",
                    timeout=5
                )

                # Close form and refresh details
                self.app.call_from_thread(self.app.pop_screen)

                # Refresh the parent CloudDatasetDetailsScreen
                def refresh_parent():
                    from .home import HomeScreen

                    # Small delay to ensure index cache is cleared
                    import time
                    time.sleep(0.1)

                    logger.info(f"Screen stack has {len(self.app.screen_stack)} screens")
                    for i, screen in enumerate(self.app.screen_stack):
                        logger.info(f"  [{i}] {type(screen).__name__}")

                    for screen in self.app.screen_stack:
                        if isinstance(screen, CloudDatasetDetailsScreen) and screen.dataset_id == self.dataset_id:
                            # Reload metadata from cloud
                            logger.info(f"Refreshing CloudDatasetDetailsScreen for {self.dataset_id}")
                            screen.load_metadata()
                            break

                    # Also refresh the HomeScreen table to show updated name (force cache clear)
                    home_found = False
                    for screen in self.app.screen_stack:
                        if isinstance(screen, HomeScreen):
                            logger.info("✓ Found HomeScreen, refreshing table with updated dataset (force refresh)")
                            screen.load_all_datasets(force_refresh=True)
                            home_found = True
                            break

                    if not home_found:
                        logger.warning("✗ HomeScreen not found in screen stack!")

                self.app.call_from_thread(refresh_parent)

            finally:
                # Cleanup temp file
                os.unlink(tmp_path)
                logger.debug(f"Cleaned up temp file: {tmp_path}")

        except Exception as e:
            logger.error(f"Error uploading to cloud: {e}", exc_info=True)
            self.app.call_from_thread(
                self.app.notify,
                f"Error uploading to cloud: {str(e)}",
                severity="error",
                timeout=5
            )
            import traceback
            traceback.print_exc()

    def action_cancel_edits(self) -> None:
        """Cancel editing and discard changes (Esc)."""
        from ..widgets.dialogs import ConfirmCancelDialog

        if len(self._dirty_fields) > 0:
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
        # Update the UI widget
        input_id = f"edit-{field_name}"

        try:
            if field_name == 'description':
                text_area = self.query_one("#edit-description", TextArea)
                text_area.text = str(value)
            else:
                input_widget = self.query_one(f"#{input_id}", Input)
                input_widget.value = str(value)
        except Exception as e:
            logger.warning(f"Could not restore field {field_name}: {e}")

        # Update metadata
        self._update_metadata_from_field(field_name, str(value))

        # Update the previous value cache so next change is tracked correctly
        self._previous_values[field_name] = str(value)
