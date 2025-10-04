"""
Outbox screen for viewing and retrying failed PR tasks.
"""
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
)

from mini_datahub.services.outbox import get_outbox, TaskStatus
from mini_datahub.services.publish import PRWorkflow


class OutboxScreen(Screen):
    """Screen to view and retry failed PR tasks."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
        ("r", "retry", "Retry Selected"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("📮 Outbox  |  [italic]Failed PR submissions[/italic]", classes="title"),
            Label("Tasks pending retry", id="outbox-label"),
            DataTable(id="outbox-table", cursor_type="row"),
            Horizontal(
                Button("Retry Selected", id="retry-btn", variant="primary"),
                Button("Retry All Pending", id="retry-all-btn", variant="default"),
                Button("Clear Completed", id="clear-btn", variant="warning"),
                Button("Back", id="back-btn", variant="default"),
            ),
            Label("", id="outbox-status"),
            id="outbox-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load outbox tasks."""
        table = self.query_one("#outbox-table", DataTable)
        table.add_columns("Dataset ID", "Status", "Created", "Error")
        table.cursor_type = "row"

        self.refresh_tasks()

    def refresh_tasks(self) -> None:
        """Refresh task list."""
        table = self.query_one("#outbox-table", DataTable)
        table.clear()

        outbox = get_outbox()
        tasks = outbox.list_tasks()

        label = self.query_one("#outbox-label", Label)
        label.update(f"Tasks: {len(tasks)} total")

        for task in tasks:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RETRYING: "🔄",
                TaskStatus.FAILED: "❌",
                TaskStatus.COMPLETED: "✅",
            }.get(task.status, "?")

            error_msg = task.error_message or ""
            error_display = error_msg[:40] + "..." if len(error_msg) > 40 else error_msg

            table.add_row(
                task.dataset_id,
                f"{status_icon} {task.status}",
                task.created_at[:19],  # Trim to datetime without microseconds
                error_display,
                key=task.task_id,
            )

    @on(Button.Pressed, "#retry-btn")
    def on_retry_button(self) -> None:
        """Retry selected task."""
        self.action_retry()

    @on(Button.Pressed, "#retry-all-btn")
    def on_retry_all_button(self) -> None:
        """Retry all pending tasks."""
        self.retry_all_pending()

    @on(Button.Pressed, "#clear-btn")
    def on_clear_button(self) -> None:
        """Clear completed tasks."""
        self.clear_completed()

    @on(Button.Pressed, "#back-btn")
    def on_back_button(self) -> None:
        """Go back."""
        self.action_back()

    def action_retry(self) -> None:
        """Retry selected task."""
        table = self.query_one("#outbox-table", DataTable)

        if not table.row_count:
            self.app.notify("No tasks in outbox", severity="warning", timeout=3)
            return

        try:
            row_key = table.cursor_row
            if row_key is None:
                self.app.notify("No task selected", severity="warning", timeout=3)
                return

            task_id = str(row_key)
            self.retry_task(task_id)

        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error", timeout=3)

    @work(exclusive=True)
    async def retry_task(self, task_id: str) -> None:
        """Retry a specific task."""
        status_label = self.query_one("#outbox-status", Label)
        status_label.update("Retrying...")

        workflow = PRWorkflow()
        success, message, pr_url, pr_number = workflow.retry_task(task_id)

        if success and pr_url:
            status_label.update(f"[green]✓ PR created: #{pr_number}[/green]")
            self.app.notify(f"PR #{pr_number} created successfully!", timeout=5)
        else:
            status_label.update(f"[red]✗ {message}[/red]")
            self.app.notify(f"Retry failed: {message}", severity="error", timeout=5)

        # Refresh task list
        self.refresh_tasks()

    def retry_all_pending(self) -> None:
        """Retry all pending tasks."""
        outbox = get_outbox()
        pending = outbox.get_pending_tasks()

        if not pending:
            self.app.notify("No pending tasks", severity="warning", timeout=3)
            return

        self.app.notify(f"Retrying {len(pending)} task(s)...", timeout=3)

        for task in pending:
            self.retry_task(task.task_id)

    def clear_completed(self) -> None:
        """Clear completed tasks."""
        outbox = get_outbox()
        completed = outbox.list_tasks(status=TaskStatus.COMPLETED)

        if not completed:
            self.app.notify("No completed tasks", severity="warning", timeout=3)
            return

        for task in completed:
            outbox.delete_task(task.task_id)

        self.app.notify(f"Cleared {len(completed)} completed task(s)", timeout=3)
        self.refresh_tasks()

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()
