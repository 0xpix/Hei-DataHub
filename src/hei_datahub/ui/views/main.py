"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging
try:
    import tomllib as tomli
except ImportError:
    import tomli  # type:ignore

logger = logging.getLogger(__name__)
from textual import work
from textual.app import App
from textual.widgets import (
    Static,
)
from textual.reactive import reactive

from mini_datahub.infra.db import ensure_database
from hei_datahub.services.config import get_config
from hei_datahub.ui.views.home import HomeScreen


class DataHubApp(App):
    """Main TUI application with Neovim-style keybindings."""

    CSS_PATH = "../styles/base.tcss"

    # Track WebDAV/Heibox connection status
    heibox_connected = reactive(False)

    def on_mount(self) -> None:
        """Initialize the app."""
        # Initialize logging
        from mini_datahub.app.runtime import setup_logging, log_startup
        from mini_datahub import __version__
        from mini_datahub.app.settings import get_github_config

        config = get_github_config()
        setup_logging(debug=config.debug_logging)
        log_startup(__version__)

        # Load user configuration
        self._load_config()

        # Ensure database is set up
        try:
            ensure_database()

            # Check if we need to do initial indexing
            from mini_datahub.infra.index import reindex_all
            from mini_datahub.infra.store import list_datasets

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
        from mini_datahub.services.indexer import start_background_indexer, get_indexer
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

        # Check WebDAV/Heibox connection status
        self.check_heibox_connection()

        # Apply theme from config
        theme_name = self.config.get("theme.name", "gruvbox")
        self.theme = theme_name

        # Initialize autocomplete from catalog
        if config.suggest_from_catalog_values:
            from mini_datahub.services.autocomplete import refresh_autocomplete
            refresh_autocomplete()

        # Push home screen (will automatically load from cloud or local based on config)
        self.push_screen(HomeScreen())

        # Check for updates (async) - after screen is mounted
        if config.auto_check_updates:
            self.check_for_updates_async()

        # Startup pull prompt (async) - after screen is mounted
        self.startup_pull_check()

    def check_heibox_connection(self) -> None:
        """Check WebDAV/Heibox connection status on startup."""
        try:
            from mini_datahub.infra.config_paths import get_config_path

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
            from mini_datahub.auth.credentials import get_auth_store

            store = get_auth_store(prefer_keyring=True)
            credential = store.load_secret(key_id)

            if not credential:
                self.heibox_connected = False
                return

            # Quick connection test (HEAD request to server)
            import requests
            from urllib.parse import urlparse

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
        self.check_heibox_connection()

        # Update home screen if it exists
        try:
            for screen in self.screen_stack:
                if isinstance(screen, HomeScreen):
                    screen.update_heibox_status()
        except Exception:
            pass

    @work(exclusive=True, thread=True)
    async def check_for_updates_async(self) -> None:
        """Check for updates asynchronously (background)."""
        from mini_datahub.services.update_check import check_for_updates, format_update_message

        update_info = check_for_updates(force=False)
        if update_info and update_info.get("has_update"):
            message = format_update_message(update_info)
            self.notify(message, severity="information", timeout=10)

    @work(exclusive=True, thread=True)
    async def startup_pull_check(self) -> None:
        """Check if we should prompt for pull on startup."""
        from mini_datahub.services.sync import get_auto_pull_manager
        from mini_datahub.services.state import get_state_manager
        from mini_datahub.app.settings import get_github_config
        from pathlib import Path
        import asyncio

        # Wait a bit for screen to be fully mounted
        await asyncio.sleep(0.5)

        state = get_state_manager()

        # Skip if user doesn't want prompts this session
        if not state.should_prompt_pull():
            return

        try:
            config = get_github_config()
            if not config.catalog_repo_path:
                return

            pull_manager = get_auto_pull_manager(Path(config.catalog_repo_path))

            # Quick network check
            if not pull_manager.check_network_available():
                return

            # Fetch to check if behind
            pull_manager.git_ops.fetch()

            is_behind, commits_behind = pull_manager.is_behind_remote()

            if is_behind:
                plural = "s" if commits_behind > 1 else ""

                # Find the HomeScreen and update its widgets
                try:
                    # Get the active screen (should be HomeScreen)
                    for screen in self.screen_stack:
                        if isinstance(screen, HomeScreen):
                            # Show status indicator below main banner
                            try:
                                update_status = screen.query_one("#update-status", Static)
                                update_status.update(
                                    f"[bold]⬇ {commits_behind} Update{plural} Available[/bold]  •  Press [bold]U[/bold] to update"
                                )
                                update_status.remove_class("hidden")
                            except Exception:
                                pass
                            break
                except Exception:
                    pass

                # Show persistent notification (no timeout)
                self.notify(
                    f"⬇ {commits_behind} update{plural} available. Press [bold]U[/bold] to update.",
                    severity="information"
                )
        except Exception:
            pass

    def _load_config(self) -> None:
        """Load and apply configuration settings."""
        try:
            self.config = get_config()
            # Config is now available for use throughout the app
            # Keybindings are already loaded when HomeScreen class is defined
            # Settings like search debounce, auto_sync, etc. can be accessed via self.config.get()
        except Exception as e:
            # Config system optional - app works without it
            self.config = None

    def apply_theme(self, theme_name: str) -> None:
        """
        Apply a theme dynamically without restart.

        Args:
            theme_name: Name of the theme to apply
        """
        try:
            # Reload config to pick up the latest changes
            from mini_datahub.services.config import reload_config
            self.config = reload_config()

            # Update the app's theme attribute (Textual built-in)
            self.theme = theme_name

            # Reload the theme manager to pick up new theme
            from mini_datahub.ui.theme import reload_theme
            reload_theme()

            # Refresh all screens to apply new theme
            self.refresh()

            # Force refresh of CSS variables if needed
            for screen in self.screen_stack:
                screen.refresh()

            self.notify(f"Theme '{theme_name}' applied successfully!", timeout=3)

        except Exception as e:
            self.notify(f"Failed to apply theme: {str(e)}", severity="error", timeout=5)

    def reload_keybindings(self) -> None:
        """
        Reload keybindings dynamically without restart.

        This recreates the HomeScreen with new bindings from the config file.
        """
        try:
            # Reload config to pick up the latest changes
            from mini_datahub.services.config import reload_config
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
                old_screen = self.screen

                # Pop current home screen
                self.pop_screen()

                # Reload the module to pick up new bindings
                import importlib
                import mini_datahub.ui.views.home as home_module
                importlib.reload(home_module)

                # Push new home screen with updated bindings
                from mini_datahub.ui.views.home import HomeScreen as NewHomeScreen
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
        """Pull updates from catalog repository."""
        from mini_datahub.services.sync import get_auto_pull_manager
        from mini_datahub.app.runtime import log_pull_update, log_reindex
        from mini_datahub.infra.index import reindex_all
        from mini_datahub.app.settings import get_github_config
        from pathlib import Path

        try:
            config = get_github_config()
            if not config.catalog_repo_path:
                self.notify("Catalog path not configured", severity="error", timeout=5)
                return

            pull_manager = get_auto_pull_manager(Path(config.catalog_repo_path))

            # Check network
            if not pull_manager.check_network_available():
                self.notify("No network connection", severity="warning", timeout=5)
                return

            # Note: Local changes check removed - pull_updates() now handles via auto-stash

            # Check divergence
            is_diverged, ahead, behind = pull_manager.is_diverged()
            if is_diverged:
                self.notify(
                    "Cannot pull: Local branch has diverged from remote",
                    severity="error",
                    timeout=7
                )
                return

            # Fetch first
            self.notify("Fetching updates...", timeout=3)
            pull_manager.git_ops.fetch()

            # Check if actually behind
            is_behind, commits_behind = pull_manager.is_behind_remote()
            if not is_behind:
                self.notify("Already up to date", timeout=3)
                return

            # Pull
            self.notify("Pulling updates...", timeout=3)
            success, message, old_commit, new_commit = pull_manager.pull_updates(
                branch="main",
                from_remote=True,   # Pull from REMOTE origin/main
                allow_merge=True,   # Allow merge commits (handles divergence)
                auto_stash=True     # Auto-stash uncommitted changes
            )

            if not success:
                self.notify(f"Pull failed: {message}", severity="error", timeout=7)
                log_pull_update(success=False, error=message)
                return

            # Hide update status after successful pull
            try:
                for screen in self.screen_stack:
                    if isinstance(screen, HomeScreen):
                        try:
                            update_status = screen.query_one("#update-status", Static)
                            update_status.add_class("hidden")
                        except Exception:
                            pass
                        break
            except Exception:
                pass

            # Check for metadata changes
            if old_commit and new_commit and old_commit != new_commit:
                has_metadata, metadata_count = pull_manager.has_metadata_changes(old_commit, new_commit)
                if has_metadata:
                    self.notify("Reindexing datasets...", timeout=3)
                    dataset_count, errors = reindex_all()

                    if errors:
                        self.notify(
                            f"Pull complete. Reindexed {dataset_count} datasets with {len(errors)} errors",
                            severity="warning",
                            timeout=7
                        )
                        log_reindex(success=False, datasets_count=dataset_count, error=f"{len(errors)} errors")
                    else:
                        self.notify(
                            f"Pull complete. Reindexed {dataset_count} datasets",
                            severity="information",
                            timeout=5
                        )
                        log_reindex(success=True, datasets_count=dataset_count)

                    log_pull_update(success=True, files_changed=metadata_count)
                else:
                    self.notify("Pull complete (no metadata changes)", timeout=5)
                    log_pull_update(success=True, files_changed=0)
            else:
                self.notify("Pull complete (already up to date)", timeout=5)
                log_pull_update(success=True, files_changed=0)

        except Exception as e:
            self.notify(f"Pull failed: {str(e)}", severity="error", timeout=7)
            log_pull_update(success=False, error=str(e))

if __name__ == "__main__":
    """Launch the TUI application."""
    app = DataHubApp()
    app.run()
