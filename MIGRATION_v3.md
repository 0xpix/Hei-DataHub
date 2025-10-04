# Migration Guide: v2.0 → v3.0

## Overview

Version 3.0 adds **automated PR workflow** for GitHub integration. This guide helps existing users migrate to the new version.

## What's New in v3.0?

- ✨ Automated Pull Request creation when saving datasets
- ⚙️ Settings screen for GitHub configuration
- 📮 Outbox queue for offline PR retry
- 🔐 Secure token storage via OS keychain
- 🔀 Smart fork vs central repo detection

## Breaking Changes

**None!** v3.0 is fully backward compatible.

- Without GitHub configuration, the app works exactly as before
- All existing datasets and search indices continue to work
- No data migration needed

## Installation

### Using uv (Recommended)

```bash
cd Hei-DataHub

# Update dependencies
uv sync --python /usr/bin/python --dev

# Activate virtualenv
source .venv/bin/activate

# Launch app
mini-datahub
```

### Using pip (Alternative)

```bash
cd Hei-DataHub

# Update dependencies
pip install -e ".[dev]"

# Launch app
mini-datahub
```

## New Dependencies

The following dependency was added in v3.0:

- `keyring>=24.0.0` - For secure token storage

All other dependencies remain the same.

## Optional: Enable GitHub PR Workflow

If you want to use the new automated PR feature:

### Step 1: Create Catalog Repository

Create a **separate** GitHub repository for your dataset catalog:

```bash
# On GitHub (web UI):
# Click "New repository"
# Name: mini-datahub-catalog (or your choice)
# Visibility: Private or Public
# Initialize: Empty (no README, .gitignore)

# Clone it locally
git clone https://github.com/your-org/mini-datahub-catalog.git
cd mini-datahub-catalog

# Copy .gitignore template
cp /path/to/Hei-DataHub/catalog-gitignore-example .gitignore

# Copy schema
cp /path/to/Hei-DataHub/schema.json .

# Create data directory
mkdir -p data

# Initial commit
git add .gitignore schema.json
git commit -m "Initial catalog structure"
git push
```

### Step 2: Generate GitHub Token

1. Go to **GitHub Settings** → **Developer Settings** → **Personal Access Tokens** → **Fine-grained tokens**
   - Direct link: https://github.com/settings/tokens?type=beta
2. Click **"Generate new token"**
3. Configure token:
   - **Name**: "Mini DataHub Catalog Access"
   - **Expiration**: 90 days (recommended)
   - **Repository access**: Only select repositories → Choose your catalog repo
4. **Scroll down** to **"Repository permissions"** section:
   - **Contents**: Select "Read and write" from dropdown
   - **Pull requests**: Select "Read and write" from dropdown
5. Scroll to bottom, click **"Generate token"**
6. **Copy the token immediately** (starts with `github_pat_` or `ghp_`)

### Step 3: Configure Mini DataHub

```bash
# Launch app
mini-datahub

# Press 'S' to open Settings

# Fill in the form:
# - GitHub Host: github.com
# - Owner: your-org
# - Repository: mini-datahub-catalog
# - Default Branch: main
# - Username: your-username
# - Token: (paste your PAT)
# - Catalog Repo Path: /home/you/mini-datahub-catalog (absolute path)
# - Reviewers: (optional, comma-separated)
# - Labels: (optional, comma-separated)

# Click "Test Connection" to verify
# Click "Save Settings"
```

### Step 4: Test It!

```bash
# Press 'A' to add a dataset
# Fill in the required fields
# Press Ctrl+S to save

# Expected result:
# ✓ Dataset validated
# ✓ Saved to catalog repo
# ✓ Branch created
# ✓ Committed and pushed
# ✓ PR opened on GitHub
# 🎉 Success toast with PR URL
```

## Configuration Files

After enabling GitHub integration, you'll have new files (git-ignored):

```
Hei-DataHub/
├── .datahub_config.json    # Your GitHub settings
└── .outbox/                 # Failed PR tasks queue
    └── *.json               # Individual task files
```

**Important:** These files contain sensitive data (tokens) and are automatically git-ignored. Never commit them.

## Token Storage

Your GitHub token is stored in your OS keychain:

- **macOS**: Keychain Access
- **Linux**: Secret Service (gnome-keyring, KWallet)
- **Windows**: Credential Manager

You can verify:

```bash
# macOS
security find-generic-password -s "mini-datahub"

# Linux (with python-keyring installed)
python -c "import keyring; print(keyring.get_password('mini-datahub', 'github-token'))"
```

## Migrating Existing Datasets

Your existing datasets in `data/` will continue to work without changes.

To add them to the catalog repository:

```bash
# Copy datasets to catalog repo
cp -r /path/to/Hei-DataHub/data/* /path/to/catalog/data/

# In catalog repo
cd /path/to/catalog
git add data/
git commit -m "feat(catalog): import existing datasets"
git push

# Reindex in Mini DataHub
mini-datahub reindex
```

Alternatively, you can re-add them through the TUI to create PRs for each.

## Team Migration

### For Administrators

1. Create catalog repository
2. Set up CI/CD for validation (see `GITHUB_WORKFLOW.md`)
3. Import existing datasets
4. Share clone instructions with team
5. Create shared documentation for contributors

### For Contributors

1. Clone catalog repository
2. Update Mini DataHub to v3.0
3. Configure GitHub settings (personal token)
4. Start adding datasets!

## Rollback

If you need to roll back to v2.0:

```bash
# Check out previous version
git checkout v2.0.0

# Reinstall dependencies
uv sync --python /usr/bin/python --dev

# Launch app (works normally without GitHub features)
mini-datahub
```

Your data is safe - only YAML files matter, and they're unchanged.

## Troubleshooting

### "keyring" module not found

```bash
# Install keyring manually
uv add keyring
# or
pip install keyring
```

### Token storage fails

On Linux, ensure you have a keyring backend:

```bash
# Debian/Ubuntu
sudo apt install gnome-keyring

# Fedora
sudo dnf install gnome-keyring
```

### Settings not saved

Check file permissions:

```bash
ls -la .datahub_config.json
# Should be readable/writable by your user
chmod 600 .datahub_config.json
```

### Outbox tasks not retrying

```bash
# Check outbox directory
ls -la .outbox/

# View task details
cat .outbox/*.json

# Manually retry in app: Press 'P', select task, press 'R'
```

## Support

- **Documentation**: [GITHUB_WORKFLOW.md](GITHUB_WORKFLOW.md)
- **Quick Reference**: [PR_WORKFLOW_QUICKREF.md](PR_WORKFLOW_QUICKREF.md)
- **Issues**: https://github.com/0xpix/Hei-DataHub/issues

---

**Migration complete! Enjoy automated PR workflows. 🚀**
