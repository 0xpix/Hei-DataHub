# Test Checklist - TUI v2.0

## Black-Box Testing Guide

This document provides a comprehensive test plan for validating all features and fixes in the enhanced Mini Hei-DataHub TUI.

---

## Setup

```bash
# Fresh installation
git clone <repo-url>
cd Hei-DataHub
uv sync --python /usr/bin/python --dev
source .venv/bin/activate
mini-datahub
```

---

## Test Cases

### ✅ 1. Incremental Prefix Search

**Objective:** Verify that partial word search works with live updates.

**Steps:**
1. Launch `mini-datahub`
2. Press `/` to focus search
3. Type slowly: `w` → `we` → `wea`
4. Observe results update after each keystroke (with ~150ms delay)

**Expected:**
- After typing "w": Shows datasets with words starting with "w"
- After typing "we": Narrows to "we*" matches (weather, web, etc.)
- After typing "wea": Shows "weather", "wealth", etc.
- Results include highlighted snippets with `<b>` tags removed
- Search input keeps focus throughout typing
- Mode indicator shows "Insert" (green)

**Pass Criteria:**
- ✅ Typing "wea" shows datasets containing "weather"
- ✅ Results update live without page reload
- ✅ No lag or UI freeze during typing

---

### ✅ 2. Row Selection (No RowKey Leak)

**Objective:** Verify that selecting a dataset opens its details correctly.

**Steps:**
1. In Home screen with search results visible
2. Use `j/k` to navigate to a dataset row
3. Press `Enter` or `o` to open details
4. Alternatively, click a row with mouse

**Expected:**
- Details screen appears with correct dataset metadata
- No text like `<textual.widgets._data_table.RowKey object at 0x...>` anywhere
- All fields (ID, name, description, source, etc.) display correctly

**Pass Criteria:**
- ✅ Details screen shows proper dataset information
- ✅ No Python object representation leaks to UI
- ✅ Works consistently for all datasets

---

### ✅ 3. Scrollable Add Data Form

**Objective:** Verify form scrollability on small terminals with multiple scroll methods.

**Steps:**
1. Resize terminal to small height (24 rows): `resize -s 24 80`
2. Press `A` to open Add Data form
3. **Test keyboard scrolling:**
   - Use `Ctrl+d` to scroll down
   - Use `Ctrl+u` to scroll up
   - Try `Page Down` / `Page Up` (alternative method)
4. **Test mouse scrolling:**
   - Use mouse wheel to scroll up/down
   - Verify smooth scrolling
5. **Test auto-scroll:**
   - Use `j/k` to navigate between fields
   - Verify focused field scrolls into view automatically
6. **Test jump commands:**
   - Use `gg` to jump to first field
   - Use `G` to jump to Save button
7. Verify all fields are reachable

**Expected:**
- Form scrolls smoothly with `Ctrl+d/u`, `Page Down/Up`, and mouse wheel
- "Save Dataset" and "Cancel" buttons always accessible
- Fields automatically scroll into view when focused with `j/k`
- No fields cut off or unreachable
- Scrollbar visible on right side

**Pass Criteria:**
- ✅ All fields accessible via scroll on 24-row terminal
- ✅ Multiple scroll methods work (keyboard, mouse, auto)
- ✅ Save/Cancel buttons reachable
- ✅ Scrolling is smooth and predictable
- ✅ Scroll works even when focus is in input field

---

### ✅ 4. Search Input Focus Retention

**Objective:** Verify search input keeps focus while typing.

**Steps:**
1. Launch TUI
2. Press `/` to focus search
3. Type slowly: "weather" (6 keystrokes)
4. Observe focus indicator and mode

**Expected:**
- Focus stays in search input for all 6 keystrokes
- Mode indicator stays "Insert" (green) throughout
- Results update in background without stealing focus
- User can type continuously without interruption
- Table cursor does NOT move during typing

**Pass Criteria:**
- ✅ User can type entire word "weather" uninterrupted
- ✅ Focus never jumps to results table automatically
- ✅ Results update live in background
- ✅ Only explicit action (Enter, Esc, Tab) changes focus

---

### ✅ 5. Zero-Query Dataset List

**Objective:** Verify all datasets show before typing.

**Steps:**
1. Launch `mini-datahub` (fresh start)
2. Observe Home screen before typing anything
3. Note the label text and table contents
4. Press `/` and type "weather"
5. Clear search (Ctrl+A, Delete or clear manually)
6. Observe table returns to full list

**Expected:**
- **On startup:** Label shows "All Datasets (N total)"
- Table shows all datasets sorted by update time
- No empty table state
- **After typing:** Label changes to "Search Results (M found)"
- **After clearing:** Returns to "All Datasets" view

**Pass Criteria:**
- ✅ Startup shows all available datasets
- ✅ Typing filters list dynamically
- ✅ Clearing search restores full list
- ✅ Dataset count accurate in label

---

### ✅ 6. Neovim-Style Keybindings

#### 6A. Home Screen Navigation

**Steps:**
1. Launch TUI (table has focus in Normal mode)
2. Test keybindings:
   - `j` - cursor down
   - `k` - cursor up
   - `gg` - jump to first row
   - `G` - jump to last row
   - `/` - focus search (Insert mode)
   - `Esc` - exit Insert mode
   - `o` or `Enter` - open details
   - `A` - add dataset
   - `?` - show help
   - `q` - quit (after Esc from search)

**Expected:**
- All keys work as documented
- Mode indicator updates (Normal/Insert)
- Navigation smooth and responsive

**Pass Criteria:**
- ✅ All listed keybindings functional
- ✅ No key conflicts or ignored inputs

#### 6B. Details Screen

