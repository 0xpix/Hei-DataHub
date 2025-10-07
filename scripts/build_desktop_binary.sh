#!/usr/bin/env bash
#
# build_desktop_binary.sh
# Builds a standalone PyInstaller binary for Hei-DataHub
#
# Usage:
#   bash scripts/build_desktop_binary.sh
#
# Requirements:
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

# Check if we're in a virtual environment
if [ -z "${VIRTUAL_ENV}" ] && [ ! -f ".venv/bin/activate" ]; then
    echo "⚠️  No virtual environment detected."
    echo "   Please activate your venv first:"
    echo "   source .venv/bin/activate"
    exit 1
fi

# Install PyInstaller if not present
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
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
