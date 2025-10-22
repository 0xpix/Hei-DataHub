# WebDAV Integration Manual Test Guide

This guide provides step-by-step instructions for testing the WebDAV integration with Heibox/Seafile.

## Prerequisites

1. **Heibox Account**: University of Heidelberg credentials
2. **WebDAV Token**: App-specific password for WebDAV access
   - Login to Heibox: https://heibox.uni-heidelberg.de
   - Go to Settings → Security → App passwords
   - Create new password for "Hei-DataHub"
3. **Test Library**: A Seafile library named `testing-hei-datahub` with some test files

## Test Setup

### 1. Configure Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export HEIBOX_URL="https://heibox.uni-heidelberg.de/seafdav"
export HEIBOX_LIB="testing-hei-datahub"
export HEIBOX_USERNAME="<your_uni_username_or_email>"
export HEIBOX_WEBDAV_TOKEN="<your_webdav_app_password>"

# Apply changes
source ~/.bashrc  # or source ~/.zshrc
```

### 2. Configure Hei-DataHub

Edit `~/.config/hei-datahub/config.yaml`:

```yaml
storage:
  backend: "webdav"  # Switch to webdav mode
  base_url: "https://heibox.uni-heidelberg.de/seafdav"
  library: "testing-hei-datahub"
  username: ""  # Leave empty to use HEIBOX_USERNAME env
  password_env: "HEIBOX_WEBDAV_TOKEN"
  connect_timeout: 5
  read_timeout: 60
  max_retries: 3
