# GitHub PR Workflow - Quick Reference Card

## One-Time Setup (5 minutes)

```bash
# 1. Create catalog repo on GitHub (web UI)
#    Example: your-org/mini-datahub-catalog

# 2. Clone it locally
git clone https://github.com/your-org/mini-datahub-catalog.git
cd mini-datahub-catalog

# 3. Copy .gitignore template
cp /path/to/Hei-DataHub/catalog-gitignore-example .gitignore

# 4. Create data directory
mkdir -p data

# 5. Initial commit
git add .gitignore
git commit -m "Initial catalog structure"
git push

# 6. Generate GitHub PAT (on GitHub web UI)
#    Go to: https://github.com/settings/tokens?type=beta
#    Click "Generate new token"
#    Token name: Mini DataHub Catalog
#    Expiration: 90 days
#    Repository access: Only select repositories → your catalog repo
#    SCROLL DOWN to "Repository permissions" section:
#      - Contents: Read and write
#      - Pull requests: Read and write
#    Generate token → Copy it (starts with github_pat_)

#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

# 7. Configure Mini DataHub
mini-datahub
# Press 'S' for Settings
# Fill in:
#   - Owner: your-org
#   - Repo: mini-datahub-catalog
#   - Username: your-username
#   - Token: (paste PAT)
#   - Catalog Path: /path/to/mini-datahub-catalog
# Test connection → Save
```

## Daily Usage

```bash
# Launch app
mini-datahub

# Add dataset (press 'A')
# Fill form
# Press Ctrl+S to save

# ✨ PR created automatically!
```

## Keybindings Reference

| Key | Screen | Action |
|-----|--------|--------|
| `S` | Home | Open Settings |
| `P` | Home | Open Outbox |
| `A` | Home | Add Dataset |
| `Ctrl+S` | Add Form | Save Dataset (→ PR) |
| `R` | Outbox | Retry Selected Task |
| `q` / `Esc` | Any | Back / Cancel |

## Troubleshooting

### PR Creation Failed

1. Press `P` to open Outbox
2. Select failed task (arrow keys or `j`/`k`)
3. Press `R` to retry
4. Check status message for errors

### "Authentication failed"

- Token expired → Generate new PAT
- Press `S` → Update token → Save

### "Catalog path does not exist"

- Ensure catalog repo is cloned
- Update path in Settings (`S`)
- Use absolute path: `/home/you/catalog`

### "Not a git repository"

```bash
cd /path/to/catalog
git init
git remote add origin https://github.com/your-org/catalog.git
```

### "Dataset ID already exists"

- Choose different ID in form
- Check remote repo for existing IDs

## Files & Locations

| File | Purpose | Committed? |
|------|---------|-----------|
| `.datahub_config.json` | GitHub settings | ❌ No (git-ignored) |
| `.outbox/*.json` | Failed PR tasks | ❌ No (git-ignored) |
| `data/*/metadata.yaml` | Dataset metadata | ✅ Yes (in catalog repo) |
| `db.sqlite` | Search index | ❌ No (git-ignored) |

## Token Security

- **Stored in**: OS keychain (Keychain/Secret Service/Credential Manager)
- **Never written to**: Plain text files, git, YAML
- **Access**: Only via `keyring` library
- **Rotation**: Generate new PAT every 90 days

## PR Conventions

- **Branch**: `add/<dataset-id>-<yyyyMMdd-HHmm>`
- **Commit**: `feat(dataset): add <id> — <name>`
- **PR Title**: `Add dataset: <name> (<id>)`
- **Labels**: `dataset:add`, `needs-review` (configurable)

## Offline Workflow

```
┌─────────────┐
│ Save Dataset│
└──────┬──────┘
       │
   Validation
       │
   ┌───▼────┐
   │ Online?│
   └───┬────┘
       │
   ┌───▼────────┐    ┌──────────┐
   │Yes: Create │    │No: Queue │
   │PR (GitHub) │    │to Outbox │
   └────────────┘    └─────┬────┘
                           │
                      ┌────▼─────┐
                      │Wait until│
                      │online    │
                      └────┬─────┘
                           │
                      ┌────▼─────┐
                      │Retry from│
                      │Outbox (P)│
                      └──────────┘
```

## Validation Checklist

Before PR creation, the app validates:

- ✅ Schema compliance (JSON Schema)
- ✅ Required fields present
- ✅ ID format: `^[a-z0-9][a-z0-9_-]*$`
- ✅ ID uniqueness (checks remote repo)
- ✅ Array fields normalized
- ✅ Dates in ISO 8601 format

If **any fail** → Form stays open, shows errors, no commit made.

## Configuration Reference

```json
{
  "host": "github.com",
  "owner": "your-org",
  "repo": "mini-datahub-catalog",
  "default_branch": "main",
  "username": "your-username",
  "catalog_repo_path": "/home/you/catalog",
  "auto_assign_reviewers": ["maintainer1", "maintainer2"],
  "pr_labels": ["dataset:add", "needs-review"]
}
```

## Support

- **Documentation**: [GITHUB_WORKFLOW.md](GITHUB_WORKFLOW.md)
- **Issues**: https://github.com/0xpix/Hei-DataHub/issues
- **Questions**: Open a discussion

---

**Built for teams who want PR automation without git complexity.**
