#!/usr/bin/env bash
#
# validate_v0.58_implementation.sh
# Validates all changes for Hei-DataHub v0.58.0-beta
#
# Usage:
#   bash scripts/validate_v0.58_implementation.sh

set -e

echo "======================================================================"
echo "Hei-DataHub v0.58.0-beta Implementation Validation"
echo "======================================================================"
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
        return 1
    fi
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Command available: $1"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Command not found: $1 (optional)"
        ((WARNINGS++))
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✓${NC} Executable: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Not executable: $1"
        ((ERRORS++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Core Package Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "src/mini_datahub/__main__.py"
check_file "src/hei_datahub/__init__.py"
check_file "src/hei_datahub/__main__.py"
check_file "MANIFEST.in"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Configuration Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "pyproject.toml"
check_file "version.yaml"
check_file "CHANGELOG.md"

# Check version in pyproject.toml
if grep -q 'version = "0.58.0-beta"' pyproject.toml; then
    echo -e "${GREEN}✓${NC} Version 0.58.0-beta in pyproject.toml"
else
    echo -e "${RED}✗${NC} Version not updated in pyproject.toml"
    ((ERRORS++))
fi

# Check package name
if grep -q 'name = "hei-datahub"' pyproject.toml; then
    echo -e "${GREEN}✓${NC} Package name 'hei-datahub' in pyproject.toml"
else
    echo -e "${RED}✗${NC} Package name not updated in pyproject.toml"
    ((ERRORS++))
fi

# Check Python version requirement
if grep -q 'requires-python = ">=3.10"' pyproject.toml; then
    echo -e "${GREEN}✓${NC} Python 3.10+ requirement set"
else
    echo -e "${YELLOW}⚠${NC} Python requirement may not be updated"
    ((WARNINGS++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Scripts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "scripts/create_desktop_entry.sh"
check_executable "scripts/create_desktop_entry.sh"
check_file "scripts/build_desktop_binary.sh"
check_executable "scripts/build_desktop_binary.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "docs/installation/README.md"
check_file "docs/installation/uv-quickstart.md"
check_file "docs/installation/private-repo-access.md"
check_file "docs/installation/windows-notes.md"
check_file "docs/installation/desktop-version.md"
check_file "docs/installation/troubleshooting.md"

# Check README for UV section
if grep -q "UV Method" README.md; then
    echo -e "${GREEN}✓${NC} README contains UV installation section"
else
    echo -e "${YELLOW}⚠${NC} UV section may be missing in README"
    ((WARNINGS++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. CI/CD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file ".github/workflows/build-binary.yml"
check_file ".github/PULL_REQUEST_TEMPLATE_v0.58.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Reference Documents"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "IMPLEMENTATION_SUMMARY_v0.58.md"
check_file "QUICK_REFERENCE_v0.58.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. Package Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if package can be imported
if python -c "import mini_datahub" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} mini_datahub package importable"
else
    echo -e "${YELLOW}⚠${NC} mini_datahub not importable (may need installation)"
    ((WARNINGS++))
fi

# Check version module
if python -c "from mini_datahub.version import __version__; print(f'Version: {__version__}')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Version module works"
    python -c "from mini_datahub.version import __version__; print(f'  Current version: {__version__}')"
else
    echo -e "${YELLOW}⚠${NC} Version module has issues"
    ((WARNINGS++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. Git Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "chore/uv-install-data-desktop-v0.58.x" ]; then
    echo -e "${GREEN}✓${NC} On correct branch: $BRANCH"
else
    echo -e "${YELLOW}⚠${NC} On branch: $BRANCH (expected: chore/uv-install-data-desktop-v0.58.x)"
    ((WARNINGS++))
fi

# Check for uncommitted changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✓${NC} No uncommitted changes"
else
    echo -e "${YELLOW}⚠${NC} Uncommitted changes present"
    ((WARNINGS++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. External Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_command "uv"
check_command "git"
check_command "python"
check_command "ssh"
check_command "pyinstaller"
check_command "update-desktop-database"

echo ""
echo "======================================================================"
echo "Validation Summary"
echo "======================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Commit changes: git add -A && git commit -m 'feat(install): ...'"
    echo "  2. Push branch: git push -u origin chore/uv-install-data-desktop-v0.58.x"
    echo "  3. Create pull request on GitHub"
    echo "  4. Review using .github/PULL_REQUEST_TEMPLATE_v0.58.md"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validation passed with $WARNINGS warning(s)${NC}"
    echo ""
    echo "Warnings are typically for optional features or uncommitted changes."
    echo "Review warnings above and proceed if acceptable."
    exit 0
else
    echo -e "${RED}❌ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before proceeding."
    exit 1
fi
