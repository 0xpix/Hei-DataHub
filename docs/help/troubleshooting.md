# Troubleshooting

Common issues and how to fix them.

**Version:** 0.56-beta, 0.57-beta, and 0.57.1-beta

---

## Known Issues (from v0.56-beta)

These issues were introduced in v0.56-beta. Some were fixed in v0.57.1-beta, others remain open.

### 1. Theme/Keybinding Changes Require Restart

**Status:** ✅ **Fixed in v0.57.1-beta** – Config changes now apply automatically without restart.

**If you still experience this on v0.57.1+:**
1. Verify you're running the latest version: `hei-datahub --version`
2. Check that your config file is valid YAML
3. If issue persists, file a bug report with reproduction steps.

---

### 2. Edit Form Doesn't Scroll on Small Screens

**Symptom:** Some fields are hidden when editing on small terminals.

**Cause:** Edit form lacks scrolling support.

**Workarounds:**
- Resize terminal to at least 80x24
- Use `Tab` to navigate to hidden fields
- Edit YAML file manually:
  ```bash
  vim data/my-dataset/metadata.yaml
  ```

**Status:** Scrollable forms coming in v0.58-beta.

---

### 3. Nested Array Fields Not Editable

**Symptom:** Can't edit `schema_fields` or other array fields in edit mode.

**Cause:** Array editing not yet implemented.

**Workaround:** Edit the YAML file manually:
```bash
vim data/my-dataset/metadata.yaml
```

**Status:** Array field editing planned for v0.58-beta.

---

### 4. PR Shows as Failed But Actually Succeeds

**Symptom:** Press `P` to publish, app says "PR creation failed" or moves to outbox, but PR is actually created on GitHub.

**Cause:** GitHub API response handling issue.

**Workaround:**
1. Check GitHub directly: `https://github.com/YOUR_ORG/YOUR_REPO/pulls`
2. If PR exists, merge it normally
3. Ignore the error message in the app

**Status:** Fix in progress for v0.57.1.

---

### 5. Edited Dataset Reverts After App Restart

**Symptom:** You edit a dataset, save successfully, close the app, reopen – changes are gone.

**Status:** ✅ **Fixed in v{{ project_version }}** – This issue has been resolved. Edits now persist correctly across app restarts.

**If you still experience this on v0.57.1+:**
1. Verify you're running the latest version: `hei-datahub --version`
2. Check YAML file was updated:
   ```bash
   cat data/my-dataset/metadata.yaml
   ```
3. If issue persists, file a bug report with reproduction steps.

---

### 6. Git Branch Not Switched After PR

**Symptom:** After publishing a PR, you're still on the feature branch instead of `main`.

**Cause:** Auto-branch-switch not implemented.

**Workaround:** Switch manually:
```bash
git checkout main
```

**Status:** Auto-switch planned for v0.58-beta.

---

### 7. No Keybinding Conflict Detection

**Symptom:** Assigning the same key to two actions causes unpredictable behavior.

**Cause:** Conflict detection not implemented.

**Workaround:** Manually track your keybindings in a note.

**Status:** Conflict detection planned for v0.58-beta.

---

### 8. No Search Field Autocomplete

**Status:** ✅ **Fixed in v0.57.1-beta** – Search field now provides autocomplete suggestions for field names.

**If you still experience this on v0.57.1+:**
1. Verify you're running the latest version: `hei-datahub --version`
2. Try typing a field name like `source:` and wait for suggestions
3. If issue persists, file a bug report with reproduction steps.

---

## Installation Issues

### App Command Not Found

**Symptom:**
```bash
hei-datahub
-bash: hei-datahub: command not found
```

**Solutions:**
1. **Install the app:**
   ```bash
   pip install -e .
   ```
