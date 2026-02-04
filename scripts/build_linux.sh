#!/usr/bin/env bash
#
# build_linux.sh - Build Hei-DataHub Linux executable and installers
#
# Usage: ./scripts/build_linux.sh
#
# Output:
#   - dist/hei-datahub (PyInstaller binary)
#   - release/heidatahub_<version>_amd64.deb (Debian package)
#   - release/HeiDataHub-<version>-x86_64.AppImage (AppImage)
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
PKG_NAME="heidatahub"
APP_NAME="hei-datahub"
MAINTAINER="Hei-DataHub <noreply@example.com>"
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

# Get Debian-compatible version (replace - with ~)
get_deb_version() {
    local ver="$1"
    # Debian versions use ~ for pre-release, replace - with ~
    echo "$ver" | sed 's/-/~/g'
}

# ==============================================================================
# START BUILD
# ==============================================================================

cd "$PROJECT_ROOT"

banner "HEI-DATAHUB LINUX BUILD"

log_info "Project root: $PROJECT_ROOT"
log_info "Build time: $(date '+%Y-%m-%d %H:%M:%S')"

VERSION=$(get_version)
# Replace -beta with b for filename consistency to match macOS/Windows builds
FILE_VERSION=${VERSION/-beta/b}
DEB_VERSION=$(get_deb_version "$VERSION")
log_info "Version: $VERSION (File: $FILE_VERSION, Deb: $DEB_VERSION)"

# Determine architecture
ARCH=$(uname -m)
DEB_ARCH="amd64"
if [[ "$ARCH" == "aarch64" ]]; then
    DEB_ARCH="arm64"
fi
log_info "Architecture: $ARCH (deb: $DEB_ARCH)"

# ==============================================================================
# STEP 1: Check Prerequisites
# ==============================================================================

banner "STEP 1/6: Checking Prerequisites"

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

# Check dpkg-deb (optional on non-Debian systems)
CAN_BUILD_DEB=true
if ! command -v dpkg-deb &> /dev/null; then
    if [[ -n "${CI:-}" ]]; then
        # In CI, dpkg-deb is required
        log_error "dpkg-deb not found - install dpkg package"
        exit 1
    else
        log_warn "dpkg-deb not found - .deb package will be skipped"
        log_warn "Install 'dpkg' package to build .deb on non-Debian systems"
        CAN_BUILD_DEB=false
    fi
else
    log_success "dpkg-deb: available"
fi

# ==============================================================================
# STEP 2: Install Dependencies
# ==============================================================================

banner "STEP 2/6: Installing Dependencies"

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

# Install the project itself (editable mode for development builds)
log_info "Installing hei-datahub package..."
uv pip install -e "$PROJECT_ROOT"

log_success "All dependencies installed"

# ==============================================================================
# STEP 3: Build PyInstaller Binary
# ==============================================================================

banner "STEP 3/6: Building PyInstaller Binary"

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
# Linux uses : as path separator (not ; like Windows)
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

# PyInstaller arguments
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
    "${DATA_ARGS[@]}"
)

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
# STEP 4: Prepare Packaging Assets
# ==============================================================================

banner "STEP 4/6: Preparing Packaging Assets"

# Create desktop file
DESKTOP_FILE="$PACKAGING_DIR/hei-datahub.desktop"
cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Type=Application
Name=Hei-DataHub
Comment=Lightweight local data hub with TUI for managing datasets
Exec=hei-datahub
Icon=hei-datahub
Terminal=true
Categories=Utility;Development;Database;
Keywords=data;catalog;metadata;tui;datahub;
StartupNotify=false
EOF
log_success "Created desktop file"

# Find or create icon (256x256 PNG preferred)
ICON_SRC=""
if [[ -f "$PROJECT_ROOT/assets/png/icon_1024.png" ]]; then
    ICON_SRC="$PROJECT_ROOT/assets/png/icon_1024.png"
elif [[ -f "$PROJECT_ROOT/assets/png/Hei-datahub-logo-round.png" ]]; then
    ICON_SRC="$PROJECT_ROOT/assets/png/Hei-datahub-logo-round.png"
elif [[ -f "$PROJECT_ROOT/assets/png/Hei-datahub-logo-main.png" ]]; then
    ICON_SRC="$PROJECT_ROOT/assets/png/Hei-datahub-logo-main.png"
fi

