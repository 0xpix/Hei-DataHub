"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging

from textual import work
from textual.app import App
from textual.binding import Binding
from textual.events import Resize
from textual.reactive import reactive

from hei_datahub.infra.db import ensure_database
from hei_datahub.services.config import get_config
from hei_datahub.ui.views.home import HomeScreen

logger = logging.getLogger(__name__)


class DataHubApp(App):
    """Main TUI application with Neovim-style keybindings."""

    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "../styles/base.tcss"

    BINDINGS = [
        Binding("ctrl+p", "commands", "Open Command Palette", priority=True),
        Binding("ctrl+t", "theme_palette", "Change Theme", priority=True),
        Binding("ctrl+s", "settings", "Settings"),
    ]

    # Track WebDAV/Heibox connection status
    heibox_connected = reactive(False)

    # Track update availability (set by silent update check)
    update_available = reactive(False)
    latest_version = reactive("")

    def on_resize(self, event: Resize) -> None:
        """Adjust layout based on window size."""
        # TODO: Implement responsive layout changes for future versions for now let's make it 10 (width) x 35 (height) (170 was for my laptop)
        if event.size.width < 170 or event.size.height < 35:
            self.add_class("compact-layout")
        else:
            self.remove_class("compact-layout")

    def action_commands(self) -> None:
        """Open the custom command palette."""
        from hei_datahub.ui.widgets.command_palette import CustomCommandPalette

        def on_command_selected(action: str | None) -> None:
            if action:
                # Schedule execution on the next tick to ensure screen stack and focus are settled
                self.call_later(self._exec_command, action)

        self.push_screen(CustomCommandPalette(), callback=on_command_selected)

    def _exec_command(self, action: str) -> None:
        """Execute command from palette."""
        logger.debug(f"Executing palette command: {action}")

        try:
            # 1. PRIORITY: Check if the active Screen has a direct handler.
            # This bypasses focused widgets (like DataTable) that might swallow the event.
            if self.screen:
                method_name = f"action_{action}"
                if hasattr(self.screen, method_name):
                    getattr(self.screen, method_name)()
                    return

            # 2. Fallback: Try focused widget
            if self.focused:
                if self.focused.run_action(action):
                    return

            # 3. Fallback: Try screen (via bubbling if not caught above)
            if self.screen:
                if self.screen.run_action(action):
                    return

            # 4. Try the app (global scope)
            if self.run_action(action):
                return
        except Exception as e:
            logger.exception(f"Error executing action '{action}'")
            self.notify(f"Error executing '{action}': {e}", severity="error")
            return

        # If nothing handled it
        logger.warning(f"Action '{action}' was not handled by any widget/screen/app")
        self.notify(f"Command '{action}' not found or failed", severity="error")

    def action_theme_palette(self) -> None:
        """Open the theme selection palette."""
        from hei_datahub.ui.widgets.theme_palette import ThemePalette
        self.push_screen(ThemePalette())

    def action_settings(self) -> None:
        """Open settings menu (Global)."""
        self.notify("Opening Settings...", timeout=1)
        try:
            from hei_datahub.ui.utils.settings_router import open_settings_screen
            open_settings_screen(self)
        except Exception as e:
            self.notify(f"Error opening settings: {e}", severity="error")

    def on_mount(self) -> None:
        """Initialize the app."""
        # Check initial size for compact mode
        if self.app.size.width < 120 or self.app.size.height < 35:
            self.add_class("compact-layout")
            logger.info("Enabled automatic compact layout")

        # Register custom themes first
        from hei_datahub.ui.themes import register_custom_themes
        register_custom_themes(self)

        # Initialize logging
        from hei_datahub import __version__
        from hei_datahub.app.runtime import log_startup, setup_logging
        from hei_datahub.app.settings import get_github_config

        config = get_github_config()
        setup_logging(debug=config.debug_logging)
        log_startup(__version__)

        # Load user configuration
        self._load_config()

        # Ensure database is set up
        try:
            ensure_database()

            # Check if we need to do initial indexing
            from hei_datahub.infra.index import reindex_all
            from hei_datahub.infra.store import list_datasets

            datasets = list_datasets()
            if datasets:
                # Reindex on startup to ensure consistency
                count, errors = reindex_all()
                if errors:
                    self.notify(f"Indexed {count} datasets with {len(errors)} errors", severity="warning", timeout=5)
        except Exception as e:
            self.notify(f"Database initialization error: {str(e)}", severity="error", timeout=10)

        # Start background indexer (FAST - non-blocking)
        import asyncio

        from hei_datahub.services.indexer import get_indexer, start_background_indexer
        try:
            # Force a fresh index on every startup for cloud datasets
            logger.info("Forcing fresh reindex on startup")

            # Reset the indexer flags to force reindexing
            indexer = get_indexer()
            indexer._remote_indexed = False
            indexer._local_indexed = False

            # Start the background indexer which will rebuild the index
            asyncio.create_task(start_background_indexer())
            logger.info("Background indexer started with forced reindex")
        except Exception as e:
            logger.warning(f"Failed to start background indexer: {e}")

        # Check WebDAV/Heibox connection status (async — avoids blocking on_mount)
        self.check_heibox_connection_async()

        # Apply theme from config (safely)
        try:
            # Load theme from config, defaulting to 'gruvbox' if missing
            if self.config:
                theme_name = self.config.get("theme.name") or "gruvbox"
            else:
                theme_name = "gruvbox"

            # Apply it
            self.theme = theme_name
            logger.info(f"Startup: Applied theme '{self.theme}' from config")

        except Exception as e:
            logger.error(f"Startup: Failed to apply theme '{theme_name}': {e}. Falling back to default.")
            self.theme = "textual-dark"
        self.push_screen(HomeScreen())

        # Check for updates (async) - after screen is mounted
        logger.info(f"auto_check_updates={config.auto_check_updates}")
        if config.auto_check_updates:
            self.check_for_updates_async()

        # Startup pull prompt (async) - after screen is mounted
        self.startup_pull_check()

    @work(thread=True)
    def check_heibox_connection_async(self) -> None:
        """Check WebDAV/Heibox connection status in background thread."""
        self._do_heibox_check()

    def _do_heibox_check(self) -> None:
        """Check WebDAV/Heibox connection status (actual logic)."""
        try:
            from hei_datahub.infra.config_paths import get_config_path

            # Check if config exists
            config_path = get_config_path()
            if not config_path.exists():
                self.heibox_connected = False
                return

            # Try to load config
            try:
                import tomllib as tomli
            except ImportError:
                import tomli

            with open(config_path, "rb") as f:
                config = tomli.load(f)

            # Check if auth section exists
            if "auth" not in config:
                self.heibox_connected = False
                return

            auth_config = config.get("auth", {})
            url = auth_config.get("url")
            username = auth_config.get("username")
            key_id = auth_config.get("key_id")

            if not all([url, username, key_id]):
                self.heibox_connected = False
                return

            # Try to load credentials
            from hei_datahub.cli.auth.credentials import get_auth_store

            store = get_auth_store(prefer_keyring=True)
            credential = store.load_secret(key_id)

            if not credential:
                self.heibox_connected = False
                return

            # Quick connection test (HEAD request to server)
            from urllib.parse import urlparse

            import requests

            parsed = urlparse(url)
            test_url = f"{parsed.scheme}://{parsed.netloc}"

            try:
                response = requests.head(
                    test_url,
                    auth=(username, credential),
                    timeout=3,
                    verify=True
                )
                # Accept any non-error response (even 404 means server is reachable)
                self.heibox_connected = response.status_code < 500
            except requests.exceptions.RequestException:
                # Network error - server not reachable
                self.heibox_connected = False

        except Exception as e:
            logger.debug(f"Heibox connection check failed: {e}")
            self.heibox_connected = False

    def refresh_heibox_status(self) -> None:
        """Refresh Heibox connection status (called after auth setup)."""
        self._do_heibox_check()

        # Update home screen if it exists
        try:
            for screen in self.screen_stack:
                if isinstance(screen, HomeScreen):
                    screen.update_heibox_status()
        except Exception:
            pass

    @work(exclusive=True, thread=True)
    def check_for_updates_async(self) -> None:
        """
        Perform silent update check on app launch (non-blocking).

        Uses the new update_service with proper version comparison
        supporting tags like 0.64.11b.
        """
        logger.info("Starting silent update check on launch...")

        try:
            from hei_datahub.services.update_service import check_for_updates_silent
        except Exception as e:
            logger.error(f"Failed to import update_service: {e}", exc_info=True)
            return

        try:
            # force=True: always hit the network on app launch so a
            # freshly-published release is detected immediately instead
            # of being hidden behind the 8-hour throttle cache.
            result = check_for_updates_silent(force=True)

            if result is None:
                logger.warning("Update check returned None (throttled or failed)")
                return

            if result.error:
                logger.warning(f"Update check error: {result.error}")
                return

            # Update reactive state for UI components
            if result.has_update:
                logger.info(f"Update available: {result.latest_version} (current: {result.current_version})")
                self.update_available = True
                self.latest_version = result.latest_version

                # Notify home screen to update badge
                self._update_home_screen_badge()
            else:
                logger.info(f"App is up to date: {result.current_version}")
                self.update_available = False
                self.latest_version = result.latest_version

                # Hide badge if stale cache had shown one before this check
                self._hide_home_screen_badge()

        except Exception as e:
            logger.error(f"Silent update check failed: {e}", exc_info=True)
            # Fail silently - no UI impact

    def _update_home_screen_badge(self) -> None:
        """Notify home screen to show update badge.

        This is called from a @work(thread=True) context, so UI
        mutations must be dispatched to the main thread.
        """
        def _do_update():
            try:
                for screen in self.screen_stack:
                    if isinstance(screen, HomeScreen):
                        if hasattr(screen, 'show_update_badge'):
                            screen.show_update_badge(self.latest_version)
            except Exception as e:
                logger.debug(f"Could not update home screen badge: {e}")

        self.call_from_thread(_do_update)

    def _hide_home_screen_badge(self) -> None:
        """Hide update badge on home screen (e.g. stale cache was wrong).

        This is called from a @work(thread=True) context, so UI
        mutations must be dispatched to the main thread.
        """
        def _do_hide():
            try:
                for screen in self.screen_stack:
                    if isinstance(screen, HomeScreen):
                        if hasattr(screen, 'hide_update_badge'):
                            screen.hide_update_badge()
            except Exception as e:
                logger.debug(f"Could not hide home screen badge: {e}")

        self.call_from_thread(_do_hide)

    @work(exclusive=True, thread=True)
    def startup_pull_check(self) -> None:
        """Check if we should prompt for pull on startup - DISABLED (cloud-only via WebDAV)."""
        # No longer needed - using WebDAV sync instead of Git pull
        pass

    def _load_config(self) -> None:
        """Load and apply configuration settings."""
        try:
            self.config = get_config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = None

    def reload_configuration(self) -> None:
        """Reload configuration and refresh app state (e.g. after auth setup)."""
        logger.info("Reloading configuration...")

        # 1. Reload global config
        self._load_config()

        # 2. Check connection
        self.check_heibox_connection()

        # 3. Trigger background re-index
        import asyncio
        from hei_datahub.services.indexer import start_background_indexer

        # We need to reset the indexer state correctly
        try:
            from hei_datahub.services.indexer import get_indexer
            indexer = get_indexer()
            indexer._remote_indexed = False
            # We don't necessarily want to wipe local index, but we do want to fetch remote
        except Exception:
            pass

        asyncio.create_task(start_background_indexer())

        # 4. Refresh Home Screen (if active)
        if hasattr(self, 'screen_stack'):
            for screen in self.screen_stack:
                if isinstance(screen, HomeScreen):
                    screen.update_heibox_status()
                    # Force a check of the indexer which should pick up new data
                    if hasattr(screen, '_check_indexer_and_reload'):
                        screen._check_indexer_and_reload()

    def apply_theme(self, theme_name: str) -> None:
        """
        Apply a theme dynamically without restart.

        Args:
            theme_name: Name of the theme to apply
        """
        try:
            # Reload config to pick up the latest changes
            from hei_datahub.services.config import reload_config
            self.config = reload_config()

            # Update the app's theme attribute (Textual built-in)
            self.theme = theme_name

            # Refresh all screens to apply new theme
            self.refresh()

            # Force refresh of CSS variables if needed
            for screen in self.screen_stack:
                screen.refresh()

            self.notify(f"Theme '{theme_name}' applied!", timeout=2)

        except Exception as e:
            self.notify(f"Failed to apply theme: {str(e)}", severity="error", timeout=5)

    def reload_keybindings(self) -> None:
        """
        Reload keybindings dynamically without restart.

        This recreates the HomeScreen with new bindings from the config file.
        """
        try:
            # Reload config to pick up the latest changes
            from hei_datahub.services.config import reload_config
            self.config = reload_config()

            # Check if we're currently on the HomeScreen
            is_on_home = isinstance(self.screen, HomeScreen)

            if is_on_home:
                # Pop the current HomeScreen and push a new one with updated bindings
                # This is necessary because BINDINGS is a class attribute set at definition time

                # First, we need to reload the HomeScreen class with new bindings
                # Since Python doesn't easily allow class redefinition, we'll use a workaround:
                # Create a new HomeScreen instance which will pick up the updated bindings

                # Store current state if needed (search text, etc.)

                # Pop current home screen
                self.pop_screen()

                # Reload the module to pick up new bindings
                import importlib

                import hei_datahub.ui.views.home as home_module
                importlib.reload(home_module)

                # Push new home screen with updated bindings
                from hei_datahub.ui.views.home import HomeScreen as NewHomeScreen
                self.push_screen(NewHomeScreen())

                self.notify("Keybindings reloaded successfully!", timeout=3)
            else:
                # Not on home screen, just notify that changes will apply on next visit
                self.notify(
                    "Keybindings updated! Changes will apply when you return to home screen.",
                    timeout=5
                )

        except Exception as e:
            self.notify(f"Failed to reload keybindings: {str(e)}", severity="error", timeout=5)

    @work(exclusive=True, thread=True)
    async def pull_updates(self) -> None:
        """Pull updates from WebDAV storage - DISABLED (no Git/GitHub integration)."""
        # Cloud-only via WebDAV - no Git pull needed
        # Data is synced directly from Heibox WebDAV storage
        self.notify("Cloud sync via WebDAV (no Git pull needed)", timeout=3)



def run_tui():
    """Launch the TUI application."""
    app = DataHubApp()
    app.run()


if __name__ == "__main__":
    run_tui()
