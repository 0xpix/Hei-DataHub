"""
Storage manager: Creates WebDAV storage instances (cloud-only).

Simplified for WebDAV-only usage (no filesystem backend).
"""
import logging
import os
from typing import Optional

from hei_datahub.services.config import get_config
from hei_datahub.services.webdav_storage import WebDAVStorage, StorageError

logger = logging.getLogger(__name__)

# Cached storage instance
_storage_instance: Optional[WebDAVStorage] = None


def get_storage_backend(force_reload: bool = False) -> WebDAVStorage:
    """
    Get the WebDAV storage instance (cached).

    Reads configuration and creates WebDAV backend with credentials from:
    - base_url, library, username from config
    - token from environment variable or keyring

    Args:
        force_reload: Force recreation of storage backend (default: False)

    Returns:
        WebDAVStorage instance

    Raises:
        StorageError: If configuration is invalid or backend cannot be created
    """
    global _storage_instance

    if _storage_instance is not None and not force_reload:
        return _storage_instance

    config = get_config()

    # Always create WebDAV storage (cloud-only)
    _storage_instance = _create_webdav_backend(config)

    return _storage_instance


def _create_webdav_backend(config) -> WebDAVStorage:
    """Create WebDAV storage backend from config."""
    base_url = config.get("storage.base_url")
    library = config.get("storage.library")
    username = config.get("storage.username")
    password_env = config.get("storage.password_env", "HEIBOX_WEBDAV_TOKEN")

    # Initialize password as None
    password = None

    # Try to load from auth setup first (keyring or ENV)
    try:
        from hei_datahub.infra.config_paths import get_config_path
        from hei_datahub.cli.auth.credentials import get_auth_store

        auth_config_path = get_config_path()
        if auth_config_path.exists():
            # Load auth config
            try:
                import tomllib as tomli
            except ImportError:
                import tomli

            with open(auth_config_path, "rb") as f:
                auth_config = tomli.load(f)

            auth_section = auth_config.get("auth", {})
            cloud_section = auth_config.get("cloud", {})

            if auth_section:
                # Use auth config values
                base_url = auth_section.get("url") or base_url
                username = auth_section.get("username") or username
                key_id = auth_section.get("key_id")
                stored_in = auth_section.get("stored_in")

            # Library is in [cloud] section
            if cloud_section:
                library = cloud_section.get("library") or library

                # Load credential from keyring or ENV
                if key_id and stored_in:
                    auth_store = get_auth_store(prefer_keyring=(stored_in == "keyring"))
                    password = auth_store.load_secret(key_id)
                    if not password:
                        logger.warning(f"Could not load credential from {stored_in}: {key_id}")
    except Exception as e:
        logger.debug(f"Could not load auth config: {e}")

    # Fallback to old config.yaml + ENV method
    if not password:
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
        errors.append(f"Credential not found. Run: hei-datahub auth setup")

    if errors:
        error_msg = "WebDAV backend misconfigured:\n  " + "\n  ".join(errors)
        logger.error(error_msg)
        raise StorageError(
            f"WebDAV backend requires configuration.\n\n"
            f"Quick setup:\n"
            f"  hei-datahub auth setup\n\n"
            f"Or manually set:\n"
            f"  - storage.base_url in config.yaml\n"
            f"  - storage.library in config.yaml\n"
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