2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```
3. **Check PATH:**
   ```bash
   which hei-datahub
   ```

---

### Import Errors on Startup

**Symptom:**
```
ModuleNotFoundError: No module named 'textual'
```

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

---

### SQLite Database Locked

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Another instance of the app is running, or database file is corrupted.

**Solutions:**
1. **Close other instances:**
   ```bash
   pkill -f hei-datahub
   ```
2. **Rebuild database:**
   ```bash
   rm db.sqlite
   hei-datahub reindex
   ```

---

## Search Issues

### No Search Results

**Symptom:** Your search returns zero results, but you know the data exists.

**Solutions:**
1. **Try a simpler query:**
   ```
   # Instead of: format:csv source:github size:>1000
   # Try: csv
   ```
2. **Check for typos in field names:**
   ```
   # Wrong: forma:csv
   # Right: format:csv
   ```
3. **Reindex database:**
   ```bash
   hei-datahub reindex
   ```

---

### Search Crashes

**Symptom:** App crashes or freezes when searching.

**Cause:** Corrupted FTS5 index (rare).

**Solution:** Rebuild search index:
```bash
rm db.sqlite
hei-datahub reindex
```

---

### Search Results Don't Update

**Symptom:** You edit a dataset, but search still shows old values.

**Solution:** Reindex manually:
```bash
hei-datahub reindex
```

**Note:** Auto-reindex on save is supposed to work in v0.57. If this happens often, please file a bug report.

---

## Editing Issues

### Can't Save Dataset

**Symptom:** Press `Ctrl+S`, get an error: "Save failed".

**Possible causes and solutions:**

1. **Name conflict:**
   - Error: "Dataset with this name already exists"
   - Solution: Choose a unique name

2. **Invalid date format:**
   - Error: "Invalid date"
   - Solution: Use `YYYY-MM-DD` format

3. **File permissions:**
   - Error: "Permission denied"
   - Solution: Check folder permissions:
     ```bash
     ls -la data/my-dataset/
     chmod u+w data/my-dataset/metadata.yaml
     ```

4. **Disk full:**
   - Error: "No space left on device"
   - Solution: Free up disk space

---

### Undo/Redo Doesn't Work

**Symptom:** `Ctrl+Z` does nothing.

**Cause:** Undo history is cleared after save.

**Workaround:** Use undo **before** saving. After save, close and edit again to reset.

---

## GitHub Integration Issues

### "GitHub Not Connected"

**Symptom:** Status indicator shows "○ GitHub Not Connected".

**Solution:**
1. Press `S` for Settings
2. Enter your Personal Access Token (PAT)
3. Generate a token at: https://github.com/settings/tokens
4. Required scopes: `repo`, `workflow`

---

### "GitHub Configured (connection failed)"

**Symptom:** Token is set but validation fails (yellow indicator).

**Possible causes:**
1. **Token expired** – Generate a new one
2. **Token lacks permissions** – Check scopes: `repo`, `workflow`
3. **Network issue** – Check internet connection
4. **GitHub API down** – Check https://www.githubstatus.com/

**Solution:** Update token:
1. Press `S`
2. Enter new token
3. Restart app

---

### PR Creation Always Fails

See [Known Issue #4](#4-pr-shows-as-failed-but-actually-succeeds) above.

---

## Performance Issues

### Slow Search

**Symptom:** Search takes several seconds.

**Expected:** < 120ms for 2,000 datasets

**Solutions:**
1. **Rebuild index:**
   ```bash
   rm db.sqlite
   hei-datahub reindex
   ```
2. **Reduce dataset count** (if you have >10,000)
3. **Check disk speed** (slow HDDs can bottleneck)

---

### Slow Startup

**Symptom:** App takes 10+ seconds to launch.

**Solutions:**
1. **Skip Git checks:**
   ```bash
   hei-datahub --no-update-check
   ```
2. **Disable weekly update check** in config:
   ```yaml
   auto_check_updates: false
   ```

---

## UI Issues

### Text Overlaps or Misaligned

**Symptom:** UI elements are jumbled or overlap.

**Cause:** Terminal too small or font issues.

**Solutions:**
1. **Resize terminal:** Minimum 80x24
2. **Use a modern terminal:** iTerm2, Windows Terminal, Alacritty
3. **Check font:** Use a monospace font

---

### Theme Looks Wrong

**Symptom:** Colors are incorrect or hard to read.

**Solutions:**
1. **Check theme name:**
   ```yaml
   theme: "gruvbox"  # Must match exactly
   ```
2. **Use a 256-color terminal:**
   ```bash
   echo $TERM
   # Should be: xterm-256color, screen-256color, etc.
   ```
3. **Try a different theme:**
   ```yaml
   theme: "textual-dark"
   ```

---

### Help Overlay Doesn't Show Shortcuts

**Symptom:** Press `?`, but keybindings are missing or wrong.

**Cause:** Context-aware help may be empty for new screens.

**Workaround:** Check [Keybindings Reference](../reference/keybindings.md) for full list.

---

## Configuration Issues

### Config File Not Found

**Symptom:** App ignores your config.

**Solution:** Ensure file is at correct location:
```bash
~/.config/hei-datahub/config.yaml
```

Create it if missing:
```bash
mkdir -p ~/.config/hei-datahub
touch ~/.config/hei-datahub/config.yaml
```

---

### Invalid YAML Syntax

**Symptom:** Config changes don't take effect.

**Cause:** YAML syntax error (invalid indentation, missing quotes, etc.)

**Solution:** Validate your YAML:
```bash
python -c "import yaml; yaml.safe_load(open('~/.config/hei-datahub/config.yaml'))"
```

Or use an online validator: https://www.yamllint.com/

---

## Data Issues

### Missing Datasets

**Symptom:** Datasets in `data/` folder don't appear in the app.

**Solutions:**
1. **Reindex:**
   ```bash
   hei-datahub reindex
   ```
2. **Check YAML syntax:**
   ```bash
   vim data/my-dataset/metadata.yaml
   ```
3. **Check file permissions:**
   ```bash
   ls -la data/
   ```

---

### Duplicate Datasets

**Symptom:** Same dataset appears twice.

**Cause:** Database out of sync with YAML files.

**Solution:** Reindex:
```bash
rm db.sqlite
hei-datahub reindex
```

---

## Getting More Help

### Enable Debug Logging

Get detailed error messages:

1. Edit config:
   ```yaml
   debug_logging: true
   ```
2. Restart app
3. Check logs:
   ```bash
   tail -f ~/.local/share/hei-datahub/logs/app.log
   ```

---

### Check Version

Make sure you're on the latest release:
```bash
hei-datahub --version
```

Compare with: https://github.com/0xpix/Hei-DataHub/releases

---

### Report a Bug

File an issue with:
1. **Version:** `hei-datahub --version-info`
2. **OS:** Linux, macOS, Windows
3. **Terminal:** Which terminal emulator
4. **Steps to reproduce**
5. **Error messages** (from debug logs if available)

→ https://github.com/0xpix/Hei-DataHub/issues

---

## Related

- [FAQ](90-faq.md) – Quick answers to common questions
- [Configuration](../reference/12-config.md) – All settings explained
- [What's New](../whats-new/0.57-beta.md) – What's new and what's fixed
