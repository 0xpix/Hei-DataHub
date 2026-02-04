"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.binding import Binding
from textual.timer import Timer
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from hei_datahub.services.config import get_config
from hei_datahub.ui.utils.keybindings import build_home_bindings
from hei_datahub.ui.widgets.contextual_footer import ContextualFooter
from hei_datahub.ui.widgets.update_overlay import UpdateOverlay
import subprocess
import sys
import urllib.parse
from textual import events

logger = logging.getLogger(__name__)


class HomeScreen(Screen):
    """Main screen with search functionality and Neovim-style navigation."""

    # Load bindings from config file
    BINDINGS = build_home_bindings() + [
        Binding("U", "check_updates", "Update", key_display="U", show=True),
        Binding("ctrl+i", "report_issue", "Report Issue", show=False),
    ]

    # Load CSS from styles directory
    ENABLE_COMMAND_PALETTE = True

    # Style (TCSS file)
    CSS_PATH = "../styles/home.tcss"

    search_mode = reactive(False)
    _debounce_timer: Optional[Timer] = None
    _g_pressed: bool = False
    _g_timer: Optional[Timer] = None

    # Track if update badge is shown
    _update_badge_shown: bool = False

    def compose(self) -> ComposeResult:
        from hei_datahub.ui.assets.loader import get_logo_widget_text

        # Load logo from config
        logo_text = get_logo_widget_text(get_config())

        yield Container(
            # Top "Hero" section with centered logo and search
            Container(
                Static(logo_text, id="banner"),
                Container(
                    Input(placeholder="Search datasets...", id="search-input"),
                    id="search-container"
                ),
                Container(
                    Static(
                        "🆕 [green]Update available[/green] • [dim]Ctrl+U[/dim]",
                        id="update-badge-text"
                    ),
                    id="update-badge",
                    classes=""
                ),
                id="hero-section"
            ),

            # Results section (hidden until search or browse)
            Container(
                Container(
                    Static("🔍 Mode: [bold cyan]Normal[/bold cyan]", id="mode-indicator"),
                    Horizontal(id="filter-badges-container", classes="filter-badges"),
                    Label("All Datasets", id="results-label"),
                    DataTable(id="results-table", cursor_type="row"),
                    id="results-section",
                ),
                id="results-wrapper",
                classes="hidden",
            ),
            id="main-container",
        )
        yield UpdateOverlay(id="update-overlay", on_restart=self._restart_app)
        yield ContextualFooter(id="contextual-footer")

    def on_mount(self) -> None:
        """Set up the screen when mounted."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Category", "Name", "Description", "Spatial Info", "Temporal Info", "Format")
        table.cursor_type = "row"
        table.show_row_labels = False

        # Focus search input on start
        self.query_one("#search-input").focus()

        # Set initial footer context (home = no shortcuts)
        self._update_footer_context()

        # Setup search autocomplete
        self._setup_search_autocomplete()

        # Check for cached update state and show badge if update available
        self._check_cached_update_state()

    def _check_cached_update_state(self) -> None:
        """Check cached update state and show badge if update available."""
        try:
            from hei_datahub.services.update_service import get_cached_update_state

            cached = get_cached_update_state()
            if cached and cached.has_update:
                self.show_update_badge(cached.latest_version)
                logger.debug(f"Showing cached update badge: {cached.latest_version}")
        except Exception as e:
            logger.debug(f"Could not check cached update state: {e}")

    def show_update_badge(self, latest_version: str) -> None:
        """
        Show the update available badge in the UI.

        Called by the app after silent update check completes.

        Args:
            latest_version: The latest available version string
        """
        if self._update_badge_shown:
            return  # Already showing

        try:
            badge = self.query_one("#update-badge")
            badge_text = self.query_one("#update-badge-text", Static)

            # Update badge text with version info (compact)
            badge_text.update(
                f"🆕 [green]v{latest_version} available[/green] • [dim]Ctrl+U[/dim]"
            )

            # Show the badge with animation
            badge.remove_class("hidden")
            self._update_badge_shown = True

            logger.info(f"Update badge shown for version {latest_version}")

        except Exception as e:
            logger.debug(f"Could not show update badge: {e}")

    def hide_update_badge(self) -> None:
        """Hide the update badge (e.g., after user triggers update)."""
        try:
            badge = self.query_one("#update-badge")
            badge.add_class("hidden")
            self._update_badge_shown = False
        except Exception:
            pass

    def on_screen_resume(self) -> None:
        """Called when returning to this screen from a pushed screen."""
        table = self.query_one("#results-table", DataTable)

        # 1. PRIORITY: Check if we explicitly saved an ID (e.g. before opening details)
        saved_focused_id = getattr(self, "_last_focused_dataset_id", None)

        # 2. FALLBACK: Save current selection ID from table if no explicit save
        if not saved_focused_id and table.row_count > 0 and table.cursor_row is not None:
            try:
                # Try to get the key from current cursor safely
                cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
                row_key = cell_key.row_key
                saved_focused_id = row_key.value if hasattr(row_key, 'value') else str(row_key)
            except Exception:
                pass

        # Clear the explicit save so it doesn't persist forever
        self._last_focused_dataset_id = None

        search_input = self.query_one("#search-input", Input)
        query = search_input.value

        if query and query.strip():
             # We have a search query, restore search results
             self.perform_search(query)
        else:
             # Load immediately - show what we have even if indexer not ready
             self.load_all_datasets()
             # Set up a very fast timer to reload when indexer finishes (100ms checks)
             self.set_interval(0.1, self._check_indexer_and_reload, name="indexer_check")

        # Focus results table if there are results AND it is visible, otherwise search bar
        results_wrapper = self.query_one("#results-wrapper")
        is_visible = "hidden" not in results_wrapper.classes

        if table.row_count > 0 and is_visible:
            table.focus()

            # Try to restore selection to saved row
            if saved_focused_id:
                try:
                    new_index = table.get_row_index(saved_focused_id)
                    if new_index is not None:
                        table.cursor_coordinate = (new_index, 0)
                except Exception:
                    # Row ID might not exist anymore or error finding it
                    pass
        else:
            self.query_one("#search-input").focus()

        # Update footer context AFTER setting focus
        # Use call_later to ensure focus state is propagated
        self.call_later(self._update_footer_context)

    def on_descendant_focus(self, event) -> None:
        """Update footer when focus changes."""
        self._update_footer_context()

    def _update_footer_context(self) -> None:
        """Update the contextual footer based on current state."""
        try:
            footer = self.query_one("#contextual-footer", ContextualFooter)
            search_input = self.query_one("#search-input", Input)
            table = self.query_one("#results-table", DataTable)
            results_wrapper = self.query_one("#results-wrapper")

            # Check if results are visible
            results_visible = "hidden" not in results_wrapper.classes

            if table.has_focus and results_visible:
                footer.set_context("results")
            elif search_input.has_focus and results_visible:
                footer.set_context("results")  # Show results shortcuts while in search with results
            elif search_input.has_focus:
                footer.set_context("search")  # Typing in search, no results yet
            else:
                footer.set_context("home")  # Home screen
        except Exception:
            pass  # Footer not mounted yet

    def _check_indexer_and_reload(self) -> None:
        """Check if indexer is ready and add new datasets incrementally.

        NOTE: This should ONLY run when showing all datasets, NOT during search!
        """
        # Get current search query to check if we're in search mode
        search_input = self.query_one("#search-input", Input)
        if search_input.value and len(search_input.value.strip()) >= 2:
            # We're in search mode - DO NOT add datasets
            logger.debug("Timer skipped: in search mode")
            return

        from hei_datahub.services.fast_search import get_all_indexed
        from hei_datahub.services.indexer import get_indexer

        indexer = get_indexer()
        table = self.query_one("#results-table", DataTable)
        label = self.query_one("#results-label", Label)

        # Get current datasets from index
        results = get_all_indexed()
        cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]

        # Get existing row keys to check what's already displayed
        existing_keys = set()
        for row_key in table.rows.keys():
            existing_keys.add(row_key.value)  # Use .value to get actual key string

        # Add only NEW datasets that aren't already in the table
        for result in cloud_results:
            if result["id"] not in existing_keys:
                # New dataset found - add it to the table immediately
                display_name = result["name"]
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:30] + "..." if len(description) > 30 else description
                else:
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:30] + "..." if len(snippet) > 30 else snippet

                meta = result.get("metadata", {})
                s_cov = meta.get("spatial_coverage") or "N/A"
                s_res = meta.get("spatial_resolution")
                s_info = f"{s_cov} ({s_res})" if s_res else s_cov

                t_cov = meta.get("temporal_coverage") or "N/A"
                t_res = meta.get("temporal_resolution")
                t_info = f"{t_cov} ({t_res})" if t_res else t_cov

                table.add_row(
                    meta.get("category") or "N/A",
                    display_name[:25],
                    snippet,
                    s_info[:40],
                    t_info[:40],
                    meta.get("file_format") or "N/A",
                    key=result["id"],
                )
                logger.info(f"Timer added dataset to table: {display_name}")

        # Update label with progress
        if not indexer.is_ready():
            label.update("🔄 Loading...")
        else:
            label.update(f"☁️ Cloud Datasets ({len(cloud_results)} total)")
            # Stop timer once indexer is done
            try:
                self.remove_timer("indexer_check")
                logger.info(f"Indexing complete - {table.row_count} datasets")
            except Exception:
                pass

    def _setup_search_autocomplete(self) -> None:
        """Setup autocomplete suggester for search input."""
        try:
            from hei_datahub.ui.widgets.autocomplete import SmartSearchSuggester

            search_input = self.query_one("#search-input", Input)
            search_input.suggester = SmartSearchSuggester()
        except Exception as e:
            logger.warning(f"Failed to setup search autocomplete: {e}")

    def _track_search_usage(self, query: str) -> None:
        """Track search filter usage for autocomplete ranking."""
        try:
            from hei_datahub.core.queries import QueryParser
            from hei_datahub.services.suggestion_service import get_suggestion_service

            parser = QueryParser()
            parsed = parser.parse(query)
            service = get_suggestion_service()

            # Track each field filter used
            for term in parsed.terms:
                if not term.is_free_text:
                    service.track_usage(term.field, term.value)
                    logger.debug(f"Tracked usage: {term.field}:{term.value}")
        except Exception as e:
            logger.debug(f"Failed to track search usage: {e}")

    def action_report_issue(self) -> None:
        """Open the issue reporting page."""
        url = "https://github.com/0xpix/Hei-DataHub/issues/new?labels=bug&template=bug_report.md"
        self.notify("Opening GitHub issue page...")
        self._open_url(url)

    def _open_url(self, url: str) -> None:
        """
        Open a URL in the default browser using subprocess.

        Avoids using webbrowser module which can cause readline symbol
        conflicts on some Linux installations.

        For packaged binaries (PyInstaller), we need to:
        1. Use shell=True to get proper PATH resolution
        2. Ensure proper environment inheritance
        3. Detach from the parent process completely
        """
        import os

        try:
            if sys.platform == "darwin":
                subprocess.Popen(
                    ["open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            elif sys.platform == "win32":
                subprocess.Popen(
                    ["start", url],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Linux - use shell=True for proper PATH resolution in packaged binaries
                # Build a clean environment with essential variables
                clean_env = {
                    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
                    "HOME": os.environ.get("HOME", ""),
                    "DISPLAY": os.environ.get("DISPLAY", ":0"),
                    "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY", ""),
                    "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR", ""),
                    "DBUS_SESSION_BUS_ADDRESS": os.environ.get("DBUS_SESSION_BUS_ADDRESS", ""),
                    "XDG_CURRENT_DESKTOP": os.environ.get("XDG_CURRENT_DESKTOP", ""),
                    "DESKTOP_SESSION": os.environ.get("DESKTOP_SESSION", ""),
                }
                # Remove empty values
                clean_env = {k: v for k, v in clean_env.items() if v}

                # Use shell=True with xdg-open for proper resolution
                # The shell will handle PATH lookup correctly
                proc = subprocess.Popen(
                    f'xdg-open "{url}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    env=clean_env,
                    cwd=os.environ.get("HOME", "/tmp")
                )
                # Don't wait - xdg-open spawns a browser and exits

        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            self.notify(f"Could not open browser: {e}", severity="error")

    def action_theme_palette(self) -> None:
        """Open theme palette (passthrough to app)."""
        self.app.action_theme_palette()

    def load_all_datasets(self, force_refresh: bool = False) -> None:
        """Load and display all available datasets from index (CLOUD ONLY)."""
        logger.info(f"load_all_datasets called (force_refresh={force_refresh})")
        table = self.query_one("#results-table", DataTable)
        table.clear()

        # Stop any existing indexer check timer
        try:
            self.remove_timer("indexer_check")
        except Exception:
            pass

        try:
            # Force cache clear if requested (e.g., after edit)
            if force_refresh:
                from hei_datahub.services.index_service import get_index_service
                index_service = get_index_service()
                index_service._query_cache.clear()
                index_service._cache_timestamps.clear()
                logger.info("✓ Cleared index cache for fresh data")

            # ALWAYS use indexed search for fast loading
            from hei_datahub.services.fast_search import get_all_indexed

            results = get_all_indexed()
            logger.info(f"get_all_indexed returned {len(results)} results")

            # CLOUD-ONLY: Filter to show only remote datasets
            cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]
            logger.info(f"After filtering for remote: {len(cloud_results)} cloud datasets")

            label = self.query_one("#results-label", Label)

            # Show indexer status if warming
            from hei_datahub.services.indexer import get_indexer
            indexer = get_indexer()
            if not indexer.is_ready():
                label.update("🔄 Loading cloud datasets... ☁️ 0 of ? datasets")
                # Don't populate table yet - timer will do it incrementally
                return
            elif len(cloud_results) == 0:
                label.update("☁️ No cloud datasets found - Add one with Ctrl+A")
            else:
                label.update(f"☁️ Cloud Datasets ({len(cloud_results)} total)")

            for result in cloud_results:
                # Get description from metadata or use snippet
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    # Use description from metadata if snippet is empty
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:30] + "..." if len(description) > 30 else description
                else:
                    # Clean snippet of HTML tags for display
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:30] + "..." if len(snippet) > 30 else snippet

                # All datasets are cloud now, but keep the indicator
                name_prefix = "☁️ "
                display_name = result["name"]  # Use metadata name, not folder path

                meta = result.get("metadata", {})
                s_cov = meta.get("spatial_coverage") or "N/A"
                s_res = meta.get("spatial_resolution")
                s_info = f"{s_cov} ({s_res})" if s_res else s_cov

                t_cov = meta.get("temporal_coverage") or "N/A"
                t_res = meta.get("temporal_resolution")
                t_info = f"{t_cov} ({t_res})" if t_res else t_cov

                table.add_row(
                    meta.get("category") or "N/A",
                    display_name[:25],
                    snippet,
                    s_info[:40],
                    t_info[:40],
                    meta.get("file_format") or "N/A",
                    key=result["id"],  # Use folder path as internal key
                )

            # Restart the indexer check timer for incremental updates (only when showing all datasets)
            self.set_interval(0.1, self._check_indexer_and_reload, name="indexer_check")

        except Exception as e:
            logger.error(f"Error loading datasets from index: {e}", exc_info=True)
            self.app.notify(f"Error loading datasets: {str(e)}", severity="error", timeout=5)

            # Don't steal focus - let user continue typing

    def _load_cloud_files(self) -> None:
        """Load files from cloud storage and display in table."""
        try:
            import os
            import tempfile

            import yaml

            from hei_datahub.services.storage_manager import get_storage_backend

            storage = get_storage_backend()
            entries = storage.listdir("")

            table = self.query_one("#results-table", DataTable)
            label = self.query_one("#results-label", Label)

            # Filter only directories (datasets)
            datasets = [e for e in entries if e.is_dir]
            label.update(f"☁️ Cloud Datasets ({len(datasets)} total)")

            # Load metadata.yaml from each directory
            for entry in datasets:
                dataset_id = entry.name

                try:
                    # Try to download and parse metadata.yaml
                    metadata_path = f"{dataset_id}/metadata.yaml"

                    # Download to temp file
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                        storage.download(metadata_path, tmp.name)
                        tmp_path = tmp.name

                    # Parse metadata
                    try:
                        with open(tmp_path, encoding='utf-8') as f:
                            metadata = yaml.safe_load(f)

                        name = metadata.get('name', dataset_id)
                        description = metadata.get('description', 'No description')

                        # Truncate for display
                        description = description[:40] + "..." if len(description) > 40 else description

                        s_cov = metadata.get("spatial_coverage") or "N/A"
                        s_res = metadata.get("spatial_resolution")
                        s_info = f"{s_cov} ({s_res})" if s_res else s_cov

                        t_cov = metadata.get("temporal_coverage") or "N/A"
                        t_res = metadata.get("temporal_resolution")
                        t_info = f"{t_cov} ({t_res})" if t_res else t_cov

                        table.add_row(
                            metadata.get("category", "N/A"),
                            name[:40],
                            description,
                            s_info[:40],
                            t_info[:40],
                            metadata.get("file_format", "N/A"),
                            key=dataset_id,
                        )
                    finally:
                        os.unlink(tmp_path)

                except Exception as e:
                    # If no metadata.yaml, show directory name only
                    logger.warning(f"Could not load metadata for {dataset_id}: {e}")
                    table.add_row(
                        "N/A",
                        f"📁 {dataset_id}"[:40],
                        "No metadata.yaml found",
                        "N/A",
                        "N/A",
                        "N/A",
                        key=dataset_id,
                    )

        except Exception as e:
            self.app.notify(f"Error loading cloud files: {str(e)}", severity="error", timeout=5)
            import traceback
            traceback.print_exc()

    def watch_search_mode(self, mode: bool) -> None:
        """Update mode indicator when search mode changes."""
        indicator = self.query_one("#mode-indicator", Static)
        if mode:
            indicator.update("🔍 Mode: [bold green]Insert[/bold green]")
        else:
            indicator.update("🔍 Mode: [bold cyan]Normal[/bold cyan]")

    @on(Input.Changed, "#search-input")
    def on_search_input(self, event: Input.Changed) -> None:
        """Handle search input changes with debouncing."""
        # Cancel existing timer
        if self._debounce_timer:
            self._debounce_timer.stop()

        # Get debounce from config or use default (200ms for fast typing)
        import os
        debounce_ms = int(os.environ.get("HEI_DATAHUB_SEARCH_DEBOUNCE_MS", "200"))

        # Set new timer for debounced search
        self._debounce_timer = self.set_timer(debounce_ms / 1000.0, lambda: self.perform_search(event.value))

    def _toggle_results_view(self, show: bool) -> None:
        """Toggle between splash screen and results view."""
        results = self.query_one("#results-wrapper")
        hero = self.query_one("#hero-section")

        if show:
            results.remove_class("hidden")
            hero.add_class("compact")
        else:
            results.add_class("hidden")
            hero.remove_class("compact")

    def perform_search(self, query: str) -> None:
        """Execute search and update results table (FAST - never hits network)."""
        logger.info(f"perform_search called with query: '{query}'")
        table = self.query_one("#results-table", DataTable)
        table.clear()

        # Determine visibility based on query
        has_query = bool(query.strip())
        self._toggle_results_view(has_query)

        # Update footer context as visibility/results changed
        self._update_footer_context()

        # If query is empty or very short, we effectively clear results (hide view)
        if not has_query:
            self._update_filter_badges("")
            return

        try:
            # Stop the indexer check timer during search to prevent interference
            try:
                self.remove_timer("indexer_check")
                logger.info("✓ Stopped indexer_check timer during search")
            except Exception as e:
                logger.debug(f"Could not remove timer (may not exist): {e}")

            # Update filter badges
            self._update_filter_badges(query)

            # Track usage of filters for autocomplete ranking
            self._track_search_usage(query)

            # ALWAYS use indexed search (never hit network on keystroke)
            from hei_datahub.services.fast_search import search_indexed

            results = search_indexed(query)
            logger.info(f"search_indexed returned {len(results)} results")

            # CLOUD-ONLY: Filter to show only remote datasets
            cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]
            logger.info(f"After cloud filter: {len(cloud_results)} results")

            label = self.query_one("#results-label", Label)

            # Show indexer status if warming
            from hei_datahub.services.indexer import get_indexer
            indexer = get_indexer()
            if not indexer.is_ready():
                label.update(f"🔄 Indexing… ☁️ Cloud Results ({len(cloud_results)} found) ")
            else:
                label.update(f"☁️ Cloud Results ({len(cloud_results)} found) ")

            if not cloud_results:
                label.update(f"No cloud results for '{query}' ")
                return

            for result in cloud_results:
                # Get description from metadata or use snippet
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    # Use description from metadata if snippet is empty
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:30] + "..." if len(description) > 30 else description
                else:
                    # Clean snippet of HTML tags for display
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:30] + "..." if len(snippet) > 30 else snippet

                # All datasets are cloud now
                name_prefix = "☁️ "
                display_name = result["name"]  # Use metadata name, not folder path

                meta = result.get("metadata", {})
                s_cov = meta.get("spatial_coverage") or "N/A"
                s_res = meta.get("spatial_resolution")
                s_info = f"{s_cov} ({s_res})" if s_res else s_cov

                t_cov = meta.get("temporal_coverage") or "N/A"
                t_res = meta.get("temporal_resolution")
                t_info = f"{t_cov} ({t_res})" if t_res else t_cov

                table.add_row(
                    meta.get("category") or "N/A",
                    display_name[:25],
                    snippet,
                    s_info[:40],
                    t_info[:40],
                    meta.get("file_format") or "N/A",
                    key=result["id"],  # Use folder path as internal key
                )
                logger.info(f"Added to table: {display_name}")

            logger.info(f"Search complete. Final table row count: {table.row_count}")
            # Don't steal focus from search input

        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            self.app.notify(f"Search error: {str(e)}", severity="error", timeout=5)
    def _search_cloud_files(self, query: str) -> None:
        """Search cloud files by name and metadata fields."""
        try:
            import os
            import tempfile

            import yaml

            from hei_datahub.core.queries import QueryParser
            from hei_datahub.services.storage_manager import get_storage_backend

            storage = get_storage_backend()
            entries = storage.listdir("")

            # Filter only directories (datasets)
            datasets = [e for e in entries if e.is_dir]

            # Parse query for field searches
            try:
                parser = QueryParser()
                parsed = parser.parse(query)
                has_field_queries = any(not term.is_free_text for term in parsed.terms)
            except Exception:
                parsed = None
                has_field_queries = False

            query_lower = query.lower()
            matches = []

            for entry in datasets:
                dataset_id = entry.name
                match_found = False

                # Load metadata for search
                try:
                    metadata_path = f"{dataset_id}/metadata.yaml"
                    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                        storage.download(metadata_path, tmp.name)
                        tmp_path = tmp.name

                    try:
                        with open(tmp_path, encoding='utf-8') as f:
                            metadata = yaml.safe_load(f)

                        if parsed and has_field_queries:
                            # Field-based search
                            match_found = self._matches_query_terms(metadata, parsed)
                        else:
                            # Simple text search in name, description, and keywords
                            name = metadata.get('name', dataset_id)
                            description = metadata.get('description', '')
                            keywords = metadata.get('keywords', [])
                            keywords_str = ' '.join(keywords) if isinstance(keywords, list) else str(keywords)

                            searchable_text = f"{dataset_id} {name} {description} {keywords_str}".lower()
                            match_found = query_lower in searchable_text

                        if match_found:
                            matches.append((dataset_id, entry, metadata))

                    finally:
                        os.unlink(tmp_path)
                except Exception:
                    # If metadata can't be loaded, do simple name match
                    if query_lower in dataset_id.lower():
                        matches.append((dataset_id, entry, None))

            table = self.query_one("#results-table", DataTable)
            label = self.query_one("#results-label", Label)
            label.update(f"☁️ Search Results ({len(matches)} found)")

            if not matches:
                label.update(f"No results for '{query}'")
                return

            # Display matches
            for dataset_id, entry, metadata in matches:
                if metadata:
                    name = metadata.get('name', dataset_id)
                    description = metadata.get('description', 'No description')
                    description = description[:40] + "..." if len(description) > 40 else description

                    s_cov = metadata.get("spatial_coverage") or "N/A"
                    s_res = metadata.get("spatial_resolution")
                    s_info = f"{s_cov} ({s_res})" if s_res else s_cov

                    t_cov = metadata.get("temporal_coverage") or "N/A"
                    t_res = metadata.get("temporal_resolution")
                    t_info = f"{t_cov} ({t_res})" if t_res else t_cov

                    table.add_row(
                        metadata.get("category", "N/A"),
                        name[:40],
                        description,
                        s_info[:40],
                        t_info[:40],
                        metadata.get("file_format", "N/A"),
                        key=dataset_id,
                    )
                else:
                    # Fallback for entries without metadata
                    table.add_row(
                        "N/A",
                        f"📁 {dataset_id}"[:40],
                        "No metadata.yaml",
                        "N/A",
                        "N/A",
                        "N/A",
                        key=dataset_id,
                    )

        except Exception as e:
            self.app.notify(f"Error searching cloud files: {str(e)}", severity="error", timeout=5)

    def _matches_query_terms(self, metadata: dict, parsed) -> bool:
        """Check if metadata matches all query terms."""
        for term in parsed.terms:
            if term.is_free_text:
                # Free text search in name, description, keywords
                name = str(metadata.get('name', '')).lower()
                description = str(metadata.get('description', '')).lower()
                keywords = metadata.get('keywords', [])
                keywords_str = ' '.join(keywords).lower() if isinstance(keywords, list) else str(keywords).lower()

                searchable = f"{name} {description} {keywords_str}"
                if term.value.lower() not in searchable:
                    return False
            else:
                # Field-specific search
                field = term.field.lower()
                search_value = term.value.lower()

                # Map common field names
                field_map = {
                    'name': 'name',
                    'description': 'description',
                    'desc': 'description',
                    'source': 'source',
                    'license': 'license',
                    'keyword': 'keywords',
                    'keywords': 'keywords',
                    'project': 'used_in_projects',
                    'projects': 'used_in_projects',
                    'temporal': 'temporal_coverage',
                    'spatial': 'spatial_coverage',
                }

                metadata_field = field_map.get(field, field)
                metadata_value = metadata.get(metadata_field)

                if metadata_value is None:
                    return False

                # Handle list fields
                if isinstance(metadata_value, list):
                    metadata_str = ' '.join(str(v).lower() for v in metadata_value)
                    if search_value not in metadata_str:
                        return False
                # Handle dict fields (like temporal_coverage)
                elif isinstance(metadata_value, dict):
                    metadata_str = ' '.join(str(v).lower() for v in metadata_value.values())
                    if search_value not in metadata_str:
                        return False
                else:
                    if search_value not in str(metadata_value).lower():
                        return False

        return True

    def _get_badge_color_class(self, badge_text: str) -> str:
        """
        Get a consistent retro color class for a badge based on its text.

        Uses hash of the badge text to consistently assign the same color
        to the same badge, but colors appear random across different badges.
        """
        retro_colors = [
            "badge-retro-teal",
            "badge-retro-coral",
            "badge-retro-sage",
            "badge-retro-mauve",
            "badge-retro-amber",
            "badge-retro-slate",
        ]
        # Use hash to get consistent color for same badge text
        color_index = hash(badge_text) % len(retro_colors)
        return retro_colors[color_index]

    def _update_filter_badges(self, query: str) -> None:
        """Update visual badges showing active search filters with uniform key-based styling."""
        from hei_datahub.core.queries import QueryParser

        badges_container = self.query_one("#filter-badges-container", Horizontal)
        badges_container.remove_children()

        if not query.strip():
            return

        try:
            parser = QueryParser()
            parsed = parser.parse(query)

            # Show badges for field filters with uniform key-based styling
            for term in parsed.terms:
                if not term.is_free_text:
                    # Operator symbols for display
                    operator_symbols = {
                        'CONTAINS': ':',
                        'GT': '>',
                        'LT': '<',
                        'GTE': '>=',
                        'LTE': '<=',
                        'EQ': '='
                    }
                    op_symbol = operator_symbols.get(term.operator.name, ':')

                    # Uniform badge text: key:value or key>value etc
                    badge_text = f"{term.field}{op_symbol}{term.value}"

                    # Get color based on the full badge text for consistency
                    color_class = self._get_badge_color_class(badge_text)

                    # Create badge with key emoji for visual grouping
                    key_emoji = {
                        "project": "📁",
                        "source": "🔗",
                        "tag": "🏷️",
                        "owner": "👤",
                        "size": "📏",
                        "format": "📄",
                        "type": "📊",
                    }.get(term.field.lower(), "🔍")

                    badge_display = f"{key_emoji} {badge_text}"
                    badges_container.mount(Static(badge_display, classes=f"filter-badge {color_class}"))

            # Show individual badges for each free text term
            free_text_terms = [term for term in parsed.terms if term.is_free_text]
            logger.debug(f"Found {len(free_text_terms)} free text terms: {[t.value for t in free_text_terms]}")

            for term in free_text_terms:
                # Free text gets consistent color based on the term value
                color_class = self._get_badge_color_class(term.value)
                badge = Static(f"📝 {term.value}", classes=f"filter-badge {color_class}")
                badges_container.mount(badge)
                logger.debug(f"Mounted badge for term: {term.value}")

        except Exception:
            # If parsing fails, show raw query with color based on query text
            color_class = self._get_badge_color_class(query)
            badges_container.mount(Static(f"[dim]🔍 {query}[/dim]", classes=f"filter-badge {color_class}"))

    def action_focus_search(self) -> None:
        """Focus search input and enter insert mode."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
        self.search_mode = True

    def on_key(self, event) -> None:
        """Handle key events for autocomplete and navigation."""
        # Only handle when search input is focused
        search_input = self.query_one("#search-input", Input)

        if search_input.has_focus:
            # Tab accepts autocomplete and prevents navigation to table
            if event.key == "tab":
                # Manually accept the suggestion by moving cursor to end
                # This is what Textual does internally for Right Arrow with suggester
                if hasattr(search_input, 'suggester') and search_input.suggester:
                    # Move cursor to end to accept suggestion
                    search_input.cursor_position = len(search_input.value)
                    # Trigger cursor_right action which accepts the suggestion
                    search_input.action_cursor_right()
                # Prevent Tab from navigating away
                event.prevent_default()
                event.stop()
        else:
            # Handle 'gg' sequence for jump to top
            if event.key == "g":
                if self._g_pressed:
                    # Second 'g' press - jump to top
                    self.action_jump_top()
                    self._g_pressed = False
                    if self._g_timer:
                        self._g_timer.stop()
                        self._g_timer = None
                    event.prevent_default()
                    event.stop()
                else:
                    # First 'g' press - wait for second one
                    self._g_pressed = True
                    # Reset after 1 second if no second 'g'
                    if self._g_timer:
                        self._g_timer.stop()
                    self._g_timer = self.set_timer(1.0, self._reset_g_buffer)
                    event.prevent_default()
                    event.stop()
            elif self._g_pressed:
                # Any other key pressed - reset the 'g' buffer
                self._reset_g_buffer()

    def _reset_g_buffer(self) -> None:
        """Reset the 'g' key buffer."""
        self._g_pressed = False
        if self._g_timer:
            self._g_timer.stop()
            self._g_timer = None

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self) -> None:
        """Handle search submission - move focus to table only if there's a query and results."""
        search_input = self.query_one("#search-input", Input)
        table = self.query_one("#results-table", DataTable)

        # Only move to table if:
        # 1. There's an actual search query (not empty)
        # 2. There are results to navigate
        if search_input.value.strip() and table.row_count > 0:
            # Set flag to prevent action_open_details from firing on same Enter press
            self._search_just_submitted = True
            # Move focus to table so user can navigate with j/k
            table.focus()
            # Ensure cursor is at first row so it's visible
            table.cursor_coordinate = (0, 0)
            self.search_mode = False
        # Otherwise, do nothing - stay in search bar

    def action_clear_search(self) -> None:
        """Clear search or exit insert mode, or confirm exit if nothing to clear."""
        search_input = self.query_one("#search-input", Input)
        table = self.query_one("#results-table", DataTable)

        if self.search_mode:
            # Exit insert mode - focus search bar (not table)
            search_input.focus()
            self.search_mode = False
            self._update_footer_context()
        elif table.has_focus:
            # Return focus to search input (without clearing)
            search_input.focus()
            # Move cursor to end
            search_input.cursor_position = len(search_input.value)
            self._update_footer_context()
        elif search_input.value:
            # Clear search and refocus search bar
            search_input.value = ""
            self._toggle_results_view(False)  # Hide results immediately
            search_input.focus()
            self._update_footer_context()  # Update footer to home context
        elif table.has_focus:
            # Table is focused with no search (shouldn't happen with new logic but safe fallback)
            self._show_exit_confirmation()
        else:
            # Already on search bar with nothing to clear - show exit confirmation
            self._show_exit_confirmation()

    def _show_exit_confirmation(self) -> None:
        """Show exit confirmation dialog."""
        from hei_datahub.ui.widgets.dialogs import ConfirmExitDialog

        def on_result(confirmed: bool) -> None:
            if confirmed:
                self.app.exit()

        self.app.push_screen(ConfirmExitDialog(), callback=on_result)

    def action_move_down(self) -> None:
        """Move selection down (j key)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.has_focus:
            table.action_cursor_down()

    def action_move_up(self) -> None:
        """Move selection up (k key)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.has_focus:
            table.action_cursor_up()

    def action_jump_top(self) -> None:
        """Jump to first row (gg)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0:
            table.cursor_coordinate = (0, 0)

    def action_jump_bottom(self) -> None:
        """Jump to last row (G)."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0:
            table.cursor_coordinate = (table.row_count - 1, 0)

    def action_add_dataset(self) -> None:
        """Navigate to Add Dataset screen."""
        from .dataset_add import AddDataScreen
        self.app.push_screen(AddDataScreen())

    def action_open_details(self) -> None:
        """Open details for selected dataset or cloud file."""
        # Prevent opening if Enter was just pressed in search bar
        if getattr(self, '_search_just_submitted', False):
            self._search_just_submitted = False
            return

        # Don't open if search input has focus (Enter in search bar shouldn't open)
        search_input = self.query_one("#search-input", Input)
        if search_input.has_focus:
            return

        table = self.query_one("#results-table", DataTable)
        # Only open if table has focus and has data
        if not table.has_focus:
            return
        if table.row_count == 0:
            return

        if table.cursor_row is not None and table.cursor_row < table.row_count:
            try:
                # Get the true RowKey from the cursor position (handles sorting correctly)
                # coordinate_to_cell_key returns a CellKey, which has a row_key attribute
                cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
                row_key = cell_key.row_key
                row_key_value = row_key.value if hasattr(row_key, 'value') else str(row_key)

                # Save specifically for restoring after back navigation
                self._last_focused_dataset_id = row_key_value

                if row_key_value:
                    # ALWAYS open cloud dataset details (cloud-only workflow)
                    self._open_cloud_file_preview(str(row_key_value))
            except Exception as e:
                # Fallback: try legacy method just in case or log error
                logger.error(f"Error getting row key: {e}")
                self.app.notify(f"Error opening details: {str(e)}", severity="error", timeout=3)

    def _open_cloud_file_preview(self, filename: str) -> None:
        """Open preview screen for cloud dataset."""
        from .dataset_detail import CloudDatasetDetailsScreen

        try:
            # For directories (datasets), show the DetailsScreen-like view with metadata
            self.app.push_screen(CloudDatasetDetailsScreen(filename))
        except Exception as e:
            self.app.notify(f"Error opening dataset: {str(e)}", severity="error", timeout=3)
            import traceback
            traceback.print_exc()

    @on(DataTable.RowSelected, "#results-table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in results table."""
        try:
            # Get the row key which is the folder path (result["id"])
            # NOT the first column which is the display name
            row_key = event.row_key.value if hasattr(event.row_key, 'value') else str(event.row_key)

            # Save specifically for restoring after back navigation
            self._last_focused_dataset_id = row_key

            # ALWAYS use cloud mode (cloud-only workflow)
            self._open_cloud_file_preview(row_key)
        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error", timeout=3)

    def action_show_help(self) -> None:
        """Show help overlay with keybindings (? key)."""
        from hei_datahub.ui.widgets.help import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_settings(self) -> None:
        """Open settings menu (S key)."""
        from hei_datahub.ui.utils.settings_router import open_settings_screen
        open_settings_screen(self.app)

    def action_pull_updates(self) -> None:
        """Start pull updates task."""
        self.app.pull_updates()

    def action_check_updates(self) -> None:
        """
        Check for app updates and run update in-place (Ctrl+U).

        Shows an overlay on the home screen with progress bar while
        the update runs in the background. After completion, prompts
        to restart the app.
        """
        # Hide the update badge when user triggers update
        self.hide_update_badge()

        logger.info("User triggered update check (Ctrl+U)")

        # Show the update overlay and start the update
        try:
            overlay = self.query_one("#update-overlay", UpdateOverlay)
            overlay.show()
        except Exception as e:
            logger.error(f"Failed to show update overlay: {e}")
            self.notify(f"Update failed: {e}", severity="error", timeout=5)

    def _restart_app(self) -> None:
        """Restart the application after update."""
        import os
        import sys

        logger.info("Restarting application after update...")

        # Get the executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled binary
            executable = sys.executable
            args = sys.argv[:]
        else:
            # Running from Python
            executable = sys.executable
            args = [sys.executable] + sys.argv[:]

        # Exit and restart
        self.app.exit()

        # Use os.execv to replace current process with new one
        try:
            os.execv(executable, args)
        except Exception as e:
            logger.error(f"Failed to restart: {e}")


    def action_refresh_data(self) -> None:
        """Refresh/reload all datasets."""
        self.notify("Refreshing datasets...", timeout=2)
        self.load_all_datasets()
        self.notify("✓ Datasets refreshed", timeout=3)

    def action_debug_console(self) -> None:
        """Open debug console (: key)."""
        from hei_datahub.ui.widgets.console import DebugConsoleScreen
        self.app.push_screen(DebugConsoleScreen())

    def action_show_about(self) -> None:
        """Show about screen."""
        from hei_datahub.ui.views.about import AboutScreen
        self.app.push_screen(AboutScreen())
