"""
Update overlay widget that displays on the home screen during updates.

Shows a progress bar and status messages while the update runs in the background.
"""
import logging
import os
import subprocess
import sys
from typing import Callable, Optional

from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.widgets import Button, ProgressBar, Static

logger = logging.getLogger(__name__)


class UpdateOverlay(Container):
    """
    Overlay widget that shows update progress on the home screen.

    This replaces the separate UpdateScreen for a more seamless experience.
    """

    DEFAULT_CSS = """
    UpdateOverlay {
        display: none;
        position: absolute;
        width: 100%;
        height: 100%;
        background: $surface 80%;
        align: center middle;
        layer: overlay;
    }

    UpdateOverlay.visible {
        display: block;
    }

    #update-overlay-box {
        width: 50;
        height: auto;
        max-height: 14;
        padding: 1 3;
        background: $surface;
        border: round $primary 50%;
    }

    #update-overlay-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $text;
    }

    #update-overlay-status {
        width: 100%;
        text-align: center;
        color: $text-muted;
        margin-top: 1;
        height: 1;
    }

    #update-overlay-progress-container {
        width: 100%;
        height: 1;
        margin: 1 0 0 0;
    }

    #update-overlay-progress {
        width: 100%;
    }

    #update-overlay-percent {
        display: none;
    }

    #update-overlay-message {
        width: 100%;
        text-align: center;
        color: $text-muted;
        margin-top: 1;
        height: auto;
        max-height: 2;
    }

    #update-overlay-button-container {
        width: 100%;
        margin-top: 1;
        align: center middle;
        display: none;
        height: auto;
    }

    #update-overlay-button-container.visible {
        display: block;
    }

    #update-restart-btn {
        min-width: 16;
    }
    """

    def __init__(
        self,
        on_complete: Optional[Callable[[], None]] = None,
        on_restart: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._on_complete = on_complete
        self._on_restart = on_restart
        self._updating = False
        self._finished = False

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Updating…", id="update-overlay-title"),
            Static("Checking for updates…", id="update-overlay-status"),
            ProgressBar(id="update-overlay-progress", total=100, show_eta=False, show_percentage=True),
            Static("", id="update-overlay-message"),
            Center(
                Button("Restart", id="update-restart-btn", variant="success"),
                id="update-overlay-button-container"
            ),
            id="update-overlay-box"
        )

    def show(self) -> None:
        """Show the overlay and start the update."""
        self.add_class("visible")
        self._finished = False
        self.query_one("#update-overlay-button-container").remove_class("visible")
        self.start_update()

    def hide(self) -> None:
        """Hide the overlay."""
        self.remove_class("visible")

    def _update_progress(self, status: str, percent: int, message: str = "") -> None:
        """Update the progress UI (must be called from main thread)."""
        try:
            self.query_one("#update-overlay-status", Static).update(status)
            self.query_one("#update-overlay-progress", ProgressBar).update(progress=percent)
            if message:
                self.query_one("#update-overlay-message", Static).update(message)
            else:
                self.query_one("#update-overlay-message", Static).update("")
        except Exception as e:
            logger.debug(f"Failed to update progress UI: {e}")

    def _set_progress(self, status: str, percent: int, message: str = "") -> None:
        """Thread-safe progress update."""
        self.app.call_from_thread(lambda: self._update_progress(status, percent, message))

    @work(exclusive=True, thread=True)
    def start_update(self) -> None:
        """Run the update process in background."""
        self._updating = True

        self._set_progress("Checking for updates...", 5)

        # Import required modules
        try:
            from hei_datahub import __version__
            from hei_datahub.services.update_service import trigger_update
            from hei_datahub.infra.install_method import get_install_info, InstallMethod
        except ImportError as e:
            self._show_error(f"Import error: {e}")
            return

        # Check for updates
        self._set_progress("Connecting to GitHub...", 10)

        try:
            result = trigger_update()
        except Exception as e:
            self._show_error(f"Failed to check: {e}")
            return

        if result is None or result.error:
            self._show_error(result.error if result else "Could not connect")
            return

        if not result.has_update:
            self._show_up_to_date(result.current_version)
            return

        latest_version = result.latest_version
        self._set_progress(f"Update v{latest_version} found!", 20)

        # Get install method
        install_info = get_install_info()
        logger.info(
            f"Update available: {result.current_version} → {latest_version}, "
            f"install method: {install_info.method.value}"
        )

        # Handle different installation methods
        if install_info.method == InstallMethod.DEV:
            self._show_dev_mode()
            return

        if install_info.method == InstallMethod.WINDOWS_EXE:
            self._handle_windows_update(result)
            return

        if install_info.method == InstallMethod.APPIMAGE:
            self._show_manual_instructions(latest_version, install_info)
            return

        # Methods that need sudo / interactive prompts cannot run
        # inside the TUI — show the command for the user to run.
        if install_info.method in (InstallMethod.AUR, InstallMethod.HOMEBREW):
            self._show_manual_instructions(latest_version, install_info)
            return

        # Auto-update for non-interactive tools (uv, pipx, pip)
        self._run_auto_update(latest_version, install_info)

    def _run_auto_update(self, latest_version: str, install_info) -> None:
        """Run automatic update for package managers."""
        from hei_datahub.infra.install_method import InstallMethod

        _debug = os.environ.get("HEI_DEBUG_UPDATER", "").strip() in ("1", "true", "yes")

        commands: list[list[str]] = []
        method_name = ""

        if install_info.method == InstallMethod.UV_TOOL:
            method_name = "uv"
            commands = [["uv", "tool", "upgrade", "hei-datahub"]]
        elif install_info.method == InstallMethod.PIPX:
            method_name = "pipx"
            commands = [["pipx", "upgrade", "hei-datahub"]]
        elif install_info.method == InstallMethod.PIP:
            method_name = "pip"
            commands = [[sys.executable, "-m", "pip", "install", "--upgrade", "hei-datahub"]]
        else:
            self._show_manual_instructions(latest_version, install_info)
            return

        self._set_progress(f"Updating via {method_name}…", 30)
        logger.info(f"Auto-update via {method_name}: {commands}")

        total_commands = len(commands)
        success = True
        last_stderr = ""

        for i, cmd in enumerate(commands):
            # Update progress
            base_progress = 30
            progress_per_cmd = 60 // total_commands
            current_progress = base_progress + (i * progress_per_cmd)
            self._set_progress(f"Running: {' '.join(cmd[:3])}…", current_progress)

            try:
                # Run command
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    env={**os.environ}
                )

                stdout, stderr = process.communicate(timeout=120)

                if process.returncode != 0:
                    last_stderr = stderr or stdout or ""
                    logger.error(
                        f"Command failed: {' '.join(cmd)} "
                        f"(exit code {process.returncode})\n"
                        f"stdout: {stdout}\nstderr: {stderr}"
                    )
                    if _debug:
                        logger.warning(f"[DEBUG-UPDATER] stdout: {stdout}")
                        logger.warning(f"[DEBUG-UPDATER] stderr: {stderr}")
                    success = False
                    break
                else:
                    if _debug:
                        logger.warning(f"[DEBUG-UPDATER] {' '.join(cmd)} succeeded: {stdout[:200]}")

            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out: {' '.join(cmd)}")
                self._show_error(f"Update timed out running: {' '.join(cmd[:3])}")
                return
            except FileNotFoundError:
                logger.error(f"Command not found: {cmd[0]}")
                self._show_error(f"Command not found: {cmd[0]}")
                return
            except Exception as e:
                logger.error(f"Error running update: {e}")
                success = False
                break

        if success:
            self._show_success(latest_version)
        else:
            short_err = last_stderr.strip().split('\n')[-1][:80] if last_stderr.strip() else ""
            msg = f"Update via {method_name} failed."
            if short_err:
                msg += f"\n{short_err}"
            msg += f"\nTry: {install_info.update_command}"
            self._show_error(msg)

    def _handle_windows_update(self, result) -> None:
        """Handle Windows executable update."""
        if not getattr(sys, 'frozen', False):
            from hei_datahub.infra.install_method import get_install_info
            install_info = get_install_info()
            self._show_manual_instructions(result.latest_version, install_info)
            return

        try:
            from hei_datahub.services.windows_updater import download_update, install_update, get_download_url
        except ImportError as e:
            self._show_error(f"Windows updater not available: {e}")
            return

        latest = result.latest_version
        win_info = get_download_url()

        if not win_info or "error" in win_info:
            self._show_error(win_info.get("error", "Failed to get download info") if win_info else "Unknown error")
            return

        download_url = win_info.get("download_url")
        file_size = win_info.get("file_size", 0)

        if not download_url:
            self._show_error("No download URL in release")
            return

        self._set_progress("Downloading update...", 30)
        mb_total = file_size / (1024 * 1024) if file_size else 0

        def download_progress(downloaded: int, total: int):
            if total > 0:
                pct = 30 + int(60 * downloaded / total)
                mb_done = downloaded / (1024 * 1024)
                self._set_progress(f"Downloading: {mb_done:.1f}/{mb_total:.1f} MB", pct)

        installer_path = download_update(download_url, download_progress)

        if not installer_path:
            self._show_error("Download failed")
            return

        self._set_progress("Starting installer...", 95)

        if not install_update(installer_path):
            self._show_error("Failed to start installer")
            return

        self._set_progress("Update ready!", 100, "Installer started, app will close...")
        self._updating = False

        # Exit app after short delay
        def do_exit():
            self.app.exit()
        self.app.call_from_thread(lambda: self.set_timer(2.0, do_exit))

    def _show_success(self, latest_version: str) -> None:
        """Show success message and restart button."""
        self._updating = False
        self._finished = True

        # Clear update cache so the badge won't reappear after restart
        try:
            from hei_datahub.services.update_service import clear_update_cache
            clear_update_cache()
        except Exception:
            pass

        def update_ui():
            self.query_one("#update-overlay-title", Static).update("Update Complete")
            self._update_progress(f"Updated to v{latest_version}", 100, "Restart to apply")
            self.query_one("#update-overlay-button-container").add_class("visible")

        self.app.call_from_thread(update_ui)

        if self._on_complete:
            self.app.call_from_thread(self._on_complete)

    def _show_up_to_date(self, current_version: str) -> None:
        """Show already up to date message."""
        self._updating = False
        self._finished = True

        # Clear stale cache
        try:
            from hei_datahub.services.update_service import clear_update_cache
            clear_update_cache()
        except Exception:
            pass

        def update_ui():
            self.query_one("#update-overlay-title", Static).update("Up to Date")
            self._update_progress(f"v{current_version} is the latest", 100)
            self.set_timer(2.0, self.hide)

        self.app.call_from_thread(update_ui)

    def _show_dev_mode(self) -> None:
        """Show dev mode message."""
        self._updating = False
        self._finished = True

        def update_ui():
            self.query_one("#update-overlay-title", Static).update("Development Mode")
            self._update_progress("Running from source", 100, "git pull && uv sync")
            self.set_timer(3.0, self.hide)

        self.app.call_from_thread(update_ui)

    def _show_manual_instructions(self, latest_version: str, install_info) -> None:
        """Show manual update instructions and copy command to clipboard."""
        self._updating = False
        self._finished = True

        cmd = install_info.update_command

        # Try to copy the command to clipboard
        copied = False
        if cmd:
            try:
                from hei_datahub.ui.utils.external import copy_to_clipboard
                copied = copy_to_clipboard(cmd)
            except Exception:
                pass

        def update_ui():
            self.query_one("#update-overlay-title", Static).update(
                f"v{latest_version} Available"
            )
            if cmd:
                hint = " (copied)" if copied else ""
                self._update_progress(
                    f"Run in terminal{hint}:",
                    100,
                    cmd,
                )
            else:
                self._update_progress(
                    install_info.update_instructions.split('\n')[0],
                    100,
                )
            self.set_timer(8.0, self.hide)

        self.app.call_from_thread(update_ui)

    def _show_error(self, message: str) -> None:
        """Show error message."""
        self._updating = False
        self._finished = True

        def update_ui():
            self.query_one("#update-overlay-title", Static).update("Update Failed")
            self._update_progress(message, 0)
            self.set_timer(4.0, self.hide)

        self.app.call_from_thread(update_ui)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle restart button press."""
        if event.button.id == "update-restart-btn":
            if self._on_restart:
                self._on_restart()
            else:
                # Default: exit and let user restart manually
                self.app.exit()
