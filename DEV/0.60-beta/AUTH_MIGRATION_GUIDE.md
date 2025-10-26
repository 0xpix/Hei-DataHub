# Authentication Fix Migration Guide (v0.60-beta)

## What Changed

We've fixed authentication issues in v0.60-beta where the GUI Auth wizard and CLI auth setup were incompatible with the storage manager's authentication checks.

### Issues Fixed:

1. **GUI Auth wizard now stores credentials in the correct format**
   - Previously used: `webdav_{random_uuid}`
   - Now uses: `heibox:password:{username}@{host}` (updated to reflect HeiBox credentials)

2. **Config file now includes all required fields**
   - Added: `method`, `stored_in`, `library` to auth section
   - These fields are required for the storage manager to load credentials

3. **Storage manager now handles both old and new formats**
   - Supports library in both `auth` section and `cloud` section
   - Defaults to keyring if `stored_in` is missing (backward compatibility)

## Do You Need to Migrate?

### Check Your Current Setup

Run this command to see your current auth configuration:

```bash
cat ~/.config/hei-datahub/config.toml
```

**If you see this (OLD FORMAT - needs migration):**
```toml
[auth]
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "your-username"
key_id = "webdav_abc12345"

[cloud]
library = "test-library"
```

**You need to migrate** ✗

**If you see this (NEW FORMAT - no migration needed):**
```toml
[auth]
method = "password"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "your-username"
library = "test-library"
key_id = "webdav:password:your-username@heibox.uni-heidelberg.de"
stored_in = "keyring"

[cloud]
library = "test-library"
```

**You're good to go!** ✓

## Migration Steps

### Option 1: Re-run the GUI Wizard (Recommended)

This is the easiest way to migrate:

1. **Launch the app:**
   ```bash
   hei-datahub
   ```

2. **Open Settings** (press `s` or navigate to Settings menu)

3. **Run the Auth Wizard:**
   - Fill in your WebDAV URL
   - Enter your library name
   - Enter your username
   - Enter your WebDAV password

4. **Save** and close the wizard

5. **Test** by trying to add a dataset (press `a`)

### Option 2: Re-run CLI Auth Setup

If you prefer command-line:

1. **Run the setup wizard:**
   ```bash
   hei-datahub auth setup --overwrite
   ```

2. **Follow the prompts:**
   - WebDAV URL
   - Username
   - Password
   - Library name
   - Storage method (keyring recommended)

3. **Verify:**
   ```bash
   hei-datahub auth status
   ```

4. **Test connection:**
   ```bash
   hei-datahub auth doctor
   ```

### Option 3: Manual Config Edit (Advanced)

If you want to edit the config file manually:

1. **Backup your current config:**
   ```bash
   cp ~/.config/hei-datahub/config.toml ~/.config/hei-datahub/config.toml.backup
   ```

2. **Edit the config file:**
   ```bash
   nano ~/.config/hei-datahub/config.toml
   ```

3. **Update to this format:**
   ```toml
   [auth]
   method = "password"
   url = "https://heibox.uni-heidelberg.de/seafdav"
   username = "your-username"
   library = "test-library"
   key_id = "webdav:password:your-username@heibox.uni-heidelberg.de"
   stored_in = "keyring"

   [cloud]
   library = "test-library"
   ```

4. **Update the keyring entry:**

   The old keyring entry won't work with the new key_id format. You'll need to:

   a. Delete the old entry:
   ```bash
   # This will fail gracefully if entry doesn't exist
   python3 -c "import keyring; keyring.delete_password('hei-datahub', 'webdav_OLD_UUID')"
   ```

   b. Add the new entry with correct key_id:
   ```bash
   python3 -c "import keyring; keyring.set_password('hei-datahub', 'webdav:password:your-username@heibox.uni-heidelberg.de', 'YOUR_WEBDAV_PASSWORD')"
   ```

5. **Test:**
   ```bash
   hei-datahub auth status
   hei-datahub auth doctor
   ```

## Verification

After migrating, verify everything works:

### 1. Check Auth Status

