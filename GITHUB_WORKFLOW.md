# GitHub PR Workflow Guide

## Overview

Mini Hei-DataHub now features **automated Pull Request creation** when saving datasets. When properly configured, the app will:

1. Save `data/<id>/metadata.yaml` to your local **catalog repository**
2. Create a git branch, commit the changes
3. Push to GitHub (central repo or your fork)
4. Open a Pull Request automatically
5. Show you a success notification with the PR URL

**You never need to run git commands or see tokens.** Everything happens silently in the background.

## Catalog Repository Model

The workflow assumes a **separate GitHub repository** that serves as your dataset catalog:

```
mini-datahub-catalog/          # Separate repo from the app
├── .gitignore                 # See catalog-gitignore-example
├── schema.json                # Validation schema
├── README.md                  # Catalog documentation
└── data/
    ├── dataset-1/
    │   ├── metadata.yaml      # ✅ Tracked
    │   ├── README.md          # ✅ Tracked (optional)
    │   └── images/            # ✅ Tracked (optional)
    └── dataset-2/
        └── metadata.yaml
```

**Important:**
- `db.sqlite` is **never committed** (in .gitignore)
- Only `metadata.yaml` (and optional README/images) are tracked
- Each contributor clones this repo locally
- The TUI writes directly into this local clone

## Setup Guide

### Step 1: Create Catalog Repository

```bash
# On GitHub, create a new repository:
# Example: your-org/mini-datahub-catalog

# Clone it locally
git clone https://github.com/your-org/mini-datahub-catalog.git
cd mini-datahub-catalog

# Copy the example .gitignore
cp /path/to/Hei-DataHub/catalog-gitignore-example .gitignore

# Copy the schema
cp /path/to/Hei-DataHub/schema.json .

# Create data directory
mkdir data

# Commit initial structure
git add .gitignore schema.json data/.gitkeep
git commit -m "Initial catalog structure"
git push
```

### Step 2: Create GitHub Personal Access Token (PAT)

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
   - Direct link: https://github.com/settings/tokens?type=beta

2. Click **"Generate new token"**

3. **Configure token basics:**
   - **Token name**: "Mini DataHub - Catalog Access"
   - **Expiration**: Your choice (90 days recommended)
   - **Description**: Optional
   - **Resource owner**: Your username or organization

4. **Repository access** (important!):
   - Select: **"Only select repositories"**
   - Click the dropdown and choose: `your-org/mini-datahub-catalog`

5. **Permissions** (scroll down to find this section!):
   - Expand **"Repository permissions"** section
   - Find **"Contents"**: Change dropdown to **"Read and write"**
   - Find **"Pull requests"**: Change dropdown to **"Read and write"**
   - Leave all other permissions at default ("No access")

6. Scroll to bottom and click **"Generate token"**

7. **Copy the token** immediately (starts with `github_pat_` or `ghp_`)
   - You won't be able to see it again!
   - Store it temporarily until you paste it into Mini DataHub Settings

**Having trouble finding the permissions?** See the detailed visual guide: [GITHUB_TOKEN_GUIDE.md](GITHUB_TOKEN_GUIDE.md)

**Security:** The token is stored in your OS keychain (via `keyring` library), never in plain text files.

### Step 3: Configure Mini DataHub

Launch the app and press `S` for Settings:

```bash
mini-datahub
# Press 'S' to open Settings
```

Fill in the form:

- **GitHub Host**: `github.com` (or your GitHub Enterprise host)
- **Owner/Organization**: `your-org`
- **Repository Name**: `mini-datahub-catalog`
- **Default Branch**: `main` (or your primary branch)
- **GitHub Username**: `your-username`
- **Personal Access Token**: Paste your PAT
- **Catalog Repository Path**: `/home/you/mini-datahub-catalog` (absolute path to local clone)
- **Auto-assign Reviewers**: `maintainer1, maintainer2` (optional)
- **PR Labels**: `dataset:add, needs-review` (optional)

Click **Test Connection** to verify. Then **Save Settings**.

### Step 4: Test the Workflow

1. Press `A` to add a new dataset
2. Fill in the required fields
3. Press `Ctrl+S` to save

