"""
Interactive setup wizard for WebDAV authentication.

Linux-only wizard with secure keyring storage.
"""
import getpass
import logging
import platform
import sys
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Constants
DEFAULT_WEBDAV_URL = "https://heibox.uni-heidelberg.de/seafdav"
SERVICE_NAME = "hei-datahub"


def _derive_key_id(method: Literal["token", "password"], username: Optional[str], url: str) -> str:
    """
    Derive key ID for keyring storage.

    Format: webdav:{method}:{username_or_dash}@{host}
    """
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    user_part = username if username else "-"
    return f"webdav:{method}:{user_part}@{host}"


def run_setup_wizard(
    url: Optional[str] = None,
    username: Optional[str] = None,
    token: Optional[str] = None,
    password: Optional[str] = None,
    library: Optional[str] = None,
    store: Optional[Literal["keyring", "env"]] = None,
    no_validate: bool = False,
    overwrite: bool = False,
    timeout: int = 8,
    non_interactive: bool = False,
) -> int:
    """
    Run the auth setup wizard.

    Args:
        url: WebDAV URL (non-interactive)
        username: Username (non-interactive)
        token: Token credential (non-interactive)
        password: Password credential (non-interactive)
        library: Library/folder name in WebDAV (non-interactive)
        store: Force storage backend (non-interactive)
        no_validate: Skip credential validation
        overwrite: Overwrite existing config without prompting
        timeout: Validation timeout in seconds
        non_interactive: Non-interactive mode

    Returns:
        Exit code: 0 success, 1 validation/abort, 2 usage error
    """
    # Platform check
    if platform.system() != "Linux":
        print("❌ Error: auth setup is only supported on Linux.", file=sys.stderr)
        return 2

    print("🔐 Hei-DataHub WebDAV Authentication Setup (Linux)\n")

    # Get config path
    from mini_datahub.infra.config_paths import get_config_path
    config_path = get_config_path()
    config_exists = config_path.exists()

    # Handle existing config
    if config_exists and not overwrite:
        if non_interactive:
            print(f"❌ Config already exists at {config_path}", file=sys.stderr)
            print("Use --overwrite to replace it.", file=sys.stderr)
            return 2
        else:
            print(f"Found config at {config_path}")
            choice = input("  [O]verwrite, [S]kip, [T]est? ").strip().upper()
            if choice == "S":
                print("Skipped. Existing config unchanged.")
                return 0
            elif choice == "T":
                return _test_existing_config(config_path, timeout)
            elif choice != "O":
                print("Invalid choice. Aborting.")
                return 1

    # Interactive or non-interactive flow
    if non_interactive:
        # Validate non-interactive inputs
        if not url:
            print("❌ Error: --url is required in non-interactive mode", file=sys.stderr)
            return 2
        if not (token or password):
            print("❌ Error: Either --token or --password is required", file=sys.stderr)
            return 2
        if token and password:
            print("❌ Error: Cannot specify both --token and --password", file=sys.stderr)
            return 2

        method = "token" if token else "password"
        credential = token or password

    else:
        # Interactive prompts
        url = input(f"WebDAV URL [{DEFAULT_WEBDAV_URL}]: ").strip()
        if not url:
            url = DEFAULT_WEBDAV_URL

        # Extract library name suggestion from URL
        library_suggestion = "Testing-hei-datahub"
        library = input(f"Library/folder name [{library_suggestion}]: ").strip()
        if not library:
            library = library_suggestion

        has_token = input("Do you have a WebDAV token? [Y/n]: ").strip().lower()
        if has_token in ("", "y", "yes"):
            method = "token"
            username = input("Username (optional): ").strip() or None
            credential = getpass.getpass("Token: ")
        else:
            method = "password"
            username = input("Username: ").strip()
            if not username:
                print("❌ Username is required for password authentication", file=sys.stderr)
                return 2
            credential = getpass.getpass("Password: ")

    if not credential:
        print("❌ Credential cannot be empty", file=sys.stderr)
        return 2

    # Determine storage backend
    from mini_datahub.auth.credentials import get_auth_store, EnvAuthStore

    if store == "env":
        auth_store = EnvAuthStore()
        use_keyring = False
    elif store == "keyring":
        auth_store = get_auth_store(prefer_keyring=True)
        if auth_store.strategy != "keyring":
            print("❌ Keyring storage requested but not available", file=sys.stderr)
            return 2
        use_keyring = True
    else:
        # Auto-detect
        auth_store = get_auth_store(prefer_keyring=True)
        use_keyring = auth_store.strategy == "keyring"

    # Warn about keyring fallback
    if not use_keyring and not non_interactive:
        print("\n⚠️  Linux keyring backend unavailable.")
        print("    Falling back to environment variables (less secure).")
        accept = input("    Continue with ENV storage? [y/N]: ").strip().lower()
        if accept not in ("y", "yes"):
            print("Aborted.")
            return 1

    # Validate credentials
    if not no_validate:
        print("\nValidating...")
        from mini_datahub.auth.validator import validate_credentials

        success, message, status_code = validate_credentials(url, username, credential, timeout)

        if not success:
            print(f"\n❌ Validation failed: {message}")
            if not non_interactive:
                retry = input("Retry? [y/N]: ").strip().lower()
                if retry in ("y", "yes"):
                    # Recursive retry
                    return run_setup_wizard(
                        url=url,
                        username=username,
                        token=token if method == "token" else None,
                        password=password if method == "password" else None,
                        store=store,
                        no_validate=no_validate,
                        overwrite=overwrite,
                        timeout=timeout,
                        non_interactive=False,
                    )
            return 1
    else:
        print("\n⚠️  Skipping validation (--no-validate). Future operations may fail.")

    # Store credential
    key_id = _derive_key_id(method, username, url)
    try:
        auth_store.store_secret(key_id, credential)
    except Exception as e:
        print(f"\n❌ Failed to store credential: {e}", file=sys.stderr)
        return 1

    # Write config (non-secret)
    config_data = {
        "auth": {
            "method": method,
            "url": url,
            "library": library or "",
            "username": username or "",
            "key_id": key_id,
            "stored_in": auth_store.strategy,
        }
    }

    try:
        _write_config(config_path, config_data)
    except Exception as e:
        print(f"\n❌ Failed to write config: {e}", file=sys.stderr)
        return 1

    # Success message
    if not no_validate:
        print("\n✅ WebDAV credentials verified and stored securely in your Linux keyring.")
    else:
        print(f"\n✅ Credentials stored in {auth_store.strategy}.")

    # Status line
    username_display = username or "-"
    print(f"URL: {url} · Method: {method} · User: {username_display} · Storage: {auth_store.strategy} · Key: {key_id}")

    # ENV export commands if needed
    if auth_store.strategy == "env":
        print("\n📋 Add these to your shell profile (~/.bashrc or ~/.zshrc):")
        env_store = auth_store  # type: EnvAuthStore
        for cmd in env_store.get_export_commands():
            print(f"  {cmd}")
        print(f"  export HEIDATAHUB_WEBDAV_URL='{url}'")
        if username:
            print(f"  export HEIDATAHUB_WEBDAV_USERNAME='{username}'")

    # Next steps
    print("\nNext: run `hei-datahub auth status` or start using WebDAV operations.")

    return 0


