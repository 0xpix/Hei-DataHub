# Configure Heibox Integration

**Requirements:** Hei-DataHub 0.59-beta or later, Linux

Learn how to set up Heibox/Seafile WebDAV integration for cloud-based dataset collaboration in Hei-DataHub. This guide covers creating authentication credentials, configuring WebDAV access, and understanding all available options.

---

## Overview

Hei-DataHub connects directly to your institutional Heibox/Seafile storage via WebDAV, enabling:

- **Instant cloud sync** - Datasets uploaded directly to Heibox
- **Team collaboration** - Everyone with access sees changes immediately
- **No GitHub required** - Direct cloud storage, no Pull Requests
- **Better privacy** - Data stays in your institution's cloud, no Git history

**What you'll need:**

- Heibox/Seafile account (e.g., from Heidelberg University)
- WebDAV access credentials (username + token or password)
- 5 minutes for setup

---

## Quick Setup with CLI Wizard

The fastest way to set up Heibox integration is using the interactive wizard:

```bash
hei-datahub auth setup
```

The wizard will guide you through 5 simple steps:

1. **WebDAV URL** - Your Heibox server (default: Heidelberg University)
2. **Username** - Your Heibox username (`username@auth.local`)
3. **Password** - Your WebDAV password from Heibox Settings
4. **Library** - Folder name in Heibox (default: `Testing-hei-datahub`)
5. **Storage** - Linux keyring (recommended) or environment variables

**After setup:**

- ✅ Verify: `hei-datahub auth status`
- 🔍 Test: `hei-datahub auth doctor`
- 🚀 Launch: `hei-datahub`

---

## Step-by-Step Setup

### Step 1: Set Up WebDAV Password

**Important:** Seafile's Web API tokens don't work with WebDAV. You need a WebDAV-specific password.

