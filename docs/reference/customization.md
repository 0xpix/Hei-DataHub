# Customization Guide

Hei-DataHub can be extensively customized through the user configuration file at `~/.config/hei-datahub/config.yaml`.

## Configuration File Location

Your configuration is stored at:
- **Linux/macOS**: `~/.config/hei-datahub/config.yaml`
- **Windows**: `%APPDATA%\hei-datahub\config.yaml`

## Configuration Version

The current configuration version is **2**. If you have an older config file (version 1), it will be automatically migrated when you start the application.

---

## Customizing the Logo

### Using the Default Logo

By default, Hei-DataHub displays a packaged ASCII logo. No configuration needed.

### Using a Custom Logo

To use your own ASCII art logo:

1. Create a text file with your ASCII art (e.g., `~/my-logo.txt`)
2. Update your config file:

```yaml
ui:
  logo:
    path: "~/my-logo.txt"  # Path to your custom logo
    align: center          # left | center | right
    color: cyan            # Color name (cyan, green, yellow, etc.)
    padding_top: 0         # Lines of padding above logo
    padding_bottom: 1      # Lines of padding below logo
```

### Logo Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path` | string | `null` | Path to custom logo file (null = use default) |
| `align` | string | `center` | Text alignment: `left`, `center`, or `right` |
| `color` | string | `cyan` | Color for the logo (see Colors section) |
| `padding_top` | int | `0` | Number of blank lines above logo |
| `padding_bottom` | int | `1` | Number of blank lines below logo |

### Available Colors

You can use any of these color names for your logo:
- `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- `bright_black`, `bright_red`, `bright_green`, `bright_yellow`, `bright_blue`, `bright_magenta`, `bright_cyan`, `bright_white`
- Or any color in `#RRGGBB` hex format

---

## Customizing Keybindings

Keybindings are fully configurable. Each action can have multiple keys assigned.

### Default Keybindings

```yaml
keybindings:
  add_dataset: ["a"]
  settings: ["s"]
  open_details: ["o", "enter"]
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
```

### Customizing Keys

To change keybindings, edit the `keybindings` section in your config:

```yaml
keybindings:
  add_dataset: ["a", "n"]      # Add dataset with 'a' or 'n'
  open_details: ["enter"]      # Only Enter opens details
  quit: ["q", "ctrl+c"]        # Quit with 'q' or Ctrl+C
```

### Special Key Notation

- Regular keys: `"a"`, `"j"`, `"1"`, `"space"`, `"enter"`, `"escape"`
- Arrow keys: `"up"`, `"down"`, `"left"`, `"right"`
- Modifiers: `"ctrl+s"`, `"shift+tab"`, `"alt+f"`
- Function keys: `"f1"`, `"f2"`, etc.

### Applying Keybinding Changes

After editing your config file:
1. Save the file
2. In the app, press `s` to open Settings
3. Click "Reload Keybindings" or restart the app

---

## Customizing Styles (TCSS)

You can override or extend the default styles by creating custom TCSS (Textual CSS) files.

### Adding Custom Stylesheets

1. Create a TCSS file (e.g., `~/.config/hei-datahub/my-styles.tcss`)
2. Add it to your config:

```yaml
theme:
  name: gruvbox
  stylesheets:
    - "~/.config/hei-datahub/my-styles.tcss"
    - "~/.config/hei-datahub/dark-mode-tweaks.tcss"
```

### Example Custom TCSS

```tcss
/* Custom styles - ~/.config/hei-datahub/my-styles.tcss */

/* Make the banner background darker */
#banner {
    background: #1a1a1a;
    padding: 2 0;
}

/* Change search input colors */
#search-input {
    background: #2d2d2d;
    border: solid #4a9eff;
}

/* Customize filter badges */
.filter-badge {
    background: #ff6b6b;
    color: #ffffff;
    padding: 1 2;
    border-radius: 2;
}
```

### TCSS Resources

