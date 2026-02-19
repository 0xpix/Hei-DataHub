"""
Cloud dataset details screen.
"""
import logging
import os
import tempfile
import time
from datetime import datetime

import pyperclip
import yaml
from textual import on, work, events
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal, Container
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.widgets import (
    Button,
    Header,
    Label,
    Static,
)

# Simple in-memory cache for metadata to avoid refetching on every view
# Key: dataset_id, Value: (metadata_dict, timestamp)
_METADATA_CACHE = {}

def clear_metadata_cache(dataset_id: str = None) -> None:
    """Clear metadata cache for specific dataset or all."""
    if dataset_id:
        if dataset_id in _METADATA_CACHE:
            del _METADATA_CACHE[dataset_id]
    else:
        _METADATA_CACHE.clear()

def update_metadata_cache(dataset_id: str, metadata: dict) -> None:
    """Update metadata cache with fresh data."""
    _METADATA_CACHE[dataset_id] = (metadata, time.time())

from hei_datahub.infra.index import delete_dataset
from hei_datahub.services.index_service import get_index_service
from hei_datahub.services.storage_manager import get_storage_backend
from hei_datahub.ui.utils.actions import ClipboardActionsMixin, NavActionsMixin, UrlActionsMixin
from hei_datahub.ui.widgets.contextual_footer import ContextualFooter

logger = logging.getLogger(__name__)


class MetadataField(Horizontal):
    """A row displaying a metadata field with a copy button."""
    def __init__(self, label: str, value: str, raw_value: str = None) -> None:
        super().__init__()
        self.label_text = label
        self.value_text = value
        self.raw_value = raw_value if raw_value is not None else value

    def compose(self) -> ComposeResult:
        # Minimalistic copy icon
        yield Label(" ", classes="copy-btn")
        yield Label(f"[bold cyan]{self.label_text}:[/bold cyan] {self.value_text}", classes="field-text")

    @on(events.Click, ".copy-btn")
    def copy_to_clipboard(self) -> None:
        try:
             pyperclip.copy(str(self.raw_value))
             self.app.notify(f"Copied {self.label_text}", timeout=2)
        except Exception as e:
             self.app.notify(f"Failed to copy: {e}", severity="error")


