"""WebDAV authentication commands.

This package exposes a small, stable public API of auth command handlers.

Rules:
- No heavy imports or side-effects at import time.
- Re-export a minimal, explicit public API.
- All handlers return int exit codes.

Public API:
- handle_auth_setup(args) -> int
- handle_auth_status(args) -> int
- handle_auth_doctor(args) -> int
- handle_auth_clear(args) -> int
"""

from .commands import (
    handle_auth_clear,
    handle_auth_doctor,
    handle_auth_setup,
    handle_auth_status,
)

__all__ = [
    "handle_auth_setup",
    "handle_auth_status",
    "handle_auth_doctor",
    "handle_auth_clear",
]
