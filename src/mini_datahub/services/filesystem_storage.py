"""
Filesystem storage backend for local directory access.

Provides backward compatibility and fallback for mounted filesystems.
"""
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from mini_datahub.services.storage_backend import (
    FileEntry,
    StorageBackend,
    StorageError,
    StorageNotFoundError,
)

logger = logging.getLogger(__name__)


class FilesystemStorage(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, root_dir: str):
        """
        Initialize filesystem storage.

        Args:
            root_dir: Root directory path (e.g., /home/user/data or mounted folder)
        """
        self.root_path = Path(root_dir).expanduser().resolve()

        if not self.root_path.exists():
            logger.warning(f"Storage root does not exist: {self.root_path}")
            try:
                self.root_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created storage root: {self.root_path}")
            except Exception as e:
                raise StorageError(f"Failed to create storage root: {e}")

        logger.info(f"Filesystem storage initialized: {self.root_path}")

    def _get_full_path(self, path: str) -> Path:
        """Get absolute path for a given relative path."""
        # Normalize path
        path = path.strip("/")
        full_path = self.root_path / path if path else self.root_path

        # Security: ensure path is within root
        try:
            resolved = full_path.resolve()
            if not resolved.is_relative_to(self.root_path):
                raise StorageError(f"Path escape attempt: {path}")
            return resolved
        except ValueError:
            raise StorageError(f"Invalid path: {path}")

    def listdir(self, path: str = "") -> List[FileEntry]:
        """
        List directory contents.

        Args:
            path: Path relative to root

        Returns:
            Sorted list of FileEntry objects
        """
        full_path = self._get_full_path(path)

        if not full_path.exists():
            raise StorageNotFoundError(f"Path not found: {path}")

        if not full_path.is_dir():
            raise StorageError(f"Not a directory: {path}")

        entries = []
        try:
            for item in full_path.iterdir():
                stat = item.stat()

                # Build relative path from root
                rel_path = str(item.relative_to(self.root_path))

                entry = FileEntry(
                    name=item.name,
                    path=rel_path,
                    is_dir=item.is_dir(),
                    size=stat.st_size if item.is_file() else None,
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    content_type=self._guess_content_type(item) if item.is_file() else None,
                )
                entries.append(entry)

            # Sort: directories first, then alphabetically
            entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
            return entries

        except PermissionError:
            raise StorageError(f"Permission denied: {path}")
        except Exception as e:
            raise StorageError(f"Failed to list directory: {e}")

    def _guess_content_type(self, file_path: Path) -> Optional[str]:
        """Guess MIME type from file extension."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type

    def download(self, remote_path: str, local_path: Path) -> None:
        """
        Copy file from storage to local path.

        Args:
            remote_path: Path in storage
            local_path: Destination local path
        """
        full_path = self._get_full_path(remote_path)

        if not full_path.exists():
            raise StorageNotFoundError(f"File not found: {remote_path}")

        if not full_path.is_file():
            raise StorageError(f"Not a file: {remote_path}")

        try:
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(full_path, local_path)
            logger.info(f"Downloaded {remote_path} to {local_path}")

        except PermissionError:
            raise StorageError(f"Permission denied: {remote_path}")
        except Exception as e:
            raise StorageError(f"Download failed: {e}")

    def upload(self, local_path: Path, remote_path: str) -> None:
        """
        Copy file from local path to storage.

        Args:
            local_path: Source local path
            remote_path: Destination path in storage
        """
        if not local_path.exists():
            raise StorageError(f"Local file not found: {local_path}")

        full_path = self._get_full_path(remote_path)

        try:
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(local_path, full_path)
            logger.info(f"Uploaded {local_path} to {remote_path}")

        except PermissionError:
            raise StorageError(f"Permission denied: {remote_path}")
        except Exception as e:
            raise StorageError(f"Upload failed: {e}")

    def mkdir(self, remote_path: str) -> None:
        """
        Create directory (idempotent).

        Args:
            remote_path: Directory path to create
        """
        full_path = self._get_full_path(remote_path)

        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {remote_path}")
        except PermissionError:
            raise StorageError(f"Permission denied: {remote_path}")
        except Exception as e:
            raise StorageError(f"Failed to create directory: {e}")

    def exists(self, remote_path: str) -> bool:
        """
        Check if path exists.

        Args:
            remote_path: Path to check

        Returns:
            True if exists
        """
        try:
            full_path = self._get_full_path(remote_path)
            return full_path.exists()
        except Exception:
            return False

    def get_info(self, remote_path: str) -> Optional[FileEntry]:
        """
        Get file/directory info.

        Args:
            remote_path: Path to query

        Returns:
            FileEntry or None
        """
        try:
            full_path = self._get_full_path(remote_path)

            if not full_path.exists():
                return None

            stat = full_path.stat()

            return FileEntry(
                name=full_path.name,
                path=remote_path,
                is_dir=full_path.is_dir(),
                size=stat.st_size if full_path.is_file() else None,
                modified=datetime.fromtimestamp(stat.st_mtime),
                content_type=self._guess_content_type(full_path) if full_path.is_file() else None,
            )
        except Exception:
            return None
