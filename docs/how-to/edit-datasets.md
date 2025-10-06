# How to Edit Datasets

**Goal:** Change dataset information directly in the app without editing YAML files manually.

**Time:** 2-5 minutes
**Version:** 0.56-beta or later

---

## Before You Start

!!! note "What you'll need"
    - Hei-DataHub 0.56-beta or later installed
    - At least one dataset in your catalog
    - Write permissions to the `data/` folder

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

1. Press **`E`** (uppercase E) to start editing
2. You'll see the edit form with all editable fields
3. The first field (usually "Name") will be selected

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
- **`Ctrl+A`** – Select all text in field
- **`Ctrl+C` / `Ctrl+V`** – Copy/paste

**Undo/Redo:**
- **`Ctrl+Z`** – Undo last change
- **`Ctrl+Shift+Z`** – Redo

---

### 4. Save Your Changes

When you're done editing:

1. Press **`Ctrl+S`** to save
2. Wait for the success message: "✅ Dataset saved and reindexed"
3. The details view refreshes automatically

**What happens when you save:**
- Original YAML file is backed up
- New values are written to disk
- Database is automatically updated
- Search index is refreshed

---

### 5. Cancel (If Needed)

Changed your mind?

1. Press **`Esc`** to cancel
2. If you have unsaved changes, you'll see a confirmation dialog:
   ```
   Discard unsaved changes?
   [Yes] [No]
   ```
3. Choose "Yes" to exit without saving

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

## Common Tasks

### Change the Dataset Name

1. Press `E` to edit
2. Tab to the "Name" field
3. Type the new name
4. Press `Ctrl+S` to save

!!! warning "Name conflicts"
    If another dataset has the same name, you'll see an error. Choose a unique name.

---

### Update the Description

1. Press `E`
2. Tab to "Description"
3. Type your new description (can be multiple lines)
4. Press `Ctrl+S`

**Tip:** Descriptions support Markdown in some views (bold, italic, links).

---

### Fix a Broken Source URL

1. Press `E`
2. Find the "Source" field
3. Update or correct the URL
4. Press `Ctrl+S`

---

### Bulk Changes (Future)

Currently, you must edit datasets one at a time. Bulk editing is planned for version 0.60-beta.

---

## Tips & Tricks

### ✅ Save Often
Press `Ctrl+S` frequently. Each save creates a backup of the original file.

### ✅ Use Undo
Made a typo? `Ctrl+Z` works across all fields (until you save).

### ✅ Check Validation
If a field turns red or shows an error, fix it before saving.

### ✅ Close and Reopen
After saving, the details view refreshes automatically. You don't need to restart the app.

---

## Troubleshooting

### "Save failed" Error

**Symptom:** You press `Ctrl+S` but see an error message.

**Possible causes:**
1. **Name conflict** – Another dataset has the same name
2. **Invalid date format** – Use `YYYY-MM-DD`
3. **File permission error** – Check folder write permissions

**What to do:**
- Read the error message carefully
- Fix the highlighted field
- Try saving again

---

### Edited Dataset Reverts After Closing App

**Known issue in 0.57-beta:** Some users report changes disappear after restarting.

**Workaround:**
1. After editing, verify YAML file was updated:
   ```bash
   cat data/my-dataset/metadata.yaml
   ```
2. If YAML is correct but app shows old data, reindex:
   ```bash
   hei-datahub reindex
   ```

This issue is being investigated for 0.57.1.

---

### Edit Form Doesn't Scroll on Small Screens

**Known issue:** If your terminal is small, some fields may be hidden.

**Workarounds:**
- Resize your terminal to at least 80x24
- Use `Tab` to navigate to hidden fields
- Edit the YAML file manually for now

Scrollable edit forms coming in version 0.57-beta.

---

### Can't Edit Array Fields

**Example:** The `schema_fields` array (column definitions) is not editable in the form.

**Workaround:**
Edit these fields manually in the YAML file:
```bash
vim data/my-dataset/metadata.yaml
```

Array editing coming in a future release.

---

## Example Walkthrough

Let's edit a dataset called `weather-2024`:

1. Launch app: `hei-datahub`
2. Search: Type `weather`
3. Select: Press `Enter` on `weather-2024`
4. Edit: Press `E`
5. Change description: Tab to "Description", type `Updated weather data for 2024`
6. Change format: Tab to "Format", type `parquet` (was `csv`)
7. Save: Press `Ctrl+S`
8. Verify: Details screen shows new values

Done! 🎉

---

## Next Steps

- **[Search for your updated dataset](search-advanced.md)** using field filters
- **[Customize keyboard shortcuts](customize-keybindings.md)** (change `E` to something else)
- **[Learn about themes](change-theme.md)** for visual customization

---

## Related

- [Configuration reference](../12-config.md)
- [Keyboard shortcuts](../reference/keybindings.md)
- [Troubleshooting](../troubleshooting.md)
- [Changelog](../99-changelog.md#0560-beta)
