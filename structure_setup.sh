#!/usr/bin/env bash
# structure_setup.sh — scaffolds Mini Hei-DataHub (TUI MVP)
# Usage: bash structure_setup.sh
set -euo pipefail

ROOT_DIR="${PWD}"
APP_NAME="mini_datahub"

echo "Scaffolding Mini Hei-DataHub in: ${ROOT_DIR}"

# --- Directories ---
mkdir -p \
  src/${APP_NAME}/core \
  src/${APP_NAME}/tui \
  src/${APP_NAME}/utils \
  etc/sql \
  data/.keep \
  scripts \
  tests \
  .github/workflows

# --- .gitignore ---
cat > .gitignore <<'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.dist/
build/
dist/
.venv/
.env

# SQLite
db.sqlite
db.sqlite-*

# App data
data/*/
!data/.keep
~/.mini-datahub/

# OS
.DS_Store
Thumbs.db
EOF
