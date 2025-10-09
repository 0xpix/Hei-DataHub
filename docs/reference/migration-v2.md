# Configuration Migration Guide

## Config Version 1 → Version 2

Hei-DataHub configuration version 2 introduces new customization options for the UI while maintaining full backward compatibility.

### What's New in Version 2

1. **Logo Customization** - Change or replace the ASCII banner
2. **Custom Stylesheets** - Add your own TCSS files to customize appearance
3. **External Help Files** - Optional external help documentation

### Automatic Migration

When you first run Hei-DataHub after upgrading, your config will be **automatically migrated** from version 1 to version 2. This process:

- ✅ Preserves all existing settings
- ✅ Adds new v2 fields with sensible defaults
- ✅ Updates `config_version` to `2`
- ✅ Keeps your current theme and keybindings

**No action required!** The migration happens automatically on startup.

### What Gets Added

The following sections will be added to your config file:

```yaml
# New in v2: UI customization
ui:
  logo:
    path: null            # Custom logo (null = use default)
    align: center         # left | center | right
    color: cyan           # Color name
    padding_top: 0
    padding_bottom: 1
  help_file: null         # Custom help file (optional)

# New in v2: Theme extensions
theme:
  name: gruvbox           # Your existing theme
  stylesheets: []         # Custom TCSS files
  tokens: null            # Design tokens file (optional)
  overrides: {}           # Your existing overrides
```

### Manual Migration (if needed)

If you want to manually update your config:

1. **Backup your current config**:
   ```bash
   cp ~/.config/hei-datahub/config.yaml ~/.config/hei-datahub/config.yaml.backup
   ```

2. **Update the version number**:
   ```yaml
   config_version: 2  # Change from 1 to 2
   ```

3. **Add the new sections** (see above)

4. **Save and restart** the application

### Verifying Migration

To check if migration was successful:

```bash
# View your config file
cat ~/.config/hei-datahub/config.yaml

# Or use the show_config script
python scripts/show_config.py
```

Look for `config_version: 2` at the top of the file.

### Rollback (Not Recommended)

If you need to rollback to version 1 (not recommended, as v2 is fully compatible):

1. Restore from backup:
   ```bash
   cp ~/.config/hei-datahub/config.yaml.backup ~/.config/hei-datahub/config.yaml
   ```

2. The app will work with v1 config, but new features won't be available.

### Getting Help

If you encounter issues during migration:

- Check the logs: `~/.mini-datahub/logs/datahub.log`
- Look for migration warnings or errors
- Restore from backup and try again
- [Report an issue](https://github.com/0xpix/Hei-DataHub/issues) with log excerpts

---

## Key Differences: V1 vs V2

| Feature | V1 | V2 |
|---------|-----|-----|
| Logo customization | ❌ Hardcoded | ✅ Configurable via `ui.logo` |
| Custom stylesheets | ❌ Not supported | ✅ Via `theme.stylesheets` |
| Help file | ❌ Built-in only | ✅ Optional external file via `ui.help_file` |
| Theme tokens | ❌ Not supported | ✅ Via `theme.tokens` |
| Keybindings | ✅ Supported | ✅ Supported (unchanged) |
| Theme selection | ✅ Supported | ✅ Supported (unchanged) |

All version 1 features continue to work in version 2.
