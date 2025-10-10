# Desktop Integration

Hei-DataHub automatically installs desktop integration on Linux systems. This gives you:

- **Application launcher** in your app grid/menu
- **Full-color icon** for the launcher
- **Symbolic tray icon** (auto-adapts to dark/light themes)
- **Standard XDG paths** (no root/sudo required)

## Automatic Installation

Desktop integration is installed automatically on **first run** (Linux only).

When you run `hei-datahub` for the first time, it will:

1. ✓ Install icons to `~/.local/share/icons/hicolor/`
2. ✓ Install desktop entry to `~/.local/share/applications/`
3. ✓ Refresh icon caches (if tools available)

The app will then appear in your launcher/app grid.

## Manual Installation

If you need to reinstall or update desktop integration:

```bash
hei-datahub desktop install
```

This will show current status and install/update all assets.

### Options

- `--force` - Force reinstall even if already up-to-date
- `--no-cache-refresh` - Skip refreshing icon caches

## What Gets Installed

All files are installed to **user scope** (`~/.local/share/`) - no sudo required:

### Icons

- `~/.local/share/icons/hicolor/scalable/apps/hei-datahub.svg` - Full-color launcher icon
- `~/.local/share/icons/hicolor/256x256/apps/hei-datahub.png` - PNG fallback
- `~/.local/share/icons/hicolor/scalable/status/hei-datahub-symbolic.svg` - Symbolic tray icon

### Desktop Entry

- `~/.local/share/applications/hei-datahub.desktop` - Application launcher entry

### Metadata

- `~/.local/share/Hei-DataHub/.desktop_assets_version` - Version stamp (for idempotency)

## Icon Themes

### Launcher Icon

The launcher icon (`hei-datahub`) is a **full-color SVG** that appears in:

- Application grid/menu
- Dock/taskbar (when app is running)
- Alt-Tab switcher

### Tray Icon (Symbolic)

If your app has a system tray component, use the **symbolic icon** name:

```python
# Use icon name, not path
tray_icon = "hei-datahub-symbolic"
```

The symbolic icon is **monochrome** and will automatically:

- ✓ Match your system theme
- ✓ Switch between dark/light as you change themes
- ✓ Follow GNOME/KDE design guidelines

## Troubleshooting

### Icon doesn't appear immediately

Try one of these:

1. **Log out and back in** (most reliable)
2. **Restart your desktop environment**:
   ```bash
   # GNOME
   killall -HUP gnome-shell

   # KDE Plasma
   kquitapp5 plasmashell && kstart5 plasmashell

   # XFCE
   xfce4-panel -r
   ```
3. **Manually refresh icon cache**:
   ```bash
   gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
   ```

### Check installation status

```bash
hei-datahub desktop install
```

This will show:

- Whether assets are installed
- Current version vs installed version
- All file paths
- Whether update is needed

### Reinstall from scratch

```bash
hei-datahub desktop install --force
```

This will reinstall all assets even if already up-to-date.

## Uninstallation

To remove desktop integration:

```bash
hei-datahub desktop uninstall
```

This removes:

- Desktop entry file
- All three icon files
- Version stamp file
- Refreshes icon caches

## How It Works

### Packaging

All assets are **shipped inside the Python wheel**:

```
hei_datahub/
  assets/
    icons/
      logo-full.svg              # Full-color launcher icon
      logo-full-256.png          # Raster fallback
      hei-datahub-symbolic.svg   # Monochrome tray icon
    desktop/
      hei-datahub.desktop.tmpl   # Desktop entry template
```

No post-install scripts needed - everything happens at runtime.

### Installation Process

1. **Check version stamp** - Skip if already installed and up-to-date
2. **Extract assets** - From installed package using `importlib.resources`
3. **Atomic write** - Write to `.tmp` files, then `os.replace()` for atomicity
4. **Refresh caches** - Best-effort icon cache refresh
5. **Write stamp** - Record installed version

The entire process is:

- ✓ **Idempotent** - Safe to run multiple times
- ✓ **Atomic** - No partial states
- ✓ **Fast** - Milliseconds if already installed
- ✓ **Safe** - No root/sudo, user scope only

### Desktop Entry

The `.desktop` file references icons by **name only** (no paths):

```ini
[Desktop Entry]
Icon=hei-datahub
```

This lets the desktop environment find the icon automatically using XDG standards.

## Platform Support

| Platform | Desktop Integration | Notes |
|----------|-------------------|-------|
| **Linux** | ✅ Automatic | Installed on first run |
| **macOS** | ❌ Not supported | macOS uses `.app` bundles |
| **Windows** | ❌ Not supported | Windows uses shortcuts + registry |

## Best Practices

### Using the Symbolic Icon

If you add a system tray component:

```python
# ✅ Good - use icon name
indicator.set_icon("hei-datahub-symbolic")

# ❌ Bad - hardcoded path
indicator.set_icon("/path/to/icon.svg")
```

The icon name lets the system:

- Find the icon via XDG search paths
- Automatically recolor for themes
- Update when themes change

### Checking Platform

Before calling desktop integration functions:

```python
import sys

if sys.platform.startswith("linux"):
    from hei_datahub.desktop_install import install_desktop_assets
    install_desktop_assets()
```

All functions check platform and raise `RuntimeError` on non-Linux.

## Development

### Testing

```bash
# Install in dev mode
uv pip install -e .

# Test desktop integration
hei-datahub desktop install --force

# Verify files
ls -lh ~/.local/share/icons/hicolor/scalable/apps/hei-datahub*
ls -lh ~/.local/share/applications/hei-datahub.desktop

# Test uninstall
hei-datahub desktop uninstall
```

### Creating Custom Icons

If you want to customize icons:

1. Replace files in `src/hei_datahub/assets/icons/`
2. Keep filenames:
   - `logo-full.svg` - Main launcher icon
   - `logo-full-256.png` - PNG fallback
   - `hei-datahub-symbolic.svg` - Tray icon
3. Symbolic icon should be:
   - Single color (`fill="currentColor"`)
   - Simple shapes (16×16 canvas)
   - No gradients or complex effects

## API Reference

See [`hei_datahub.desktop_install`](../src/hei_datahub/desktop_install.py) for the full Python API.

### Key Functions

- `install_desktop_assets()` - Install/update desktop integration
- `ensure_desktop_assets_once()` - Idempotent first-run installer
- `uninstall_desktop_assets()` - Remove all assets
- `get_desktop_assets_status()` - Check installation status
- `get_install_paths_info()` - Get paths as formatted string

### Example Usage

```python
from hei_datahub.desktop_install import (
    install_desktop_assets,
    get_desktop_assets_status,
)

# Check status
status = get_desktop_assets_status()
print(f"Installed: {status['installed']}")
print(f"Version: {status['version']}")
print(f"Needs update: {status['needs_update']}")

# Install/update
result = install_desktop_assets(force=True, verbose=True)
if result['success']:
    print(f"Installed {len(result['installed_files'])} files")
```

## FAQs

**Q: Do I need root/sudo?**

A: No! Everything installs to `~/.local/share/` (user scope).

**Q: Will this work on Wayland?**

A: Yes! XDG desktop standards work on both X11 and Wayland.

**Q: What if I use a custom icon theme?**

A: Icons are installed to the fallback theme (`hicolor`), which all themes inherit from.

**Q: Can I change the icon?**

A: Yes! Replace files in `src/hei_datahub/assets/icons/` and reinstall.

**Q: Does this affect portable installations?**

A: No - desktop integration is optional. The app works fine without it.

**Q: What if installation fails?**

A: The app will still work. Desktop integration is non-critical. Check permissions on `~/.local/share/`.
