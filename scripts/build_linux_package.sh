#!/usr/bin/env bash
#
# build_linux_package.sh
# Creates a complete Linux installation package for Hei-DataHub v0.60-beta
#
# This script:
#   1. Builds a standalone PyInstaller binary
#   2. Creates a .deb package for Debian/Ubuntu
#   3. Creates a .tar.gz archive for manual installation
#   4. Includes desktop entry, icons, and all assets
#
# Usage:
#   bash scripts/build_linux_package.sh
#
# Requirements:
#   - uv (package manager)
#   - pyinstaller
#   - dpkg-deb (for .deb package creation)
#
# Output:
#   dist/packages/hei-datahub_0.60.0-beta_amd64.deb
#   dist/packages/hei-datahub_0.60.0-beta_linux_amd64.tar.gz

set -e

# Progress bar function
show_progress() {
    local msg="$1"
    echo -n "  $msg... "
}

complete_progress() {
    echo "✅"
}

error_progress() {
    echo "❌"
}

# Spinner for long-running operations
show_spinner() {
    local pid=$1
    local msg="$2"
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    echo -n "  $msg... "

    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %10 ))
        printf "\r  $msg... ${spin:$i:1}"
        sleep 0.1
    done

    wait $pid
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        printf "\r  $msg... ✅\n"
    else
        printf "\r  $msg... ❌\n"
    fi

    return $exit_code
}

echo "🚀 Building Hei-DataHub v0.60-beta Linux Packages"
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Version info
VERSION="0.60.0-beta"
PACKAGE_NAME="hei-datahub"
ARCH="amd64"

# Step 1: Build the binary
echo "📦 Step 1/4: Building standalone binary"

bash scripts/build_desktop_binary.sh > /tmp/build_binary.log 2>&1 &
if ! show_spinner $! "Building binary"; then
    echo ""
    echo "❌ Binary build failed. Output from build log:"
    cat /tmp/build_binary.log
    rm -f /tmp/build_binary.log
    exit 1
fi
rm -f /tmp/build_binary.log

if [ ! -f "dist/linux/hei-datahub" ]; then
    echo "❌ Binary build failed - file not found"
    exit 1
fi
echo ""

# Step 2: Create package directory structure
echo "📁 Step 2/4: Creating package structure"

PACKAGE_DIR="dist/package-build/${PACKAGE_NAME}_${VERSION}_${ARCH}"

show_progress "Setting up directories"
rm -rf "$PACKAGE_DIR" 2>/dev/null
mkdir -p "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/usr/local/bin"
mkdir -p "$PACKAGE_DIR/usr/share/applications"
mkdir -p "$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PACKAGE_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$PACKAGE_DIR/usr/share/${PACKAGE_NAME}"
mkdir -p "$PACKAGE_DIR/DEBIAN"
complete_progress

show_progress "Copying binary"
cp dist/linux/hei-datahub "$PACKAGE_DIR/usr/local/bin/"
chmod +x "$PACKAGE_DIR/usr/local/bin/hei-datahub"
complete_progress

show_progress "Copying icons"
if [ -f "src/hei_datahub/assets/icons/logo-full-256.png" ]; then
    cp src/hei_datahub/assets/icons/logo-full-256.png \
       "$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps/hei-datahub.png"
fi
if [ -f "src/hei_datahub/assets/icons/logo-full.svg" ]; then
    cp src/hei_datahub/assets/icons/logo-full.svg \
       "$PACKAGE_DIR/usr/share/icons/hicolor/scalable/apps/hei-datahub.svg"
fi
complete_progress

