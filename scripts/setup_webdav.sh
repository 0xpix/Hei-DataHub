#!/usr/bin/env bash
#
# Quick setup script for WebDAV/Heibox integration
#
# Usage: ./scripts/setup_webdav.sh

set -e

echo "=================================================="
echo "Hei-DataHub WebDAV/Heibox Setup"
echo "=================================================="
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if config directory exists
CONFIG_DIR="$HOME/.config/hei-datahub"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

if [ ! -d "$CONFIG_DIR" ]; then
    echo -e "${YELLOW}Creating config directory: $CONFIG_DIR${NC}"
    mkdir -p "$CONFIG_DIR"
fi

# Prompt for configuration
echo -e "${BLUE}WebDAV Configuration${NC}"
echo
echo "Enter your Heibox/WebDAV details:"
echo

# Base URL
read -p "WebDAV URL [https://heibox.uni-heidelberg.de/seafdav]: " WEBDAV_URL
WEBDAV_URL=${WEBDAV_URL:-https://heibox.uni-heidelberg.de/seafdav}

# Library name
read -p "Library/Folder name [hei-datahub-catalog]: " LIBRARY_NAME
LIBRARY_NAME=${LIBRARY_NAME:-hei-datahub-catalog}

# Username
read -p "Username (WebDAV ID): " USERNAME

# Token (hidden input)
echo -n "WebDAV Token (hidden): "
read -s TOKEN
echo

# Validation
if [ -z "$USERNAME" ] || [ -z "$TOKEN" ]; then
    echo -e "${RED}Error: Username and token are required${NC}"
    exit 1
fi

# Test connection
echo
echo -e "${BLUE}Testing WebDAV connection...${NC}"

TEST_URL="$WEBDAV_URL/$LIBRARY_NAME/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$TOKEN" \
    -X PROPFIND \
    -H "Depth: 0" \
    "$TEST_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "207" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Connection successful!${NC}"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo -e "${RED}✗ Authentication failed (HTTP $HTTP_CODE)${NC}"
    echo "  Check your username and token"
    exit 1
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${RED}✗ Library not found (HTTP 404)${NC}"
    echo "  Check library name: $LIBRARY_NAME"
    exit 1
else
    echo -e "${YELLOW}⚠ Connection test failed (HTTP $HTTP_CODE)${NC}"
    echo "  Continuing anyway..."
fi

# Update config file
echo
echo -e "${BLUE}Updating config file: $CONFIG_FILE${NC}"

if [ -f "$CONFIG_FILE" ]; then
    # Backup existing config
    BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${YELLOW}Backed up existing config to: $BACKUP_FILE${NC}"
fi

# Check if storage section exists
if grep -q "^storage:" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}Storage section exists, updating...${NC}"
    # Update existing storage section (using sed)
    sed -i.bak \
        -e "/^storage:/,/^[^ ]/ s|backend:.*|backend: \"webdav\"|" \
        -e "/^storage:/,/^[^ ]/ s|base_url:.*|base_url: \"$WEBDAV_URL\"|" \
        -e "/^storage:/,/^[^ ]/ s|library:.*|library: \"$LIBRARY_NAME\"|" \
        "$CONFIG_FILE"
    rm -f "${CONFIG_FILE}.bak"
else
    # Append storage section
    echo -e "${YELLOW}Adding storage section to config...${NC}"
    cat >> "$CONFIG_FILE" <<EOF

# Storage backend (webdav for cloud, filesystem for local)
storage:
  backend: "webdav"
  base_url: "$WEBDAV_URL"
  library: "$LIBRARY_NAME"
  username: ""  # Uses HEIBOX_USERNAME env var
  password_env: "HEIBOX_WEBDAV_TOKEN"
  connect_timeout: 5
  read_timeout: 60
  max_retries: 3
EOF
fi

# Set environment variables
echo
echo -e "${BLUE}Setting environment variables${NC}"

SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

echo "Detected shell config: $SHELL_RC"

# Check if variables already exist
if grep -q "HEIBOX_USERNAME" "$SHELL_RC" 2>/dev/null; then
    echo -e "${YELLOW}Environment variables already exist in $SHELL_RC${NC}"
    echo "Please update them manually if needed"
else
    echo
    echo "# Hei-DataHub WebDAV Configuration" >> "$SHELL_RC"
    echo "export HEIBOX_URL=\"$WEBDAV_URL\"" >> "$SHELL_RC"
    echo "export HEIBOX_LIB=\"$LIBRARY_NAME\"" >> "$SHELL_RC"
    echo "export HEIBOX_USERNAME=\"$USERNAME\"" >> "$SHELL_RC"
    echo "export HEIBOX_WEBDAV_TOKEN=\"$TOKEN\"" >> "$SHELL_RC"
    echo
    echo -e "${GREEN}✓ Environment variables added to $SHELL_RC${NC}"
fi

# Export for current session
export HEIBOX_URL="$WEBDAV_URL"
export HEIBOX_LIB="$LIBRARY_NAME"
export HEIBOX_USERNAME="$USERNAME"
export HEIBOX_WEBDAV_TOKEN="$TOKEN"

# Summary
echo
echo "=================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================================="
echo
echo "Configuration:"
echo "  - Config file: $CONFIG_FILE"
echo "  - Shell config: $SHELL_RC"
echo "  - WebDAV URL: $WEBDAV_URL"
echo "  - Library: $LIBRARY_NAME"
echo "  - Username: $USERNAME"
echo
echo "Next steps:"
echo "  1. Restart your terminal (or run: source $SHELL_RC)"
echo "  2. Launch Hei-DataHub: hei-datahub"
echo "  3. Press 'c' to open Cloud Files"
echo
echo "Troubleshooting:"
echo "  - Test connection: curl -u \"\$HEIBOX_USERNAME:\$HEIBOX_WEBDAV_TOKEN\" \"$TEST_URL\" -X PROPFIND -H \"Depth: 1\""
echo "  - View logs: tail -f ~/.local/state/hei-datahub/logs/app.log"
echo "  - Documentation: WEBDAV_INTEGRATION.md"
echo
echo -e "${BLUE}Tip:${NC} To switch back to filesystem mode, set 'storage.backend: filesystem' in config.yaml"
echo
