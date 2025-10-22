"""
Abstract storage backend interface for Hei-DataHub.

Supports multiple storage backends (filesystem, WebDAV, etc.)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class FileEntry:
    """Represents a file or directory entry in storage."""
    name: str
    path: str  # Full path relative to storage root
    is_dir: bool
    size: Optional[int] = None  # Size in bytes (None for directories)
    modified: Optional[datetime] = None  # Last modified timestamp
    content_type: Optional[str] = None  # MIME type (optional)

    def __str__(self) -> str:
        """Human-readable representation."""
        type_icon = "📁" if self.is_dir else "📄"
        size_str = self._format_size() if self.size else ""
        return f"{type_icon} {self.name} {size_str}"

    def _format_size(self) -> str:
        """Format file size in human-readable format."""
        if self.size is None:
            return ""

        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(self.size)
        unit_idx = 0

        while size >= 1024 and unit_idx < len(units) - 1:
            size /= 1024
            unit_idx += 1

        if unit_idx == 0:
            return f"{int(size)} {units[unit_idx]}"
        return f"{size:.1f} {units[unit_idx]}"


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def listdir(self, path: str = "") -> List[FileEntry]:
        """
        List contents of a directory.

        Args:
            path: Path relative to storage root (empty string = root)

        Returns:
            List of FileEntry objects sorted (directories first, then files)

        Raises:
            StorageError: If operation fails
        """
        pass

    @abstractmethod
    def download(self, remote_path: str, local_path: Path) -> None:
        """
        Download a file from storage to local filesystem.

        Args:
            remote_path: Path in remote storage
            local_path: Destination path on local filesystem

        Raises:
            StorageError: If download fails
        """
        pass

    @abstractmethod
    def upload(self, local_path: Path, remote_path: str) -> None:
        """
        Upload a file from local filesystem to storage.

        Args:
            local_path: Source path on local filesystem
            remote_path: Destination path in remote storage

        Raises:
            StorageError: If upload fails
        """
        pass

    @abstractmethod
    def mkdir(self, remote_path: str) -> None:
        """
        Create a directory in storage (idempotent).

        Args:
            remote_path: Path of directory to create

        Raises:
            StorageError: If operation fails
        """
        pass

    @abstractmethod
    def exists(self, remote_path: str) -> bool:
        """
        Check if a path exists in storage.

        Args:
            remote_path: Path to check

        Returns:
            True if path exists, False otherwise
        """
        pass

    @abstractmethod
    def get_info(self, remote_path: str) -> Optional[FileEntry]:
        """
        Get information about a file or directory.

        Args:
            remote_path: Path to query

        Returns:
            FileEntry object or None if not found
        """
        pass


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class StorageAuthError(StorageError):
    """Authentication failed (401/403)."""
    pass


class StorageNotFoundError(StorageError):
    """Resource not found (404)."""
    pass


class StorageConnectionError(StorageError):
    """Connection/network error."""
    pass
