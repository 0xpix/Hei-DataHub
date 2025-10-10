# CLI Command Structure Update

## Summary

Updated the desktop integration CLI commands to use a more organized structure under the `desktop` subcommand.

## Changes

### Old Commands ❌
```bash
hei-datahub setup desktop [--force] [--no-cache-refresh]
hei-datahub uninstall
```

### New Commands ✅
```bash
hei-datahub desktop install [--force] [--no-cache-refresh]
hei-datahub desktop uninstall
```

## Rationale

The new structure:

1. **Groups related commands** - All desktop integration commands are now under `hei-datahub desktop`
2. **More intuitive** - `desktop install` and `desktop uninstall` are clearer than `setup desktop` and `uninstall`
3. **Consistent with future expansion** - Can add more desktop-related subcommands like:
   - `hei-datahub desktop status` - Check installation status
   - `hei-datahub desktop repair` - Fix broken installations
   - `hei-datahub desktop verify` - Validate installed files

## Implementation Details

### Modified Files

1. **`src/mini_datahub/cli/main.py`**
   - Changed `parser_setup` to `parser_desktop`
   - Changed `setup_subparsers` to `desktop_subparsers`
   - Renamed `parser_setup_desktop` to `parser_desktop_install`
   - Moved `parser_uninstall` under `desktop` subcommand as `parser_desktop_uninstall`
   - Updated command handler to check for `desktop` instead of `setup`

2. **Documentation Updates**
   - `docs/installation/desktop-integration.md` - Updated all command examples
   - `DESKTOP_INTEGRATION.md` - Updated API reference and testing guide
   - `DESKTOP_INTEGRATION_SUMMARY.md` - Updated all CLI examples and test results

### Handler Functions

The actual handler functions remain unchanged:
- `handle_setup_desktop()` - Still handles installation (called by `desktop install`)
- `handle_uninstall()` - Still handles uninstallation (called by `desktop uninstall`)

### Auto-Install

The automatic first-run installation continues to work as before - it calls `ensure_desktop_assets_once()` in the main CLI entrypoint before any command is executed.

## Testing

All commands tested and verified:

```bash
# Show desktop subcommands
$ hei-datahub desktop --help
usage: mini-datahub desktop [-h] {install,uninstall} ...

positional arguments:
  {install,uninstall}
    install            Install desktop integration (icons and .desktop entry)
    uninstall          Uninstall desktop integration (removes launcher and icons)

# Install desktop integration
$ hei-datahub desktop install --force
✓ Desktop assets installed successfully

# Uninstall desktop integration
$ hei-datahub desktop uninstall
✓ Removed 5 file(s)

# Auto-install on first run
$ hei-datahub --version
✓ Desktop integration installed (first run only)
```

## Backward Compatibility

**Breaking Change**: Old commands (`hei-datahub setup desktop` and `hei-datahub uninstall`) will no longer work.

Users will need to update to:
- `hei-datahub desktop install`
- `hei-datahub desktop uninstall`

This is acceptable because:
1. Desktop integration is a new feature (v0.58.1-beta)
2. Most users rely on auto-install (transparent)
3. Manual commands are documented clearly
4. CLI help text guides users to correct commands

## Benefits

1. **Clearer organization** - Desktop-related commands grouped together
2. **Better discoverability** - `hei-datahub --help` shows `desktop` as a clear category
3. **Future-proof** - Easy to add more desktop subcommands without cluttering top level
4. **Semantic consistency** - `install`/`uninstall` pair is more intuitive than `setup`/`uninstall`

## Documentation Status

✅ All documentation updated to reflect new command structure:
- User guides
- Examples
- Testing instructions
- API reference
- Help text
