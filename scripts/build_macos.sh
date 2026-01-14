#!/usr/bin/env bash
#
# build_macos.sh - Build Hei-DataHub macOS executable and DMG installer
#
# Usage: ./scripts/build_macos.sh
#
# Output:
#   - dist/hei-datahub (PyInstaller binary)
#   - release/HeiDataHub-<version>-macos-<arch>.dmg (DMG installer)
#   - release/HeiDataHub-<version>-macos-<arch>.zip (Zipped .app bundle)
#

set -euo pipefail

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"
RELEASE_DIR="$PROJECT_ROOT/release"
BUILD_DIR="$PROJECT_ROOT/build"
PACKAGING_DIR="$PROJECT_ROOT/packaging"

# Package metadata
APP_NAME="Hei-DataHub"
BUNDLE_ID="com.heidatahub.app"
DESCRIPTION="Lightweight local data hub with TUI for managing datasets"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

banner() {
    echo ""
    echo "======================================================================"
    echo "  $1"
    echo "======================================================================"
    echo ""
}

# ==============================================================================
# DETERMINE VERSION
# ==============================================================================

get_version() {
    # Try to get version from git tag first (strip leading 'v')
    if [[ -n "${GITHUB_REF_NAME:-}" && "${GITHUB_REF_TYPE:-}" == "tag" ]]; then
        echo "${GITHUB_REF_NAME#v}"
        return
    fi

    # Try git describe (strip leading 'v')
    if tag=$(git describe --tags --exact-match 2>/dev/null); then
        echo "${tag#v}"
        return
    fi

    # Try to extract from version.yaml
    if [[ -f "$PROJECT_ROOT/version.yaml" ]]; then
        version=$(grep -E "^version:" "$PROJECT_ROOT/version.yaml" | sed 's/version:[[:space:]]*//' | tr -d "'" | tr -d '"')
        if [[ -n "$version" ]]; then
            echo "$version"
            return
        fi
    fi

    # Fallback to dev
    echo "0.0.0-dev"
}

# ==============================================================================
# START BUILD
# ==============================================================================

cd "$PROJECT_ROOT"

banner "HEI-DATAHUB MACOS BUILD"

log_info "Project root: $PROJECT_ROOT"
log_info "Build time: $(date '+%Y-%m-%d %H:%M:%S')"

VERSION=$(get_version)
log_info "Version: $VERSION"

# Determine architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    ARCH_NAME="x86_64"
elif [[ "$ARCH" == "arm64" ]]; then
    ARCH_NAME="arm64"
else
    ARCH_NAME="$ARCH"
fi
log_info "Architecture: $ARCH_NAME"

# ==============================================================================
# STEP 1: Check Prerequisites
# ==============================================================================

banner "STEP 1/4: Checking Prerequisites"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
log_success "Python: $PYTHON_VERSION"

# Check uv
if ! command -v uv &> /dev/null; then
    log_error "uv not found - install from https://docs.astral.sh/uv/"
    exit 1
fi
UV_VERSION=$(uv --version)
log_success "uv: $UV_VERSION"

# Check for create-dmg (optional)
CAN_BUILD_DMG=true
if ! command -v create-dmg &> /dev/null; then
    if ! command -v hdiutil &> /dev/null; then
        log_warn "Neither create-dmg nor hdiutil found - DMG will use basic hdiutil"
    fi
fi
log_success "DMG tools: available"

# ==============================================================================
# STEP 2: Install Dependencies
# ==============================================================================

banner "STEP 2/4: Installing Dependencies"

log_info "Installing PyInstaller..."
uv pip install pyinstaller

# Install project dependencies
if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
    log_info "Installing from requirements.txt..."
    uv pip install -r "$PROJECT_ROOT/requirements.txt"
fi

if [[ -f "$PROJECT_ROOT/requirements-dev.txt" ]]; then
    log_info "Installing from requirements-dev.txt..."
    uv pip install -r "$PROJECT_ROOT/requirements-dev.txt"
fi

# Install the project itself
log_info "Installing hei-datahub package..."
uv pip install -e "$PROJECT_ROOT"

