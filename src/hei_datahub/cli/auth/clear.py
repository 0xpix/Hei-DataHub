"""
Clear stored WebDAV authentication credentials.

Safely remove auth material without deleting other config.
"""
import logging
import platform
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _clear_index_database() -> None:
    """Clear the search index database."""
    try:
        from hei_datahub.services.index_service import INDEX_DB_PATH

        if INDEX_DB_PATH.exists():
            INDEX_DB_PATH.unlink()
            print(f"ℹ️  Removed search index: {INDEX_DB_PATH}")
            logger.info(f"Removed index database: {INDEX_DB_PATH}")
        else:
            print(f"ℹ️  Index database not found at {INDEX_DB_PATH}")

    except Exception as e:
        logger.warning(f"Error clearing index database: {e}")
        print(f"⚠️  Could not remove index database: {e}")


def run_clear(force: bool = False, clear_all: bool = False) -> int:
    """
    Clear stored WebDAV authentication credentials and search index.

    Args:
        force: Skip interactive confirmation
        clear_all: Also remove cached session files

    Returns:
        Exit code (0 = success)
    """
    if platform.system() not in ["Linux", "Windows"]:
        print(f"❌ Error: auth clear is only supported on Linux and Windows (current: {platform.system()}).", file=sys.stderr)
        return 2

    from hei_datahub.infra.config_paths import get_config_path

    config_path = get_config_path()

    # Check if config exists
    if not config_path.exists():
        # Even if no config, still clear index
        _clear_index_database()
        print("Nothing to clear.")
        return 0

    # Read current config
    try:
        try:
            import tomllib as tomli
        except ImportError:
            import tomli

        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_config = config.get("auth", {})

        if not auth_config:
            # No auth config, but still clear index
            _clear_index_database()
            print("Nothing to clear.")
            return 0

    except Exception as e:
        print(f"❌ Error reading config: {e}", file=sys.stderr)
        return 2

    # Interactive confirmation unless --force
    if not force:
        response = input("⚠️  Are you sure you want to clear WebDAV credentials? [y/N] ").strip().lower()
        if response not in ("y", "yes"):
            print("Cancelled.")
            return 0

    # Clear credentials from keyring/env
    try:
        from hei_datahub.cli.auth.credentials import KeyringAuthStore

        key_id = auth_config.get("key_id")
        stored_in = auth_config.get("stored_in", "keyring")

        if key_id:
            if stored_in == "keyring":
                # Clear from keyring
                try:
                    store = KeyringAuthStore()
                    if store.available():
                        # Delete from keyring by setting to None
                        import keyring
                        keyring.delete_password(KeyringAuthStore.SERVICE_NAME, key_id)
                        logger.info(f"Cleared credential from keyring: {key_id}")
                except Exception as e:
                    logger.warning(f"Could not clear keyring credential: {e}")

            elif stored_in == "env":
                # For ENV storage, we can't actually clear the environment variable
                # Just inform the user
                from hei_datahub.cli.auth.credentials import EnvAuthStore
                env_name = EnvAuthStore._key_to_env(key_id)
                print(f"ℹ️  Note: Remove environment variable manually: unset {env_name}")

    except Exception as e:
        logger.warning(f"Error clearing credentials: {e}")

    # Remove [auth] section from config file
    try:
        # Remove the auth section
        if "auth" in config:
            del config["auth"]

        # Write back the config (without auth section)
        _write_toml_config(config_path, config)

        logger.info(f"Removed [auth] section from {config_path}")

    except Exception as e:
        print(f"❌ Error updating config file: {e}", file=sys.stderr)
        return 2

    # Clear cached session files if --all
    if clear_all:
        try:
            from hei_datahub.infra.config_paths import get_user_config_dir
            config_dir = get_user_config_dir()

            # Look for session/cache files (adjust patterns as needed)
            session_patterns = ["*session*", "*cache*", "*.etag"]
            removed_count = 0

            for pattern in session_patterns:
                for file_path in config_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            removed_count += 1
                            logger.info(f"Removed cached file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Could not remove {file_path}: {e}")

            if removed_count > 0:
                print(f"ℹ️  Removed {removed_count} cached file(s)")

        except Exception as e:
            logger.warning(f"Error clearing cached files: {e}")

    # Always clear index.db when clearing auth
    _clear_index_database()

    print("✅ Cleared WebDAV credentials and search index.")
    return 0


def _write_toml_config(path: Path, config: dict) -> None:
    """
    Write TOML config file.

    Args:
        path: Path to config file
        config: Config dictionary
    """
    # Use tomli_w for writing TOML (if available), otherwise write manually
    try:
        import tomli_w

        with open(path, "wb") as f:
            tomli_w.dump(config, f)

    except ImportError:
        # Fallback: manual TOML generation for simple configs
        lines = []

        for section_name, section_data in config.items():
            if not isinstance(section_data, dict):
                # Top-level key-value
                lines.append(f"{section_name} = {_toml_value(section_data)}\n")
            else:
                # Section
                lines.append(f"\n[{section_name}]\n")
                for key, value in section_data.items():
                    lines.append(f"{key} = {_toml_value(value)}\n")

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)


def _toml_value(value) -> str:
    """Convert Python value to TOML string representation."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        # Escape quotes
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        items = ", ".join(_toml_value(item) for item in value)
        return f"[{items}]"
    else:
        return f'"{str(value)}"'
