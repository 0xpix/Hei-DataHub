# Update Command Documentation (v0.58.0-beta)

## Overview
Hei-DataHub now includes a built-in `update` command that makes it easy to update to the latest version without manually running `uv` commands.

## Usage

### Basic Update
Update to the latest version from the default branch:

```bash
hei-datahub update
```

**Output:**
```
Updating Hei-DataHub...

  Source: git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=hei-datahub
  Using uv tool install --upgrade...

✓ Update completed successfully!

Run 'hei-datahub --version-info' to see the new version.
```

### Update from Specific Branch
Update from a different branch (e.g., for testing or switching versions):

```bash
hei-datahub update --branch main
```

### Check Version After Update
```bash
hei-datahub --version-info
```

## How It Works

The `update` command:
1. Uses `uv tool install --upgrade` under the hood
2. Pulls the latest code from the specified Git branch
3. Reinstalls the package with the new version
4. Preserves all your user data (datasets, database, config)

### What Gets Updated
- ✅ Application code and dependencies
- ✅ Packaged dataset templates
- ✅ CLI commands and features

### What Gets Preserved
- ✅ Your datasets in `~/.local/share/hei-datahub/datasets/`
- ✅ Your database in `~/.local/share/hei-datahub/db.sqlite`
- ✅ Your config in `~/.config/hei-datahub/config.json`
- ✅ Your keybindings in `~/.config/hei-datahub/keymap.json`
- ✅ All logs and state

## Default Branch

By default, the update command uses:
```
chore/uv-install-data-desktop-v0.58.x
```

This is the branch with the latest XDG-compliant standalone installation features.

## Requirements

- UV package manager must be installed
- SSH access to GitHub repository (if using SSH URLs)
- Alternatively, use HTTPS with token authentication

## Error Handling

### UV Not Found
```
❌ Error: 'uv' command not found!

Please ensure UV is installed:
  curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Update Failed
If the update fails, the error output from UV will be displayed. Common causes:
- Network issues
- Invalid branch name
- Authentication problems
- Git repository access issues

## Examples

### Regular Update Workflow
```bash
# Check current version
hei-datahub --version

# Update to latest
hei-datahub update

# Verify new version
hei-datahub --version-info

# Launch with new features
hei-datahub
```

### Switch Between Branches
```bash
# Update to development branch
hei-datahub update --branch develop

# Switch back to stable branch
hei-datahub update --branch chore/uv-install-data-desktop-v0.58.x
```

## Technical Details

### Implementation
The update command is implemented in `src/mini_datahub/cli/main.py`:

```python
def handle_update(args):
    """Handle the update subcommand."""
    import subprocess
    
    # Determine branch
    branch = args.branch or "chore/uv-install-data-desktop-v0.58.x"
    repo_url = f"git+ssh://git@github.com/0xpix/Hei-DataHub.git@{branch}#egg=hei-datahub"
    
    # Run uv tool install --upgrade
    result = subprocess.run(
        ["uv", "tool", "install", "--upgrade", repo_url],
        capture_output=True,
        text=True,
        check=False
    )
    
    # Handle success/failure
    if result.returncode == 0:
        print("✓ Update completed successfully!")
        sys.exit(0)
    else:
        print("❌ Update failed!")
        print(result.stderr)
        sys.exit(1)
```

### Command Registration
```python
# In main() function
parser_update = subparsers.add_parser(
    "update",
    help="Update Hei-DataHub to the latest version"
)
parser_update.add_argument(
    "--branch",
    type=str,
    default="chore/uv-install-data-desktop-v0.58.x",
    help="Git branch to install from"
)
parser_update.set_defaults(func=handle_update)
```

## Benefits

### Before (Manual Update)
```bash
# User had to remember the full command
uv tool install --upgrade "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=hei-datahub"
```

### After (Built-in Update)
```bash
# Simple and memorable
hei-datahub update
```

## Safety

- ✅ **Data preservation**: User data is in XDG directories, separate from package
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Rollback**: Can switch branches to previous versions
- ✅ **Error handling**: Clear error messages if update fails

## Related Commands

```bash
# Check current version
hei-datahub --version

# Detailed version info
hei-datahub --version-info

# Update to latest
hei-datahub update

# Diagnostic paths
hei-datahub paths

# Reindex after major update (if needed)
hei-datahub reindex
```

## Troubleshooting

### "Update failed" with network error
- Check internet connection
- Verify GitHub access (try `ssh -T git@github.com`)
- Try using HTTPS instead of SSH

### "Invalid branch" error
- Verify the branch exists: `git ls-remote --heads git@github.com:0xpix/Hei-DataHub.git`
- Use the default by omitting `--branch` flag

### Update succeeded but TUI shows old version
- Clear cache: `rm -rf ~/.cache/hei-datahub`
- Re-run: `hei-datahub --version-info`
- Restart terminal if needed

## Future Enhancements

Potential improvements for future versions:
- [ ] `hei-datahub update --check` - Check for updates without installing
- [ ] `hei-datahub update --list-branches` - Show available branches
- [ ] `hei-datahub update --version X.Y.Z` - Update to specific release tag
- [ ] Automatic update notifications in TUI
- [ ] Rollback command: `hei-datahub rollback`
- [ ] Update history: `hei-datahub update --history`

## Commit
- `685f9ca` - feat: Add 'hei-datahub update' command for easy updates