**What happens:**
- ✅ Metadata validated
- ✅ ID uniqueness checked (remote)
- ✅ Branch created: `add/<dataset-id>-<timestamp>`
- ✅ File written: `data/<id>/metadata.yaml`
- ✅ Changes committed: `feat(dataset): add <id> — <name>`
- ✅ Branch pushed to GitHub
- ✅ PR opened with formatted description
- ✅ Labels and reviewers added
- 🎉 Success toast with PR URL!

## PR Workflow Details

### Central vs Fork Strategy

The workflow automatically detects your permissions:

**If you have PUSH access** (team member):
- Branch created in **central repo**: `your-org/mini-datahub-catalog`
- PR: `your-org:add/dataset-...` → `your-org:main`

**If you DON'T have push access** (external contributor):
- Fork created automatically: `your-username/mini-datahub-catalog`
- Branch pushed to **your fork**
- PR: `your-username:add/dataset-...` → `your-org:main`
- Fork creation may take a few seconds

### Branch Naming Convention

```
add/<dataset-id>-<yyyyMMdd-HHmm>
```

Examples:
- `add/weather-stations-20241003-1430`
- `add/financial-data-20241003-0915`

### Commit Message Format

```
feat(dataset): add <dataset-id> — <Dataset Name>
```

Examples:
- `feat(dataset): add weather-stations — Global Weather Stations 2024`
- `feat(dataset): add financial-data — NYSE Trading Data 2023`

### PR Title Format

```
Add dataset: <Dataset Name> (<dataset-id>)
```

### PR Body Template

The PR automatically includes:

```markdown
## Dataset: Global Weather Stations

**ID:** `weather-stations`

### Description
Hourly weather observations from 10,000+ stations worldwide

### Summary

| Field | Value |
|-------|-------|
| **Source** | https://example.com/data.csv |
| **File Format** | CSV |
| **Size** | 2.5 GB |
| **Data Types** | weather, time-series |
| **Used In Projects** | climate-analysis |

### Checklist

- [x] Metadata validated against schema
- [x] Dataset ID is unique
- [x] All required fields provided
- [ ] Reviewer: Metadata accuracy verified
- [ ] Reviewer: Source URL accessible
- [ ] Reviewer: Ready to merge

### Files Changed

- `data/weather-stations/metadata.yaml`

---
*This PR was automatically generated by Mini Hei-DataHub TUI.*
```

## Offline & Error Handling

### What if I'm offline?

The dataset is **saved locally**, and the PR creation is **queued** in the Outbox:

1. You see: "Saved locally. Couldn't publish PR. Retry from Outbox when online."
2. Press `P` to open the Outbox
3. When back online, select the task and press `R` to retry

### Outbox Management

Press `P` from the home screen to open the Outbox:

**Keybindings:**
- `R` - Retry selected task
- `Enter` - Retry selected task
- `q` / `Esc` - Back to home

**Buttons:**
- **Retry Selected** - Retry the currently selected task
- **Retry All Pending** - Retry all pending tasks in batch
- **Clear Completed** - Remove successful tasks from outbox
- **Back** - Return to home screen

### Common Errors

**"Catalog repository path does not exist"**
- Solution: Ensure you've cloned the catalog repo and set the correct path in Settings

**"Not a git repository"**
- Solution: The catalog path must point to a git repository. Run `git init` or clone the repo.

**"Dataset ID already exists in repository"**
- Solution: Choose a different ID. The app checks the remote repository for collisions.

**"Failed to create fork"**
- Solution: Check your token permissions. You need `Contents: Read and write` and `Pull requests: Read and write`.

**"Authentication failed: 401"**
- Solution: Your token may be expired or revoked. Create a new one and update Settings.

**"Rate limit exceeded"**
- Solution: GitHub API has rate limits. Wait a few minutes and retry from Outbox.

## Validation Gates

Before any commit/push, the workflow validates:

1. **Schema validation**: `metadata.yaml` against `schema.json`
2. **ID format**: Must match `^[a-z0-9][a-z0-9_-]*$`
3. **ID uniqueness**: Checked against remote repository
4. **Required fields**: All required fields must be present
5. **Array normalization**: Lists stored as arrays, not comma strings

**If validation fails:** The form stays open with inline error messages. No branch or commit is created.

## Catalog Repository CI

