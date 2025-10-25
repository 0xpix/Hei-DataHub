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
| / | Focus Search | Enter insert mode in search box |
| j | Move Down | Select next dataset in results |
| k | Move Up | Select previous dataset in results |
| g+g | Jump to Top | First dataset in list |
| shift+g | Jump to Bottom | Last dataset in list |
| enter / o | Open Details | View selected dataset |
| a | Add Dataset | Open Add Dataset form |
| s | Settings | Configure WebDAV|
| u | Updates | Update the app |
| r | Refresh | Reload dataset list |
| Ctrl+q | Quit | Exit Hei-DataHub |
| escape | Clear/Exit | Clear search or exit insert mode |
| ? | Help | Show keyboard shortcuts |

---

### Details Screen

| Key | Action | Description |
|-----|--------|-------------|
| escape/b | Back | Return to Home screen |
| e | Edit | Edit a dataset |
| c | Copy Source | Copy source URL/snippet to clipboard |
| o | Open URL | Open source URL in browser (if valid URL) |
| q | Quit | Exit Hei-DataHub |

---

### Add/Edit Dataset Form

| Key | Action | Description |
|-----|--------|-------------|
| tab | Next Field | Move to next input field |
| shift+tab | Previous Field | Move to previous input field |
| ctrl+s | Save | Save dataset and return to Home |
| escape | Cancel | Discard changes and return to Home |

---

### Settings Screen

| Key | Action | Description |
|-----|--------|-------------|
| tab | Next Field | Move to next setting |
| shift+tab | Previous Field | Move to previous setting |
| ctrl+s | Save | Save configuration |
| escape | Cancel | Discard changes |

---

## Dataset Detail Flow

Understanding the navigation flow helps you move efficiently:

```
Home Screen (Search)
  ↓ (Enter or o)
Details Screen
  ↓ (Escape)
Home Screen
```

**Example flow:**

```
Home → Search → Details → Edit → Save
```

For detailed instructions, see:

- **[The Basics](03-the-basics.md)** — Understanding datasets and search
- **[Tutorial: Configure WebDAV integration](../how-to/04-settings.md)** — Enable HeiBox integration
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

---

## Add Dataset Workflow - (Will be changed in future releases)

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

- **Push screen:** a (Add), s (Settings)
- **Pop screen:** escape or action completion (e.g., Save)

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

### Copy/open Source for Quick Reference

On Details Screen:

```
c → Copies source URL/snippet to clipboard
o -> Opens the source in the browser
```

---

## Customization

- **[Tutorial: Customize your Keybinds](../how-to/08-customize-keybindings.md) - Customize your keybinds

---

## Next Steps

- **[Learn the basics](03-the-basics.md)** — Understand datasets, fields, and metadata
- **[Tutorial: Configure WebDAV integration](../how-to/04-settings.md)** — Enable HeiBox integration
- **[Tutorial: Create your first dataset](../how-to/05-first-dataset.md)** — Learn how to create a dataset
