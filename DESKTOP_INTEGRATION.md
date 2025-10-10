# Desktop Integration Implementation

## Overview

This implementation provides automatic desktop integration for Hei-DataHub on Linux systems. All assets are packaged inside the Python wheel and installed on first run with zero configuration.

## Architecture

### Components

1. **Asset Package** (`src/hei_datahub/assets/`)
   - Icons (SVG, PNG, symbolic)
   - Desktop entry template
   - Shipped in wheel, no post-install scripts

2. **Desktop Installer** (`src/hei_datahub/desktop_install.py`)
   - Pure Python module (500+ lines)
   - XDG-compliant paths
   - Atomic writes with version stamping
   - Best-effort cache refresh

3. **CLI Integration** (`src/mini_datahub/cli/main.py`)
   - `hei-datahub desktop install` - Manual installation
   - `hei-datahub desktop uninstall` - Removal
   - Auto-install on first run (silent)

4. **Documentation** (`docs/installation/desktop-integration.md`)
   - User guide
   - Troubleshooting
   - API reference

## Design Decisions

### Why Not Post-Install Scripts?

Modern Python packaging (pip, uv) doesn't support post-install scripts for security reasons. All installation happens at runtime instead.

### Why Idempotent + Versioned?

The auto-install happens on **every** first run, not just once globally. Version stamping ensures:

- Fast path: Skip if already up-to-date (milliseconds)
- Updates: Auto-update when app version changes
- Repairs: Self-heal if files are missing

### Why User Scope Only?

