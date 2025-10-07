# Configure GitHub Integration

**Requirements:** Hei-DataHub 0.56-beta or later

Learn how to set up GitHub integration for automated Pull Request workflows in Hei-DataHub. This guide covers creating a Personal Access Token (PAT), configuring settings via the TUI or setup script, and understanding all available options.

---

## Overview

Hei-DataHub can automatically create Pull Requests to a GitHub catalog repository when you add, edit, or delete datasets.

**What you'll need:**

- A GitHub account
- A Personal Access Token with appropriate permissions
- 5-10 minutes for setup

**Planned for the upcoming versions**

- A catalog repository (public or private) dedicated to storing the entire dataset collection.

---

## Quick Setup with Script

The fastest way to set up GitHub integration is using the automated setup script:

```bash
# From the Hei-DataHub directory
./scripts/setup_pr_workflow.sh
```

The script will guide you through:

1. Installing dependencies (if needed)
2. Creating/cloning your catalog repository
3. Setting up `.gitignore` and `schema.json`
4. Generating a GitHub Personal Access Token (opens documentation)
5. Configuring `.datahub_config.json`
6. Launching the TUI to add your token

**After running the script:**

1. Launch Hei-DataHub: `mini-datahub`
2. Press `S` to open Settings
3. Paste your GitHub token (copied from GitHub)
4. Click **Test Connection** to verify
5. Click **Save Settings** to complete setup

**Planned for 0.58-beta**

- Add CLI flags to the script for fully automated setup (no TUI) -> `hei-datahub pr`

---

## Manual Setup: Step-by-Step

### Step 1: Create a Personal Access Token (PAT)

GitHub Personal Access Tokens provide secure, granular access to your repositories.

#### Option A: Fine-grained Personal Access Token (Recommended)

1. Go to [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta)
2. Click **Generate new token**
3. **Token name:** `Mini DataHub Catalog Access`
4. **Expiration:** 90 days (recommended) or custom
5. **Repository access:** Only select repositories
   - Click the dropdown
   - Select your catalog repository (e.g., `mini-datahub-catalog`)
6. **Permissions → Repository permissions:**
   - **Contents:** Read and write ✅
   - **Pull requests:** Read and write ✅
7. Click **Generate token**
8. **Copy the token immediately** (starts with `github_pat_`)
   - You won't be able to see it again!
   - Store it temporarily in a secure note app

#### Option B: Classic Personal Access Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. **Note:** `Mini DataHub Catalog Access`
4. **Expiration:** 90 days or custom
5. **Select scopes:**
   - `repo` (Full control of private repositories) ✅
6. Click **Generate token**
7. **Copy the token** (starts with `ghp_`)

**Security Best Practices:**
- Use fine-grained tokens when possible (more secure, scoped access)
- Set expiration dates (90 days recommended)
- Never commit tokens to Git
- Rotate tokens regularly
- Revoke unused tokens

### Step 2: Configure via TUI (Recommended)

Launch Hei-DataHub and open the Settings screen:

```bash
mini-datahub
# Press 's' to open Settings
```

#### Fill in the Settings Form

1. **GitHub Host:** `github.com` (default, leave as-is)

2. **Owner/Organization:** Your GitHub username or organization name
   - Example: `mycompany` (from `github.com/mycompany/mini-datahub-catalog`)

3. **Repository Name:** The catalog repository name
   - Example: `mini-datahub-catalog`

4. **Default Branch:** Main branch name
   - Example: `main` (or `master` for older repos)

5. **GitHub Username:** Your personal GitHub username
   - Used for commit attribution and PR authorship

6. **Personal Access Token (PAT):** Paste your token
   - Starts with `github_pat_` or `ghp_`
   - Will be stored securely in your OS keychain
   - Displayed as `••••••••` after saving

7. **Catalog Repository Path:** Full path to your cloned repository
   - Example: `/home/user/catalogs/my-catalog`
   - Use absolute paths, not relative (`~` is expanded automatically)

8. **Auto-assign Reviewers:** Comma-separated GitHub usernames (optional)
   - Example: `alice, bob, charlie`
   - These users will be automatically assigned to review PRs
   - Leave empty if you don't want auto-assignment

9. **PR Labels:** Comma-separated labels for automatic tagging (optional)
   - Example: `dataset:add, needs-review, climate`
   - Labels help organize PRs in your repository
   - Default: `dataset:add, needs-review`

#### Test and Save

1. Click **Test Connection** to verify your settings
   - Success: ✅ "Successfully connected to GitHub! Repository accessible."
   - Failure: Check your token, repository name, and permissions

