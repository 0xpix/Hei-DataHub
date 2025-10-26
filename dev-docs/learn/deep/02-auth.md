# Deep Dive: Authentication System

**Learning Goal**: Master the credential storage and authentication architecture.

By the end of this page, you'll:
- Understand the AuthStore abstraction
- Work with system keyring (Secret Service)
- Implement fallback strategies
- Build secure interactive wizards
- Test WebDAV connections
- Debug authentication issues

---

## Why Abstract Authentication?

**Problem:** Different environments have different secure storage mechanisms.

```
Linux    → Secret Service (GNOME Keyring, KWallet)
macOS    → Keychain
Windows  → Credential Vault
CI/CD    → Environment variables
```

**Solution:** `AuthStore` abstraction with multiple backends.

---

## The AuthStore Interface

**File:** `src/mini_datahub/auth/credentials.py`

### Abstract Base Class

```python
from abc import ABC, abstractmethod
from typing import Literal, Optional

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
```

**Design:**
- **`store_secret()`** — Save credential
- **`load_secret()`** — Retrieve credential
- **`available()`** — Check if backend works
- **`strategy`** — Identify backend type

---

## Backend 1: KeyringAuthStore

**Use case:** Production use on Linux with GUI desktop.

### Implementation

```python
import keyring
import platform
import logging

logger = logging.getLogger(__name__)

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
```

### How It Works

**1. Service Name:**
```python
SERVICE_NAME = "hei-datahub"
```

All credentials are stored under this service in the keyring.

**2. Platform Check:**
```python
if platform.system() != "Linux":
    raise RuntimeError("KeyringAuthStore is only supported on Linux")
```

Currently Linux-only (GNOME Keyring, KWallet via Secret Service).

**3. Availability Test:**
```python
self._keyring.get_password(self.SERVICE_NAME, "test_availability")
self._available = True
```

Test that keyring backend is functional (not just imported).

**4. Storage:**
```python
self._keyring.set_password(self.SERVICE_NAME, key_id, value)
```

Stores credential in system keyring.

---

### Key ID Format

**Pattern:** `webdav:{method}:{username}@{host}`

**Examples:**
```python
# Token-based auth
"webdav:token:alice@heibox.uni-heidelberg.de"

# Password-based auth
"webdav:password:bob@example.com"

# Anonymous (no username)
"webdav:token:-@seafile.example.com"
```

**Derivation function:**

```python
from urllib.parse import urlparse

def _derive_key_id(method: Literal["token", "password"], username: Optional[str], url: str) -> str:
    """
    Derive key ID for keyring storage.

    Format: webdav:{method}:{username_or_dash}@{host}
    """
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    user_part = username if username else "-"
    return f"webdav:{method}:{user_part}@{host}"
```

**Usage:**

```python
key_id = _derive_key_id(
    method="token",
    username="alice",
    url="https://heibox.uni-heidelberg.de/seafdav"
)
# → "webdav:token:alice@heibox.uni-heidelberg.de"
```

---

## Backend 2: EnvAuthStore

**Use case:** CI/CD, headless servers, Docker containers.

### Implementation

```python
import os

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
```

### Environment Variable Naming

**Rules:**
1. Prefix: `HEIDATAHUB_`
2. Credential type: `WEBDAV_TOKEN` or `WEBDAV_PASSWORD`
3. Normalize special characters: `:` → `_`, `@` → `_AT_`, `.` → `_`

**Examples:**

| Key ID | Environment Variable |
|--------|---------------------|
| `webdav:token:alice@heibox` | `HEIDATAHUB_WEBDAV_TOKEN` |
| `webdav:password:bob@example` | `HEIDATAHUB_WEBDAV_PASSWORD` |

---

### Export Commands

**Usage:**

```python
store = EnvAuthStore()
store.store_secret("webdav:token:alice@heibox", "secret123")

# Get shell export commands
commands = store.get_export_commands()
print("\n".join(commands))
```

**Output:**

```bash
export HEIDATAHUB_WEBDAV_TOKEN='secret123'
```

**User workflow:**

