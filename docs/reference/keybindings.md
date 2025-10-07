# Keyboard Shortcuts Reference

Complete list of all keyboard shortcuts in Hei-DataHub v0.57.x beta.

**Tip:** Press `?` in the app to see context-aware shortcuts.

---

## Global Shortcuts

These work from any screen:

| Key | Action | Description |
|-----|--------|-------------|
| `?` | Help | Show help overlay with shortcuts |
| `q` | Quit | Exit application |
| `Ctrl+C` | Force quit | Emergency exit |
| `/` | Search | Focus search box (Home screen) |
| `s` | Settings | Open settings screen |
| `r` | Refresh | Refresh data without reindexing |
| `u` | Pull updates | Pull latest changes from Git |

**Tip:** Press `?` in the app to see context-aware shortcuts.
---

## Home Screen

### Navigation

| Key | Action | Description |
|-----|--------|-------------|
| `j` or `↓` | Move down | Select next dataset |
| `k` or `↑` | Move up | Select previous dataset |
| `g g` | Top | Jump to first dataset |
| `G` | Bottom | Jump to last dataset |
| `Ctrl+D` | Page down | Scroll down half page |
| `Ctrl+U` | Page up | Scroll up half page |

### Actions

| Key | Action | Description |
|-----|--------|-------------|
| `Enter` | Open | View dataset details |
| `a` | Add | Create new dataset |
| `/` | Search | Focus search box |
| `Esc` | Clear search | Clear search and show all datasets |

---

## Details Screen

| Key | Action | Description |
|-----|--------|-------------|
| `e` | Edit | Enter edit mode (Added in v0.56) |
| `p` | Publish | Create GitHub PR |
| `c` | Copy source | Copy source URL to clipboard |
| `o` | Open URL | Open source URL in browser |
| `Esc` | Back | Return to home screen |

---

## Edit Mode (Added in v0.56)

### Navigation

| Key | Action | Description |
|-----|--------|-------------|
| `Tab` | Next field | Move to next editable field |
| `Shift+Tab` | Previous field | Move to previous field |
| `↑` / `↓` | Scroll | Scroll through fields |

### Editing

| Key | Action | Description |
|-----|--------|-------------|
| `Ctrl+A` | Select all | Select all text in current field |
| `Ctrl+C` | Copy | Copy selected text |
| `Ctrl+V` | Paste | Paste from clipboard |
| `Ctrl+X` | Cut | Cut selected text |

### Actions

| Key | Action | Description |
|-----|--------|-------------|
| `Ctrl+S` | Save | Save changes and reindex |
| `Esc` | Cancel | Cancel editing (confirms if unsaved) |
| `Ctrl+Z` | Undo | Undo last change |
| `Ctrl+Shift+Z` | Redo | Redo undone change |

---

## Search Box

| Key | Action | Description |
|-----|--------|-------------|
| `/` | Focus search | Enter search mode |
| `Esc` | Exit search | Return focus to results |
| `Esc Esc` | Clear search | Clear query and show all |
| `Enter` | Search | Execute search (auto-searches on typing) |
| `↑` / `↓` | History | Navigate search history (if available) |

---

## Settings Screen

| Key | Action | Description |
|-----|--------|-------------|
| `Tab` | Next field | Move to next setting |
| `Shift+Tab` | Previous field | Move to previous setting |
| `Ctrl+S` | Save | Save settings |
| `Esc` | Cancel | Cancel and return |

---

## Debug Console (Advanced)

| Key | Action | Description |
|-----|--------|-------------|
| `:` | Open console | Open debug console (v0.57+) |
| `Esc` | Close console | Close debug console |

**Note:** Debug console is for advanced users and developers.

---

## Vim-Style Navigation Summary

If you're familiar with Vim:

| Vim | Hei-DataHub | Action |
|-----|------------|--------|
| `j` | `j` | Down |
| `k` | `k` | Up |
| `gg` | `g g` | Top |
| `G` | `G` | Bottom |
| `Ctrl+D` | `Ctrl+D` | Page down |
| `Ctrl+U` | `Ctrl+U` | Page up |
| `/` | `/` | Search |
| `Esc` | `Esc` | Exit mode |

---

## Customizing Keybindings (Added in v0.56)

You can remap any shortcut! Edit `~/.config/hei-datahub/config.yaml`:

```yaml
keybindings:
  edit_dataset: "ctrl+e"    # Change from 'e' to Ctrl+E
  search: "ctrl+f"           # Change from '/' to Ctrl+F
  quit: "ctrl+q"             # Change from 'q' to Ctrl+Q
```

👉 [Full customization guide](../how-to/08-customize-keybindings.md)

---

## Action Names for Custom Keybindings

Use these names in your config:

### Global Actions
- `quit` - Exit app
- `help` - Show help
- `search` - Focus search
- `settings` - Open settings
- `refresh` - Refresh data
- `pull_updates` - Pull Git updates

### Home Screen Actions
- `add_dataset` - Add new dataset
- `open_dataset` - Open selected dataset
- `vim_down` - Move down (j)
- `vim_up` - Move up (k)
- `vim_top` - Jump to top (gg)
- `vim_bottom` - Jump to bottom (G)
- `page_down` - Scroll down
- `page_up` - Scroll up

### Details Screen Actions
- `edit_dataset` - Enter edit mode
- `publish_dataset` - Create PR
- `copy_source` - Copy URL
- `open_url` - Open in browser
- `back` - Return to home

### Edit Screen Actions
- `save` - Save changes
- `cancel` - Cancel editing
- `undo` - Undo
- `redo` - Redo
- `next_field` - Next field (Tab)
- `prev_field` - Previous field (Shift+Tab)

---

## Quick Reference Card

**Print this section for easy reference!**

```
╔══════════════════════════════════════════════════════╗
║           HEI-DATAHUB QUICK REFERENCE                ║
╠══════════════════════════════════════════════════════╣
║ GLOBAL                                               ║
║   ?          Help          q        Quit             ║
║   /          Search        s        Settings         ║
║   r          Refresh       u        Pull updates     ║
║                                                      ║
║ NAVIGATION (Home)                                    ║
║   j/↓        Down          k/↑      Up               ║
║   gg         Top           G        Bottom           ║
║   Enter      Open          a        Add dataset      ║
║                                                      ║
║ DETAILS                                              ║
║   e          Edit          p        Publish PR       ║
║   c          Copy URL      o        Open URL         ║
║   Esc        Back                                    ║
║                                                      ║
║ EDITING (v0.57+)                                     ║
║   Ctrl+S     Save          Esc      Cancel           ║
║   Ctrl+Z     Undo          Ctrl+Shift+Z  Redo        ║
║   Tab        Next field    Shift+Tab     Prev field  ║
╚══════════════════════════════════════════════════════╝
```

---

## Tips

### ✅ Mode Indicator
Watch the mode indicator at top-right:
- **"Mode: Normal"** - Shortcuts active
- **"Mode: Insert"** - Typing in a field

### ✅ Context-Aware Help
Press `?` on any screen to see shortcuts for that screen.

### ✅ Terminal Compatibility
Some terminals intercept certain key combinations:
- `Ctrl+S` might trigger XOFF (freeze terminal)
  - Fix: Run `stty -ixon` or remap the key
- `Ctrl+C` might be reserved for system interrupt
  - Workaround: Use `q` to quit

### ✅ Accessibility
All actions are keyboard-only (no mouse required).

---

## Related

- [How to customize keybindings](../how-to/08-customize-keybindings.md)
- [Navigation guide](../getting-started/02-navigation.md)
- [UI guide](10-ui.md)
- [FAQ](../help/90-faq.md)
