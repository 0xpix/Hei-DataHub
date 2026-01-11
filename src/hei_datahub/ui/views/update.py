"""
Update screen with progress animation and cross-platform support.
"""
import sys
from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, ProgressBar, Static, Log


class UpdateScreen(Screen):
    """Screen showing update progress with animation."""

    CSS = """
    UpdateScreen {
        align: center middle;
    }

    #update-container {
        width: 70;
        height: auto;
        max-height: 90%;
        padding: 2 4;
        background: $surface;
        border: thick $primary;
        align: center middle;
    }

    #update-title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    #update-status {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    #progress-container {
        height: 3;
        margin: 1 2;
        align: center middle;
    }

    #update-progress {
        width: 100%;
    }

    #update-percent {
        text-align: center;
        color: $success;
        text-style: bold;
        margin-bottom: 1;
    }

    #update-log {
        height: 8;
        border: solid $primary-darken-2;
        margin: 1 0;
        background: $surface-darken-1;
    }

    #button-container {
        margin-top: 1;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .success {
        color: $success;
    }

    .error {
        color: $error;
    }

    .info {
        color: $primary;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, auto_start: bool = True):
        super().__init__()
        self.auto_start = auto_start
        self._updating = False
        self._success = False
        self._platform = "windows" if sys.platform == "win32" else "linux"

    def compose(self) -> ComposeResult:
        yield Container(
            Static("🔄 Hei-DataHub Updater", id="update-title"),
            Static("Initializing...", id="update-status"),
            Vertical(
                ProgressBar(id="update-progress", total=100, show_eta=False),
                id="progress-container"
            ),
            Static("0%", id="update-percent"),
            Log(id="update-log", highlight=True),
            Center(
                Button("Cancel", id="cancel-btn", variant="default"),
                id="button-container"
            ),
            id="update-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start update check when mounted."""
        log = self.query_one("#update-log", Log)
        log.write_line(f"Platform: {self._platform}")
        
        if self.auto_start:
            self.run_update()

    def _log(self, message: str, style: str = "") -> None:
        """Write to log widget thread-safely."""
        def write():
            try:
                log = self.query_one("#update-log", Log)
                # Log widget uses Rich Text internally, just write the message
                log.write_line(message)
            except Exception:
                pass
        self.app.call_from_thread(write)

    def _update_ui(self, status: str, percent: int) -> None:
        """Update progress UI thread-safely."""
        def update():
            try:
                self.query_one("#update-status", Static).update(status)
                self.query_one("#update-progress", ProgressBar).update(progress=percent)
                self.query_one("#update-percent", Static).update(f"{percent}%")
            except Exception:
                pass
        self.app.call_from_thread(update)

    @work(exclusive=True, thread=True)
    def run_update(self) -> None:
        """Run the update process in background."""
        self._updating = True
        
        self._log("Starting update check...")
        self._update_ui("Checking for updates...", 5)

        # Import version check
        try:
            from hei_datahub import __version__
            from hei_datahub.services.update_check import check_for_updates
            self._log(f"Current version: v{__version__}")
        except ImportError as e:
            self._show_error(f"Import error: {e}")
            return

        # Check for updates
        self._update_ui("Connecting to GitHub...", 10)
        self._log("Fetching latest release info...")
        
        try:
            update_info = check_for_updates(force=True)
        except Exception as e:
            self._show_error(f"Failed to check: {e}")
            return

        if update_info is None:
            self._show_error("Could not connect to update server")
            return

        if "error" in update_info:
            self._show_error(update_info["error"])
            return

        # Check if update is available
        has_update = update_info.get("has_update", False)
        latest_version = update_info.get("latest_version", "unknown")
        current_version = update_info.get("current_version", __version__)

        self._update_ui("Checking version...", 20)

        if not has_update:
            # No update available - show success message
            self._log(f"Latest version: v{latest_version}")
            self._log("✓ You're running the latest version!")
            self._show_no_update(current_version)
            return

        # Update available!
        self._log(f"New version available: v{latest_version}")
        self._update_ui(f"Update available: v{latest_version}", 25)

        # Platform-specific handling
        if self._platform == "linux":
            self._handle_linux_update(latest_version)
        else:
            self._handle_windows_update(update_info)

    def _handle_linux_update(self, latest_version: str) -> None:
        """Handle update on Linux - show instructions."""
        self._update_ui("Update instructions", 100)
        self._log("")
        self._log("─" * 40)
        self._log("📦 To update on Linux, run:", "info")
        self._log("")
        self._log("  uv tool upgrade hei-datahub")
        self._log("")
        self._log("Or if using pip:")
        self._log("  pip install --upgrade hei-datahub")
        self._log("─" * 40)
        
        self._show_result_linux(latest_version)

    def _handle_windows_update(self, update_info: dict) -> None:
        """Handle update on Windows - download and install."""
        # Check if frozen (PyInstaller)
        if not getattr(sys, 'frozen', False):
            self._log("Running from source code")
            self._log("Auto-update only works with installed .exe")
            self._log("")
            self._log("To update from source:")
            self._log("  git pull origin main")
            self._show_dev_mode()
            return

        # Import Windows updater
        try:
            from hei_datahub.services.windows_updater import download_update, install_update, get_download_url
        except ImportError as e:
            self._show_error(f"Windows updater not available: {e}")
            return

        # Get download info from windows updater
        latest = update_info.get("latest_version", "?")
        self._log("Fetching download URL...")
        win_info = get_download_url()
        
        if not win_info or "error" in win_info:
            error_msg = win_info.get("error", "Unknown error") if win_info else "Failed to get download info"
            self._show_error(error_msg)
            return
        
        download_url = win_info.get("download_url")
        file_size = win_info.get("file_size", 0)
        
        if not download_url:
            self._show_error("No download URL in release")
            return

        self._log(f"Downloading v{latest}...")
        self._update_ui("Downloading update...", 30)

        mb_total = file_size / (1024 * 1024) if file_size else 0

        def download_progress(downloaded: int, total: int):
            if total > 0:
                pct = 30 + int(60 * downloaded / total)  # 30-90%
                mb_done = downloaded / (1024 * 1024)
                self._update_ui(f"Downloading: {mb_done:.1f}/{mb_total:.1f} MB", pct)

        installer_path = download_update(download_url, download_progress)

        if not installer_path:
            self._show_error("Download failed")
            return

        self._log(f"✓ Downloaded to: {installer_path.name}")
        self._update_ui("Starting installer...", 95)
        self._log("Launching installer...")

        if not install_update(installer_path):
            self._show_error("Failed to start installer")
            return

        # Success - app will exit
        self._log("✓ Installer started!")
        self._log("Closing app in 2 seconds...")
        self._update_ui("Update ready!", 100)
        
        self._updating = False
        self._success = True
        
        # Update button and schedule exit
        def finish():
            try:
                self.query_one("#cancel-btn", Button).label = "Closing..."
                self.query_one("#cancel-btn", Button).disabled = True
            except Exception:
                pass
            self.set_timer(2.0, self._do_exit)
        
        self.app.call_from_thread(finish)

    def _show_no_update(self, current_version: str) -> None:
        """Show 'no update available' message."""
        self._updating = False
        
        def update():
            try:
                self.query_one("#update-status", Static).update("✅ Up to date!")
                self.query_one("#update-progress", ProgressBar).update(progress=100)
                self.query_one("#update-percent", Static).update("100%")
                btn = self.query_one("#cancel-btn", Button)
                btn.label = "Close"
                btn.variant = "success"
            except Exception:
                pass
        
        self.app.call_from_thread(update)

    def _show_result_linux(self, latest_version: str) -> None:
        """Show result for Linux with update instructions."""
        self._updating = False
        
        def update():
            try:
                self.query_one("#update-status", Static).update(f"🐧 Update to v{latest_version}")
                self.query_one("#update-progress", ProgressBar).update(progress=100)
                self.query_one("#update-percent", Static).update("100%")
                btn = self.query_one("#cancel-btn", Button)
                btn.label = "Close"
                btn.variant = "primary"
            except Exception:
                pass
        
        self.app.call_from_thread(update)

    def _show_dev_mode(self) -> None:
        """Show result for dev mode (running from source)."""
        self._updating = False
        
        def update():
            try:
                self.query_one("#update-status", Static).update("📁 Development Mode")
                self.query_one("#update-progress", ProgressBar).update(progress=100)
                self.query_one("#update-percent", Static).update("100%")
                btn = self.query_one("#cancel-btn", Button)
                btn.label = "Close"
            except Exception:
                pass
        
        self.app.call_from_thread(update)

    def _show_error(self, message: str) -> None:
        """Show error message."""
        self._updating = False
        self._log(f"✗ {message}")
        
        def update():
            try:
                self.query_one("#update-status", Static).update("❌ Update Failed")
                self.query_one("#update-progress", ProgressBar).update(progress=0)
                self.query_one("#update-percent", Static).update("")
                btn = self.query_one("#cancel-btn", Button)
                btn.label = "Close"
                btn.variant = "error"
            except Exception:
                pass
        
        self.app.call_from_thread(update)

    def _do_exit(self) -> None:
        """Actually exit the app."""
        self.app.exit()

    def action_cancel(self) -> None:
        """Cancel and go back."""
        if not self._updating:
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel-btn":
            if not self._updating:
                self.app.pop_screen()
