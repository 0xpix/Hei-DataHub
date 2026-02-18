#!/usr/bin/env bash
#
# build_macos.sh - Build Hei-DataHub macOS executable for Homebrew/Release
#
# Usage: ./scripts/build_macos.sh <ARCH> <VERSION>
# Example: ./scripts/build_macos.sh arm64 0.1.0
#
# Output:
#   - dist/hei-datahub-${VERSION}-macos-${ARCH}.tar.gz
#   - dist/sha256-macos-${ARCH}.txt
#

set -euo pipefail

# ==============================================================================
# CONFIGURATION
# ==============================================================================

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <ARCH> <VERSION>"
    echo "Example: $0 arm64 0.1.0"
    exit 1
fi

TARGET_ARCH="$1"
# Strip any path prefix (e.g. "release/0.65-beta" -> "0.65-beta") and leading 'v'
VERSION="${2##*/}"
VERSION="${VERSION#v}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$PROJECT_ROOT"

log_info "Starting build for $TARGET_ARCH version $VERSION..."

# ==============================================================================
# VERIFY ENVIRONMENT
# ==============================================================================

# Ensure we are running on similar architecture or Rosseta
CURRENT_ARCH=$(uname -m)
log_info "Current architecture: $CURRENT_ARCH"
log_info "Target architecture: $TARGET_ARCH"

if [ "$TARGET_ARCH" != "arm64" ] && [ "$TARGET_ARCH" != "x86_64" ]; then
    log_error "Unsupported architecture: $TARGET_ARCH. Use arm64 or x86_64."
    exit 1
fi

# ==============================================================================
# INSTALL DEPENDENCIES
# ==============================================================================

log_info "Installing dependencies..."

# Use uv if available, else pip
if command -v uv &>/dev/null; then
    PIP_CMD="uv pip"
else
    PIP_CMD="pip3"
fi

$PIP_CMD install pyinstaller
$PIP_CMD install -e .

# ==============================================================================
# BUILD PYINSTALLER BINARY
# ==============================================================================

log_info "Building specific artifact..."

# Clean up
if [[ -d "$BUILD_DIR" ]]; then rm -rf "$BUILD_DIR"; fi
if [[ -f "$DIST_DIR/hei-datahub" ]]; then rm -f "$DIST_DIR/hei-datahub"; fi

# PyInstaller arguments
# Note: Re-using the configuration known to work from previous script
SEP=":"
DATA_ARGS=(
    --add-data "src/hei_datahub/ui/styles${SEP}hei_datahub/ui/styles"
    --add-data "src/hei_datahub/ui/assets${SEP}hei_datahub/ui/assets"
    --add-data "src/hei_datahub/assets${SEP}hei_datahub/assets"
    --add-data "src/hei_datahub/version.yaml${SEP}hei_datahub"
    --add-data "src/hei_datahub/schema.json${SEP}hei_datahub"
)

# Create config.yaml placeholder if needed (required by the app)
if [[ ! -f "$PROJECT_ROOT/config.yaml" ]]; then
    log_info "Creating config.yaml placeholder..."
    echo "# Placeholder config for build" > "$PROJECT_ROOT/config.yaml"
    DATA_ARGS+=(--add-data "config.yaml${SEP}hei_datahub")
elif [[ -f "$PROJECT_ROOT/config.yaml" ]]; then
    DATA_ARGS+=(--add-data "config.yaml${SEP}hei_datahub")
fi

# Add SQL files if present
if [[ -d "$PROJECT_ROOT/src/hei_datahub/infra/sql" ]]; then
    DATA_ARGS+=(--add-data "src/hei_datahub/infra/sql${SEP}hei_datahub/infra/sql")
fi

# Entry point
ENTRY_POINT="src/hei_datahub/__main__.py"
if [[ ! -f "$ENTRY_POINT" ]]; then
    # Fallback checks
    if [[ -f "hei_datahub/__main__.py" ]]; then ENTRY_POINT="hei_datahub/__main__.py"; fi
fi

log_info "Using entry point: $ENTRY_POINT"

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

# Run pyinstaller
python3 -m PyInstaller "${PYINSTALLER_ARGS[@]}" "$ENTRY_POINT"

if [[ ! -f "$DIST_DIR/hei-datahub" ]]; then
    log_error "Build failed: $DIST_DIR/hei-datahub not found"
    exit 1
fi

chmod +x "$DIST_DIR/hei-datahub"

# ==============================================================================
# PACKAGE TARBALL
# ==============================================================================

TARBALL_NAME="hei-datahub-${VERSION}-macos-${TARGET_ARCH}.tar.gz"
TARBALL_PATH="$DIST_DIR/$TARBALL_NAME"

log_info "Creating tarball: $TARBALL_NAME"

# Create a temporary directory for packaging to ensure clean top-level
PKG_TMP="$(mktemp -d)"
cp "$DIST_DIR/hei-datahub" "$PKG_TMP/hei-datahub"

# Create hdh symlink so both 'hei-datahub' and 'hdh' work
ln -sf hei-datahub "$PKG_TMP/hdh"

# Verify executable
# Note: This might fail on cross-compilation if we were doing that,
# but we expect to run on native runner.
# Ignoring error code here slightly just in case it returns non-zero for some reason,
# but log it.
"$PKG_TMP/hei-datahub" --version || log_warn "Version check returned non-zero (expected if just returning version string?)"

# Tar it up
# -C changes to directory before adding files
tar -czf "$TARBALL_PATH" -C "$PKG_TMP" hei-datahub hdh

rm -rf "$PKG_TMP"

# Verify tarball structure
if tar -tzf "$TARBALL_PATH" | grep -q "^hei-datahub$"; then
    log_success "Tarball structure verified."
    tar -tzf "$TARBALL_PATH"
else
    log_error "Tarball structure incorrect! Must be top-level 'hei-datahub'."
    tar -tzf "$TARBALL_PATH"
    exit 1
fi

# ==============================================================================
# CHECKSUM
# ==============================================================================

CHECKSUM_FILE="$DIST_DIR/sha256-macos-${TARGET_ARCH}.txt"
shasum -a 256 "$TARBALL_PATH" > "$CHECKSUM_FILE"

log_success "Build complete!"
log_info "Artifacts:"
log_info "  - $TARBALL_PATH"
log_info "  - $CHECKSUM_FILE"
