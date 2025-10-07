# Navigation & Keyboard Shortcuts

Hei-DataHub is built for **keyboard-first workflows**. If you're familiar with Vim/Neovim, you'll feel right at home.
**TODO: Add the new shortcuts for settings, dataset details, etc**
---

## Philosophy

- **Normal Mode:** Navigate and trigger actions (like Vim's normal mode)
- **Insert Mode:** Edit text in search boxes and forms
- **Quick Actions:** Single-key shortcuts for common tasks
- **Vim-style Movement:** `j/k` for up/down, `gg/G` for top/bottom

---

## Common Shortcuts

### Home Screen (Search & Browse)

| Key | Action | Description |
|-----|--------|-------------|
| ++/++ | Focus Search | Enter insert mode in search box |
| ++j++ | Move Down | Select next dataset in results |
| ++k++ | Move Up | Select previous dataset in results |
| ++g+g++ | Jump to Top | First dataset in list |
| ++shift+g++ | Jump to Bottom | Last dataset in list |
| ++enter++ | Open Details | View selected dataset |
| ++o++ | Open Details | Alternative to Enter |
| ++a++ | Add Dataset | Open Add Dataset form |
| ++s++ | Settings | Configure GitHub, preferences |
| ++p++ | Outbox | View pending/failed PR tasks |
| ++u++ | Pull Updates | Sync from remote (if configured) |
| ++r++ | Refresh | Reload dataset list |
| ++Ctrl+q++ | Quit | Exit Hei-DataHub |
| ++escape++ | Clear/Exit | Clear search or exit insert mode |
| ++?++ | Help | Show keyboard shortcuts |

---

### Details Screen

| Key | Action | Description |
|-----|--------|-------------|
| ++escape/b++ | Back | Return to Home screen |
| ++e++ | Edit | Edit a dataset |
| ++Shift+P++ | Publish as Pull Request (PR) | Publish the dataset |
| ++c++ | Copy Source | Copy source URL/snippet to clipboard |
| ++o++ | Open URL | Open source URL in browser (if valid URL) |
| ++q++ | Quit | Exit Hei-DataHub |

---

### Add/Edit Dataset Form

| Key | Action | Description |
|-----|--------|-------------|
| ++tab++ | Next Field | Move to next input field |
| ++shift+tab++ | Previous Field | Move to previous input field |
| ++ctrl+s++ | Save | Save dataset and return to Home |
| ++escape++ | Cancel | Discard changes and return to Home |

---

### Settings Screen

| Key | Action | Description |
|-----|--------|-------------|
| ++tab++ | Next Field | Move to next setting |
| ++shift+tab++ | Previous Field | Move to previous setting |
| ++ctrl+s++ | Save | Save configuration |
| ++escape++ | Cancel | Discard changes |

---

### Outbox Screen

| Key | Action | Description |
|-----|--------|-------------|
| ++r++ | Retry Task | Retry failed PR task |
| ++d++ | Delete Task | Remove task from outbox |
| ++escape++ | Back | Return to Home screen |

---

## Dataset Detail Flow

Understanding the navigation flow helps you move efficiently:

```
Home Screen (Search)
  ↓ (Enter or o)
Details Screen
  ↓ (Escape or b)
Home Screen
```

**Example flow:**

```
Home → Search → Details → Edit → Save → PR
```

For detailed instructions, see:

- **[The Basics](03-the-basics.md)** — Understanding datasets and search
- **[Tutorial: Configure GitHub integration](../how-to/04-settings.md)** — Enable PR workflow
- **[Tutorial: Create your first dataset](../how-to/05-first-dataset.md)** — Learn how to create a dataset

---

## Search Workflow

### Basic Search

```
1. Press / from anywhere in Home Screen
2. Type your query (e.g., "climate")
3. Results update in real-time (150ms debounce)
4. Press Enter to move focus to results
5. Navigate with j/k or arrow keys
```

### Clear Search

```
1. Press Escape once → Exit insert mode
2. Press Escape again → Clear search results
```

### Search Tips

- **Partial matching:** "clim" finds "climate", "climatic"
- **Multi-word:** "burned area" finds datasets with both words
- **Project search:** Searches `used_in_projects` field
- **Field matching:** Searches name, description, source, data types
- **Case-insensitive:** "MODIS" and "modis" are equivalent

---

## Add Dataset Workflow

Fast path to add a new dataset:

```
1. Press a from Home Screen
2. Fill required fields:
   - Dataset Name*
   - Description*
   - Source*
   - Storage Location*
3. Tab between fields
4. Leave ID empty to auto-generate from name
5. Press Ctrl+S to save
```

**Auto-generated ID example:**

- **Name:** "Global Weather Data 2024"
- **Auto-ID:** `global-weather-data-2024`

---

## Mode Indicator

The status bar shows your current mode:

| Indicator | Meaning |
|-----------|---------|
| **Mode: Normal** | Ready for shortcuts (j/k, /, a, etc.) |
| **Mode: Insert** | Typing in search box |

---

## Panel Navigation

Hei-DataHub has a single-column layout:

```
┌─────────────────────────────────────┐
│  Header: HEI DATAHUB                │  ← App title
├─────────────────────────────────────┤
│  Banner: ASCII logo                 │
│  Status: GitHub connection          │
│  Mode: Normal/Insert                │
├─────────────────────────────────────┤
│  Search Input                       │  ← Press / to focus
├─────────────────────────────────────┤
│  Results Table                      │  ← j/k to navigate
│  ┌─────────────────────────────┐    │
│  │ ID │ Name │ Description     │    │
│  └─────────────────────────────┘    │
├─────────────────────────────────────┤
│  Footer: Keyboard shortcuts         │  ← A: Add | S: Settings | Q: Quit
└─────────────────────────────────────┘
```

---

## Back/Forward Patterns

Hei-DataHub uses a **stack-based navigation model**:

- **Push screen:** ++a++ (Add), ++s++ (Settings), ++p++ (Outbox)
- **Pop screen:** ++escape++, ++b++, or action completion (e.g., Save)

**Example:**

```
Home → (a) → Add Dataset → (Ctrl+S) → Home
Home → (s) → Settings → (Escape) → Home
Home → (p) → Outbox → (Escape) → Home
```

---

## Power User Tips

### Jump to First/Last Dataset

```
gg      → Jump to first result
Shift+G → Jump to last result
```

### Rapid Dataset Review

```
Enter → (view details) → Escape → j → Enter → Escape → j
```

Use this pattern to quickly review multiple datasets.

### Search Without Losing Position

The search debounce (150ms) means you can type fast without lag. Results update smoothly as you type.

### Copy Source for Quick Reference

On Details Screen:

```
c → Copies source URL/snippet to clipboard
```

Paste into your terminal, notebook, or documentation.

---

## Customization

Currently, keybindings are **hardcoded** but follow Vim conventions. Future versions may support custom keymaps.

---

## Next Steps

- **[Learn the basics](03-the-basics.md)** — Understand datasets, fields, and metadata
- **[Tutorial: Configure GitHub integration](../how-to/04-settings.md)** — Enable PR workflow
- **[Tutorial: Create your first dataset](../how-to/05-first-dataset.md)** — Learn how to create a dataset
