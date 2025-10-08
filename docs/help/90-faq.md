# FAQ & Quick Answers

Common questions, issues, and solutions for Hei-DataHub v0.57.x beta.

---## Q: How do I edit a dataset without manually editing YAML?

**A:** Use **inline editing** (added in v0.56):

**Steps:**
1. Open a dataset (press `Enter` on it)
2. Press `E` to enter edit mode
3. Edit fields with Tab/Shift+Tab to navigate
4. Press `Ctrl+S` to save

👉 [Full editing guide](../how-to/06-edit-datasets.md)

---

### Q: How do I search for CSV files only?

**A:** Use **field-specific search** (added in v0.56):

```
format:csv
```

**More examples:**
- `source:github` - Find GitHub datasets
- `size:>1000000` - Find files larger than 1 MB
- `project:climate` - Find datasets in "climate" project

👉 [Advanced search guide](../how-to/07-search-advanced.md)

---

### Q: What are those colored badges below the search box?

**A:** Those are **filter badges** showing your active search filters in real time:

- **🏷 source:github** - Field filter active
- **📝 "exact phrase"** - Phrase search active

They help you see what you're searching for at a glance.

---

### Q: How do I change the theme?

**A:** Edit your config file:

```bash
vim ~/.config/hei-datahub/config.yaml
```

Add:
```yaml
theme: "gruvbox"  # or nord, dracula, monokai, etc.
```

Available themes: gruvbox, nord, dracula, monokai, catppuccin-mocha, solarized-dark, solarized-light, forest, ocean, tokyo-night, material, textual-dark

Then restart the app.

👉 [Theme customization guide](../how-to/09-change-theme.md)

---

### Q: How do I remap keybindings?

**A:** Edit your config file:

```bash
vim ~/.config/hei-datahub/config.yaml
```

Add:
```yaml
keybindings:
  edit_dataset: "ctrl+e"  # Change from 'e' to Ctrl+E
  search: "ctrl+f"         # Change from '/' to Ctrl+F
```

Then restart the app.

👉 [Keybinding customization guide](../how-to/08-customize-keybindings.md)

---

### Q: My edited dataset reverts after restarting the app. Why?

**A:** ✅ **Fixed in v0.57.1-beta** – This issue has been resolved. Edits now persist correctly across app restarts.

**If you're still experiencing this:**
1. Verify you're running v0.57.1 or later: `hei-datahub --version`
2. Check YAML file was updated:
   ```bash
   cat data/my-dataset/metadata.yaml
   ```
3. If issue persists, file a bug report with reproduction steps.

---

### Q: The app says "PR creation failed" but the PR was actually created. What's happening?

**A:** This is a known issue in v0.57.0-beta. The PR is created successfully on GitHub, but the app doesn't detect it.

**Workaround:**
1. Check GitHub: `https://github.com/YOUR_ORG/YOUR_REPO/pulls`
2. If PR exists, merge it normally
3. Ignore the error message in the app

**Status:** Fix in progress for future release.

---

### Q: Theme/keybinding changes don't work until I restart. Can I reload config?

**A:** ✅ **Fixed in v0.57.1-beta** – Config changes now apply automatically without restart.

**If you're still experiencing this:**
1. Verify you're running v0.57.1 or later: `hei-datahub --version`
2. Check that your config file is valid YAML
3. If issue persists, file a bug report

---

## Installation Issues

### Q: `hei-datahub` command not found

**A:** Virtual environment not activated or package not installed.

**Fix:**

```bash
source .venv/bin/activate
pip install -e .
```

---

### Q: Import error: `ModuleNotFoundError: No module named 'textual'`

**A:** Dependencies not installed.

**Fix:**

```bash
pip install -e .
# Or with uv:
uv sync --dev
```

---

### Q: Permission denied when running scripts

**A:** Scripts not executable.

**Fix:**

```bash
chmod +x scripts/*.sh
```

---

### Q: Python version too old

**A:** Hei-DataHub requires Python 3.9+.

**Fix:**

```bash
python --version  # Check current version
# Install Python 3.9+ via your package manager
```

---

## Database Issues

### Q: `sqlite3.OperationalError: unable to open database`

**A:** Database file corrupted or permissions issue.

**Fix:**

```bash
rm db.sqlite
hei-datahub  # Recreates database
```

---

### Q: Datasets not appearing after adding them

**A:** Search index not updated.

**Fix:**

```bash
hei-datahub reindex
```

---

### Q: Database file very large

**A:** Large number of datasets or inefficient FTS5 index.

**Fix:**