- Textual CSS uses a subset of CSS
- Available properties: `background`, `color`, `padding`, `margin`, `border`, `width`, `height`, `align`, etc.
- Spacing units: integer values (e.g., `padding: 1 2` = 1 row, 2 columns)
- [Textual CSS Guide](https://textual.textualize.io/guide/CSS/)

---

## Theme Selection

Change the base color theme:

```yaml
theme:
  name: gruvbox  # Change this to any available theme
```

### Available Themes

- `textual-dark` - Default dark theme
- `textual-light` - Light theme
- `gruvbox` - Gruvbox color scheme (default)
- `monokai` - Monokai color scheme
- `nord` - Nord color palette
- `dracula` - Dracula colors
- `catppuccin-mocha` - Catppuccin Mocha
- `catppuccin-latte` - Catppuccin Latte (light)
- `flexoki` - Flexoki theme
- `tokyo-night` - Tokyo Night
- `solarized-light` - Solarized Light

---

## Other Customization Options

### Search Settings

```yaml
search:
  debounce_ms: 150        # Delay before search executes (ms)
  max_results: 50         # Maximum search results to display
  highlight_enabled: true # Enable search term highlighting
```

### Startup Behavior

```yaml
startup:
  check_updates: true     # Check for app updates on startup
  auto_reindex: false     # Automatically reindex datasets on startup
```

### Telemetry

```yaml
telemetry:
  opt_in: false          # Opt into anonymous usage statistics
```

---

## Complete Example Configuration

Here's a fully customized config file:

```yaml
config_version: 2

# Custom UI configuration
ui:
  logo:
    path: "~/.config/hei-datahub/ascii/custom-logo.txt"
    align: center
    color: green
    padding_top: 1
    padding_bottom: 2

# Theme with custom stylesheets
theme:
  name: nord
  stylesheets:
    - "~/.config/hei-datahub/styles/custom.tcss"
  overrides: {}

# Custom keybindings
keybindings:
  add_dataset: ["a", "n", "ctrl+n"]
  settings: ["s", ","]
  open_details: ["enter", "o"]
  pull_updates: ["u", "ctrl+u"]
  refresh_data: ["r", "f5"]
  quit: ["q", "ctrl+c"]
  move_down: ["j", "down"]
  move_up: ["k", "up"]
  jump_top: ["g"]
  jump_bottom: ["G"]
  focus_search: ["/", "ctrl+f"]
  clear_search: ["escape"]
  debug_console: [":"]
  show_help: ["?", "f1"]

# Search configuration
search:
  debounce_ms: 200
  max_results: 100
  highlight_enabled: true

# Startup behavior
startup:
  check_updates: true
  auto_reindex: false

# Telemetry (opt-in only)
telemetry:
  opt_in: false
```

---

## Tips

1. **Backup your config**: Before making major changes, copy your config file
2. **Test incrementally**: Make one change at a time to identify issues
3. **Check logs**: If something doesn't work, check `~/.mini-datahub/logs/datahub.log`
4. **Fallback behavior**: If custom assets fail to load, the app will use built-in defaults
5. **Reload in app**: Most config changes can be reloaded without restarting (use Settings > Reload Keybindings)

---

## Troubleshooting

### Logo not appearing
- Check that the file path is correct and the file exists
- Ensure the file is plain text (UTF-8 encoding)
- Check logs for error messages

### Custom styles not applying
- Verify TCSS syntax (similar to CSS)
- Check file path is correct
- Ensure file has `.tcss` extension
- Look for errors in logs

### Keybindings not working
- Make sure key names are correct (lowercase)
- Use proper modifier syntax: `"ctrl+key"`, not `"Ctrl+Key"`
- Reload keybindings from Settings menu
- Check for conflicting bindings

---

## Getting Help

- Check the [FAQ](../help/90-faq.md)
- Report issues: [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- Examples: See `~/.config/hei-datahub/config.yaml` for inline documentation
