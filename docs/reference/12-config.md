# Configuration Reference

**(req. Hei-DataHub 0.59-beta or later)**

## Configuration Overview

Hei-DataHub uses a **YAML config file** for persistent settings:

**Location:** `~/.config/hei-datahub/config.yaml`

**Stored settings:**

- Heibox/WebDAV integration (server URL, library ID)
- Theme customization
- Keybinding overrides
- UI preferences
- Performance tuning

**Not stored in config:**

- **WebDAV password:** Stored in OS keyring (Linux Secret Service) for security
- **Search index:** Cached separately in `~/.cache/hei-datahub/index.db`

**Authentication:**

WebDAV credentials are managed via CLI commands:
```bash
hei-datahub auth setup     # Interactive setup wizard
hei-datahub auth status    # Check connection
hei-datahub auth doctor    # Troubleshoot issues
hei-datahub auth clear     # Remove credentials
```

---

## Configuration File

### Location

**Linux/macOS:**
```bash
~/.config/hei-datahub/config.yaml
```

**Windows:**
```powershell
%APPDATA%\hei-datahub\config.yaml
```

**Note:** This file is **user-specific** and not shared across team members.

---

### Full Schema

```yaml
# ~/.config/hei-datahub/config.yaml

# ============================================================
# THEME
# ============================================================
theme: "gruvbox"  # Choose from: catppuccin, dracula, gruvbox,
                  # monokai, nord, one-dark, rose-pine, solarized,
                  # tokyo-night, and more

# ============================================================
# HEIBOX/WEBDAV CONFIGURATION
# ============================================================
heibox:
  server_url: "https://heibox.uni-heidelberg.de"
  library_id: "your-library-uuid-here"
  auto_sync: true               # Sync on save
  sync_interval: 15             # Minutes between background syncs

# ============================================================
# KEYBINDINGS
# ============================================================
keybindings:
  # Global actions
  quit: "q"
  help: "?"
  search: "/"
  settings: "s"
  refresh: "r"

  # Home screen
  add_dataset: "a"
  open_dataset: "enter"
  delete_dataset: "d"
  vim_down: "j"
  vim_up: "k"
  vim_top: "g g"
  vim_bottom: "shift+g"
  page_down: "ctrl+d"
  page_up: "ctrl+u"

  # Details screen
  edit_dataset: "e"
  publish_dataset: "p"
  copy_source: "c"
  open_url: "o"
  back: "escape"

  # Edit screen
  save: "ctrl+s"
  cancel: "escape"
  undo: "ctrl+z"
  redo: "ctrl+shift+z"

# ============================================================
# UI PREFERENCES
# ============================================================
ui:
  enable_critter_parade: true   # Animated critters on load
  reduce_motion: false          # Accessibility: disable animations
  startup_message: true         # Show welcome message
  confirm_delete: true          # Confirm before deleting datasets

# ============================================================
# SEARCH SETTINGS
# ============================================================
search:
  fuzzy_matching: true          # Allow typos in search
  auto_complete: true           # Show suggestions as you type
  max_results: 100              # Maximum search results to show
  highlight_matches: true       # Highlight matched terms

# ============================================================
# PERFORMANCE
# ============================================================
performance:
  cache_size_mb: 50             # Search index cache size
  background_indexing: true     # Index while app runs
  preload_datasets: true        # Load dataset list on startup
```

---

### Configuration Keys

#### Heibox Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `heibox.server_url` | String | `"https://heibox.uni-heidelberg.de"` | WebDAV server URL |
| `heibox.library_id` | String | `""` | Seafile library UUID |
| `heibox.auto_sync` | Boolean | `true` | Automatically sync datasets on save |
| `heibox.sync_interval` | Integer | `15` | Minutes between background syncs |

**Note:** Username and password are stored securely in system keyring, not in config file.

---

#### Theme Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `theme` | String | `"gruvbox"` | Color scheme name |

**Available themes:**
- `catppuccin` - Pastel colors with warm tones
- `dracula` - Dark theme with purple accents
- `gruvbox` - Retro warm colors (default)
- `monokai` - Classic dark editor theme
- `nord` - Arctic blue-ish theme
- `one-dark` - Atom editor inspired
- `rose-pine` - Natural pine colors
- `solarized` - Low-contrast classic
- `tokyo-night` - Modern dark theme
- And more...

See [Theme Customization Guide](../how-to/09-change-theme.md) for details.

---

#### Keybinding Configuration

| Section | Description |
|---------|-------------|
| `keybindings` | Custom keyboard shortcuts |

**Example customizations:**
```yaml
keybindings:
  search: "ctrl+f"        # VS Code style
  add_dataset: "ctrl+n"   # New file convention
  quit: "ctrl+q"          # Standard quit
```

See [Keybindings Guide](../how-to/08-customize-keybindings.md) for complete reference.

---

#### UI Preferences

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `ui.enable_critter_parade` | Boolean | `true` | Show animated critters on startup |
| `ui.reduce_motion` | Boolean | `false` | Disable animations for accessibility |
| `ui.startup_message` | Boolean | `true` | Show welcome message |
| `ui.confirm_delete` | Boolean | `true` | Confirm before deleting datasets |

---

#### Search Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `search.fuzzy_matching` | Boolean | `true` | Allow typos in search |
| `search.auto_complete` | Boolean | `true` | Show autocomplete suggestions |
| `search.max_results` | Integer | `100` | Maximum search results |
| `search.highlight_matches` | Boolean | `true` | Highlight matched terms |

---

#### Performance Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `performance.cache_size_mb` | Integer | `50` | Search index cache size |
| `performance.background_indexing` | Boolean | `true` | Index while app runs |
| `performance.preload_datasets` | Boolean | `true` | Load dataset list on startup |

---

## Heibox Configuration

💡 **See the comprehensive [Heibox Settings Guide](../how-to/04-settings.md)** for detailed setup instructions, including:
- Step-by-step WebDAV setup
- Finding your Library ID
- Troubleshooting connection issues
- Security best practices

### Quick Setup via CLI

Interactive setup wizard:

```bash
hei-datahub auth setup
```

**Prompts:**

1. **Server URL:** `https://heibox.uni-heidelberg.de`
2. **Username:** Your Heibox/Uni Heidelberg username
3. **Password:** Your WebDAV password (separate from web login)
4. **Library ID:** UUID from Heibox library settings

**Result:**

- Credentials saved to system keyring (encrypted)
- Connection tested and validated
- Config file updated with server URL and library ID

**Authentication commands:**

```bash
hei-datahub auth status    # Check connection status
hei-datahub auth doctor    # Troubleshoot issues
hei-datahub auth clear     # Remove credentials
```

📖 [Detailed setup guide](../how-to/04-settings.md)

**Security:**

- Password stored in OS keyring (Linux Secret Service with AES-256 encryption)
- **Never** stored in plain text config file
- Transmitted over HTTPS only

---

### Manual Configuration

Edit `~/.config/hei-datahub/config.yaml` directly:

```yaml
heibox:
  server_url: "https://heibox.uni-heidelberg.de"
  library_id: "abc123-def456-ghi789"
  auto_sync: true
  sync_interval: 15
```

**Set credentials via CLI:**

```bash
hei-datahub auth setup
# Follow interactive prompts
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
