"""
Shared action mixins for screens.

Provides reusable actions like navigation, URL handling, clipboard, and dataset deletion.
"""
import logging
import webbrowser
from typing import Optional

import pyperclip

logger = logging.getLogger(__name__)


class NavActionsMixin:
    """Mixin for navigation actions."""

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()


class UrlActionsMixin:
    """Mixin for URL opening actions.

    Requires the screen to have a `source_url` property that returns the URL string.
    """

    @property
    def source_url(self) -> Optional[str]:
        """Override this to provide the URL to open."""
        raise NotImplementedError("UrlActionsMixin requires source_url property")

    def action_open_url(self) -> None:
        """Open source URL in browser if it's a URL (o key)."""
        url = self.source_url
        if url and (url.startswith('http://') or url.startswith('https://')):
            try:
                webbrowser.open(url)
                self.app.notify("Opening URL in browser...", timeout=2)
            except Exception as e:
                self.app.notify(f"Failed to open URL: {str(e)}", severity="error", timeout=3)
        else:
            self.app.notify("Source is not a URL", severity="warning", timeout=2)


class ClipboardActionsMixin:
    """Mixin for clipboard copy actions.

    Requires the screen to have a `source_url` property that returns the text to copy.
    """

    @property
    def source_url(self) -> Optional[str]:
        """Override this to provide the text to copy."""
        raise NotImplementedError("ClipboardActionsMixin requires source_url property")

    def action_copy_source(self) -> None:
        """Copy source to clipboard (y key)."""
        source = self.source_url
        if source:
            try:
                pyperclip.copy(source)
                self.app.notify("✓ Source copied to clipboard!", timeout=2)
            except Exception as e:
                self.app.notify(f"Failed to copy: {str(e)}", severity="error", timeout=3)


class DatasetDeleteActionsMixin:
    """Mixin for dataset deletion actions.

    Requires:
    - confirm_dialog_cls: Class to use for confirmation dialog
    - get_dataset_id(): Method that returns the dataset ID
    """

    confirm_dialog_cls = None  # Override with ConfirmDeleteDialog class

    def get_dataset_id(self) -> str:
        """Override this to provide the dataset ID."""
        raise NotImplementedError("DatasetDeleteActionsMixin requires get_dataset_id() method")

    def action_delete_dataset(self) -> None:
        """Delete dataset (d key) - shows confirmation dialog."""
        if not self.confirm_dialog_cls:
            raise NotImplementedError("DatasetDeleteActionsMixin requires confirm_dialog_cls to be set")

        self.app.push_screen(
            self.confirm_dialog_cls(self.get_dataset_id()),
            self._handle_delete_confirmation
        )

    def _handle_delete_confirmation(self, confirmed: bool) -> None:
        """Handle delete confirmation dialog response."""
        if confirmed:
            # Import here to avoid circular dependency
            from textual import work
            self.delete_from_cloud()

    @work(thread=True)
    def delete_from_cloud(self) -> None:
        """Delete dataset from cloud storage and local index.

        Override this method to customize deletion behavior.
        """
        raise NotImplementedError("DatasetDeleteActionsMixin requires delete_from_cloud() method")


def bindings_from(*mixins, extra=None):
    """
    Compose keybindings from multiple mixins.

    Args:
        *mixins: Mixin classes to extract bindings from
        extra: Additional bindings list to append

    Returns:
        Combined list of Binding objects
    """
    from textual.binding import Binding

    bindings = []
    for mixin in mixins:
        if hasattr(mixin, 'BINDINGS'):
            bindings.extend(mixin.BINDINGS)

    if extra:
        bindings.extend(extra)

    return bindings
