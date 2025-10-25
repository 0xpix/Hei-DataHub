# Customize Keybindings

**Requirements:** Hei-DataHub 0.56-beta or later

**Goal:** Personalize keyboard shortcuts to match your workflow and preferences.

**Time:** 5-10 minutes

---

## Why Customize Keybindings?

- ⌨️ **Match your muscle memory** - Use shortcuts from Vim, Emacs, VS Code, etc.
- 🚀 **Boost productivity** - Optimize for actions you use most
- ♿ **Accessibility** - Remap keys to avoid difficult combinations
- 🎯 **Reduce conflicts** - Avoid clashes with terminal or tmux shortcuts

---

## Quick Start

### TL;DR

1. Edit config file: `~/.config/hei-datahub/config.yaml`
2. Add keybindings section with your custom shortcuts
3. Save and restart Hei-DataHub
4. Enjoy your personalized workflow!

---

## Step-by-Step Guide

### 1. Locate Your Config File

The configuration file is located at:

**Linux/macOS:**
```bash
~/.config/hei-datahub/config.yaml
```

**Windows:**
```
C:\Users\YourName\.config\hei-datahub\config.yaml
```

**Quick check if file exists:**
```bash
# Linux/macOS
ls -l ~/.config/hei-datahub/config.yaml

# Windows PowerShell
Test-Path "$env:USERPROFILE\.config\hei-datahub\config.yaml"
```

**Note:** If the file doesn't exist, Hei-DataHub creates it with defaults on first run.

---

### 2. Open the Config File

Choose your preferred editor:

**NeoVim/Vim:**
```bash
nvim ~/.config/hei-datahub/config.yaml
# or
vim ~/.config/hei-datahub/config.yaml
```

**VS Code:**
```bash
code ~/.config/hei-datahub/config.yaml
```

**Nano (beginner-friendly):**
```bash
nano ~/.config/hei-datahub/config.yaml
```

**Any text editor:**
```bash
# Linux
xdg-open ~/.config/hei-datahub/config.yaml

# macOS
open ~/.config/hei-datahub/config.yaml
```

---

### 3. Add or Modify Keybindings Section

If not already present, add a `keybindings:` section to your config:

```yaml
# Hei-DataHub Configuration

keybindings:
  # Your custom keybindings go here
  # Format: action_name: "key_combination"

theme: "gruvbox"
```

**Important:**
- Indentation matters in YAML (use 2 spaces)
- Always use quotes around key values: `"ctrl+s"` not `ctrl+s`
- Action names are case-sensitive: `add_dataset` not `Add_Dataset`

---

### 4. Define Your Custom Bindings

**Basic format:**
```yaml
keybindings:
  action_name: "key"
```

**Common examples:**
```yaml
keybindings:
  # Change edit from 'e' to Ctrl+E
  edit_dataset: "ctrl+e"

  # Change search from '/' to Ctrl+F (like VS Code)
  search: "ctrl+f"

  # Change quit from 'q' to Ctrl+Q
  quit: "ctrl+q"

  # Use function keys
  help: "f1"
  refresh: "f5"

  # Add dataset with Ctrl+N (like "new file")
  add_dataset: "ctrl+n"
```

**Pro tip:** Comment out the default first, then add your custom binding:
```yaml
keybindings:
  # edit_dataset: "e"        # Default (commented)
  edit_dataset: "ctrl+e"     # My custom binding
```

---

### 5. Save and Test

1. **Save the file:**
   - Vim/NeoVim: `:wq` or `:w` then `:q`
   - Nano: `Ctrl+O` (save), `Ctrl+X` (exit)
   - VS Code: `Ctrl+S`

2. **Restart Hei-DataHub:**
   ```bash
   hei-datahub
   ```

3. **Test your new keybindings:**
   - Try each custom shortcut
   - If something doesn't work, check for typos in the config
   - Press `?` to see current keybindings help

4. **Verify changes took effect:**
   - The help screen (`?`) should show your custom bindings
   - Test the actual shortcuts to confirm they work

Your personalized keybindings are now active! 🎉

---

## Available Actions Reference



### Home Screen Actions

Dataset catalog navigation and management:

