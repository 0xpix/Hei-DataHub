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

# Get the icon path (if available)
ICON_NAME="hei-datahub"
# You can add custom icon logic here if you have an icon file

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
EOF

# Make sure the file is readable
chmod 644 "${DESKTOP_FILE}"

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi

echo ""
echo "✅ Hei-DataHub desktop launcher created successfully!"
echo "   Location: ${DESKTOP_FILE}"
echo "   Executable: ${HEI_EXEC}"
echo ""
echo "🎉 Hei-DataHub should now appear in your applications menu."
echo "   Look for it under 'Development' or search for 'Hei-DataHub'."
echo ""
