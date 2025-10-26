"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging
from typing import Optional

try:
    import tomllib as tomli
except ImportError:
    import tomli  # type:ignore

logger = logging.getLogger(__name__)
from textual.app import ComposeResult
from textual import on
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)
from textual.reactive import reactive
from textual.timer import Timer

from hei_datahub.services.config import get_config
from hei_datahub.utils.bindings import _build_bindings_from_config

class HomeScreen(Screen):
    """Main screen with search functionality and Neovim-style navigation."""

    # Load bindings from config file
    BINDINGS = _build_bindings_from_config()

    # Load CSS from styles directory
    CSS_PATH = "../styles/home.tcss"  # TODO: Copy CSS from mini_datahub or create new

    search_mode = reactive(False)
    _debounce_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        from mini_datahub.ui.assets.loader import get_logo_widget_text

        # Load logo from config
        logo_text = get_logo_widget_text(get_config())

        yield Header()
        yield Container(
            Static(logo_text, id="banner"),
            Static("", id="update-status", classes="hidden"),
            Static("🔍 Search Datasets  |  Mode: [bold cyan]Normal[/bold cyan]", id="mode-indicator"),
            Static(id="heibox-status"),
            Input(placeholder="Type / to search | Tab/→/Ctrl+F for autocomplete | Enter to view", id="search-input"),
            Horizontal(id="filter-badges-container", classes="filter-badges"),
            Label("All Datasets", id="results-label"),
            DataTable(id="results-table", cursor_type="row"),
            id="search-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when mounted."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("ID", "Name", "Description")
        table.cursor_type = "row"
        # Start with table focused, but don't refocus it during searches
        table.focus()

        # Setup search autocomplete
        self._setup_search_autocomplete()

        # Update Heibox status indicator
        self.update_heibox_status()

        # Load immediately - show what we have even if indexer not ready
        self.load_all_datasets()

        # Set up a very fast timer to reload when indexer finishes (100ms checks)
        self.set_interval(0.1, self._check_indexer_and_reload, name="indexer_check")

    def _check_indexer_and_reload(self) -> None:
        """Check if indexer is ready and add new datasets incrementally."""
        from mini_datahub.services.indexer import get_indexer
        from mini_datahub.services.fast_search import get_all_indexed

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
                    snippet = description[:80] + "..." if len(description) > 80 else description
                else:
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:80] + "..." if len(snippet) > 80 else snippet

                table.add_row(
                    display_name,
                    ("☁️ " + display_name)[:40],
                    snippet,
                    key=result["id"],
                )
                logger.info(f"Added dataset to table: {display_name}")

        # Update label with progress
        if not indexer.is_ready():
            label.update(f"🔄 Loading... ☁️ {len(cloud_results)} of ? datasets")
        else:
            label.update(f"☁️ Cloud Datasets ({len(cloud_results)} total)")
            # Stop timer once indexer is done
            try:
                self.remove_timer("indexer_check")
                logger.info(f"Indexing complete - {table.row_count} datasets")
            except:
                pass

    def _setup_search_autocomplete(self) -> None:
        """Setup autocomplete suggester for search input."""
        try:
            from mini_datahub.ui.widgets.autocomplete import SmartSearchSuggester

            search_input = self.query_one("#search-input", Input)
            search_input.suggester = SmartSearchSuggester()
        except Exception as e:
            logger.warning(f"Failed to setup search autocomplete: {e}")

    def _track_search_usage(self, query: str) -> None:
        """Track search filter usage for autocomplete ranking."""
        try:
            from mini_datahub.core.queries import QueryParser
            from mini_datahub.services.suggestion_service import get_suggestion_service

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

    def update_heibox_status(self) -> None:
        """Update Heibox/WebDAV connection status display."""
        try:
            from mini_datahub.infra.config_paths import get_config_path

            status_widget = self.query_one("#heibox-status", Static)

            # Check if configured and connected
            if self.app.heibox_connected:
                # Simply show synced status without username
                status_widget.update("[green]☁ Synced to Hei-box[/green]")
            else:
                # Check if configured but not connected
                config_path = get_config_path()
                if config_path.exists():
                    with open(config_path, "rb") as f:
                        config = tomli.load(f)

                    if "auth" in config:
                        status_widget.update("[yellow]⚠ Hei-box Configured (connection failed)[/yellow] [dim]Run: hei-datahub auth doctor[/dim]")
                    else:
                        status_widget.update("[dim]○ Hei-box Not Connected[/dim] [dim]Run: hei-datahub auth setup[/dim]")
                else:
                    status_widget.update("[dim]○ Hei-box Not Connected[/dim] [dim]Run: hei-datahub auth setup[/dim]")

        except Exception as e:
            logger.debug(f"Failed to update heibox status: {e}")
            # Fallback to simple message
            status_widget = self.query_one("#heibox-status", Static)
            status_widget.update("[dim]○ Hei-box Status Unknown[/dim]")


    def load_all_datasets(self, force_refresh: bool = False) -> None:
        """Load and display all available datasets from index (CLOUD ONLY)."""
        logger.info(f"load_all_datasets called (force_refresh={force_refresh})")
        table = self.query_one("#results-table", DataTable)
        table.clear()

        try:
            # Force cache clear if requested (e.g., after edit)
            if force_refresh:
                from mini_datahub.services.index_service import get_index_service
                index_service = get_index_service()
                index_service._query_cache.clear()
                index_service._cache_timestamps.clear()
                logger.info("✓ Cleared index cache for fresh data")

            # ALWAYS use indexed search for fast loading
            from mini_datahub.services.fast_search import get_all_indexed

            results = get_all_indexed()
            logger.info(f"get_all_indexed returned {len(results)} results")

            # CLOUD-ONLY: Filter to show only remote datasets
            cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]
            logger.info(f"After filtering for remote: {len(cloud_results)} cloud datasets")

            label = self.query_one("#results-label", Label)

            # Show indexer status if warming
            from mini_datahub.services.indexer import get_indexer
            indexer = get_indexer()
            if not indexer.is_ready():
                label.update(f"🔄 Loading cloud datasets... ☁️ 0 of ? datasets")
                # Don't populate table yet - timer will do it incrementally
                return
            elif len(cloud_results) == 0:
                label.update(f"☁️ No cloud datasets found - Add one with Ctrl+A")
            else:
                label.update(f"☁️ Cloud Datasets ({len(cloud_results)} total)")

            for result in cloud_results:
                # Get description from metadata or use snippet
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    # Use description from metadata if snippet is empty
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:80] + "..." if len(description) > 80 else description
                else:
                    # Clean snippet of HTML tags for display
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:80] + "..." if len(snippet) > 80 else snippet

                # All datasets are cloud now, but keep the indicator
                name_prefix = "☁️ "
                display_name = result["name"]  # Use metadata name, not folder path

                table.add_row(
                    display_name,  # Show name in ID column
                    (name_prefix + display_name)[:40],  # Show name with cloud icon
                    snippet,
                    key=result["id"],  # Use folder path as internal key
                )

        except Exception as e:
            logger.error(f"Error loading datasets from index: {e}", exc_info=True)
            self.app.notify(f"Error loading datasets: {str(e)}", severity="error", timeout=5)

            # Don't steal focus - let user continue typing

    def _load_cloud_files(self) -> None:
        """Load files from cloud storage and display in table."""
        try:
            from mini_datahub.services.storage_manager import get_storage_backend
            import yaml
            import tempfile
            import os

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
                        with open(tmp_path, 'r', encoding='utf-8') as f:
                            metadata = yaml.safe_load(f)

                        name = metadata.get('name', dataset_id)
                        description = metadata.get('description', 'No description')

                        # Truncate for display
                        description = description[:80] + "..." if len(description) > 80 else description

                        table.add_row(
                            dataset_id,
                            name[:40],
                            description,
                            key=dataset_id,
                        )
                    finally:
                        os.unlink(tmp_path)

                except Exception as e:
                    # If no metadata.yaml, show directory name only
                    logger.warning(f"Could not load metadata for {dataset_id}: {e}")
                    table.add_row(
                        dataset_id,
                        f"📁 {dataset_id}"[:40],
                        "No metadata.yaml found",
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
            indicator.update("🔍 Search Datasets  |  Mode: [bold green]Insert[/bold green]")
        else:
            indicator.update("🔍 Search Datasets  |  Mode: [bold cyan]Normal[/bold cyan]")

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

    def perform_search(self, query: str) -> None:
        """Execute search and update results table (FAST - never hits network)."""
        table = self.query_one("#results-table", DataTable)
        table.clear()

        # If query is empty or very short, show all datasets
        if not query.strip() or len(query.strip()) < 2:
            self._update_filter_badges("")
            self.load_all_datasets()
            return

        try:
            # Update filter badges
            self._update_filter_badges(query)

            # Track usage of filters for autocomplete ranking
            self._track_search_usage(query)

            # ALWAYS use indexed search (never hit network on keystroke)
            from mini_datahub.services.fast_search import search_indexed

            results = search_indexed(query)

            # CLOUD-ONLY: Filter to show only remote datasets
            cloud_results = [r for r in results if r.get("metadata", {}).get("is_remote", False)]

            label = self.query_one("#results-label", Label)

            # Show indexer status if warming
            from mini_datahub.services.indexer import get_indexer
            indexer = get_indexer()
            if not indexer.is_ready():
                label.update(f"🔄 Indexing… ☁️ Cloud Results ({len(cloud_results)} found)")
            else:
                label.update(f"☁️ Cloud Results ({len(cloud_results)} found)")

            if not cloud_results:
                label.update(f"No cloud results for '{query}'")
                return

            for result in cloud_results:
                # Get description from metadata or use snippet
                snippet = result.get("snippet", "")
                if not snippet or snippet.strip() == "":
                    # Use description from metadata if snippet is empty
                    description = result.get("metadata", {}).get("description", "No description")
                    snippet = description[:80] + "..." if len(description) > 80 else description
                else:
                    # Clean snippet of HTML tags for display
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    snippet = snippet[:80] + "..." if len(snippet) > 80 else snippet

                # All datasets are cloud now
                name_prefix = "☁️ "
                display_name = result["name"]  # Use metadata name, not folder path

                table.add_row(
                    display_name,  # Show name in ID column
                    (name_prefix + display_name)[:40],  # Show name with cloud icon
                    snippet,
                    key=result["id"],  # Use folder path as internal key
                )

            # Don't steal focus from search input

        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            self.app.notify(f"Search error: {str(e)}", severity="error", timeout=5)
    def _search_cloud_files(self, query: str) -> None:
        """Search cloud files by name and metadata fields."""
        try:
            from mini_datahub.services.storage_manager import get_storage_backend
            from mini_datahub.core.queries import QueryParser
            import yaml
            import tempfile
            import os

            storage = get_storage_backend()
            entries = storage.listdir("")

            # Filter only directories (datasets)
            datasets = [e for e in entries if e.is_dir]

            # Parse query for field searches
            try:
                parser = QueryParser()
                parsed = parser.parse(query)
                has_field_queries = any(not term.is_free_text for term in parsed.terms)
            except:
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
                        with open(tmp_path, 'r', encoding='utf-8') as f:
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
                except:
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
                    description = description[:80] + "..." if len(description) > 80 else description

                    table.add_row(
                        dataset_id,
                        name[:40],
                        description,
                        key=dataset_id,
                    )
                else:
                    # Fallback for entries without metadata
                    table.add_row(
                        dataset_id,
                        f"📁 {dataset_id}"[:40],
                        "No metadata.yaml",
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

    def _get_badge_color_class(self, key: str) -> str:
        """
        Get a consistent color class for a badge based on its key type.

        Maps filter keys to specific colors for visual consistency:
        - project: Blue
        - source: Purple
        - tag: Teal
        - owner: Orange
        - size: Gray
        - format/type: Coral
        - default: Neutral
        """
        key_colors = {
            "project": "badge-blue",
            "source": "badge-purple",
            "tag": "badge-teal",
            "owner": "badge-orange",
            "size": "badge-gray",
            "format": "badge-coral",
            "file_format": "badge-coral",
            "type": "badge-sage",
            "data_type": "badge-sage",
        }
        return key_colors.get(key.lower(), "badge-neutral")

    def _update_filter_badges(self, query: str) -> None:
        """Update visual badges showing active search filters with uniform key-based styling."""
        from mini_datahub.core.queries import QueryParser

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

                    # Get color based on key type (not operator)
                    color_class = self._get_badge_color_class(term.field)

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
                # Free text uses neutral gray color
                color_class = "badge-neutral"
                badge = Static(f"📝 {term.value}", classes=f"filter-badge {color_class}")
                badges_container.mount(badge)
                logger.debug(f"Mounted badge for term: {term.value}")

        except Exception as e:
            # If parsing fails, just show the raw query
            badges_container.mount(Static(f"[dim]🔍 {query}[/dim]", classes="filter-badge"))

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

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self) -> None:
        """Handle search submission - move focus to table."""
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0:
            table.focus()
            self.search_mode = False

    def action_clear_search(self) -> None:
        """Clear search or exit insert mode."""
        search_input = self.query_one("#search-input", Input)

        if self.search_mode:
            # Exit insert mode
            table = self.query_one("#results-table", DataTable)
            table.focus()
            self.search_mode = False
        elif search_input.value:
            # Clear search
            search_input.value = ""
            self.load_all_datasets()
        else:
            # Focus table
            table = self.query_one("#results-table", DataTable)
            table.focus()

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
        table = self.query_one("#results-table", DataTable)
        if table.row_count > 0 and table.cursor_row < table.row_count:
            # Get the row key properly
            try:
                row_key = table.get_row_at(table.cursor_row)[0]
                if row_key:
                    # ALWAYS open cloud dataset details (cloud-only workflow)
                    self._open_cloud_file_preview(str(row_key))
            except Exception as e:
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

            # ALWAYS use cloud mode (cloud-only workflow)
            self._open_cloud_file_preview(row_key)
        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error", timeout=3)

    def action_show_help(self) -> None:
        """Show help overlay with keybindings (? key)."""
        from .help import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_settings(self) -> None:
        """Open settings menu (S key)."""
        from .settings import SettingsScreen
        self.app.push_screen(SettingsScreen())

    def action_pull_updates(self) -> None:
        """Start pull updates task."""
        self.app.pull_updates()

    def action_refresh_data(self) -> None:
        """Refresh/reload all datasets."""
        self.notify("Refreshing datasets...", timeout=2)
        self.load_all_datasets()
        self.notify("✓ Datasets refreshed", timeout=3)

    def action_debug_console(self) -> None:
        """Open debug console (: key)."""
        from mini_datahub.ui.widgets.console import DebugConsoleScreen
        self.app.push_screen(DebugConsoleScreen())
