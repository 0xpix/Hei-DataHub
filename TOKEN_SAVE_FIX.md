# 🔧 Token Save Fix - v3.0.1

## Problem Identified

The PAT (Personal Access Token) was not persisting after saving in Settings because:

1. **Missing dependency**: `keyring` was in `pyproject.toml` but not installed
2. **Logic bug**: `action_save()` created a **temporary config object** instead of updating the **global singleton**

## Solutions Applied

### 1. Installed keyring ✅

```bash
uv sync --python /usr/bin/python --dev
```

Result:
- Installed `keyring==25.6.0` with 10 dependencies
- Verified working with Backend: `Keyring` (Linux SecretService)

### 2. Fixed Settings Save Logic ✅

**Before** (Bug):
```python
def action_save(self):
    config = self._get_form_config()  # ❌ Creates NEW temporary config
    config.save_config(save_token=True)
    reload_config()  # ✅ Reloads global, but too late
```

**After** (Fixed):
```python
def action_save(self):
    config = get_github_config()  # ✅ Get the GLOBAL singleton
    config.host = self.query_one("#input-host", Input).value.strip()
    config.owner = self.query_one("#input-owner", Input).value.strip()
    # ... update all fields directly on global config ...

    token_input = self.query_one("#input-token", Input).value.strip()
    if token_input and token_input != "••••••••":
        config.set_token(token_input)  # ✅ Set token on global config

    config.save_config(save_token=True)  # ✅ Save global config
```

### 3. Enhanced Test Connection ✅

Added token validation before testing:
```python
if not config.get_token():
    status_label.update("[red]✗ GitHub token is required[/red]")
    return
```

## Testing Results

Created `test_token_save.py` to verify fix:

```
============================================================
Testing Token Persistence
============================================================

1. Keyring available: True
2. Initial token: <empty>
3. Setting test token: ghp_test_token_12345
   Token in memory: ghp_test_token_12345
4. Saving config...
   ✓ Saved
5. Reloading config (simulates restart)...
   Loaded token: ghp_test_token_12345

✅ SUCCESS: Token persisted correctly!

6. Cleaning up...
   ✓ Token cleared
============================================================
```

## How to Use Now

### Step 1: Start the TUI
```bash
uv run python -m mini_datahub.tui
```

### Step 2: Open Settings (Press `S`)

### Step 3: Fill in the form
```
GitHub Host:       github.com
Owner:             YourOrg
Repository:        YourCatalog
Default Branch:    main
GitHub Username:   your-username
GitHub Token:      ghp_YourTokenHere123456789
```

### Step 4: Save (Press `Ctrl+S` or click Save)
- You'll see: `✓ Settings saved!`
- Token is now stored in your system keyring (OS-level encryption)

### Step 5: Test Connection (Click "Test Connection")
- Should show: `✓ Connected to github.com as your-username`
- If it fails, check your token permissions (see GITHUB_TOKEN_GUIDE.md)

### Step 6: Close and Reopen Settings
- Token field should show: `••••••••` (masked)
- This confirms token is persisted and loaded from keyring

### Step 7: Create a Dataset
- Fill in the form
- Press `Ctrl+S` to save
- PR should be created automatically! 🎉

## Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│ Settings Screen (screens.py)                            │
│                                                          │
│  User pastes token → action_save()                      │
│                           ↓                              │
│                   get_github_config() ← Global singleton │
│                           ↓                              │
│                   config.set_token()                     │
│                           ↓                              │
│                   config.save_config()                   │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ GitHubConfig (config.py)                                │
│                                                          │
│  save_config(save_token=True)                           │
│         ↓                        ↓                       │
│   JSON File              keyring.set_password()         │
│   .datahub_config.json   Service: mini-datahub          │
│   (no token!)            Username: github-token         │
│                          Value: ghp_xxx...               │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ OS Keyring (Secure Storage)                             │
│                                                          │
│  Linux:   gnome-keyring / kwallet / SecretService       │
│  macOS:   Keychain                                      │
│  Windows: Credential Manager                            │
└─────────────────────────────────────────────────────────┘
```

## Files Modified

1. **mini_datahub/screens.py**
   - Fixed `action_save()` to update global config directly
   - Added token validation in `test_connection()`

2. **pyproject.toml** (already had keyring)
   - `keyring>=24.0.0` dependency

3. **test_token_save.py** (new)
   - Automated test for token persistence

## Next Steps

1. **Test the Settings screen**:
   - Press `S` in the TUI
   - Paste your GitHub PAT
   - Click Save
   - Close and reopen Settings
   - Should show `••••••••`

2. **Test connection**:
   - Click "Test Connection" button
   - Should succeed with your credentials

3. **Create a test dataset**:
   - Press `A` (Add Dataset)
   - Fill in the form
   - Press `Ctrl+S`
   - Should create PR automatically!

4. **Check the PR**:
   - Open browser to your GitHub repo
   - Navigate to Pull Requests
   - Should see: "Add dataset: [your-dataset-id]"

## Troubleshooting

### Token still not saving?

**Check keyring backend**:
```bash
python -c "import keyring; print('Backend:', type(keyring.get_keyring()).__name__)"
```

If it shows `fail.Keyring`, you need to install a keyring backend:

**Linux**:
```bash
# For GNOME
sudo apt install gnome-keyring

# For KDE
sudo apt install kwalletmanager

# Then restart your session
```

**macOS**: Built-in Keychain (should work)

**Windows**: Built-in Credential Manager (should work)

### PRs not being created?

1. Check Settings are saved (S key, should show `••••••••`)
2. Test connection (should show green ✓)
3. Check `catalog_repo_path` is set to your local clone
4. Check git remote: `git -C /path/to/catalog remote -v`

### Permission denied?

Check your PAT permissions in GitHub (see GITHUB_TOKEN_GUIDE.md):
- Repository permissions → Contents: Read and write
- Repository permissions → Pull requests: Read and write

## Verification Checklist

- [x] keyring installed and working
- [x] Token save logic fixed
- [x] Test connection validates token
- [x] Token persists across restarts
- [x] Token masked in UI (••••••••)
- [ ] User tests Settings → Save → Reopen
- [ ] User tests PR creation
- [ ] User confirms PR appears on GitHub

---

**Version**: v3.0.1
**Status**: Ready for Testing
**Date**: 2025-01-XX
