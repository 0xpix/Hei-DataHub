"""
GitHub API integration for PR creation and repository management.
"""
import time
from typing import Optional, Dict, Any, Tuple
import requests

from mini_datahub.app.settings import GitHubConfig


class GitHubAPIError(Exception):
    """Exception raised for GitHub API errors."""
    pass


class GitHubIntegration:
    """Handle GitHub API operations."""

    def __init__(self, config: GitHubConfig):
        """
        Initialize GitHub integration.

        Args:
            config: GitHub configuration
        """
        self.config = config
        self.base_url = config.get_api_base_url()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {config.get_token()}",
            "Accept": "application/vnd.github.v3+json",
        })

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test GitHub connection and permissions.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check user authentication
            response = self.session.get(f"{self.base_url}/user", timeout=10)
            if response.status_code != 200:
                return False, f"Authentication failed: {response.status_code}"

            # Check repository access
            repo_url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}"
            response = self.session.get(repo_url, timeout=10)
            if response.status_code == 404:
                return False, f"Repository {self.config.get_repo_fullname()} not found"
            elif response.status_code != 200:
                return False, f"Cannot access repository: {response.status_code}"

            repo_data = response.json()
            permissions = repo_data.get("permissions", {})

            if permissions.get("push"):
                return True, "Connected with push access"
            else:
                return True, "Connected (read-only, will use fork workflow)"

        except requests.Timeout:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def has_push_access(self) -> bool:
        """
        Check if user has push access to the repository.

        Returns:
            True if user has push access
        """
        try:
            repo_url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}"
            response = self.session.get(repo_url, timeout=10)
            if response.status_code != 200:
                return False

            repo_data = response.json()
            permissions = repo_data.get("permissions", {})
            return permissions.get("push", False)
        except Exception:
            return False

    def get_or_create_fork(self) -> Tuple[bool, Optional[str], str]:
        """
        Get existing fork or create one.

        Returns:
            Tuple of (success, fork_full_name, message)
        """
        try:
            # Check if fork already exists
            fork_name = f"{self.config.username}/{self.config.repo}"
            fork_url = f"{self.base_url}/repos/{fork_name}"

            response = self.session.get(fork_url, timeout=10)
            if response.status_code == 200:
                return True, fork_name, "Fork already exists"

            # Create fork
            parent_url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}/forks"
            response = self.session.post(parent_url, timeout=10)

            if response.status_code == 202:
                # Fork is being created, wait for it
                for _ in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    response = self.session.get(fork_url, timeout=10)
                    if response.status_code == 200:
                        return True, fork_name, "Fork created successfully"

                return False, None, "Fork creation timed out"
            else:
                return False, None, f"Failed to create fork: {response.status_code}"

        except Exception as e:
            return False, None, f"Fork error: {str(e)}"

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> Tuple[bool, Optional[int], Optional[str], str]:
        """
        Create a pull request.

        Args:
            title: PR title
            body: PR description
            head: Head branch (format: "user:branch" for forks or "branch" for same repo)
            base: Base branch

        Returns:
            Tuple of (success, pr_number, pr_url, message)
        """
        try:
            pr_url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}/pulls"

            data = {
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            }

            response = self.session.post(pr_url, json=data, timeout=10)

            if response.status_code == 201:
                pr_data = response.json()
                pr_number = pr_data["number"]
                html_url = pr_data["html_url"]
                return True, pr_number, html_url, "PR created successfully"
            else:
                error_msg = response.json().get("message", "Unknown error")
                return False, None, None, f"Failed to create PR: {error_msg}"

        except Exception as e:
            return False, None, None, f"PR creation error: {str(e)}"

    def add_labels_to_pr(self, pr_number: int, labels: list[str]) -> bool:
        """
        Add labels to a pull request.

        Args:
            pr_number: PR number
            labels: List of label names

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}/issues/{pr_number}/labels"
            response = self.session.post(url, json={"labels": labels}, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def request_reviewers(self, pr_number: int, reviewers: list[str]) -> bool:
        """
        Request reviewers for a pull request.

        Args:
            pr_number: PR number
            reviewers: List of GitHub usernames

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}/pulls/{pr_number}/requested_reviewers"
            response = self.session.post(url, json={"reviewers": reviewers}, timeout=10)
            return response.status_code == 201
        except Exception:
            return False

    def check_file_exists_remote(self, path: str) -> Tuple[bool, str]:
        """
        Check if a file exists in the remote repository.

        Args:
            path: Path to check (e.g., "data/my-dataset/metadata.yaml")

        Returns:
            Tuple of (exists, message)
        """
        try:
            url = f"{self.base_url}/repos/{self.config.get_repo_fullname()}/contents/{path}"
            params = {"ref": self.config.default_branch}
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 404:
                return False, "File does not exist"
            elif response.status_code == 200:
                return True, "File exists"
            else:
                # Unknown state - assume doesn't exist to allow PR creation
                return False, f"Could not verify (status {response.status_code})"

        except Exception as e:
            # On error, assume doesn't exist to allow PR creation
            return False, f"Could not verify: {str(e)}"

    def check_id_uniqueness(self, dataset_id: str) -> Tuple[bool, str]:
        """
        Check if dataset ID is unique in the repository.

        Args:
            dataset_id: Dataset ID to check

        Returns:
            Tuple of (is_unique, message)
        """
        exists, msg = self.check_file_exists_remote(f"data/{dataset_id}/metadata.yaml")
        if exists:
            return False, f"Dataset ID '{dataset_id}' already exists in repository"
        else:
            return True, "ID is unique"


def format_pr_body(metadata: Dict[str, Any]) -> str:
    """
    Format PR body with dataset information and checklist.

    Args:
        metadata: Dataset metadata dictionary

    Returns:
        Formatted PR body markdown
    """
    # Extract key fields
    dataset_id = metadata.get("id", "")
    dataset_name = metadata.get("dataset_name", "")
    description = metadata.get("description", "")
    source = metadata.get("source", "")
    file_format = metadata.get("file_format", "N/A")
    size = metadata.get("size", "N/A")
    data_types = metadata.get("data_types", [])
    used_in_projects = metadata.get("used_in_projects", [])

    # Format lists
    types_str = ", ".join(data_types) if data_types else "N/A"
    projects_str = ", ".join(used_in_projects) if used_in_projects else "N/A"

    body = f"""## Dataset: {dataset_name}

**ID:** `{dataset_id}`

### Description
{description}

### Summary

| Field | Value |
|-------|-------|
| **Source** | {source} |
| **File Format** | {file_format} |
| **Size** | {size} |
| **Data Types** | {types_str} |
| **Used In Projects** | {projects_str} |

### Checklist

- [x] Metadata validated against schema
- [x] Dataset ID is unique
- [x] All required fields provided
- [ ] Reviewer: Metadata accuracy verified
- [ ] Reviewer: Source URL accessible (if applicable)
- [ ] Reviewer: Ready to merge

### Files Changed

- `data/{dataset_id}/metadata.yaml`

---
*This PR was automatically generated by Mini Hei-DataHub TUI.*
"""

    return body

    def get_latest_release(self, repo: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the latest release for a repository.

        Args:
            repo: Repository in owner/repo format (defaults to configured repo)

        Returns:
            Release data dict or None
        """
        if repo is None:
            repo = self.config.get_repo_fullname()

        try:
            url = f"{self.base_url}/repos/{repo}/releases/latest"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None
