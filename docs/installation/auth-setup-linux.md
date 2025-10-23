# WebDAV Authentication Setup (Linux Only)

**Requirements:** Hei-DataHub 0.59-beta or later, Linux only

Learn how to securely configure WebDAV authentication for Hei-Box or any WebDAV endpoint using the Linux keyring (Secret Service).

---

## Overview

The `hei-datahub auth setup` command provides an interactive wizard to configure WebDAV credentials:

✅ **Secure storage** - Uses Linux keyring (Secret Service), never writes secrets to disk
✅ **Multiple auth methods** - Supports both token and password authentication
✅ **ENV fallback** - Falls back to environment variables if keyring unavailable
✅ **Credential validation** - Tests credentials before storing
✅ **Non-interactive mode** - Supports scripting and automation

---

## Requirements

### Linux Keyring (Secret Service)

For secure storage, you need a Secret Service implementation running:

**Arch Linux:**
```bash
sudo pacman -S gnome-keyring libsecret python-keyring python-secretstorage
```

**Debian/Ubuntu:**
```bash
sudo apt install gnome-keyring libsecret-1-0 python3-keyring python3-secretstorage dbus-user-session
```

**Fedora:**
```bash
sudo dnf install gnome-keyring libsecret python3-keyring python3-secretstorage dbus-daemon
```

### Start Keyring Daemon

Ensure the keyring daemon is running in your session:

```bash
# Check if running
ps aux | grep gnome-keyring

# Start manually if needed (usually automatic in desktop environments)
gnome-keyring-daemon --start --components=secrets
```

**Note:** Most desktop environments (GNOME, KDE, XFCE) start the keyring automatically.

---

## Quick Start: Interactive Setup

### 1. Run the Setup Wizard

```bash
hei-datahub auth setup
```

Or use the alias:

```bash
hei-datahub setup
```

### 2. Follow the Prompts

**Example session:**

```
$ hei-datahub auth setup
🔐 Hei-DataHub WebDAV Authentication Setup (Linux)

WebDAV URL [https://heibox.uni-heidelberg.de/seafdav]:
Do you have a WebDAV token? [Y/n]: y
Username (optional): alice
Token: ********
Validating...
✅ WebDAV credentials verified and stored securely in your Linux keyring.
URL: https://heibox.uni-heidelberg.de/seafdav · Method: token · User: alice · Storage: keyring · Key: webdav:token:alice@heibox.uni-heidelberg.de
Next: run `hei-datahub auth status` or start using WebDAV operations.
```

### 3. Verify Configuration

```bash
hei-datahub auth status
```

**Output:**

```
🔐 WebDAV Authentication Status

Method:     token
URL:        https://heibox.uni-heidelberg.de/seafdav
Username:   alice
Storage:    keyring
Key ID:     webdav:token:alice@heibox.uni-heidelberg.de

Config:     /home/alice/.config/hei-datahub/config.toml
```

---

## Authentication Methods

### Token-Based (Recommended)

Best for services like Seafile/Heibox that support API tokens:

```bash
hei-datahub auth setup
```

When prompted:
- **Do you have a WebDAV token?** → `y`
- **Username** → (optional, can leave empty)
- **Token** → Paste your token (hidden)

