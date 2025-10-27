"""System diagnostic and health check commands.

This package exposes a small, stable public API of command handlers.

Rules:
- No heavy imports or side-effects at import time.
- Re-export a minimal, explicit public API.

Public API:
- handle_doctor(args) -> int
- handle_tui(args) -> int
- handle_paths(args) -> int
"""

from .doctor import handle_doctor
from .tui import handle_tui
from .paths import handle_paths

__all__ = ["handle_doctor", "handle_tui", "handle_paths"]