| Action | Default Key | Description | When to use |
|--------|-------------|-------------|-------------|
| `add_dataset` | `a` | Add new dataset | Create dataset entry |
| `open_dataset` | `Enter` | Open selected dataset | View full details |
| `delete_dataset` | `d` | Delete dataset | Remove from catalog |
| `vim_down` | `j` | Move down one row | Navigate list (Vim-style) |
| `vim_up` | `k` | Move up one row | Navigate list (Vim-style) |
| `vim_top` | `g g` | Jump to top | Go to first dataset |
| `vim_bottom` | `G` | Jump to bottom | Go to last dataset |
| `page_down` | `Ctrl+d` | Scroll down half page | Fast navigation |
| `page_up` | `Ctrl+u` | Scroll up half page | Fast navigation |

**Popular customizations:**
- Change `add_dataset` to `Ctrl+N` (like "new file" in editors)
- Use arrow keys instead of `j/k` (already works by default)

---

### Details Screen Actions

When viewing a dataset's full information:

| Action | Default Key | Description | Use case |
|--------|-------------|-------------|----------|
| `edit_dataset` | `e` | Enter edit mode | Modify metadata |
| `copy_source` | `c` | Copy source URL | Quick copy to clipboard |
| `open_url` | `o` | Open URL in browser | View external source |
| `back` | `Esc` or `b` | Return to home screen | Exit details view |
| `delete_dataset` | `d` | Delete this dataset | Remove from catalog |

**Workflow tip:** Common pattern is `e` (edit) → make changes → `Ctrl+S` (save) → `Esc` (back)

---

### Edit Screen Actions

When modifying dataset metadata:

| Action | Default Key | Description | Notes |
|--------|-------------|-------------|-------|
| `save` | `Ctrl+s` | Save changes | Syncs to Heibox if connected |
| `cancel` | `Esc` | Cancel editing | Confirms if unsaved changes |
| `undo` | `Ctrl+z` | Undo last change | Works within edit session |
| `redo` | `Ctrl+Shift+z` | Redo change | Restore undone change |
| `next_field` | `Tab` | Move to next field | Navigate form |
| `prev_field` | `Shift+Tab` | Move to previous field | Navigate backwards |

**Customization idea:** Some users prefer `Ctrl+Y` for redo (Windows-style):
```yaml
keybindings:
  redo: "ctrl+y"
```

---

## Key Syntax Reference

### Single Character Keys

Simple letter or symbol keys:

```yaml
keybindings:
  quit: "q"
  help: "?"
  add_dataset: "a"
  search: "/"
```

**Tip:** Use lowercase for letters. Uppercase requires shift (see below).

---

### Modifier Keys

Combine modifiers with keys using `ctrl+`, `shift+`, `alt+`:

```yaml
keybindings:
  save: "ctrl+s"
  delete: "ctrl+d"
  copy: "ctrl+c"
  uppercase_letter: "shift+a"  # Capital A
  alternate: "alt+f"
```

**Available Modifiers:**

- `ctrl+` - Control key (most common)
- `shift+` - Shift key (use for uppercase or shifted symbols)
- `alt+` - Alt/Option key (less common in terminals)

**Common Patterns:**

- `ctrl+<letter>` - Primary shortcuts (save, quit, delete)
- `shift+<letter>` - Uppercase letters or shifted symbols
- `ctrl+shift+<letter>` - Advanced operations
- `alt+<letter>` - Alternative actions

**Note:** Not all terminal emulators support `alt+` combinations reliably. Test in your terminal first.

---

### Function Keys

Use F1-F12 for quick actions:

```yaml
keybindings:
  help: "f1"        # Common convention for help
  refresh: "f5"     # Like browser refresh
  settings: "f9"
  custom: "f12"
```

**Tip:** Function keys are ideal for frequently-used actions since they don't conflict with text editing shortcuts.

---

### Special Keys

Named keys for common special characters:

```yaml
keybindings:
  back: "escape"
  confirm: "enter"
  delete: "delete"
  tab_next: "tab"
  tab_prev: "shift+tab"
```

**Available special keys:** `escape`, `enter`, `delete`, `backspace`, `tab`, `space`

---

### Multi-Key Combinations

Combine multiple modifiers:

```yaml
keybindings:
  redo: "ctrl+shift+z"          # Standard redo shortcut
  advanced_search: "ctrl+alt+f"
  vim_quit: "shift+z shift+z"   # Vim-style ZZ
```

**Tip:** Keep combinations to 2 modifiers max for usability. `ctrl+alt+shift+x` is hard to remember!

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

