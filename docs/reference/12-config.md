# Configuration Reference

This guide covers all configuration options for Hei-DataHub, including config files, environment variables, and example scenarios.

---

## Configuration Overview

Hei-DataHub uses a **JSON config file** for persistent settings:

**Location:** `PROJECT_ROOT/.datahub_config.json`

**Stored settings:**

- GitHub integration (owner, repo, username, branch)
- Auto-assign reviewers and PR labels
- Feature toggles (auto-update check, autocomplete, debug logging)

**Not stored in config:**

- **GitHub PAT (Personal Access Token):** Stored in OS keyring (secure)

---

## Configuration File

### Location

```bash
Hei-DataHub/.datahub_config.json
```

**Note:** This file is **not** version-controlled (`.gitignore` excludes it).

---

### Full Schema

```json
{
  "host": "github.com",
  "owner": "0xpix",
  "repo": "Hei-DataHub",
  "default_branch": "main",
  "username": "your-github-username",
  "auto_assign_reviewers": ["reviewer1", "reviewer2"],
  "pr_labels": ["dataset:add", "needs-review"],
  "catalog_repo_path": null,
  "auto_check_updates": true,
  "suggest_from_catalog_values": true,
  "background_fetch_interval_minutes": 0,
  "debug_logging": false
}
```

---

### Configuration Keys

#### GitHub Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `host` | String | `"github.com"` | GitHub hostname (use custom for GitHub Enterprise) |
| `owner` | String | `""` | Repository owner (username or org) |
| `repo` | String | `""` | Repository name |
| `default_branch` | String | `"main"` | Base branch for PRs |
| `username` | String | `""` | Your GitHub username |
| `auto_assign_reviewers` | List[String] | `[]` | Auto-assign these users to PRs |
| `pr_labels` | List[String] | `["dataset:add", "needs-review"]` | Labels applied to PRs |
| `catalog_repo_path` | String | `null` | Local path to separate catalog repo (beta: unused) |

---

#### Feature Toggles

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `auto_check_updates` | Boolean | `true` | Check for new releases weekly |
| `suggest_from_catalog_values` | Boolean | `true` | Autocomplete suggestions from existing datasets |
| `background_fetch_interval_minutes` | Integer | `0` | Background fetch interval (0 = disabled) |
| `debug_logging` | Boolean | `false` | Enable debug-level logs |

---

## GitHub Configuration

💡 **See the comprehensive [GitHub Settings Guide](../how-to/04-settings.md)** for detailed setup instructions, including:
- Step-by-step PAT creation (fine-grained vs classic tokens)
- Using the automated setup script (`setup_pr_workflow.sh`)
- Troubleshooting common issues
- Security best practices

### Quick Setup via TUI

1. Press ++s++ to open Settings screen
2. Fill in required fields:
    - **GitHub Owner:** Your username or org (e.g., `0xpix`)
    - **Repository Name:** Repo name (e.g., `Hei-DataHub`)
    - **GitHub Username:** Your GitHub username
    - **Personal Access Token (PAT):** Token with appropriate permissions
3. Press ++ctrl+s++ to save

**Result:**

- Config saved to `.datahub_config.json`
- PAT saved to OS keyring (secure storage)

**Token Requirements:**
- **Fine-grained tokens** (recommended): `Contents: Read and write` + `Pull requests: Read and write`
- **Classic tokens**: `repo` scope