```bash
$ hei-datahub auth setup --store=env
...
Add this to ~/.bashrc or ~/.zshrc:
    export HEIDATAHUB_WEBDAV_TOKEN='your-token-here'

Then run:
    source ~/.bashrc
```

---

## Factory Function

**Goal:** Get the best available auth store.

```python
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
```

**Usage:**

```python
from mini_datahub.auth.credentials import get_auth_store

# Try keyring first, fallback to ENV
store = get_auth_store(prefer_keyring=True)

# Force ENV
store = get_auth_store(prefer_keyring=False)
```

---

## Interactive Setup Wizard

**File:** `src/mini_datahub/auth/setup.py`

**Goal:** Guide user through secure auth configuration.

### Wizard Flow

```
┌───────────────────────────────────────┐
│  1. Check existing config             │
│     - Overwrite? Skip? Test?          │
└───────────┬───────────────────────────┘
            │
┌───────────▼───────────────────────────┐
│  2. Prompt for credentials            │
│     - URL                             │
│     - Username                        │
│     - Password (hidden)               │
│     - Library name                    │
└───────────┬───────────────────────────┘
            │
┌───────────▼───────────────────────────┐
│  3. Select storage backend            │
│     - Keyring (if available)          │
│     - ENV (fallback)                  │
└───────────┬───────────────────────────┘
            │
┌───────────▼───────────────────────────┐
│  4. Validate connection               │
│     - Test WebDAV PROPFIND            │
│     - Timeout: 8 seconds              │
└───────────┬───────────────────────────┘
            │
┌───────────▼───────────────────────────┐
│  5. Save credentials                  │
│     - Keyring: set_password()         │
│     - ENV: print export command       │
└───────────┬───────────────────────────┘
            │
┌───────────▼───────────────────────────┐
│  6. Write config.toml                 │
│     - URL, username, library          │
│     - Storage strategy                │
└───────────────────────────────────────┘
```

---

### Implementation

```python
import getpass
import sys
from pathlib import Path
from typing import Optional, Literal

DEFAULT_WEBDAV_URL = "https://heibox.uni-heidelberg.de/seafdav"

def run_setup_wizard(
    url: Optional[str] = None,
    username: Optional[str] = None,
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

    # Interactive prompts
    if not non_interactive:
        print("📍 Enter WebDAV base URL")
        print(f"   Default: {DEFAULT_WEBDAV_URL}")
        url = input("   > ").strip()
        if not url:
            url = DEFAULT_WEBDAV_URL

        print("\n👤 Enter username")
        username = input("   > ").strip()
        if not username:
            print("❌ Username is required", file=sys.stderr)
            return 2

        print("\n🔑 Enter WebDAV password")
        print("   (from Heibox Settings → WebDAV Password)")
        password = getpass.getpass("   > ")

        library_suggestion = "Testing-hei-datahub"
        print(f"\n📁 Library/folder name")
        print(f"   Default: {library_suggestion}")
        library = input("   > ").strip()
        if not library:
            library = library_suggestion

    if not password:
        print("❌ Password cannot be empty", file=sys.stderr)
        return 2

    # Determine storage backend
    from mini_datahub.auth.credentials import get_auth_store, EnvAuthStore

    if store == "env":
        auth_store = EnvAuthStore()
    elif store == "keyring":
        auth_store = get_auth_store(prefer_keyring=True)
        if auth_store.strategy != "keyring":
            print("❌ Keyring requested but not available", file=sys.stderr)
            return 2
    else:
        # Auto-detect
        auth_store = get_auth_store(prefer_keyring=True)

    print(f"\n💾 Using storage: {auth_store.strategy}")

    # Validate connection
    if not no_validate:
        print(f"\n🔍 Testing WebDAV connection (timeout: {timeout}s)...")

        try:
            from mini_datahub.services.webdav_storage import WebDAVStorage

            storage = WebDAVStorage(
                base_url=url,
                library=library,
                username=username,
                password=password,
                connect_timeout=timeout,
            )

            # Try to list root
            files = storage.listdir("")
            print(f"✓ Connection successful! Found {len(files)} items")

        except Exception as e:
            print(f"❌ Connection failed: {e}", file=sys.stderr)
            print("Hint: Check URL, username, password, and network", file=sys.stderr)
            return 1

    # Save credentials
    print("\n💾 Saving credentials...")

    key_id = _derive_key_id("password", username, url)

    try:
        auth_store.store_secret(key_id, password)
        print(f"✓ Credentials saved ({auth_store.strategy})")

        if auth_store.strategy == "env":
            # Print export commands
            export_cmds = auth_store.get_export_commands()
            print("\nAdd to ~/.bashrc or ~/.zshrc:")
            for cmd in export_cmds:
                print(f"    {cmd}")
            print("\nThen run: source ~/.bashrc")

    except Exception as e:
        print(f"❌ Failed to save credentials: {e}", file=sys.stderr)
        return 1

    # Write config file
    print(f"\n📝 Writing config to {config_path}...")

    config_data = {
        "auth": {
            "method": "webdav",
            "url": url,
            "username": username,
            "library": library,
            "stored_in": auth_store.strategy,
            "key_id": key_id,
        }
    }

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)

        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(config_data, f)

        print(f"✓ Config saved")

    except Exception as e:
        print(f"❌ Failed to write config: {e}", file=sys.stderr)
        return 1

    print("\n🎉 Setup complete! Try: hei-datahub")
    return 0
```

