"""
Async utilities for debouncing and cancellation.
"""
import asyncio
from typing import Any, Callable, Optional, TypeVar
from functools import wraps

T = TypeVar('T')


class Debouncer:
    """Debounce async function calls with cancellation support."""

    def __init__(self, wait_ms: int = 200):
        """
        Initialize debouncer.

        Args:
            wait_ms: Milliseconds to wait before executing
        """
        self.wait_ms = wait_ms
        self._task: Optional[asyncio.Task] = None

    async def __call__(self, coro):
        """
        Execute debounced coroutine.
        Cancels previous pending execution.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine
        """
        # Cancel previous task if still running
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Wait for debounce period
        await asyncio.sleep(self.wait_ms / 1000)

        # Execute the coroutine
        return await coro

    def cancel(self):
        """Cancel any pending execution."""
        if self._task and not self._task.done():
            self._task.cancel()


def debounce(wait_ms: int = 200):
    """
    Decorator to debounce async function calls.

    Args:
        wait_ms: Milliseconds to wait before executing

    Example:
        @debounce(200)
        async def search(query: str):
            return await perform_search(query)
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        _task: Optional[asyncio.Task] = None

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal _task

            # Cancel previous task
            if _task and not _task.done():
                _task.cancel()
                try:
                    await _task
                except asyncio.CancelledError:
                    pass

            # Create new task
            async def run():
                await asyncio.sleep(wait_ms / 1000)
                return await func(*args, **kwargs)

            _task = asyncio.create_task(run())
            return await _task

        return wrapper
    return decorator


class CancellableTask:
    """Wrapper for cancellable async tasks."""

    def __init__(self):
        """Initialize cancellable task."""
        self._task: Optional[asyncio.Task] = None

    async def run(self, coro):
        """
        Run a coroutine, cancelling any previous execution.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine, or None if cancelled
        """
        # Cancel previous task
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Run new task
        self._task = asyncio.create_task(coro)
        try:
            return await self._task
        except asyncio.CancelledError:
            return None

    def cancel(self):
        """Cancel the current task if running."""
        if self._task and not self._task.done():
            self._task.cancel()

    @property
    def is_running(self) -> bool:
        """Check if a task is currently running."""
        return self._task is not None and not self._task.done()