1. Log in to Heibox: [https://heibox.uni-heidelberg.de](https://heibox.uni-heidelberg.de)
2. Click your profile icon → **Settings**
3. Navigate to **WebDAV Password** section
4. Click **set password**, enter a secure password, and click **Submit**
5. **Copy this password** - you'll need it in the wizard

**Note:**
- This is a separate password just for WebDAV access
- NOT your regular Heibox login password
- NOT the Web API Auth Token (API tokens are for REST API, not WebDAV)

### Step 2: Run the Setup Wizard

Launch the interactive setup:

```bash
hei-datahub auth setup
```

#### Wizard Prompts:

**1. WebDAV URL:**
```
📍 Enter WebDAV base URL
   Default: https://heibox.uni-heidelberg.de/seafdav
   >
```
- Press Enter for default (Heidelberg University)
- Or enter your institution's URL

**2. Username:**
```
👤 Enter username
   (e.g., username@auth.local)
   > username@auth.local
```
- Your Heibox login username

**3. WebDAV Password:**
```
🔑 Enter WebDAV password
   (from Heibox Settings → WebDAV Password)
   >
```
- Paste your WebDAV password from Step 1
- Input is hidden for security

**4. Library Name:**
```
📁 Library/folder name
   Default: Testing-hei-datahub (for now)
   >
```
- Press Enter for default
- Or enter your library name

**5. Credential Storage:**
```
🔐 Store credentials in Linux keyring?
   Recommended for security (encrypted storage)
   [Y/n] >
```
- Press Enter for keyring (recommended)
- Type `n` for environment variables

**6. Validation:**
```
🔍 Testing connection...
   ✓ Successfully connected to WebDAV server
   ✓ Write permissions verified

✅ Configuration saved
   📄 /home/user/.config/hei-datahub/config.toml
   🔐 Credentials stored in Linux keyring

🎯 Next steps:
   • Run: hei-datahub auth status
   • Run: hei-datahub auth doctor
   • Launch TUI: hei-datahub
```

### Step 3: Verify Connection

Check your configuration status:

```bash
hei-datahub auth status
```

**Expected output:**
```
WebDAV Authentication Status:

  URL: https://heibox.uni-heidelberg.de/seafdav
  Username: username@auth.local
  Method: token
  Storage: keyring
  Status: ✓ Connected
```

### Step 4: Test in TUI

Launch the app and verify the status indicator:

```bash
hei-datahub
```

Look for the status line:

- ✅ **Connected:** ` Synced to Hei-box` (green)
- ⚠️ **Connection failed:** `⚠ Hei-box Configured (connection failed)` (yellow)
- ○ **Not configured:** `○ Hei-box Not Connected` (gray)

---

## Configuration Reference

### Config File Location

**Linux:** `~/.config/hei-datahub/config.toml`

### Example Configuration

```toml
[auth]
method = "password"  # WebDAV requires password method
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "username@auth.local"
key_id = "webdav:password:username@heibox.uni-heidelberg.de"
stored_in = "keyring"  # or "env"
```

### Configuration Fields

| Field | Description | Example |
|-------|-------------|---------|
| **method** | Auth type: `password` (WebDAV only) | `password` |
| **url** | WebDAV server URL | `https://heibox.uni-heidelberg.de/seafdav` |
| **username** | Your Heibox username | `username@auth.local` |
| **key_id** | Keyring identifier (auto-generated) | `webdav:password:username@heibox...` |
| **stored_in** | Storage backend: `keyring` or `env` | `keyring` |

**Note:** The `method` field can be `token` or `password` in the config, but for Seafile WebDAV, always use `password` with your WebDAV password. The "token" method is reserved for future API token support.

### Credential Storage

**Linux Keyring (Recommended):**

- Service: `hei-datahub`
- Key format: `webdav:{method}:{username}@{host}`
- Encryption: AES-256 (handled by system keyring)
- Backends: GNOME Keyring, KWallet, Secret Service

**Environment Variables (Fallback):**

- `HEIDATAHUB_WEBDAV_TOKEN` - API token
- `HEIDATAHUB_WEBDAV_PASSWORD` - Password
- `HEIDATAHUB_WEBDAV_URL` - Server URL
- `HEIDATAHUB_WEBDAV_USERNAME` - Username

**Security Note:** Environment variables are NOT encrypted. Use keyring when possible.

---

## Advanced Configuration

### Non-Interactive Setup

For scripting or automation:

```bash
hei-datahub auth setup \
  --url https://heibox.uni-heidelberg.de/seafdav \
  --username username@auth.local \
  --token "$SEAFILE_TOKEN" \
  --non-interactive \
  --overwrite
```

**Options:**

- `--url URL` - WebDAV server URL
- `--username USER` - Heibox username
- `--token TOKEN` - API token
- `--password PASS` - Password (less secure than token)
- `--store {keyring,env}` - Force storage backend
- `--no-validate` - Skip connection test
- `--non-interactive` - No prompts
- `--overwrite` - Replace existing config

### Environment Variables Only

If keyring is unavailable:

```bash
# Set credentials
export HEIDATAHUB_WEBDAV_URL="https://heibox.uni-heidelberg.de/seafdav"
export HEIDATAHUB_WEBDAV_USERNAME="username@auth.local"
export HEIDATAHUB_WEBDAV_TOKEN="your-token-here"

# Create minimal config
hei-datahub auth setup --store env --non-interactive
```

**Security Warning:** Environment variables are visible to all processes. Use keyring when possible.

### Using Different Seafile Servers

For other institutions:

```bash
# Example: TU Munich
hei-datahub auth setup \
  --url https://syncandshare.lrz.de/seafdav \
  --username user@tum.de

# Example: Generic Seafile
hei-datahub auth setup \
  --url https://seafile.example.com/seafdav \
  --username your-email@example.com
```

### Multiple Configurations

Switch between different Heibox accounts:

```bash
# Save current config
cp ~/.config/hei-datahub/config.toml ~/.config/hei-datahub/config.work.toml

# Setup personal account
hei-datahub auth setup  # Configure personal Heibox

# Switch back to work
cp ~/.config/hei-datahub/config.work.toml ~/.config/hei-datahub/config.toml
```

---

## Security Best Practices

### Protecting Your Credentials

✅ **DO:**

- Use API tokens instead of passwords
- Store in Linux keyring (automatic with setup wizard)
- Use unique tokens per application
- Revoke tokens when no longer needed
- Keep tokens out of shell history

❌ **DON'T:**

- Share tokens via email or chat
- Commit config files with credentials to Git
- Use the same token for multiple apps
- Store credentials in plaintext files
- Leave unused tokens active

### Credential Rotation

Rotate tokens regularly (recommended: every 90 days):

```bash
# 1. Generate new token in Heibox
# 2. Update credentials
hei-datahub auth clear --force
hei-datahub auth setup
```

---

## Related Documentation

- [**First Dataset**](05-first-dataset.md) - Add dataset metadata
- [**Edit Datasets**](06-edit-datasets.md) - Modify existing dataset metadata
- [**FAQ**](../help/90-faq.md) - Common questions about GitHub integration
- [**Troubleshooting**](../help/troubleshooting.md) - Resolve common issues

---

## What's Next?

✅ **WebDAV configured!** You're ready to:

- Press `a` to add your first dataset
- Press `s` anytime to update settings

**Learn more:**

- [Getting Started Guide](../getting-started/01-getting-started.md)
- [The Basics](../getting-started/03-the-basics.md)
- [All Keyboard Shortcuts](../reference/keybindings.md)