class YankFooter(Static):
    """Footer for Yank Mode cheat sheet."""

    DEFAULT_CSS = """
    YankFooter {
        dock: bottom;
        width: 100%;
        height: auto;
        min-height: 1;
        background: $surface;
        color: $text;
        border-top: wide $accent;
        padding: 0 1;
        display: none;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        # Mappings for display
        items = [
            ("n", "name"), ("c", "cat"), ("d", "desc"), ("s", "src"),
            ("a", "access"), ("f", "fmt"), ("r", "ref"), ("l", "loc"),
            ("t", "time"), ("p", "space"), ("y", "all")
        ]

        text_parts = ["[bold reverse magenta] YANK [/]"]

        parts = []
        for k, label in items:
            parts.append(f"[bold]{k}[/]:{label}")
        parts.append("[bold]Esc[/]:cancel")

        text_parts.append("  ".join(parts))

        yield Label("  ".join(text_parts), markup=True)

class CloudDatasetDetailsScreen(NavActionsMixin, UrlActionsMixin, Screen):
    """Screen to view cloud dataset details (from metadata.yaml)."""

    CSS_PATH = "../styles/dataset_detail.tcss"

    BINDINGS = [
        ("escape", "back", "Back"),
        ("e", "edit_cloud_dataset", "Edit"),
        ("o", "open_url", "Open URL"),
        ("d", "delete_dataset", "Delete"),
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
    ]

    def action_scroll_down(self) -> None:
        """Scroll down (vim style)."""
        self.query_one("#details-container", VerticalScroll).scroll_down()

    def action_scroll_up(self) -> None:
        """Scroll up (vim style)."""
        self.query_one("#details-container", VerticalScroll).scroll_up()

    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id
        self.metadata = None
        self._yank_mode = False
        self._yank_auto_cancel_timer = None

        self.field_map = {
            'n': ('name', 'Name'),
            'c': ('category', 'Category'),
            'd': ('description', 'Description'),
            's': ('source', 'Source'),
            'a': ('access_method', 'Access Method'),
            'f': ('file_format', 'Format'),
            'r': ('reference', 'Reference'),
            'l': ('storage_location', 'Storage Location'),
            'e': ('date_created', 'Date Created'),
            'z': ('size', 'Size'),
            'p': ('spatial_coverage', 'Spatial Coverage'),
            't': ('temporal_coverage', 'Temporal Coverage'),
            'u': ('used_in_projects', 'Used in Projects'),
            'g': ('tags', 'Tags'),
            'y': ('__ALL__', 'All Fields'),
        }

    @property
    def source_url(self) -> str:
        """Get source URL for mixins (used by UrlActionsMixin)."""
        if not self.metadata:
            return None

        # Check Access/Location (storage_location) first
        url = self.metadata.get('storage_location')
        if url and (url.startswith('http://') or url.startswith('https://')):
            return url

        return self.metadata.get('storage_location')

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Label(f"󱤟 Dataset: {self.dataset_id}", classes="title"),
            id="details-container",
        )
        footer = ContextualFooter()
        footer.set_context("details")
        yield footer
        # Add YankFooter but keep it hidden via CSS until toggled
        yield YankFooter()

    def on_mount(self) -> None:
        """Load metadata when screen is mounted."""
        # 1. Start loading from cache/index immediately (fast)
        self.load_metadata_from_index()

        # 2. Check in-memory cache for full metadata
        if self.dataset_id in _METADATA_CACHE:
             cached_meta, timestamp = _METADATA_CACHE[self.dataset_id]
             # Cache valid for 5 minutes
             if time.time() - timestamp < 300:
                 logger.info(f"Using cached cloud metadata for {self.dataset_id}")

                 # Merge cached cloud data with current metadata (which might be from index)
                 if self.metadata:
                     self.metadata.update(cached_meta)
                 else:
                     self.metadata = cached_meta

                 self._display_metadata(is_loading=False)
                 return

        # 3. If not in cache, fetch from cloud (slower)
        self.load_metadata_from_cloud()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses for yank mode."""
        # Yank Mode Logic
        if self._yank_mode:
            # Stop timer on any key press
            if self._yank_auto_cancel_timer:
                self._yank_auto_cancel_timer.stop()

            if event.key == "escape":
                self._exit_yank_mode()
                event.stop()
                return

            key = event.key
            if len(key) == 1:
                key = key.lower()

            if key in self.field_map:
                self._perform_yank(key)
                event.stop()
            else:
                self.app.notify("Yank cancelled", severity="warning")
                self._exit_yank_mode()
                event.stop()
            return

        # Normal Mode Logic
        if event.key == "y":
             # Only enter yank mode if metadata is available
             if self.metadata:
                 self._enter_yank_mode()
                 event.stop()

    def _enter_yank_mode(self) -> None:
        """Activate operator-pending yank mode."""
        self._yank_mode = True
        self.query_one(ContextualFooter).styles.display = "none"
        self.query_one(YankFooter).styles.display = "block"

        # Auto-cancel after 10 seconds
        self._yank_auto_cancel_timer = self.set_timer(10.0, self._exit_yank_mode)

    def _exit_yank_mode(self) -> None:
        """Deactivate yank mode."""
        self._yank_mode = False
        if self._yank_auto_cancel_timer:
            self._yank_auto_cancel_timer.stop()

        # Switch footers back
        try:
            self.query_one(YankFooter).styles.display = "none"
            self.query_one(ContextualFooter).styles.display = "block"
        except Exception:
            # In case widget is unmounted
            pass

    def _perform_yank(self, key_char: str) -> None:
        field_key, display_name = self.field_map[key_char]

        if field_key == '__ALL__':
            # YAML dump all
            try:
                # Clean up metadata for YAML dump (remove internal keys if any?)
                # We dump the whole metadata dict
                content = yaml.dump(self.metadata, sort_keys=False, allow_unicode=True)
                pyperclip.copy(content)
                self.app.notify("✓ Yanked All Fields (YAML)")
            except Exception as e:
                self.app.notify(f"Yank failed: {e}", severity="error")
        else:
            # Specific field
            # Check if key exists in metadata or try aliases
            val = self.metadata.get(field_key)

            # Fallback for 'format' if 'file_format' used in map but mostly stored as 'format'
            if val is None and field_key == 'file_format':
                 val = self.metadata.get('format')

            if val is not None:
                try:
                    pyperclip.copy(str(val))
                    self.app.notify(f"✓ Yanked {display_name}")
                except Exception as e:
                    self.app.notify(f"Yank failed: {e}", severity="error")
            else:
                self.app.notify(f"Field '{display_name}' is empty", severity="warning")

        self._exit_yank_mode()



    def load_metadata_from_index(self) -> None:
        """Load metadata from index (fast)."""
        try:
            index_service = get_index_service()
            # Search for this specific dataset in the index
            results = index_service.search(query_text="", project_filter=None, limit=1000)

            dataset_item = None
            for item in results:
                if item.get('path') == self.dataset_id:
                    dataset_item = item
                    break

            if dataset_item:
                logger.info(f"Loading metadata for '{self.dataset_id}' from index (fast)")

                # Handle project list splitting
                projects = []
                if dataset_item.get('project'):
                    # The index stores 'project' as a single string (possibly comma-separated)
                    projects = [p.strip() for p in dataset_item.get('project').split(',')]

                self.metadata = {
                    'name': dataset_item.get('name', self.dataset_id),
                    'description': dataset_item.get('description', ''),
                    'tags': dataset_item.get('tags', '').split() if dataset_item.get('tags') else [],
                    'format': dataset_item.get('format'),
                    'file_format': dataset_item.get('format'),
                    'source': dataset_item.get('source'),
                    'size': dataset_item.get('size'),
                    'category': dataset_item.get('category'),
                    'spatial_coverage': dataset_item.get('spatial_coverage'),
                    'temporal_coverage': dataset_item.get('temporal_coverage'),
                    'access_method': dataset_item.get('access_method') or '',
                    'storage_location': dataset_item.get('storage_location'),
                    'reference': dataset_item.get('reference'),
                    'spatial_resolution': dataset_item.get('spatial_resolution'),
                    'temporal_resolution': dataset_item.get('temporal_resolution'),
                    'used_in_projects': projects,
                }

                # Update UI immediately
                self._display_metadata(is_loading=True)
        except Exception as e:
            logger.warning(f"Failed to load from index: {e}")

    @work(thread=True)
    def load_metadata_from_cloud(self) -> None:
        """Load metadata from cloud storage (WebDAV) to show full source of truth."""
        try:
            # We silently fetch in background without notifying user
            # self.app.call_from_thread(self.app.notify, f"Fetching details for {self.dataset_id}...", timeout=2)
            logger.info("Downloading metadata from cloud to ensure full details")

            storage = get_storage_backend()
            metadata_path = f"{self.dataset_id}/metadata.yaml"

            # Download metadata.yaml
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                storage.download(metadata_path, tmp.name)
                tmp_path = tmp.name

            try:
                with open(tmp_path, encoding='utf-8') as f:
                    self.metadata = yaml.safe_load(f)

                # Ensure 'file_format' alias is present if 'format' exists (for compatibility)
                if self.metadata.get('format') and not self.metadata.get('file_format'):
                    self.metadata['file_format'] = self.metadata['format']

                # Update cache
                _METADATA_CACHE[self.dataset_id] = (self.metadata, time.time())

                # Update UI on main thread
                self.app.call_from_thread(self._display_metadata)

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            # Only show error if we also failed to load from index (metadata is None)
            if not self.metadata:
                error_msg = f"Error loading metadata: {str(e)}"
                self.app.call_from_thread(lambda: self.app.notify(error_msg, severity="error", timeout=5))
                self.app.call_from_thread(lambda: self.query_one("#details-content", Static).update(f"[red]{error_msg}[/red]"))
            else:
                logger.warning(f"Failed to refresh metadata from cloud: {e}")

    def _display_metadata(self, is_loading: bool = False) -> None:
        """Display formatted metadata in the details view."""
        if not self.metadata:
            return

        container = self.query_one("#details-container", VerticalScroll)

        # Clear existing fields (keep the title which is the first child)
        for child in container.query(MetadataField):
            child.remove()
        for child in container.query(".loading-msg"):
            child.remove()

        if is_loading:
             container.mount(Label("Refreshing details...", classes="loading-msg"))

        # Define field handlers for nicer display and ordering
        # Field Key -> (Display Name, Formatter Function)
        field_config = {
            'name': ('Name', lambda x: x),
            'dataset_name': ('Name', lambda x: x), # Alias
            'id': ('ID', lambda x: x),
            'category': ('Category', lambda x: x),
            'description': ('Description', lambda x: x),
            'source': ('Source', lambda x: x),
            'reference': ('Reference', lambda x: x),
            'access_method': ('Access Method', lambda x: x),
            'file_format': ('Format', lambda x: x),
            'format': ('Format', lambda x: x), # Alias
            'storage_location': ('Storage Location', lambda x: x),
            'size': ('Size', lambda x: x),
            'spatial_resolution': ('Spatial Resolution', lambda x: x),
            'spatial_coverage': ('Spatial Coverage', lambda x: x),
            'temporal_resolution': ('Temporal Resolution', lambda x: x),
            'temporal_coverage': ('Temporal Coverage', lambda x: f"{x.get('start', 'N/A')} to {x.get('end', 'N/A')}" if isinstance(x, dict) else x),
            'tags': ('Tags', lambda x: ', '.join(x) if isinstance(x, list) else x),
            'license': ('License', lambda x: x),
            'keywords': ('Keywords', lambda x: ', '.join(x) if isinstance(x, list) else x),
            'used_in_projects': ('Used in Projects', lambda x: ', '.join(x) if isinstance(x, list) else str(x)),
            'date_created': ('Date Created', lambda x: x),
        }

        # Track processed keys to handle dynamic/unknown fields
        processed_keys = set()

        def mount_field(key, val):
            display_name, formatter = field_config.get(key, (key.replace('_', ' ').title(), str))
            formatted_val = formatter(val)

            # For copying, ensure we have a string
            raw_val = val
            if isinstance(val, (dict, list)):
                raw_val = str(val)

            container.mount(MetadataField(display_name, formatted_val, raw_value=raw_val))

        # 1. Display known fields in preferred order
        preferred_order = [
            'name', 'category', 'description', 'source', 'access_method',
            'file_format', 'reference', 'dataset_id', 'id'
        ]

        for key in preferred_order:
            val = self.metadata.get(key)
            if val and key not in processed_keys:
                mount_field(key, val)
                processed_keys.add(key)

                # Handle aliases (e.g. if we processed 'name', mark 'dataset_name' as processed too)
                if key == 'name': processed_keys.add('dataset_name')
                if key == 'dataset_name': processed_keys.add('name')
                if key == 'file_format': processed_keys.add('format')
                if key == 'format': processed_keys.add('file_format')

        # 2. Display remaining known fields
        for key, val in self.metadata.items():
            if key in field_config and key not in processed_keys and val:
                mount_field(key, val)
                processed_keys.add(key)

        # 3. Display any other unknown fields (to ensure user sees EVERYTHING)
        for key, val in self.metadata.items():
            if key not in processed_keys and val and key not in ('id',): # Skip internal ID if redundant
                mount_field(key, val)
                processed_keys.add(key)

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
                # Version control/Backup: Move to _DELETED_DATASETS instead of permanent deletion
                # This ensures data can be restored from Heibox if needed.
                backup_root = "_DELETED_DATASETS"
                if not storage.exists(backup_root):
                    storage.mkdir(backup_root)

                # Append timestamp to avoid collisions
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{backup_root}/{folder_path}_{timestamp}"

                # Move instead of delete
                storage.move(folder_path, backup_path)
                logger.info(f"Moved dataset folder to backup: {backup_path}")

                self.app.call_from_thread(
                    lambda: self.app.notify(f"Dataset moved to {backup_path} (recover via Heibox)", timeout=5)
                )

            except Exception as e:
                logger.warning(f"Error moving to backup (cloud): {e}")
                # Continue with local deletion even if cloud deletion/move fails

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
