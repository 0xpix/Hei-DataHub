# UI Customization Guide

This guide explains how to customize the Hei-DataHub UI without modifying code.

## Configuration File

All UI customization is controlled through `~/.config/hei-datahub/config.yaml`.

### Config Version 2 Schema

```yaml
config_version: 2

# UI Customization
ui:
  logo:
    path: null  # Custom logo path (null = use default)
    align: center  # left | center | right
    color: cyan  # color name (cyan, green, yellow, red, etc.)
    padding_top: 0
    padding_bottom: 1
  help_file: null  # Optional custom help text file

# Theme Configuration
theme:
  name: gruvbox  # Built-in theme name
  stylesheets: []  # List of custom TCSS file paths
  tokens: null  # Optional design tokens YAML file
  overrides: {}  # Color overrides

# Keybindings
keybindings:
  add_dataset: ["a"]
  settings: ["s"]
  open_details: ["o", "enter"]
  outbox: ["p"]
  pull_updates: ["u"]
  refresh_data: ["r"]
  quit: ["q"]
  move_down: ["j", "down"]
  move_up: ["k", "up"]
  jump_top: ["g"]
  jump_bottom: ["G"]
  focus_search: ["/"]
  clear_search: ["escape"]
  debug_console: [":"]
  show_help: ["?"]

# ... other sections (search, startup, telemetry)
```

## Customizing the Logo

### Using a Custom Logo

1. Create your ASCII art logo in a text file:
   ```
   ~/.config/hei-datahub/ascii/my_logo.txt
   ```

2. Update your config:
   ```yaml
   ui:
     logo:
       path: "~/.config/hei-datahub/ascii/my_logo.txt"
       align: center
       color: green
       padding_top: 1
       padding_bottom: 2
   ```

3. Restart the app

### Logo Options

- **path**: Path to your logo file (use `~` for home directory)
- **align**: `left`, `center`, or `right`
- **color**: Any Textual color name (`cyan`, `green`, `yellow`, `red`, `blue`, `magenta`, `white`, etc.)
- **padding_top**: Empty lines above logo
- **padding_bottom**: Empty lines below logo

## Customizing Styles

### Using Custom TCSS Files

1. Create a custom TCSS file:
   ```css
   /* ~/.config/hei-datahub/theme/custom.tcss */

   #banner {
       background: #2d3748;
       border: solid green;
   }

   #results-table {
       border: solid cyan;
   }

   .filter-badge {
       background: #4a5568;
       color: #f7fafc;
       padding: 1 2;
   }
   ```

2. Add to your config:
   ```yaml
   theme:
     name: gruvbox
     stylesheets:
       - "~/.config/hei-datahub/theme/custom.tcss"
   ```

3. Restart the app

### Available Selectors

Common IDs and classes you can style:

- `#banner` - Logo banner at top
- `#update-status` - Update notification bar
- `#mode-indicator` - Shows Insert/Normal mode
- `#search-input` - Search input box
- `#results-table` - Main dataset table
- `#filter-badges-container` - Container for search badges
- `.filter-badge` - Individual search term badges
- `.badge-retro-*` - Badge color variants
- `#details-container` - Dataset details view
- `#form-container` - Add/edit forms

### TCSS Tips

- Colors: Use hex codes or Textual variables like `$primary`, `$accent`, `$error`
- Spacing: Use integers (e.g., `padding: 1 2` means 1 row, 2 columns)
- Borders: `border: solid <color>` or `border: thick $primary`
- Layout: `layout: horizontal` or `layout: vertical`
- Sizing: `width: 50%`, `height: 10`, `height: 1fr`

## Customizing Keybindings

### Remapping Keys

Edit the `keybindings` section in your config:

```yaml
keybindings:
  # Use Vim-style navigation
  move_down: ["j", "down", "ctrl+n"]
  move_up: ["k", "up", "ctrl+p"]

  # Add multiple keys for the same action
  quit: ["q", "ctrl+q", "ctrl+c"]

  # Use special key combinations
  add_dataset: ["a", "ctrl+shift+n"]
  settings: ["s", "ctrl+comma"]
```

### Available Actions

**Home Screen:**
- `add_dataset` - Open add dataset form
- `settings` - Open settings
- `open_details` - View dataset details
- `outbox` - View failed PR outbox
- `pull_updates` - Pull catalog updates
- `refresh_data` - Refresh dataset list
- `quit` - Quit app
- `move_down` / `move_up` - Navigate table
- `jump_top` / `jump_bottom` - Jump to start/end
- `focus_search` - Focus search input
- `clear_search` - Clear search/exit insert mode
- `debug_console` - Open debug console
- `show_help` - Show help overlay