📖 [Detailed token setup guide](../how-to/04-settings.md#step-1-create-a-personal-access-token-pat)

**Security:**

- PAT stored in OS keyring (Keychain on macOS, Secret Service on Linux, Credential Manager on Windows)
- **Never** stored in plain text

---

### Manual Configuration

Edit `.datahub_config.json` directly:

```json
{
  "host": "github.com",
  "owner": "0xpix",
  "repo": "Hei-DataHub",
  "default_branch": "main",
  "username": "your-github-username",
  "auto_assign_reviewers": ["teammate1"],
  "pr_labels": ["dataset:add", "needs-review"]
}
```

**Set PAT via Python:**

```python
import keyring
keyring.set_password("mini-datahub", "github-token", "ghp_YourTokenHere")
```

---

## Environment Variables

Currently, Hei-DataHub **does not** support environment variables for configuration. All settings must be in `.datahub_config.json` or OS keyring.

**Future versions** may support:

```bash
export DATAHUB_GITHUB_OWNER=0xpix
export DATAHUB_GITHUB_REPO=Hei-DataHub
export DATAHUB_GITHUB_TOKEN=ghp_...
```

---

## Configuration Precedence

Since environment variables are not yet supported, precedence is simple:

1. **Config file:** `.datahub_config.json`
2. **OS keyring:** GitHub PAT
3. **Defaults:** Hardcoded in `mini_datahub/app/settings.py`

---

## Example Scenarios

### Scenario 1: Minimal Setup (No GitHub)

**Goal:** Use Hei-DataHub for local dataset management only (no PRs).

**Config:**

```json
{}
```

**Steps:**

1. Skip GitHub configuration in Settings
2. Use TUI for search, add, edit
3. Manually commit YAML files if needed

---

### Scenario 2: Personal GitHub Repo

**Goal:** Use PR workflow for personal repo.

**Config:**

```json
{
  "host": "github.com",
  "owner": "your-username",
  "repo": "my-datasets",
  "default_branch": "main",
  "username": "your-username",
  "pr_labels": ["dataset:add"]
}
```

**PAT Scopes:** `repo`

**Steps:**

1. Press ++s++ to open Settings
2. Fill in owner, repo, username, PAT
3. Press ++ctrl+s++ to save
4. Add a dataset and press ++ctrl+s++ → Auto-creates PR

---

### Scenario 3: Team Collaboration

**Goal:** Auto-assign reviewers, use labels for triage.

**Config:**

```json
{
  "host": "github.com",
  "owner": "my-org",
  "repo": "data-catalog",
  "default_branch": "main",
  "username": "your-username",
  "auto_assign_reviewers": ["teammate1", "teammate2"],
  "pr_labels": ["dataset:add", "needs-review", "high-priority"]
}
```

**PAT Scopes:** `repo`, `workflow` (if PRs trigger CI)

**Steps:**

1. Configure Settings as above
2. Add dataset → PR auto-created with reviewers + labels
3. Teammates review and merge

---

### Scenario 4: GitHub Enterprise

**Goal:** Use Hei-DataHub with GitHub Enterprise Server.

**Config:**

```json
{
  "host": "github.company.com",
  "owner": "data-team",
  "repo": "datasets",
  "default_branch": "main",
  "username": "your-username",
  "pr_labels": ["dataset:add"]
}
```

**PAT:** Generate from your GitHub Enterprise instance.

---

### Scenario 5: Custom Data Directory (Future)

**Goal:** Use a separate repo for datasets (not inside app repo).

**Config:**

```json
{
  "catalog_repo_path": "/home/user/my-datasets"
}
```

**Note:** This feature is **not fully implemented** in v0.55.x beta. Datasets must live in `Hei-DataHub/data/` for now.

---

## Feature Toggle Details

### `auto_check_updates`

**Default:** `true`

**Behavior:**

- On TUI launch, checks GitHub API for latest release (once per week)
- Displays notification if newer version available

**Disable:**

```json
{
  "auto_check_updates": false
}
```

---

### `suggest_from_catalog_values`

**Default:** `true`

**Behavior:**

- Form fields suggest values from existing datasets (autocomplete)
- E.g., typing "s3://" suggests previous `storage_location` values

**Disable:**

```json
{
  "suggest_from_catalog_values": false
}
```

---

### `background_fetch_interval_minutes`

**Default:** `0` (disabled)

**Behavior:**

- If > 0, periodically fetches updates from remote Git repo
- **Not fully implemented in v0.55.x beta**

**Enable (future):**

```json
{
  "background_fetch_interval_minutes": 30
}
```

---

### `debug_logging`

**Default:** `false`

**Behavior:**

- Enables verbose debug logs (useful for troubleshooting)
- Logs written to `~/.mini-datahub/logs/`

**Enable:**

```json
{
  "debug_logging": true
}
```

---

## File Paths

### Config File

```
PROJECT_ROOT/.datahub_config.json
```

**Example:** `/home/user/Hei-DataHub/.datahub_config.json`

---

### Database

```
PROJECT_ROOT/db.sqlite
```

**Example:** `/home/user/Hei-DataHub/db.sqlite`

---

### Data Directory

```
PROJECT_ROOT/data/
```

**Example:** `/home/user/Hei-DataHub/data/`

---

### Cache Directory

```
PROJECT_ROOT/.cache/
```

**Used for:** Temporary files, lock files.

---

### Outbox Directory

```
PROJECT_ROOT/.outbox/
```

**Used for:** Failed PR tasks (retryable).

---

### Logs Directory

```
~/.mini-datahub/logs/
```

**Files:**

- `hei-datahub.log` — General logs
- `debug.log` — Debug-level logs (if `debug_logging = true`)

---

## Reset Configuration

### Delete Config File

```bash
rm .datahub_config.json
```

**Result:** Settings reset to defaults.

---

### Clear GitHub PAT

**macOS:**

```bash
security delete-generic-password -s "mini-datahub" -a "github-token"
```

**Linux:**

```bash
secret-tool clear service mini-datahub username github-token
```

**Windows:**

Use Credential Manager GUI or PowerShell:

```powershell
cmdkey /delete:mini-datahub
```

---

## Troubleshooting

### "GitHub Not Connected" After Configuring

**Cause:** PAT invalid or missing `repo` scope.

**Fix:**

1. Regenerate PAT with `repo` scope
2. Re-enter in Settings (++s++)
3. Restart TUI

---

### Config Changes Not Applied

**Cause:** Config cached in memory.

**Fix:**

1. Restart TUI:
    ```bash
    hei-datahub
    ```
2. Or reload programmatically:
    ```python
    from mini_datahub.app.settings import reload_github_config
    reload_github_config()
    ```

---

### PAT Not Saved

**Cause:** Keyring not available (missing `keyring` package or OS keyring service).

**Fix:**

1. Install keyring:
    ```bash
    pip install keyring
    ```
2. Ensure OS keyring service is running:
    - **macOS:** Keychain (built-in)
    - **Linux:** `gnome-keyring` or `kwallet`
    - **Windows:** Credential Manager (built-in)

---

## Security Best Practices

1. **Never commit `.datahub_config.json`** — It's in `.gitignore`, but double-check
2. **Rotate PATs regularly** — Generate new tokens every 90 days
3. **Use minimal scopes** — Only `repo` scope needed for PRs
4. **Revoke unused PATs** — Delete tokens for old projects
5. **Use fine-grained PATs** — GitHub's new token type with repo-specific access

---

## Next Steps

- **[Tutorial: Your First Dataset](../how-to/05-first-dataset.md)** — Practice adding datasets
- **[FAQ](../help/90-faq.md)** — Troubleshooting config issues
- **[GitHub Workflow Guide](https://github.com/0xpix/Hei-DataHub/blob/main/GITHUB_WORKFLOW.md)** — Detailed PR workflow docs