**How to get a Heibox token:**
1. Log in to [heibox.uni-heidelberg.de](https://heibox.uni-heidelberg.de)
2. Click your avatar → Settings
3. Generate a new API token
4. Copy the token

### Password-Based

For standard WebDAV servers requiring username/password:

```bash
hei-datahub auth setup
```

When prompted:
- **Do you have a WebDAV token?** → `n`
- **Username** → Your username (required)
- **Password** → Your password (hidden)

---

## Non-Interactive Mode

For scripts and automation:

### Token Auth

```bash
hei-datahub auth setup \
  --url https://heibox.uni-heidelberg.de/seafdav \
  --username alice \
  --token "$SEAFILE_TOKEN" \
  --non-interactive --overwrite
```

### Password Auth

```bash
hei-datahub auth setup \
  --url https://example.com/webdav \
  --username bob \
  --password "$WEBDAV_PASSWORD" \
  --non-interactive --overwrite
```

### Skip Validation (Fast Setup)

```bash
hei-datahub auth setup \
  --url https://heibox.uni-heidelberg.de/seafdav \
  --token "$TOKEN" \
  --no-validate \
  --non-interactive --overwrite
```

**Warning:** `--no-validate` skips credential testing. Use only if you're confident the credentials are correct.

---

## Environment Variable Fallback

If the Linux keyring is unavailable, the wizard offers an ENV fallback:

```
⚠️  Linux keyring backend unavailable.
    Falling back to environment variables (less secure).
    Continue with ENV storage? [y/N]: y

✅ Credentials stored in env.

📋 Add these to your shell profile (~/.bashrc or ~/.zshrc):
  export HEIDATAHUB_WEBDAV_TOKEN='your-token-here'
  export HEIDATAHUB_WEBDAV_URL='https://heibox.uni-heidelberg.de/seafdav'
  export HEIDATAHUB_WEBDAV_USERNAME='alice'
```

**To make ENV storage permanent:**

1. Add exports to `~/.bashrc` or `~/.zshrc`:
   ```bash
   echo "export HEIDATAHUB_WEBDAV_TOKEN='your-token'" >> ~/.bashrc
   echo "export HEIDATAHUB_WEBDAV_URL='https://heibox.uni-heidelberg.de/seafdav'" >> ~/.bashrc
   echo "export HEIDATAHUB_WEBDAV_USERNAME='alice'" >> ~/.bashrc
   ```

2. Reload shell:
   ```bash
   source ~/.bashrc
   ```

---

## Configuration File

**Location:** `~/.config/hei-datahub/config.toml`

**Format (secrets NOT included):**

```toml
[auth]
method = "token"        # or "password"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "alice"      # optional for token method
key_id = "webdav:token:alice@heibox.uni-heidelberg.de"
stored_in = "keyring"   # or "env"
```

**Security:** Secrets are NEVER written to this file. They're stored in the keyring or ENV.

---

## Updating Configuration

### Re-run Setup (Overwrite)

```bash
hei-datahub auth setup --overwrite
```

### Test Existing Config

```bash
hei-datahub auth setup
# Choose [T]est when prompted
```

Or directly:

```bash
# Test by checking status
hei-datahub auth status
```

---

## Troubleshooting

### "Keyring backend unavailable"

**Symptoms:**
```
⚠️  Linux keyring backend unavailable.
    Falling back to environment variables (less secure).
```

**Causes & Fixes:**

1. **Keyring daemon not running:**
   ```bash
   # Check if running
   ps aux | grep gnome-keyring

   # Start it
   gnome-keyring-daemon --start --components=secrets

   # Add to session startup if needed
   ```

2. **Missing dependencies:**
   ```bash
   # Arch
   sudo pacman -S python-keyring python-secretstorage libsecret

   # Debian/Ubuntu
   sudo apt install python3-keyring python3-secretstorage libsecret-1-0

   # Fedora
   sudo dnf install python3-keyring python3-secretstorage libsecret
   ```

3. **D-Bus session not available:**
   ```bash
   # Check D-Bus
   echo $DBUS_SESSION_BUS_ADDRESS

   # If empty, start session bus
   eval $(dbus-launch --sh-syntax)
   ```

4. **No desktop environment:**
   - Keyring requires a desktop session or explicit daemon
   - Use ENV fallback for headless servers

### "Validation failed: Invalid credentials"

**Checks:**

1. **Token expired?** Generate a new token from Heibox
2. **Wrong URL?** Check the WebDAV endpoint: `https://heibox.uni-heidelberg.de/seafdav`
3. **Username required?** Some servers need username even with token
4. **Test manually:**
   ```bash
   curl -u "username:token" https://heibox.uni-heidelberg.de/seafdav/
   ```

### "Request timed out"

**Fixes:**

1. **Increase timeout:**
   ```bash
   hei-datahub auth setup --timeout 15
   ```

2. **Check connectivity:**
   ```bash
   ping heibox.uni-heidelberg.de
   curl -I https://heibox.uni-heidelberg.de
   ```

3. **Proxy settings:**
   ```bash
   export https_proxy=http://proxy:port
   hei-datahub auth setup
   ```

### "TLS/SSL error"

**Fixes:**

1. **Update CA certificates:**
   ```bash
   # Arch
   sudo pacman -S ca-certificates
   sudo trust extract-compat

   # Debian/Ubuntu
   sudo apt update && sudo apt install ca-certificates
   sudo update-ca-certificates

   # Fedora
   sudo dnf install ca-certificates
   sudo update-ca-trust
   ```

2. **Check system time:**
   ```bash
   timedatectl status
   # Fix if incorrect:
   sudo timedatectl set-ntp true
   ```

### "Config already exists"

**Options:**

1. **Overwrite:**
   ```bash
   hei-datahub auth setup --overwrite
   ```

2. **Test existing:**
   ```bash
   hei-datahub auth setup
   # Choose [T]est
   ```

3. **Manual edit:**
   ```bash
   nano ~/.config/hei-datahub/config.toml
   ```

---

## Advanced Usage

### Force Storage Backend

**Use keyring (fail if unavailable):**
```bash
hei-datahub auth setup --store keyring
```

**Use ENV (skip keyring check):**
```bash
hei-datahub auth setup --store env
```

### Custom Timeout

```bash
hei-datahub auth setup --timeout 15
```

### Skip Validation (Fast)

```bash
hei-datahub auth setup --no-validate
```

**Use case:** You're confident credentials are correct and want fast setup.

---

## Security Best Practices

### ✅ DO

- Use token authentication when possible
- Let the wizard use keyring storage
- Rotate tokens regularly (e.g., every 90 days)
- Use tokens with minimal required permissions
- Lock your desktop when away

### ❌ DON'T

- Don't share tokens or passwords
- Don't store tokens in git repos or scripts
- Don't use `--no-validate` in production setups
- Don't bypass keyring unless necessary

---

## Integration with Hei-DataHub

Once configured, Hei-DataHub automatically uses the stored credentials for:

- **Loading datasets** from cloud storage
- **Adding datasets** to cloud (via TUI)
- **Searching** cloud-hosted datasets
- **Downloading** dataset metadata

**Example workflow:**

```bash
# 1. Setup auth
hei-datahub auth setup

# 2. Configure cloud storage in TUI settings
hei-datahub
# Press 'S' → Configure storage backend → webdav

# 3. Browse cloud datasets
# Main screen now shows datasets from Heibox!

# 4. Add new dataset (press 'a')
# Automatically uploads to Heibox
```

---

## Exit Codes

- **0** - Success
- **1** - Validation failure or user abort
- **2** - Usage error (invalid arguments)

**Example script usage:**

```bash
#!/bin/bash
if hei-datahub auth setup --non-interactive --token "$TOKEN" --overwrite; then
    echo "Auth configured successfully"
    hei-datahub
else
    echo "Auth setup failed" >&2
    exit 1
fi
```

---

## Keyring Technical Details

### Storage Format

**Service:** `hei-datahub`
**Key ID:** `webdav:{method}:{username}@{host}`
**Examples:**
- `webdav:token:alice@heibox.uni-heidelberg.de`
- `webdav:password:bob@example.com`
- `webdav:token:-@heibox.uni-heidelberg.de` (no username)

### Backends

The `keyring` library tries these backends in order:

1. **SecretService** (GNOME Keyring, KWallet) - Preferred
2. **kwallet** - KDE Plasma
3. **fail** - No backend available → ENV fallback

### Access Secrets Manually

```python
import keyring
token = keyring.get_password("hei-datahub", "webdav:token:alice@heibox.uni-heidelberg.de")
print(token)
```

---

## Related Commands

- `hei-datahub auth status` - Show current configuration
- `hei-datahub doctor` - Diagnose installation issues
- `hei-datahub paths` - Show config file locations

---

## Summary

**Interactive setup:**
```bash
hei-datahub auth setup
```

**Non-interactive with token:**
```bash
hei-datahub auth setup \
  --url https://heibox.uni-heidelberg.de/seafdav \
  --token "$TOKEN" \
  --non-interactive --overwrite
```

**Check status:**
```bash
hei-datahub auth status
```

**Troubleshoot keyring:**
```bash
# Ensure daemon running
gnome-keyring-daemon --start --components=secrets

# Test keyring
python3 -c "import keyring; print(keyring.get_keyring())"
```

Now you can securely manage WebDAV credentials and collaborate using cloud storage! 🔐
