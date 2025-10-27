"""Update commands and utilities.

This package exposes a small, stable public API for update commands.

Rules:
- No heavy imports or side-effects at import time.
- Re-export a minimal, explicit public API.
- Handlers return int exit codes (or rely on _call_handler to catch SystemExit).

Public API:
- handle_update(args) -> int
"""

from .commands import handle_update

__all__ = ["handle_update"]
