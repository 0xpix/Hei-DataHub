#!/usr/bin/env bash
#
# Setup script for GitHub PR workflow (v3.0)
# This script helps you create and configure a catalog repository
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

prompt() {
    echo -e "${YELLOW}?${NC} $1"
}

# Banner
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Mini Hei-DataHub - GitHub PR Workflow Setup (v3.0)     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
info "Checking prerequisites..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    error "git is not installed. Please install git first."
    exit 1
fi
success "git found"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    warning "uv is not installed"
    echo ""
    prompt "Do you want to install uv now? (y/n)"
    read -r install_uv
    if [ "$install_uv" = "y" ]; then
        info "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Source the shell config to get uv in PATH
        export PATH="$HOME/.cargo/bin:$PATH"
        success "uv installed"
    else
        error "uv is required. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
else
    success "uv found"
fi

echo ""
info "Installing Mini Hei-DataHub dependencies..."
uv sync --python /usr/bin/python --dev
success "Dependencies installed"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Step 1: Catalog Repository Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

prompt "Have you created a catalog repository on GitHub? (y/n)"
read -r has_repo

if [ "$has_repo" != "y" ]; then
    echo ""
    info "Please create a GitHub repository for your catalog:"
    echo "  1. Go to https://github.com/new"
    echo "  2. Repository name: mini-datahub-catalog (or your choice)"
    echo "  3. Visibility: Private or Public"
    echo "  4. Do NOT initialize with README or .gitignore"
    echo "  5. Click 'Create repository'"
    echo ""
    prompt "Press Enter when done..."
    read -r
fi

echo ""
prompt "Enter the repository URL (e.g., https://github.com/your-org/mini-datahub-catalog.git):"
read -r repo_url

# Extract owner and repo name
if [[ $repo_url =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
    owner="${BASH_REMATCH[1]}"
    repo="${BASH_REMATCH[2]}"
    success "Detected: $owner/$repo"
else
    error "Invalid GitHub URL format"
    exit 1
fi

echo ""
prompt "Where should we clone the catalog repository? (default: ./catalog)"
read -r catalog_path
catalog_path=${catalog_path:-./catalog}

# Expand ~ to home directory
catalog_path="${catalog_path/#\~/$HOME}"

# Convert to absolute path
catalog_path=$(cd "$(dirname "$catalog_path")" 2>/dev/null && pwd)/$(basename "$catalog_path")

info "Cloning catalog repository to $catalog_path..."
if [ -d "$catalog_path" ]; then
    warning "Directory already exists. Skipping clone."
else
    git clone "$repo_url" "$catalog_path"
    success "Repository cloned"
fi

cd "$catalog_path"

# Copy .gitignore if not exists
if [ ! -f .gitignore ]; then
    info "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Database files - never commit these
db.sqlite
db.sqlite-*

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
.venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Ignore all data directory contents EXCEPT metadata and specific files
data/**

# But explicitly include metadata.yaml files
!data/**/metadata.yaml

# Include optional README files for datasets
!data/**/README.md

# Include optional images directories for datasets
!data/**/images/
!data/**/images/**

# Application config (contains sensitive info)
.datahub_config.json

# Outbox (contains failed PR tasks)
.outbox/
EOF
    success ".gitignore created"
fi

# Copy schema.json if not exists
if [ ! -f schema.json ]; then
    info "Copying schema.json..."
    # Go back to app directory
    cd - > /dev/null
    cp schema.json "$catalog_path/"
    cd "$catalog_path"
    success "schema.json copied"
fi

# Create data directory
mkdir -p data

# Initial commit if needed
if [ -z "$(git status --porcelain)" ]; then
    info "Repository already initialized"
else
    info "Creating initial commit..."
    git add .gitignore schema.json
    git commit -m "Initial catalog structure"
    git push -u origin main || git push -u origin master
    success "Initial commit pushed"
fi

cd - > /dev/null

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Step 2: GitHub Personal Access Token"
echo "════════════════════════════════════════════════════════════"
echo ""

info "You need a GitHub Personal Access Token (PAT) with these permissions:"
echo "  • Contents: Read and write"
echo "  • Pull requests: Read and write"
echo ""
echo "To create one:"
echo "  1. Go to https://github.com/settings/tokens?type=beta"
echo "  2. Click 'Generate new token'"
echo "  3. Token name: Mini DataHub Catalog Access"
echo "  4. Expiration: 90 days (recommended)"
echo "  5. Repository access: Only select repositories → Choose $owner/$repo"
echo "  6. Permissions → Repository permissions:"
echo "     - Contents: Read and write"
echo "     - Pull requests: Read and write"
echo "  7. Click 'Generate token'"
echo "  8. Copy the token (starts with github_pat_ or ghp_)"
echo ""
prompt "Press Enter when you have your token ready..."
read -r

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Step 3: Configure Mini Hei-DataHub"
echo "════════════════════════════════════════════════════════════"
echo ""

info "Configuration will be saved to .datahub_config.json"
info "Your token will be stored securely in your OS keychain"
echo ""

# Get configuration values
prompt "GitHub username:"
read -r github_username

prompt "Default branch (default: main):"
read -r default_branch
default_branch=${default_branch:-main}

prompt "Auto-assign reviewers (comma-separated, optional):"
read -r reviewers

prompt "PR labels (default: dataset:add, needs-review):"
read -r labels
labels=${labels:-dataset:add, needs-review}

echo ""
info "Configuration summary:"
echo "  GitHub Host: github.com"
echo "  Owner: $owner"
echo "  Repository: $repo"
echo "  Branch: $default_branch"
echo "  Username: $github_username"
echo "  Catalog Path: $catalog_path"
echo "  Reviewers: ${reviewers:-none}"
echo "  Labels: $labels"
echo ""

prompt "Save this configuration? (y/n)"
read -r save_config

if [ "$save_config" != "y" ]; then
    warning "Configuration not saved. You can configure later in the TUI (press 'S')."
    exit 0
fi

# Create config file
info "Saving configuration..."
cat > .datahub_config.json << EOF
{
  "host": "github.com",
  "owner": "$owner",
  "repo": "$repo",
  "default_branch": "$default_branch",
  "username": "$github_username",
  "catalog_repo_path": "$catalog_path",
  "auto_assign_reviewers": [$(echo "$reviewers" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/')]
  "pr_labels": [$(echo "$labels" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/')]
}
EOF
success "Configuration saved to .datahub_config.json"

echo ""
warning "IMPORTANT: You still need to add your GitHub token in the TUI!"
info "Your token will be stored securely in your OS keychain."
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  Setup Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
success "Mini Hei-DataHub is ready to use!"
echo ""
info "Next steps:"
echo "  1. Activate virtualenv: source .venv/bin/activate"
echo "  2. Launch the app: mini-datahub"
echo "  3. Press 'S' to open Settings"
echo "  4. Paste your GitHub token"
echo "  5. Click 'Test Connection'"
echo "  6. Click 'Save Settings'"
echo "  7. Press 'A' to add your first dataset!"
echo ""
info "Documentation:"
echo "  • Full guide: GITHUB_WORKFLOW.md"
echo "  • Quick ref: PR_WORKFLOW_QUICKREF.md"
echo "  • Migration: MIGRATION_v3.md"
echo ""
prompt "Launch Mini Hei-DataHub now? (y/n)"
read -r launch_now

if [ "$launch_now" = "y" ]; then
    source .venv/bin/activate
    mini-datahub
fi

echo ""
success "Setup complete! Happy cataloging! 🎉"
