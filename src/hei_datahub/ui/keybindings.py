"""
Keybinding utilities for dynamically binding actions from config.
"""
import logging
from typing import Dict
from textual.binding import Binding

logger = logging.getLogger(__name__)


def bind_actions_from_config(
    action_map: Dict[str, tuple],
    keys_cfg: Dict[str, list[str]]
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


def get_action_display_map_home() -> Dict[str, tuple]:
    """Get action display map for home screen."""
    return {
        "add_dataset": ("Add Dataset", "a", True),
        "settings": ("Settings", "s", True),
        "open_details": ("Open", "o", False),
        "outbox": ("Outbox", "p", True),
        "pull_updates": ("Pull", "u", True),
        "refresh_data": ("Refresh", "r", True),
        "quit": ("Quit", "q", True),
        "move_down": ("Down", "j", False),
        "move_up": ("Up", "k", False),
        "jump_top": ("Top", "gg", False),
        "jump_bottom": ("Bottom", "G", False),
        "focus_search": ("Search", "/", True),
        "clear_search": ("Clear", "esc", False),
        "debug_console": ("Debug", ":", False),
        "show_help": ("Help", "?", True),
    }


def get_action_display_map_details() -> Dict[str, tuple]:
    """Get action display map for details screen."""
    return {
        "back": ("Back", "q", True),
        "copy_source": ("Copy", "y", True),
        "open_url": ("Open URL", "o", True),
        "enter_edit_mode": ("Edit", "e", True),
        "publish_pr": ("Publish PR", "P", True),
    }


def get_action_display_map_add_form() -> Dict[str, tuple]:
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


def get_action_display_map_settings() -> Dict[str, tuple]:
    """Get action display map for settings screen."""
    return {
        "back": ("Back", "esc", True),
        "save_settings": ("Save", "s", True),
    }
