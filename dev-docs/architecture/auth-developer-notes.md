# Authentication Architecture - Developer Notes

## Overview

This document explains the authentication system architecture for future maintainers.

## Key Concepts

### Credential Types

The system uses **WebDAV credentials** for authentication:

- **WebDAV username:** User's HeiBox/Seafile username
- **WebDAV password:** Special password created in HeiBox Settings → WebDAV Password
  - This is NOT the user's web login password
  - This is NOT the same as a Seafile API token

**Important:** The system does NOT have separate "Hei-DataHub user credentials". The WebDAV credentials ARE the user credentials for accessing cloud storage.

### Storage Locations

**Sensitive data (encrypted):**
- Linux keyring via Secret Service API
- Environment variables (fallback, less secure)

**Non-sensitive data (plaintext):**
- `~/.config/hei-datahub/config.toml`

## Components

### 1. GUI Auth Wizard (`ui/widgets/settings_wizard.py`)

**Purpose:** Interactive wizard for setting up WebDAV authentication within the TUI.

**Key methods:**
- `_save_settings_worker()` - Async worker that saves credentials
- `save_settings()` - Alternative sync save method
- `test_connection()` - Tests WebDAV connection before saving

**Configuration format:**
```toml
[auth]
method = "password"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "alice"
library = "test-library"
key_id = "webdav:password:alice@heibox.uni-heidelberg.de"
stored_in = "keyring"

[cloud]
library = "test-library"
```

**Critical implementation details:**
- Uses `get_auth_store(prefer_keyring=True)` to get storage backend
- Generates key_id in format: `webdav:{method}:{username}@{host}`
- Calls `store.store_secret(key_id, password)` to save credential
- Saves all fields required by storage_manager

### 2. CLI Auth Setup (`cli/auth/setup.py`)

**Purpose:** Command-line wizard for setting up WebDAV authentication.

**Entry point:**
```bash
hei-datahub auth setup [OPTIONS]
```

**Key functions:**
- `run_setup_wizard()` - Main wizard logic
- `_derive_key_id()` - Generates key_id from method, username, URL
- `_write_config()` - Writes config.toml file

**Configuration format:** (Same as GUI)

**Critical implementation details:**
- Interactive prompts for URL, username, password, library
- Non-interactive mode with `--non-interactive` flag
- Validates credentials with `validate_credentials()` from validator.py
- Supports keyring and ENV storage backends

### 3. Credential Storage (`cli/auth/credentials.py`)

**Purpose:** Abstract credential storage with keyring and ENV backends.

**Classes:**
- `AuthStore` (ABC) - Abstract interface
- `KeyringAuthStore` - Linux keyring implementation (preferred)
- `EnvAuthStore` - Environment variable fallback

**API:**
```python
store = get_auth_store(prefer_keyring=True)

# Store
store.store_secret(key_id, password)

# Load
password = store.load_secret(key_id)  # Returns None if not found

# Check availability
if store.available():
    print(f"Using {store.strategy}")
```

**Key ID format:**
```
webdav:{method}:{username}@{host}
```

Examples:
- `webdav:password:alice@heibox.uni-heidelberg.de`
- `webdav:token:bob@cloud.example.com`
- `webdav:password:-@myserver.org` (username optional for token auth)

### 4. Storage Manager (`services/storage_manager.py`)

**Purpose:** Creates WebDAV storage instances and manages credential loading.

**Key function:**
```python
storage = get_storage_backend(force_reload=False)
```

**Authentication loading logic:**

1. Check for `~/.config/hei-datahub/config.toml`
2. Load `[auth]` section
3. Extract: `url`, `username`, `library`, `key_id`, `stored_in`
4. Load credential from keyring using `key_id`
5. Fallback to environment variables if keyring fails
6. Validate all required fields are present
7. Raise `StorageError` if anything is missing

**Error message when auth not configured:**
```
Credential not found. Run: hei-datahub auth setup
```

**Critical checks:**
```python
if not base_url:
    errors.append("storage.base_url is not set")
if not library:
    errors.append("storage.library is not set")
if not username:
    errors.append("storage.username is not set")
if not password:
    errors.append("Credential not found. Run: hei-datahub auth setup")
```

### 5. Validator (`cli/auth/validator.py`)

**Purpose:** Validates WebDAV credentials by attempting authentication.