log_success "All dependencies installed"

# ==============================================================================
# STEP 3: Build PyInstaller Binary
# ==============================================================================

banner "STEP 3/4: Building PyInstaller Binary"

# Check for entry point
ENTRY_POINT=""
if [[ -f "$PROJECT_ROOT/src/hei_datahub/__main__.py" ]]; then
    ENTRY_POINT="$PROJECT_ROOT/src/hei_datahub/__main__.py"
    log_success "Entry point: src/hei_datahub/__main__.py"
elif [[ -f "$PROJECT_ROOT/hei_datahub/__main__.py" ]]; then
    ENTRY_POINT="$PROJECT_ROOT/hei_datahub/__main__.py"
    log_success "Entry point: hei_datahub/__main__.py"
elif [[ -f "$PROJECT_ROOT/main.py" ]]; then
    ENTRY_POINT="$PROJECT_ROOT/main.py"
    log_success "Entry point: main.py"
else
    log_error "No entry point found! Expected one of:"
    log_error "  - src/hei_datahub/__main__.py"
    log_error "  - hei_datahub/__main__.py"
    log_error "  - main.py"
    exit 1
fi

# Clean previous builds
log_info "Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR" "$PACKAGING_DIR" 2>/dev/null || true
rm -f "$PROJECT_ROOT/hei-datahub.spec" 2>/dev/null || true

# Create directories
mkdir -p "$RELEASE_DIR"
mkdir -p "$PACKAGING_DIR"

# Create config.yaml placeholder if needed (required by the app)
if [[ ! -f "$PROJECT_ROOT/config.yaml" ]]; then
    log_info "Creating config.yaml placeholder..."
    echo "# Placeholder config for build" > "$PROJECT_ROOT/config.yaml"
fi

# Build PyInstaller command
# macOS uses : as path separator (like Linux)
SEP=":"

# Data files to include
DATA_ARGS=(
    --add-data "src/hei_datahub/ui/styles${SEP}hei_datahub/ui/styles"
    --add-data "src/hei_datahub/ui/assets${SEP}hei_datahub/ui/assets"
    --add-data "src/hei_datahub/assets${SEP}hei_datahub/assets"
    --add-data "src/hei_datahub/version.yaml${SEP}hei_datahub"
    --add-data "src/hei_datahub/schema.json${SEP}hei_datahub"
    --add-data "config.yaml${SEP}hei_datahub"
)

# Add SQL files if present
if [[ -d "$PROJECT_ROOT/src/hei_datahub/infra/sql" ]]; then
    DATA_ARGS+=(--add-data "src/hei_datahub/infra/sql${SEP}hei_datahub/infra/sql")
fi

# Find icon - convert .ico to .icns if needed
ICON_ARG=""
ICNS_PATH="$PROJECT_ROOT/assets/icons/hei-datahub.icns"
ICO_PATH="$PROJECT_ROOT/assets/icons/hei-datahub.ico"

if [[ -f "$ICNS_PATH" ]]; then
    ICON_ARG="--icon=$ICNS_PATH"
    log_success "Found .icns icon"
