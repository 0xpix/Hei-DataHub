# Desktop Version Guide

> 🧱 Compatible with Hei-DataHub **v0.58.x-beta**

This guide covers creating desktop launchers and standalone binaries for Hei-DataHub on Linux systems.

---

## 🖥️ Overview

Hei-DataHub offers two desktop integration options:

| Method | Description | Best For |
|--------|-------------|----------|
| **Desktop Launcher** | Creates a menu entry that runs your UV installation | Daily use after UV install |
| **Standalone Binary** | Self-contained executable (no Python required) | Distribution, offline use |

---

## Method 1: Desktop Launcher (Recommended)

After installing Hei-DataHub via UV, create a desktop launcher to access it from your applications menu.

### ✅ Prerequisites

- Hei-DataHub installed via `uv tool install`
- XDG-compliant desktop environment (GNOME, KDE, XFCE, etc.)
- `hei-datahub` command available in PATH

### 📝 Installation Steps

#### 1. Run the Desktop Entry Script

```bash
bash scripts/create_desktop_entry.sh
```

**What it does:**
- Creates `~/.local/share/applications/hei-datahub.desktop`
- Finds your `hei-datahub` executable automatically
- Updates desktop database
- Makes Hei-DataHub appear in your applications menu

#### 2. Verify Installation

Look for **"Hei-DataHub"** in your application launcher:

- **GNOME:** Press `Super` (Windows key), type "Hei-DataHub"
- **KDE:** Open Application Launcher, search "Hei-DataHub"
- **XFCE:** Open Whisker Menu, search "Hei-DataHub"

You should find it under **Development** category.

### 🎨 Customization

The desktop entry is located at:
```
~/.local/share/applications/hei-datahub.desktop
```

Edit it to customize:

```bash
nano ~/.local/share/applications/hei-datahub.desktop
```

**Example customizations:**

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Hei-DataHub
Comment=Lightweight local data hub with TUI
Exec=/home/username/.local/bin/hei-datahub
Icon=hei-datahub  # Point to a custom icon if you have one
Terminal=true
Categories=Development;Utility;Database;
Keywords=data;catalog;tui;metadata;search;
```

### 🖼️ Adding a Custom Icon

If you have a custom icon:

1. Save icon to `~/.local/share/icons/` (e.g., `hei-datahub.png`)
2. Update the desktop entry:
   ```ini
   Icon=/home/username/.local/share/icons/hei-datahub.png
   ```
3. Update desktop database:
   ```bash
   update-desktop-database ~/.local/share/applications
   ```

---

## Method 2: Standalone Binary (PyInstaller)

Build a self-contained executable that doesn't require Python installation.

### ✅ Prerequisites

- Python 3.10+ installed
- Active virtual environment
- Hei-DataHub source code cloned

### 📝 Build Steps

#### 1. Activate Virtual Environment

```bash
cd /path/to/Hei-DataHub
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate
```

#### 2. Run Build Script

```bash
bash scripts/build_desktop_binary.sh
```

**What it does:**
- Installs PyInstaller
- Bundles Hei-DataHub and all dependencies
- Creates standalone executable at `dist/linux/hei-datahub`

**Build time:** ~30-60 seconds

#### 3. Test the Binary

```bash
./dist/linux/hei-datahub --version
```

### 📦 Distribution

The binary is **semi-portable**:
- ✅ Works on similar Linux distributions
- ✅ No Python required on target system
- ⚠️ Requires compatible glibc version
- ⚠️ ~50-100 MB file size

**Share it:**
```bash
# Compress for distribution
tar -czf hei-datahub-linux-x64.tar.gz -C dist/linux hei-datahub

# Or create a deb/rpm package (advanced)
# See: https://fpm.readthedocs.io/
```

### 🖥️ Desktop Entry for Binary

Create a launcher for the binary:

```bash
# Edit the create_desktop_entry.sh script first
# Change Exec= to point to your binary location