```bash
# Optimize FTS5 index
sqlite3 db.sqlite "INSERT INTO datasets_fts(datasets_fts) VALUES('optimize')"
```

---

## Search Issues

### Q: Search returns no results for common terms

**A:** Very common terms (e.g., "data") rank low in BM25.

**Fix:** Add more specific terms:

```
data temperature 2024
```

---

### Q: Expected dataset not found in search

**A:** Not indexed or different wording.

**Fix:**

1. Reindex:
    ```bash
    hei-datahub reindex
    ```
2. Try synonyms (e.g., "temp" vs. "temperature")
3. Check YAML file for typos

---

### Q: Search feels slow or laggy

**A:** Large dataset count or unoptimized index.

**Fix:**

```bash
# Optimize FTS5 index
sqlite3 db.sqlite "INSERT INTO datasets_fts(datasets_fts) VALUES('optimize')"
```

---

## Dataset Management

### Q: How do I delete a dataset?

**A:** Remove directory and reindex:

```bash
rm -rf data/<dataset-id>/
hei-datahub reindex
```

---

### Q: Validation error: "ID must match pattern"

**A:** ID contains uppercase or invalid characters.

**Fix:**

- Leave ID field **empty** to auto-generate
- Or use only lowercase, digits, dashes, underscores (must start with alphanumeric)

---

### Q: Auto-generated ID too long

**A:** Dataset name too long.

**Fix:**

- Shorten the dataset name
- Or manually specify a shorter ID (lowercase, dashes/underscores only)

---

## GitHub Integration

💡 **New!** See the comprehensive [GitHub Settings Guide](../how-to/04-settings.md) for detailed PAT setup instructions.

### Q: "GitHub Not Connected" after configuring

**A:** PAT invalid or missing `repo` scope.

**Fix:**