## Real-World Examples

### Example 1: Vim Purist Setup

For Vim users who want maximum consistency:

```yaml
keybindings:
  # Navigation (already default, shown for reference)
  vim_down: "j"                 # Move down
  vim_up: "k"                   # Move up
  vim_top: "g g"                # Jump to top
  vim_bottom: "shift+g"         # Jump to bottom

  # Actions with Vim-style keys
  quit: "shift+z shift+z"       # ZZ to quit (Vim style)
  search: "/"                   # Already default
  back: "escape"                # Already default
  edit_dataset: "i"             # i for "insert mode" (edit)
  delete_dataset: "d d"         # dd for delete (Vim style)
```

**Why this works:** Muscle memory from Vim transfers directly to Hei-DataHub.

---

### Example 2: VS Code Migration

Match your editor shortcuts for seamless workflow:

```yaml
keybindings:
  # File operations
  add_dataset: "ctrl+n"         # New file
  save: "ctrl+s"                # Save (already default)
  quit: "ctrl+q"                # Quit app

  # Navigation & search
  search: "ctrl+f"              # Find in file
  open_dataset: "ctrl+o"        # Open file
  back: "escape"                # Close panel

  # Advanced
  settings: "ctrl+comma"        # Open settings
  help: "ctrl+shift+p"          # Command palette style
```

**Tip:** Add comments in your config to remember why you chose each binding.

---

### Example 3: Productivity Power User

Optimize for speed with function keys:

```yaml
keybindings:
  # Quick access via F-keys
  help: "f1"                    # Standard help key
  add_dataset: "f2"             # Quick create
  edit_dataset: "f3"            # Quick edit
  publish_dataset: "f4"         # Quick publish
  refresh: "f5"                 # Refresh (like browsers)
  search: "f6"                  # Quick search
  settings: "f9"                # Settings

  # Keep common shortcuts
  save: "ctrl+s"
  quit: "ctrl+q"
  copy_source: "ctrl+c"
```

**Why function keys?** One-handed access, no conflicts with text editing, easy to remember numbers.

---

### Example 4: Accessibility-Focused

Reduce hand strain with comfortable key placements:

```yaml
keybindings:
  # Avoid pinky stretches
  save: "ctrl+s"                # Already comfortable
  quit: "ctrl+w"                # Close window (easier than ctrl+q)

  # Use right-hand side for common actions
  edit_dataset: "l"             # Right hand (instead of e)
  help: "semicolon"             # Right hand

  # Function keys for one-hand use
  add_dataset: "f2"
  search: "f3"
  refresh: "f5"
```

**Principle:** Minimize hand movement and awkward key combinations.

---

## Pro Tips & Best Practices

### 💡 Start Small, Iterate Often

**Don't rebind everything at once!** Change 1-2 shortcuts, use them for a day, then add more.

**Why:** Your muscle memory needs time to adapt. Too many changes at once leads to confusion.

**Recommended progression:**
1. Week 1: Change your most-used action (e.g., `add_dataset`)
2. Week 2: Add 2-3 navigation shortcuts
3. Week 3: Customize advanced features

---

### 💡 Mirror Your Primary Editor

**Match the shortcuts from your main code editor** (VS Code, Vim, Emacs, etc.)

**Why:** Context switching is smoother when shortcuts are consistent across tools.

**Example:** If you use VS Code, set `search: "ctrl+f"` and `add_dataset: "ctrl+n"` to match "Find" and "New File".

---

### 💡 Use Mnemonic Keys

**Choose keys that remind you of the action:**

- `e` for **E**dit
- `d` for **D**elete
- `p` for **P**ublish
- `s` for **S**earch
- `a` for **A**dd

**Why:** Easier to remember than arbitrary assignments.

---

### 💡 Reserve Ctrl for Important Actions

**Use `ctrl+<key>` combinations for critical, frequent operations:**

```yaml
keybindings:
  save: "ctrl+s"          # Critical: saving work
  quit: "ctrl+q"          # Important: exiting
  search: "ctrl+f"        # Frequent: finding datasets
```

**Keep single-letter keys for less destructive actions:**
```yaml
keybindings:
  help: "?"               # Safe: just viewing help
  edit_dataset: "e"       # Reversible: can cancel edits
```

**Why:** Harder to accidentally trigger `ctrl+` combinations.

---

### 💡 Document Your Custom Setup