---

### Secure Password Input

**Use `getpass` module:**

```python
import getpass

password = getpass.getpass("   > ")
```

**Benefits:**
- Hidden input (no echo)
- Works in terminals
- Cross-platform

**Example:**

```bash
🔑 Enter WebDAV password
   (from Heibox Settings → WebDAV Password)
   > ••••••••
```

---

## Connection Validation

**Goal:** Test WebDAV credentials before saving.

### Implementation

```python
from mini_datahub.services.webdav_storage import WebDAVStorage

def validate_webdav_connection(
    url: str,
    library: str,
    username: str,
    password: str,
    timeout: int = 8,
) -> bool:
    """
    Validate WebDAV credentials by attempting to list root directory.

    Args:
        url: WebDAV base URL
        library: Library/folder name
        username: Username
        password: Password
        timeout: Connection timeout in seconds

    Returns:
        True if connection successful, False otherwise
    """
    try:
        storage = WebDAVStorage(
            base_url=url,
            library=library,
            username=username,
            password=password,
            connect_timeout=timeout,
        )

        # Try to list root
        files = storage.listdir("")

        return True

    except Exception as e:
        logger.error(f"WebDAV validation failed: {e}")
        return False
```

**Usage:**

```python
is_valid = validate_webdav_connection(
    url="https://heibox.uni-heidelberg.de/seafdav",
    library="my-library",
    username="alice",
    password="secret123",
    timeout=8,
)

if is_valid:
    print("✓ Connection successful!")
else:
    print("❌ Connection failed")
```

---

## Configuration File Format

**File:** `~/.config/hei-datahub/config.toml`

```toml
[auth]
method = "webdav"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "alice"
library = "Testing-hei-datahub"
stored_in = "keyring"
key_id = "webdav:password:alice@heibox.uni-heidelberg.de"
```

**Fields:**
- `method` — Always `"webdav"` for now
- `url` — WebDAV base URL
- `username` — Username (optional)
- `library` — Library/folder name in WebDAV
- `stored_in` — `"keyring"` or `"env"`
- `key_id` — Key used to retrieve credential

---

## Security Best Practices

### 1. Never Log Credentials

```python
def redact(s: str) -> str:
    """Redact sensitive strings for logging."""
    if not s or len(s) < 4:
        return "***"
    return s[:2] + "***" + s[-2:]

logger.info(f"Password: {redact(password)}")
# → Password: se***23
```

---

### 2. Use System Keyring When Available

```python
# ✅ Good
store = get_auth_store(prefer_keyring=True)

# ❌ Avoid (unless necessary)
store = EnvAuthStore()
```

---

### 3. Validate Before Saving

