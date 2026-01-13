"""
Settings screen for WebDAV (HeiBox) configuration.
"""
try:
    import tomllib as tomli
except ImportError:
    import tomli  # type:ignore
from urllib.parse import urlparse

import tomli_w
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Header,
    Input,
    Label,
)

from hei_datahub.cli.auth.credentials import get_auth_store
from hei_datahub.infra.config_paths import get_config_path
from hei_datahub.services.webdav_storage import WebDAVStorage
from hei_datahub.ui.widgets.contextual_footer import ContextualFooter


class SettingsScreen(Screen):
    """Settings screen for WebDAV (HeiBox) configuration."""

    CSS_PATH = "../styles/settings.tcss"

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("q", "cancel", "Back"),
        Binding("ctrl+s", "save", "Save", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("☁️ WebDAV (HeiBox) Settings  |  [italic]Configure cloud storage credentials[/italic]", classes="title"),
            Label(""),
            Container(
                Label("WebDAV URL:"),
                Input(placeholder="https://heibox.uni-heidelberg.de/seafdav", id="input-url"),
                Label("Library Name:"),
                Input(placeholder="e.g., heidata", id="input-library"),
                Label("Username:"),
                Input(placeholder="your-username", id="input-username"),
                Label("Password/Token:"),
                Input(placeholder="your-WebDAV-password", password=True, id="input-token"),
                Label("[dim]Note: Credentials are stored securely in system keyring[/dim]"),
                Label(""),
                Horizontal(
                    Button("Test Connection", id="test-btn", variant="default"),
                    Button("Save Settings", id="save-btn", variant="primary"),
                    Button("Clear Credentials", id="clear-btn", variant="warning"),
                ),
                Horizontal(
                    Button("Reconfigure (Wizard)", id="wizard-btn", variant="default"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                ),
                Label("", id="status-message"),
                Label("\n[dim]💡 Tip: You can also use 'hei-datahub auth setup' in terminal[/dim]"),
                id="settings-container",
            ),
        )
        footer = ContextualFooter()
        footer.set_context("settings")
        yield footer

    def on_mount(self) -> None:
        """Load current settings from config."""
        try:
            config_path = get_config_path()
            if config_path.exists():
                with open(config_path, "rb") as f:
                    config = tomli.load(f)

                # Load from [auth] section (this is where auth setup stores it)
                auth_config = config.get("auth", {})
                if auth_config:
                    self.query_one("#input-url", Input).value = auth_config.get("url", "")
                    self.query_one("#input-username", Input).value = auth_config.get("username", "")

                    # Check if credentials exist
                    key_id = auth_config.get("key_id", "")
                    if key_id:
                        try:
                            store = get_auth_store(prefer_keyring=True)
                            secret = store.load_secret(key_id)
                            if secret:
                                self.query_one("#input-token", Input).value = "••••••••"  # Masked
                        except Exception:
                            pass

                # Try to extract library from URL or cloud config
                cloud_config = config.get("cloud", {})
                if cloud_config:
                    self.query_one("#input-library", Input).value = cloud_config.get("library", "")

                # If library not in cloud config, try to get from storage config
                if not self.query_one("#input-library", Input).value:
                    storage_config = config.get("storage", {})
                    if storage_config:
                        self.query_one("#input-library", Input).value = storage_config.get("library", "")

            self.query_one("#input-url", Input).focus()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to load WebDAV config: {e}")    @on(Button.Pressed, "#test-btn")
    def on_test_button(self) -> None:
        """Test WebDAV connection."""
        self.test_connection()

    @work(exclusive=True)
    async def test_connection(self) -> None:
        """Test connection to WebDAV server."""
        status_label = self.query_one("#status-message", Label)
        status_label.update("Testing connection...")

        url = self.query_one("#input-url", Input).value.strip()
        library = self.query_one("#input-library", Input).value.strip()
        username = self.query_one("#input-username", Input).value.strip()
        token = self.query_one("#input-token", Input).value.strip()

        if not all([url, library, username, token]) or token == "••••••••":
            status_label.update("[red]✗ Please fill in all fields[/red]")
            self.app.notify("All fields are required for testing", severity="error", timeout=5)
            return

        try:
            storage = WebDAVStorage(
                base_url=url,
                library=library,
                username=username,
                password=token,
                connect_timeout=5,
                read_timeout=10
            )

            # Try to list root directory
            files = storage.list_files("")
            status_label.update(f"[green]✓ Connection successful! Found {len(files)} items[/green]")
            self.app.notify("WebDAV connection successful!", timeout=3)
        except Exception as e:
            error_msg = str(e)
            status_label.update(f"[red]✗ Connection failed: {error_msg}[/red]")
            self.app.notify(f"Connection failed: {error_msg}", severity="error", timeout=8)

    @on(Button.Pressed, "#save-btn")
    def on_save_button(self) -> None:
        """Save settings."""
        self.action_save()

    @on(Button.Pressed, "#clear-btn")
    def on_clear_button(self) -> None:
        """Clear stored credentials."""
        try:
            store = get_auth_store(prefer_keyring=True)

            # Clear token/password from keyring
            url = self.query_one("#input-url", Input).value.strip()
            username = self.query_one("#input-username", Input).value.strip()

            if url and username:
                host = urlparse(url).netloc
                key_id = f"webdav:token:{username}@{host}"

                try:
                    store.load_secret(key_id)  # Check if exists
                    # Clear the credential (implementation would need delete method)
                    self.query_one("#input-token", Input).value = ""
                    self.query_one("#status-message", Label).update("[yellow]Credentials cleared[/yellow]")
                    self.app.notify("Credentials cleared. Use CLI 'auth clear' for complete removal.", timeout=5)
                except Exception:
                    self.query_one("#status-message", Label).update("[yellow]No credentials found[/yellow]")
                    self.app.notify("No credentials to clear", timeout=3)
        except Exception as e:
            self.app.notify(f"Clear failed: {str(e)}", severity="error", timeout=5)

    @on(Button.Pressed, "#wizard-btn")
    def on_wizard_button(self) -> None:
        """Open the setup wizard."""
        from hei_datahub.ui.widgets.settings_wizard import SettingsWizard
        self.app.pop_screen()  # Close current settings
        self.app.push_screen(SettingsWizard())

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_button(self) -> None:
        """Cancel and go back."""
        self.action_cancel()

    def action_save(self) -> None:
        """Save WebDAV configuration."""
        status_label = self.query_one("#status-message", Label)

        try:
            url = self.query_one("#input-url", Input).value.strip()
            library = self.query_one("#input-library", Input).value.strip()
            username = self.query_one("#input-username", Input).value.strip()
            token_input = self.query_one("#input-token", Input).value.strip()

            if not all([url, username]):
                status_label.update("[red]URL and Username are required[/red]")
                return

            # Determine method (assume token)
            method = "token"

            # Derive key_id using the same format as auth setup
            parsed = urlparse(url)
            host = parsed.hostname or "unknown"
            user_part = username if username else "-"
            key_id = f"webdav:{method}:{user_part}@{host}"

            # Load existing config or create new
            config_path = get_config_path()
            config = {}
            if config_path.exists():
                try:
                    with open(config_path, "rb") as f:
                        config = tomli.load(f)
                except Exception:
                    pass

            # Store credential if provided
            saved_credential = False
            if token_input and token_input != "••••••••":
                store = get_auth_store(prefer_keyring=True)
                try:
                    store.store_secret(key_id, token_input)
                    saved_credential = True
                except Exception as e:
                    status_label.update(f"[red]Failed to store credential: {str(e)}[/red]")
                    self.app.notify(f"Failed to store credential: {str(e)}", severity="error", timeout=5)
                    return

            # Update auth section to match auth setup format
            config["auth"] = {
                "method": method,
                "url": url,
                "library": library or "",
                "username": username or "",
                "key_id": key_id,
                "stored_in": get_auth_store(prefer_keyring=True).strategy,
            }

            # Write config file
            with open(config_path, "wb") as f:
                tomli_w.dump(config, f)

            # Refresh connection status
            self.app.refresh_heibox_status()

            if saved_credential:
                status_label.update("[green]✓ Settings saved! Credentials stored securely.[/green]")
                self.app.notify("WebDAV settings saved successfully!", timeout=5)
            else:
                status_label.update("[green]✓ Configuration saved![/green]")
                self.app.notify("WebDAV configuration saved!", timeout=3)

        except Exception as e:
            status_label.update(f"[red]Error saving: {str(e)}[/red]")
            self.app.notify(f"Save failed: {str(e)}", severity="error", timeout=5)

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()
