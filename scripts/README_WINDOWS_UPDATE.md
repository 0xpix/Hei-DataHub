# Windows Update Scripts

This directory contains helper scripts for updating Hei-DataHub on Windows.

## The Problem

When you run `hei-datahub update` from within the app on Windows, the update fails with:

```
error: Failed to install entrypoint
  Caused by: failed to copy file from C:\Users\...\hei-datahub.exe
```

**Why?** Windows locks executable files while they're running. You can't update an app from within itself on Windows.

## The Solutions

### Option 1: Batch Script (Easiest)

**File:** `windows_update.bat`

**How to use:**
1. Download the file or navigate to the scripts directory
2. Close ALL Hei-DataHub windows
3. Double-click `windows_update.bat` (or run from Command Prompt)
4. Follow the prompts

**What it does:**
- Checks if the app is running
- Verifies UV and Git are installed
- Performs the update using `uv tool install --force`
- Handles both SSH and HTTPS authentication

**Usage:**
```cmd
REM Update to main branch
windows_update.bat

REM Update to specific branch
windows_update.bat v0.58.x

REM Update to develop branch
windows_update.bat develop
```

### Option 2: PowerShell Script (Advanced)

**File:** `windows_update_helper.ps1`

**How to use:**
1. Open PowerShell
2. Navigate to scripts directory:
   ```powershell
   cd path\to\Hei-DataHub\scripts
   ```
3. Run:
   ```powershell
   .\windows_update_helper.ps1
   ```

**What it does:**
- Performs comprehensive preflight checks:
  - Running processes
  - Long paths support
  - Windows Defender exclusions
  - Git configuration
  - UV installation
- Launches the Python update manager
- More detailed diagnostics than the batch script

**Usage:**
```powershell
# Interactive mode
.\windows_update_helper.ps1

# Specify branch
.\windows_update_helper.ps1 -Branch main

# Force update (skip checks)
.\windows_update_helper.ps1 -Force

# Specify branch and force
.\windows_update_helper.ps1 -Branch v0.58.x -Force
```

## Manual Update (No Scripts)

If you prefer to update manually:

### Using SSH (if configured)

```powershell
# Close all Hei-DataHub windows first
uv tool install --force git+ssh://git@github.com/0xpix/Hei-DataHub.git@main
```

### Using HTTPS + Token

```powershell
# Set your token
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Close all Hei-DataHub windows first
uv tool install --force "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main"
```

## Troubleshooting

### "UV not found"

**Solution:** Install UV first:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### "Git not found"

**Solution:** Install Git from https://git-scm.com/download/win

### "Authentication failed"

**Solution:** Set up authentication:

**SSH:**
```bash
# In Git Bash
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
# Add output to: https://github.com/settings/keys
```

**Token:**
```powershell
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Update still fails

If the update fails even with these scripts:

1. **Verify all windows are closed:**
   - Check Task Manager for `hei-datahub.exe` processes
   - Kill any hanging processes

2. **Restart your computer:**
   - Sometimes Windows needs a full restart to release file locks

3. **Fresh install:**
   ```powershell
   # Uninstall
   uv tool uninstall hei-datahub

   # Wait 10 seconds
   Start-Sleep -Seconds 10

   # Reinstall
   uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
   ```

## Why Does This Happen?

Unlike Unix-like systems (Linux, macOS), Windows locks executable files while they're running to prevent corruption. This is a security feature of the Windows file system.

When you run `hei-datahub update` from within the app:
1. The `hei-datahub.exe` file is locked by Windows
2. UV tries to replace `hei-datahub.exe` with the new version
3. Windows blocks the file operation → update fails

The workaround is to run the update from **outside** the locked executable, which is what these scripts do.

## Contributing

If you find issues with these scripts or have improvements, please:
1. Open an issue: https://github.com/0xpix/Hei-DataHub/issues
2. Submit a PR with your fix

## See Also

- [Windows Installation Notes](../docs/installation/windows-notes.md)
- [Troubleshooting Guide](../docs/help/troubleshooting.md)
- [UV Documentation](https://docs.astral.sh/uv/)
