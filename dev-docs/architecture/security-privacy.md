# Security & Privacy

## Overview

Hei-DataHub is designed with **security and privacy as core principles**. This document explains how sensitive data is protected, how credentials are managed, and what privacy guarantees the application provides.

**Key Security Features:**

- 🔐 **OS Keyring Storage:** Credentials encrypted by the operating system
- 🔒 **HTTPS Required:** All WebDAV communication over TLS/SSL
- 🚫 **No Telemetry:** Zero data collection or analytics
- 🛡️ **Input Validation:** All user inputs sanitized and validated
- 📝 **Audit Logging:** Security events logged for review
- 🔑 **Credential Isolation:** Secrets never in code, configs, or logs

---

## Threat Model

### What We Protect Against

| Threat | Protection | Status |
|--------|-----------|--------|
| **Credential theft from config files** | Keyring storage, no credentials in TOML | ✅ Mitigated |
| **Man-in-the-middle (MITM) attacks** | HTTPS required for WebDAV | ✅ Mitigated |
| **SQL injection** | Parameterized queries only | ✅ Mitigated |
| **Path traversal** | Path sanitization and validation | ✅ Mitigated |
| **Credential logging** | Credentials masked in all logs | ✅ Mitigated |
| **Process snooping** | Credentials loaded only when needed | ⚠️ Partially mitigated |
| **Memory dumps** | Credentials cleared after use | ⚠️ Partially mitigated |
| **Malicious datasets** | Schema validation, content sanitization | ✅ Mitigated |

### What We Trust

- ✅ **Operating system keyring** (Linux Secret Service, Windows Credential Manager, macOS Keychain)
- ✅ **WebDAV server TLS certificates** (user must verify on first connect)
- ✅ **Python package ecosystem** (dependencies from PyPI)
- ✅ **User's local filesystem permissions**

### What We Don't Protect Against

- ❌ **Compromised operating system** (root/admin malware can access keyring)
- ❌ **Malicious WebDAV server** (user must trust their cloud provider)
- ❌ **Physical access attacks** (encrypted disk recommended)
- ❌ **Supply chain attacks** (dependency poisoning)

---

## Credential Management

### Storage Architecture

```mermaid
graph TD
    subgraph "User Input"
        Setup[auth setup wizard]
    end

    subgraph "Application"
        Validator[Auth Validator]
        CredService[Credential Service]
    end

    subgraph "OS Keyring"
        SecretService[Secret Service API]
        GNOME[GNOME Keyring]
        KDE[KDE Wallet]
    end

    subgraph "Filesystem"
        Config[config.toml<br/>NON-SENSITIVE ONLY]
    end

    subgraph "WebDAV Server"
        HeiBox[HeiBox/Seafile]
    end

    Setup -->|1. User enters credentials| Validator
    Validator -->|2. Test connection| HeiBox
    HeiBox -->|3. Validate| Validator
    Validator -->|4. Save to keyring| CredService
    CredService -->|5. Store encrypted| SecretService
    SecretService --> GNOME
    SecretService --> KDE
    CredService -->|6. Save metadata| Config

    style Config fill:#fff3cd
    style GNOME fill:#d4edda
    style KDE fill:#d4edda
```

### Credential Lifecycle

#### 1. **Setup Phase**

```python
# User enters credentials via interactive wizard
def run_setup_wizard():
    """
    Interactive setup - credentials never logged.
    """
    url = input("WebDAV URL: ")
    token = getpass.getpass("Token (hidden): ")  # Hidden input

    # Validate credentials (HTTPS required)
    if not validate_credentials(url, token):
        raise AuthError("Invalid credentials")

    # Store in keyring (encrypted by OS)
    key_id = derive_key_id("token", None, url)
    keyring.set_password(SERVICE_NAME, key_id, token)

    # Save metadata to config (NO credentials)
    save_config({
        "auth": {
            "method": "token",
            "url": url,
            "stored_in": "keyring",
            "key_id": key_id  # Reference only
        }
    })
```