You can add CI checks to your catalog repo to enforce quality:

```yaml
# .github/workflows/validate-datasets.yml
name: Validate Datasets

on:
  pull_request:
    paths:
      - 'data/**/metadata.yaml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install jsonschema pyyaml

      - name: Validate changed metadata files
        run: |
          python scripts/validate_all.py

      - name: Check ID uniqueness
        run: |
          python scripts/check_unique_ids.py
```

This blocks PRs if:
- Metadata doesn't match schema
- IDs are duplicated
- Required fields are missing

## Team Workflow

### For Contributors

1. Clone catalog repository
2. Configure Mini DataHub settings (one-time)
3. Add datasets through the TUI
4. PRs created automatically
5. Wait for maintainer review

### For Maintainers

1. Review PRs on GitHub
2. Check:
   - Metadata accuracy
   - Source URL accessibility
   - Dataset actually exists at storage location
   - Proper categorization
3. Request changes or approve + merge
4. Merged datasets immediately available to all team members (after they pull)

### Syncing Your Local Catalog

The TUI automatically:
- Fetches from origin before creating branches
- Fast-forwards your default branch
- Creates branches from latest upstream

To manually sync:

```bash
cd ~/mini-datahub-catalog
git checkout main
git pull origin main
```

Then run:
```bash
mini-datahub reindex
```

To rebuild your local search index from the updated YAML files.

## Security Best Practices

1. **Never commit tokens**: The `.datahub_config.json` is in `.gitignore`
2. **Use fine-grained PATs**: Limit permissions to one repository
3. **Set token expiration**: Rotate tokens every 90 days
4. **Store in keychain**: The `keyring` library uses OS-native secure storage:
   - macOS: Keychain
   - Linux: Secret Service (gnome-keyring, KWallet)
   - Windows: Credential Manager
5. **Revoke compromised tokens**: GitHub Settings → Tokens → Revoke

## Configuration Files

### `.datahub_config.json`

Located in the app repository root (not the catalog repo). Contains:

```json
{
  "host": "github.com",
  "owner": "your-org",
  "repo": "mini-datahub-catalog",
  "default_branch": "main",
  "username": "your-username",
  "auto_assign_reviewers": ["maintainer1"],
  "pr_labels": ["dataset:add", "needs-review"],
  "catalog_repo_path": "/home/you/mini-datahub-catalog"
}
```

**Never commit this file.** It's in `.gitignore`.

### Token Storage

Stored in OS keychain via `keyring`:
- Service: `mini-datahub`
- Username: `github-token`

Access: `keyring.get_password("mini-datahub", "github-token")`

## Troubleshooting Advanced Issues

### Reset Configuration

```bash
# Remove config file
rm .datahub_config.json

# Clear token from keychain (Python)
python -c "import keyring; keyring.delete_password('mini-datahub', 'github-token')"

# Restart and reconfigure
mini-datahub
# Press S to open Settings
```

### Inspect Outbox Tasks

Outbox files are stored in `.outbox/<task-id>.json`:

```bash
ls -la .outbox/
cat .outbox/weather-stations-1696348800.json
```

Each task contains:
- Dataset ID
- Full metadata
- Branch name
- Commit message
- Error message (if failed)
- Retry count

### Manual PR Creation

If the workflow fails repeatedly, you can manually create the PR:

```bash
cd ~/mini-datahub-catalog

# Create branch
git checkout main
git pull
git checkout -b add/dataset-id-$(date +%Y%m%d-%H%M)

# Edit file
vim data/dataset-id/metadata.yaml

# Commit
git add data/dataset-id/metadata.yaml
git commit -m "feat(dataset): add dataset-id — Dataset Name"

# Push
git push origin HEAD

# Then open PR on GitHub web UI
```

## Roadmap

- [x] Automated PR creation
- [x] Fork workflow support
- [x] Offline queue (Outbox)
- [x] Secure token storage
- [ ] Bulk import from CSV
- [ ] PR templates customization
- [ ] GitHub App authentication (instead of PAT)
- [ ] PR auto-merge for trusted contributors
- [ ] Dataset update workflow (edit existing)
- [ ] Conflict resolution UI

---

**Questions?** Open an issue at github.com/0xpix/Hei-DataHub