**Steps:**
1. Open any dataset details
2. Test keybindings:
   - `y` - copy source to clipboard (check with paste)
   - `o` - open URL in browser (if source is URL)
   - `q` or `Esc` - back to search

**Expected:**
- `y` shows toast "✓ Source copied to clipboard!"
- `o` opens browser if URL, warns if not
- `q/Esc` returns to previous screen

**Pass Criteria:**
- ✅ Clipboard copy works
- ✅ URL opening works for valid URLs
- ✅ Back navigation works

#### 6C. Add Data Form

**Steps:**
1. Press `A` to open form
2. Test keybindings:
   - `j` / `k` - next/previous field
   - `gg` - first field (Dataset Name)
   - `G` - last element (Save button)
   - `Ctrl+d` / `Ctrl+u` - scroll down/up
   - `Ctrl+S` - save (test with valid data)
   - `q` or `Esc` - cancel

**Expected:**
- Field navigation works
- Scrolling works on small terminals
- Save creates dataset and shows details
- Cancel returns to home

**Pass Criteria:**
- ✅ All navigation keys work
- ✅ Save/cancel work correctly

#### 6D. Help Screen

**Steps:**
1. Press `?` from any screen
2. Observe help content
3. Press `q` or `Esc` to close

**Expected:**
- Help screen shows all keybindings organized by screen
- Markdown formatting renders (bold, colors)
- Closing returns to previous screen

**Pass Criteria:**
- ✅ Help content comprehensive and readable
- ✅ Close action works

---

### ✅ 7. Metadata Validation

**Objective:** Verify inline validation prevents invalid data.

**Steps:**
1. Press `A` to add dataset
2. Leave Dataset Name empty, try to save (`Ctrl+S`)
3. Observe error message
4. Fill name, leave Description empty, try to save
5. Test with invalid date format (e.g., "2024-13-45")
6. Test with invalid ID (e.g., "My Dataset!")

**Expected:**
- Red error messages appear below form
- Cursor moves to problematic field
- No YAML file written until validation passes
- Clear, helpful error messages

**Pass Criteria:**
- ✅ Required fields enforced
- ✅ Date validation works
- ✅ ID format validation works
- ✅ No invalid data written to disk

---

### ✅ 8. Reindex from Disk

**Objective:** Verify database rebuild from YAML files.

**Steps:**
1. Delete `db.sqlite` file (if exists): `rm db.sqlite`
2. Ensure `data/` directory has some datasets
3. Run: `mini-datahub reindex`
4. Launch TUI and search for a known dataset

**Expected:**
- Reindex command reports "Indexed N datasets"
- Search finds datasets from YAML files
- No errors during reindex
- Database file recreated

**Pass Criteria:**
- ✅ Reindex completes without errors
- ✅ All datasets searchable after reindex
- ✅ Search results match YAML file content

---

### ✅ 9. URL Probe Feature

**Objective:** Verify HTTP HEAD probe infers format/size.

**Steps:**
1. Press `A` to add dataset
2. Enter a valid public URL in Source (e.g., CSV file URL)
3. Click "Probe URL" button
4. Observe File Format and Size fields

**Expected:**
- Probe status shows "Probing..." then "✓ Probed: <content-type>"
- File Format auto-filled if detected (CSV, JSON, etc.)
- Size auto-filled with human-readable size (MB, GB)
- Toast notification on success
- Timeout/error handled gracefully (shows "✗ Failed")

**Pass Criteria:**
- ✅ Valid URL probed successfully
- ✅ Format/size inferred correctly
- ✅ Non-URL or invalid URL shows appropriate error
- ✅ Timeout handled (doesn't hang UI)

---

### ✅ 10. Performance with Many Datasets

**Objective:** Verify smooth operation with ~100-1000 datasets.

**Steps:**
1. Generate test datasets (script or manual)
2. Run `mini-datahub reindex`
3. Search for common terms
4. Navigate results with `j/k`
5. Observe response time

**Expected:**
- Search completes in < 200ms for 1000 datasets
- UI remains responsive during search
- No lag when navigating results
- Memory usage reasonable

**Pass Criteria:**
- ✅ Search fast even with large dataset count
- ✅ No UI freezing or stuttering
- ✅ Debouncing prevents search spam

---

## Smoke Tests (Quick Validation)

Run these for rapid validation after changes:

```bash
# 1. Fresh install works
uv sync --python /usr/bin/python --dev && source .venv/bin/activate && mini-datahub

# 2. Search works
# - Press `/`, type "test", see results

# 3. Add dataset works
# - Press `A`, fill required fields, `Ctrl+S`

# 4. Navigation works
# - Use `j/k`, `gg`, `G`, `o`, `q`

# 5. Reindex works
mini-datahub reindex
```

---

## Regression Prevention

Before committing changes, verify:

1. ✅ No syntax errors: `python -m py_compile mini_datahub/*.py`
2. ✅ Tests pass: `pytest`
3. ✅ Linting clean: `ruff check mini_datahub`
4. ✅ Formatting consistent: `black mini_datahub`
5. ✅ Type checking: `mypy mini_datahub` (optional)

---

## Known Limitations

- **gg keybinding:** Textual may interpret as single 'g' press (mode-dependent)
- **Clipboard on headless:** Requires X11/Wayland on Linux
- **URL probe:** Requires network; times out after 10s

---

## Reporting Issues

If any test fails, report with:
1. Test case number (e.g., "Test 4: Search Focus")
2. Expected vs actual behavior
3. Terminal size and OS
4. Steps to reproduce
5. Error messages or screenshots

---

**Last Updated:** 2025-10-03
**Version:** TUI v2.0
