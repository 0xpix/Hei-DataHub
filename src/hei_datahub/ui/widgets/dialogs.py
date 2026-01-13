"""
Dialog screens for confirmations.

Moved from hei_datahub.ui.views.home
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class ConfirmCancelDialog(ModalScreen[bool]):
    """Modal dialog to confirm canceling edits with unsaved changes."""

    CSS = """
    ConfirmCancelDialog {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }

    .dialog-box {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .dialog-title {
        text-align: center;
        width: 100%;
    }

    .dialog-text {
        text-align: center;
        width: 100%;
        padding: 1;
    }
    """

    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
        ("escape", "cancel", "No"),
    ]

    def __init__(self, dataset_id: str, dirty_count: int):
        super().__init__()
        self.dataset_id = dataset_id
        self.dirty_count = dirty_count

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("[bold yellow]Discard Changes?[/bold yellow]", classes="dialog-title"),
            Static(f"\nYou have {self.dirty_count} unsaved change(s) to [cyan]{self.dataset_id}[/cyan].\n", classes="dialog-text"),
            Static("Press [bold]Y[/bold] to discard changes or [bold]N[/bold] to keep editing.", classes="dialog-text"),
            id="confirm-dialog",
            classes="dialog-box",
        )

    def action_confirm(self) -> None:
        """User confirmed - discard changes."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """User canceled - keep editing."""
        self.dismiss(False)


class ConfirmDeleteDialog(ModalScreen[bool]):
    """Modal dialog to confirm dataset deletion."""

    CSS = """
    ConfirmDeleteDialog {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }

    .dialog-box {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .dialog-title {
        text-align: center;
        width: 100%;
    }

    .dialog-text {
        text-align: center;
        width: 100%;
        padding: 1;
    }
    """

    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
        ("escape", "cancel", "No"),
    ]

    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("[bold red]Delete Dataset?[/bold red]", classes="dialog-title"),
            Static(f"\nAre you sure you want to delete [cyan]{self.dataset_id}[/cyan]?\n", classes="dialog-text"),
            Static("[bold red]This action cannot be undone![/bold red]", classes="dialog-text"),
            Static("\nPress [bold]Y[/bold] to delete or [bold]N[/bold] to cancel.", classes="dialog-text"),
            id="confirm-dialog",
            classes="dialog-box",
        )

    def action_confirm(self) -> None:
        """User confirmed - delete dataset."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """User canceled - don't delete."""
        self.dismiss(False)


class ConfirmExitDialog(ModalScreen[bool]):
    """Modal dialog to confirm exiting the application."""

    CSS = """
    ConfirmExitDialog {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }

    .dialog-box {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .dialog-title {
        text-align: center;
        width: 100%;
    }

    .dialog-text {
        text-align: center;
        width: 100%;
        padding: 1;
    }
    """

    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
        ("escape", "cancel", "No"),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("[bold yellow]Exit Application?[/bold yellow]", classes="dialog-title"),
            Static("\nAre you sure you want to exit Hei-DataHub?\n", classes="dialog-text"),
            Static("Press [bold]Y[/bold] to exit or [bold]N[/bold] to cancel.", classes="dialog-text"),
            id="confirm-dialog",
            classes="dialog-box",
        )

    def action_confirm(self) -> None:
        """User confirmed - exit app."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """User canceled - stay in app."""
        self.dismiss(False)
