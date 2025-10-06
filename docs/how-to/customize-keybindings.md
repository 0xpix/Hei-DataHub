# How to Customize Keybindings

**Goal:** Change keyboard shortcuts to match your preferences.

**Time:** 5-10 minutes
**Version:** 0.56-beta or later

---

## Before You Start

!!! warning "Restart Required"
    Changes to keybindings require **restarting the app**. This will be improved in a future release.

!!! note "What you'll need"
    - Hei-DataHub 0.56-beta or later
    - A text editor (Vim, Nano, VS Code, etc.)
    - Basic YAML knowledge (we'll provide examples)

---

## Step-by-Step

### 1. Find Your Config File

The configuration file is located at:

```
~/.config/hei-datahub/config.yaml
```

**On Linux/macOS:**
```bash
~/.config/hei-datahub/config.yaml
```

**On Windows:**
```
C:\Users\YourName\.config\hei-datahub\config.yaml
```

---

### 2. Open the Config File

If the file doesn't exist, the app will create it with defaults on first run.

**Using Vim:**
```bash
vim ~/.config/hei-datahub/config.yaml
```

**Using VS Code:**
```bash
code ~/.config/hei-datahub/config.yaml
```

**Using Nano:**
```bash
nano ~/.config/hei-datahub/config.yaml
```

---

### 3. Add Keybinding Section

If not already present, add a `keybindings:` section:

```yaml
# Hei-DataHub Configuration

keybindings:
  # Your custom keybindings go here

theme: "gruvbox"
```

---

### 4. Add Your Custom Bindings

**Format:**
```yaml
keybindings:
  action_name: "key"
```

**Example:**
```yaml
keybindings:
  edit_dataset: "ctrl+e"      # Change from 'e' to Ctrl+E
  search: "ctrl+f"             # Change from '/' to Ctrl+F
  quit: "ctrl+q"               # Change from 'q' to Ctrl+Q
```

---

### 5. Save and Restart

1. Save the file (`Ctrl+S` in most editors, `:wq` in Vim)
2. Restart Hei-DataHub:
   ```bash
   hei-datahub
   ```

Your new keybindings are now active! 🎉

---

## Available Actions

Here are common actions you can customize:

### Global Actions (Work Everywhere)

| Action | Default Key | What it does |
|--------|-------------|-------------|
| `quit` | `q` or `Ctrl+C` | Exit app |
| `help` | `?` | Show help overlay |
| `search` | `/` | Focus search box |
| `settings` | `s` | Open settings |
| `refresh` | `r` | Refresh data |
| `pull_updates` | `u` | Pull Git updates |

---

### Home Screen Actions

| Action | Default Key | What it does |
|--------|-------------|-------------|
| `add_dataset` | `a` | Add new dataset |
| `open_dataset` | `Enter` | Open selected dataset |
| `vim_down` | `j` | Move down one row |
| `vim_up` | `k` | Move up one row |
| `vim_top` | `g g` | Jump to top |
| `vim_bottom` | `G` | Jump to bottom |

---

### Details Screen Actions

| Action | Default Key | What it does |
|--------|-------------|-------------|
| `edit_dataset` | `e` | Enter edit mode |
| `publish_dataset` | `p` | Create PR |
| `copy_source` | `c` | Copy source URL |
| `open_url` | `o` | Open URL in browser |
| `back` | `Esc` | Return to home |

---

### Edit Screen Actions

| Action | Default Key | What it does |
|--------|-------------|-------------|
| `save` | `ctrl+s` | Save changes |
| `cancel` | `escape` | Cancel editing |
| `undo` | `ctrl+z` | Undo last change |
| `redo` | `ctrl+shift+z` | Redo change |

---

## Key Syntax

### Single Keys
```yaml
keybindings:
  quit: "q"
  help: "?"
```

---

### Control Key
```yaml
keybindings:
  save: "ctrl+s"
  quit: "ctrl+q"
```

---

### Shift Key
```yaml
keybindings:
  vim_bottom: "shift+g"  # Note: 'G' is already Shift+g
```

---

### Alt/Option Key
```yaml
keybindings:
  custom_action: "alt+x"
```

---

### Function Keys
```yaml
keybindings:
  help: "f1"
  refresh: "f5"
```

---

### Special Keys
```yaml
keybindings:
  back: "escape"
  confirm: "enter"
  delete: "delete"
```

---

### Key Combinations
```yaml
keybindings:
  redo: "ctrl+shift+z"
  custom: "ctrl+alt+d"
```

---

## Examples

### Example 1: Vim-Style Keybindings

Make navigation more Vim-like:

```yaml
keybindings:
  quit: "shift+z shift+z"      # :q → ZZ
  search: "slash"               # Already default
  back: "escape"                # Already default
  vim_down: "j"                 # Already default
  vim_up: "k"                   # Already default
```

---

### Example 2: Emacs-Style Keybindings

Prefer Emacs shortcuts:

```yaml
keybindings:
  search: "ctrl+s"              # Emacs search
  quit: "ctrl+x ctrl+c"         # Emacs quit
  save: "ctrl+x ctrl+s"         # Emacs save
```

---

### Example 3: VS Code-Style Keybindings

Match VS Code shortcuts:

```yaml
keybindings:
  search: "ctrl+f"              # VS Code search
  add_dataset: "ctrl+n"         # New file
  settings: "ctrl+comma"        # Settings
  quit: "ctrl+q"                # Quit
```

---

### Example 4: Custom Function Keys

Use F-keys for quick actions:

```yaml
keybindings:
  help: "f1"
  add_dataset: "f2"
  edit_dataset: "f3"
  publish_dataset: "f4"
  refresh: "f5"
```

---

## Tips & Tricks

### ✅ Start Small
Change one or two keys first, get comfortable, then add more.

---

### ✅ Keep Defaults for Less-Used Actions
You don't need to customize everything. Focus on actions you use often.

---

### ✅ Write Down Your Changes
Keep a note of your custom keybindings until you memorize them.

---

### ✅ Test After Each Change
Restart the app after editing to make sure your new bindings work.

---

## Troubleshooting

### Keybinding Doesn't Work

**Problem:** You changed a keybinding but it doesn't respond.

**Solutions:**
1. **Check spelling:** Action names are case-sensitive
2. **Check syntax:** Use quotes around keys (`"ctrl+s"` not `ctrl+s`)
3. **Restart app:** Changes require a restart
4. **Check logs:** Look for errors in debug mode

---

### Multiple Keys Conflict

**Problem:** Two actions have the same keybinding.

**Current behavior:** Last one in the file wins (but no warning shown).

**Workaround:** Manually check for conflicts until conflict detection is added (planned for 0.57-beta).

---

### App Ignores Config File

**Problem:** Changes don't take effect.

**Solutions:**
1. **Check file location:** Must be `~/.config/hei-datahub/config.yaml`
2. **Check YAML syntax:** Invalid YAML is silently ignored
3. **Validate YAML:** Use an online YAML validator
4. **Check file permissions:** File must be readable

---

### How to Reset to Defaults

**Option 1:** Delete custom bindings from config file

**Option 2:** Delete the entire config file and restart (app recreates defaults)

```bash
rm ~/.config/hei-datahub/config.yaml
hei-datahub
```

---

## Limitations

### No Conflict Detection (Yet)

If you accidentally assign the same key to two actions, the app won't warn you. Conflict detection is planned for version 0.57-beta.

**Workaround:** Keep a checklist of your bindings.

---

### Restart Required

Changes don't take effect until you restart. Hot-reloading is planned for a future release.

---

### Some Keys Can't Be Rebound

System keys (like `Ctrl+C` in some terminals) may not be rebindable.

---

## Full Example Config

Here's a complete config file with custom keybindings:

```yaml
# Hei-DataHub Configuration
# ~/.config/hei-datahub/config.yaml

# Theme (choose from 12 built-in themes)
theme: "gruvbox"

# Custom keybindings
keybindings:
  # Global
  quit: "ctrl+q"
  help: "f1"
  search: "ctrl+f"
  settings: "ctrl+comma"
  refresh: "f5"

  # Home screen
  add_dataset: "ctrl+n"
  open_dataset: "enter"

  # Details screen
  edit_dataset: "f3"
  publish_dataset: "ctrl+p"
  copy_source: "ctrl+c"
  open_url: "ctrl+o"

  # Edit screen
  save: "ctrl+s"
  cancel: "escape"
  undo: "ctrl+z"
  redo: "ctrl+shift+z"

# GitHub integration (optional)
github:
  auto_open_pr: true

# UI preferences
ui:
  enable_critter_parade: false  # Disable animated critters (0.57+)
  reduce_motion: false           # Accessibility setting
```

---

## Next Steps

- **[Change your theme](change-theme.md)** to match your terminal
- **[Configure GitHub integration](../12-config.md#github-settings)** for publishing
- **[See all configuration options](../12-config.md)** for more customization

---

## Related

- [Configuration reference](../12-config.md)
- [Keyboard shortcuts reference](../reference/keybindings.md)
- [Theme customization](change-theme.md)
- [FAQ](../90-faq.md#customization)
