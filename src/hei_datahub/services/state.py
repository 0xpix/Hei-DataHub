"""
State management for persistent application state.
Tracks last indexed commit, session flags, and other transient state.
"""
from typing import Optional
from pathlib import Path
import json
from datetime import datetime


class StateManager:
    """Manage application state persistence."""

    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize state manager.

        Args:
            state_file: Path to state file (defaults to ~/.hei-datahub/state.json)
        """
        if state_file is None:
            state_file = Path.home() / ".hei-datahub" / "state.json"

        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # In-memory state
        self._state = self._load_state()

        # Reset session-only flags on startup
        self.reset_session_flags()

    def _load_state(self) -> dict:
        """
        Load state from disk.

        Returns:
            State dictionary
        """
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_state(self) -> None:
        """Save state to disk, excluding session-only flags."""
        try:
            # Filter out session-only keys before saving
            session_only_keys = {"dont_prompt_pull_this_session"}
            state_to_save = {k: v for k, v in self._state.items() if k not in session_only_keys}

            with open(self.state_file, 'w') as f:
                json.dump(state_to_save, f, indent=2)
        except Exception:
            pass

    def get_last_indexed_commit(self) -> Optional[str]:
        """
        Get last indexed git commit hash.

        Returns:
            Commit hash or None
        """
        return self._state.get("last_indexed_commit")

    def set_last_indexed_commit(self, commit_hash: str) -> None:
        """
        Set last indexed git commit hash.

        Args:
            commit_hash: Git commit hash
        """
        self._state["last_indexed_commit"] = commit_hash
        self._save_state()

    def get_last_update_check(self) -> Optional[datetime]:
        """
        Get last update check timestamp.

        Returns:
            Datetime or None
        """
        timestamp = self._state.get("last_update_check")
        if timestamp:
            try:
                return datetime.fromisoformat(timestamp)
            except Exception:
                return None
        return None

    def set_last_update_check(self, timestamp: Optional[datetime] = None) -> None:
        """
        Set last update check timestamp.

        Args:
            timestamp: Datetime (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        self._state["last_update_check"] = timestamp.isoformat()
        self._save_state()

    def should_prompt_pull(self) -> bool:
        """
        Check if we should prompt for pull this session.

        Returns:
            True if should prompt
        """
        return not self._state.get("dont_prompt_pull_this_session", False)

    def set_dont_prompt_pull_this_session(self, value: bool = True) -> None:
        """
        Set flag to not prompt for pull this session.

        Args:
            value: True to disable prompts
        """
        self._state["dont_prompt_pull_this_session"] = value
        # Don't persist this - it's session-only

    def reset_session_flags(self) -> None:
        """Reset all session-only flags."""
        self._state.pop("dont_prompt_pull_this_session", None)

    def get_preference(self, key: str, default=None):
        """
        Get user preference value.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value
        """
        preferences = self._state.get("preferences", {})
        return preferences.get(key, default)

    def set_preference(self, key: str, value) -> None:
        """
        Set user preference value.

        Args:
            key: Preference key
            value: Preference value
        """
        if "preferences" not in self._state:
            self._state["preferences"] = {}

        self._state["preferences"][key] = value
        self._save_state()


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """
    Get global state manager instance.

    Returns:
        StateManager instance
    """
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
