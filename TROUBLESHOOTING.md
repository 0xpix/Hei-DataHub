# Troubleshooting Guide

## Common Issues & Solutions

### Installation Issues

#### `uv: command not found`

**Problem:** uv is not installed.

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

#### `Import "textual" could not be resolved`

**Problem:** Dependencies not installed yet.

**Solution:**
```bash
cd /home/pix/Github/Hei-DataHub
uv sync --python /usr/bin/python --dev
source .venv/bin/activate
```

---

### Runtime Errors

#### `AttributeError: type object 'Input' has no attribute 'Focused'`

**Status:** ✅ **FIXED** in latest version

**Solution:** Pull latest changes. This was caused by using non-existent Textual events. Now uses explicit mode management.

#### `Database errors on startup`

**Problem:** Database schema incompatible or corrupted.

**Solution:**
```bash
# Delete old database
rm db.sqlite

# Reindex from YAML files
mini-datahub reindex

# Or let TUI rebuild on startup
mini-datahub
```

#### `Search not finding datasets`

**Problem:** FTS index out of sync with YAML files.

**Solution:**
```bash
mini-datahub reindex
```

#### `No datasets visible on startup`

**Problem:** No YAML files in `data/` directory.

**Solution:**
1. Check `data/` directory exists and has subdirectories with `metadata.yaml`
2. Add example dataset:
   ```bash
   mkdir -p data/test-dataset
   # Create metadata.yaml with required fields
   ```
3. Run reindex: `mini-datahub reindex`

---

### Search Issues

#### Partial words not finding results

**Problem:** Database needs reindex with new prefix-enabled schema.

**Solution:**
```bash
mini-datahub reindex
```

**Verify:** Type "wea" in search - should find "weather" datasets.

#### Search feels laggy

**Symptoms:** Delay between keystrokes and results.

**Cause:** Debouncing is set to 150ms (intentional to prevent query spam).

**If needed:** Adjust `_debounce_timer` delay in `mini_datahub/tui.py` line ~123.

---

### UI Issues

#### Focus jumps to results while typing

**Status:** ✅ **FIXED** in latest version

**Verify:**
1. Launch TUI
2. Press `/` to focus search
3. Type "weather" (6 keystrokes)
4. Focus should stay in search input throughout

#### Form fields cut off on small terminal

**Status:** ✅ **FIXED** - form now fully scrollable with buttons always visible

**Multiple scroll options:**
1. **Keyboard:**
   - `Ctrl+d` / `Ctrl+u` - Scroll half-page down/up
   - `Page Down` / `Page Up` - Scroll half-page down/up
   - `j` / `k` - Navigate fields (auto-scrolls into view)
   - `G` - Jump directly to Save/Cancel buttons at bottom

2. **Mouse:**
   - Scroll wheel - Scroll up/down naturally

3. **Terminal resize** (if needed):
   ```bash
   # Resize terminal to at least 24 rows
   resize -s 24 80
   ```

**If Save/Cancel buttons disappear:**
- Use `G` (capital G) to jump to bottom
- Scroll down with `Ctrl+d` or mouse wheel
- Buttons have extra padding and are always reachable via scroll

**If scrolling still doesn't work:** Pull latest changes - scroll improvements added in v2.0.1+

#### Keybindings not working

**Check:**
1. Are you in the right mode? (Normal vs Insert)
   - In search field: Insert mode (green) - only `Esc` works
   - In results: Normal mode (cyan) - all vim keys work
2. Press `?` to see help screen with all keybindings

---

### Clipboard Issues

#### `y` (yank) doesn't copy to clipboard

**Linux:** Install clipboard support:
```bash
# X11
sudo apt install xclip

# Wayland
sudo apt install wl-clipboard
```

**macOS/Windows:** Should work out of the box with `pyperclip`.

#### Clipboard copy shows error

**Check:** `pyperclip` installed:
```bash
pip list | grep pyperclip
# If missing:
uv add pyperclip
```

---

### Network Issues

#### URL probe fails / times out

**Cause:** Network unreachable or slow server.

**Solution:**
- Check internet connection
- URL probe has 10s timeout (intentional)
- Just skip probe and enter format/size manually

---

### Validation Errors

#### "Dataset Name is required" even though filled

**Check:**
1. Field actually has content (not just spaces)
2. Focus is in the field (not just clicked)
3. Press `Ctrl+S` to save (not just clicking Save button in some cases)

#### "Invalid ID format"

**Requirements:**
- Lowercase only
- Alphanumeric plus dashes/underscores
- No spaces or special characters

**Examples:**
- ✅ `weather-data-2024`
- ✅ `nyc_taxi_trips`
- ❌ `Weather Data` (spaces)
- ❌ `NYC-Taxi!` (special char)

---

### Performance Issues

#### TUI slow with many datasets

**If >1000 datasets:**
- Search should still be <200ms
- Check `data/` directory isn't too large
- Consider archiving old datasets

**Debug:**
```bash
# Check dataset count
ls -d data/*/ | wc -l

# Check DB size
ls -lh db.sqlite
```

---

### Testing / Development Issues

#### Tests failing after update

**Solution:**
```bash
# Reinstall dependencies
uv sync --python /usr/bin/python --dev
source .venv/bin/activate

# Rebuild database
rm db.sqlite
mini-datahub reindex

# Run tests
pytest -v
```

#### Import errors during development

**Solution:**
```bash
# Ensure virtual environment activated
source .venv/bin/activate

# Reinstall in editable mode
uv sync --dev
```

---

## Diagnostic Commands

```bash
# Check Python version (need 3.9+)
python --version

# Check if uv is installed
uv --version

# Check virtual environment
which python  # Should show .venv/bin/python

# Check installed packages
pip list

# Check data directory structure
tree data/

# Check database exists
ls -lh db.sqlite

# Test CLI loads
mini-datahub --help

# Test reindex
mini-datahub reindex

# Launch with error output visible
mini-datahub 2>&1 | tee tui_output.log
```

---

## Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   mini-datahub 2>&1 | tee debug.log
   ```

2. **Run test checklist:** See `TEST_CHECKLIST.md`

3. **Verify installation:**
   ```bash
   python -m py_compile mini_datahub/*.py
   pytest -v
   ```

4. **Report issue with:**
   - OS and Python version
   - Error message (full traceback)
   - Steps to reproduce
   - Output of diagnostic commands above

---

## Known Limitations

- **gg keybinding:** Some terminals interpret as single 'g'
- **Clipboard:** Requires X11/Wayland on Linux
- **URL probe:** Requires network, 10s timeout
- **Search tokens:** <2 chars ignored (too broad)

---

**Last Updated:** 2025-10-03
**Version:** TUI v2.0