**Key class:**
```python
validator = WebDAVValidator(url, username, credential, timeout=8)
success, message, status_code = validator.validate()
```

**Validation steps:**
1. HTTP PROPFIND request to WebDAV URL
2. Basic auth with username + password/token
3. Check for 2xx status code
4. Return (success, message, status_code)

## Data Flow

### GUI Auth Setup Flow

```
User fills wizard form
  ↓
User clicks "Save"
  ↓
_save_settings_worker() runs in background thread
  ↓
Generate key_id: webdav:password:{username}@{host}
  ↓
get_auth_store(prefer_keyring=True)
  ↓
store.store_secret(key_id, password)
  ↓
Build config dict with [auth] and [cloud] sections
  ↓
Write to ~/.config/hei-datahub/config.toml
  ↓
Notify user: "Settings saved!"
  ↓
Close wizard
```

### CLI Auth Setup Flow

```
User runs: hei-datahub auth setup
  ↓
Prompt for: URL, username, password, library
  ↓
Derive key_id from method, username, URL
  ↓
(Optional) Validate credentials with WebDAV server
  ↓
get_auth_store(prefer_keyring=True)
  ↓
store.store_secret(key_id, password)
  ↓
Build config dict with [auth] section
  ↓
Write to ~/.config/hei-datahub/config.toml
  ↓
Print success message
```

### Dataset Creation Flow (with Auth)

```
User clicks "Add Dataset" in TUI
  ↓
User fills dataset form
  ↓
User clicks "Save"
  ↓
submit_form() validates form
  ↓
save_to_cloud() runs in background thread
  ↓
get_storage_backend() called
  ↓
storage_manager loads config.toml
  ↓
storage_manager extracts auth section
  ↓
storage_manager loads credential from keyring
  ↓
If credential missing: raise StorageError("Credential not found. Run: hei-datahub auth setup")
  ↓
If credential found: create WebDAVStorage instance
  ↓
Upload dataset metadata to WebDAV
  ↓
Notify user: "Dataset uploaded!"
```

## Compatibility Requirements

### Config File Structure

Both GUI and CLI MUST save these fields in `[auth]` section:

- `method` (string) - "password" or "token"
- `url` (string) - WebDAV base URL
- `username` (string) - WebDAV username
- `library` (string) - Library/folder name
- `key_id` (string) - Key for credential retrieval
- `stored_in` (string) - "keyring" or "env"

**Optional for backward compatibility:**
- `[cloud]` section with `library` field

### Key ID Format

Both GUI and CLI MUST use this format:

```
webdav:{method}:{username_or_dash}@{hostname}
```

**Implementation:**
```python
from urllib.parse import urlparse

def derive_key_id(method: str, username: Optional[str], url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    user_part = username if username else "-"
    return f"webdav:{method}:{user_part}@{host}"
```

### Storage Manager Requirements

Storage manager MUST:

1. Load `[auth]` section from config
2. Support `library` in both `auth` section and `cloud` section
3. Default to keyring if `stored_in` is missing
4. Load credential using `auth_store.load_secret(key_id)`
5. Raise clear error if credential not found

## Common Issues and Solutions

### Issue: "Credential not found" after GUI setup

**Cause:** GUI was using old key_id format (`webdav_{uuid}`)

**Fix:** Updated GUI to use same format as CLI (`webdav:password:{user}@{host}`)

### Issue: GUI and CLI configs conflict

**Cause:** Different config structures

**Fix:** Standardized config structure - both save same fields

### Issue: Storage manager rejects GUI config

**Cause:** Missing `stored_in` field in GUI config

**Fix:** GUI now saves `stored_in` field

### Issue: Adding dataset says "Run auth setup" after GUI wizard

**Cause:** Storage manager couldn't find credential due to:
  - Wrong key_id format
  - Missing `stored_in` field
  - Credential not in keyring

**Fix:** All above issues resolved

## Testing

### Unit Tests

Location: `tests/unit/test_auth_integration.py`

**Test coverage:**
- GUI wizard saves correct format
- CLI saves correct format
- Key ID format matches between GUI and CLI
- Storage manager accepts GUI config
- Storage manager accepts CLI config
- Dataset creation works with GUI auth
- Dataset creation works with CLI auth

**Run tests:**
```bash
pytest tests/unit/test_auth_integration.py -v
```

