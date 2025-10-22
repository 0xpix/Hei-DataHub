"""
Cloud Files TUI view for browsing remote storage (WebDAV/Heibox).

Displays directory listing with navigation, preview, and download capabilities.
"""
import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static, TextArea

from mini_datahub.services.storage_backend import FileEntry, StorageAuthError, StorageError
from mini_datahub.services.storage_manager import get_storage_backend

logger = logging.getLogger(__name__)


class CloudFilesScreen(Screen):
    """Cloud files browser screen with Vim-style navigation."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("g", "jump_top", "Top", show=False),
        Binding("G", "jump_bottom", "Bottom", show=False),
        Binding("enter", "open_selected", "Open/Preview"),
        Binding("o", "open_selected", "Open/Preview", show=False),
        Binding("d", "download_selected", "Download"),
        Binding("r", "refresh", "Refresh"),
        Binding("h", "go_up", "Parent Dir"),
        Binding("u", "go_up", "Parent Dir", show=False),
    ]

    CSS_PATH = "../styles/cloud_files.tcss"

    def __init__(self):
        super().__init__()
        self.current_path = ""  # Current directory path
        self.path_stack: List[str] = []  # Navigation history
        self.current_entries: List[FileEntry] = []
        self.storage = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("☁️ Cloud Files (Heibox)", id="cloud-title"),
            Static("", id="breadcrumb"),
            Static("", id="storage-status"),
            DataTable(id="files-table", cursor_type="row"),
            Container(
                Label("Preview", id="preview-label"),
                VerticalScroll(
                    Static("", id="preview-content"),
                    id="preview-scroll",
                ),
                id="preview-panel",
                classes="hidden",
            ),
            id="cloud-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen and load root directory."""
        # Setup table columns
        table = self.query_one("#files-table", DataTable)
        table.add_columns("Type", "Name", "Size", "Modified")
        table.focus()

        # Load storage backend and list files
        self.load_directory("")

    def _update_breadcrumb(self) -> None:
        """Update breadcrumb navigation display."""
        breadcrumb = self.query_one("#breadcrumb", Static)

        if not self.current_path:
            breadcrumb.update("📍 / (root)")
        else:
            parts = self.current_path.split("/")
            path_display = " / ".join(parts)
            breadcrumb.update(f"📍 / {path_display}")

    def _update_status(self, message: str, severity: str = "info") -> None:
        """Update status message."""
        status = self.query_one("#storage-status", Static)

        if severity == "error":
            status.update(f"[red]✗ {message}[/red]")
        elif severity == "success":
            status.update(f"[green]✓ {message}[/green]")
        elif severity == "warning":
            status.update(f"[yellow]⚠ {message}[/yellow]")
        else:
            status.update(f"[dim]{message}[/dim]")

    @work(exclusive=True, thread=True)
    async def load_directory(self, path: str) -> None:
        """Load directory contents asynchronously."""
        try:
            self._update_status("Loading...", "info")

            # Get storage backend
            if self.storage is None:
                self.storage = get_storage_backend()

            # List directory
            entries = self.storage.listdir(path)

            # Update UI on main thread
            self.app.call_from_thread(self._populate_table, entries, path)

        except StorageAuthError as e:
            self.app.call_from_thread(
                self._update_status,
                f"Auth failed: {str(e)}. Check HEIBOX_USERNAME and HEIBOX_WEBDAV_TOKEN",
                "error",
            )
            self.app.call_from_thread(self.notify, str(e), severity="error", timeout=10)

        except StorageError as e:
            self.app.call_from_thread(self._update_status, str(e), "error")
            self.app.call_from_thread(self.notify, str(e), severity="error", timeout=7)

        except Exception as e:
            logger.exception("Failed to load directory")
            self.app.call_from_thread(
                self._update_status, f"Unexpected error: {str(e)}", "error"
            )
            self.app.call_from_thread(
                self.notify, f"Error: {str(e)}", severity="error", timeout=7
            )

    def _populate_table(self, entries: List[FileEntry], path: str) -> None:
        """Populate table with file entries (called on main thread)."""
        table = self.query_one("#files-table", DataTable)
        table.clear()

        self.current_entries = entries
        self.current_path = path

        self._update_breadcrumb()

        if not entries:
            self._update_status("Empty directory", "info")
            table.add_row("", "[dim]No files[/dim]", "", "", key="empty")
            return

        # Add entries to table
        for entry in entries:
            icon = "📁" if entry.is_dir else "📄"

            size_str = ""
            if entry.size is not None:
                size_str = entry._format_size()

            modified_str = ""
            if entry.modified:
                modified_str = entry.modified.strftime("%Y-%m-%d %H:%M")

            table.add_row(icon, entry.name, size_str, modified_str, key=entry.path)

        self._update_status(f"{len(entries)} item{'s' if len(entries) != 1 else ''}", "success")

    def action_move_down(self) -> None:
        """Move selection down (j key)."""
        table = self.query_one("#files-table", DataTable)
        if table.row_count > 0:
            table.action_cursor_down()

    def action_move_up(self) -> None:
        """Move selection up (k key)."""
        table = self.query_one("#files-table", DataTable)
        if table.row_count > 0:
            table.action_cursor_up()

    def action_jump_top(self) -> None:
        """Jump to first row (gg)."""
        table = self.query_one("#files-table", DataTable)
        if table.row_count > 0:
            table.cursor_coordinate = (0, 0)

    def action_jump_bottom(self) -> None:
        """Jump to last row (G)."""
        table = self.query_one("#files-table", DataTable)
        if table.row_count > 0:
            table.cursor_coordinate = (table.row_count - 1, 0)

    def action_open_selected(self) -> None:
        """Open selected item (enter or o key)."""
        table = self.query_one("#files-table", DataTable)

        if table.row_count == 0:
            return

        row_key = table.cursor_row
        if row_key is None or row_key == "empty":
            return

        # Find entry
        entry = self._get_entry_by_path(str(row_key))
        if entry is None:
            return

        if entry.is_dir:
            # Navigate into directory
            self.path_stack.append(self.current_path)
            self.load_directory(entry.path)
        else:
            # Preview file
            self.preview_file(entry)

    def _get_entry_by_path(self, path: str) -> Optional[FileEntry]:
        """Find entry by path."""
        for entry in self.current_entries:
            if entry.path == path:
                return entry
        return None

    @work(exclusive=True, thread=True)
    async def preview_file(self, entry: FileEntry) -> None:
        """Preview file contents (text/csv/yaml/json only)."""
        try:
            self.app.call_from_thread(self._update_status, f"Loading preview: {entry.name}...", "info")

            # Download to temp file
            temp_dir = Path(tempfile.gettempdir()) / "hei-datahub"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / entry.name

            self.storage.download(entry.path, temp_file)

            # Read content (limit to first 100 KB for preview)
            max_preview_size = 100 * 1024

            # Check if text-previewable
            previewable_extensions = {".txt", ".md", ".yaml", ".yml", ".json", ".csv", ".log", ".py", ".sh"}
            ext = Path(entry.name).suffix.lower()

            if ext not in previewable_extensions:
                self.app.call_from_thread(
                    self._show_preview,
                    f"[dim]Binary file ({ext}) - download to view\n\nFile: {entry.name}\nSize: {entry._format_size()}[/dim]",
                    entry.name,
                )
                self.app.call_from_thread(self._update_status, f"Downloaded to {temp_file}", "success")
                return

            # Read text content
            content = temp_file.read_text(encoding="utf-8", errors="replace")

            if len(content) > max_preview_size:
                content = content[:max_preview_size] + f"\n\n[dim]... (truncated, {len(content) - max_preview_size} bytes remaining)[/dim]"

            self.app.call_from_thread(self._show_preview, content, entry.name)
            self.app.call_from_thread(self._update_status, f"Previewing {entry.name}", "success")

        except StorageError as e:
            self.app.call_from_thread(
                self._update_status, f"Preview failed: {str(e)}", "error"
            )
            self.app.call_from_thread(self.notify, str(e), severity="error", timeout=5)
        except Exception as e:
            logger.exception("Failed to preview file")
            self.app.call_from_thread(
                self._update_status, f"Preview error: {str(e)}", "error"
            )

    def _show_preview(self, content: str, filename: str) -> None:
        """Show preview panel with content (called on main thread)."""
        preview_panel = self.query_one("#preview-panel")
        preview_label = self.query_one("#preview-label", Label)
        preview_content = self.query_one("#preview-content", Static)

        preview_label.update(f"Preview: {filename}")
        preview_content.update(content)
        preview_panel.remove_class("hidden")

    def action_download_selected(self) -> None:
        """Download selected file (d key)."""
        table = self.query_one("#files-table", DataTable)

        if table.row_count == 0:
            return

        row_key = table.cursor_row
        if row_key is None or row_key == "empty":
            return

        entry = self._get_entry_by_path(str(row_key))
        if entry is None or entry.is_dir:
            self.notify("Cannot download directories", severity="warning", timeout=3)
            return

        # Download to ~/Downloads or /tmp
        download_dir = Path.home() / "Downloads"
        if not download_dir.exists():
            download_dir = Path("/tmp/hei-datahub-downloads")

        download_dir.mkdir(parents=True, exist_ok=True)
        dest_path = download_dir / entry.name

        self.download_file_async(entry, dest_path)

    @work(exclusive=True, thread=True)
    async def download_file_async(self, entry: FileEntry, dest_path: Path) -> None:
        """Download file asynchronously."""
        try:
            self.app.call_from_thread(self._update_status, f"Downloading {entry.name}...", "info")

            self.storage.download(entry.path, dest_path)

            self.app.call_from_thread(
                self._update_status, f"Downloaded to {dest_path}", "success"
            )
            self.app.call_from_thread(
                self.notify, f"✓ Downloaded: {dest_path}", severity="information", timeout=5
            )

        except StorageError as e:
            self.app.call_from_thread(
                self._update_status, f"Download failed: {str(e)}", "error"
            )
            self.app.call_from_thread(self.notify, str(e), severity="error", timeout=5)

    def action_go_up(self) -> None:
        """Go to parent directory (h or u key)."""
        if self.path_stack:
            # Pop from history
            prev_path = self.path_stack.pop()
            self.load_directory(prev_path)
        elif self.current_path:
            # Go up one level
            parent_path = str(Path(self.current_path).parent)
            if parent_path == ".":
                parent_path = ""
            self.load_directory(parent_path)

    def action_refresh(self) -> None:
        """Refresh current directory (r key)."""
        self.load_directory(self.current_path)
        self.notify("Refreshing...", timeout=2)

    def action_close(self) -> None:
        """Close cloud files view."""
        self.app.pop_screen()
