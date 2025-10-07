#!/usr/bin/env bash
#
# fix_uv_commands.sh
# Updates all UV install commands to use correct simplified syntax
#

set -e

echo "🔧 Fixing UV commands in all documentation..."

# Function to replace in file
fix_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "⚠️  Skipping $file (not found)"
        return
    fi

    echo "  📝 Updating $file"

    # Fix: Remove #egg=hei-datahub and #egg=mini-datahub
    sed -i 's|#egg=hei-datahub||g' "$file"
    sed -i 's|#egg=mini-datahub||g' "$file"

    # Fix: Remove --from flag for git installs
    sed -i 's|uv tool install --from "git+|uv tool install "git+|g' "$file"
    sed -i 's|uv tool install --from "git+|uv tool install "git+|g' "$file"

    # Fix: Simplify install commands - remove package name at end
    sed -i 's| hei-datahub"| |g; s|" hei-datahub$|"|g' "$file"
    sed -i 's| mini-datahub"| |g; s|" mini-datahub$|"|g' "$file"

    echo "  ✓ Done"
}

# Update all documentation files
fix_file "README.md"
fix_file "docs/installation/README.md"
fix_file "docs/installation/uv-quickstart.md"
fix_file "docs/installation/private-repo-access.md"
fix_file "docs/installation/windows-notes.md"
fix_file "docs/installation/desktop-version.md"
fix_file "QUICK_REFERENCE_v0.58.md"
fix_file "FINAL_CHECKLIST_v0.58.md"
fix_file "IMPLEMENTATION_SUMMARY_v0.58.md"

echo ""
echo "✅ All documentation files updated!"
echo ""
echo "Key changes:"
echo "  - Removed #egg=hei-datahub and #egg=mini-datahub"
echo "  - Simplified to: uv tool install \"git+ssh://...\""
echo "  - UV will auto-detect package name from pyproject.toml"
echo ""
