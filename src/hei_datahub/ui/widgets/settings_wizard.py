"""
Guided settings wizard with step-by-step WebDAV configuration.

This wizard configures WebDAV authentication for cloud storage.
It stores credentials in the same format as the CLI `hei-datahub auth setup` command.

Key points:
- Credentials are stored in the system keyring (encrypted)
- Config file stores non-sensitive metadata (URL, username, key_id, etc.)
- Uses same key_id format as CLI: webdav:{method}:{username}@{host}
- Compatible with storage_manager.py authentication checks
"""
import logging

try:
    import tomllib as tomli
except ImportError:
    import tomli  # type:ignore

import tomli_w
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from hei_datahub.cli.auth.credentials import get_auth_store
from hei_datahub.infra.config_paths import get_config_path
from hei_datahub.services.webdav_storage import WebDAVStorage

logger = logging.getLogger(__name__)


class SettingsWizard(Screen):
    """Step-by-step guided settings wizard for WebDAV configuration."""

    CSS_PATH = "../styles/settings_wizard.tcss"

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("q", "cancel", "Cancel"),
    ]

    current_step = reactive(1)
    total_steps = 4

    # Store values as we go
    url_value = reactive("")
    library_value = reactive("")
    username_value = reactive("")
    password_value = reactive("")

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            # Step 1: URL
            Container(
                Static("⚙️  WebDAV Setup - Step 1 of 4", classes="step-header"),
                Static("📍 WebDAV Server URL", classes="step-title"),
                Static(
                    "Enter your WebDAV server URL.\n"
                    "For HeiBox, use: https://heibox.uni-heidelberg.de/seafdav",
                    classes="step-description"
                ),
                Input(
                    value="https://heibox.uni-heidelberg.de/seafdav",
                    placeholder="https://heibox.uni-heidelberg.de/seafdav",
                    id="step1-url",
                    classes="wizard-input"
                ),
                Static("", id="step1-error", classes="error-message"),
                Horizontal(
                    Button("Next →", id="step1-next", variant="primary"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                    classes="button-row"
                ),
                id="step1-card",
                classes="wizard-card active"
            ),

            # Step 2: Library
            Container(
                Static("⚙️  WebDAV Setup - Step 2 of 4", classes="step-header"),
                Static("📚 Library Name", classes="step-title"),
                Static(
                    "Enter the library/folder name where your datasets are stored.\n"
                    "Common values: heidata, datasets, research",
                    classes="step-description"
                ),
                Input(
                    value="heidata",
                    placeholder="e.g., heidata",
                    id="step2-library",
                    classes="wizard-input"
                ),
                Static("", id="step2-error", classes="error-message"),
                Horizontal(
                    Button("← Back", id="step2-back", variant="default"),
                    Button("Next →", id="step2-next", variant="primary"),
                    classes="button-row"
                ),
                id="step2-card",
                classes="wizard-card hidden"
            ),

            # Step 3: Username
            Container(
                Static("⚙️  WebDAV Setup - Step 3 of 4", classes="step-header"),
                Static("👤 Username", classes="step-title"),
                Static(
                    "Enter your HeiBox username.\n"
                    "This is usually your university/organization username.",
                    classes="step-description"
                ),
                Input(
                    placeholder="your-username",
                    id="step3-username",
                    classes="wizard-input"
                ),
                Static("", id="step3-error", classes="error-message"),
                Horizontal(
                    Button("← Back", id="step3-back", variant="default"),
                    Button("Next →", id="step3-next", variant="primary"),
                    classes="button-row"
                ),
                id="step3-card",
                classes="wizard-card hidden"
            ),

            # Step 4: Password & Test
            Container(
                Static("⚙️  WebDAV Setup - Step 4 of 4", classes="step-header"),
                Static("🔐 HeiBox WebDAV Password", classes="step-title"),
                Static(
                    "Enter your HeiBox WebDAV password (NOT your login password).\n"
                    "Find it in HeiBox web interface: Settings → WebDAV Password.",
                    classes="step-description"
                ),
                Input(
                    placeholder="your-webdav-password",
                    password=True,
                    id="step4-password",
                    classes="wizard-input"
                ),
                Static("", id="step4-error", classes="error-message"),
                Static("", id="step4-status", classes="status-message"),
                Horizontal(
                    Button("← Back", id="step4-back", variant="default"),
                    Button("Test Connection", id="test-btn", variant="default"),
                    Button("Save & Finish", id="save-btn", variant="primary"),
                    classes="button-row"
                ),
                id="step4-card",
                classes="wizard-card hidden"
            ),

            id="wizard-scroll"
        )

    def on_mount(self) -> None:
        """Focus the first input on mount and load existing config."""
        # Load existing config if available (only override defaults if config exists)
        try:
            config_path = get_config_path()
            if config_path.exists():
                with open(config_path, "rb") as f:
                    config = tomli.load(f)

                # Override URL default if config has different value
                auth_config = config.get("auth", {})
                url = auth_config.get("url")
                if url and url != "https://heibox.uni-heidelberg.de/seafdav":
                    self.query_one("#step1-url", Input).value = url

                # Override library default if config has different value
                cloud_config = config.get("cloud", {})
                library = cloud_config.get("library")
                if library and library != "heidata":
                    self.query_one("#step2-library", Input).value = library

                # Pre-fill username if available (no default for this)
                if auth_config.get("username"):
                    self.query_one("#step3-username", Input).value = auth_config.get("username", "")
        except Exception as e:
            logger.debug(f"Could not load existing config: {e}")

        self.query_one("#step1-url", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle all button presses."""
        button_id = event.button.id

        # IMMEDIATE feedback
        self.app.notify(f"🔘 Button clicked: {button_id}", timeout=2)
        logger.error(f"!!! BUTTON PRESSED: {button_id} !!!")

        if button_id == "step1-next":
            logger.info("Calling step1_next")
            self.step1_next()
        elif button_id == "step2-next":
            self.step2_next()
        elif button_id == "step2-back":
            self.step2_back()
        elif button_id == "step3-next":
            self.step3_next()
        elif button_id == "step3-back":
            self.step3_back()
        elif button_id == "step4-back":
            self.step4_back()
        elif button_id == "test-btn":
            # Test connection in background worker
            logger.error("!!! TEST BUTTON - CALLING run_worker(test_connection) !!!")
            # Update UI immediately
            error_label = self.query_one("#step4-error", Static)
            status_label = self.query_one("#step4-status", Static)
            error_label.update("")
            status_label.update("🔄 Testing connection...")
            self.app.notify("🔄 Starting connection test...", timeout=2)
            self.run_worker(self._test_connection_worker(), exclusive=True)
        elif button_id == "save-btn":
            # Save settings in background worker
            logger.error("!!! SAVE BUTTON - CALLING run_worker(save_settings) !!!")
            # Update UI immediately
            error_label = self.query_one("#step4-error", Static)
            status_label = self.query_one("#step4-status", Static)
            error_label.update("")
            status_label.update("💾 Saving settings...")
            self.app.notify("💾 Starting save process...", timeout=2)
            self.run_worker(self._save_settings_worker(), exclusive=True)
        elif button_id == "cancel-btn":
            self.action_cancel()
        else:
            logger.warning(f"Unknown button id: {button_id}")

    # Step 1: URL
    def step1_next(self) -> None:
        """Validate URL and move to step 2."""
        logger.info("step1_next called")
        url_input = self.query_one("#step1-url", Input)
        url = url_input.value.strip()
        error_label = self.query_one("#step1-error", Static)

        logger.info(f"URL value: '{url}'")

        if not url:
            error_label.update("⚠️  Please enter a WebDAV URL")
            return

        if not url.startswith(("http://", "https://")):
            error_label.update("⚠️  URL must start with http:// or https://")
            return

        # Store value and move to next step
        self.url_value = url
        error_label.update("")
        logger.info("Transitioning to step 2")
        self._transition_to_step(2)

    # Step 2: Library
    def step2_next(self) -> None:
        """Validate library and move to step 3."""
        library_input = self.query_one("#step2-library", Input)
        library = library_input.value.strip()
        error_label = self.query_one("#step2-error", Static)

        if not library:
            error_label.update("⚠️  Please enter a library name")
            return

        # Store value and move to next step
        self.library_value = library
        error_label.update("")
        self._transition_to_step(3)

    def step2_back(self) -> None:
        """Go back to step 1."""
        self._transition_to_step(1)

    # Step 3: Username
    def step3_next(self) -> None:
        """Validate username and move to step 4."""
        username_input = self.query_one("#step3-username", Input)
        username = username_input.value.strip()
        error_label = self.query_one("#step3-error", Static)

        if not username:
            error_label.update("⚠️  Please enter a username")
            return

        # Store value and move to next step
        self.username_value = username
        error_label.update("")
        self._transition_to_step(4)

    def step3_back(self) -> None:
        """Go back to step 2."""
        self._transition_to_step(2)

    # Step 4: Password & Save
    def step4_back(self) -> None:
        """Go back to step 3."""
        self._transition_to_step(3)

    async def _test_connection_worker(self) -> None:
        """Test the WebDAV connection with proper UI updates."""
        error_label = self.query_one("#step4-error", Static)
        status_label = self.query_one("#step4-status", Static)

        try:
            # Get all current values from inputs
            url = self.query_one("#step1-url", Input).value.strip()
            library = self.query_one("#step2-library", Input).value.strip()
            username = self.query_one("#step3-username", Input).value.strip()
            password_input = self.query_one("#step4-password", Input)
            password = password_input.value.strip()

            if not password:
                error_label.update("⚠️  Please enter a password")
                self.app.notify("⚠️  Password required", timeout=3, severity="warning")
                return

            status_label.update("🔄 Authenticating with WebDAV server...")
            self.app.notify("🔄 Testing credentials...", timeout=2)

            # Test WebDAV connection
            storage = WebDAVStorage(
                base_url=url,
                username=username,
                password=password,
                library=library
            )

            status_label.update(f"🔄 Accessing library '{library}'...")

            try:
                # Try to list root directory
                entries = storage.listdir("")

                status_label.update(f"✅ Connection successful! Found {len(entries)} items in '{library}'.")
                error_label.update("")
                self.app.notify(f"✅ Connected! Found {len(entries)} items", timeout=3, severity="information")

            except Exception as list_err:
                # Check if it's a 404 (library doesn't exist)
                if "404" in str(list_err) or "not found" in str(list_err).lower():
                    error_label.update(f"❌ Library '{library}' not found. Check the library name.")
                    self.app.notify(f"❌ Library '{library}' doesn't exist", timeout=5, severity="error")
                else:
                    raise  # Re-raise other errors

        except Exception as e:
            error_msg = str(e)

            # Provide helpful error messages based on error type
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_label.update("❌ Invalid username or password")
                self.app.notify("❌ Authentication failed", timeout=5, severity="error")
            elif "403" in error_msg or "Forbidden" in error_msg:
                error_label.update("❌ Access denied. Check your permissions.")
                self.app.notify("❌ Access forbidden", timeout=5, severity="error")
            elif "timeout" in error_msg.lower():
                error_label.update("❌ Connection timeout. Check the URL.")
                self.app.notify("❌ Connection timeout", timeout=5, severity="error")
            elif "connection" in error_msg.lower():
                error_label.update("❌ Cannot reach server. Check the URL.")
                self.app.notify("❌ Connection failed", timeout=5, severity="error")
            else:
                error_label.update(f"❌ Connection failed: {error_msg}")
                self.app.notify(f"❌ Error: {error_msg[:50]}", timeout=5, severity="error")

            status_label.update("")

    async def _save_settings_worker(self) -> None:
        """Save settings and close wizard with proper UI updates."""
        error_label = self.query_one("#step4-error", Static)
        status_label = self.query_one("#step4-status", Static)

        try:
            # Get all current values from inputs
            url = self.query_one("#step1-url", Input).value.strip()
            library = self.query_one("#step2-library", Input).value.strip()
            username = self.query_one("#step3-username", Input).value.strip()
            password_input = self.query_one("#step4-password", Input)
            password = password_input.value.strip()

            if not password:
                error_label.update("⚠️  Please enter a password")
                self.app.notify("⚠️  Password required", timeout=3, severity="warning")
                return

            status_label.update("💾 Creating config directory...")

            # Save to config file
            config_path = get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)

            status_label.update("💾 Loading existing config...")
            # Load existing config or create new
            if config_path.exists():
                with open(config_path, "rb") as f:
                    config = tomli.load(f)
            else:
                config = {}

            status_label.update("💾 Generating credentials...")
            # Generate key_id for credential storage (same format as CLI)
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname or "unknown"
            method = "password"  # GUI wizard uses password authentication
            key_id = f"heibox:{method}:{username}@{host}"

            status_label.update("💾 Storing password securely...")
            # Store password in keyring
            store = get_auth_store(prefer_keyring=True)
            store.store_secret(key_id, password)

            status_label.update("💾 Updating config file...")
            # Update config with auth section (compatible with CLI format)
            config["auth"] = {
                "method": method,
                "url": url,
                "username": username,
                "library": library,
                "key_id": key_id,
                "stored_in": store.strategy,
            }

            # Update cloud section (for backward compatibility)
            config["cloud"] = {
                "library": library
            }

            status_label.update("💾 Writing config to disk...")
            # Save config
            with open(config_path, "wb") as f:
                tomli_w.dump(config, f)

            status_label.update("✅ Settings saved successfully!")
            error_label.update("")
            self.app.notify("✅ WebDAV settings configured!", timeout=3, severity="information")

            # Close wizard after a brief delay
            self.set_timer(1.5, self._close_wizard)

        except Exception as e:
            error_msg = str(e)
            status_label.update("")
            error_label.update(f"❌ Failed to save: {error_msg}")
            self.app.notify(f"❌ Save failed: {error_msg}", timeout=5, severity="error")

    def _close_wizard(self) -> None:
        """Close the wizard screen."""
        try:
            self.app.pop_screen()
        except Exception as e:
            self.app.notify(f"❌ Failed to close wizard: {e}", timeout=3, severity="error")

    async def test_connection(self) -> None:
        """Test the WebDAV connection."""
        logger.info("=== test_connection STARTED ===")

        # Get all current values from inputs
        url = self.query_one("#step1-url", Input).value.strip()
        library = self.query_one("#step2-library", Input).value.strip()
        username = self.query_one("#step3-username", Input).value.strip()
        password_input = self.query_one("#step4-password", Input)
        password = password_input.value.strip()
        error_label = self.query_one("#step4-error", Static)
        status_label = self.query_one("#step4-status", Static)

        logger.info(f"Testing connection with URL: {url}, username: {username}, library: {library}, password length: {len(password)}")

        if not password:
            error_label.update("⚠️  Please enter a password")
            logger.warning("No password entered")
            return

        error_label.update("")
        status_label.update("🔄 Testing connection...")
        self.refresh()

        try:
            # Test WebDAV connection
            logger.info("Creating WebDAVStorage instance...")
            storage = WebDAVStorage(
                base_url=url,
                username=username,
                password=password,
                library=library
            )

            # Try to list root directory
            logger.info("Listing root directory...")
            entries = storage.listdir("")

            logger.info(f"Connection test succeeded! Found {len(entries)} items")
            status_label.update(f"✅ Connection successful! Found {len(entries)} items.")
            error_label.update("")
            self.refresh()

        except Exception as e:
            logger.error(f"Connection test failed: {e}", exc_info=True)
            status_label.update("")
            error_label.update(f"❌ Connection failed: {str(e)}")
            self.refresh()

    async def save_settings(self) -> None:
        """Save settings and close wizard."""
        logger.info("=== save_settings STARTED ===")

        # Get all current values from inputs
        url = self.query_one("#step1-url", Input).value.strip()
        library = self.query_one("#step2-library", Input).value.strip()
        username = self.query_one("#step3-username", Input).value.strip()
        password_input = self.query_one("#step4-password", Input)
        password = password_input.value.strip()
        error_label = self.query_one("#step4-error", Static)
        status_label = self.query_one("#step4-status", Static)

        logger.info(f"Saving settings for URL: {url}, username: {username}, library: {library}, password length: {len(password)}")

        if not password:
            error_label.update("⚠️  Please enter a password")
            logger.warning("No password entered")
            return

        error_label.update("")
        status_label.update("💾 Saving settings...")
        self.refresh()

        try:
            # Save to config file
            logger.info("Creating config directory...")
            config_path = get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Load existing config or create new
            if config_path.exists():
                logger.info("Loading existing config...")
                with open(config_path, "rb") as f:
                    config = tomli.load(f)
            else:
                logger.info("Creating new config...")
                config = {}

            # Generate key_id for credential storage (same format as CLI)
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname or "unknown"
            method = "password"  # GUI wizard uses password authentication
            key_id = f"webdav:{method}:{username}@{host}"
            logger.info(f"Generated key_id: {key_id}")

            # Store password in keyring
            logger.info("Storing password in keyring...")
            store = get_auth_store(prefer_keyring=True)
            store.store_secret(key_id, password)

            # Update config with auth section (compatible with CLI format)
            config["auth"] = {
                "method": method,
                "url": url,
                "username": username,
                "library": library,
                "key_id": key_id,
                "stored_in": store.strategy,
            }

            # Update cloud section (for backward compatibility)
            config["cloud"] = {
                "library": library
            }

            # Save config
            logger.info(f"Saving config to {config_path}...")
            with open(config_path, "wb") as f:
                tomli_w.dump(config, f)

            logger.info("Settings saved successfully!")
            status_label.update("✅ Settings saved successfully!")
            error_label.update("")
            self.refresh()

            # Notify parent app
            self.app.notify("✅ WebDAV settings configured successfully!", timeout=3)

            # Close wizard after a brief delay
            self.set_timer(1.5, self.action_cancel)

        except Exception as e:
            logger.error(f"Save failed: {e}", exc_info=True)
            status_label.update("")
            error_label.update(f"❌ Failed to save: {str(e)}")
            self.refresh()

    def action_cancel(self) -> None:
        """Cancel wizard and return to home."""
        self.app.pop_screen()

    def _transition_to_step(self, step: int) -> None:
        """Transition to a specific step with animation."""
        # Hide all cards
        for i in range(1, self.total_steps + 1):
            card = self.query_one(f"#step{i}-card", Container)
            if i == step:
                card.remove_class("hidden")
                card.add_class("active")
                # Focus the input in the new step
                try:
                    input_widget = card.query_one("Input", Input)
                    input_widget.focus()
                except Exception:
                    pass
            else:
                card.remove_class("active")
                card.add_class("hidden")

        self.current_step = step
