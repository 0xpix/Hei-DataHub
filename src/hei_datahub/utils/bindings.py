"""
TUI application using Textual framework with Neovim-style keybindings.
"""
import logging

logger = logging.getLogger(__name__)
from textual.binding import Binding

from hei_datahub.services.config import get_config
from hei_datahub.ui.keybindings import bind_actions_from_config, get_action_display_map_home

def _build_bindings_from_config() -> list[Binding]:
    """Build keybindings list from config file."""
    try:
        config = get_config()
        keybindings = config.get_keybindings()
        action_map = get_action_display_map_home()

        bindings = bind_actions_from_config(action_map, keybindings)

        if not bindings:
            logger.warning("No bindings generated from config, using defaults")
            raise ValueError("Empty bindings")

        return bindings
    except Exception as e:
        logger.warning(f"Failed to load keybindings from config: {e}, using defaults")
        # Fallback to hardcoded defaults if config fails
        return [
            Binding("a", "add_dataset", "Add Dataset", key_display="a"),
            Binding("s", "settings", "Settings", key_display="s"),
            Binding("o", "open_details", "Open", show=False),
            Binding("enter", "open_details", "View Details", show=False),
            Binding("u", "pull_updates", "Update", key_display="u"),
            Binding("r", "refresh_data", "Refresh", key_display="r"),
            Binding("q", "quit", "Quit", key_display="^q"),
            Binding("j", "move_down", "Down", show=False),
            Binding("k", "move_up", "Up", show=False),
            Binding("down", "move_down", "", show=False),
            Binding("up", "move_up", "", show=False),
            Binding("gg", "jump_top", "Top", key_display="gg", show=False),
            Binding("G", "jump_bottom", "Bottom", show=False),
            Binding("/", "focus_search", "Search", key_display="/"),
            Binding("escape", "clear_search", "Clear", show=False),
            Binding(":", "debug_console", "Debug", show=False),
            Binding("?", "show_help", "Help", key_display="?"),
        ]
