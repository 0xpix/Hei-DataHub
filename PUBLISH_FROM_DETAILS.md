# Publishing Datasets as PRs from Details View

## Overview

You can now publish any dataset as a Pull Request directly from its Details view with a single keystroke (`P`). This feature provides a seamless workflow for contributing datasets to the catalog repository without manually handling git or GitHub operations.

## Features

### 🚀 One-Key Publishing

- **`P` key** in Details view creates a PR for the dataset
- Automatic validation before PR creation
- Opens PR in browser automatically
- Shows real-time status updates

### 🔐 Persistent GitHub Configuration

- GitHub credentials stored securely in OS keychain
- Configuration loaded once at app startup
- Never asked for token again (unless you sign out)
- Connection status displayed in Home screen

### 📊 Remote Status Checking

- Automatically checks if dataset exists in catalog repo
- Shows publication status in Details view
- Disables PR creation for already-published datasets

### 🎨 Visual Feedback

- ASCII art banner ("HEI-DATAHUB") on every dataset detail page
- Color-coded status indicators:
  - **Green** ● GitHub Connected
  - **Yellow** ⚠ Configured but connection failed
  - **Gray** ○ Not connected
- Real-time PR creation progress

## Usage

### First-Time Setup

1. **Configure GitHub Settings** (Press `S` from Home):
   ```
   GitHub Host:       github.com
   Owner:             your-org
   Repository:        catalog-repo-name
   Default Branch:    main
   GitHub Username:   your-username
   GitHub Token:      ghp_your_token_here
   Catalog Path:      /path/to/local/catalog/clone
   ```

2. **Save Settings** (Press `Ctrl+S`)
   - Credentials are stored securely in OS keychain
   - Connection status is tested automatically

3. **Done!** You're never asked for the token again.

### Publishing a Dataset

1. **Browse Datasets** (Home screen)
2. **Open Details** (Press `Enter` on any dataset)
3. **Check Status**:
   - "📤 Not yet in catalog repo" → Ready to publish
   - "✓ Already published" → Already in repo (P disabled)
4. **Publish** (Press `P`)
   - Creates feature branch
   - Commits metadata
   - Pushes to repo (or fork)
   - Opens PR automatically
   - Shows PR number and opens in browser

## How It Works

### Remote Existence Check

When you open a dataset's Details view, the app:

1. Loads metadata from local database
2. Displays ASCII banner and all fields
3. Checks GitHub API for `data/<id>/metadata.yaml` on default branch
4. Updates status indicator:
   - Not found → "Press P to Publish as PR!"
   - Found → "Already published to catalog repo"
   - Error → Shows warning with reason

### PR Creation Flow

When you press `P`:

```
┌─────────────────────────────────────┐
│ 1. Validate Configuration          │
│    - GitHub credentials present?    │
│    - Catalog path exists?           │
│    - Metadata valid?                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 2. Check Remote Uniqueness          │
│    - Query GitHub API               │
│    - Ensure ID doesn't exist        │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 3. Git Operations                   │
│    - Fetch & update base branch     │
│    - Create feature branch          │
│    - Write metadata.yaml            │
│    - Stage & commit                 │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 4. Push Strategy                    │
│    - Has push access?               │
│      Yes: Push to central repo      │
│      No:  Fork & push to fork       │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 5. Create Pull Request              │
│    - Open PR on GitHub              │
│    - Add labels & reviewers         │
│    - Return PR URL & number         │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 6. Success Feedback                 │
│    - Update status: "✓ PR created!" │
│    - Show notification with PR#     │
│    - Open PR in browser             │
│    - Cache "exists remotely" flag   │
└─────────────────────────────────────┘
```

### Failure Handling

If PR creation fails:
- Error message shown in Details view
- Dataset queued to **Outbox** for retry
- Toast notification with reason
- Press `P` (Outbox) from Home to retry later

## Keyboard Shortcuts

### Home Screen
| Key | Action |
|-----|--------|
| `Enter` | Open dataset details |
| `A` | Add new dataset |
| `S` | Open Settings |
| `P` | Open Outbox (retry failed PRs) |
| `q` | Quit |

### Details Screen
| Key | Action |
|-----|--------|
| `P` | **Publish as PR** (if not already in repo) |
| `y` | Copy source to clipboard |
| `o` | Open source URL in browser |
| `Esc` / `q` | Back to Home |