**Keep a cheat sheet until you memorize your bindings.**

**Quick method:** Add comments in your config file:
```yaml
keybindings:
  # EDITING SHORTCUTS
  edit_dataset: "f3"      # Quick edit (like Excel)
  save: "ctrl+s"          # Save changes

  # NAVIGATION
  search: "ctrl+f"        # Find datasets (like browsers)
  vim_down: "j"           # Down (Vim muscle memory)
```

**Advanced method:** Create a markdown file in `~/.config/hei-datahub/my-shortcuts.md`

---

### 💡 Test in Isolation

**After adding a new binding, test it immediately:**

1. Save config file
2. Restart Hei-DataHub
3. Press `?` to view help (confirms binding registered)
4. Try the actual shortcut in context

**Why:** Catches typos and conflicts early, before you forget what you changed.

---

### 💡 Keep a Backup

**Before major changes, save a copy of your working config:**

```bash
cp ~/.config/hei-datahub/config.yaml ~/.config/hei-datahub/config.yaml.backup
```

**To restore if something breaks:**
```bash
cp ~/.config/hei-datahub/config.yaml.backup ~/.config/hei-datahub/config.yaml
```

---

### 💡 Don't Customize Everything

**You don't need to rebind every action.** Focus on:

✅ **High-frequency actions** you do 20+ times per day
✅ **Awkward defaults** that slow you down
✅ **Conflicts** with your editor or terminal

❌ **Don't change** actions you rarely use
❌ **Don't change** shortcuts that already feel natural

**Pareto principle:** 20% of shortcuts handle 80% of your workflow.

---

## Troubleshooting

### ⚠️ Keybinding Doesn't Work

**Symptoms:** You press your custom shortcut but nothing happens.

**Common causes & solutions:**

1. **Typo in action name**
   ```yaml
   # ❌ Wrong (typo)
   edit_datset: "ctrl+e"

   # ✅ Correct
   edit_dataset: "ctrl+e"
   ```
   Action names are case-sensitive and must match exactly.

2. **Missing quotes around key value**
   ```yaml
   # ❌ Wrong (no quotes)
   save: ctrl+s

   # ✅ Correct
   save: "ctrl+s"
   ```

3. **Wrong indentation**
   ```yaml
   # ❌ Wrong (not indented under keybindings)
   keybindings:
   quit: "q"

   # ✅ Correct (2 spaces indent)
   keybindings:
     quit: "q"
   ```

4. **Forgot to restart Hei-DataHub**
   - Changes only apply after restart
   - Exit and relaunch the app

5. **Key combination not supported by your terminal**
   - Some terminals don't support all key combos (especially `alt+`)
   - Test the key in the terminal first
   - Try a different key combination

**Debugging steps:**
```bash
# 1. Validate YAML syntax
yamllint ~/.config/hei-datahub/config.yaml

# 2. Check config file exists and is readable
cat ~/.config/hei-datahub/config.yaml

# 3. Launch with debug output
hei-datahub --debug
```

---

### ⚠️ Multiple Actions Have Same Key (Conflict)

**Problem:** You accidentally assigned the same key to two different actions.

**Current behavior:** The last binding in the file wins, with no warning shown.

**Example of conflict:**
```yaml
keybindings:
  edit_dataset: "e"
  export_data: "e"      # ❌ Conflict! Only this one will work
```

**Solutions:**

1. **Manual audit:** Search your config file for duplicate key values
2. **Use unique keys:** Assign different keys to each action
3. **Wait for conflict detection:** Planned for v0.57-beta

**Temporary workaround script:**
```bash
# Find duplicate keybindings
grep -A 100 "keybindings:" ~/.config/hei-datahub/config.yaml | \
  grep -E '^\s+\w+:' | \
  awk -F': ' '{print $2}' | \
  sort | \
  uniq -d
```

---

### ⚠️ Config File Changes Ignored

**Symptoms:** You edit the config but changes don't take effect.

**Common causes:**

1. **Wrong file location**
   ```bash
   # Must be exactly this path:
   ~/.config/hei-datahub/config.yaml

   # Verify location:
   ls -la ~/.config/hei-datahub/config.yaml
   ```

2. **Invalid YAML syntax**
   - One syntax error breaks the entire file
   - App silently falls back to defaults

   **Validation:**
   ```bash
   # Install YAML linter
   pip install yamllint

   # Check your config
   yamllint ~/.config/hei-datahub/config.yaml
   ```