```python
# Test connection first
is_valid = validate_webdav_connection(url, library, username, password)

if is_valid:
    # Then save
    store.store_secret(key_id, password)
else:
    print("❌ Invalid credentials, not saving")
```

---

### 4. Escape Shell Variables

```python
# Escape single quotes in password
escaped_value = value.replace("'", "'\\''")
export_cmd = f"export HEIDATAHUB_WEBDAV_TOKEN='{escaped_value}'"
```

**Example:**

```python
password = "p@ss'word"
escaped = password.replace("'", "'\\''")
# → "p@ss'\\''word"

export = f"export HEIDATAHUB_WEBDAV_TOKEN='{escaped}'"
# → export HEIDATAHUB_WEBDAV_TOKEN='p@ss'\''word'
```

---

## Debugging Authentication

### Command: `auth doctor`

**Purpose:** Diagnose auth issues.

```python
def run_auth_doctor():
    """Diagnose authentication setup."""
    from mini_datahub.infra.config_paths import get_config_path

    print("🩺 Authentication Diagnostics\n")

    # Check 1: Config file
    config_path = get_config_path()
    print(f"📝 Config file: {config_path}")

    if not config_path.exists():
        print("   ❌ Config file not found")
        print("   Run: hei-datahub auth setup")
        return

    print("   ✓ Config file exists")

    # Check 2: Load config
    try:
        import tomllib as tomli
    except ImportError:
        import tomli

    with open(config_path, "rb") as f:
        config = tomli.load(f)

    auth_config = config.get("auth", {})

    print(f"\n🔐 Auth configuration:")
    print(f"   Method:     {auth_config.get('method', 'unknown')}")
    print(f"   URL:        {auth_config.get('url', 'unknown')}")
    print(f"   Username:   {auth_config.get('username', '-')}")
    print(f"   Library:    {auth_config.get('library', 'unknown')}")
    print(f"   Storage:    {auth_config.get('stored_in', 'unknown')}")

    # Check 3: Test credential retrieval
    key_id = auth_config.get("key_id")
    stored_in = auth_config.get("stored_in")

    print(f"\n💾 Credential retrieval:")

    from mini_datahub.auth.credentials import get_auth_store

    if stored_in == "keyring":
        store = KeyringAuthStore()
        if not store.available():
            print("   ❌ Keyring not available")
            print("   Install: pip install keyring")
            return

        password = store.load_secret(key_id)
        if password:
            print(f"   ✓ Credential found in keyring")
            print(f"   ✓ Length: {len(password)} characters")
        else:
            print(f"   ❌ Credential not found in keyring")
            print(f"   Run: hei-datahub auth setup")

    elif stored_in == "env":
        env_name = EnvAuthStore._key_to_env(key_id)
        value = os.environ.get(env_name)

        if value:
            print(f"   ✓ Found ${env_name}")
            print(f"   ✓ Length: {len(value)} characters")
        else:
            print(f"   ❌ ${env_name} not set")
            print(f"   Run: export {env_name}='your-password-here'")

    # Check 4: Test connection
    print(f"\n🔍 Testing WebDAV connection...")

    # ... validation code ...

    print("\n✓ Diagnostics complete")
```

---

## What You've Learned

✅ **AuthStore abstraction** — Multiple backends with unified interface
✅ **KeyringAuthStore** — Linux Secret Service integration
✅ **EnvAuthStore** — Environment variable fallback
✅ **Interactive wizard** — Secure password input with validation
✅ **Configuration format** — TOML-based auth config
✅ **Security practices** — Redaction, validation, escaping
✅ **Debugging** — Auth doctor command

---

## Next Steps

Now let's explore the configuration system and how settings are loaded.

**Next:** [Configuration System Deep Dive](03-config.md)

---

## Further Reading

- [Python keyring Library](https://github.com/jaraco/keyring)
- [Secret Service Specification](https://specifications.freedesktop.org/secret-service/latest/)
- [getpass Module](https://docs.python.org/3/library/getpass.html)
- [TOML Format](https://toml.io/)