2. Click **Save Settings** to persist configuration
   - Settings saved to `.datahub_config.json`
   - Token saved to OS keychain (macOS Keychain, GNOME Keyring, Windows Credential Manager)

3. Press `Escape` or `Q` to return to the home screen

### Step 6: Configure via Config File (Alternative)

If you prefer editing configuration files directly, or the TUI isn't working:

Create `.datahub_config.json` in the Hei-DataHub root directory:

```json
{
  "host": "github.com",
  "owner": "your-org",
  "repo": "mini-datahub-catalog",
  "default_branch": "main",
  "username": "your-github-username",
  "catalog_repo_path": "/home/user/catalogs/my-catalog",
  "auto_assign_reviewers": ["alice", "bob"],
  "pr_labels": ["dataset:add", "needs-review"]
}
```

**Important:** The config file does NOT store your token for security reasons. You must add it via the TUI:

1. Launch Hei-DataHub: `mini-datahub`
2. Press `s` for Settings
3. Verify pre-filled values from config file
4. Paste your token in the **Personal Access Token** field
5. Click **Test Connection**
6. Click **Save Settings**

---

## Configuration Reference

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| **host** | GitHub server hostname | `github.com` |
| **owner** | GitHub username or organization | `mycompany` |
| **repo** | Catalog repository name | `mini-datahub-catalog` |
| **default_branch** | Main branch for PRs | `main` |
| **username** | Your GitHub username | `alice` |
| **token** | Personal Access Token | `github_pat_...` (stored in keychain) |
| **catalog_repo_path** | Absolute path to local repo | `/home/user/catalogs/my-catalog` |

### Optional Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **auto_assign_reviewers** | Auto-assign PR reviewers | `[]` (none) |
| **pr_labels** | Labels for new PRs | `["dataset:add", "needs-review"]` |
| **auto_check_updates** | Weekly update check | `true` |
| **suggest_from_catalog_values** | Autocomplete suggestions | `true` |
| **background_fetch_interval_minutes** | Background fetch interval | `0` (disabled) |
| **debug_logging** | Enable debug logs | `false` |

### Token Storage: OS Keychain

Hei-DataHub uses your operating system's secure credential storage via the `keyring` library:

- **macOS:** Keychain Access
- **Linux:** GNOME Keyring, KWallet, or Secret Service
- **Windows:** Windows Credential Manager

**Service name:** `mini-datahub`
**Username:** `github-token`

You can verify token storage using your OS tools:

```bash
# macOS
security find-generic-password -s "mini-datahub" -a "github-token"

# Linux (GNOME)
secret-tool lookup service mini-datahub username github-token

# Windows
cmdkey /list | findstr "mini-datahub"
```

---

## Testing Your Configuration

### Test Connection in TUI

1. Press `s` to open Settings
2. Verify all fields are filled
3. Click **Test Connection**
4. Look for success message: ✅ "Successfully connected to GitHub!"

### Manual Connection Test

You can test your GitHub connection from the command line:

```bash
# Using curl with your token
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/your-org/mini-datahub-catalog

# Should return JSON with repository details
```
---

## Troubleshooting

### "Failed to authenticate with GitHub"

**Cause:** Invalid or expired token, or insufficient permissions.

**Solution:**
1. Generate a new token with correct permissions (Contents + Pull requests)
2. Paste the new token in Settings
3. Click **Save Settings**
4. Test connection again

### "Repository not found or inaccessible"

**Cause:** Incorrect owner/repo, or token doesn't have access.

**Solution:**
1. Verify repository name: `owner/repo` format
2. Check repository visibility (private repos need token access)
3. For fine-grained tokens, ensure repository is selected in token settings
4. Regenerate token if needed

### "No such file or directory: catalog_repo_path"

**Cause:** Catalog repository path doesn't exist or is incorrect.

**Solution:**
1. Verify path exists: `ls /path/to/catalog`
2. Use absolute paths (not relative like `./catalog`)
3. Clone repository if missing: `git clone https://github.com/owner/repo.git /path`

### "Failed to push to remote repository"

**Cause:** Network issues, authentication failure, or branch protection.

**Solution:**
1. Check internet connection
2. Verify token has `Contents: Write` permission
3. Check if branch is protected (Settings → Branches in GitHub)
4. Try manual push: `cd /path/to/catalog && git push`

### Token not saved to keychain

**Cause:** `keyring` library not installed or keyring backend unavailable.

**Solution:**
1. Check if keyring is available: `python -c "import keyring; print(keyring.get_keyring())"`
2. Install keyring backend:
   ```bash
   # Linux
   sudo apt install gnome-keyring  # or libsecret-1-dev

   # macOS (built-in)
   # No action needed

   # Windows (built-in)
   # No action needed
   ```