**Security measures:**

- `getpass.getpass()` for hidden input (not echoed to terminal)
- Validation over HTTPS before storage
- Keyring encryption handled by OS
- Only metadata saved to config file

#### 2. **Usage Phase**

```python
def get_webdav_client():
    """
    Load credentials from keyring only when needed.
    """
    # Load config (contains NO credentials)
    config = load_config()
    auth_config = config["auth"]

    # Retrieve from keyring
    key_id = auth_config["key_id"]
    credential = keyring.get_password(SERVICE_NAME, key_id)

    if not credential:
        raise AuthError("Credentials not found in keyring")

    # Create WebDAV client
    client = WebDAVStorage(
        base_url=auth_config["url"],
        password=credential  # Only in memory during request
    )

    # Credential cleared when client object is destroyed
    return client
```

**Security measures:**

- Credentials loaded from keyring only when needed
- Never stored in global variables
- Cleared from memory when no longer needed
- No credentials logged or printed

#### 3. **Cleanup Phase**

```bash
# User clears credentials
hei-datahub auth clear
```

```python
def clear_credentials():
    """
    Remove all authentication data.
    """
    config = load_config()
    key_id = config["auth"]["key_id"]

    # Remove from keyring
    keyring.delete_password(SERVICE_NAME, key_id)

    # Remove config file
    config_path.unlink()

    # Remove search index (may contain sensitive metadata)
    db_path.unlink()
```

---

## Data Privacy

### What Data is Stored Where

| Data Type | Location | Encrypted | Shared with Server | Privacy Level |
|-----------|----------|-----------|-------------------|---------------|
| **WebDAV credentials** | OS keyring | ✅ Yes (OS-managed) | ❌ No | 🔴 Critical |
| **WebDAV URL** | `config.toml` | ❌ No | ❌ No | 🟡 Sensitive |
| **Dataset metadata** | Local cache, SQLite | ❌ No | ✅ Yes (on sync) | 🟢 Public |
| **Search queries** | Memory only | ❌ No | ❌ No | 🟡 Sensitive |
| **Search index** | SQLite FTS5 | ❌ No | ❌ No | 🟢 Public |
| **User settings** | `config.toml` | ❌ No | ❌ No | 🟢 Low |
| **Application logs** | `~/.cache/hei-datahub/logs/` | ❌ No | ❌ No | 🟡 Sensitive |

### No Telemetry Policy

Hei-DataHub **does not collect any telemetry or analytics data**:

- ❌ No usage statistics
- ❌ No crash reports
- ❌ No version checking (user-initiated only)
- ❌ No tracking pixels or beacons
- ❌ No network requests except WebDAV sync

**Exception:** Update checker (optional, user-initiated):

```python
def check_for_updates():
    """
    Check for new versions.

    Privacy: Only sends HTTP GET to version check endpoint.
    No user identification or tracking.
    """
    response = requests.get(
        get_update_check_url(),
        headers={"User-Agent": f"Hei-DataHub/{__version__}"}
    )
    # Only version comparison, no data sent
```

### Data Retention

| Data | Retention | Deletion |
|------|-----------|----------|
| **Credentials** | Until user runs `auth clear` | Immediate |
| **Search index** | Until user runs `auth clear` or `reindex` | Immediate |
| **Local cache** | Until manual deletion or `auth clear --all` | Manual |
| **Logs** | 7 days (auto-rotated) | Automatic |
| **Query history** | Session only (in-memory) | On app close |

---

## Network Security

### HTTPS Enforcement

WebDAV connections **must use HTTPS**:

```python
def validate_url(url: str) -> None:
    """
    Validate WebDAV URL for security.

    Raises:
        ValueError: If URL is not HTTPS
    """
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise ValueError(
            "WebDAV URL must use HTTPS for security. "
            f"Got: {parsed.scheme}://"
        )

    if not parsed.netloc:
        raise ValueError("Invalid WebDAV URL: missing hostname")
```

