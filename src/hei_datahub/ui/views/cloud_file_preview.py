"""
Cloud file preview screen.

"""
import logging
import os
import tempfile
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, TextArea

logger = logging.getLogger(__name__)


class CloudFilePreviewScreen(Screen):
    """Screen to preview cloud file contents."""

    CSS_PATH = "../styles/cloud_file_preview.tcss"

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
        ("d", "download", "Download"),
    ]

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.content = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label(f"☁️ Cloud File: {self.filename}", classes="title"),
            TextArea(id="file-content", read_only=True),
            id="preview-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load file content when screen is mounted."""
        self.load_file_content()

    @work(thread=True)
    def load_file_content(self) -> None:
        """Load file content from cloud storage."""
        try:
            from mini_datahub.services.storage_manager import get_storage_backend

            storage = get_storage_backend()

            # Download to temp file
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(self.filename)[1]) as tmp:
                storage.download(self.filename, tmp.name)
                tmp_path = tmp.name

            # Read content
            try:
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()

                # Update UI on main thread
                self.app.call_from_thread(self._update_content)

            except UnicodeDecodeError:
                self.app.call_from_thread(lambda: self.app.notify("Cannot preview binary file", severity="warning"))
                self.app.call_from_thread(lambda: self.query_one("#file-content", TextArea).load_text("[Binary file - cannot display]"))
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            self.app.call_from_thread(lambda: self.app.notify(f"Error loading file: {str(e)}", severity="error", timeout=5))
            self.app.call_from_thread(lambda: self.query_one("#file-content", TextArea).load_text(f"Error: {str(e)}"))

    def _update_content(self) -> None:
        """Update the text area with loaded content."""
        text_area = self.query_one("#file-content", TextArea)
        text_area.load_text(self.content)

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_download(self) -> None:
        """Download file to local filesystem."""
        try:
            from mini_datahub.services.storage_manager import get_storage_backend

            storage = get_storage_backend()
            download_dir = Path.home() / "Downloads"
            download_dir.mkdir(exist_ok=True)

            output_path = download_dir / self.filename
            storage.download(self.filename, str(output_path))

            self.app.notify(f"✓ Downloaded to {output_path}", timeout=5)

        except Exception as e:
            self.app.notify(f"Download failed: {str(e)}", severity="error", timeout=5)
