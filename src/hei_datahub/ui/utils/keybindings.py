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
            # Use priority=True for bindings with modifiers so they work even when Input has focus
            has_modifier = any(mod in key.lower() for mod in ["ctrl+", "alt+", "shift+"])
            bindings.append(
                Binding(
                    key,
                    action,
                    display_name,  # Always include description for command palette
                    key_display=key_display if i == 0 else key,
                    show=show if i == 0 else False,  # Only show first binding in footer
                    priority=has_modifier,  # Priority bindings work even when Input is focused
                )
            )

    return bindings


def get_action_display_map_home() -> dict[str, tuple]:
    """Get action display map for home screen."""
    return {
        "add_dataset": ("Add Dataset", "Ctrl+N", True),
        "settings": ("Settings", "Ctrl+S", True),
        "open_details": ("Open", "o", False),
        "check_updates": ("Check Updates", "Ctrl+U", True),
        "refresh_data": ("Refresh", "Ctrl+R", True),
        "quit": ("Quit", "Ctrl+Q", True),
        "show_about": ("About", "F1", True),
        "move_down": ("Down", "j", False),
        "move_up": ("Up", "k", False),
        "jump_top": ("Top", "g g", False),
        "jump_bottom": ("Bottom", "G", False),
        "focus_search": ("Search", "Ctrl+F", True),
        "clear_search": ("Clear", "Esc", False),
        "debug_console": ("Debug", ":", False),
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
        # priority=True ensures modifier bindings work even when Input widget is focused
        return [
            Binding("ctrl+n", "add_dataset", "Add Dataset", key_display="Ctrl+N", priority=True),
            Binding("ctrl+s", "settings", "Settings", key_display="Ctrl+S", priority=True),
            Binding("o", "open_details", "Open", show=False),
            Binding("enter", "open_details", "View Details", show=False),
            Binding("ctrl+u", "check_updates", "Check Updates", key_display="Ctrl+U", priority=True),
            Binding("ctrl+r", "refresh_data", "Refresh", key_display="Ctrl+R", priority=True),
            Binding("ctrl+q", "quit", "Quit", key_display="Ctrl+Q", priority=True),
            Binding("f1", "show_about", "About", key_display="F1", priority=True),
            Binding("j", "move_down", "Down", show=False),
            Binding("k", "move_up", "Up", show=False),
            Binding("down", "move_down", "", show=False),
            Binding("up", "move_up", "", show=False),
            # Note: 'gg' is handled manually in on_key() method to require double-press
            Binding("G", "jump_bottom", "Bottom", show=False),
            Binding("/", "focus_search", "Search", show=False),
            Binding("ctrl+f", "focus_search", "Search", key_display="Ctrl+F", priority=True),
            Binding("escape", "clear_search", "Clear", show=False),
            Binding(":", "debug_console", "Debug", show=False),
        ]
