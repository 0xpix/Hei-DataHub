#!/usr/bin/env bash
# Verification script for Hei-DataHub installation

set -e

echo "🔍 Verifying Hei-DataHub installation..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

# Check virtual environment
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${YELLOW}!${NC} Virtual environment not found (run ./scripts/setup_dev.sh)"
fi

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${YELLOW}!${NC} Virtual environment not activated"
    echo "   Run: source .venv/bin/activate"
fi

# Check package installation
if python3 -c "import mini_datahub" 2>/dev/null; then
    VERSION=$(python3 -c "from mini_datahub import __version__; print(__version__)")
    echo -e "${GREEN}✓${NC} mini_datahub package installed (version $VERSION)"
else
    echo -e "${RED}✗${NC} mini_datahub package not found"
    echo "   Run: pip install -e ."
    exit 1
fi

# Check required files
echo ""
echo "📁 Checking required files..."

FILES=(
    "pyproject.toml"
    "schema.json"
    "sql/schema.sql"
    "mini_datahub/__init__.py"
    "mini_datahub/models.py"
    "mini_datahub/storage.py"
    "mini_datahub/index.py"
    "mini_datahub/tui.py"
    "mini_datahub/cli.py"
    "mini_datahub/utils.py"
    "tests/test_basic.py"
    "data/example-weather/metadata.yaml"
)

ALL_FILES_EXIST=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo ""
    echo -e "${RED}Some required files are missing!${NC}"
    exit 1
fi

# Check command availability
echo ""
echo "🔧 Checking CLI command..."
if command -v mini-datahub &> /dev/null; then
    echo -e "${GREEN}✓${NC} mini-datahub command available"
    mini-datahub --version
else
    echo -e "${YELLOW}!${NC} mini-datahub command not found"
    echo "   Make sure virtual environment is activated and package is installed"
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
DEPS=("textual" "pydantic" "yaml" "jsonschema" "requests" "pyperclip")
for dep in "${DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $dep"
    else
        echo -e "${RED}✗${NC} $dep"
    fi
done

# Test basic imports
echo ""
echo "🧪 Testing basic imports..."
python3 -c "
from mini_datahub.models import DatasetMetadata
from mini_datahub.storage import slugify, validate_metadata
from mini_datahub.index import ensure_database
from mini_datahub.utils import DATA_DIR, DB_PATH
print('✓ All imports successful')
" && echo -e "${GREEN}✓${NC} Module imports working"

# Check database
echo ""
if [ -f "db.sqlite" ]; then
    SIZE=$(du -h db.sqlite | cut -f1)
    echo -e "${GREEN}✓${NC} Database exists (size: $SIZE)"
else
    echo -e "${YELLOW}!${NC} Database not yet created (will be created on first run)"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Installation verification complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Launch TUI:        mini-datahub"
echo "  2. Reindex datasets:  mini-datahub reindex"
echo "  3. Run tests:         pytest tests/ -v"
echo "  4. View help:         mini-datahub --help"
echo ""
echo "For more information, see:"
echo "  - README.md for full documentation"
echo "  - QUICKSTART.md for step-by-step guide"
echo ""
