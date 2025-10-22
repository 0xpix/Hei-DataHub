"""
Storage manager: Factory for creating storage backend instances.

Automatically selects the appropriate backend based on configuration.
"""
import logging
import os
from typing import Optional

from mini_datahub.services.config import get_config
from mini_datahub.services.filesystem_storage import FilesystemStorage
from mini_datahub.services.storage_backend import StorageBackend, StorageError
from mini_datahub.services.webdav_storage import WebDAVStorage

logger = logging.getLogger(__name__)

# Cached storage instance
_storage_instance: Optional[StorageBackend] = None


def get_storage_backend(force_reload: bool = False) -> StorageBackend:
    """
    Get the configured storage backend instance (cached).

    Reads configuration and creates the appropriate backend:
    - WebDAV: Requires base_url, library, username, and token from env
    - Filesystem: Requires data_dir

    Args:
        force_reload: Force recreation of storage backend (default: False)

    Returns:
        StorageBackend instance

    Raises:
        StorageError: If configuration is invalid or backend cannot be created
    """
    global _storage_instance

    if _storage_instance is not None and not force_reload:
        return _storage_instance

    config = get_config()

    # Get storage config
    backend_type = config.get("storage.backend", "filesystem")

    if backend_type == "webdav":
        _storage_instance = _create_webdav_backend(config)
    elif backend_type == "filesystem":
        _storage_instance = _create_filesystem_backend(config)
    else:
        raise StorageError(f"Unknown storage backend: {backend_type}")

    return _storage_instance


def _create_webdav_backend(config) -> WebDAVStorage:
    """Create WebDAV storage backend from config."""
    base_url = config.get("storage.base_url")
    library = config.get("storage.library")
    username = config.get("storage.username")
    password_env = config.get("storage.password_env", "HEIBOX_WEBDAV_TOKEN")

    # Read credentials from environment
    if not username:
        username = os.getenv("HEIBOX_USERNAME")

    password = os.getenv(password_env)

    # Validate required fields
    errors = []
    if not base_url:
        errors.append("storage.base_url is not set")
    if not library:
        errors.append("storage.library is not set")
    if not username:
        errors.append("storage.username is not set (config or HEIBOX_USERNAME env)")
    if not password:
        errors.append(f"{password_env} environment variable is not set")

    if errors:
        error_msg = "WebDAV backend misconfigured:\n  " + "\n  ".join(errors)
        logger.error(error_msg)
        raise StorageError(
            f"WebDAV backend requires configuration. Please set:\n"
            f"  - storage.base_url (e.g., https://heibox.uni-heidelberg.de/seafdav)\n"
            f"  - storage.library (e.g., testing-hei-datahub)\n"
            f"  - HEIBOX_USERNAME environment variable\n"
            f"  - {password_env} environment variable\n\n"
            f"Or switch to filesystem backend in config.yaml"
        )

    # Get timeout settings
    connect_timeout = config.get("storage.connect_timeout", 5)
    read_timeout = config.get("storage.read_timeout", 60)
    max_retries = config.get("storage.max_retries", 3)

    try:
        return WebDAVStorage(
            base_url=base_url,
            library=library,
            username=username,
            password=password,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            max_retries=max_retries,
        )
    except Exception as e:
        raise StorageError(f"Failed to create WebDAV backend: {e}")


def _create_filesystem_backend(config) -> FilesystemStorage:
    """Create filesystem storage backend from config."""
    data_dir = config.get("storage.data_dir")

    if not data_dir:
        # Fallback to default data directory (current datasets location)
        from mini_datahub.infra.paths import DATA_DIR
        data_dir = str(DATA_DIR)
        logger.info(f"No storage.data_dir configured, using default: {data_dir}")

    try:
        return FilesystemStorage(root_dir=data_dir)
    except Exception as e:
        raise StorageError(f"Failed to create filesystem backend: {e}")


def validate_storage_config() -> tuple[bool, Optional[str]]:
    """
    Validate storage configuration without creating backend.

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        get_storage_backend(force_reload=False)
        return True, None
    except StorageError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def clear_storage_cache() -> None:
    """Clear cached storage backend (forces reload on next access)."""
    global _storage_instance
    _storage_instance = None
    logger.debug("Storage backend cache cleared")
