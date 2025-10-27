# Authentication Module

**Linux-only secure credential management for Hei-DataHub**

## Overview

This module provides secure WebDAV credential storage and management for Hei-DataHub on Linux systems. It uses the system keyring (Secret Service) to store credentials securely, with an environment variable fallback when keyring is unavailable.

## Components

### `credentials.py`
- `AuthStore` - Abstract interface for credential storage
- `KeyringAuthStore` - Linux keyring implementation (Secret Service)
- `EnvAuthStore` - Environment variable fallback
- `get_auth_store()` - Factory function to get best available store

### `validator.py`
- `WebDAVValidator` - HTTP client for testing WebDAV credentials
- `validate_credentials()` - Validate credentials using HEAD/PROPFIND
- Handles 405/501 (HEAD unsupported) by falling back to PROPFIND
- Maps common error codes to human-readable messages

### `setup.py`
- `run_setup_wizard()` - Interactive/non-interactive setup wizard
- Supports token and password authentication
- Validates credentials before storing
- Writes non-secret config to TOML
- Handles overwrite/skip/test for existing configs

## Usage

### CLI

**Interactive:**
```bash
hei-datahub auth setup
```

**Non-interactive:**
```bash
hei-datahub auth setup \
  --url https://heibox.uni-heidelberg.de/seafdav \
  --username alice \
  --token "$TOKEN" \
  --non-interactive --overwrite
```

**Check status:**
```bash
hei-datahub auth status
```

### Programmatic

```python
from mini_datahub.auth.credentials import get_auth_store
from mini_datahub.auth.validator import validate_credentials

# Get auth store
store = get_auth_store(prefer_keyring=True)

# Store credential
key_id = "webdav:token:alice@heibox.uni-heidelberg.de"
store.store_secret(key_id, "my-secret-token")

# Load credential
token = store.load_secret(key_id)

# Validate
success, message, status = validate_credentials(
    url="https://heibox.uni-heidelberg.de/seafdav",
    username="alice",
    credential=token
)
```

## Security

### Keyring Storage (Preferred)

- Uses Linux Secret Service API
- Credentials encrypted by system keyring daemon
- Requires `gnome-keyring`, `kwallet`, or compatible backend
- Never writes secrets to disk

**Service name:** `hei-datahub`
**Key format:** `webdav:{method}:{username}@{host}`

### ENV Fallback (Less Secure)

When keyring unavailable:
- Stores in memory during setup
- Generates export commands for shell profile
- Warns user about reduced security

**Env vars:**
- `HEIDATAHUB_WEBDAV_TOKEN`
- `HEIDATAHUB_WEBDAV_PASSWORD`
- `HEIDATAHUB_WEBDAV_URL`
- `HEIDATAHUB_WEBDAV_USERNAME`

### Config File (Non-Secret)

**Location:** `~/.config/hei-datahub/config.toml`

**Contents (example):**
```toml
[auth]
method = "token"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "alice"
key_id = "webdav:token:alice@heibox.uni-heidelberg.de"
stored_in = "keyring"
```

**Security:** NO secrets stored in this file.

## Requirements

### Python Dependencies

- `keyring>=24.0.0` - Keyring abstraction
- `tomli>=2.0.0` (Python <3.11) - TOML reading
- `tomli-w>=1.0.0` - TOML writing
- `requests>=2.31.0` - HTTP client

### Linux System Dependencies

**For keyring support:**
- Secret Service implementation (gnome-keyring, kwallet, etc.)
- D-Bus session bus
- libsecret (optional but recommended)

**Package hints:**

Arch:
```bash
sudo pacman -S python-keyring python-secretstorage libsecret
```

Debian/Ubuntu:
```bash
sudo apt install python3-keyring python3-secretstorage libsecret-1-0 gnome-keyring
```

Fedora:
```bash
sudo dnf install python3-keyring python3-secretstorage libsecret gnome-keyring
```

## Platform Support

**Supported:** Linux only
**Not supported:** macOS, Windows

The module explicitly checks for Linux and raises `RuntimeError` on other platforms.

## Error Handling

### Exit Codes

- `0` - Success
- `1` - Validation failure or user abort
- `2` - Usage error (invalid arguments)

### Validation Error Mapping

- `401/403` → "Invalid credentials or insufficient permissions"
- `404` → "Server path not found (check the URL)"
- `405/501` → HEAD unsupported, retries with PROPFIND
- `5xx` → "Server error; try again later"
- Timeout → "Request timed out; check connectivity"
- SSL/TLS → "TLS/SSL error; check certificate"

## Testing

### Unit Tests

```bash
pytest tests/auth/
```

### Manual Testing

```bash
# Interactive setup
hei-datahub auth setup

# Non-interactive
hei-datahub auth setup \
  --url https://heibox.uni-heidelberg.de/seafdav \
  --token "test-token" \
  --no-validate \
  --non-interactive --overwrite

# Status check
hei-datahub auth status

# Test keyring availability
python3 -c "
from mini_datahub.auth.credentials import KeyringAuthStore
store = KeyringAuthStore()
print(f'Keyring available: {store.available()}')
print(f'Strategy: {store.strategy}')
"
```

## Troubleshooting

### Keyring Not Available

**Symptoms:**
```
⚠️ Linux keyring backend unavailable.
    Falling back to environment variables (less secure).
```

**Fixes:**
1. Ensure keyring daemon running: `gnome-keyring-daemon --start --components=secrets`
2. Install dependencies: `python3-keyring python3-secretstorage libsecret`
3. Check D-Bus: `echo $DBUS_SESSION_BUS_ADDRESS`

### Validation Fails

**Common causes:**
- Expired token
- Wrong URL/endpoint
- Network connectivity
- TLS/certificate issues

**Debug:**
```bash
# Test with curl
curl -u "username:token" https://heibox.uni-heidelberg.de/seafdav/

# Increase timeout
hei-datahub auth setup --timeout 15

# Skip validation (not recommended)
hei-datahub auth setup --no-validate
```

## Documentation

- [Complete setup guide](../../docs/installation/auth-setup-linux.md)
- [Usage examples](../../docs/how-to/add-dataset-to-cloud.md)

## Future Enhancements

Potential improvements for future releases:

- [ ] Add `hei-datahub auth clear` command
- [ ] Add `hei-datahub auth test` command (validate stored credentials)
- [ ] Add `hei-datahub auth rotate` command (update token)
- [ ] Support multiple WebDAV profiles
- [ ] Integration with OS credential managers (Plasma Vault, etc.)
- [ ] Token expiry warnings

## Contributing

When adding features:
1. Maintain Linux-only scope
2. Never log or print secrets
3. Use `redact()` helper for logging URLs with auth
4. Add tests for new functionality
5. Update documentation

## License

MIT License - same as Hei-DataHub
