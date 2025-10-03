"""
Git operations for automated branching, committing, and pushing.
"""
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


class GitOperationError(Exception):
    """Exception raised for git operation failures."""
    pass


class GitOperations:
    """Handle git operations for the catalog repository."""

    def __init__(self, repo_path: Path):
        """
        Initialize git operations.

        Args:
            repo_path: Path to the git repository (catalog repo)
        """
        self.repo_path = repo_path

    def _run_command(self, cmd: list[str], check: bool = True) -> Tuple[int, str, str]:
        """
        Run a git command.

        Args:
            cmd: Command and arguments
            check: Whether to raise exception on non-zero exit

        Returns:
            Tuple of (exit_code, stdout, stderr)

        Raises:
            GitOperationError: If command fails and check=True
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if check and result.returncode != 0:
                raise GitOperationError(
                    f"Git command failed: {' '.join(cmd)}\n"
                    f"Exit code: {result.returncode}\n"
                    f"Error: {result.stderr}"
                )

            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            raise GitOperationError(f"Git command timed out: {' '.join(cmd)}")
        except Exception as e:
            raise GitOperationError(f"Git command error: {str(e)}")

    def is_git_repo(self) -> bool:
        """Check if the path is a git repository."""
        return (self.repo_path / ".git").exists()

    def get_current_branch(self) -> str:
        """Get current branch name."""
        code, stdout, _ = self._run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return stdout.strip()

    def fetch(self) -> None:
        """Fetch from remote with prune."""
        self._run_command(["git", "fetch", "--prune", "origin"])

    def checkout_branch(self, branch: str, create: bool = False) -> None:
        """
        Checkout a branch.

        Args:
            branch: Branch name
            create: Whether to create the branch if it doesn't exist
        """
        if create:
            self._run_command(["git", "checkout", "-b", branch])
        else:
            self._run_command(["git", "checkout", branch])

    def fast_forward(self, branch: str) -> None:
        """Fast-forward to origin/branch."""
        try:
            self._run_command(["git", "merge", "--ff-only", f"origin/{branch}"])
        except GitOperationError:
            # If fast-forward fails, it's okay - we'll work from current state
            pass

    def create_branch(self, branch_name: str, base_branch: str = "main") -> None:
        """
        Create a new branch from base.

        Args:
            branch_name: Name for the new branch
            base_branch: Base branch to branch from
        """
        # Ensure we're on base branch and up to date
        self.checkout_branch(base_branch)
        self.fetch()
        self.fast_forward(base_branch)

        # Create new branch
        self.checkout_branch(branch_name, create=True)

    def stage_files(self, patterns: list[str]) -> None:
        """
        Stage files matching patterns.

        Args:
            patterns: List of file patterns to stage (e.g., ["data/*/metadata.yaml"])
        """
        for pattern in patterns:
            self._run_command(["git", "add", pattern])

    def commit(self, message: str) -> None:
        """
        Create a commit.

        Args:
            message: Commit message
        """
        self._run_command(["git", "commit", "-m", message])

    def push(self, remote: str = "origin", branch: Optional[str] = None, force: bool = False) -> None:
        """
        Push to remote.

        Args:
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)
            force: Whether to force push
        """
        if branch is None:
            branch = self.get_current_branch()

        cmd = ["git", "push", remote, branch]
        if force:
            cmd.append("--force")

        self._run_command(cmd)

    def has_changes(self, path: str) -> bool:
        """
        Check if there are changes in a specific path.

        Args:
            path: Path to check

        Returns:
            True if there are changes
        """
        code, stdout, _ = self._run_command(
            ["git", "status", "--porcelain", path],
            check=False
        )
        return bool(stdout.strip())

    def get_remote_url(self, remote: str = "origin") -> str:
        """Get remote URL."""
        code, stdout, _ = self._run_command(["git", "remote", "get-url", remote])
        return stdout.strip()

    def set_remote_url(self, remote: str, url: str) -> None:
        """Set remote URL."""
        self._run_command(["git", "remote", "set-url", remote, url])

    def add_remote(self, remote: str, url: str) -> None:
        """Add a remote."""
        self._run_command(["git", "remote", "add", remote, url])

    def has_remote(self, remote: str) -> bool:
        """Check if remote exists."""
        code, stdout, _ = self._run_command(
            ["git", "remote", "get-url", remote],
            check=False
        )
        return code == 0

    def ensure_remote(self, remote: str, url: str) -> None:
        """Ensure remote exists with correct URL."""
        if self.has_remote(remote):
            current_url = self.get_remote_url(remote)
            if current_url != url:
                self.set_remote_url(remote, url)
        else:
            self.add_remote(remote, url)


def generate_branch_name(dataset_id: str) -> str:
    """
    Generate a unique branch name for a dataset.

    Args:
        dataset_id: Dataset ID

    Returns:
        Branch name in format: add/<dataset-id>-<timestamp>
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    return f"add/{dataset_id}-{timestamp}"


def format_commit_message(dataset_id: str, dataset_name: str) -> str:
    """
    Format commit message according to convention.

    Args:
        dataset_id: Dataset ID
        dataset_name: Dataset name

    Returns:
        Formatted commit message
    """
    return f"feat(dataset): add {dataset_id} — {dataset_name}"