3. **File permissions issue**
   ```bash
   # Check if file is readable
   ls -l ~/.config/hei-datahub/config.yaml

   # Fix permissions if needed
   chmod 644 ~/.config/hei-datahub/config.yaml
   ```

4. **Cached settings**
   - Rarely, old settings stick around

   **Clear cache:**
   ```bash
   # Remove cache (safe, will regenerate)
   rm -rf ~/.cache/hei-datahub/
   ```

---

### ⚠️ How to Reset to Defaults

**Option 1: Remove custom keybindings section**

Edit `~/.config/hei-datahub/config.yaml` and delete the `keybindings:` section:
```yaml
# Before
theme: "gruvbox"
keybindings:
  quit: "ctrl+q"
  search: "ctrl+f"

# After (keybindings removed)
theme: "gruvbox"
```

**Option 2: Delete entire config file**

```bash
# Backup first (recommended)
mv ~/.config/hei-datahub/config.yaml ~/.config/hei-datahub/config.yaml.old

# Restart app - it will create fresh default config
hei-datahub
```

**Option 3: Comment out specific bindings**
```yaml
keybindings:
  # quit: "ctrl+q"      # Commented out - reverts to default "q"
  search: "ctrl+f"      # Still active
```

---

### ⚠️ Terminal Intercepts My Keybinding

**Problem:** Your terminal or shell intercepts the keybinding before Hei-DataHub sees it.

**Common conflicts:**

| Key | Often Intercepted By | Solution |
|-----|----------------------|----------|
| `Ctrl+S` | Terminal flow control (XOFF) | Disable with `stty -ixon` |
| `Ctrl+Q` | Terminal flow control (XON) | Disable with `stty -ixon` |
| `Ctrl+C` | Terminal interrupt signal | Use different key |
| `Ctrl+Z` | Suspend process | Use different key or `Ctrl+Shift+Z` |
| `Alt+<key>` | Window manager shortcuts | Check WM config |

**To disable flow control permanently:**
```bash
# Add to ~/.zshrc or ~/.bashrc
stty -ixon
```

**Debugging:** Try the key in a different terminal emulator to isolate the issue.

---

### ⚠️ Special Characters Don't Work

**Problem:** Keys like `[`, `]`, `,` don't register properly.

**Solution:** Some special characters need to be spelled out:

```yaml
keybindings:
  action1: "left_bracket"   # Instead of "["
  action2: "right_bracket"  # Instead of "]"
  action3: "comma"          # Instead of ","
```

**Tip:** Check the Textual framework documentation for special character names.

---

## Limitations & Future Features

### ⏳ No Conflict Detection (Yet)

**Current behavior:** If you assign the same key to two actions, the last one wins. No warning shown.

**Workaround:** Manually audit your config file for duplicate keys.

**Coming in v0.57-beta:** Automatic conflict detection with warnings.

---

### ⏳ Restart Required for Changes

**Current behavior:** Changes to `config.yaml` only apply after restarting Hei-DataHub.

**Workaround:** Quick restart after editing (takes only 300ms with warm cache).

**Future improvement:** Hot-reloading configuration without restart (planned).

---

### ⚠️ Some Keys Can't Be Rebound

**System-level keys** may be intercepted by your terminal or window manager:

- `Ctrl+C` - Terminal interrupt signal
- `Ctrl+Z` - Suspend process
- `Ctrl+S` / `Ctrl+Q` - Flow control (unless disabled)
- `Alt+Tab` - Window switching (OS-level)

**Workaround:** Use alternative key combinations (e.g., `Ctrl+Shift+C` instead of `Ctrl+C`).

---

### 🔍 Limited Multi-Key Sequences

**Current support:** Two-key sequences like `g g` (jump to top) work.

**Not yet supported:** Complex sequences like `d i w` (Vim "delete inner word").

**Workaround:** Use modifier combinations instead (`ctrl+shift+d`).

---

### 📝 No GUI Configuration

**Current method:** Manual YAML editing.

**Coming later:** Interactive keybinding configuration UI within the app.

---

## Complete Example Configuration

Here's a production-ready config file showing best practices:

