#!/bin/bash
#
# Hei-DataHub Uninstallation Script
#
# Usage:
#   ./uninstall.sh              # Removes user installation (~/.local/)
#   sudo ./uninstall.sh         # Removes system installation (/usr/local/, /usr/share/)
#

set -e

echo "🗑️  Hei-DataHub Uninstaller"
echo ""

# Detect installation type
if [ "$EUID" -eq 0 ]; then
    echo "Running as root - removing system-wide installation"
    PREFIX=""
    SUDO=""
else
    echo "Running as user - removing user installation"
    PREFIX="$HOME/.local"
    SUDO=""
fi

# Check what's installed
FOUND_SOMETHING=false

# Check binary
if [ -z "$PREFIX" ]; then
    if [ -f "/usr/local/bin/hei-datahub" ]; then
        echo "  Found: /usr/local/bin/hei-datahub"
        FOUND_SOMETHING=true
    fi
else
    if [ -f "$PREFIX/bin/hei-datahub" ]; then
        echo "  Found: $PREFIX/bin/hei-datahub"
        FOUND_SOMETHING=true
    fi
fi

# Check desktop entry
if [ -z "$PREFIX" ]; then
    if [ -f "/usr/share/applications/hei-datahub.desktop" ]; then
        echo "  Found: /usr/share/applications/hei-datahub.desktop"
        FOUND_SOMETHING=true
    fi
else
    if [ -f "$PREFIX/share/applications/hei-datahub.desktop" ]; then
        echo "  Found: $PREFIX/share/applications/hei-datahub.desktop"
        FOUND_SOMETHING=true
    fi
fi

# Check shared resources
if [ -z "$PREFIX" ]; then
    if [ -d "/usr/share/hei-datahub" ]; then
        echo "  Found: /usr/share/hei-datahub/"
        FOUND_SOMETHING=true
    fi
else
    if [ -d "$PREFIX/share/hei-datahub" ]; then
        echo "  Found: $PREFIX/share/hei-datahub/"
        FOUND_SOMETHING=true
    fi
fi

if [ "$FOUND_SOMETHING" = false ]; then
    echo "❌ No installation found"
    echo ""
    if [ "$EUID" -eq 0 ]; then
        echo "💡 Tip: Run without sudo to check for user installation:"
        echo "   ./uninstall.sh"
    else
        echo "💡 Tip: Run with sudo to check for system installation:"
        echo "   sudo ./uninstall.sh"
    fi
    exit 1
fi

echo ""
read -p "Remove these files? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Removing files..."

# Remove binary
if [ -z "$PREFIX" ]; then
    if [ -f "/usr/local/bin/hei-datahub" ]; then
        rm -f /usr/local/bin/hei-datahub
        echo "  ✅ Removed binary"
    fi
else
    if [ -f "$PREFIX/bin/hei-datahub" ]; then
        rm -f "$PREFIX/bin/hei-datahub"
        echo "  ✅ Removed binary"
    fi
fi

# Remove desktop entry
if [ -z "$PREFIX" ]; then
    if [ -f "/usr/share/applications/hei-datahub.desktop" ]; then
        rm -f /usr/share/applications/hei-datahub.desktop
        echo "  ✅ Removed desktop entry"
    fi
else
    if [ -f "$PREFIX/share/applications/hei-datahub.desktop" ]; then
        rm -f "$PREFIX/share/applications/hei-datahub.desktop"
        echo "  ✅ Removed desktop entry"
    fi
fi

# Remove icons
if [ -z "$PREFIX" ]; then
    if [ -f "/usr/share/icons/hicolor/256x256/apps/hei-datahub.png" ]; then
        rm -f /usr/share/icons/hicolor/256x256/apps/hei-datahub.png
        echo "  ✅ Removed 256x256 icon"
    fi
    if [ -f "/usr/share/icons/hicolor/scalable/apps/hei-datahub.svg" ]; then
        rm -f /usr/share/icons/hicolor/scalable/apps/hei-datahub.svg
        echo "  ✅ Removed SVG icon"
    fi
else
    if [ -f "$PREFIX/share/icons/hicolor/256x256/apps/hei-datahub.png" ]; then
        rm -f "$PREFIX/share/icons/hicolor/256x256/apps/hei-datahub.png"
        echo "  ✅ Removed 256x256 icon"
    fi
    if [ -f "$PREFIX/share/icons/hicolor/scalable/apps/hei-datahub.svg" ]; then
        rm -f "$PREFIX/share/icons/hicolor/scalable/apps/hei-datahub.svg"
        echo "  ✅ Removed SVG icon"
    fi
fi

# Remove shared resources
if [ -z "$PREFIX" ]; then
    if [ -d "/usr/share/hei-datahub" ]; then
        rm -rf /usr/share/hei-datahub
        echo "  ✅ Removed shared resources"
    fi
else
    if [ -d "$PREFIX/share/hei-datahub" ]; then
        rm -rf "$PREFIX/share/hei-datahub"
        echo "  ✅ Removed shared resources"
    fi
fi

# Update caches
if command -v update-desktop-database >/dev/null 2>&1; then
    if [ -z "$PREFIX" ]; then
        update-desktop-database -q /usr/share/applications 2>/dev/null || true
    else
        update-desktop-database -q "$PREFIX/share/applications" 2>/dev/null || true
    fi
    echo "  ✅ Updated desktop database"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    if [ -z "$PREFIX" ]; then
        gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
    else
        gtk-update-icon-cache -q -t -f "$PREFIX/share/icons/hicolor" 2>/dev/null || true
    fi
    echo "  ✅ Updated icon cache"
fi

echo ""
echo "✅ Hei-DataHub has been uninstalled"
echo ""
echo "📝 Note: User data is preserved at:"
echo "   ~/.local/share/Hei-DataHub/"
echo "   ~/.config/hei-datahub/"
echo ""
read -p "Remove user data too? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$HOME/.local/share/Hei-DataHub" ]; then
        rm -rf "$HOME/.local/share/Hei-DataHub"
        echo "  ✅ Removed data directory"
    fi
    if [ -d "$HOME/.config/hei-datahub" ]; then
        rm -rf "$HOME/.config/hei-datahub"
        echo "  ✅ Removed config directory"
    fi
    echo ""
    echo "✅ All data removed"
else
    echo ""
    echo "User data preserved"
fi

echo ""
echo "👋 Thanks for using Hei-DataHub!"
echo ""
