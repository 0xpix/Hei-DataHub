"""
Outbox/queue system for handling failed PR submissions.
Allows retry when back online.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

from mini_datahub.infra.paths import PROJECT_ROOT


OUTBOX_DIR = PROJECT_ROOT / ".outbox"


class TaskStatus(str, Enum):
    """Status of an outbox task."""
    PENDING = "pending"
    RETRYING = "retrying"
    FAILED = "failed"
    COMPLETED = "completed"


class OutboxTask:
    """Represents a queued PR creation task."""

    def __init__(
        self,
        task_id: str,
        dataset_id: str,
        metadata: Dict[str, Any],
        branch_name: str,
        commit_message: str,
        status: TaskStatus = TaskStatus.PENDING,
        created_at: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
    ):
        self.task_id = task_id
        self.dataset_id = dataset_id
        self.metadata = metadata
        self.branch_name = branch_name
        self.commit_message = commit_message
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.error_message = error_message
        self.retry_count = retry_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "dataset_id": self.dataset_id,
            "metadata": self.metadata,
            "branch_name": self.branch_name,
            "commit_message": self.commit_message,
            "status": self.status,
            "created_at": self.created_at,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OutboxTask":
        """Create task from dictionary."""
        return cls(
            task_id=data["task_id"],
            dataset_id=data["dataset_id"],
            metadata=data["metadata"],
            branch_name=data["branch_name"],
            commit_message=data["commit_message"],
            status=TaskStatus(data.get("status", TaskStatus.PENDING)),
            created_at=data.get("created_at"),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
        )


class Outbox:
    """Manage outbox tasks for PR creation."""

    def __init__(self):
        """Initialize outbox."""
        OUTBOX_DIR.mkdir(exist_ok=True)

    def _get_task_path(self, task_id: str) -> Path:
        """Get path to task file."""
        return OUTBOX_DIR / f"{task_id}.json"

    def add_task(
        self,
        dataset_id: str,
        metadata: Dict[str, Any],
        branch_name: str,
        commit_message: str,
        error_message: Optional[str] = None,
    ) -> OutboxTask:
        """
        Add a new task to the outbox.

        Args:
            dataset_id: Dataset ID
            metadata: Dataset metadata
            branch_name: Git branch name
            commit_message: Git commit message
            error_message: Optional error message

        Returns:
            Created OutboxTask
        """
        task_id = f"{dataset_id}-{int(time.time())}"
        task = OutboxTask(
            task_id=task_id,
            dataset_id=dataset_id,
            metadata=metadata,
            branch_name=branch_name,
            commit_message=commit_message,
            error_message=error_message,
        )

        # Save to file
        task_path = self._get_task_path(task_id)
        with open(task_path, "w") as f:
            json.dump(task.to_dict(), f, indent=2)

        return task

    def get_task(self, task_id: str) -> Optional[OutboxTask]:
        """Get a task by ID."""
        task_path = self._get_task_path(task_id)
        if not task_path.exists():
            return None

        with open(task_path, "r") as f:
            data = json.load(f)

        return OutboxTask.from_dict(data)

    def update_task(self, task: OutboxTask) -> None:
        """Update a task."""
        task_path = self._get_task_path(task.task_id)
        with open(task_path, "w") as f:
            json.dump(task.to_dict(), f, indent=2)

    def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        task_path = self._get_task_path(task_id)
        if task_path.exists():
            task_path.unlink()

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[OutboxTask]:
        """
        List all tasks.

        Args:
            status: Optional status filter

        Returns:
            List of OutboxTask objects
        """
        tasks = []

        if not OUTBOX_DIR.exists():
            return tasks

        for task_file in OUTBOX_DIR.glob("*.json"):
            try:
                with open(task_file, "r") as f:
                    data = json.load(f)

                task = OutboxTask.from_dict(data)

                if status is None or task.status == status:
                    tasks.append(task)
            except Exception:
                continue

        # Sort by created_at
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def get_pending_tasks(self) -> List[OutboxTask]:
        """Get all pending tasks."""
        return self.list_tasks(status=TaskStatus.PENDING)

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            self.update_task(task)

    def mark_failed(self, task_id: str, error_message: str) -> None:
        """Mark a task as failed."""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            task.retry_count += 1
            self.update_task(task)

    def mark_retrying(self, task_id: str) -> None:
        """Mark a task as retrying."""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.RETRYING
            self.update_task(task)

    def has_pending_tasks(self) -> bool:
        """Check if there are pending tasks."""
        return len(self.get_pending_tasks()) > 0


# Global outbox instance
_outbox_instance: Optional[Outbox] = None


def get_outbox() -> Outbox:
    """Get the global outbox instance."""
    global _outbox_instance
    if _outbox_instance is None:
        _outbox_instance = Outbox()
    return _outbox_instance
