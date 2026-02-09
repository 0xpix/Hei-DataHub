"""
Update overlay widget that displays on the home screen during updates.

Shows a progress bar and status messages while the update runs in the background.
"""
import logging
import os
import subprocess
import sys
from typing import Callable, Optional

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.widgets import Button, Input, ProgressBar, Static

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

    #update-overlay-password-container {
        width: 100%;
        height: auto;
        margin-top: 1;
        display: none;
    }

    #update-overlay-password-container.visible {
        display: block;
    }

    #update-overlay-password {
        width: 100%;
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
        # Pending sudo update state
        self._pending_sudo_cmd: Optional[list[str]] = None
        self._pending_sudo_version: Optional[str] = None
        self._pending_sudo_info = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Updating…", id="update-overlay-title"),
            Static("Checking for updates…", id="update-overlay-status"),
            ProgressBar(id="update-overlay-progress", total=100, show_eta=False, show_percentage=True),
            Static("", id="update-overlay-message"),
            Container(
                Input(
                    placeholder="Password",
                    password=True,
                    id="update-overlay-password",
                ),
                id="update-overlay-password-container",
            ),
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
        self.query_one("#update-overlay-password-container").remove_class("visible")
        self._pending_sudo_cmd = None
        self._pending_sudo_version = None
        self._pending_sudo_info = None
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
            self._handle_appimage_update(latest_version)
            return

        # AUR needs sudo — prompt for password inside the overlay
        if install_info.method == InstallMethod.AUR:
            self._prompt_sudo_update(latest_version, install_info)
            return

        # Homebrew doesn't need sudo — run directly
        if install_info.method == InstallMethod.HOMEBREW:
            self._run_auto_update(latest_version, install_info)
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
        elif install_info.method == InstallMethod.HOMEBREW:
            method_name = "brew"
            commands = [["brew", "upgrade", "hei-datahub"]]
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

    def _prompt_sudo_update(self, latest_version: str, install_info) -> None:
        """Show a password prompt so the user can authorize a sudo update."""
        self._pending_sudo_version = latest_version
        self._pending_sudo_info = install_info

        # Build the command that will run under sudo
        cmd = install_info.update_command  # e.g. "yay -Syu hei-datahub"
        self._pending_sudo_cmd = cmd.split() if cmd else ["yay", "-Syu", "--noconfirm", "hei-datahub"]

        def show_prompt():
            self.query_one("#update-overlay-title", Static).update(
                f"v{latest_version} — Password Required"
            )
            self._update_progress("Enter your password to update", 20)
            pwd_container = self.query_one("#update-overlay-password-container")
            pwd_container.add_class("visible")
            pwd_input = self.query_one("#update-overlay-password", Input)
            pwd_input.value = ""
            pwd_input.focus()

        self.app.call_from_thread(show_prompt)

    @on(Input.Submitted, "#update-overlay-password")
    def _on_password_submitted(self, event: Input.Submitted) -> None:
        """Handle password submission — run the sudo update."""
        password = event.value
        event.input.value = ""

        # Hide the password field immediately
        self.query_one("#update-overlay-password-container").remove_class("visible")

        if not password:
            self._update_progress("Password cannot be empty", 20)
            return

        if self._pending_sudo_cmd and self._pending_sudo_version:
            self._run_sudo_update(
                password,
                self._pending_sudo_cmd,
                self._pending_sudo_version,
                self._pending_sudo_info,
            )

    @work(exclusive=True, thread=True)
    def _run_sudo_update(
        self, password: str, cmd: list[str], latest_version: str, install_info
    ) -> None:
        """Run an update command via sudo, piping the password to stdin."""
        self._updating = True
        _debug = os.environ.get("HEI_DEBUG_UPDATER", "").strip() in ("1", "true", "yes")

        method_name = cmd[0]  # e.g. "yay" or "paru"
        # Wrap in sudo -S so password is read from stdin.
        # --noconfirm avoids interactive prompts from pacman/yay.
        sudo_cmd = ["sudo", "-S"] + cmd
        if "--noconfirm" not in sudo_cmd:
            sudo_cmd.insert(2, "--noconfirm") if method_name in ("yay", "paru", "pacman") else None

        self._set_progress(f"Updating via {method_name}…", 30)
        logger.info(f"Sudo update: {' '.join(sudo_cmd)}")

        try:
            process = subprocess.Popen(
                sudo_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ},
            )
            stdout, stderr = process.communicate(
                input=password + "\n", timeout=300
            )

            if _debug:
                logger.warning(f"[DEBUG-UPDATER] stdout: {stdout[:300]}")
                logger.warning(f"[DEBUG-UPDATER] stderr: {stderr[:300]}")

            if process.returncode == 0:
                self._show_success(latest_version)
            else:
                # Check for wrong-password errors
                lower_err = (stderr + stdout).lower()
                if "incorrect password" in lower_err or "sorry" in lower_err:
                    self._show_error("Incorrect password")
                else:
                    short_err = stderr.strip().split("\n")[-1][:80] if stderr.strip() else ""
                    msg = f"Update via {method_name} failed."
                    if short_err:
                        msg += f"\n{short_err}"
                    self._show_error(msg)

        except subprocess.TimeoutExpired:
            self._show_error(f"Update timed out ({method_name})")
        except FileNotFoundError:
            self._show_error(f"Command not found: {sudo_cmd[0]}")
        except Exception as e:
            logger.error(f"Sudo update error: {e}")
            self._show_error(str(e))

    def _handle_appimage_update(self, latest_version: str) -> None:
        """Download the new AppImage from GitHub and replace the current one."""
        import tempfile
        import requests
        from pathlib import Path
        from hei_datahub.version import GITHUB_REPO

        _debug = os.environ.get("HEI_DEBUG_UPDATER", "").strip() in ("1", "true", "yes")

        appimage_path = os.environ.get("APPIMAGE")
        if not appimage_path:
            self._show_error("Cannot determine AppImage path")
            return

        appimage_file = Path(appimage_path)
        if not appimage_file.exists():
            self._show_error(f"AppImage not found: {appimage_path}")
            return

        # Find the AppImage download URL from GitHub releases
        self._set_progress("Fetching release info…", 25)
        asset_pattern = "AppImage"

        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
            headers = {
                "Accept": "application/vnd.github+json",
                "User-Agent": f"Hei-DataHub/{latest_version}",
            }
            resp = requests.get(api_url, headers=headers, timeout=15)
            resp.raise_for_status()
            releases = resp.json()
        except Exception as e:
            self._show_error(f"Failed to fetch releases: {e}")
            return

        # Find the release matching latest_version
        download_url = None
        file_size = 0
        for release in releases:
            tag = release.get("tag_name", "")
            if tag == latest_version or tag.lstrip("v") == latest_version:
                for asset in release.get("assets", []):
                    name = asset.get("name", "")
                    if asset_pattern in name and "x86_64" in name:
                        download_url = asset.get("browser_download_url")
                        file_size = asset.get("size", 0)
                        break
                break

        if not download_url:
            logger.warning(f"No AppImage asset found for {latest_version}")
            from hei_datahub.infra.install_method import get_install_info
            self._show_manual_instructions(latest_version, get_install_info())
            return

        # Download to a temporary file
        self._set_progress("Downloading AppImage…", 30)
        mb_total = file_size / (1024 * 1024) if file_size else 0

        try:
            dl_resp = requests.get(download_url, stream=True, timeout=300)
            dl_resp.raise_for_status()
            total = int(dl_resp.headers.get("content-length", 0)) or file_size

            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".AppImage")
            downloaded = 0
            with os.fdopen(tmp_fd, "wb") as f:
                for chunk in dl_resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = 30 + int(60 * downloaded / total)
                            mb_done = downloaded / (1024 * 1024)
                            self._set_progress(
                                f"Downloading: {mb_done:.1f}/{mb_total:.1f} MB",
                                min(pct, 90),
                            )
        except Exception as e:
            self._show_error(f"Download failed: {e}")
            return

        # Replace the old AppImage with the new one
        self._set_progress("Installing…", 92)
        tmp_file = Path(tmp_path)

        try:
            # Make the new file executable
            os.chmod(tmp_path, 0o755)

            # Back up current AppImage (just rename, same dir)
            backup_path = appimage_file.with_suffix(".AppImage.bak")
            try:
                if backup_path.exists():
                    backup_path.unlink()
                appimage_file.rename(backup_path)
            except PermissionError:
                # May need sudo to replace system-installed AppImage
                self._show_error(
                    f"Permission denied replacing {appimage_path}\n"
                    "Try running with sudo or move the AppImage."
                )
                tmp_file.unlink(missing_ok=True)
                return

            # Move new AppImage into place
            import shutil
            shutil.move(str(tmp_file), str(appimage_file))

            if _debug:
                logger.warning(f"[DEBUG-UPDATER] Replaced {appimage_path}")

            # Clean up backup
            backup_path.unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Failed to replace AppImage: {e}")
            # Try to restore backup
            if backup_path.exists() and not appimage_file.exists():
                backup_path.rename(appimage_file)
            tmp_file.unlink(missing_ok=True)
            self._show_error(f"Install failed: {e}")
            return

        self._show_success(latest_version)

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