ICON_FILE="$PACKAGING_DIR/hei-datahub.png"
if [[ -n "$ICON_SRC" ]]; then
    # Try to resize with ImageMagick if available, otherwise just copy
    if command -v convert &> /dev/null; then
        convert "$ICON_SRC" -resize 256x256 "$ICON_FILE" 2>/dev/null || cp "$ICON_SRC" "$ICON_FILE"
        log_success "Created 256x256 icon from $ICON_SRC"
    else
        cp "$ICON_SRC" "$ICON_FILE"
        log_success "Copied icon from $ICON_SRC (ImageMagick not available for resize)"
    fi
else
    # Create a placeholder icon (1x1 transparent PNG)
    log_warn "No icon source found, creating placeholder"
    # Minimal valid PNG (1x1 transparent)
    printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82' > "$ICON_FILE"
fi

# ==============================================================================
# STEP 5: Build .deb Package
# ==============================================================================

banner "STEP 5/6: Building .deb Package"

DEB_ROOT="$PACKAGING_DIR/deb-root"
DEB_OUTPUT="${PKG_NAME}_${DEB_VERSION}_${DEB_ARCH}.deb"

if [[ "$CAN_BUILD_DEB" != "true" ]]; then
    log_warn "Skipping .deb build (dpkg-deb not available)"
else

log_info "Creating Debian package structure..."

# Create directory structure
mkdir -p "$DEB_ROOT/DEBIAN"
mkdir -p "$DEB_ROOT/usr/bin"
mkdir -p "$DEB_ROOT/usr/share/applications"
mkdir -p "$DEB_ROOT/usr/share/icons/hicolor/256x256/apps"

# Copy binary
cp "$DIST_DIR/hei-datahub" "$DEB_ROOT/usr/bin/hei-datahub"
chmod 755 "$DEB_ROOT/usr/bin/hei-datahub"
log_success "Copied binary to /usr/bin/"

# Copy desktop file
cp "$DESKTOP_FILE" "$DEB_ROOT/usr/share/applications/hei-datahub.desktop"
log_success "Copied desktop file to /usr/share/applications/"

# Copy icon
cp "$ICON_FILE" "$DEB_ROOT/usr/share/icons/hicolor/256x256/apps/hei-datahub.png"
log_success "Copied icon to /usr/share/icons/"

# Calculate installed size (in KB)
INSTALLED_SIZE=$(du -sk "$DEB_ROOT" | cut -f1)

# Create control file
cat > "$DEB_ROOT/DEBIAN/control" << EOF
Package: ${PKG_NAME}
Version: ${DEB_VERSION}
Section: utils
Priority: optional
Architecture: ${DEB_ARCH}
Installed-Size: ${INSTALLED_SIZE}
Depends: libc6
Maintainer: ${MAINTAINER}
Description: ${DESCRIPTION}
 Hei-DataHub is a lightweight local data hub with a terminal user interface
 (TUI) for managing datasets, metadata, and data catalogs.
EOF
log_success "Created DEBIAN/control"

# Set correct permissions for DEBIAN directory
chmod 755 "$DEB_ROOT/DEBIAN"

# Build the .deb package
log_info "Building .deb package..."
dpkg-deb --build --root-owner-group "$DEB_ROOT" "$RELEASE_DIR/$DEB_OUTPUT"

if [[ ! -f "$RELEASE_DIR/$DEB_OUTPUT" ]]; then
    log_error "Failed to create .deb package"
    exit 1
fi

DEB_SIZE=$(du -h "$RELEASE_DIR/$DEB_OUTPUT" | cut -f1)
log_success "Created: $DEB_OUTPUT ($DEB_SIZE)"
fi  # End CAN_BUILD_DEB check

# ==============================================================================
# STEP 6: Build .AppImage
# ==============================================================================

banner "STEP 6/6: Building .AppImage"

APPDIR="$PACKAGING_DIR/AppDir"
APPIMAGE_OUTPUT="HeiDataHub-${FILE_VERSION}-x86_64.AppImage"

log_info "Creating AppDir structure..."

# Create AppDir structure
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy binary
cp "$DIST_DIR/hei-datahub" "$APPDIR/usr/bin/hei-datahub"
chmod 755 "$APPDIR/usr/bin/hei-datahub"

# Copy desktop file to AppDir root (required by AppImage)
cp "$DESKTOP_FILE" "$APPDIR/hei-datahub.desktop"
# Also copy to standard location
cp "$DESKTOP_FILE" "$APPDIR/usr/share/applications/hei-datahub.desktop"

