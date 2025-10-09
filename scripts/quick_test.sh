#!/bin/bash
# Quick test script for cross-platform data fix
# Run this after installing to verify everything works

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Hei-DataHub v0.58.1 Cross-Platform Data Fix Test         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

info() {
    echo -e "ℹ $1"
}

# Check if hei-datahub is installed
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Checking Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v hei-datahub &> /dev/null; then
    success "hei-datahub command found"
    VERSION=$(hei-datahub --version 2>&1 | head -n 1)
    info "Version: $VERSION"
else
    error "hei-datahub command not found"
    echo ""
    echo "Please install first:"
    echo "  uv tool install \"git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x\""
    exit 1
fi

echo ""

# Run doctor
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Running System Diagnostics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if hei-datahub doctor; then
    success "System diagnostics passed"
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        error "Directory issue detected (exit code 1)"
    elif [ $EXIT_CODE -eq 2 ]; then
        error "Permission error detected (exit code 2)"
    elif [ $EXIT_CODE -eq 3 ]; then
        error "Data issues detected (exit code 3)"
    else
        error "Unknown error (exit code $EXIT_CODE)"
    fi
    echo ""
    warning "Run 'hei-datahub doctor' manually for detailed diagnostics"
    exit $EXIT_CODE
fi

echo ""

# Check paths
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Checking Data Directory"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Detect OS and set data directory
case "$(uname -s)" in
    Darwin*)
        DATA_DIR="$HOME/Library/Application Support/Hei-DataHub"
        OS_NAME="macOS"
        ;;
    Linux*)
        DATA_DIR="$HOME/.local/share/Hei-DataHub"
        OS_NAME="Linux"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        DATA_DIR="$LOCALAPPDATA/Hei-DataHub"
        OS_NAME="Windows"
        ;;
    *)
        DATA_DIR="$HOME/.local/share/Hei-DataHub"
        OS_NAME="Unknown"
        ;;
esac

info "OS: $OS_NAME"
info "Expected data directory: $DATA_DIR"

if [ -d "$DATA_DIR" ]; then
    success "Data directory exists"

    # Count datasets
    DATASETS_DIR="$DATA_DIR/datasets"
    if [ -d "$DATASETS_DIR" ]; then
        DATASET_COUNT=$(find "$DATASETS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
        if [ "$DATASET_COUNT" -ge 4 ]; then
            success "Found $DATASET_COUNT datasets"

            # List datasets
            echo ""
            info "Datasets:"
            for dataset in "$DATASETS_DIR"/*; do
                if [ -d "$dataset" ]; then
                    DATASET_NAME=$(basename "$dataset")
                    if [ -f "$dataset/metadata.yaml" ]; then
                        echo "  ✓ $DATASET_NAME"
                    else
                        echo "  ⚠ $DATASET_NAME (missing metadata.yaml)"
                    fi
                fi
            done
        else
            warning "Only found $DATASET_COUNT datasets (expected 4+)"
        fi
    else
        error "Datasets directory not found: $DATASETS_DIR"
    fi

    # Check database
    if [ -f "$DATA_DIR/db.sqlite" ]; then
        DB_SIZE=$(du -h "$DATA_DIR/db.sqlite" | cut -f1)
        success "Database exists ($DB_SIZE)"
    else
        warning "Database not found (will be created on first run)"
    fi

    # Check schema
    if [ -f "$DATA_DIR/schema.json" ]; then
        success "Schema file exists"
    else
        warning "Schema file not found (will be created on first run)"
    fi
else
    error "Data directory not found: $DATA_DIR"
    echo ""
    info "The directory should be created on first run."
    info "Try running: hei-datahub"
fi

echo ""

# Run verification script if available
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Running Verification Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -c "import mini_datahub" 2>/dev/null; then
    SCRIPT_PATH="scripts/verify_cross_platform_data_fix.py"

    # Try to find the script
    if [ -f "$SCRIPT_PATH" ]; then
        python3 "$SCRIPT_PATH"
    else
        # Try to run from installed package
        if python3 -c "from pathlib import Path; import mini_datahub; script = Path(mini_datahub.__file__).parent.parent.parent / 'scripts' / 'verify_cross_platform_data_fix.py'; exit(0 if script.exists() else 1)" 2>/dev/null; then
            python3 -c "from pathlib import Path; import mini_datahub; import subprocess; script = Path(mini_datahub.__file__).parent.parent.parent / 'scripts' / 'verify_cross_platform_data_fix.py'; subprocess.run(['python3', str(script)])"
        else
            warning "Verification script not found (this is OK if you're not in the repo)"
            info "You can run it manually if you cloned the repo:"
            info "  python3 scripts/verify_cross_platform_data_fix.py"
        fi
    fi
else
    error "mini_datahub module not found"
    echo ""
    info "Ensure Hei-DataHub is properly installed"
fi

echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                         Test Summary                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ -d "$DATA_DIR" ] && [ -d "$DATASETS_DIR" ] && [ "$DATASET_COUNT" -ge 4 ]; then
    success "All checks passed! ✨"
    echo ""
    info "Your installation appears to be working correctly."
    info "You can now run: hei-datahub"
    exit 0
else
    warning "Some checks failed or incomplete"
    echo ""
    info "Try these troubleshooting steps:"
    echo "  1. Run: hei-datahub doctor"
    echo "  2. Check the data directory exists at: $DATA_DIR"
    echo "  3. Try reindexing: hei-datahub reindex"
    echo "  4. For more help: https://github.com/0xpix/Hei-DataHub/blob/main/docs/installation/troubleshooting.md"
    exit 1
fi
