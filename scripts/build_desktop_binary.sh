#!/usr/bin/env bash
#
# build_desktop_binary.sh
# Builds a standalone PyInstaller binary for Hei-DataHub
#
# Usage:
#   bash scripts/build_desktop_binary.sh
#
# Requirements:
#   - uv (package manager)
#   - pyinstaller (will be installed if not present)
#   - Active Python environment with hei-datahub installed
#
# Output:
#   dist/linux/hei-datahub (standalone executable)

set -e

echo "🔨 Building Hei-DataHub standalone binary..."
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "❌ Error: uv is not installed"
    echo "   Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if we're in a virtual environment
if [ -z "${VIRTUAL_ENV}" ] && [ ! -f ".venv/bin/activate" ]; then
    echo "⚠️  No virtual environment detected."
    echo "   Creating .venv with uv..."
    uv venv
    source .venv/bin/activate
fi

# Activate venv if not already active
if [ -z "${VIRTUAL_ENV}" ] && [ -f ".venv/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Ensure project is installed in editable mode
echo "📦 Installing project dependencies with uv..."
uv pip install -e .
echo ""

# Install PyInstaller if not present
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "📦 Installing PyInstaller with uv..."
    uv pip install pyinstaller
    echo ""
fi

# Clean previous builds
if [ -d "build" ]; then
    echo "🧹 Cleaning previous build artifacts..."
    rm -rf build
fi

if [ -d "dist/hei-datahub" ]; then
    rm -rf dist/hei-datahub
fi

# Build the binary
echo "🏗️  Running PyInstaller..."
echo ""

pyinstaller \
    --onefile \
    --name hei-datahub \
    --add-data "src/mini_datahub/infra/sql:mini_datahub/infra/sql" \
    --add-data "src/mini_datahub/ui/styles:mini_datahub/ui/styles" \
    --add-data "src/mini_datahub/ui/assets:mini_datahub/ui/assets" \
    --add-data "src/hei_datahub/assets:hei_datahub/assets" \
    --add-data "src/mini_datahub/version.yaml:mini_datahub" \
    --hidden-import=mini_datahub \
    --hidden-import=mini_datahub.cli.main \
    --hidden-import=textual \
    --collect-all textual \
    --clean \
    src/mini_datahub/cli/main.py

# Organize output
mkdir -p dist/linux
if [ -f "dist/hei-datahub" ]; then
    mv dist/hei-datahub dist/linux/
    echo ""
    echo "✅ Binary built successfully!"
    echo "   Location: dist/linux/hei-datahub"
    echo "   Size: $(du -h dist/linux/hei-datahub | cut -f1)"
    echo ""
    echo "🚀 Test it with:"
    echo "   ./dist/linux/hei-datahub --version"
    echo ""
    echo "📦 To create a desktop launcher for the binary:"
    echo "   Update scripts/create_desktop_entry.sh to point to:"
    echo "   $(pwd)/dist/linux/hei-datahub"
else
    echo "❌ Build failed - binary not found"
    exit 1
fi

# Clean up spec file
rm -f hei-datahub.spec

echo "💡 Note: The binary is portable but still requires:"
echo "   - Compatible Linux distribution (glibc version)"
echo "   - Standard system libraries"
echo ""
