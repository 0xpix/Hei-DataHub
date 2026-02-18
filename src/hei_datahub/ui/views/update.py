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
        # Detect platform
        if sys.platform == "win32":
            self._platform = "windows"
        elif sys.platform == "darwin":
            self._platform = "macos"
        else:
            self._platform = "linux"

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

        # Import version check - use new update_service with proper version comparison
        try:
            from hei_datahub import __version__
            from hei_datahub.services.update_service import (
                trigger_update,
                is_newer_version,
            )
            self._log(f"Current version: v{__version__}")
        except ImportError as e:
            self._show_error(f"Import error: {e}")
            return

        # Check for updates using new service with proper version comparison
        self._update_ui("Connecting to GitHub...", 10)
        self._log("Fetching latest release info...")

        try:
            result = trigger_update()
        except Exception as e:
            self._show_error(f"Failed to check: {e}")
            return

        if result is None:
            self._show_error("Could not connect to update server")
            return

        if result.error:
            self._show_error(result.error)
            return

        # Build update_info dict for compatibility with existing code
        update_info = {
            "has_update": result.has_update,
            "current_version": result.current_version,
            "latest_version": result.latest_version,
            "release_url": result.release_url,
            "release_notes": result.release_notes,
        }

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

        # Use installation method detection for correct update instructions
        from hei_datahub.infra.install_method import get_install_info, InstallMethod

        install_info = get_install_info()

        # Handle Windows EXE separately (auto-update)
        if install_info.method == InstallMethod.WINDOWS_EXE:
            self._handle_windows_update(update_info)
            return

        # All other installation methods: show instructions
        self._handle_manual_update(latest_version, install_info)

    def _handle_manual_update(self, latest_version: str, install_info) -> None:
        """Handle update for non-auto-update installations - run update command."""
        import subprocess
        import shlex
        from hei_datahub.infra.install_method import InstallMethod

        # Determine the update command(s) to run
        commands = []
        method_name = ""

        if install_info.method == InstallMethod.AUR:
            method_name = "AUR (Arch Linux)"
            # Use yay for AUR updates
            commands = [["yay", "-Syu", "--noconfirm", "hei-datahub"]]
        elif install_info.method == InstallMethod.HOMEBREW:
            method_name = "Homebrew"
            # brew update first, then upgrade
            commands = [
                ["brew", "update"],
                ["brew", "upgrade", "hei-datahub"]
            ]
        elif install_info.method == InstallMethod.UV_TOOL:
            method_name = "uv tool"
            commands = [["uv", "tool", "upgrade", "hei-datahub"]]
        elif install_info.method == InstallMethod.PIP:
            method_name = "pip"
            commands = [["pip", "install", "--upgrade", "hei-datahub"]]
        elif install_info.method == InstallMethod.DEV:
            method_name = "Development"
            # For dev mode, just show instructions (can't auto-update source)
            self._update_ui("Development mode", 100)
            self._log("")
            self._log("─" * 40)
            self._log("🔧 Running from source (dev mode)", "info")
            self._log("")
            self._log("To update, run in the repo:")
            self._log("  git pull origin main")
            self._log("  uv sync")
            self._log("─" * 40)
            self._show_result_manual(latest_version, install_info)
            return
        elif install_info.method == InstallMethod.APPIMAGE:
            # Generic AppImage - show download instructions
            self._update_ui("AppImage", 100)
            self._log("")
            self._log("─" * 40)
            self._log("📦 Running from AppImage", "info")
            self._log("")
            self._log("To update, download the latest AppImage from:")
            self._log("  https://github.com/0xpix/Hei-DataHub/releases")
            self._log("")
            self._log("Or install via AUR for automatic updates:")
            self._log("  yay -S hei-datahub")
            self._log("─" * 40)
            self._show_result_manual(latest_version, install_info)
            return
        else:
            # Unknown method - show instructions
            self._update_ui("Update instructions", 100)
            self._log("")
            self._log("─" * 40)
            self._log("📦 To update:", "info")
            self._log("")
            self._log(install_info.update_instructions)
            self._log("─" * 40)
            self._show_result_manual(latest_version, install_info)
            return

        # Run the update command(s)
        self._log("")
        self._log("─" * 40)
        self._log(f"📦 Updating to v{latest_version}...", "info")
        self._log("")

        total_commands = len(commands)
        success = True

        for i, cmd in enumerate(commands):
            cmd_str = " ".join(cmd)
            self._log(f"$ {cmd_str}")

            # Update progress
            base_progress = 30
            progress_per_cmd = 60 // total_commands
            current_progress = base_progress + (i * progress_per_cmd)
            self._update_ui(f"Running: {cmd[0]}...", current_progress)

            try:
                # Run command and capture output in real-time
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                # Read output line by line
                for line in iter(process.stdout.readline, ''):
                    line = line.rstrip()
                    if line:
                        self._log(f"  {line}")

                process.wait()

                if process.returncode != 0:
                    self._log(f"✗ Command failed with exit code {process.returncode}")
                    success = False
                    break
                else:
                    self._log(f"✓ {cmd[0]} completed")

            except FileNotFoundError:
                self._log(f"✗ Command not found: {cmd[0]}")
                success = False
                break
            except Exception as e:
                self._log(f"✗ Error: {e}")
                success = False
                break

            self._log("")

        self._log("─" * 40)

        if success:
            self._update_ui("Update complete!", 100)
            self._log("")
            self._log("✓ Update completed successfully!")
            self._log("")
            self._log("Restart the app to use the new version.")
            self._show_update_success(latest_version)
        else:
            self._update_ui("Update failed", 100)
            self._log("")
            self._log("✗ Update failed. Try running manually:")
            self._log(f"  {install_info.update_command}")
            self._show_result_manual(latest_version, install_info)

    def _show_update_success(self, latest_version: str) -> None:
        """Show update success message."""
        self._updating = False

        def update():
            try:
                self.query_one("#update-status", Static).update(f"✅ Updated to v{latest_version}")
                self.query_one("#update-progress", ProgressBar).update(progress=100)
                self.query_one("#update-percent", Static).update("100%")
                btn = self.query_one("#cancel-btn", Button)
                btn.label = "Restart"
                btn.variant = "success"
            except Exception:
                pass

        self.app.call_from_thread(update)

    def _handle_windows_update(self, update_info: dict) -> None:
        """Handle update on Windows - download and install."""
        # Check if frozen (PyInstaller)
        if not getattr(sys, 'frozen', False):
            from hei_datahub.infra.install_method import get_install_info
            install_info = get_install_info()
            self._handle_manual_update(update_info.get("latest_version", "?"), install_info)
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
        win_info = get_download_url(target_version=latest)

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
            self._show_error(
                "Failed to start installer. "
                "Please approve the admin prompt (UAC) or "
                "try running the installer manually from: "
                f"{installer_path}"
            )
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

    def _show_result_manual(self, latest_version: str, install_info) -> None:
        """Show result for manual update installations (AUR, Homebrew, pip, etc.)."""
        from hei_datahub.infra.install_method import InstallMethod

        self._updating = False

        # Determine icon based on install method
        method_icons = {
            InstallMethod.AUR: "🐧",
            InstallMethod.HOMEBREW: "🍺",
            InstallMethod.UV_TOOL: "📦",
            InstallMethod.PIP: "🐍",
            InstallMethod.DEV: "🔧",
            InstallMethod.APPIMAGE: "📦",
        }
        icon = method_icons.get(install_info.method, "📦")

        def update():
            try:
                self.query_one("#update-status", Static).update(f"{icon} Update to v{latest_version}")
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