- No sudo/root required
- Works in user-only environments (HPC, shared systems)
- Follows XDG standards
- Safer (can't break system)

### Why Symbolic Icons?

Symbolic icons (monochrome) are GNOME/KDE standard for:

- System tray
- Status indicators
- Notifications

They auto-recolor to match system themes (dark/light).

## File Structure

```
src/hei_datahub/
  assets/
    icons/
      logo-full.svg                   # 42KB - Full-color launcher icon
      logo-full-256.png               # 43KB - PNG fallback for docks
      hei-datahub-symbolic.svg        # 666B - Monochrome tray icon
    desktop/
      hei-datahub.desktop.tmpl        # 270B - Desktop entry template
  desktop_install.py                  # 500+ lines - Installer module
```

## Installation Paths

All files install to `~/.local/share/` (XDG user directories):

```
~/.local/share/
  icons/hicolor/
    scalable/
      apps/hei-datahub.svg           # Launcher icon (vector)
      status/hei-datahub-symbolic.svg # Tray icon (vector)
    256x256/
      apps/hei-datahub.png           # Launcher icon (raster)
  applications/
    hei-datahub.desktop              # Desktop entry
  Hei-DataHub/
    .desktop_assets_version          # Version stamp
```

## API

### Public Functions

```python
from hei_datahub.desktop_install import (
    install_desktop_assets,       # Manual install/update
    ensure_desktop_assets_once,   # First-run auto-install
    uninstall_desktop_assets,     # Removal
    get_desktop_assets_status,    # Status check
    get_install_paths_info,       # Path info
)
```

### Return Values

All functions return dictionaries with:

- `success: bool` - Operation succeeded
- `message: str` - Human-readable message
- `installed_files: list` - Paths of installed files
- `cache_refreshed: bool` - Icon cache refresh status
- Additional metadata (version, errors, etc.)

## Testing

### Manual Testing

```bash
# 1. Install from source
cd /home/pix/Github/Hei-DataHub
uv pip install -e .

# 2. Test status check
python3 -c "from hei_datahub.desktop_install import get_desktop_assets_status; import json; print(json.dumps(get_desktop_assets_status(), indent=2))"

# 3. Test installation
hei-datahub desktop install --force

# 4. Verify files
ls -lh ~/.local/share/icons/hicolor/scalable/apps/hei-datahub.svg
ls -lh ~/.local/share/applications/hei-datahub.desktop

# 5. Test uninstall
hei-datahub desktop uninstall

# 6. Test auto-install
hei-datahub --version  # Should auto-install on first run
```

### Automated Testing

```bash
# Run test suite (if exists)
pytest tests/test_desktop_install.py -v

# Check icon validity
desktop-file-validate ~/.local/share/applications/hei-datahub.desktop
```

## Platform Support

| Platform | Supported | Notes |
|----------|-----------|-------|
| Linux    | ✅ Yes    | Primary target, all features |
| macOS    | ❌ No     | Not applicable (uses .app bundles) |
| Windows  | ❌ No     | Not applicable (uses shortcuts) |

All functions check `sys.platform` and raise `RuntimeError` on non-Linux.

## Icon Design

### Launcher Icon (logo-full.svg)

- **Source**: `assets/svg/dark_logo_circle.svg`
- **Format**: Full-color SVG
- **Size**: 42KB
- **Usage**: App grid, launcher, dock, Alt-Tab

### PNG Fallback (logo-full-256.png)

- **Generated**: From SVG via ImageMagick
- **Format**: 256×256 PNG with transparency
- **Size**: 43KB
- **Usage**: Docks that don't support SVG

### Symbolic Icon (hei-datahub-symbolic.svg)

- **Design**: Custom monochrome "H" with data dots
- **Format**: Simple SVG with `fill="currentColor"`
- **Size**: 666 bytes
- **Usage**: System tray, status bar

The symbolic icon is:

- Simple shapes only
- Single color (recolored by system)
- 16×16 base size
- No gradients or effects

## Troubleshooting

### Icon Cache Issues

Some desktops cache icons aggressively. Solutions:

```bash
# GNOME
killall -HUP gnome-shell

# KDE
rm ~/.cache/icon-cache.kcache
kquitapp5 plasmashell && kstart5 plasmashell

# Manual
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
```

### Desktop Entry Not Appearing

Check:

1. File exists: `ls ~/.local/share/applications/hei-datahub.desktop`
2. Valid syntax: `desktop-file-validate ~/.local/share/applications/hei-datahub.desktop`
3. Update database: `update-desktop-database ~/.local/share/applications`

### Import Errors

If `from hei_datahub.desktop_install import ...` fails:

1. Check package data: `python3 -c "from importlib.resources import files; print(files('hei_datahub'))"`
2. Reinstall: `uv pip install -e . --force-reinstall`
3. Check `pyproject.toml` includes `hei_datahub.assets`

## Future Enhancements

### Possible Additions

1. **macOS support** - Create `.app` bundle (different approach)
2. **Windows support** - Create Start Menu shortcuts
3. **Custom icon themes** - Let users specify icon variants
4. **System tray integration** - Add tray module using symbolic icon
5. **MIME types** - Associate file types with Hei-DataHub
6. **Auto-start** - Add autostart desktop entry

### Not Planned

- System-wide installation (requires root, non-standard)
- Post-install scripts (blocked by pip/uv security)
- Binary packaging (AppImage, Flatpak, Snap) - separate concern

## Maintenance

### Updating Icons

1. Replace files in `src/hei_datahub/assets/icons/`
2. Keep filenames the same
3. Test with `hei-datahub desktop install --force`
4. Bump version in `version.yaml` to trigger updates

### Updating Desktop Entry

1. Edit `src/hei_datahub/assets/desktop/hei-datahub.desktop.tmpl`
2. Validate with `desktop-file-validate`
3. Test installation
4. Bump version to trigger updates

### Version Stamp

The version stamp (`.desktop_assets_version`) contains the app version string:

- Written after successful installation
- Read on startup to check if update needed
- Deleted on uninstall

Format: Plain text, single line, no newline.

Example: `0.58.1-beta`

## Performance

### First Run (No Assets)

- Extract assets: ~5ms
- Write 4 files: ~10ms
- Refresh caches: ~50-100ms
- **Total**: ~115ms

### Subsequent Runs (Assets Present)

- Check version stamp: <1ms
- **Total**: <1ms (fast path)

### Update (Version Changed)

- Same as first run: ~115ms

The auto-install is designed to be imperceptible on subsequent runs.

## Security

### Considerations

- All files written to user scope (no privilege escalation)
- Atomic writes prevent partial states
- Version stamp prevents downgrade attacks
- No network access during installation
- All assets from trusted source (packaged wheel)

### File Permissions

- Icons: 0644 (rw-r--r--)
- Desktop entry: 0644 (rw-r--r--)
- Version stamp: 0644 (rw-r--r--)

Standard user file permissions, readable by all, writable by owner.

## Credits

- Icon design: Based on Hei-DataHub logo
- Symbolic icon: Custom design following GNOME HIG
- Implementation: Follows XDG Base Directory Specification

## References

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html)
- [Icon Theme Specification](https://specifications.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html)
- [Icon Naming Specification](https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html)
