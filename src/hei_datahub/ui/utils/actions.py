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
import os
import subprocess
import sys
from typing import Optional

import pyperclip

# Re-export ActionContext and ActionRegistry from services

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

    def _open_url_subprocess(self, url: str) -> None:
        """
        Open a URL using subprocess to avoid readline conflicts.

        Uses platform-specific commands instead of webbrowser module
        which can cause 'undefined symbol: rl_print_keybinding' errors
        on some Linux installations.

        For packaged binaries (PyInstaller), we need to:
        1. Use shell=True to get proper PATH resolution
        2. Ensure proper environment inheritance
        3. Detach from the parent process completely
        """
        try:
            if sys.platform == "darwin":
                subprocess.Popen(
                    ["open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            elif sys.platform == "win32":
                subprocess.Popen(
                    ["start", url],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Linux - use shell=True for proper PATH resolution in packaged binaries
                # Build a clean environment with essential variables
                clean_env = {
                    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
                    "HOME": os.environ.get("HOME", ""),
                    "DISPLAY": os.environ.get("DISPLAY", ":0"),
                    "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY", ""),
                    "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR", ""),
                    "DBUS_SESSION_BUS_ADDRESS": os.environ.get("DBUS_SESSION_BUS_ADDRESS", ""),
                    "XDG_CURRENT_DESKTOP": os.environ.get("XDG_CURRENT_DESKTOP", ""),
                    "DESKTOP_SESSION": os.environ.get("DESKTOP_SESSION", ""),
                }
                # Remove empty values
                clean_env = {k: v for k, v in clean_env.items() if v}

                # Use shell=True with xdg-open for proper resolution
                subprocess.Popen(
                    f'xdg-open "{url}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    env=clean_env,
                    cwd=os.environ.get("HOME", "/tmp")
                )
                # Don't wait - xdg-open spawns a browser and exits

        except Exception as e:
            raise RuntimeError(f"Could not open browser: {e}")

    def action_open_url(self) -> None:
        """Open source URL in browser if it's a URL (o key)."""
        url = self.source_url
        if url and (url.startswith('http://') or url.startswith('https://')):
            try:
                self._open_url_subprocess(url)
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

    bindings = []
    for mixin in mixins:
        if hasattr(mixin, 'BINDINGS'):
            bindings.extend(mixin.BINDINGS)

    if extra:
        bindings.extend(extra)

    return bindings