### TLS Certificate Validation

By default, TLS certificates are validated:

```python
session = requests.Session()
session.verify = True  # Enforce certificate validation

# User can disable for self-signed certs (not recommended)
# session.verify = False  # ⚠️ INSECURE - only for testing
```

**Best practice:** Use valid certificates from trusted CAs (Let's Encrypt, etc.)

### Network Timeouts

Prevent hanging connections:

```python
CONNECT_TIMEOUT = 5   # seconds
READ_TIMEOUT = 60     # seconds

response = session.request(
    method="GET",
    url=url,
    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
)
```

### Retry Strategy

Failed requests are retried with exponential backoff:

```python
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,                          # Max 3 retries
    backoff_factor=0.5,               # 0.5s, 1s, 2s delays
    status_forcelist=[500, 502, 503, 504],  # Retry on server errors
    allowed_methods=["HEAD", "GET", "OPTIONS", "PROPFIND"]  # Safe methods only
)
```

**Security note:** POST/PUT/DELETE are **not** automatically retried to prevent duplicate operations.

---

## Input Validation

### SQL Injection Prevention

**All database queries use parameterized statements:**

```python
# ✅ SAFE: Parameterized query
cursor.execute(
    "SELECT * FROM datasets_fts WHERE id = ?",
    (dataset_id,)
)

# ❌ UNSAFE: String concatenation (NEVER USED)
# cursor.execute(f"SELECT * FROM datasets_fts WHERE id = '{dataset_id}'")
```

### Path Traversal Prevention

**All file paths are validated and sanitized:**

```python
def validate_dataset_path(dataset_id: str) -> Path:
    """
    Validate dataset ID to prevent path traversal.

    Args:
        dataset_id: Dataset identifier

    Returns:
        Safe path within data directory

    Raises:
        ValueError: If dataset_id contains path traversal
    """
    # Reject path traversal attempts
    if ".." in dataset_id or "/" in dataset_id or "\\" in dataset_id:
        raise ValueError(f"Invalid dataset ID: {dataset_id}")

    # Ensure path is within DATA_DIR
    dataset_path = DATA_DIR / dataset_id
    if not dataset_path.resolve().is_relative_to(DATA_DIR.resolve()):
        raise ValueError(f"Path traversal detected: {dataset_id}")

    return dataset_path
```

### Schema Validation

**All dataset metadata is validated against JSON Schema:**

```python
from pydantic import BaseModel, Field, validator

class DatasetMetadata(BaseModel):
    """Dataset metadata with validation."""

    dataset_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    file_format: str = Field(..., pattern=r'^[a-z0-9\-]+$')  # Alphanumeric only
    source: str = Field(..., max_length=500)

    @validator('source')
    def validate_source(cls, v):
        """Validate source URL or name."""
        if v.startswith('http://') or v.startswith('https://'):
            # Validate URL
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError('Invalid URL')
        return v

    @validator('dataset_name')
    def sanitize_name(cls, v):
        """Sanitize dataset name."""
        # Remove control characters
        v = ''.join(c for c in v if c.isprintable())
        # Remove leading/trailing whitespace
        v = v.strip()
        return v
```

### XSS Prevention in Metadata

**All metadata is sanitized before display:**

```python
def sanitize_html(text: str) -> str:
    """
    Sanitize text to prevent XSS in terminal output.

    Args:
        text: Untrusted text from metadata

    Returns:
        Sanitized text safe for display
    """
    # Remove control characters (except newline/tab)
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')

    # Escape ANSI sequences that could manipulate terminal
    text = text.replace('\x1b', '')

    # Limit length to prevent terminal flooding
    if len(text) > 10000:
        text = text[:10000] + "... (truncated)"

    return text
```

---

## Logging Security

### Credential Masking

**Credentials are never logged:**

```python
def _mask_auth(url: str) -> str:
    """
    Mask authentication info in URLs for logging.

    Args:
        url: URL potentially containing credentials

    Returns:
        URL with credentials masked
    """
    parsed = urlparse(url)
    if parsed.username:
        # Replace username:password@ with ***:***@
        masked = url.replace(
            f"{parsed.username}:{parsed.password}@",
            "***:***@"
        )
        return masked
    return url

# Usage
logger.info(f"Connecting to {_mask_auth(webdav_url)}")
# Output: "Connecting to https://***:***@heibox.uni-heidelberg.de/seafdav"
```

### Sensitive Data Filtering

**Log messages are filtered for sensitive patterns:**

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from log messages."""

    PATTERNS = [
        (re.compile(r'token["\s:=]+([a-zA-Z0-9]+)', re.I), r'token=***'),
        (re.compile(r'password["\s:=]+([^\s"]+)', re.I), r'password=***'),
        (re.compile(r'key["\s:=]+([a-zA-Z0-9]+)', re.I), r'key=***'),
    ]

    def filter(self, record):
        """Filter log record."""
        message = record.getMessage()

        for pattern, replacement in self.PATTERNS:
            message = pattern.sub(replacement, message)

        record.msg = message
        return True

# Apply filter to all loggers
logger = logging.getLogger('hei_datahub')
logger.addFilter(SensitiveDataFilter())
```

### Log Rotation

**Logs are rotated to prevent disk space exhaustion:**

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    filename='~/.cache/hei-datahub/logs/app.log',
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=3                # Keep 3 old files
)
```

---

## Secure Coding Practices

### 1. **Least Privilege Principle**

- Application runs with user privileges (no root/admin required)
- File permissions: `0600` for config, `0700` for directories
- Database files: `0600` (readable only by owner)

```python
def create_config_file(path: Path, content: str) -> None:
    """
    Create config file with restrictive permissions.
    """
    # Write file
    path.write_text(content)

    # Set permissions: owner read/write only
    path.chmod(0o600)
```

### 2. **Defense in Depth**

Multiple layers of security:

```
Layer 1: Input Validation (Pydantic schemas)
    ↓
Layer 2: SQL Parameterization (no injection)
    ↓
Layer 3: Path Sanitization (no traversal)
    ↓
Layer 4: HTTPS Enforcement (no MITM)
    ↓
Layer 5: Keyring Encryption (OS-managed)
```

### 3. **Fail Securely**

Errors don't leak sensitive information:

```python
try:
    client = get_webdav_client()
    client.connect()
except AuthError as e:
    # ❌ BAD: Leaks credentials
    # logger.error(f"Auth failed with token: {token}")

    # ✅ GOOD: Generic error message
    logger.error("Authentication failed")
    raise AuthError("Invalid credentials") from e
```

### 4. **Secure Defaults**

```python
# Default configuration emphasizes security
DEFAULT_CONFIG = {
    "auth": {
        "stored_in": "keyring",      # Not "env"
        "verify_ssl": True,           # Not False
    },
    "network": {
        "timeout": 30,                # Prevent hanging
        "max_retries": 3,             # Limit retry attempts
    },
    "logging": {
        "level": "INFO",              # Not "DEBUG" (avoid verbose logs)
        "mask_credentials": True,     # Always mask
    }
}
```

---

## Security Auditing

### Audit Events

Security-relevant events are logged:

```python
def log_security_event(event_type: str, details: dict) -> None:
    """
    Log security event for audit trail.

    Args:
        event_type: Type of security event
        details: Event details (credentials masked)
    """
    logger.warning(
        f"SECURITY_EVENT: {event_type}",
        extra={
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
    )

# Usage examples
log_security_event("AUTH_SETUP", {"url": _mask_auth(url)})
log_security_event("AUTH_CLEAR", {"key_id": key_id})
log_security_event("AUTH_FAILURE", {"url": _mask_auth(url), "error": "401"})
log_security_event("INDEX_REBUILD", {"count": dataset_count})
```

### Security Checklist for Developers

When adding new features:

- [ ] Credentials never logged or printed
- [ ] URLs masked before logging
- [ ] All SQL queries parameterized
- [ ] All file paths validated (no `..` or absolute paths)
- [ ] All user inputs validated with Pydantic
- [ ] HTTPS enforced for network requests
- [ ] Sensitive data cleared from memory after use
- [ ] Error messages don't leak sensitive info
- [ ] File permissions set correctly (0600 for sensitive files)
- [ ] Audit events logged for security-relevant operations

---

## Vulnerability Disclosure

### Reporting Security Issues

**Do NOT report security vulnerabilities via public GitHub issues.**

Instead:

1. Email: `security@hei-datahub.example.com` (if available)
2. Or: Create a private security advisory on GitHub
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 7 days
- **Fix:** Within 30 days (critical issues prioritized)
- **Disclosure:** After fix is released and users have time to update

---

## Compliance & Standards

### GDPR Compliance (if applicable)

- ✅ **Data minimization:** Only essential data collected
- ✅ **User control:** Users can delete all data (`auth clear --all`)
- ✅ **No tracking:** No analytics or telemetry
- ✅ **Transparent:** This document explains all data storage

### Security Standards

| Standard | Compliance |
|----------|------------|
| **OWASP Top 10** | Addressed (SQL injection, XSS, sensitive data exposure) |
| **CWE Top 25** | Mitigated (path traversal, injection, auth issues) |
| **NIST Guidelines** | Followed (least privilege, defense in depth) |

---

## Best Practices for Users

### For Maximum Security

1. ✅ **Use keyring storage** (default on Linux)
2. ✅ **Use token auth** instead of password
3. ✅ **Enable full disk encryption** (LUKS, BitLocker, FileVault)
4. ✅ **Use strong WebDAV tokens** (generate via HeiBox web interface)
5. ✅ **Rotate tokens regularly** (every 6 months)
6. ✅ **Verify HTTPS certificates** on first connect
7. ✅ **Keep system updated** (OS, Python, Hei-DataHub)
8. ✅ **Use VPN on untrusted networks** (public WiFi)

### Red Flags

If you see any of these, report immediately:

- ⚠️ Application asks for credentials outside of `auth setup`
- ⚠️ Credentials visible in config files
- ⚠️ Network requests to unknown domains
- ⚠️ Errors that expose full credentials
- ⚠️ Unexpected file modifications outside `~/.config`, `~/.cache`, `~/.local/share`

---

## Security Roadmap

### Planned Enhancements (v0.60+)

- [ ] **Two-factor authentication** for WebDAV (if supported by server)
- [ ] **Encrypted local cache** (optional, user-configurable)
- [ ] **Security audit logs** (separate from app logs)
- [ ] **Certificate pinning** for HeiBox servers
- [ ] **Secure memory wiping** for credentials
- [ ] **Sandboxing** for dataset operations
- [ ] **Code signing** for releases

---

## Related Documentation

- **[Authentication & Sync](auth-and-sync.md)** - Credential management details
- **[Architecture Overview](overview.md)** - System design security boundaries
- **[Search & Autocomplete](search-and-autocomplete.md)** - Search data privacy
- **[CLI Commands Reference](../api-reference/cli-commands.md)** - Auth commands

---

## Security Contact

- **GitHub Security Advisories:** [Create private advisory](https://github.com/0xpix/Hei-DataHub/security/advisories)
- **Issues:** For non-security bugs only
- **Documentation:** This file and linked references

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"

**Security Commitment:** Hei-DataHub prioritizes user privacy and data security. We follow industry best practices and welcome security researchers to help us improve.
