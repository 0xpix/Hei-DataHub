#!/usr/bin/env bash
# Developer setup script for Hei-DataHub

set -e

echo "🚀 Setting up Hei-DataHub development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not found."
    echo "📥 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ Found uv $(uv --version)"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.9 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Install dependencies with uv
echo "📦 Installing dependencies with uv..."
uv sync --python /usr/bin/python --dev

# Activate virtual environment
echo "🔧 Virtual environment created at .venv"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run the TUI:"
echo "     mini-datahub"
echo ""
echo "  3. Reindex datasets:"
echo "     mini-datahub reindex"
echo ""
echo "  4. Run tests:"
echo "     pytest"
echo ""
echo "Happy hacking! 🎉"
