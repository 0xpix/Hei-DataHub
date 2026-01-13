"""
Cloud dataset details screen.
"""
import logging
import os
import tempfile

import yaml
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Header,
    Label,
    Static,
)

from hei_datahub.infra.index import delete_dataset
from hei_datahub.services.index_service import get_index_service
from hei_datahub.services.storage_manager import get_storage_backend
from hei_datahub.ui.utils.actions import ClipboardActionsMixin, NavActionsMixin, UrlActionsMixin
from hei_datahub.ui.widgets.contextual_footer import ContextualFooter

logger = logging.getLogger(__name__)


class CloudDatasetDetailsScreen(NavActionsMixin, UrlActionsMixin, ClipboardActionsMixin, Screen):
    """Screen to view cloud dataset details (from metadata.yaml)."""

    CSS_PATH = "../styles/dataset_detail.tcss"

    BINDINGS = [
        ("escape", "back", "Back"),
        ("e", "edit_cloud_dataset", "Edit"),
        ("y", "copy_source", "Copy Source"),
        ("o", "open_url", "Open URL"),
        ("d", "delete_dataset", "Delete"),
    ]

    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id
        self.metadata = None

    @property
    def source_url(self) -> str:
        """Get source URL for mixins (used by UrlActionsMixin and ClipboardActionsMixin)."""
        if self.metadata and 'source' in self.metadata:
            return self.metadata['source']
        return None

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label(f"󱤟 Dataset: {self.dataset_id}", classes="title"),
            Static(id="details-content"),
            id="details-container",
        )
        footer = ContextualFooter()
        footer.set_context("details")
        yield footer

    def on_mount(self) -> None:
        """Load metadata when screen is mounted."""
        self.load_metadata()

    @work(thread=True)
    def load_metadata(self) -> None:
        """Load metadata from index (fast) or cloud storage (fallback)."""
        try:
            # First try to get metadata from the index (much faster)
            index_service = get_index_service()

            # Search for this specific dataset in the index
            results = index_service.search(query_text="", project_filter=None, limit=1000)

            # Find the dataset by path
            dataset_item = None
            for item in results:
                if item.get('path') == self.dataset_id:
                    dataset_item = item
                    break

            if dataset_item:
                # Build metadata from index data (no network call!)
                logger.info(f"Loading metadata for '{self.dataset_id}' from index (fast)")
                self.metadata = {
                    'name': dataset_item.get('name', self.dataset_id),
                    'description': dataset_item.get('description', ''),
                    'tags': dataset_item.get('tags', '').split() if dataset_item.get('tags') else [],
                    'format': dataset_item.get('format'),
                    'source': dataset_item.get('source'),
                    'size': dataset_item.get('size'),
                    # Note: Some fields might not be in index, but that's OK for preview
                }

                # Update UI on main thread
                self.app.call_from_thread(self._display_metadata)
                return

            # Fallback: If not in index, download from cloud (slower)
            logger.info("Dataset not in index, downloading metadata from cloud")

            storage = get_storage_backend()
            metadata_path = f"{self.dataset_id}/metadata.yaml"

            # Download metadata.yaml
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                storage.download(metadata_path, tmp.name)
                tmp_path = tmp.name

            try:
                with open(tmp_path, encoding='utf-8') as f:
                    self.metadata = yaml.safe_load(f)

                # Update UI on main thread
                self.app.call_from_thread(self._display_metadata)

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            error_msg = f"Error loading metadata: {str(e)}"
            self.app.call_from_thread(lambda: self.app.notify(error_msg, severity="error", timeout=5))
            self.app.call_from_thread(lambda: self.query_one("#details-content", Static).update(f"[red]{error_msg}[/red]"))

    def _display_metadata(self) -> None:
        """Display formatted metadata in the details view."""
        if not self.metadata:
            return

        content = []

        # Format metadata nicely
        if 'name' in self.metadata:
            content.append(f"[bold cyan]Name:[/bold cyan] {self.metadata['name']}")

        if 'description' in self.metadata:
            content.append(f"\n[bold cyan]Description:[/bold cyan]\n{self.metadata['description']}")

        if 'source' in self.metadata:
            content.append(f"\n[bold cyan]Source:[/bold cyan] {self.metadata['source']}")

        if 'license' in self.metadata:
            content.append(f"\n[bold cyan]License:[/bold cyan] {self.metadata['license']}")

        if 'temporal_coverage' in self.metadata:
            tc = self.metadata['temporal_coverage']
            if isinstance(tc, dict):
                start = tc.get('start', 'N/A')
                end = tc.get('end', 'N/A')
                content.append(f"\n[bold cyan]Temporal Coverage:[/bold cyan] {start} to {end}")

        if 'spatial_coverage' in self.metadata:
            content.append(f"\n[bold cyan]Spatial Coverage:[/bold cyan] {self.metadata['spatial_coverage']}")

        if 'keywords' in self.metadata:
            keywords = ', '.join(self.metadata['keywords']) if isinstance(self.metadata['keywords'], list) else self.metadata['keywords']
            content.append(f"\n[bold cyan]Keywords:[/bold cyan] {keywords}")

        # Show raw YAML at the end
        import yaml
        content.append("\n\n[bold cyan]Raw Metadata:[/bold cyan]")
        content.append(f"[dim]{yaml.dump(self.metadata, default_flow_style=False)}[/dim]")

        details_widget = self.query_one("#details-content", Static)
        details_widget.update("\n".join(content))

    # action_back, action_copy_source, action_open_url are inherited from mixins

    def action_delete_dataset(self) -> None:
        """Delete dataset (d key) - shows confirmation dialog."""
        from ..widgets.dialogs import ConfirmDeleteDialog

        self.app.push_screen(
            ConfirmDeleteDialog(self.dataset_id),
            self._handle_delete_confirmation
        )

    def _handle_delete_confirmation(self, confirmed: bool) -> None:
        """Handle delete confirmation dialog response."""
        if confirmed:
            self.delete_from_cloud()

    @work(thread=True)
    def delete_from_cloud(self) -> None:
        """Delete dataset from cloud storage and local index."""
        try:
            self.app.call_from_thread(
                lambda: self.app.notify(f"Deleting {self.dataset_id} from cloud...", timeout=3)
            )

            # Delete from cloud storage (WebDAV)
            storage = get_storage_backend()

            # Delete the entire dataset folder
            folder_path = self.dataset_id
            try:
                # List and delete all files in the dataset folder
                items = storage.listdir(folder_path)
                for item in items:
                    file_path = f"{folder_path}/{item.name}"
                    storage.delete(file_path)
                    logger.debug(f"Deleted file: {file_path}")

                # Delete the folder itself
                storage.delete(folder_path)
                logger.info(f"Deleted dataset folder from cloud: {folder_path}")
            except Exception as e:
                logger.warning(f"Error deleting from cloud: {e}")
                # Continue with local deletion even if cloud deletion fails

            # Delete from local SQLite index (datasets_store and datasets_fts)
            try:
                delete_dataset(self.dataset_id)
                logger.info(f"Deleted dataset from local index: {self.dataset_id}")
            except Exception as e:
                logger.warning(f"Error deleting from local index: {e}")

            # Delete from fast search index
            try:
                index_service = get_index_service()
                index_service.delete_item(self.dataset_id)
                logger.info(f"Deleted dataset from search index: {self.dataset_id}")
            except Exception as e:
                logger.warning(f"Error deleting from search index: {e}")

            # Success notification
            self.app.call_from_thread(
                lambda: self.app.notify(f"✓ Dataset '{self.dataset_id}' deleted successfully!", timeout=5)
            )

            # Go back to home screen
            self.app.call_from_thread(lambda: self.app.pop_screen())

            # Refresh the home screen table
            def refresh_home():
                from .home import HomeScreen
                for screen in self.app.screen_stack:
                    if isinstance(screen, HomeScreen):
                        screen.refresh_data()
                        break

            self.app.call_from_thread(refresh_home)

        except Exception as e:
            error_msg = f"Error deleting dataset: {str(e)}"
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
            self.app.call_from_thread(
                lambda: self.app.notify(error_msg, severity="error", timeout=5)
            )

    def action_download_all(self) -> None:
        """Download entire dataset directory."""
        self.app.notify("Download all not yet implemented", severity="warning", timeout=3)

    def action_edit_cloud_dataset(self) -> None:
        """Edit cloud dataset (e key)."""
        from .dataset_edit import CloudEditDetailsScreen

        if not self.metadata:
            self.app.notify("No metadata loaded", severity="error", timeout=3)
            return

        # Convert cloud metadata format to match local format
        # Cloud metadata has 'name' but local expects 'dataset_name'
        local_format_metadata = self.metadata.copy()
        if 'name' in local_format_metadata and 'dataset_name' not in local_format_metadata:
            local_format_metadata['dataset_name'] = local_format_metadata['name']

        # Add id field from dataset_id
        local_format_metadata['id'] = self.dataset_id

        # Push cloud edit screen
        self.app.push_screen(CloudEditDetailsScreen(self.dataset_id, local_format_metadata.copy()))
