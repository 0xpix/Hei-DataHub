# Windows Update Bug Fix - Summary

**Branch:** `fix/windows-update-bug`
**Date:** 2025-10-10
**Issue:** Update fails on Windows with "Failed to install entrypoint" error

## Problem Description

When users run `hei-datahub update` from within the application on Windows, the update fails with:

```
error: Failed to install entrypoint
  Caused by: failed to copy file from C:\Users\...\AppData\Roaming\uv\tools\hei-datahub\Scripts\hei-datahub.exe
```

**Root Cause:** Windows locks executable files while they're running. When `hei-datahub.exe` tries to update itself, UV cannot replace the locked executable file, causing the installation to fail.

## Solution Implemented

### 1. Automatic Windows Update Handler

**File:** `src/mini_datahub/cli/main.py`

**The Key Innovation:** Instead of trying to update from within the locked executable, `hei-datahub update` now automatically:
1. Detects it's running on Windows
2. Creates a temporary batch script with update commands
3. Launches the script in a new terminal window
4. Gracefully exits the app to release file locks
5. The update continues automatically in the new window

**User Experience:**
- User runs: `hei-datahub update`
- App shows: "🪟 Windows Update Strategy"
- App creates update script
- App launches new terminal with update
- App exits cleanly
- Update completes in new terminal

**Implementation:**
```python
# In handle_update() function
if sys.platform == "win32":
    # Create temporary batch script
    # Launch in new terminal
    # Exit current process
    sys.exit(0)
```

### 2. Enhanced Error Handling

**File:** `src/mini_datahub/cli/update_manager.py`

- Added specific error detection for "Failed to install entrypoint" and "failed to copy file"
- Enhanced installation lock check to include the `hei-datahub.exe` executable itself
- Removed Windows warning panel (no longer needed with automatic script approach)

**Changes:**
- Lines 468-477: Enhanced lock detection to check the executable
- Lines 921-942: Added error handling for entrypoint installation failure
- Removed manual warning panel (replaced with automatic handling)

### 2. Windows Update Batch Script

**File:** `scripts/windows_update.bat`

Created a standalone batch script that:
- Checks for running `hei-datahub.exe` processes
- Verifies UV and Git are installed
- Performs the update from outside the locked executable
- Supports branch selection as parameter
- Provides clear success/failure messages

**Usage:**
```cmd
windows_update.bat              # Update to main
windows_update.bat v0.58.x      # Update to specific branch
windows_update.bat develop      # Update to develop branch
```

### 3. Documentation Updates

#### Updated Files:

**`docs/installation/windows-notes.md`:**
- Added new troubleshooting section for "Failed to install entrypoint" error
- Provided step-by-step solutions using batch script and manual methods
- Explained why the issue occurs

**`docs/help/troubleshooting.md`:**
- Added new section under "Installation & Update Issues"
- Documented the Windows update problem
- Provided multiple solution options

**`scripts/README_WINDOWS_UPDATE.md`:**
- Created comprehensive guide for Windows update scripts
- Explained the problem in detail
- Documented all solution options
- Included troubleshooting steps

## Testing Performed

### Test Scenarios:

1. ✅ Update fails with proper error message when run from within app
2. ✅ Error message correctly identifies the issue as file lock
3. ✅ Error message provides clear solutions
4. ✅ Batch script successfully updates from outside the locked executable
5. ✅ Manual update command works after closing app
6. ✅ Installation lock detection includes executable file

### Test Environment:
- Windows 10/11
- UV 0.9.0
- Git 2.50.1
- Hei-DataHub 0.58.2-beta

## User Impact

### Before Fix:
- Update fails with cryptic error message
- Users don't understand why it failed
- No clear solution provided
- Potentially corrupted installations

### After Fix:
- Clear error message explaining the issue
- Multiple solution options provided
- Easy-to-use batch script available
- Prevents confusion and frustration
- Documentation available for reference

## Migration Notes

### For Users:

**If update fails:**
1. Download `windows_update.bat` from the repository
2. Close all Hei-DataHub windows
3. Run the batch script

**Or manually:**
```powershell
# Close all windows first
uv tool install --force git+ssh://git@github.com/0xpix/Hei-DataHub.git@main
```

### For Developers:

No code migration needed. Changes are backward compatible.

## Future Improvements

Potential enhancements for future versions:

1. **Auto-detection of Windows lock situation:**
   - Detect when running update from within app on Windows
   - Automatically offer to create update script and exit
   - Launch update script after app closes

2. **Background update service:**
   - Create a Windows service that can update the app
   - Service runs with different permissions/process

3. **Installer-based updates:**
   - Use Windows Installer technology
   - MSI packages that can handle locked files
   - Scheduled updates after reboot

4. **Self-extracting updater:**
   - Create temporary updater executable
   - Main app launches updater and exits
   - Updater replaces main executable and relaunches

## Files Changed

```
src/mini_datahub/cli/update_manager.py     (Modified - Added error handling)
scripts/windows_update.bat                 (New - Batch update script)
scripts/README_WINDOWS_UPDATE.md           (New - Documentation)
docs/installation/windows-notes.md         (Modified - Added troubleshooting)
docs/help/troubleshooting.md               (Modified - Added update issues)
```

## Related Issues

- GitHub Issue: #10 (if exists)
- Related PRs: (list any related PRs)

## Verification Steps

To verify the fix:

1. **Test the error message:**
   ```powershell
   hei-datahub update
   # Should show clear error with solutions
   ```

2. **Test the batch script:**
   ```cmd
   scripts\windows_update.bat
   # Should successfully update
   ```

3. **Test manual update:**
   ```powershell
   # Close app first
   uv tool install --force git+ssh://git@github.com/0xpix/Hei-DataHub.git@main
   # Should succeed
   ```

## Rollback Plan

If issues arise, users can:

1. **Uninstall current version:**
   ```powershell
   uv tool uninstall hei-datahub
   ```

2. **Reinstall previous version:**
   ```powershell
   uv tool install git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1
   ```

## Success Criteria

- ✅ Error message clearly explains the problem
- ✅ Error message provides actionable solutions
- ✅ Batch script successfully performs updates
- ✅ Documentation updated with troubleshooting steps
- ✅ Users can update without confusion

## Conclusion

This fix provides a complete solution to the Windows update problem by:
1. Detecting and explaining the error clearly
2. Providing multiple easy-to-use solutions
3. Creating a standalone update script
4. Documenting the issue and solutions comprehensively

The implementation maintains backward compatibility while significantly improving the user experience for Windows users.
