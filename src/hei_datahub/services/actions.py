"""
Action registry for command palette and keybindings.

Provides a centralized registry of all available actions in the TUI.
"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ActionContext(Enum):
    """Context where an action is available."""
    GLOBAL = "global"
    HOME = "home"
    DETAILS = "details"
    SETTINGS = "settings"
    FORM = "form"
    OUTBOX = "outbox"


@dataclass
class Action:
    """
    An action that can be triggered by the user.
    """
    id: str
    label: str
    description: str
    contexts: list[ActionContext]
    handler: Optional[Callable] = None
    default_keys: list[str] = None

    def __post_init__(self):
        if self.default_keys is None:
            self.default_keys = []

    def is_available_in(self, context: ActionContext) -> bool:
        """Check if action is available in a given context."""
        return ActionContext.GLOBAL in self.contexts or context in self.contexts


class ActionRegistry:
    """
    Registry of all available actions.
    """

    def __init__(self):
        self._actions: dict[str, Action] = {}
        self._recent_actions: list[str] = []
        self._max_recent = 10
        self._register_built_in_actions()

    def _register_built_in_actions(self) -> None:
        """Register all built-in actions."""
        # Navigation actions
        self.register(Action(
            id="quit",
            label="Quit",
            description="Exit the application",
            contexts=[ActionContext.GLOBAL],
            default_keys=["q", "ctrl+c"]
        ))

        self.register(Action(
            id="home",
            label="Go to Home",
            description="Navigate to the home screen",
            contexts=[ActionContext.GLOBAL],
            default_keys=["escape"]
        ))

        self.register(Action(
            id="settings",
            label="Open Settings",
            description="Open the settings screen",
            contexts=[ActionContext.GLOBAL, ActionContext.HOME],
            default_keys=["s"]
        ))

        self.register(Action(
            id="help",
            label="Show Help",
            description="Show help and keybindings",
            contexts=[ActionContext.GLOBAL],
            default_keys=["?"]
        ))

        self.register(Action(
            id="command_palette",
            label="Command Palette",
            description="Open the command palette",
            contexts=[ActionContext.GLOBAL],
            default_keys=["ctrl+p"]
        ))

        # Search actions
        self.register(Action(
            id="search",
            label="Search",
            description="Focus the search input",
            contexts=[ActionContext.HOME],
            default_keys=["/"]
        ))

        self.register(Action(
            id="clear_search",
            label="Clear Search",
            description="Clear the search query",
            contexts=[ActionContext.HOME],
            default_keys=["ctrl+u"]
        ))

        # Dataset actions
        self.register(Action(
            id="add_dataset",
            label="Add Dataset",
            description="Open the add dataset form",
            contexts=[ActionContext.HOME],
            default_keys=["a"]
        ))

        self.register(Action(
            id="view_details",
            label="View Details",
            description="View dataset details",
            contexts=[ActionContext.HOME],
            default_keys=["enter"]
        ))

        self.register(Action(
            id="edit_dataset",
            label="Edit Dataset",
            description="Edit dataset metadata",
            contexts=[ActionContext.DETAILS],
            default_keys=["e"]
        ))

        self.register(Action(
            id="delete_dataset",
            label="Delete Dataset",
            description="Delete the current dataset",
            contexts=[ActionContext.DETAILS],
            default_keys=["d"]
        ))

        self.register(Action(
            id="copy_source",
            label="Copy Source URL",
            description="Copy the dataset source URL to clipboard",
            contexts=[ActionContext.DETAILS],
            default_keys=["c"]
        ))

        self.register(Action(
            id="open_url",
            label="Open URL in Browser",
            description="Open the dataset source URL in browser",
            contexts=[ActionContext.DETAILS],
            default_keys=["o"]
        ))

        # Data management actions
        self.register(Action(
            id="reindex",
            label="Reindex All Datasets",
            description="Rebuild the search index",
            contexts=[ActionContext.HOME, ActionContext.SETTINGS],
            default_keys=["ctrl+r"]
        ))

        self.register(Action(
            id="refresh",
            label="Refresh",
            description="Refresh the current view",
            contexts=[ActionContext.GLOBAL],
            default_keys=["r"]
        ))

        self.register(Action(
            id="sync_pull",
            label="Pull Updates",
            description="Pull updates from remote",
            contexts=[ActionContext.HOME],
            default_keys=["u"]
        ))

        # Navigation (Vim-style)
        self.register(Action(
            id="nav_down",
            label="Navigate Down",
            description="Move selection down",
            contexts=[ActionContext.HOME],
            default_keys=["j", "down"]
        ))

        self.register(Action(
            id="nav_up",
            label="Navigate Up",
            description="Move selection up",
            contexts=[ActionContext.HOME],
            default_keys=["k", "up"]
        ))

        self.register(Action(
            id="nav_top",
            label="Go to Top",
            description="Jump to the first item",
            contexts=[ActionContext.HOME],
            default_keys=["gg"]
        ))

        self.register(Action(
            id="nav_bottom",
            label="Go to Bottom",
            description="Jump to the last item",
            contexts=[ActionContext.HOME],
            default_keys=["G"]
        ))

        # Form actions
        self.register(Action(
            id="save",
            label="Save",
            description="Save changes",
            contexts=[ActionContext.FORM, ActionContext.DETAILS],
            default_keys=["ctrl+s"]
        ))

        self.register(Action(
            id="cancel",
            label="Cancel",
            description="Cancel and discard changes",
            contexts=[ActionContext.FORM, ActionContext.DETAILS],
            default_keys=["escape"]
        ))

        # Edit mode actions
        self.register(Action(
            id="undo",
            label="Undo",
            description="Undo last change",
            contexts=[ActionContext.DETAILS],
            default_keys=["ctrl+z"]
        ))

        self.register(Action(
            id="redo",
            label="Redo",
            description="Redo last undone change",
            contexts=[ActionContext.DETAILS],
            default_keys=["ctrl+shift+z"]
        ))

    def register(self, action: Action) -> None:
        """
        Register an action.

        Args:
            action: Action to register
        """
        self._actions[action.id] = action
        logger.debug(f"Registered action: {action.id}")

    def get(self, action_id: str) -> Optional[Action]:
        """
        Get an action by ID.

        Args:
            action_id: Action ID

        Returns:
            Action if found, None otherwise
        """
        return self._actions.get(action_id)

    def get_all(self) -> list[Action]:
        """Get all registered actions."""
        return list(self._actions.values())

    def get_for_context(self, context: ActionContext) -> list[Action]:
        """
        Get all actions available in a context.

        Args:
            context: Context to filter by

        Returns:
            List of actions available in the context
        """
        return [
            action for action in self._actions.values()
            if action.is_available_in(context)
        ]

    def search(self, query: str, context: Optional[ActionContext] = None) -> list[Action]:
        """
        Search for actions by label or description.

        Args:
            query: Search query
            context: Optional context to filter by

        Returns:
            List of matching actions
        """
        query_lower = query.lower()
        actions = self.get_for_context(context) if context else self.get_all()

        matches = []
        for action in actions:
            if (query_lower in action.label.lower() or
                query_lower in action.description.lower() or
                query_lower in action.id.lower()):
                matches.append(action)

        return matches

    def track_recent(self, action_id: str) -> None:
        """
        Track a recently used action.

        Args:
            action_id: Action ID
        """
        if action_id in self._recent_actions:
            self._recent_actions.remove(action_id)
        self._recent_actions.insert(0, action_id)
        self._recent_actions = self._recent_actions[:self._max_recent]

    def get_recent(self, limit: int = 5) -> list[Action]:
        """
        Get recently used actions.

        Args:
            limit: Maximum number of actions to return

        Returns:
            List of recent actions
        """
        return [
            self._actions[action_id]
            for action_id in self._recent_actions[:limit]
            if action_id in self._actions
        ]


# Global registry instance
_action_registry: Optional[ActionRegistry] = None


def get_action_registry() -> ActionRegistry:
    """Get the global action registry instance."""
    global _action_registry
    if _action_registry is None:
        _action_registry = ActionRegistry()
    return _action_registry