```bash
hei-datahub auth status
```

**Expected output:**
```
🔐 WebDAV Authentication Status

   Method: password
   URL: https://heibox.uni-heidelberg.de/seafdav
   Username: your-username
   Library: test-library
   Stored in: keyring

✅ Configuration valid
✅ Credentials found in keyring
```

### 2. Test Connection

```bash
hei-datahub auth doctor
```

**Expected output:**
```
✓ Config file readable
✓ Credentials present in keyring
✓ Network reachable
✓ WebDAV authentication successful
✓ Read/write permissions OK
```

### 3. Try Adding a Dataset

1. Launch the app: `hei-datahub`
2. Press `a` to add a dataset
3. Fill in the form
4. Save

**Expected:** Dataset is saved to cloud without errors.

**Before fix:** You would see: *"Credential not found. Run: hei-datahub auth setup"*

## Troubleshooting

### "Credential not found" Error

**Cause:** The keyring entry doesn't match the new key_id format.

**Fix:** Re-run auth setup:
```bash
hei-datahub auth setup --overwrite
```

### "Config missing [auth] section"

**Cause:** Config file is corrupted or very old format.

**Fix:** Delete and recreate:
```bash
rm ~/.config/hei-datahub/config.toml
hei-datahub auth setup
```

### GUI and CLI Configs Conflict

**Cause:** You ran both GUI and CLI setup, creating conflicting configs.

**Fix:** Choose one and stick with it:
```bash
# Option 1: Use CLI
hei-datahub auth setup --overwrite

# Option 2: Use GUI
hei-datahub  # then go to Settings → Auth Wizard
```

### Still Getting Errors After Migration

**Steps:**

1. **Clear everything and start fresh:**
   ```bash
   # Backup first
   cp ~/.config/hei-datahub/config.toml ~/.config/hei-datahub/config.toml.backup

   # Remove config
   rm ~/.config/hei-datahub/config.toml

   # Re-run setup
   hei-datahub auth setup
   ```

2. **Check logs:**
   ```bash
   tail -f ~/.local/state/hei-datahub/logs/app.log
   ```

3. **Run diagnostics:**
   ```bash
   hei-datahub auth doctor --json
   ```

## Technical Details

### Key ID Format

**Old GUI format (broken):**
```
webdav_{random_uuid}
```
Example: `webdav_a1b2c3d4`

**New format (compatible with CLI):**
```
webdav:{method}:{username}@{host}
```
Example: `webdav:password:alice@heibox.uni-heidelberg.de`

### Config File Structure

**Minimum required fields in `[auth]` section:**
- `method` - Authentication method ("password" or "token")
- `url` - WebDAV server URL
- `username` - Your WebDAV username
- `library` - Library/folder name in WebDAV
- `key_id` - Key for credential storage
- `stored_in` - Storage backend ("keyring" or "env")

### Storage Manager Logic

The storage manager (`storage_manager.py`) now:

1. Checks for `auth` section in config
2. Loads `url`, `username`, `library`, `key_id`, `stored_in`
3. Falls back to `cloud.library` if `auth.library` is missing
4. Defaults to keyring if `stored_in` is missing
5. Loads credential from keyring using `key_id`
6. Raises error if any required field or credential is missing

## Need Help?

If you're still having issues after following this guide:

1. **Check the logs:**
   ```bash
   tail -100 ~/.local/state/hei-datahub/logs/app.log
   ```

2. **Create an issue:**
   - Go to: https://github.com/0xpix/Hei-DataHub/issues
   - Include:
     - Your config file (with password redacted)
     - Error messages from logs
     - Output of `hei-datahub auth doctor`

3. **Ask in your team's communication channel**

## Summary

The authentication system now works consistently across:

- ✅ GUI Auth wizard in Settings
- ✅ CLI `hei-datahub auth setup` command
- ✅ Storage manager authentication checks
- ✅ Dataset creation flow

**Migration is required** if you set up auth using the GUI in v0.60-beta before this fix.

**Migration is simple:** Just re-run the GUI wizard or CLI setup command.