elif [[ -f "$ICO_PATH" ]]; then
    # Convert .ico to .icns using sips and iconutil (macOS built-in)
    log_info "Converting .ico to .icns..."
    ICONSET_DIR="$PROJECT_ROOT/assets/icons/hei-datahub.iconset"
    mkdir -p "$ICONSET_DIR"

    # Extract icon from .ico and create iconset
    # sips can convert ico to png
    sips -s format png "$ICO_PATH" --out "$ICONSET_DIR/icon_512x512.png" 2>/dev/null || true

    if [[ -f "$ICONSET_DIR/icon_512x512.png" ]]; then
        # Create required sizes
        sips -z 16 16 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_16x16.png" 2>/dev/null || true
        sips -z 32 32 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_16x16@2x.png" 2>/dev/null || true
        sips -z 32 32 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_32x32.png" 2>/dev/null || true
        sips -z 64 64 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_32x32@2x.png" 2>/dev/null || true
        sips -z 128 128 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_128x128.png" 2>/dev/null || true
        sips -z 256 256 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_128x128@2x.png" 2>/dev/null || true
        sips -z 256 256 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_256x256.png" 2>/dev/null || true
        sips -z 512 512 "$ICONSET_DIR/icon_512x512.png" --out "$ICONSET_DIR/icon_256x256@2x.png" 2>/dev/null || true
        cp "$ICONSET_DIR/icon_512x512.png" "$ICONSET_DIR/icon_512x512@2x.png" 2>/dev/null || true

        # Convert iconset to icns
        iconutil -c icns "$ICONSET_DIR" -o "$ICNS_PATH" 2>/dev/null && {
            ICON_ARG="--icon=$ICNS_PATH"
            log_success "Converted .ico to .icns"
        } || {
            log_warn "iconutil failed, using .ico directly"
            ICON_ARG="--icon=$ICO_PATH"
        }

        # Cleanup iconset
        rm -rf "$ICONSET_DIR"
    else
        log_warn "Failed to convert icon, using .ico directly"
        ICON_ARG="--icon=$ICO_PATH"
    fi
fi

# PyInstaller arguments for macOS
# Using --onefile for a single executable
PYINSTALLER_ARGS=(
    --noconfirm
    --onefile
    --console
    --name "hei-datahub"
    --clean
    --paths "src"
    --collect-all textual
    --collect-all rich
    --collect-all hei_datahub
    --hidden-import "hei_datahub.ui.views"
    --hidden-import "hei_datahub.ui.views.update"
    --hidden-import "hei_datahub.ui.views.home"
    --hidden-import "hei_datahub.ui.views.main"
    --hidden-import "hei_datahub.services.update_check"
    --hidden-import "hei_datahub.infra.sql"
    --osx-bundle-identifier "$BUNDLE_ID"
    "${DATA_ARGS[@]}"
)

if [[ -n "$ICON_ARG" ]]; then
    PYINSTALLER_ARGS+=("$ICON_ARG")
fi

log_info "Running PyInstaller (this may take a while)..."
python3 -m PyInstaller "${PYINSTALLER_ARGS[@]}" "$ENTRY_POINT"

# Check if build succeeded
if [[ ! -f "$DIST_DIR/hei-datahub" ]]; then
    log_error "PyInstaller build failed - no output binary found"
    exit 1
fi

BINARY_SIZE=$(du -h "$DIST_DIR/hei-datahub" | cut -f1)
log_success "PyInstaller build complete: hei-datahub ($BINARY_SIZE)"

# ==============================================================================
# STEP 4: Create Release Artifacts
# ==============================================================================

banner "STEP 4/4: Creating Release Artifacts"

# Output naming
OUTPUT_BASE="HeiDataHub-${VERSION}-macos-${ARCH_NAME}"

# Copy standalone binary
BINARY_OUTPUT="$RELEASE_DIR/${OUTPUT_BASE}"
cp "$DIST_DIR/hei-datahub" "$BINARY_OUTPUT"
chmod +x "$BINARY_OUTPUT"
log_success "Created standalone binary: ${OUTPUT_BASE}"

# Create a simple .app bundle wrapper (for GUI launchers)
APP_DIR="$PACKAGING_DIR/${APP_NAME}.app"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Copy binary
cp "$DIST_DIR/hei-datahub" "$APP_DIR/Contents/MacOS/hei-datahub"
chmod +x "$APP_DIR/Contents/MacOS/hei-datahub"

# Create launcher script that opens Terminal (TUI app needs terminal)
# This MUST be created before Info.plist references it
cat > "$APP_DIR/Contents/MacOS/Hei-DataHub" << 'LAUNCHER'
#!/bin/bash
# Hei-DataHub Launcher - Opens TUI app in Terminal
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BINARY="${DIR}/hei-datahub"

# Check if we're already in a terminal
if [ -t 0 ]; then
    # Already in terminal, just run
    exec "$BINARY" "$@"
else
    # Not in terminal, open Terminal.app and run
    osascript <<EOF