1. Regenerate PAT at [GitHub Tokens](https://github.com/settings/tokens)
2. Select `repo` scope (or `Contents` + `Pull requests` for fine-grained tokens)
3. Re-enter in Settings (++s++)

📖 [Detailed PAT setup guide](../how-to/04-settings.md#step-1-create-a-personal-access-token-pat)

---

### Q: PR creation fails with "Permission denied"

**A:** PAT doesn't have write access to repo.

**Fix:**

1. Check PAT scopes include `repo` (classic) or `Contents: Read and write` + `Pull requests: Read and write` (fine-grained)
2. Ensure you have write access to the repository
3. Regenerate PAT if needed

📖 [Troubleshoot token issues](../how-to/04-settings.md#troubleshooting)

---

### Q: PR created but empty

**A:** Auto-stash may have failed or no changes detected.

**Fix:**

1. Check Outbox (++p++) for failed tasks
2. Manually commit changes:
    ```bash
    git add data/<dataset-id>/metadata.yaml
    git commit -m "Add dataset: <name>"
    git push
    ```

---

### Q: PAT not saved (keyring error)

**A:** Keyring service not available.

**Fix:**

**Linux:**

```bash
# Install keyring backend
sudo apt install gnome-keyring  # GNOME
# or
sudo apt install kwalletmanager  # KDE
```

**macOS/Windows:** Keyring is built-in.

---

## UI / TUI Issues

### Q: Terminal too small warning

**A:** Terminal size below minimum (80x24).

**Fix:**

- Resize terminal to at least 100x30 for best experience

---

### Q: Colors look wrong

**A:** Terminal doesn't support 256 colors or true color.

**Fix:**

- Use a modern terminal emulator (Alacritty, iTerm2, GNOME Terminal, Windows Terminal)
- Check `$TERM` variable:
    ```bash
    echo $TERM  # Should be xterm-256color or similar
    ```

---

### Q: ++ctrl+s++ doesn't work (terminal hangs)

**A:** Terminal flow control enabled (XOFF/XON).

**Fix:**

```bash
stty -ixon
```

Add to `~/.bashrc` or `~/.zshrc` to make permanent.

---

### Q: Vim keybindings (j/k) not working

**A:** Focus not on results table.

**Fix:**

- Press ++enter++ after searching to focus results table
- Or press ++escape++ to exit insert mode

---

## Performance Issues

### Q: TUI startup slow

**A:** Large dataset count or first-run indexing.

**Expected:**

- First run: ~5 seconds (indexing example datasets)
- Subsequent runs: ~1 second

**If consistently slow:**

```bash
# Optimize database
sqlite3 db.sqlite "VACUUM; INSERT INTO datasets_fts(datasets_fts) VALUES('optimize')"
```

---

### Q: Dataset details load slowly

**A:** Very large `description` field or network latency (if fetching remote data).

**Fix:**

- Limit description to 2-4 sentences
- Avoid embedding large data blobs in metadata

---

## Configuration Issues

### Q: Config changes not applied

**A:** Config cached in memory.

**Fix:**

Restart TUI:

```bash
hei-datahub
```

---

### Q: Can't find config file

**A:** Config file location:

```bash
echo $PWD/.datahub_config.json
```

**If missing:**

- Create manually or via Settings screen (++s++)

---

## Error Messages

### `KeyError: 'id'`

**Cause:** Metadata missing required `id` field.

**Fix:** Ensure all YAML files have `id` field, then reindex.

---

### `jsonschema.ValidationError: 'description' is a required property`

**Cause:** Metadata missing required field.

**Fix:** Add missing fields to YAML file:

```yaml
description: "Your description here"
```

---

### `UnicodeDecodeError`

**Cause:** YAML file has invalid encoding.

**Fix:** Ensure YAML files are UTF-8 encoded:

```bash
file data/<dataset-id>/metadata.yaml
# Should show: UTF-8 Unicode text
```

---

### `GitCommandError: git is not installed`

**Cause:** Git not installed or not in PATH.

**Fix:**

```bash
# Check git
which git

# Install if missing (Ubuntu/Debian)
sudo apt install git
```

---

## Data / YAML Issues

### Q: Multi-line strings in YAML not displaying correctly

**A:** Use block scalar (`|`) for multi-line strings:

```yaml
description: |
  Line 1
  Line 2
  Line 3
```

---

### Q: YAML syntax error when loading dataset

**A:** Invalid YAML syntax.

**Fix:**

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('data/<dataset-id>/metadata.yaml'))"
```

**Common issues:**

- Missing quotes around strings with special chars (`:`, `#`)
- Incorrect indentation (use 2 spaces, not tabs)

---

### Q: Date format rejected

**A:** Date must be ISO 8601 (`YYYY-MM-DD`).

**Fix:**

```yaml
date_created: '2024-10-04'  # Correct
# Not: '10/04/2024' or '04-Oct-2024'
```

---

## Platform-Specific Issues

### Windows: `FileNotFoundError` when launching

**Cause:** Virtual environment activation failed.

**Fix:**

```powershell
.venv\Scripts\activate
```

---

### macOS: Keychain access denied

**Cause:** Keychain locked or permissions issue.

**Fix:**

1. Open Keychain Access app
2. Unlock "login" keychain
3. Grant Python access to keychain when prompted

---

### Linux: `ModuleNotFoundError: 'gi'` (for keyring)

**Cause:** Missing system packages.

**Fix:**

```bash
sudo apt install python3-gi python3-secretstorage
```

---

## Getting More Help

### Check Logs

**Location:** `~/.mini-datahub/logs/hei-datahub.log`

**View:**

```bash
tail -f ~/.mini-datahub/logs/hei-datahub.log
```

---

### Enable Debug Logging

**Settings:**

```json
{
  "debug_logging": true
}
```

**Or:**

Press ++s++ → Set "Debug Logging" → ++ctrl+s++

---

### Report an Issue

**Before reporting:**

1. Check this FAQ
2. Search [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
3. Check logs for error messages

**When reporting:**

- Hei-DataHub version (`hei-datahub --version`)
- OS and Python version
- Full error message / stack trace
- Steps to reproduce

**Create issue:** [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues/new)

---

## Tips for Avoiding Issues

1. **Keep virtual environment activated** when running commands
2. **Reindex after manual YAML edits** (`hei-datahub reindex`)
3. **Use auto-generated IDs** (leave ID field empty)
4. **Validate YAML syntax** before committing
5. **Back up `db.sqlite`** before major changes
6. **Use consistent naming** for projects and data types
7. **Test GitHub integration** with a test repo first

---

## Known Limitations (v0.57.x beta)

- **No deletion from TUI:** Must remove dataset directory manually (planned for v0.58)
- **No bulk operations:** Add/edit one dataset at a time (planned for v0.60)
- **No export/import:** Can't bulk export to JSON/CSV (planned for v0.60)
- **No array field editing:** Can't edit `schema_fields` or arrays in edit mode (planned for v0.58)
- **No conflict detection:** Duplicate keybindings not detected (planned for v0.58)
- **No hot-reload:** Theme/keybinding changes require restart (planned for v0.58)

**Planned for future releases.**

---

## Next Steps

- **[GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)** — Report bugs or request features
- **[What's New](../whats-new/0.57-beta.md)** — See what's new in the latest release
