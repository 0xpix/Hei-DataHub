#!/usr/bin/env bash
#
# build_desktop_binary.sh
# Builds a standalone PyInstaller binary for Hei-DataHub v0.60-beta
#
# Usage:
#   bash scripts/build_desktop_binary.sh
#
# Requirements:
#   - uv (package manager)
#   - pyinstaller (will be installed if not present)
#   - Linux environment (tested on Ubuntu/Debian)
#
# Output:
#   dist/linux/hei-datahub (standalone executable)

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

echo "🔨 Building Hei-DataHub v0.60-beta standalone binary"
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if uv is installed
show_progress "Checking uv installation"
if ! command -v uv >/dev/null 2>&1; then
    error_progress
    echo ""
    echo "❌ Error: uv is not installed"
    echo "   Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
complete_progress

# Check if we're in a virtual environment
if [ -z "${VIRTUAL_ENV}" ] && [ ! -f ".venv/bin/activate" ]; then
    show_progress "Creating virtual environment"
    uv venv >/dev/null 2>&1
    complete_progress
    source .venv/bin/activate
fi

# Activate venv if not already active
if [ -z "${VIRTUAL_ENV}" ] && [ -f ".venv/bin/activate" ]; then
    show_progress "Activating virtual environment"
    source .venv/bin/activate
    complete_progress
fi

# Install project with development dependencies
uv sync --dev >/dev/null 2>&1 &
if ! show_spinner $! "Installing dependencies"; then
    echo ""
    echo "❌ Failed to install dependencies. Running with output:"
    uv sync --dev
    exit 1
fi

# Install PyInstaller if not present
if ! python -c "import PyInstaller" 2>/dev/null; then
    uv add --dev pyinstaller >/dev/null 2>&1 &
    if ! show_spinner $! "Installing PyInstaller"; then
        echo ""
        echo "❌ Failed to install PyInstaller. Running with output:"
        uv add --dev pyinstaller
        exit 1
    fi
fi

# Clean previous builds
if [ -d "build" ] || [ -d "dist/hei-datahub" ]; then
    show_progress "Cleaning previous builds"
    rm -rf build dist/hei-datahub 2>/dev/null
    complete_progress
fi

# Build the binary
pyinstaller \
    --onefile \
    --name hei-datahub \
    --add-data "src/hei_datahub/infra/sql:hei_datahub/infra/sql" \
    --add-data "src/hei_datahub/ui/styles:hei_datahub/ui/styles" \
    --add-data "src/hei_datahub/ui/assets:hei_datahub/ui/assets" \
    --add-data "src/hei_datahub/assets:hei_datahub/assets" \
    --add-data "version.yaml:hei_datahub" \
    --add-data "schema.json:hei_datahub" \
    --hidden-import=hei_datahub \
    --hidden-import=hei_datahub.cli.main \
    --hidden-import=textual \
    --hidden-import=textual.widgets \
    --hidden-import=textual.containers \
    --collect-all textual \
    --clean \
    src/hei_datahub/cli/main.py \
    >/dev/null 2>&1 &

if ! show_spinner $! "Building binary (this may take 1-2 minutes)"; then
    echo ""
    echo "❌ PyInstaller build failed. Running with output:"
    echo ""
    pyinstaller \
        --onefile \
        --name hei-datahub \
        --add-data "src/hei_datahub/infra/sql:hei_datahub/infra/sql" \
        --add-data "src/hei_datahub/ui/styles:hei_datahub/ui/styles" \
        --add-data "src/hei_datahub/ui/assets:hei_datahub/ui/assets" \
        --add-data "src/hei_datahub/assets:hei_datahub/assets" \
        --add-data "version.yaml:hei_datahub" \
        --add-data "schema.json:hei_datahub" \
        --hidden-import=hei_datahub \
        --hidden-import=hei_datahub.cli.main \
        --hidden-import=textual \
        --hidden-import=textual.widgets \
        --hidden-import=textual.containers \
        --collect-all textual \
        --clean \
        src/hei_datahub/cli/main.py
    exit 1
fi

# Organize output
show_progress "Organizing output"
mkdir -p dist/linux
if [ -f "dist/hei-datahub" ]; then
    mv dist/hei-datahub dist/linux/
    complete_progress
else
    error_progress
    echo ""
    echo "❌ Build failed - binary not found"
    exit 1
fi

# Clean up spec file
rm -f hei-datahub.spec

echo ""
echo "✅ Binary built successfully!"
echo "   Version: 0.60.0-beta 'Clean-up'"
echo "   Location: dist/linux/hei-datahub"
echo "   Size: $(du -h dist/linux/hei-datahub | cut -f1)"
echo ""
echo "🚀 Test it with:"
echo "   ./dist/linux/hei-datahub --version"
echo "   ./dist/linux/hei-datahub --help"
echo ""
echo "📦 To create a desktop launcher:"
echo "   bash scripts/create_desktop_entry.sh"
echo ""
echo "💡 Distribution notes:"
echo "   • Portable within same Linux distribution family"
echo "   • Requires compatible glibc version"
echo "   • WebDAV credentials use Linux keyring (if available)"
echo "   • Data directory: ~/.local/share/Hei-DataHub"
echo ""
echo "📋 Next steps:"
echo "   1. Test: ./dist/linux/hei-datahub"
echo "   2. Install: Copy to /usr/local/bin or ~/bin"
echo "   3. Desktop: bash scripts/create_desktop_entry.sh"
echo ""