```

### 3. Prepare Test Files

Create these test files in your `testing-hei-datahub` library via Heibox web interface:

```
testing-hei-datahub/
├── README.md               # Text file for preview test
├── sample.csv              # CSV file for preview test
├── config.yaml             # YAML file for preview test
├── data.json               # JSON file for preview test
├── subfolder/              # Directory for navigation test
│   ├── nested.txt
│   └── image.png           # Binary file (non-previewable)
└── large-file.zip          # Large binary file
```

## Test Cases

### Test 1: Launch Cloud Files View

**Steps:**
1. Launch Hei-DataHub: `hei-datahub`
2. Press `c` (cloud files) from the home screen

**Expected Result:**
- Cloud Files screen opens
- Title shows "☁️ Cloud Files (Heibox)"
- Breadcrumb shows "📍 / (root)"
- File table displays contents of `testing-hei-datahub/`
- Status shows "X items"

**Failure Scenarios:**
- **401/403 Error**: Check `HEIBOX_USERNAME` and `HEIBOX_WEBDAV_TOKEN`
- **Empty listing**: Verify library name matches exactly
- **Connection timeout**: Check network/VPN connection

---

### Test 2: Directory Navigation

**Steps:**
1. Open Cloud Files view (`c`)
2. Use `j`/`k` to navigate to `subfolder/`
3. Press `Enter` or `o` to open

**Expected Result:**
- Breadcrumb updates to "📍 / subfolder"
- Table shows contents of subfolder
- Files: `nested.txt`, `image.png`

**Return to Parent:**
- Press `h` or `u`
- Breadcrumb returns to "📍 / (root)"

---

### Test 3: Text File Preview

**Steps:**
1. Navigate to `README.md`
2. Press `Enter` or `o`

**Expected Result:**
- Preview panel appears at bottom
- Shows "Preview: README.md"
- Content is displayed with syntax
- Status shows "Previewing README.md"

**Test Other Formats:**
- CSV: Shows tabular data
- YAML: Shows configuration
- JSON: Shows structured data

---

### Test 4: Binary File Preview

**Steps:**
1. Navigate to `subfolder/image.png`
2. Press `Enter` or `o`

**Expected Result:**
- Preview panel shows:
  ```
  Binary file (.png) - download to view

  File: image.png
  Size: X.X KB
  ```
- Status shows download location

---

### Test 5: File Download

**Steps:**
1. Navigate to any file (e.g., `README.md`)
2. Press `d` (download)

**Expected Result:**
- Status shows "Downloading README.md..."
- Notification: "✓ Downloaded: ~/Downloads/README.md"
- File exists in `~/Downloads/` (or `/tmp/hei-datahub-downloads/`)

**Verify:**
```bash
ls -lh ~/Downloads/README.md
cat ~/Downloads/README.md
```

---

### Test 6: Vim-Style Navigation

**Test Keybindings:**
- `j` / `k`: Move down/up in file list
- `g` (double-tap): Jump to top
- `G`: Jump to bottom
- `h` / `u`: Go to parent directory
- `Enter` / `o`: Open file/folder
- `d`: Download selected file
- `r`: Refresh current directory
- `q` / `Escape`: Close cloud files view

**Expected Result:**
All keybindings work smoothly without lag

---

### Test 7: Refresh Directory

**Steps:**
1. Open Cloud Files view
2. Press `r` (refresh)

**Expected Result:**
- Notification: "Refreshing..."
- Table reloads with current directory contents
- Cursor position maintained

---

### Test 8: Large File Handling

**Steps:**
1. Navigate to `large-file.zip` (>10 MB)
2. Press `o` to preview

**Expected Result:**
- Preview shows binary file message (no crash)
- Status shows file info

**Download Test:**
1. Press `d` to download
2. Wait for completion

**Expected Result:**
- Progress indication in status
- Success notification after download

---

### Test 9: Empty Directory

**Steps:**
1. Create an empty folder in Heibox: `empty-folder/`
2. Navigate to it in TUI

**Expected Result:**
- Breadcrumb shows "📍 / empty-folder"
- Table shows "[dim]No files[/dim]"
- Status shows "Empty directory"

---

### Test 10: Error Recovery

**Test Network Error:**
1. Disconnect network/VPN
2. Press `r` to refresh

**Expected Result:**
- Error notification: "Connection failed: ..."
- Status shows error in red
- UI remains responsive

**Reconnect and Retry:**
1. Reconnect network
2. Press `r` again

**Expected Result:**
- Successfully refreshes
- Status shows "X items"

---

### Test 11: Fallback to Filesystem Mode

**Steps:**
1. Edit `~/.config/hei-datahub/config.yaml`:
   ```yaml
   storage:
     backend: "filesystem"
     data_dir: "/home/<user>/seafile_mount/testing-hei-datahub"
   ```
2. Restart Hei-DataHub
3. Press `c`

**Expected Result:**
- Cloud Files view uses local filesystem
- Same UI/navigation works identically
- No network requests

---

## Performance Benchmarks

### Listing Performance
- Small directory (<10 files): < 1 second
- Medium directory (10-100 files): < 2 seconds
- Large directory (100-500 files): < 5 seconds

### Download Performance
- Small file (<1 MB): < 2 seconds
- Medium file (1-10 MB): < 10 seconds
- Large file (10-100 MB): Proportional to network speed

### Preview Load Time
- Text files (<100 KB): < 1 second
- Large text files (>1 MB): Truncated at 100 KB

---

## Troubleshooting

### Authentication Failed (401/403)

**Symptoms:**
- Error: "Auth failed. Check HEIBOX_USERNAME and HEIBOX_WEBDAV_TOKEN"

**Solutions:**
1. Verify environment variables are set:
   ```bash
   echo $HEIBOX_USERNAME
   echo $HEIBOX_WEBDAV_TOKEN
   ```
2. Check token is valid in Heibox web interface
3. Regenerate WebDAV app password if expired

---

### Library Not Found (404)

**Symptoms:**
- Error: "Path not found: "

**Solutions:**
1. Verify library name matches exactly (case-sensitive)
2. Check library exists in Heibox web interface
3. Ensure you have access permissions

---

### Connection Timeout

**Symptoms:**
- Error: "Request timeout for ..."

**Solutions:**
1. Check internet connection
2. Verify VPN if required
3. Increase timeout in config:
   ```yaml
   storage:
     connect_timeout: 10
     read_timeout: 120
   ```

---

### Empty File Listing

**Symptoms:**
- Shows "No files" but library has content

**Solutions:**
1. Refresh with `r`
2. Check WebDAV URL is correct: `/seafdav` (not `/dav`)
3. Verify library name in config matches Heibox

---

## Security Checks

### ✓ Secrets Not Logged
```bash
# Check log files for secrets
tail -f ~/.local/state/hei-datahub/logs/app.log | grep -i "token\|password"
```
**Expected:** No actual token values, only `***:***` masks

### ✓ Config File Security
```bash
# Verify config doesn't contain token
cat ~/.config/hei-datahub/config.yaml | grep -i "token\|password"
```
**Expected:** Only shows `password_env: "HEIBOX_WEBDAV_TOKEN"`, not actual token

---

## Acceptance Criteria

All tests must pass:

- [x] Can list files in `testing-hei-datahub/`
- [x] Navigate into subdirectories
- [x] Preview text/CSV/YAML/JSON files
- [x] Binary files show info message
- [x] Download files to local machine
- [x] Vim keybindings work correctly
- [x] Errors display helpful messages
- [x] No secrets in logs or config files
- [x] Filesystem fallback works
- [x] Network errors handled gracefully

---

## Cleanup

After testing:

```bash
# Remove test downloads
rm -rf ~/Downloads/hei-datahub-test-*
rm -rf /tmp/hei-datahub-downloads/

# Switch back to filesystem mode (optional)
# Edit ~/.config/hei-datahub/config.yaml:
#   storage.backend: "filesystem"
```

---

## Reporting Issues

If any test fails, collect this info:

1. **Error message** (screenshot or copy-paste)
2. **Log file**: `~/.local/state/hei-datahub/logs/app.log`
3. **Config** (with secrets redacted): `~/.config/hei-datahub/config.yaml`
4. **Environment**:
   ```bash
   echo "HEIBOX_USERNAME: ${HEIBOX_USERNAME}"
   echo "Token set: ${HEIBOX_WEBDAV_TOKEN:+YES}"
   ```
5. **Network test**:
   ```bash
   curl -u "$HEIBOX_USERNAME:$HEIBOX_WEBDAV_TOKEN" \
     "https://heibox.uni-heidelberg.de/seafdav/testing-hei-datahub/"
   ```
