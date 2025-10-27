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
    from hei_datahub.infra.config_paths import get_config_path
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
        print("📍 Enter WebDAV base URL")
        print(f"   Default: {DEFAULT_WEBDAV_URL}")
        url = input("   > ").strip()
        if not url:
            url = DEFAULT_WEBDAV_URL

        print("\n👤 Enter username")
        print("   (e.g., username@auth.local)")
        username = input("   > ").strip()
        if not username:
            print("❌ Username is required", file=sys.stderr)
            return 2

        print("\n🔑 Enter WebDAV password")
        print("   (from Heibox Settings → WebDAV Password)")
        credential = getpass.getpass("   > ")
        method = "password"

        # Library name - ask after authentication method
        library_suggestion = "Testing-hei-datahub"
        print(f"\n📁 Library/folder name")
        print(f"   Default: {library_suggestion}")
        library = input("   > ").strip()
        if not library:
            library = library_suggestion

    if not credential:
        print("❌ Credential cannot be empty", file=sys.stderr)
        return 2

    # Determine storage backend
    from hei_datahub.cli.auth.credentials import get_auth_store, EnvAuthStore

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
        # Interactive mode: ask user
        if non_interactive:
            # Auto-detect in non-interactive mode
            auth_store = get_auth_store(prefer_keyring=True)
            use_keyring = auth_store.strategy == "keyring"
        else:
            # Ask user in interactive mode
            print("\n🔐 Store credentials in Linux keyring?")
            print("   Recommended for security (encrypted storage)")
            keyring_choice = input("   [Y/n] > ").strip().lower()
            if keyring_choice in ("", "y", "yes"):
                auth_store = get_auth_store(prefer_keyring=True)
                use_keyring = auth_store.strategy == "keyring"
                if not use_keyring:
                    print("\n⚠️  Linux keyring backend unavailable.")
                    print("    Falling back to environment variables (less secure).")
                    accept = input("    Continue with ENV storage? [y/N]: ").strip().lower()
                    if accept not in ("y", "yes"):
                        print("Aborted.")
                        return 1
                    auth_store = EnvAuthStore()
            else:
                auth_store = EnvAuthStore()
                use_keyring = False

    # Validate credentials
    if not no_validate:
        print("\n🔍 Testing connection...")
        from hei_datahub.cli.auth.validator import validate_credentials

        success, message, status_code = validate_credentials(url, username, credential, timeout)

        if not success:
            print(f"\n❌ {message}")
            if not non_interactive:
                retry = input("\n🔄 Retry? [y/N]: ").strip().lower()
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
            print("   ✓ Successfully connected to WebDAV server")
            print("   ✓ Write permissions verified")
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
    print(f"\n✅ Configuration saved")
    print(f"   📄 {config_path}")
    if use_keyring:
        print(f"   🔐 Credentials stored in Linux keyring")
    else:
        print(f"   💾 Credentials stored in environment variables")

    # Status line for debugging (optional)
    if non_interactive:
        username_display = username or "-"
        print(f"\n📊 Details: {url} · {method} · {username_display} · {auth_store.strategy} · {key_id}")

    # ENV export commands if needed
    if auth_store.strategy == "env":
        print("\n📋 Add these to your shell profile (~/.bashrc or ~/.zshrc):")
        env_store = auth_store  # type: EnvAuthStore
        for cmd in env_store.get_export_commands():
            print(f"   {cmd}")
        print(f"   export HEIDATAHUB_WEBDAV_URL='{url}'")
        if username:
            print(f"   export HEIDATAHUB_WEBDAV_USERNAME='{username}'")

    # Next steps
    print("\n🎯 Next steps:")
    print("   • Run: hei-datahub auth status")
    print("   • Run: hei-datahub auth doctor")
    print("   • Launch TUI: hei-datahub")

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
        from hei_datahub.cli.auth.credentials import get_auth_store

        if stored_in == "keyring":
            auth_store = get_auth_store(prefer_keyring=True)
        else:
            from hei_datahub.cli.auth.credentials import EnvAuthStore
            auth_store = EnvAuthStore()

        credential = auth_store.load_secret(key_id)
        if not credential:
            print(f"❌ Could not load credential with key: {key_id}", file=sys.stderr)
            return 1

        # Validate
        print("Testing existing configuration...")
        from hei_datahub.cli.auth.validator import validate_credentials

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
