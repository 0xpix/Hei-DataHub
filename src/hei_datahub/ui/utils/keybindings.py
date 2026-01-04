"""
Keybinding utilities for dynamically binding actions from config.

Provides generic binding utilities and screen-specific binding builders.
"""
import logging

from textual.binding import Binding

logger = logging.getLogger(__name__)


def bind_actions_from_config(
    action_map: dict[str, tuple],
    keys_cfg: dict[str, list[str]]
) -> list[Binding]:
    """
    Build Textual bindings from config and action map.

    Args:
        action_map: Map of action_name -> (display_name, key_display, show_in_footer)
        keys_cfg: Config keybindings dict {action_name: [keys]}

    Returns:
        List of Textual Binding objects

    Example:
        action_map = {
            "add_dataset": ("Add Dataset", "a", True),
            "quit": ("Quit", "q", True),
        }
        keys_cfg = {
            "add_dataset": ["a", "ctrl+n"],
            "quit": ["q", "ctrl+c"],
        }
        bindings = bind_actions_from_config(action_map, keys_cfg)
    """
    bindings = []

    for action, (display_name, key_display, show) in action_map.items():
        # Skip jump_top as it's handled manually in on_key() to require double 'g' press
        if action == "jump_top":
            continue

        keys = keys_cfg.get(action, [])
        if not keys:
            logger.warning(f"No keys configured for action: {action}")
            continue

        # Add bindings for each key
        for i, key in enumerate(keys):
            bindings.append(
                Binding(
                    key,
                    action,
                    display_name if i == 0 else "",  # Only show display for first key
                    key_display=key_display if i == 0 else key,
                    show=show if i == 0 else False  # Only show first binding in footer
                )
            )

    return bindings


def get_action_display_map_home() -> dict[str, tuple]:
    """Get action display map for home screen."""
    return {
        "add_dataset": ("Add Dataset", "a", True),
        "settings": ("Settings", "s", True),
        "open_details": ("Open", "o", False),
        "pull_updates": ("Pull", "u", False),
        "refresh_data": ("Refresh", "r", True),
        "quit": ("Quit", "^q", True),
        "show_about": ("About", "^a", True),
        "move_down": ("Down", "j", False),
        "move_up": ("Up", "k", False),
        "jump_top": ("Top", "g g", False),
        "jump_bottom": ("Bottom", "G", False),
        "focus_search": ("Search", "/", True),
        "clear_search": ("Clear", "esc", False),
        "debug_console": ("Debug", ":", False),
        "show_help": ("Help", "?", True),
    }


def get_action_display_map_add_form() -> dict[str, tuple]:
    """Get action display map for add data form."""
    return {
        "cancel": ("Cancel", "esc", True),
        "submit": ("Save", "ctrl+s", True),
        "next_field": ("Next", "j", False),
        "prev_field": ("Prev", "k", False),
        "scroll_down": ("Scroll Down", "ctrl+d", False),
        "scroll_up": ("Scroll Up", "ctrl+u", False),
        "jump_first": ("First", "g", False),
        "jump_last": ("Last", "G", False),
    }


def get_action_display_map_settings() -> dict[str, tuple]:
    """Get action display map for settings screen."""
    return {
        "back": ("Back", "esc", True),
        "save_settings": ("Save", "s", True),
    }


def build_home_bindings() -> list[Binding]:
    """Build keybindings list from config file."""
    try:
        from hei_datahub.services.config import get_config

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
            Binding("a", "show_about", "About", key_display="^a"),
            Binding("j", "move_down", "Down", show=False),
            Binding("k", "move_up", "Up", show=False),
            Binding("down", "move_down", "", show=False),
            Binding("up", "move_up", "", show=False),
            # Note: 'gg' is handled manually in on_key() method to require double-press
            Binding("G", "jump_bottom", "Bottom", show=False),
            Binding("/", "focus_search", "Search", key_display="/"),
            Binding("escape", "clear_search", "Clear", show=False),
            Binding(":", "debug_console", "Debug", show=False),
            Binding("?", "show_help", "Help", key_display="?"),
        ]