```yaml
# ~/.config/hei-datahub/config.yaml
# Hei-DataHub Configuration File
# Last updated: 2024

# ============================================================
# THEME
# ============================================================
# Choose from: catppuccin, dracula, gruvbox, monokai, nord,
#              one-dark, rose-pine, solarized, tokyo-night, etc.
theme: "gruvbox"

# ============================================================
# CUSTOM KEYBINDINGS
# ============================================================
keybindings:
  # -------------------- GLOBAL ACTIONS --------------------
  quit: "ctrl+q"              # Quit app (instead of 'q')
  help: "f1"                  # Help screen (function key is standard)
  search: "ctrl+f"            # Search datasets (like browsers/editors)
  settings: "ctrl+comma"      # Open settings (VS Code style)
  refresh: "f5"               # Refresh data (like browser refresh)

  # -------------------- HOME SCREEN --------------------
  add_dataset: "ctrl+n"       # New dataset (like "new file")
  open_dataset: "enter"       # Open selected (already default)
  delete_dataset: "ctrl+d"    # Delete (with confirmation)

  # Vim-style navigation (keep defaults, shown for reference)
  vim_down: "j"               # Move down
  vim_up: "k"                 # Move up
  vim_top: "g g"              # Jump to top
  vim_bottom: "shift+g"       # Jump to bottom

  # Fast scrolling
  page_down: "ctrl+d"         # Half-page down (Vim style)
  page_up: "ctrl+u"           # Half-page up (Vim style)

  # -------------------- DETAILS SCREEN --------------------
  edit_dataset: "f3"          # Quick edit (function key for speed)
  publish_dataset: "ctrl+p"   # Publish to Heibox
  copy_source: "ctrl+c"       # Copy source URL
  open_url: "ctrl+o"          # Open URL in browser
  back: "escape"              # Return to home (already default)

  # -------------------- EDIT SCREEN --------------------
  save: "ctrl+s"              # Save changes (universal convention)
  cancel: "escape"            # Cancel editing (already default)
  undo: "ctrl+z"              # Undo change (standard)
  redo: "ctrl+y"              # Redo (Windows style, easier than ctrl+shift+z)
  next_field: "tab"           # Move to next field (already default)
  prev_field: "shift+tab"     # Move to previous field (already default)

# ============================================================
# HEIBOX INTEGRATION
# ============================================================
heibox:
  server_url: "https://heibox.uni-heidelberg.de"
  library_id: "your-library-uuid-here"
  auto_sync: true             # Sync on save
  sync_interval: 15           # Minutes between background syncs

# ============================================================
# UI PREFERENCES
# ============================================================
ui:
  enable_critter_parade: true     # Animated critters on load
  reduce_motion: false            # Accessibility: disable animations
  startup_message: true           # Show welcome message
  confirm_delete: true            # Confirm before deleting datasets

# ============================================================
# SEARCH SETTINGS
# ============================================================
search:
  fuzzy_matching: true            # Allow typos in search
  auto_complete: true             # Show suggestions as you type
  max_results: 100                # Maximum search results to show
  highlight_matches: true         # Highlight matched terms

# ============================================================
# PERFORMANCE
# ============================================================
performance:
  cache_size_mb: 50               # Search index cache size
  background_indexing: true       # Index while app runs
  preload_datasets: true          # Load dataset list on startup
```

**What makes this a good config?**

✅ **Well-organized:** Sections with clear headers
✅ **Commented:** Explains why each binding was chosen
✅ **Consistent patterns:** All `ctrl+` for important actions
✅ **Muscle memory friendly:** Matches common conventions (VS Code, browsers)
✅ **Backwards compatible:** Doesn't override defaults that work well
✅ **Documented:** Easy to understand and modify later

---

## Next Steps

**Now that you've customized your keybindings:**

- 🎨 **[Customize your theme](09-change-theme.md)** - Match your terminal color scheme with 12+ built-in themes
- 📖 **[View complete settings reference](../reference/12-config.md)** - All configuration options documented

---

## Related Documentation

- **[Settings Guide](04-settings.md)** - Complete configuration walkthrough
- **[Change Theme](09-change-theme.md)** - Visual customization
- **[Advanced Search](07-search-advanced.md)** - Search techniques and shortcuts
- **[Configuration Reference](../reference/12-config.md)** - Full config file specification
- **[FAQ](../help/90-faq.md)** - Common questions and troubleshooting

---

**Questions or issues?** Check the [FAQ](../help/90-faq.md) or open an issue on our repository.
