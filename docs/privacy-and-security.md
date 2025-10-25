# Privacy and Security

**Last updated:** October 25, 2025
**Version:** 0.59-beta "Privacy"

This document explains how Hei-DataHub handles your credentials, data, and privacy.

---

## Table of Contents

- [Security Model](#security-model)
- [Credential Storage](#credential-storage)
- [Data Storage](#data-storage)
- [Network Communication](#network-communication)
- [Privacy Considerations](#privacy-considerations)
- [Threat Model](#threat-model)
- [Best Practices](#best-practices)
- [Security Checklist](#security-checklist)

---

## Security Model

### Design Principles

Hei-DataHub follows these security principles:

1. **Local-first:** All operations work offline; data stays on your machine
2. **No plaintext secrets:** Credentials never stored in plaintext
3. **Minimal network:** Network calls only when explicitly syncing
4. **User control:** You decide what gets uploaded and when
5. **Standard protocols:** Uses established security libraries and protocols

### What Hei-DataHub Does NOT Do

❌ **Never** sends credentials over unencrypted connections
❌ **Never** stores passwords in config files
❌ **Never** logs sensitive information
❌ **Never** shares data without explicit user action

---

## Credential Storage

### WebDAV Authentication (v0.59+)

#### Linux Keyring (Recommended)

**Where credentials are stored:**
```
Linux Secret Service (D-Bus)
├── GNOME Keyring (gnome-keyring-daemon)
├── KDE Wallet (kwalletd)
└── Other Secret Service implementations
```

**Technical details:**
- Service name: `hei-datahub`
- Key format: `webdav:{method}:{username}@{host}`
- Example: `webdav:token:alice@heibox.uni-heidelberg.de`
- Encryption: Handled by keyring backend (typically AES-256)
- Access: Requires user session unlock

**Security properties:**
✅ Encrypted at rest
✅ Per-user isolation
✅ Protected by session password
✅ No file-based storage
✅ Automatic cleanup on logout

**How to verify:**
```bash
# Check stored credentials
secret-tool search service hei-datahub

# View keyring status
hei-datahub auth status
```

#### Environment Variables (Fallback)

If Linux keyring is unavailable, Hei-DataHub can use environment variables:

**Variables:**
- `HEIDATAHUB_WEBDAV_TOKEN` - Seafile/Heibox API token
- `HEIDATAHUB_WEBDAV_PASSWORD` - WebDAV password
- `HEIDATAHUB_WEBDAV_URL` - WebDAV server URL
- `HEIDATAHUB_WEBDAV_USERNAME` - Username

**⚠️ Security warning:**
- Environment variables are **not encrypted**
- Visible to all processes running as your user
- May appear in shell history
- Persisted in `~/.bashrc` or `~/.zshrc`

**Best practices when using ENV:**
```bash
# Store in a separate file with restricted permissions
echo 'export HEIDATAHUB_WEBDAV_TOKEN="your-token"' > ~/.heidatahub-env
chmod 600 ~/.heidatahub-env
source ~/.heidatahub-env

# Or use one-time export (not persistent)
export HEIDATAHUB_WEBDAV_TOKEN="your-token"
hei-datahub
```

### GitHub Personal Access Tokens

**Storage location:** Not stored by Hei-DataHub

GitHub tokens are used only for:
1. Installing from private repository (`uv tool install`)
2. Creating pull requests (user manages via Git)

**You manage tokens yourself:**
- Store in Git credential helper
- Or pass via environment variable
- Or use SSH keys (recommended)

**Hei-DataHub never:**
- Stores GitHub tokens
- Requests GitHub credentials
- Accesses GitHub token files

---

## Data Storage

### Local Data (Default)

**Location:** `~/.local/share/Hei-DataHub/data/` (Linux)

**What's stored:**
```
~/.local/share/Hei-DataHub/
├── data/
│   └── <dataset-id>/
│       ├── metadata.yaml          # Dataset metadata
│       └── [data files]           # Optional: actual datasets
├── config/
│   └── config.toml               # Non-secret config only
└── db.sqlite                     # Local search index
```

**File permissions:**
- Default: `0644` (readable by user, group, world)
- Recommended: `chmod 700 ~/.local/share/Hei-DataHub`

**Security:**
- No encryption at rest (relies on filesystem encryption)
- Standard file permissions apply
- Sensitive data should use disk encryption (LUKS, etc.)

### Cloud Data (WebDAV/Heibox)

**Location:** Your institutional cloud storage (e.g., Heibox/Seafile)

**What's uploaded:**
- Dataset metadata (`metadata.yaml` files)
- Optional: Actual data files (if you choose to upload)

**Transport security:**
- All WebDAV connections use **HTTPS** (TLS 1.2+)
- Server certificate validation enabled
- No plaintext HTTP allowed

**Access control:**
- Managed by your cloud provider (Seafile/Heibox)
- You control who has read/write access
- Team members need their own credentials

### Search Index Cache

**Location:** `~/.cache/hei-datahub/index.db` (Linux)

**What's cached:**
- Dataset names, descriptions, tags
- Project names and metadata
- File paths and ETags
- Search index (SQLite FTS5)

**Privacy notes:**
- Contains dataset metadata (not actual data)
- No credentials stored
- Can be safely deleted (rebuilds automatically)
- Not encrypted

**Clear cache:**
```bash
rm -rf ~/.cache/hei-datahub/
hei-datahub  # Rebuilds automatically
```

### Configuration Files

**Location:** `~/.config/hei-datahub/config.toml` (Linux)

**What's stored:**
```toml
[auth]
method = "token"  # or "password"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "alice"
key_id = "webdav:token:alice@heibox.uni-heidelberg.de"
stored_in = "keyring"  # or "env"

[preferences]
theme = "monokai"
# ... other non-secret settings
```

**Security:**
✅ **No passwords or tokens**
✅ Only references to keyring entries
✅ Safe to commit to Git (user-specific)
⚠️ Contains username and server URL

---

## Network Communication

### When Network Calls Happen

Hei-DataHub is **local-first** and only makes network calls when:

1. **WebDAV sync** (background, every 15 minutes)
   - PROPFIND requests to list remote datasets
   - ETag comparisons for changed files
   - PUT requests to upload new/changed datasets

2. **User actions**
   - Uploading a dataset to cloud (`Ctrl+S` in TUI)
   - Running `hei-datahub auth doctor` (connection test)
   - Creating a GitHub Pull Request

3. **Installation/updates**
   - Downloading package from GitHub (via `uv`)
   - Not managed by Hei-DataHub itself

### Network Security

**All WebDAV communication:**
- Protocol: HTTPS only (TLS 1.2+)
- Authentication: HTTP Basic Auth over TLS
- Headers: User-Agent includes version
- Timeout: 8 seconds default

**Certificate validation:**
```python
# Certificate verification is ENABLED
requests.get(url, auth=auth, verify=True)  # verify=True is default
```

**No network calls during:**
- Searching datasets (`/` in TUI)
- Browsing local datasets
- Editing metadata locally
- Application startup

---

## Privacy Considerations

### What Data Leaves Your Machine

**Sent to Cloud (WebDAV) when you upload:**
- Dataset metadata YAML files
- Actual data files (if you choose to upload)
- HTTP headers: User-Agent, Date, Content-Type

**Never sent anywhere:**
- Credentials (stay in keyring)
- Search queries (local-only)
- User preferences
- Keystrokes or usage patterns

### Metadata in Requests

**HTTP User-Agent:**
```
python-requests/2.31.0 (indicates HTTP client library)
```

**WebDAV headers:**
```http
Depth: 0                    # PROPFIND depth
Content-Type: text/plain    # File type
If-Match: <etag>           # For updates
```

### Logging

**What's logged:**
- Application startup/shutdown
- Errors and warnings
- WebDAV request URLs (no credentials)
- Index rebuild events

**Location:** `~/.local/share/Hei-DataHub/logs/` or `stdout`

**Not logged:**
- Passwords or tokens
- Request/response bodies
- Dataset content
- Search queries

**Example safe log entry:**
```
2025-10-25 10:30:15 INFO Uploading to https://heibox.uni-heidelberg.de/seafdav/library/dataset-1/
2025-10-25 10:30:16 INFO Upload successful (HTTP 201)
```

### Third-Party Dependencies

Hei-DataHub uses these security-relevant libraries:

| Library | Purpose | Trust Level |
|---------|---------|-------------|
| `keyring` | Credential storage | ⭐⭐⭐ Python core ecosystem |
| `requests` | HTTP client | ⭐⭐⭐ Industry standard |
| `cryptography` | (via keyring) | ⭐⭐⭐ Audited, widely used |
| `secretstorage` | D-Bus Secret Service | ⭐⭐⭐ Linux standard |

**Dependency verification:**
```bash
# View installed packages
uv pip list

# Check for vulnerabilities (requires safety)
pip install safety
safety check
```

---

## Threat Model

### Threats We Protect Against

✅ **Credential theft from disk**
- Credentials encrypted in keyring
- Config files contain no secrets

✅ **Credential theft from logs**
- Credentials redacted in all logs
- Only last 4 chars shown in diagnostics

✅ **Man-in-the-middle attacks**
- TLS required for all WebDAV
- Certificate validation enabled

✅ **Accidental credential commits**
- Credentials never in Git-tracked files
- Config files safe to commit

### Threats We Do NOT Protect Against

❌ **Malicious admin on cloud server**
- Cloud provider can see uploaded data
- Use end-to-end encryption if needed

❌ **Compromised keyring**
- If attacker has session access, keyring is accessible
- Use disk encryption + strong session password

❌ **Malicious Python packages**
- Dependencies could theoretically access keyring
- Use virtual environments, review dependencies

❌ **Physical access to unlocked machine**
- Keyring is unlocked during session
- Lock your screen when away

❌ **Network traffic analysis**
- TLS hides content, not metadata (URLs, timing)
- Use VPN if needed

---

## Best Practices

### For Maximum Security

1. **Use Linux Keyring (not ENV variables)**
   ```bash
   hei-datahub auth setup  # Choose keyring when prompted
   ```

2. **Enable disk encryption**
   ```bash
   # LUKS full disk encryption (during OS install)
   # or per-directory encryption
   ```

3. **Use API tokens (not passwords)**
   - Tokens can be revoked without changing password
   - Easier to rotate
   - Can have limited scope

4. **Set restrictive file permissions**
   ```bash
   chmod 700 ~/.local/share/Hei-DataHub
   chmod 700 ~/.config/hei-datahub
   chmod 600 ~/.config/hei-datahub/config.toml
   ```

5. **Regularly audit credentials**
   ```bash
   hei-datahub auth status  # Check what's configured
   hei-datahub auth doctor  # Test connections
   ```

6. **Use SSH keys for GitHub (not PAT)**
   ```bash
   uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
   ```

7. **Clear credentials when done**
   ```bash
   hei-datahub auth clear --force --all
   ```

### For Shared/Untrusted Machines

⚠️ **Not recommended!** But if you must:

1. **Use environment variables (not keyring)**
   ```bash
   export HEIDATAHUB_WEBDAV_TOKEN="..."
   hei-datahub
   unset HEIDATAHUB_WEBDAV_TOKEN  # Clear immediately after
   ```

2. **Use custom data directory**
   ```bash
   hei-datahub --data-dir /tmp/heidatahub-temp
   rm -rf /tmp/heidatahub-temp  # Delete after use
   ```

3. **Never save credentials**
   - Don't use `hei-datahub auth setup`
   - Pass credentials via ENV each time

4. **Clear history**
   ```bash
   history -c  # Clear shell history
   ```

---

## Security Checklist

### Installation

- [ ] Installed via official repository (`git+ssh://git@github.com/0xpix/Hei-DataHub`)
- [ ] Using SSH keys (not HTTPS + PAT) for GitHub
- [ ] Verified installation: `hei-datahub doctor`

### Configuration

- [ ] Used `hei-datahub auth setup` (interactive wizard)
- [ ] Chose keyring storage (not ENV variables)
- [ ] Used API token (not password)
- [ ] Tested connection: `hei-datahub auth doctor`
- [ ] Verified config has no secrets: `cat ~/.config/hei-datahub/config.toml`

### File Permissions

- [ ] Data directory: `chmod 700 ~/.local/share/Hei-DataHub`
- [ ] Config directory: `chmod 700 ~/.config/hei-datahub`
- [ ] Config file: `chmod 600 ~/.config/hei-datahub/config.toml`

### System Security

- [ ] Disk encryption enabled (LUKS or equivalent)
- [ ] Strong session password
- [ ] Auto-lock screen when idle
- [ ] Keyring unlocked only when logged in

### Regular Maintenance

- [ ] Review credentials monthly: `hei-datahub auth status`
- [ ] Check logs for errors: `tail -f ~/.local/share/Hei-DataHub/logs/hei-datahub.log`
- [ ] Update to latest version: `uv tool install --upgrade hei-datahub`
- [ ] Audit dependencies: `uv pip list`

### When Leaving Project

- [ ] Clear credentials: `hei-datahub auth clear --force --all`
- [ ] Delete data directory: `rm -rf ~/.local/share/Hei-DataHub`
- [ ] Delete config: `rm -rf ~/.config/hei-datahub`
- [ ] Delete cache: `rm -rf ~/.cache/hei-datahub`

---

## Getting Help

### Security Issues

**🔒 Found a security vulnerability?**

**DO NOT** open a public GitHub issue!

Instead:
1. Email maintainer privately: [security contact needed]
2. Include: description, steps to reproduce, impact
3. Allow 90 days for fix before public disclosure

### General Security Questions

- Check [WebDAV Setup Guide](installation/auth-setup-linux.md)
- Run diagnostics: `hei-datahub auth doctor`
- Ask in GitHub Discussions (for non-sensitive questions)

### Audit and Compliance

For institutional security audits, provide:
1. This document
2. List of dependencies: `uv pip list`
3. Source code: [GitHub repository]
4. Keyring documentation: [Secret Service API spec]

---

## Frequently Asked Questions

### Q: Are my credentials encrypted?

**A:** Yes, when using Linux keyring. The keyring encrypts credentials using your session password. ENV variables are not encrypted.

### Q: Can other users on the system access my credentials?

**A:** No, if using keyring. The keyring is per-user and requires your session to be unlocked. File permissions also prevent access.

### Q: What happens if I forget my session password?

**A:** You'll lose access to keyring credentials. You'll need to run `hei-datahub auth setup` again to reconfigure.

### Q: Does Hei-DataHub send telemetry?

**A:** No. Hei-DataHub never phones home or sends usage data.

### Q: Can my institution see what datasets I'm accessing?

**A:** If using WebDAV/Heibox, your institution can see:
- What datasets you upload/download
- When you access the server
- Your IP address

This is standard for any cloud service.

### Q: Is the search index encrypted?

**A:** No. The cache at `~/.cache/hei-datahub/` is not encrypted. Use disk encryption if this is a concern.

### Q: How do I completely remove all data?

**A:** Run these commands:
```bash
hei-datahub auth clear --force --all
rm -rf ~/.local/share/Hei-DataHub
rm -rf ~/.config/hei-datahub
rm -rf ~/.cache/hei-datahub
uv tool uninstall hei-datahub
```

### Q: What about Windows/macOS?

**A:** v0.59 only supports Linux keyring. Windows/macOS credential storage is planned for future releases.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.59-beta | 2025-10-25 | Initial privacy and security documentation |

---

**Questions or concerns?** Open an issue or discussion on GitHub.

**Built for teams who want to organize data securely without the overhead.**
