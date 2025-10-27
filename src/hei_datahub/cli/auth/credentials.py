"""
Credential storage abstraction for WebDAV authentication.

Linux-only implementation using Secret Service (keyring) with ENV fallback.
"""
import logging
import os
import platform
from abc import ABC, abstractmethod
from typing import Literal, Optional

logger = logging.getLogger(__name__)


def redact(s: str) -> str:
    """Redact sensitive strings for logging."""
    if not s or len(s) < 4:
        return "***"
    return s[:2] + "***" + s[-2:]


class AuthStore(ABC):
    """Abstract interface for credential storage."""

    @abstractmethod
    def store_secret(self, key_id: str, value: str) -> None:
        """Store a secret with given key_id."""
        pass

    @abstractmethod
    def load_secret(self, key_id: str) -> Optional[str]:
        """Load a secret by key_id. Returns None if not found."""
        pass

    @abstractmethod
    def available(self) -> bool:
        """Check if this storage backend is available."""
        pass

    @property
    @abstractmethod
    def strategy(self) -> Literal["keyring", "env"]:
        """Return the storage strategy name."""
        pass


class KeyringAuthStore(AuthStore):
    """Linux keyring-based credential storage (Secret Service)."""

    SERVICE_NAME = "hei-datahub"

    def __init__(self):
        """Initialize keyring store."""
        if platform.system() != "Linux":
            raise RuntimeError("KeyringAuthStore is only supported on Linux")

        try:
            import keyring
            self._keyring = keyring
            # Test if keyring is actually available
            try:
                # Try to get a non-existent key to verify backend works
                self._keyring.get_password(self.SERVICE_NAME, "test_availability")
                self._available = True
            except Exception as e:
                logger.warning(f"Keyring backend test failed: {e}")
                self._available = False
        except ImportError:
            logger.warning("keyring module not available")
            self._available = False

    def store_secret(self, key_id: str, value: str) -> None:
        """Store secret in Linux keyring."""
        if not self._available:
            raise RuntimeError("Keyring backend not available")

        try:
            self._keyring.set_password(self.SERVICE_NAME, key_id, value)
            logger.info(f"Stored secret in keyring: {key_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to store secret in keyring: {e}")

    def load_secret(self, key_id: str) -> Optional[str]:
        """Load secret from Linux keyring."""
        if not self._available:
            raise RuntimeError("Keyring backend not available")

        try:
            secret = self._keyring.get_password(self.SERVICE_NAME, key_id)
            if secret:
                logger.debug(f"Loaded secret from keyring: {key_id}")
            return secret
        except Exception as e:
            logger.error(f"Failed to load secret from keyring: {e}")
            return None

    def available(self) -> bool:
        """Check if keyring is available."""
        return self._available

    @property
    def strategy(self) -> Literal["keyring", "env"]:
        return "keyring"


class EnvAuthStore(AuthStore):
    """Environment variable-based credential storage (fallback)."""

    def __init__(self):
        """Initialize env store."""
        self._env_vars = {}

    def store_secret(self, key_id: str, value: str) -> None:
        """Store secret in memory (for generating export commands)."""
        # Convert key_id to env var name
        env_name = self._key_to_env(key_id)
        self._env_vars[env_name] = value
        logger.info(f"Stored secret in memory for ENV export: {env_name}")

    def load_secret(self, key_id: str) -> Optional[str]:
        """Load secret from environment variable."""
        env_name = self._key_to_env(key_id)
        value = os.environ.get(env_name)
        if value:
            logger.debug(f"Loaded secret from ENV: {env_name}")
        return value

    def available(self) -> bool:
        """ENV storage is always available."""
        return True

    @property
    def strategy(self) -> Literal["keyring", "env"]:
        return "env"

    def get_export_commands(self) -> list[str]:
        """Get shell export commands for stored secrets."""
        commands = []
        for env_name, value in self._env_vars.items():
            # Properly escape value for shell
            escaped_value = value.replace("'", "'\\''")
            commands.append(f"export {env_name}='{escaped_value}'")
        return commands

    @staticmethod
    def _key_to_env(key_id: str) -> str:
        """
        Convert key_id to environment variable name.

        Examples:
            webdav:token:alice@heibox.uni-heidelberg.de -> HEIDATAHUB_WEBDAV_TOKEN
            webdav:password:bob@example.com -> HEIDATAHUB_WEBDAV_PASSWORD
        """
        # Extract the credential type (token or password)
        if "token" in key_id:
            return "HEIDATAHUB_WEBDAV_TOKEN"
        elif "password" in key_id:
            return "HEIDATAHUB_WEBDAV_PASSWORD"
        else:
            # Generic fallback
            return f"HEIDATAHUB_{key_id.upper().replace(':', '_').replace('@', '_AT_').replace('.', '_')}"


def get_auth_store(prefer_keyring: bool = True) -> AuthStore:
    """
    Get the best available auth store for this platform.

    Args:
        prefer_keyring: If True, try keyring first, fallback to ENV

    Returns:
        AuthStore instance
    """
    if platform.system() != "Linux":
        raise RuntimeError("Only Linux is supported for auth setup")

    if prefer_keyring:
        try:
            store = KeyringAuthStore()
            if store.available():
                logger.info("Using keyring auth store")
                return store
            else:
                logger.warning("Keyring unavailable, falling back to ENV")
        except Exception as e:
            logger.warning(f"Could not initialize keyring: {e}")

    logger.info("Using environment variable auth store")
    return EnvAuthStore()
