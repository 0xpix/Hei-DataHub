#!/bin/bash
# Quick test script for Hei-DataHub
# Run this after installing to verify everything works

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║               Hei-DataHub Quick Test                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "✓ $1"
}

error() {
    echo -e "✗ $1"
}

warning() {
    echo -e "⚠ $1"
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
    error "System diagnostics failed"
    exit 1
fi

echo ""
success "All checks passed! ✨"
