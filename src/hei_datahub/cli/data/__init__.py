"""Data management commands.

This package exposes a small, stable public API for data operations.

Rules:
- No heavy imports or side-effects at import time.
- Re-export a minimal, explicit public API.
- All handlers return int exit codes.

Public API:
- handle_reindex(args) -> int
"""

from .reindex import handle_reindex

__all__ = ['handle_reindex']
