"""
Configuration management with secure credential storage.
Uses keyring for secure token storage (OS keychain).
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

from mini_datahub.utils import PROJECT_ROOT

CONFIG_FILE = PROJECT_ROOT / ".datahub_config.json"
KEYRING_SERVICE = "mini-datahub"
KEYRING_USERNAME = "github-token"


class GitHubConfig:
    """GitHub configuration manager with secure token storage."""

    def __init__(self):
        self.host: str = "github.com"
        self.owner: str = ""
        self.repo: str = ""
        self.default_branch: str = "main"
        self.username: str = ""
        self._token: Optional[str] = None
        self.auto_assign_reviewers: list[str] = []
        self.pr_labels: list[str] = ["dataset:add", "needs-review"]
        self.catalog_repo_path: Optional[str] = None  # Local path to catalog repo

        # Load config from file
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not CONFIG_FILE.exists():
            return

        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)

            self.host = data.get("host", "github.com")
            self.owner = data.get("owner", "")
            self.repo = data.get("repo", "")
            self.default_branch = data.get("default_branch", "main")
            self.username = data.get("username", "")
            self.auto_assign_reviewers = data.get("auto_assign_reviewers", [])
            self.pr_labels = data.get("pr_labels", ["dataset:add", "needs-review"])
            self.catalog_repo_path = data.get("catalog_repo_path")

            # Try to load token from keyring
            if KEYRING_AVAILABLE and self.username:
                try:
                    self._token = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
                except Exception:
                    pass
        except Exception:
            pass

    def save_config(self, save_token: bool = True) -> None:
        """
        Save configuration to file and token to keyring.

        Args:
            save_token: Whether to save the token to keyring
        """
        data = {
            "host": self.host,
            "owner": self.owner,
            "repo": self.repo,
            "default_branch": self.default_branch,
            "username": self.username,
            "auto_assign_reviewers": self.auto_assign_reviewers,
            "pr_labels": self.pr_labels,
            "catalog_repo_path": self.catalog_repo_path,
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

        # Save token to keyring
        if save_token and KEYRING_AVAILABLE and self._token:
            try:
                keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, self._token)
            except Exception:
                pass

    def set_token(self, token: str) -> None:
        """Set the GitHub token."""
        self._token = token

    def get_token(self) -> Optional[str]:
        """Get the GitHub token."""
        return self._token

    def clear_token(self) -> None:
        """Clear the GitHub token from memory and keyring."""
        self._token = None
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            except Exception:
                pass

    def is_configured(self) -> bool:
        """Check if GitHub is configured."""
        return bool(
            self.host
            and self.owner
            and self.repo
            and self.username
            and self._token
        )

    def get_repo_fullname(self) -> str:
        """Get repository in owner/repo format."""
        return f"{self.owner}/{self.repo}"

    def get_api_base_url(self) -> str:
        """Get GitHub API base URL."""
        if self.host == "github.com":
            return "https://api.github.com"
        else:
            # GitHub Enterprise
            return f"https://{self.host}/api/v3"

    def to_dict(self) -> Dict[str, Any]:
        """Export config as dictionary (without token)."""
        return {
            "host": self.host,
            "owner": self.owner,
            "repo": self.repo,
            "default_branch": self.default_branch,
            "username": self.username,
            "auto_assign_reviewers": self.auto_assign_reviewers,
            "pr_labels": self.pr_labels,
            "catalog_repo_path": self.catalog_repo_path,
            "has_token": bool(self._token),
        }


# Global config instance
_config_instance: Optional[GitHubConfig] = None


def get_github_config() -> GitHubConfig:
    """Get the global GitHub configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = GitHubConfig()
    return _config_instance


def reload_config() -> GitHubConfig:
    """Reload configuration from file."""
    global _config_instance
    _config_instance = GitHubConfig()
    return _config_instance