3. Reinstall dependencies: `uv sync --python /usr/bin/python`

### "Config file not found"

**Cause:** `.datahub_config.json` doesn't exist.

**Solution:**
1. Run setup script: `./scripts/setup_pr_workflow.sh`
2. Or create manually in Hei-DataHub root directory
3. Or configure entirely via TUI (Settings screen)

---

## Advanced Configuration

### Using GitHub Enterprise

For GitHub Enterprise Server (self-hosted):

1. Press `s` to open Settings
2. Change **GitHub Host** to your server (e.g., `github.company.com`)
3. Use a token from your Enterprise instance
4. All other settings remain the same

### Automation with Environment Variables

You can override settings via environment variables (useful for CI/CD):

```bash
export DATAHUB_GITHUB_TOKEN="github_pat_..."
export DATAHUB_CATALOG_PATH="/ci/catalog"

mini-datahub
```

**Note:** Environment variable support is a future feature planned for v0.58.

---

## Security Best Practices

### Protecting Your Token

✅ **DO:**
- Store tokens in OS keychain (automatic with Hei-DataHub)
- Set expiration dates (90 days recommended)
- Use fine-grained tokens with minimal permissions
- Revoke tokens when no longer needed
- Rotate tokens regularly

❌ **DON'T:**
- Commit tokens to Git (`.datahub_config.json` is in `.gitignore`)
- Share tokens via email, Slack, or other insecure channels
- Use tokens with excessive permissions (`admin` scope)
- Leave tokens without expiration dates
- Reuse tokens across multiple applications

### Repository Security

Add `.datahub_config.json` to your `.gitignore`:

```bash
# In Hei-DataHub root directory
echo ".datahub_config.json" >> .gitignore
```

### Token Revocation

If your token is compromised:

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Find the token (e.g., "Mini DataHub Catalog Access")
3. Click **Revoke**
4. Generate a new token (see [Step 1](#step-1-create-a-personal-access-token-pat))
5. Update in Hei-DataHub Settings
6. Click **Remove Token** → **Save Settings** → paste new token → **Save Settings**

---

## Understanding the PR Workflow

### What happens when you create a dataset?

1. **Metadata saved locally** to `data/dataset-name/metadata.yaml`
2. **Git operations:**
   - Branch created: `dataset/add-dataset-name-TIMESTAMP`
   - Files staged: `git add data/dataset-name/metadata.yaml`
   - Commit: `git commit -m "feat(dataset): Add dataset-name"`
   - Push: `git push origin dataset/add-dataset-name-TIMESTAMP`
   - Switch back to default branch
3. **Pull Request created** on GitHub with:
   - Title: `Add Dataset: dataset-name`
   - Body: Metadata summary (name, description, source, tags)
   - Labels: Auto-applied from `pr_labels` setting
   - Reviewers: Auto-assigned from `auto_assign_reviewers`
4. **Team reviews** the PR on GitHub
5. **Merge completes** the workflow
6. **Local sync** (optional) pulls merged changes

### Customizing PR Templates

```bash
# In your repository
mkdir -p .github
cat > .github/pull_request_template.md << 'EOF'
## Dataset Information

**Name:** <!-- Auto-filled by Hei-DataHub -->
**Source:** <!-- Auto-filled -->
**Tags:** <!-- Auto-filled -->

## Review Checklist

- [ ] Metadata is complete and accurate
- [ ] Source is accessible and trustworthy
- [ ] Tags are appropriate
- [ ] No sensitive data in metadata
- [ ] Follows naming conventions

## Additional Notes

<!-- Add any context for reviewers -->
EOF

git add .github/pull_request_template.md
git commit -m "Add PR template for dataset reviews"
git push
```

---

## Related Documentation

- [**Search for Datasets**](07-search-advanced.md) - Find and filter datasets in your catalog
- [**Edit Datasets**](06-edit-datasets.md) - Modify existing dataset metadata (creates PRs)
- [**FAQ**](../help/90-faq.md) - Common questions about GitHub integration
- [**Troubleshooting**](../help/troubleshooting.md) - Resolve common issues

---

## What's Next?

✅ **GitHub configured!** You're ready to:

- Press `A` to add your first dataset (creates a PR)
- Press `/` to search and filter datasets
- Press `S` anytime to update settings
- Check GitHub for new Pull Requests

**Learn more:**
- [Getting Started Guide](../getting-started/01-getting-started.md)
- [The Basics](../getting-started/03-the-basics.md)
- [All Keyboard Shortcuts](../reference/keybindings.md)