# Copy icon to AppDir root (required by AppImage)
cp "$ICON_FILE" "$APPDIR/hei-datahub.png"
# Also copy to standard location
cp "$ICON_FILE" "$APPDIR/usr/share/icons/hicolor/256x256/apps/hei-datahub.png"

# Create AppRun script
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
# AppRun for Hei-DataHub AppImage
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/hei-datahub" "$@"
EOF
chmod 755 "$APPDIR/AppRun"
log_success "Created AppDir structure"

# Download appimagetool if not present
APPIMAGETOOL="$PACKAGING_DIR/appimagetool"
if [[ ! -f "$APPIMAGETOOL" ]]; then
    log_info "Downloading appimagetool..."
    APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"

    if command -v curl &> /dev/null; then
        curl -L -o "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
    elif command -v wget &> /dev/null; then
        wget -O "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
    else
        log_error "Neither curl nor wget available to download appimagetool"
        exit 1
    fi
    chmod +x "$APPIMAGETOOL"
    log_success "Downloaded appimagetool"
fi

# Build AppImage
log_info "Building AppImage..."
# ARCH env var tells appimagetool the target architecture
ARCH=x86_64 "$APPIMAGETOOL" --no-appstream "$APPDIR" "$RELEASE_DIR/$APPIMAGE_OUTPUT" 2>&1 || {
    # If running in container without FUSE, try extracting and running
    log_warn "Direct execution failed, trying extracted mode..."
    "$APPIMAGETOOL" --appimage-extract 2>/dev/null || true
    if [[ -d "squashfs-root" ]]; then
        ARCH=x86_64 ./squashfs-root/AppRun --no-appstream "$APPDIR" "$RELEASE_DIR/$APPIMAGE_OUTPUT"
        rm -rf squashfs-root
    else
        log_error "Failed to build AppImage"
        exit 1
    fi
}

if [[ ! -f "$RELEASE_DIR/$APPIMAGE_OUTPUT" ]]; then
    log_error "Failed to create AppImage"
    exit 1
fi

chmod +x "$RELEASE_DIR/$APPIMAGE_OUTPUT"
APPIMAGE_SIZE=$(du -h "$RELEASE_DIR/$APPIMAGE_OUTPUT" | cut -f1)
log_success "Created: $APPIMAGE_OUTPUT ($APPIMAGE_SIZE)"

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

# Validate .deb package (if built)
if [[ -f "$RELEASE_DIR/$DEB_OUTPUT" ]]; then
    log_info "Validating .deb package..."
    echo ""
    dpkg-deb -I "$RELEASE_DIR/$DEB_OUTPUT"
    echo ""
    dpkg-deb -c "$RELEASE_DIR/$DEB_OUTPUT"
    echo ""
else
    log_warn ".deb package was not built (skipped)"
fi

# Validate AppImage exists
log_info "Validating AppImage..."
if [[ -f "$RELEASE_DIR/$APPIMAGE_OUTPUT" ]]; then
    log_success "AppImage exists and is executable"
    file "$RELEASE_DIR/$APPIMAGE_OUTPUT"
else
    log_error "AppImage not found!"
    exit 1
fi

# ==============================================================================
# BUILD COMPLETE
# ==============================================================================

banner "BUILD SUCCESSFUL"

echo "Artifacts created in release/:"
echo ""
if [[ -f "$RELEASE_DIR/$DEB_OUTPUT" ]]; then
    echo "  📦 .deb package:  $DEB_OUTPUT"
fi
echo "  📦 AppImage:      $APPIMAGE_OUTPUT"
echo ""

# Final verification
MISSING=0

# .deb is only required in CI
if [[ "$CAN_BUILD_DEB" == "true" ]] && [[ ! -f "$RELEASE_DIR/$DEB_OUTPUT" ]]; then
    log_error "Missing: .deb package"
    MISSING=1
fi

if [[ ! -f "$RELEASE_DIR/$APPIMAGE_OUTPUT" ]]; then
    log_error "Missing: AppImage"
    MISSING=1
fi

if [[ $MISSING -eq 1 ]]; then
    log_error "Build incomplete - some artifacts are missing!"
    exit 1
fi

if [[ "$CAN_BUILD_DEB" == "true" ]]; then
    log_success "All artifacts created successfully!"
else
    log_success "AppImage created successfully! (.deb skipped - dpkg-deb not available)"
fi
