#!/usr/bin/env bash
#
# create_desktop_entry.sh
# Creates a .desktop launcher for Hei-DataHub in the user's applications menu.
#
# Usage:
#   bash scripts/create_desktop_entry.sh
#
# This script is designed for Linux systems with XDG-compliant desktop environments.

set -e

DESKTOP_DIR="${HOME}/.local/share/applications"
DESKTOP_FILE="${DESKTOP_DIR}/hei-datahub.desktop"

echo "🚀 Creating Hei-DataHub desktop launcher..."

# Create directory if it doesn't exist
mkdir -p "${DESKTOP_DIR}"

# Determine the executable path
# First try to find hei-datahub in PATH
HEI_EXEC=$(command -v hei-datahub 2>/dev/null || echo "")

if [ -z "${HEI_EXEC}" ]; then
    echo "⚠️  hei-datahub not found in PATH."
    echo "   Make sure you've installed it via:"
    echo "   uv tool install --from \"git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub\" hei-datahub"
    echo ""
    echo "   Or add ~/.local/bin to your PATH."
    exit 1
fi

# Get the icon path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
ICON_SOURCE="${PROJECT_ROOT}/assets/desktop/28.png"
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
ICON_DEST="${ICON_DIR}/hei-datahub.svg"
ICON_NAME="hei-datahub"

# Install icon if it exists
if [ -f "${ICON_SOURCE}" ]; then
    echo "📦 Installing icon..."
    mkdir -p "${ICON_DIR}"
    cp "${ICON_SOURCE}" "${ICON_DEST}"
    chmod 644 "${ICON_DEST}"
    echo "   Icon installed: ${ICON_DEST}"
else
    echo "⚠️  Icon not found at: ${ICON_SOURCE}"
    echo "   Desktop entry will use fallback icon."
fi

# Create the .desktop file
cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Hei-DataHub
Comment=Lightweight local data hub with TUI for managing datasets
Exec=${HEI_EXEC}
Icon=${ICON_NAME}
Terminal=true
Categories=Development;Utility;Database;
Keywords=data;catalog;tui;metadata;search;datahub;
StartupNotify=false
EOF

# Make sure the file is readable
chmod 644 "${DESKTOP_FILE}"

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo ""
echo "✅ Hei-DataHub desktop launcher created successfully!"
echo "   Desktop file: ${DESKTOP_FILE}"
echo "   Icon: ${ICON_DEST}"
echo "   Executable: ${HEI_EXEC}"
echo ""
echo "🎉 Hei-DataHub should now appear in your applications menu."
echo "   Look for it under 'Development' or search for 'Hei-DataHub'."
echo ""
echo "💡 If the icon doesn't appear immediately:"
echo "   - Log out and log back in, or"
echo "   - Run: gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor"
echo ""