### Settings Screen
| Key | Action |
|-----|--------|
| `Ctrl+S` | Save settings |
| `Esc` / `q` | Cancel |

## Configuration Storage

### Secure Storage

- **PAT Token**: Stored in OS keychain
  - **Linux**: gnome-keyring / kwallet / SecretService
  - **macOS**: Keychain Access
  - **Windows**: Credential Manager
- **Service**: `mini-datahub`
- **Username**: `github-token`

### Config File

Non-secret fields stored in `.datahub_config.json`:
```json
{
  "host": "github.com",
  "owner": "your-org",
  "repo": "catalog-repo",
  "default_branch": "main",
  "username": "your-username",
  "catalog_repo_path": "/path/to/catalog",
  "auto_assign_reviewers": ["reviewer1"],
  "pr_labels": ["dataset:add", "needs-review"]
}
```

### Token Lifetime

- GitHub fine-grained tokens expire after 90 days (or your chosen duration)
- App shows warning if connection fails
- Regenerate token and update in Settings (S)

## GitHub Connection Status

### Status Indicators

**Home Screen Header:**

1. **Connected** (Green ●)
   ```
   ● GitHub Connected (username@owner/repo)
   ```
   - All credentials present
   - Connection test passed
   - Ready to create PRs

2. **Configured but Disconnected** (Yellow ⚠)
   ```
   ⚠ GitHub Configured (connection failed)  Press S for Settings
   ```
   - Credentials stored
   - Connection test failed (token expired/invalid, network issue, etc.)
   - Update token in Settings

3. **Not Connected** (Gray ○)
   ```
   ○ GitHub Not Connected  Press S to configure
   ```
   - No credentials stored
   - First-time setup needed

**Details Screen Footer:**

1. **Not Published**
   ```
   📤 Not yet in catalog repo  Press P to Publish as PR!
   ```

2. **Already Published**
   ```
   ✓ Already published to catalog repo  Press P to view (disabled)
   ```

3. **Not Configured**
   ```
   💡 Configure GitHub in Settings (S) to publish PRs
   ```

## Validation

Before creating a PR, the app validates:

### Configuration
- ✅ GitHub host, owner, repo, username present
- ✅ Token present and valid
- ✅ Catalog repo path exists locally
- ✅ Path is a git repository

### Metadata
- ✅ Schema compliance (Pydantic validation)
- ✅ Required fields present (id, dataset_name, description, source, etc.)
- ✅ ID format: `^[a-z0-9][a-z0-9_-]*$`
- ✅ Array fields normalized
- ✅ Dates in ISO 8601 format

### Remote State
- ✅ ID uniqueness (checks GitHub API)
- ✅ No conflicting PRs exist

If **any validation fails** → PR blocked, error shown, no git operations performed.

## Troubleshooting

### "GitHub not configured"

**Problem**: Credentials not set up.

**Solution**:
1. Press `S` to open Settings
2. Fill in all required fields
3. Generate PAT: https://github.com/settings/tokens?type=beta
4. Paste token and save

### "GitHub Configured (connection failed)"

**Problem**: Token expired, invalid, or network issue.

**Solution**:
1. Check network connectivity
2. Verify token hasn't expired
3. Test token permissions: https://github.com/settings/tokens
4. Regenerate token if needed
5. Update in Settings

### "Catalog path does not exist"

**Problem**: Local clone path is wrong or doesn't exist.

**Solution**:
```bash
# Clone the catalog repo
git clone https://github.com/your-org/catalog.git /path/to/catalog

# Update Settings with correct path
# Press S → Update Catalog Path → Save
```

### "Dataset ID already exists"

**Problem**: Another dataset with same ID exists in remote repo.

**Solution**:
- Choose a different dataset ID
- Check remote repo: https://github.com/your-org/catalog/tree/main/data

### "Already published to catalog repo"

**Problem**: Dataset already exists remotely, P key does nothing.

**Status**: This is expected behavior! The dataset is already in the catalog.

**If you need to update it**:
- Clone the catalog repo
- Edit `data/<id>/metadata.yaml` locally
- Create PR manually with git

### PR creation fails but no error shown