show_progress "Copying ASCII art and assets"
if [ -d "src/hei_datahub/ui/assets/ascii" ]; then
    mkdir -p "$PACKAGE_DIR/usr/share/${PACKAGE_NAME}/ascii"
    cp src/hei_datahub/ui/assets/ascii/*.txt \
       "$PACKAGE_DIR/usr/share/${PACKAGE_NAME}/ascii/" 2>/dev/null || true
fi
if [ -d "src/hei_datahub/assets/icons" ]; then
    mkdir -p "$PACKAGE_DIR/usr/share/${PACKAGE_NAME}/icons"
    cp -r src/hei_datahub/assets/icons/* \
       "$PACKAGE_DIR/usr/share/${PACKAGE_NAME}/icons/" 2>/dev/null || true
fi
complete_progress

show_progress "Creating desktop entry"
cat > "$PACKAGE_DIR/usr/share/applications/hei-datahub.desktop" << 'EOF'
[Desktop Entry]
Version=0.6-beta
Type=Application
Name=Hei-DataHub
GenericName=Dataset Catalog Manager
Comment=Local-first dataset catalog with instant search and cloud sync
Exec=/usr/local/bin/hei-datahub
Icon=hei-datahub
Terminal=true
Categories=Development;DataVisualization;Science;
Keywords=data;dataset;catalog;search;webdav;heibox;
StartupNotify=false
EOF
complete_progress

echo ""

# Step 3: Create .deb package
echo "📦 Step 3/4: Creating .deb package"

show_progress "Generating control files"
cat > "$PACKAGE_DIR/DEBIAN/control" << EOF
Package: hei-datahub
Version: ${VERSION}
Section: science
Priority: optional
Architecture: ${ARCH}
Maintainer: Hei-DataHub Team <noreply@github.com>
Homepage: https://github.com/0xpix/Hei-DataHub
Depends: libc6 (>= 2.31)
Description: Local-first dataset catalog with instant search
 Hei-DataHub is a TUI (Text User Interface) application for cataloging
 datasets with YAML metadata, SQLite full-text search, and WebDAV cloud
 synchronization. Features include:
 .
  - <80ms full-text search with SQLite FTS5
  - WebDAV integration with Heibox/Seafile
  - Secure credential storage via Linux keyring
  - Keyboard-driven interface with Vim shortcuts
  - Schema validation with JSON Schema
EOF
complete_progress

show_progress "Creating install/uninstall scripts"
cat > "$PACKAGE_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

echo "✅ Hei-DataHub installed successfully!"
echo "   Run: hei-datahub"
echo "   Help: hei-datahub --help"

exit 0
EOF

chmod +x "$PACKAGE_DIR/DEBIAN/postinst"

# Create postrm script
cat > "$PACKAGE_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

if [ "$1" = "remove" ]; then
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q /usr/share/applications || true
    fi

    # Update icon cache
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
    fi
fi

exit 0
EOF

chmod +x "$PACKAGE_DIR/DEBIAN/postrm"
complete_progress

show_progress "Building .deb package"
mkdir -p dist/packages
DEB_FILE="dist/packages/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

if command -v dpkg-deb >/dev/null 2>&1; then
    if dpkg-deb --build --root-owner-group "$PACKAGE_DIR" "$DEB_FILE" >/dev/null 2>&1; then
        complete_progress
    else
        error_progress
        echo ""
        echo "❌ dpkg-deb failed. Running with output:"
        dpkg-deb --build --root-owner-group "$PACKAGE_DIR" "$DEB_FILE"
        exit 1
    fi
else
    error_progress
    echo ""
    echo "⚠️  dpkg-deb not found, skipping .deb creation"
fi

echo ""

# Step 4: Create .tar.gz archive for manual installation
echo "📦 Step 4/4: Creating .tar.gz archive"

TARBALL="dist/packages/${PACKAGE_NAME}_${VERSION}_linux_${ARCH}.tar.gz"
INSTALL_DIR="${PACKAGE_NAME}-${VERSION}"

show_progress "Preparing tarball structure"
mkdir -p "dist/tarball/$INSTALL_DIR"
cp -r "$PACKAGE_DIR/usr" "dist/tarball/$INSTALL_DIR/"
complete_progress

show_progress "Creating install/uninstall scripts"
cat > "dist/tarball/$INSTALL_DIR/install.sh" << 'EOF'
#!/bin/bash
#
# Hei-DataHub Installation Script
#

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Installing Hei-DataHub..."
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    SUDO=""
    PREFIX=""
    echo "Installing system-wide to /usr/local/"
else
    SUDO="sudo"
    PREFIX="$HOME/.local"
    echo "Installing to user directory: $PREFIX"
fi

echo ""

# Install binary
if [ -z "$PREFIX" ]; then
    $SUDO cp -f usr/local/bin/hei-datahub /usr/local/bin/
    $SUDO chmod +x /usr/local/bin/hei-datahub
    echo "  ✅ Installed binary to /usr/local/bin/hei-datahub"
else
    mkdir -p "$PREFIX/bin"
    cp -f usr/local/bin/hei-datahub "$PREFIX/bin/"
    chmod +x "$PREFIX/bin/hei-datahub"
    echo "  ✅ Installed binary to $PREFIX/bin/hei-datahub"
fi

# Install desktop entry
if [ -z "$PREFIX" ]; then
    $SUDO cp -f usr/share/applications/hei-datahub.desktop /usr/share/applications/
    echo "  ✅ Installed desktop entry"
else
    mkdir -p "$PREFIX/share/applications"
    cp -f usr/share/applications/hei-datahub.desktop "$PREFIX/share/applications/"
    # Update Exec path for user install
    sed -i "s|/usr/local/bin/hei-datahub|$PREFIX/bin/hei-datahub|" \
        "$PREFIX/share/applications/hei-datahub.desktop"
    echo "  ✅ Installed desktop entry"
fi

# Install icons
if [ -z "$PREFIX" ]; then
    $SUDO mkdir -p /usr/share/icons/hicolor/{256x256,scalable}/apps
    $SUDO cp -f usr/share/icons/hicolor/256x256/apps/hei-datahub.png \
        /usr/share/icons/hicolor/256x256/apps/ 2>/dev/null || true
    $SUDO cp -f usr/share/icons/hicolor/scalable/apps/hei-datahub.svg \
        /usr/share/icons/hicolor/scalable/apps/ 2>/dev/null || true
    echo "  ✅ Installed icons"
else
    mkdir -p "$PREFIX/share/icons/hicolor/{256x256,scalable}/apps"
    cp -f usr/share/icons/hicolor/256x256/apps/hei-datahub.png \
        "$PREFIX/share/icons/hicolor/256x256/apps/" 2>/dev/null || true
    cp -f usr/share/icons/hicolor/scalable/apps/hei-datahub.svg \
        "$PREFIX/share/icons/hicolor/scalable/apps/" 2>/dev/null || true
    echo "  ✅ Installed icons"
fi

# Install shared resources
if [ -z "$PREFIX" ]; then
    $SUDO mkdir -p /usr/share/hei-datahub
    $SUDO cp -r usr/share/hei-datahub/* /usr/share/hei-datahub/ 2>/dev/null || true
    echo "  ✅ Installed shared resources"
else
    mkdir -p "$PREFIX/share/hei-datahub"
    cp -r usr/share/hei-datahub/* "$PREFIX/share/hei-datahub/" 2>/dev/null || true
    echo "  ✅ Installed shared resources"
fi

echo ""

# Update caches
if command -v update-desktop-database >/dev/null 2>&1; then
    if [ -z "$PREFIX" ]; then
        $SUDO update-desktop-database -q /usr/share/applications || true
    else
        update-desktop-database -q "$PREFIX/share/applications" || true
    fi
    echo "  ✅ Updated desktop database"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    if [ -z "$PREFIX" ]; then
        $SUDO gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
    else
        gtk-update-icon-cache -q -t -f "$PREFIX/share/icons/hicolor" || true
    fi
    echo "  ✅ Updated icon cache"
fi

echo ""
echo "✅ Hei-DataHub installed successfully!"
if [ -n "$PREFIX" ]; then
    echo "   Make sure $PREFIX/bin is in your PATH"
    echo "   Add to ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"$PREFIX/bin:\$PATH\""
    echo ""
fi
echo "   Run: hei-datahub"
echo "   Help: hei-datahub --help"
EOF

chmod +x "dist/tarball/$INSTALL_DIR/install.sh"

# Create README
cat > "dist/tarball/$INSTALL_DIR/README.md" << 'EOF'
# Hei-DataHub Installation

## Quick Install

### System-wide installation (requires sudo):
```bash
sudo ./install.sh
```

### User installation (no sudo required):
```bash
./install.sh
```
The user installation installs to `~/.local/bin/hei-datahub`

## Manual Installation

1. Copy binary:
   ```bash
   sudo cp usr/local/bin/hei-datahub /usr/local/bin/
   # OR for user install:
   mkdir -p ~/.local/bin
   cp usr/local/bin/hei-datahub ~/.local/bin/
   ```

2. Copy desktop entry:
   ```bash
   sudo cp usr/share/applications/hei-datahub.desktop /usr/share/applications/
   # OR for user install:
   mkdir -p ~/.local/share/applications
   cp usr/share/applications/hei-datahub.desktop ~/.local/share/applications/
   ```

3. Copy icons:
   ```bash
   sudo cp -r usr/share/icons/hicolor/* /usr/share/icons/hicolor/
   # OR for user install:
   mkdir -p ~/.local/share/icons/hicolor
   cp -r usr/share/icons/hicolor/* ~/.local/share/icons/hicolor/
   ```

## Usage

```bash
hei-datahub              # Launch TUI
hei-datahub --version    # Show version
hei-datahub --help       # Show help
hei-datahub auth setup   # Configure WebDAV
```

## Uninstallation

```bash
# User install
./uninstall.sh

# System install
sudo ./uninstall.sh
```

## Documentation

https://0xpix.github.io/Hei-DataHub/
EOF
complete_progress

# Copy uninstall script
if [ -f "scripts/uninstall.sh" ]; then
    cp scripts/uninstall.sh "dist/tarball/$INSTALL_DIR/uninstall.sh"
    chmod +x "dist/tarball/$INSTALL_DIR/uninstall.sh"
fi

show_progress "Creating tarball"
cd dist/tarball
if ! tar czf "../../${TARBALL}" "$INSTALL_DIR" 2>/dev/null; then
    cd ../..
    error_progress
    echo ""
    echo "❌ Failed to create tarball"
    exit 1
fi
cd ../..
complete_progress

show_progress "Cleaning up temporary files"
rm -rf dist/package-build dist/tarball
complete_progress

echo ""

# Final summary
echo "=========================================="
echo "✅ Package build complete!"
echo "=========================================="
echo ""
echo "📦 Packages created:"
echo ""

if [ -f "$DEB_FILE" ]; then
    echo "   🔹 Debian/Ubuntu package:"
    echo "      $DEB_FILE"
    echo "      Size: $(du -h "$DEB_FILE" | cut -f1)"
    echo "      Install: sudo dpkg -i $DEB_FILE"
    echo ""
fi

echo "   🔹 Portable tarball:"
echo "      $TARBALL"
echo "      Size: $(du -h "$TARBALL" | cut -f1)"
echo "      Extract and run: ./install.sh"
echo ""

echo "📋 Package contents:"
echo "   • Binary: /usr/local/bin/hei-datahub"
echo "   • Desktop entry: /usr/share/applications/hei-datahub.desktop"
echo "   • Icons: /usr/share/icons/hicolor/{256x256,scalable}/apps/"
echo "   • ASCII art: /usr/share/hei-datahub/ascii/"
echo "   • Resources: /usr/share/hei-datahub/"
echo ""

if [ -f "$DEB_FILE" ]; then
    echo "🚀 Test .deb: sudo dpkg -i $DEB_FILE"
fi
echo "🚀 Test tarball: tar xzf $TARBALL && cd ${INSTALL_DIR} && sudo ./install.sh"
echo ""