# Or create manually:
cat > ~/.local/share/applications/hei-datahub-binary.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Hei-DataHub (Binary)
Comment=Lightweight local data hub (standalone)
Exec=/home/USERNAME/Hei-DataHub/dist/linux/hei-datahub
Icon=hei-datahub
Terminal=true
Categories=Development;Utility;Database;
EOF

# Replace USERNAME with your actual username
# Update desktop database
update-desktop-database ~/.local/share/applications
```

---

## 🔍 Troubleshooting

### Desktop Launcher

**Issue:** "hei-datahub not found in PATH"

**Solution:**
1. Verify installation:
   ```bash
   which hei-datahub
   ```
2. Add to PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
3. Re-run the script:
   ```bash
   bash scripts/create_desktop_entry.sh
   ```

**Issue:** Launcher doesn't appear in menu

**Solution:**
1. Update desktop database manually:
   ```bash
   update-desktop-database ~/.local/share/applications
   ```
2. Restart your desktop environment (logout/login)
3. Check file permissions:
   ```bash
   ls -la ~/.local/share/applications/hei-datahub.desktop
   ```

**Issue:** Terminal closes immediately

**Solution:**
Edit the desktop entry and ensure `Terminal=true` is set.

### Standalone Binary

**Issue:** "cannot execute binary file"

**Solution:**
Make sure it's executable:
```bash
chmod +x dist/linux/hei-datahub
```

**Issue:** "No module named 'mini_datahub'"

**Solution:**
The build didn't include all dependencies. Try:
```bash
pyinstaller --clean --onefile --name hei-datahub \
  --collect-all mini_datahub \
  --collect-all textual \
  src/mini_datahub/cli/main.py
```

**Issue:** "libstdc++.so.6: version GLIBCXX not found"

**Solution:**
The binary was built on a newer system. Options:
1. Build on an older Linux distribution
2. Use Docker to build in a compatible environment
3. Stick with UV installation method

**Issue:** Binary is too large (>100 MB)

**Solution:**
This is normal for PyInstaller binaries. They include:
- Python interpreter
- All dependencies
- Standard library

To reduce size:
- Use `--exclude-module` for unused packages
- Use UPX compression (not always recommended)

---

## 🚀 Advanced: AppImage Creation

For maximum portability, create an AppImage:

### Prerequisites

```bash
# Install AppImageTool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

### Create AppImage Structure

```bash
mkdir -p Hei-DataHub.AppDir/usr/bin
cp dist/linux/hei-datahub Hei-DataHub.AppDir/usr/bin/

# Create AppRun script
cat > Hei-DataHub.AppDir/AppRun <<'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
exec "${HERE}/usr/bin/hei-datahub" "$@"
EOF

chmod +x Hei-DataHub.AppDir/AppRun

# Create .desktop file
cat > Hei-DataHub.AppDir/hei-datahub.desktop <<'EOF'
[Desktop Entry]
Name=Hei-DataHub
Exec=hei-datahub
Icon=hei-datahub
Type=Application
Categories=Development;
EOF

# Build AppImage
./appimagetool-x86_64.AppImage Hei-DataHub.AppDir
```

Now you have `Hei-DataHub-x86_64.AppImage`!

### Run AppImage

```bash
chmod +x Hei-DataHub-x86_64.AppImage
./Hei-DataHub-x86_64.AppImage
```

---

## 📋 Quick Reference

| Task | Command |
|------|---------|
| Create desktop launcher | `bash scripts/create_desktop_entry.sh` |
| Build binary | `bash scripts/build_desktop_binary.sh` |
| Test binary | `./dist/linux/hei-datahub --version` |
| Update database | `update-desktop-database ~/.local/share/applications` |
| Remove launcher | `rm ~/.local/share/applications/hei-datahub.desktop` |

---

## 💡 Best Practices

1. **For Development:** Use UV install + desktop launcher
2. **For Distribution:** Use PyInstaller binary or AppImage
3. **For CI/CD:** Use ephemeral `uvx` runs
4. **For Production:** Use version-pinned UV installs

---

## 📚 Additional Resources

- [XDG Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [AppImage Documentation](https://appimage.org/)

---

**Launch Hei-DataHub with a single click!** 🚀
