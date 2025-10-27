"""
Action mixins for TUI screens.

Provides reusable action implementations:
- NavActionsMixin: Back navigation
- UrlActionsMixin: Open URLs in browser
- ClipboardActionsMixin: Copy to clipboard

Usage:
    # In a screen class, inherit mixins:
    class MyScreen(NavActionsMixin, UrlActionsMixin, Screen):
        ...
"""
import logging
import webbrowser
from typing import Optional

import pyperclip

# Re-export ActionContext and ActionRegistry from services
from hei_datahub.services.actions import ActionContext, ActionRegistry, get_action_registry

logger = logging.getLogger(__name__)


# =============================================================================
# ACTION MIXINS - Reusable action implementations for screens
# =============================================================================

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


# =============================================================================
# UTILITIES
# =============================================================================

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
