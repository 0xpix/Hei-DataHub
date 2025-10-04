"""
Additional TUI screens for Settings and Outbox management.
"""
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from mini_datahub.config import get_github_config, reload_config
from mini_datahub.github_integration import GitHubIntegration
from mini_datahub.outbox import get_outbox, TaskStatus
from mini_datahub.pr_workflow import PRWorkflow


class SettingsScreen(Screen):
    """Settings screen for GitHub configuration."""

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("q", "cancel", "Back"),
        Binding("ctrl+s", "save", "Save", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("⚙️ GitHub Settings  |  [italic]Configure GitHub integration for PR automation[/italic]", classes="title"),
            Container(
                Label("GitHub Host:"),
                Input(placeholder="github.com", id="input-host"),
                Label("Owner/Organization:"),
                Input(placeholder="e.g., your-org", id="input-owner"),
                Label("Repository Name:"),
                Input(placeholder="e.g., mini-datahub-catalog", id="input-repo"),
                Label("Default Branch:"),
                Input(placeholder="main", id="input-branch"),
                Label("GitHub Username:"),
                Input(placeholder="your-username", id="input-username"),
                Label("Personal Access Token (PAT):"),
                Input(placeholder="ghp_xxxxxxxxxxxx", password=True, id="input-token"),
                Label("Catalog Repository Path (local):"),
                Input(placeholder="/path/to/catalog/repo", id="input-catalog-path"),
                Label("Auto-assign Reviewers (comma-separated):"),
                Input(placeholder="reviewer1, reviewer2", id="input-reviewers"),
                Label("PR Labels (comma-separated):"),
                Input(placeholder="dataset:add, needs-review", id="input-labels"),
                Horizontal(
                    Button("Test Connection", id="test-btn", variant="default"),
                    Button("Save Settings", id="save-btn", variant="primary"),
                    Button("Remove Token", id="remove-token-btn", variant="warning"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                ),
                Label("", id="status-message"),
                id="settings-container",
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load current settings."""
        config = get_github_config()

        self.query_one("#input-host", Input).value = config.host
        self.query_one("#input-owner", Input).value = config.owner
        self.query_one("#input-repo", Input).value = config.repo
        self.query_one("#input-branch", Input).value = config.default_branch
        self.query_one("#input-username", Input).value = config.username

        if config.get_token():
            self.query_one("#input-token", Input).value = "••••••••"  # Masked

        if config.catalog_repo_path:
            self.query_one("#input-catalog-path", Input).value = config.catalog_repo_path

        if config.auto_assign_reviewers:
            self.query_one("#input-reviewers", Input).value = ", ".join(config.auto_assign_reviewers)

        if config.pr_labels:
            self.query_one("#input-labels", Input).value = ", ".join(config.pr_labels)

        self.query_one("#input-host", Input).focus()

    @on(Button.Pressed, "#test-btn")
    def on_test_button(self) -> None:
        """Test GitHub connection."""
        self.test_connection()

    @work(exclusive=True)
    async def test_connection(self) -> None:
        """Test connection to GitHub."""
        status_label = self.query_one("#status-message", Label)
        status_label.update("Testing connection...")

        # Get current form values (creates temporary config for testing)
        config = self._get_form_config()

        if not config.is_configured():
            status_label.update("[red]✗ Please fill in all required fields[/red]")
            return

        # Ensure token is available for test
        if not config.get_token():
            status_label.update("[red]✗ GitHub token is required[/red]")
            self.app.notify("Please enter a GitHub token", severity="error", timeout=5)
            return

        try:
            github = GitHubIntegration(config)
            success, message = github.test_connection()

            if success:
                status_label.update(f"[green]✓ {message}[/green]")
                self.app.notify("Connection successful!", timeout=3)
            else:
                status_label.update(f"[red]✗ {message}[/red]")
                self.app.notify(f"Connection failed: {message}", severity="error", timeout=5)
        except Exception as e:
            status_label.update(f"[red]✗ Error: {str(e)}[/red]")
            self.app.notify(f"Test failed: {str(e)}", severity="error", timeout=5)

    @on(Button.Pressed, "#save-btn")
    def on_save_button(self) -> None:
        """Save settings."""
        self.action_save()

    @on(Button.Pressed, "#remove-token-btn")
    def on_remove_token_button(self) -> None:
        """Remove stored token."""
        config = get_github_config()
        config.clear_token()
        config.save_config(save_token=False)

        self.query_one("#input-token", Input).value = ""
        self.query_one("#status-message", Label).update("[yellow]Token removed[/yellow]")
        self.app.notify("Token removed", timeout=3)

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_button(self) -> None:
        """Cancel and go back."""
        self.action_cancel()

    def action_save(self) -> None:
        """Save settings."""
        status_label = self.query_one("#status-message", Label)

        try:
            # Get the global config instance and update it directly
            config = get_github_config()

            # Update from form fields
            config.host = self.query_one("#input-host", Input).value.strip()
            config.owner = self.query_one("#input-owner", Input).value.strip()
            config.repo = self.query_one("#input-repo", Input).value.strip()
            config.default_branch = self.query_one("#input-branch", Input).value.strip() or "main"
            config.username = self.query_one("#input-username", Input).value.strip()

            # Handle token input
            token_input = self.query_one("#input-token", Input).value.strip()
            if token_input and token_input != "••••••••":
                config.set_token(token_input)
            # If token field is masked, keep existing token (already in config)

            # Update catalog path
            catalog_path = self.query_one("#input-catalog-path", Input).value.strip()
            if catalog_path:
                config.catalog_repo_path = catalog_path

            # Update reviewers
            reviewers_str = self.query_one("#input-reviewers", Input).value.strip()
            if reviewers_str:
                config.auto_assign_reviewers = [r.strip() for r in reviewers_str.split(",") if r.strip()]
            else:
                config.auto_assign_reviewers = []

            # Update labels
            labels_str = self.query_one("#input-labels", Input).value.strip()
            if labels_str:
                config.pr_labels = [l.strip() for l in labels_str.split(",") if l.strip()]
            else:
                config.pr_labels = ["dataset:add", "needs-review"]

            # Validate required fields
            if not config.owner or not config.repo or not config.username:
                status_label.update("[red]Owner, Repository, and Username are required[/red]")
                return

            # Save configuration (writes to file and keyring)
            config.save_config(save_token=True)

            # Refresh GitHub connection status in the app
            self.app.refresh_github_status()

            status_label.update("[green]✓ Settings saved![/green]")
            self.app.notify("Settings saved successfully!", timeout=3)

        except Exception as e:
            status_label.update(f"[red]Error saving: {str(e)}[/red]")
            self.app.notify(f"Save failed: {str(e)}", severity="error", timeout=5)

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()

    def _get_form_config(self):
        """Get configuration from form fields."""
        from mini_datahub.config import GitHubConfig

        config = GitHubConfig()

        config.host = self.query_one("#input-host", Input).value.strip()
        config.owner = self.query_one("#input-owner", Input).value.strip()
        config.repo = self.query_one("#input-repo", Input).value.strip()
        config.default_branch = self.query_one("#input-branch", Input).value.strip() or "main"
        config.username = self.query_one("#input-username", Input).value.strip()

        token_input = self.query_one("#input-token", Input).value.strip()
        if token_input and token_input != "••••••••":
            config.set_token(token_input)
        else:
            # Keep existing token
            existing_config = get_github_config()
            if existing_config.get_token():
                config.set_token(existing_config.get_token())

        catalog_path = self.query_one("#input-catalog-path", Input).value.strip()
        if catalog_path:
            config.catalog_repo_path = catalog_path

        reviewers_str = self.query_one("#input-reviewers", Input).value.strip()
        if reviewers_str:
            config.auto_assign_reviewers = [r.strip() for r in reviewers_str.split(",") if r.strip()]

        labels_str = self.query_one("#input-labels", Input).value.strip()
        if labels_str:
            config.pr_labels = [l.strip() for l in labels_str.split(",") if l.strip()]

        return config


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