**Problem**: Queued to Outbox.

**Solution**:
1. Press `P` from Home (Outbox screen)
2. Select failed task
3. Press `R` to retry
4. Check error message for details

## Security Notes

### Token Permissions

Your GitHub fine-grained PAT needs:

**Repository permissions** (for the catalog repo only):
- **Contents**: Read and write
- **Pull requests**: Read and write
- **Metadata**: Read (automatically included)

**Optional**:
- **Issues**: Read and write (for labels)

### Token Storage

- Never stored in plain text
- Never committed to git
- Never logged or displayed
- OS-level encryption (keychain/keyring)
- Accessible only by Mini DataHub app

### Token Rotation

Best practices:
1. Set token expiration to 90 days
2. Calendar reminder to regenerate
3. Update in Settings when expired
4. Old token is overwritten in keychain

## Examples

### Example 1: First-Time Publish

```
1. Launch app: uv run python -m mini_datahub.tui
2. Press S → Configure GitHub → Save
3. Status bar shows: "● GitHub Connected (alice@myorg/catalog)"
4. Navigate to dataset "weather-stations-2024"
5. Press Enter (open details)
6. Banner shows: "HEI-DATAHUB"
7. Footer shows: "📤 Not yet in catalog repo  Press P to Publish as PR!"
8. Press P
9. Status: "📤 Creating PR..."
10. Success: "✓ PR #42 created successfully!"
11. Browser opens: https://github.com/myorg/catalog/pull/42
```

### Example 2: Already Published

```
1. Navigate to dataset "global-temperatures"
2. Press Enter (open details)
3. Footer shows: "✓ Already published to catalog repo"
4. Press P → Nothing happens (disabled)
5. Toast: "Dataset already exists in catalog repo"
```

### Example 3: Offline/No Config

```
1. Navigate to dataset "test-data"
2. Press Enter (open details)
3. Footer shows: "💡 Configure GitHub in Settings (S) to publish PRs"
4. Press P → Error: "GitHub not configured. Open Settings (S) to connect."
```

## Integration with Existing Workflow

### From Add Form (Ctrl+S)

- Existing behavior preserved
- Automatically creates PR when saving new dataset
- Same validation and workflow

### From Details (P)

- New feature!
- Publish existing datasets that weren't auto-submitted
- Useful for migrating old datasets to catalog
- Same PR creation logic

### From Outbox (R)

- Retry failed PR attempts
- Same for both Add Form and Details failures

## Technical Details

### API Endpoints Used

- `GET /repos/:owner/:repo/contents/:path` - Check file existence
- `POST /repos/:owner/:repo/pulls` - Create PR
- `POST /repos/:owner/:repo/issues/:number/labels` - Add labels
- `POST /repos/:owner/:repo/pulls/:number/requested_reviewers` - Assign reviewers

### Branch Naming

Format: `add/<dataset-id>-<yyyyMMdd-HHmm>`

Example: `add/weather-2024-20251004-1530`

### Commit Message

Format: `feat(dataset): add <id> — <name>`

Example: `feat(dataset): add weather-2024 — Global Weather Stations`

### PR Title

Format: `Add dataset: <name> (<id>)`

Example: `Add dataset: Global Weather Stations (weather-2024)`

## Future Enhancements

Potential improvements (not in v3.0):

- [ ] Bulk publish (select multiple datasets)
- [ ] Edit-in-place from Details → auto-update PR
- [ ] PR status tracking (open/merged/closed)
- [ ] Conflict resolution UI
- [ ] Branch cleanup after merge

---

## Quick Reference

**Publish Dataset PR**: `Enter` (open details) → `P` (publish)

**Check Status**: Look at footer in Details view

**Configure GitHub**: `S` (settings) from Home

**Retry Failed**: `P` (outbox) from Home → `R` (retry)

---

**Version**: v3.0
**Last Updated**: 2025-10-04
**Related Docs**:
- [GITHUB_WORKFLOW.md](GITHUB_WORKFLOW.md) - Complete setup guide
- [GITHUB_TOKEN_GUIDE.md](GITHUB_TOKEN_GUIDE.md) - Token permissions visual guide
- [PR_WORKFLOW_QUICKREF.md](PR_WORKFLOW_QUICKREF.md) - Quick reference card