def _test_existing_config(config_path: Path, timeout: int) -> int:
    """Test existing configuration."""
    try:
        # Python 3.11+ has tomllib built-in
        try:
            import tomllib as tomli
        except ImportError:
            import tomli

        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_config = config.get("auth", {})
        url = auth_config.get("url")
        username = auth_config.get("username")
        key_id = auth_config.get("key_id")
        stored_in = auth_config.get("stored_in")

        if not url or not key_id:
            print("❌ Invalid config: missing required fields", file=sys.stderr)
            return 1

        # Load credential
        from mini_datahub.auth.credentials import get_auth_store

        if stored_in == "keyring":
            auth_store = get_auth_store(prefer_keyring=True)
        else:
            from mini_datahub.auth.credentials import EnvAuthStore
            auth_store = EnvAuthStore()

        credential = auth_store.load_secret(key_id)
        if not credential:
            print(f"❌ Could not load credential with key: {key_id}", file=sys.stderr)
            return 1

        # Validate
        print("Testing existing configuration...")
        from mini_datahub.auth.validator import validate_credentials

        success, message, status_code = validate_credentials(url, username or None, credential, timeout)

        if success:
            print(f"\n✅ {message}")
            return 0
        else:
            print(f"\n❌ Validation failed: {message}")
            return 1

    except Exception as e:
        print(f"❌ Error testing config: {e}", file=sys.stderr)
        return 1


def _write_config(config_path: Path, config_data: dict) -> None:
    """Write config to TOML file."""
    try:
        import tomli_w
    except ImportError:
        # Fallback to manual TOML writing
        _write_config_manual(config_path, config_data)
        return

    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Merge with existing config if present
    if config_path.exists():
        try:
            # Python 3.11+ has tomllib built-in
            try:
                import tomllib as tomli
            except ImportError:
                import tomli
            with open(config_path, "rb") as f:
                existing = tomli.load(f)
        except:
            existing = {}
    else:
        existing = {}

    # Merge auth section
    existing["auth"] = config_data["auth"]

    # Write
    with open(config_path, "wb") as f:
        tomli_w.dump(existing, f)

    logger.info(f"Wrote config to {config_path}")


def _write_config_manual(config_path: Path, config_data: dict) -> None:
    """Manual TOML writing fallback."""
    config_path.parent.mkdir(parents=True, exist_ok=True)

    auth = config_data["auth"]

    toml_content = f"""# Hei-DataHub Configuration
# WebDAV authentication (secrets stored in keyring)

[auth]
method = "{auth['method']}"
url = "{auth['url']}"
username = "{auth['username']}"
key_id = "{auth['key_id']}"
stored_in = "{auth['stored_in']}"
"""

    config_path.write_text(toml_content, encoding="utf-8")
    logger.info(f"Wrote config to {config_path} (manual)")