tell application "Terminal"
    activate
    do script "\"${BINARY}\"; exit"
end tell
EOF
fi
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/Hei-DataHub"

# Create Info.plist - executable points to our launcher
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>Hei-DataHub</string>
    <key>CFBundleIdentifier</key>
    <string>${BUNDLE_ID}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleExecutable</key>
    <string>Hei-DataHub</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.developer-tools</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>
EOF

# Copy icon to Resources
if [[ -f "$ICNS_PATH" ]]; then
    cp "$ICNS_PATH" "$APP_DIR/Contents/Resources/icon.icns"
    log_success "Added app icon"
elif [[ -f "$ICO_PATH" ]]; then
    # Try to use the ico as fallback
    cp "$ICO_PATH" "$APP_DIR/Contents/Resources/icon.icns"
    log_warn "Using .ico as icon (may not display correctly)"
else
    log_warn "No icon found"
fi

log_success "Created .app bundle: ${APP_NAME}.app"

# Create ZIP of the .app bundle
ZIP_OUTPUT="$RELEASE_DIR/${OUTPUT_BASE}.zip"
cd "$PACKAGING_DIR"
zip -r "$ZIP_OUTPUT" "${APP_NAME}.app"
cd "$PROJECT_ROOT"
ZIP_SIZE=$(du -h "$ZIP_OUTPUT" | cut -f1)
log_success "Created: ${OUTPUT_BASE}.zip ($ZIP_SIZE)"

# Create DMG
DMG_OUTPUT="$RELEASE_DIR/${OUTPUT_BASE}.dmg"
log_info "Creating DMG..."

if command -v create-dmg &> /dev/null; then
    # Use create-dmg for prettier DMG
    create-dmg \
        --volname "HeiDataHub" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --app-drop-link 450 185 \
        "$DMG_OUTPUT" \
        "$APP_DIR" 2>/dev/null || {
            # Fallback to hdiutil if create-dmg fails
            log_warn "create-dmg failed, using hdiutil..."
            hdiutil create -volname "HeiDataHub" -srcfolder "$APP_DIR" -ov -format UDZO "$DMG_OUTPUT"
        }
else
    # Use hdiutil (built into macOS)
    hdiutil create -volname "HeiDataHub" -srcfolder "$APP_DIR" -ov -format UDZO "$DMG_OUTPUT"
fi

if [[ -f "$DMG_OUTPUT" ]]; then
    DMG_SIZE=$(du -h "$DMG_OUTPUT" | cut -f1)
    log_success "Created: ${OUTPUT_BASE}.dmg ($DMG_SIZE)"
else
    log_warn "DMG creation failed - ZIP is still available"
fi

# ==============================================================================
# VALIDATION
# ==============================================================================

banner "VALIDATION"

log_info "Listing output directories..."
echo ""
echo "  dist/"
ls -la "$DIST_DIR" 2>/dev/null || echo "    (empty or not found)"
echo ""
echo "  release/"
ls -la "$RELEASE_DIR" 2>/dev/null || echo "    (empty or not found)"
echo ""

# ==============================================================================
# BUILD COMPLETE
# ==============================================================================

banner "BUILD SUCCESSFUL"

echo "Artifacts created in release/:"
echo ""
if [[ -f "$BINARY_OUTPUT" ]]; then
    echo "  📦 Binary:  ${OUTPUT_BASE}"
fi
if [[ -f "$ZIP_OUTPUT" ]]; then
    echo "  📦 ZIP:     ${OUTPUT_BASE}.zip"
fi
if [[ -f "$DMG_OUTPUT" ]]; then
    echo "  📦 DMG:     ${OUTPUT_BASE}.dmg"
fi
echo ""

# Final verification
MISSING=0
if [[ ! -f "$BINARY_OUTPUT" ]] && [[ ! -f "$ZIP_OUTPUT" ]]; then
    log_error "No artifacts found in release/"
    MISSING=1
fi

if [[ $MISSING -eq 1 ]]; then
    log_error "Build incomplete - some artifacts are missing!"
    exit 1
fi

log_success "macOS build complete!"