### Manual Tests

1. **GUI Auth Setup:**
   ```bash
   hei-datahub  # Open TUI
   # Press 's' for Settings
   # Run Auth Wizard
   # Try adding dataset (press 'a')
   ```

2. **CLI Auth Setup:**
   ```bash
   hei-datahub auth setup
   hei-datahub auth status
   hei-datahub auth doctor
   hei-datahub  # Open TUI and try adding dataset
   ```

3. **Verify Compatibility:**
   ```bash
   # Setup with GUI
   hei-datahub  # Run wizard

   # Verify with CLI
   hei-datahub auth status  # Should show config

   # Or vice versa
   hei-datahub auth setup  # CLI setup
   hei-datahub  # GUI should work
   ```

## Maintenance Guidelines

### When Adding New Auth Features

1. **Update both GUI and CLI** to maintain compatibility
2. **Keep config structure consistent** between both
3. **Update storage_manager** if adding new config fields
4. **Add tests** for new functionality
5. **Update documentation** (this file and user-facing docs)

### When Modifying Key ID Format

⚠️ **WARNING:** Changing key_id format breaks existing installations!

If you must change it:
1. Add migration logic to storage_manager
2. Support both old and new formats
3. Provide migration tool/script
4. Update all docs
5. Add prominent migration guide

### When Adding New Storage Backends

1. Create new class inheriting from `AuthStore`
2. Implement: `store_secret()`, `load_secret()`, `available()`, `strategy`
3. Update `get_auth_store()` to support new backend
4. Add CLI flag: `--store {keyring,env,new_backend}`
5. Test with both GUI and CLI
6. Update docs

### Code Style

**Credential handling:**
- ✅ Use `store.store_secret(key_id, password)`
- ❌ Never `print(password)` or log credentials
- ✅ Use `redact(password)` for debug logging
- ❌ Never store credentials in config file
- ✅ Clear credentials from memory after use

**Error messages:**
- ✅ Be specific: "Credential not found. Run: hei-datahub auth setup"
- ❌ Avoid generic: "Authentication failed"
- ✅ Provide actionable next steps
- ✅ Include relevant config file paths

**Config file handling:**
- ✅ Use `tomli` for reading (built-in tomllib on Python 3.11+)
- ✅ Use `tomli_w` for writing
- ✅ Create parent directories: `config_path.parent.mkdir(parents=True, exist_ok=True)`
- ✅ Handle missing config gracefully

## Security Considerations

### Credential Storage

**Linux keyring (preferred):**
- Encrypted by OS
- Accessible only to user
- Survives reboots
- Protected by user's login session

**Environment variables (fallback):**
- Stored in shell profile (~/.bashrc, ~/.zshrc)
- Readable by user and processes
- Less secure than keyring
- Only use if keyring unavailable

### Transport Security

- ✅ Always HTTPS for WebDAV
- ❌ Reject HTTP connections
- ✅ Verify SSL certificates
- ✅ Use Basic Auth over TLS only

### Validation

- ✅ Validate credentials before saving
- ✅ Test connection with PROPFIND request
- ✅ Handle authentication errors gracefully
- ✅ Don't expose credentials in error messages

## Future Enhancements

Potential improvements (not yet implemented):

- [ ] Support for OAuth2 authentication
- [ ] Multi-server profile support
- [ ] Credential rotation/expiry warnings
- [ ] Integration with OS credential managers (GNOME Keyring, KWallet)
- [ ] Token-based auth support (separate from password)
- [ ] Encrypted config file option
- [ ] Auth session management

## References

- CLI Auth Commands: `/src/hei_datahub/cli/auth/`
- GUI Auth Wizard: `/src/hei_datahub/ui/widgets/settings_wizard.py`
- Storage Manager: `/src/hei_datahub/services/storage_manager.py`
- Tests: `/tests/unit/test_auth_integration.py`
- User Docs: `/docs/installation/auth-setup-linux.md`
- Migration Guide: `/DEV/0.60-beta/AUTH_MIGRATION_GUIDE.md`

## Questions?

For questions about the authentication system:

1. Read this document first
2. Check the code references above
3. Review existing tests for examples
4. Ask in team communication channel
5. Create an issue if you find bugs

---

**Last updated:** December 2025 (v0.60-beta auth fix)
**Maintainer:** Backend Team
