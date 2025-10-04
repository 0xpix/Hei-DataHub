"""
Auto-pull functionality for syncing with upstream catalog repository.
Handles git fetch, pull, and safe fast-forward operations.
"""
from pathlib import Path
from typing import Tuple, Optional, List
from datetime import datetime
import subprocess

from mini_datahub.git_ops import GitOperations, GitOperationError


class AutoPullError(Exception):
    """Exception raised for auto-pull errors."""
    pass


class AutoPullManager:
    """Manage automatic pulling and syncing from upstream catalog."""

    def __init__(self, catalog_path: Path):
        """
        Initialize auto-pull manager.

        Args:
            catalog_path: Path to local catalog repository
        """
        self.catalog_path = catalog_path.expanduser().resolve()
        self.git_ops = GitOperations(self.catalog_path)

    def check_network_available(self) -> bool:
        """
        Quick check if network is available.

        Returns:
            True if network appears available
        """
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", "github.com"],
                capture_output=True,
                timeout=2,
            )
            return result.returncode == 0
        except Exception:
            return False

    def has_local_changes(self) -> Tuple[bool, str]:
        """
        Check if catalog repo has uncommitted changes.

        Returns:
            Tuple of (has_changes, status_output)
        """
        try:
            code, stdout, _ = self.git_ops._run_command(
                ["git", "status", "--porcelain"],
                check=False
            )
            has_changes = bool(stdout.strip())
            return has_changes, stdout
        except Exception as e:
            return False, str(e)

    def is_behind_remote(self, branch: str = "main") -> Tuple[bool, int]:
        """
        Check if local branch is behind remote.

        Args:
            branch: Branch name to check

        Returns:
            Tuple of (is_behind, commits_behind)
        """
        try:
            # Fetch to get latest remote refs
            self.git_ops.fetch()

            # Get commit counts
            code, stdout, _ = self.git_ops._run_command(
                ["git", "rev-list", "--count", f"HEAD..origin/{branch}"],
                check=False
            )

            if code == 0:
                commits_behind = int(stdout.strip())
                return commits_behind > 0, commits_behind

            return False, 0

        except Exception:
            return False, 0

    def is_diverged(self, branch: str = "main") -> Tuple[bool, int, int]:
        """
        Check if local and remote branches have diverged.

        Args:
            branch: Branch name to check

        Returns:
            Tuple of (is_diverged, commits_ahead, commits_behind)
        """
        try:
            # Check ahead
            code, ahead_str, _ = self.git_ops._run_command(
                ["git", "rev-list", "--count", f"origin/{branch}..HEAD"],
                check=False
            )
            commits_ahead = int(ahead_str.strip()) if code == 0 else 0

            # Check behind
            code, behind_str, _ = self.git_ops._run_command(
                ["git", "rev-list", "--count", f"HEAD..origin/{branch}"],
                check=False
            )
            commits_behind = int(behind_str.strip()) if code == 0 else 0

            is_diverged = commits_ahead > 0 and commits_behind > 0
            return is_diverged, commits_ahead, commits_behind

        except Exception:
            return False, 0, 0

    def get_changed_files_since_commit(self, since_commit: str, until_commit: str = "HEAD") -> List[str]:
        """
        Get list of files changed between two commits.

        Args:
            since_commit: Starting commit hash
            until_commit: Ending commit hash (default HEAD)

        Returns:
            List of changed file paths
        """
        try:
            code, stdout, _ = self.git_ops._run_command(
                ["git", "diff", "--name-only", since_commit, until_commit],
                check=False
            )

            if code == 0 and stdout:
                return [line.strip() for line in stdout.strip().split('\n') if line.strip()]

            return []

        except Exception:
            return []

    def has_metadata_changes(self, since_commit: str, until_commit: str = "HEAD") -> Tuple[bool, int]:
        """
        Check if any metadata.yaml files changed between commits.

        Args:
            since_commit: Starting commit hash
            until_commit: Ending commit hash

        Returns:
            Tuple of (has_changes, count_of_changed_files)
        """
        changed_files = self.get_changed_files_since_commit(since_commit, until_commit)
        metadata_files = [f for f in changed_files if f.startswith('data/') and f.endswith('metadata.yaml')]
        return len(metadata_files) > 0, len(metadata_files)

    def get_current_commit(self) -> Optional[str]:
        """
        Get current HEAD commit hash.

        Returns:
            Commit hash or None
        """
        try:
            code, stdout, _ = self.git_ops._run_command(
                ["git", "rev-parse", "HEAD"],
                check=False
            )
            if code == 0:
                return stdout.strip()
            return None
        except Exception:
            return None

    def pull_updates(self, branch: str = "main") -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Pull updates from remote repository.

        Args:
            branch: Branch to pull

        Returns:
            Tuple of (success, message, old_commit, new_commit)
        """
        # Check for local changes first
        has_changes, status = self.has_local_changes()
        if has_changes:
            return (
                False,
                f"Local changes detected in catalog repo. Please commit/stash or discard.\nPath: {self.catalog_path}",
                None,
                None
            )

        # Check if diverged
        is_diverged, ahead, behind = self.is_diverged(branch)
        if is_diverged:
            return (
                False,
                f"Local branch has diverged from remote (+{ahead} -{behind} commits). Resolve manually.\nPath: {self.catalog_path}",
                None,
                None
            )

        # Get current commit before pull
        old_commit = self.get_current_commit()

        try:
            # Fetch latest
            self.git_ops.fetch()

            # Check if behind
            is_behind, commits = self.is_behind_remote(branch)
            if not is_behind:
                return (
                    True,
                    "Already up to date with remote.",
                    old_commit,
                    old_commit
                )

            # Checkout branch
            self.git_ops.checkout_branch(branch)

            # Fast-forward pull
            self.git_ops.fast_forward(branch)

            # Get new commit
            new_commit = self.get_current_commit()

            return (
                True,
                f"Pulled {commits} commit(s) from {branch}.",
                old_commit,
                new_commit
            )

        except GitOperationError as e:
            return (
                False,
                f"Pull failed: {str(e)}",
                old_commit,
                None
            )
        except Exception as e:
            return (
                False,
                f"Unexpected error during pull: {str(e)}",
                old_commit,
                None
            )


def get_auto_pull_manager(catalog_path: Path) -> AutoPullManager:
    """
    Factory function to create AutoPullManager.

    Args:
        catalog_path: Path to catalog repository

    Returns:
        AutoPullManager instance
    """
    return AutoPullManager(catalog_path)
