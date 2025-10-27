"""Desktop integration commands.

This package exposes a small, stable public API for desktop integration.

Rules:
- No heavy imports or side-effects at import time.
- Re-export a minimal, explicit public API.
- All handlers return int exit codes.

Public API:
- handle_setup_desktop(args) -> int
- handle_uninstall(args) -> int
"""

from .setup import handle_setup_desktop
from .uninstall import handle_uninstall

__all__ = ['handle_setup_desktop', 'handle_uninstall']
