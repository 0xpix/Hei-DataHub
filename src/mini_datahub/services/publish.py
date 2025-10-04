"""
Main workflow orchestrator for Save → PR automation.
"""
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from mini_datahub.app.settings import get_github_config
from mini_datahub.infra.git import (
    GitOperations,
    GitOperationError,
    generate_branch_name,
    format_commit_message,
)
from mini_datahub.infra.github_api import (
    GitHubIntegration,
    GitHubAPIError,
    format_pr_body,
)
from mini_datahub.services.outbox import get_outbox
from mini_datahub.infra.store import write_dataset


class PRWorkflowError(Exception):
    """Exception raised for PR workflow errors."""
    pass


class PRWorkflow:
    """Orchestrate the complete Save → PR workflow."""

    def __init__(self):
        """Initialize workflow components."""
        self.config = get_github_config()
        self.outbox = get_outbox()

    def execute(
        self,
        metadata: Dict[str, Any],
        dataset_id: str,
    ) -> Tuple[bool, str, Optional[str], Optional[int]]:
        """
        Execute the complete Save → PR workflow.

        Args:
            metadata: Dataset metadata dictionary
            dataset_id: Dataset ID

        Returns:
            Tuple of (success, message, pr_url, pr_number)
        """
        # Check if GitHub is configured
        if not self.config.is_configured():
            return self._save_local_only(metadata, dataset_id)

        # Get catalog repo path
        catalog_path = self.config.catalog_repo_path
        if not catalog_path:
            return self._save_local_only(metadata, dataset_id)

        catalog_path = Path(catalog_path).expanduser().resolve()
        if not catalog_path.exists():
            return (
                False,
                f"Catalog repository path does not exist: {catalog_path}",
                None,
                None,
            )

        # Initialize components
        git_ops = GitOperations(catalog_path)
        github = GitHubIntegration(self.config)

        # Generate branch and commit info
        dataset_name = metadata.get("dataset_name", dataset_id)
        branch_name = generate_branch_name(dataset_id)
        commit_message = format_commit_message(dataset_id, dataset_name)

        # Track if we stashed changes (for restoration later)
        stashed = False

        try:
            # Pre-flight checks
            if not git_ops.is_git_repo():
                return (
                    False,
                    f"Catalog path is not a git repository: {catalog_path}",
                    None,
                    None,
                )

            # Auto-stash uncommitted changes if present
            if not git_ops.is_working_tree_clean():
                try:
                    stashed = git_ops.stash_push(message=f"Auto-stash before PR for {dataset_id}")
                    if stashed:
                        # Log that we stashed (visible in TUI notifications if needed)
                        pass
                except Exception as e:
                    return (
                        False,
                        f"Failed to stash uncommitted changes: {str(e)}. Please manually commit or stash.",
                        None,
                        None,
                    )

            # Check ID uniqueness remotely
            is_unique, uniqueness_msg = github.check_id_uniqueness(dataset_id)
            if not is_unique:
                return False, uniqueness_msg, None, None

            # Step 1: Write metadata to catalog repo
            self._write_metadata_to_catalog(catalog_path, dataset_id, metadata)

            # Step 2: Git operations
            self._perform_git_operations(
                git_ops,
                branch_name,
                dataset_id,
                commit_message,
            )

            # Step 3: Determine push strategy (central vs fork)
            has_push = github.has_push_access()

            if has_push:
                # Push directly to central repo
                git_ops.push(remote="origin", branch=branch_name)
                head = branch_name
            else:
                # Fork workflow
                success, fork_name, msg = github.get_or_create_fork()
                if not success:
                    raise PRWorkflowError(f"Failed to create fork: {msg}")

                # Ensure fork remote exists
                fork_url = f"https://{self.config.host}/{fork_name}.git"
                git_ops.ensure_remote("fork", fork_url)

                # Push to fork
                git_ops.push(remote="fork", branch=branch_name)
                head = f"{self.config.username}:{branch_name}"

            # Step 4: Create PR
            pr_title = f"Add dataset: {dataset_name} ({dataset_id})"
            pr_body = format_pr_body(metadata)

            success, pr_number, pr_url, msg = github.create_pull_request(
                title=pr_title,
                body=pr_body,
                head=head,
                base=self.config.default_branch,
            )

            if not success:
                # Save to outbox for retry
                self.outbox.add_task(
                    dataset_id=dataset_id,
                    metadata=metadata,
                    branch_name=branch_name,
                    commit_message=commit_message,
                    error_message=msg,
                )
                return False, f"PR creation failed (saved to outbox): {msg}", None, None

            # Step 5: Add labels and reviewers
            if pr_number:
                if self.config.pr_labels:
                    github.add_labels_to_pr(pr_number, self.config.pr_labels)

                if self.config.auto_assign_reviewers:
                    github.request_reviewers(pr_number, self.config.auto_assign_reviewers)

            return True, "PR created successfully!", pr_url, pr_number

        except GitOperationError as e:
            # Save to outbox
            self.outbox.add_task(
                dataset_id=dataset_id,
                metadata=metadata,
                branch_name=branch_name,
                commit_message=commit_message,
                error_message=str(e),
            )
            return False, f"Git operation failed (saved to outbox): {str(e)}", None, None

        except Exception as e:
            # Save to outbox
            self.outbox.add_task(
                dataset_id=dataset_id,
                metadata=metadata,
                branch_name=branch_name,
                commit_message=commit_message,
                error_message=str(e),
            )
            return False, f"Workflow failed (saved to outbox): {str(e)}", None, None

        finally:
            # Always restore stashed changes if we stashed them
            if stashed:
                try:
                    git_ops.stash_pop()
                except Exception as e:
                    # If stash pop fails, log it but don't fail the workflow
                    # The stash is still in the stash list and can be manually recovered
                    pass

    def _save_local_only(
        self,
        metadata: Dict[str, Any],
        dataset_id: str,
    ) -> Tuple[bool, str, Optional[str], Optional[int]]:
        """Save dataset locally without PR workflow."""
        # This is handled by the caller, we just return a signal
        return True, "github_not_configured", None, None

    def _write_metadata_to_catalog(
        self,
        catalog_path: Path,
        dataset_id: str,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Write metadata to catalog repository.

        Args:
            catalog_path: Path to catalog repository
            dataset_id: Dataset ID
            metadata: Dataset metadata
        """
        dataset_dir = catalog_path / "data" / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)

        metadata_path = dataset_dir / "metadata.yaml"

        # Use storage module to write YAML
        import yaml
        from datetime import date

        metadata_copy = metadata.copy()
        if isinstance(metadata_copy.get("date_created"), date):
            metadata_copy["date_created"] = metadata_copy["date_created"].isoformat()
        if isinstance(metadata_copy.get("last_updated"), date):
            metadata_copy["last_updated"] = metadata_copy["last_updated"].isoformat()

        with open(metadata_path, "w") as f:
            yaml.safe_dump(metadata_copy, f, default_flow_style=False, sort_keys=False)

    def _perform_git_operations(
        self,
        git_ops: GitOperations,
        branch_name: str,
        dataset_id: str,
        commit_message: str,
    ) -> None:
        """
        Perform git operations: branch, stage, commit.

        Args:
            git_ops: GitOperations instance
            branch_name: Branch name
            dataset_id: Dataset ID
            commit_message: Commit message
        """
        # Fetch latest changes
        try:
            git_ops.fetch()
        except Exception as e:
            raise PRWorkflowError(f"Failed to fetch from remote: {str(e)}")

        # Checkout and update base branch
        try:
            git_ops.checkout_branch(self.config.default_branch)
            git_ops.fast_forward(self.config.default_branch)
        except Exception as e:
            raise PRWorkflowError(
                f"Failed to update {self.config.default_branch} branch. "
                f"Make sure your catalog repository is in a clean state: {str(e)}"
            )

        # Create and checkout feature branch
        try:
            git_ops.checkout_branch(branch_name, create=True)
        except Exception as e:
            raise PRWorkflowError(f"Failed to create branch '{branch_name}': {str(e)}")

        # Stage the entire dataset directory (includes metadata.yaml and any other files)
        patterns = [
            f"data/{dataset_id}/",
        ]
        git_ops.stage_files(patterns)

        # Check if there are changes to commit
        if git_ops.has_changes(f"data/{dataset_id}"):
            git_ops.commit(commit_message)
        else:
            raise GitOperationError("No changes to commit")

    def retry_task(self, task_id: str) -> Tuple[bool, str, Optional[str], Optional[int]]:
        """
        Retry a failed outbox task.

        Args:
            task_id: Task ID

        Returns:
            Tuple of (success, message, pr_url, pr_number)
        """
        task = self.outbox.get_task(task_id)
        if not task:
            return False, "Task not found", None, None

        self.outbox.mark_retrying(task_id)

        success, message, pr_url, pr_number = self.execute(
            metadata=task.metadata,
            dataset_id=task.dataset_id,
        )

        if success and pr_url:
            self.outbox.mark_completed(task_id)
        else:
            self.outbox.mark_failed(task_id, message)

        return success, message, pr_url, pr_number