**Details Screen:**
- `back` - Return to home
- `copy_source` - Copy source URL
- `open_url` - Open source in browser
- `enter_edit_mode` - Edit metadata
- `publish_pr` - Create/update PR

**Add/Edit Forms:**
- `submit` - Save changes
- `cancel` - Cancel without saving
- `next_field` / `prev_field` - Navigate fields
- `scroll_down` / `scroll_up` - Scroll form
- `jump_first` / `jump_last` - Jump to first/last field

### Key Syntax

- Single keys: `"a"`, `"q"`, `"/"`, `"escape"`
- Modified keys: `"ctrl+s"`, `"shift+tab"`, `"alt+enter"`
- Multi-character: `"gg"`, `"dd"` (must press in sequence)
- Special: `"enter"`, `"space"`, `"backspace"`, `"tab"`

### Reload Keybindings

After changing keybindings, press `s` → "Reload Keybindings" or restart the app.

## Advanced Customization

### Design Tokens

Create a tokens file to define reusable values:

```yaml
# ~/.config/hei-datahub/theme/tokens.yaml
colors:
  brand_primary: "#7c3aed"
  brand_accent: "#ec4899"
  success: "#10b981"
  warning: "#f59e0b"

spacing:
  unit: 1
  gutter: 2

borders:
  style: "solid"
  color: "$brand_primary"
```

Reference in config:
```yaml
theme:
  tokens: "~/.config/hei-datahub/theme/tokens.yaml"
```

### Multiple Stylesheets

Stack multiple TCSS files for modular customization:

```yaml
theme:
  stylesheets:
    - "~/.config/hei-datahub/theme/colors.tcss"
    - "~/.config/hei-datahub/theme/layout.tcss"
    - "~/.config/hei-datahub/theme/badges.tcss"
```

Files are loaded in order. Later files override earlier ones.

## Troubleshooting

### Logo Not Showing

- Check file path is correct (use absolute path or `~`)
- Verify file exists: `cat ~/.config/hei-datahub/ascii/my_logo.txt`
- Check config syntax with: `mini-datahub show-config`
- Look for errors in logs: `~/.mini-datahub/logs/datahub.log`

### Styles Not Applying

- Validate TCSS syntax (no invalid units like `0.5fr` in padding)
- Check file path is correct
- Restart app after changes
- Review logs for CSS parse errors

### Keybindings Not Working

- Check for conflicting keybindings (same key for multiple actions)
- Verify action names are spelled correctly
- Press `s` → "Reload Keybindings" in app
- Check logs for binding errors

### Config Migration

If upgrading from v1, your config will auto-migrate to v2 on first run. Original settings are preserved, new sections are added with defaults.

## Examples

### Minimal Dark Theme

```yaml
ui:
  logo:
    color: white
    align: left

theme:
  name: textual-dark
  stylesheets:
    - "~/.config/hei-datahub/theme/dark.tcss"
```

```css
/* dark.tcss */
Screen {
    background: #0a0e27;
}

#banner {
    background: #1a1e37;
    border: solid #4a5568;
}

#results-table {
    background: #1a1e37;
    border: solid #4a5568;
}
```

### Colorful Badge Theme

```yaml
theme:
  name: catppuccin-mocha
  stylesheets:
    - "~/.config/hei-datahub/theme/rainbow-badges.tcss"
```

```css
/* rainbow-badges.tcss */
.badge-retro-teal {
    background: linear-gradient(90deg, #5eead4 0%, #14b8a6 100%);
    color: #0f172a;
}

.badge-retro-coral {
    background: linear-gradient(90deg, #fca5a5 0%, #dc2626 100%);
    color: #ffffff;
}

/* ... more badge styles */
```

### Power User Keybindings

```yaml
keybindings:
  # Multi-key bindings
  add_dataset: ["a", "ctrl+n", "insert"]
  quit: ["q", "ctrl+q", "ctrl+d"]
  # Vim-style
  move_down: ["j", "ctrl+n"]
  move_up: ["k", "ctrl+p"]
  jump_top: ["gg"]
  jump_bottom: ["G"]
  # Quick access
  settings: ["s", "comma"]
  show_help: ["?", "f1"]
```

## Resources

- [Textual CSS Guide](https://textual.textualize.io/guide/CSS/)
- [Textual Styles](https://textual.textualize.io/styles/)
- [ASCII Art Generator](https://patorjk.com/software/taag/)
- [Color Picker](https://htmlcolorcodes.com/)

## Sharing Themes

Share your custom themes in the Hei-DataHub Discussions under "Show and Tell"!

1. Export your config section
2. Share your TCSS files
3. Include screenshots

Happy customizing! 🎨
