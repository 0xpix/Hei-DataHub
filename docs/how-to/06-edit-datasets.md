# How to Edit Datasets

**Requirements:** Hei-DataHub 0.59-beta or later, WebDAV configured

**Goal:** Change dataset information directly in the app with instant cloud sync.

**Time:** 2-5 minutes

---

## Overview

Editing datasets in Hei-DataHub v0.59:

- ✅ **Edit inline** - No manual YAML editing needed
- ✅ **Instant cloud sync** - Changes uploaded to Heibox immediately
- ✅ **Team visibility** - Everyone sees updates in real-time
- ✅ **Auto-indexing** - Search results update automatically

---

## Step-by-Step

### 1. Find the Dataset

Launch the app and search for the dataset you want to edit:

```bash
hei-datahub
```

- Type in the search box to filter datasets
- Use arrow keys or `j`/`k` to navigate
- Press `Enter` to open the details screen

---

### 2. Enter Edit Mode

Once you're viewing the dataset details:

1. Press **`e`** to start editing
2. You'll see the edit form with all editable fields
3. The first field will be selected

**What you'll see:**
```
┌─────────────────────────────────────────┐
│ Edit Dataset: my-dataset                │
├─────────────────────────────────────────┤
│ Name:        [my-dataset____________]   │
│ Description: [A sample dataset______]   │
│ Source:      [https://example.com___]   │
│ ...                                     │
└─────────────────────────────────────────┘
```

---

### 3. Edit Fields

**Move between fields:**

- **`Tab`** – Next field
- **`Shift+Tab`** – Previous field
- **Mouse click** – Jump to any field

**Edit text:**

- Type normally to change values
- **`Ctrl+a`** – Select all text in field
- **`Ctrl+c` / `Ctrl+v`** – Copy/paste

**Undo/Redo:**

- **`Ctrl+z`** – Undo last change
- **`Ctrl+Shift+z`** – Redo

---

### 4. Save Your Changes

When you're done editing:

1. Press **`Ctrl+s`** to save
2. You'll see: "Uploading to Heibox..."
3. Success message: "✅ Dataset saved and synced to cloud"
4. Details view refreshes automatically

**What happens when you save:**

- Changes uploaded to Heibox immediately
- Search index updated automatically
- **Team members see changes instantly** (no waiting)
- Cloud becomes the source of truth

**Note:** If Heibox is not connected, changes are saved to local buffer and will sync when connection is restored.

---

### 5. Cancel (If Needed)

Changed your mind?

1. Press **`Esc`** to cancel
2. If you have unsaved changes, you'll see a confirmation dialog:
   ```
   Y to discard changes, N to continue editing
   ```
3. Choose "Y" to exit without saving

---

## Editable Fields

| Field | What it does | Example |
|-------|-------------|---------|
| **Name** | Dataset identifier (must be unique) | `climate-data-2024` |
| **Description** | What the dataset contains | `Monthly temperature readings` |
| **Source** | Where the data came from | `https://example.com/data` |
| **Storage Location** | File path or URL | `s3://bucket/data.csv` |
| **Format** | File format | `csv`, `parquet`, `json` |
| **Size** | File size in bytes | `1048576` (1 MB) |
| **Data Type** | Kind of data | `raster`, `vector`, `tabular` |
| **Project** | Associated project name | `climate-research` |
| **Date Created** | When dataset was made | `2024-01-15` |
| **Date Modified** | Last update | `2024-03-20` |

!!! important "Field validation"

- **Name** must be unique across all datasets
- **Dates** must be in `YYYY-MM-DD` format
- **Size** must be a number (bytes)
- Invalid values are highlighted when you try to save

---

## Tips & Tricks

### ✅ Save Often
Press `Ctrl+s` frequently. Each save syncs to Heibox immediately.

### ✅ Use Undo
Made a typo? `Ctrl+z` works across all fields (until you save).

### ✅ Check Validation
If a field turns red or shows an error, fix it before saving.

### ✅ Instant Team Updates
After saving, team members with Heibox access see changes immediately in their TUI.

### ✅ Offline Editing
If Heibox is offline, edits are buffered locally and sync when connection is restored.

---

## Example Walkthrough

Let's edit a dataset called `weather-2024`:

1. **Launch app:** `hei-datahub`
2. **Verify Heibox status:** Look for ` Synced to Hei-box` (green)
3. **Search:** Type `weather`
4. **Select:** Press `Enter` on `weather-2024`
5. **Edit:** Press `e`
6. **Change description:** Tab to "Description", type `Updated weather data for 2024`
7. **Change format:** Tab to "Format", type `parquet` (was `csv`)
8. **Save:** Press `Ctrl+s`
9. **Wait for sync:** "Uploading to Heibox..." → "✅ Dataset saved and synced to cloud"
10. **Verify:** Details screen shows new values
11. **Team sees it:** Anyone with Heibox access sees updates immediately

Done! 🎉

---

## Next Steps

- **[Search for your updated dataset](07-search-advanced.md)** using field filters
- **[Customize keyboard shortcuts](08-customize-keybindings.md)** (change `e` to something else)
- **[Learn about themes](09-change-theme.md)** for visual customization

---

## Related

- **[Settings Guide](04-settings.md)** - WebDAV configuration
- **[Privacy & Security](../privacy-and-security.md)** - How data is stored
- **[Keyboard shortcuts](../reference/keybindings.md)** - Complete shortcut reference
- **[Troubleshooting](../help/troubleshooting.md)** - Common issues
- **[What's New in 0.59-beta](../whats-new/0.59-beta.md)** - Latest features
