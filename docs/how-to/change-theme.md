# How to Change Your Theme

**Requirements:** Hei-DataHub 0.56-beta or later

**Goal:** Customize the app's colors and appearance with built-in themes.

**Time:** 2 minutes

---

## Quick Start

### Step 1: Open Config File

```bash
nvim ~/.config/hei-datahub/config.yaml
```

(Or use any text editor: `nano`, `code`, etc.)

---

### Step 2: Set Your Theme

Add or change the `theme:` line:

```yaml
theme: "gruvbox"
```

---

### Step 3: Save and Restart

1. Save the file
2. Restart the app:
   ```bash
   hei-datahub
   ```

Done! 🎨

---

## Available Themes

### 🌰 Gruvbox (Default)
Warm, retro color scheme inspired by the Gruvbox Vim theme.

**Best for:** Developers who love classic terminal aesthetics.

```yaml
theme: "gruvbox"
```

---

### 🌃 Dracula
Dark purple theme with high contrast.

**Best for:** Late-night coding sessions.

```yaml
theme: "dracula"
```

---

### ❄️ Nord
Cool, minimalist Nordic color palette.

**Best for:** Clean, distraction-free work.

```yaml
theme: "nord"
```

---

### 🎨 Monokai
Classic code editor theme with vibrant colors.

**Best for:** Users migrating from Sublime Text or VS Code.

```yaml
theme: "monokai"
```

---

### 🌙 Catppuccin Mocha
Soft, warm dark theme with pastel accents.

**Best for:** Gentle on the eyes during long sessions.

```yaml
theme: "catppuccin-mocha"
```

---

### ☀️ Solarized Dark
Scientific color scheme designed for readability.

**Best for:** Maximum contrast and eye comfort.

```yaml
theme: "solarized-dark"
```

---

### 🌅 Solarized Light
Light variant of the Solarized theme.

**Best for:** Bright environments or daytime use.

```yaml
theme: "solarized-light"
```

---

### 🌲 Forest
Dark green theme with nature-inspired colors.

**Best for:** Calm, focused work environments.

```yaml
theme: "forest"
```

---

### 🌊 Ocean
Cool blue theme reminiscent of deep waters.

**Best for:** Relaxed, low-stress workflows.

```yaml
theme: "ocean"
```

---

### 🔥 Tokyo Night
Dark theme with vibrant neon accents.

**Best for:** Cyberpunk aesthetics lovers.

```yaml
theme: "tokyo-night"
```

---

### 🎯 Material
Google's Material Design color scheme.

**Best for:** Modern, professional look.

```yaml
theme: "material"
```

---

### 💎 Textual Dark (Default Textual Theme)
The original Textual framework theme.

**Best for:** Consistency with other Textual apps.

```yaml
theme: "textual-dark"
```

---

## Complete Theme List

Copy and paste one of these into your config:

```yaml
theme: "gruvbox"
theme: "dracula"
theme: "nord"
theme: "monokai"
theme: "catppuccin-mocha"
theme: "solarized-dark"
theme: "solarized-light"
theme: "forest"
theme: "ocean"
theme: "tokyo-night"
theme: "material"
theme: "textual-dark"
```

---

## Full Config Example

Here's a complete config file with theme settings:

```yaml
# Hei-DataHub Configuration
# ~/.config/hei-datahub/config.yaml

# Choose your theme
theme: "nord"

# Optional: Keybinding customizations
keybindings:
  quit: "ctrl+q"
  help: "f1"

# Optional: GitHub integration
github:
  auto_open_pr: true
```

---

## Tips & Tricks

### ✅ Try Before You Commit
Change themes quickly by editing the config and restarting. Find your favorite!

---

### ✅ Match Your Terminal
Choose a theme that complements your terminal's color scheme.

---

### ✅ Consider Lighting
Use **light themes** (solarized-light) in bright rooms, **dark themes** (nord, dracula) at night.

---

### ✅ Accessibility
If you have color vision deficiency, try **high-contrast themes** like solarized-dark or material.

---

## Troubleshooting

### Theme Doesn't Change

**Problem:** You edited the config but the theme looks the same.

**Solutions:**

1. **Restart the app** – Changes don't apply until restart
2. **Check spelling** – Theme names are case-sensitive and must match exactly
3. **Check YAML syntax** – Incorrect YAML is silently ignored

---

### Theme Looks Weird

**Problem:** Colors are wrong or hard to read.

**Possible causes:**

1. **Terminal doesn't support 256 colors** – Check your terminal settings
2. **Terminal theme conflicts** – Your terminal's own color scheme may override app colors

**Solutions:**

- Use a modern terminal (iTerm2, Windows Terminal, Alacritty, etc.)
- Set terminal to use "default" or "true color" mode
- Try a different theme

---

### How to Reset to Default

Delete the `theme:` line or set it to:

```yaml
theme: "gruvbox"
```

---

## Terminal Compatibility

### ✅ Recommended Terminals

These terminals have excellent theme support:

- **Linux:** Alacritty, Kitty, GNOME Terminal, Konsole
- **macOS:** iTerm2, Alacritty, Kitty
- **Windows:** Windows Terminal, Alacritty

---

### ⚠️ Limited Support

These terminals may have issues:

- **Windows CMD** – Limited color support
- **Older terminal emulators** – May not support 256 colors

---

## Custom Themes (Advanced)

!!! note "Future Feature" - Custom CSS themes are planned for version 0.59-beta. For now, choose from the 12 built-in themes.

If you want to experiment with custom colors today, you can:

1. Fork the repo
2. Edit `src/mini_datahub/ui/theme.py`
3. Add your custom theme definition

(This requires Python knowledge and is not officially supported.)

---

## Examples by Use Case

### For Long Coding Sessions
```yaml
theme: "gruvbox"        # Warm, easy on eyes
# or
theme: "catppuccin-mocha"  # Soft, low contrast
```

---

### For Presentations
```yaml
theme: "material"       # Professional, clear
# or
theme: "monokai"        # Vibrant, eye-catching
```

---

### For Bright Offices
```yaml
theme: "solarized-light"  # High visibility in daylight
```

---

### For Dark Rooms
```yaml
theme: "nord"           # Cool, minimal
# or
theme: "dracula"        # High contrast, dark
```

---

## Next Steps

- **[Customize keybindings](customize-keybindings.md)** to match your workflow
- **[Configure GitHub integration](../12-config.md)** for publishing
- **[See all config options](../12-config.md)** for more customization

---

## Related

- [Configuration reference](../12-config.md)
- [UI guide](../10-ui.md)
- [FAQ](../90-faq.md#themes)
- [Changelog](../99-changelog.md#theme-support)
