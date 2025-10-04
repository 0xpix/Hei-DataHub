# Migration to src/ Layout - Version 0.40.0

This guide explains the restructuring to a clean, layered architecture.

## What Changed

### Version Bump
- **v0.1.0 → v0.40.0 (Beta)**
- Indicates maturity and significant architectural improvement

### Directory Structure
```
OLD:                              NEW:
mini_datahub/                     src/mini_datahub/
  ├── cli.py                        ├── __init__.py (with __version__)
  ├── tui.py                        ├── app/
  ├── screens.py                    │   ├── runtime.py (logging)
  ├── models.py                     │   └── settings.py (config)
  ├── storage.py                    ├── ui/
  ├── index.py                      │   ├── views/
  ├── config.py                     │   │   ├── home.py
  ├── git_ops.py                    │   │   ├── details.py
  ├── github_integration.py         │   │   ├── add_data.py
  ├── pr_workflow.py                │   │   └── settings.py
  ├── auto_pull.py                  │   └── widgets/
  ├── autocomplete.py               │       ├── tables.py
  ├── outbox.py                     │       ├── forms.py
  ├── update_checker.py             │       ├── console.py (debug)
  ├── debug_console.py              │       └── toasts.py
  ├── logging_setup.py              ├── core/
  ├── utils.py                      │   ├── models.py
  └── version.py                    │   ├── rules.py (slugify, etc.)
                                    │   └── errors.py
sql/schema.sql                      ├── services/
                                    │   ├── search.py
                                    │   ├── catalog.py
                                    │   ├── sync.py (auto-pull)
                                    │   ├── publish.py (PR workflow)
                                    │   ├── autocomplete.py
                                    │   ├── outbox.py
                                    │   └── update_check.py
                                    ├── infra/
                                    │   ├── paths.py (all paths)
                                    │   ├── store.py (YAML I/O)
                                    │   ├── db.py (sqlite)
                                    │   ├── index.py (FTS5)
                                    │   ├── git.py
                                    │   ├── github_api.py
                                    │   ├── auth.py (keyring)
                                    │   ├── net.py (HTTP helpers)
                                    │   └── sql/
                                    │       └── schema.sql
                                    ├── cli/
                                    │   ├── main.py (entrypoint)
                                    │   └── commands.py
                                    └── utils/
                                        ├── text.py (slugify, humanize)
                                        ├── cache.py (LRU)
                                        └── timing.py
```

### Dependency Rules (enforced)

```
┌────────┐
│   UI   │────────────┐
└────────┘            │
     │                │
     ↓                ↓
┌──────────┐    ┌────────┐
│ Services │───→│  Core  │
└──────────┘    └────────┘
     │               ↑
     ↓               │
┌─────────┐          │
│  Infra  │──────────┘
└─────────┘
     │
     ↓
┌─────────┐
│  Utils  │
└─────────┘
```

- **UI** → Services, Core, Utils, App (never Infra directly)
- **Services** → Infra, Core, Utils
- **Infra** → Utils only (no circular deps)
- **Core** → Nothing (pure domain logic)
- **CLI** → App, Services

## Migration Steps

### 1. Structure Already Created
The new `src/` directory structure has been created with:
- All package `__init__.py` files
- Core modules (models, rules, errors)
- Infrastructure paths module
- SQL schema moved into package

### 2. Update Imports (TODO)

You'll need to update all imports in the copied files. Examples:

**OLD:**
```python
from mini_datahub.models import DatasetMetadata
from mini_datahub.utils import DATA_DIR
from mini_datahub.storage import read_dataset
```

**NEW:**
```python
from mini_datahub.core.models import DatasetMetadata
from mini_datahub.infra.paths import DATA_DIR
from mini_datahub.infra.store import read_dataset
```

### 3. Split Combined Modules

Some modules need to be split:

**index.py → 3 modules:**
- `infra/db.py` - SQLite connection, schema init
- `infra/index.py` - FTS5 upsert operations
- `services/search.py` - Query policy (limits, snippets)

**storage.py → 2 modules:**
- `infra/store.py` - YAML read/write
- `services/catalog.py` - Validation orchestration, save/update flows

**config.py → 2 modules:**
- `app/settings.py` - Non-secret configuration
- `infra/auth.py` - Keyring PAT management

**utils.py → multiple:**
- Path constants → `infra/paths.py` (already done)
- Text helpers → `utils/text.py`
- Caching → `utils/cache.py` (if needed)

### 4. Move Remaining Files

Use the migration script or manually copy:

```bash
chmod +x scripts/migrate_to_src.sh
./scripts/migrate_to_src.sh
```

Or manually:
```bash
# Example manual copies (then edit imports)
cp mini_datahub/autocomplete.py src/mini_datahub/services/autocomplete.py
cp mini_datahub/outbox.py src/mini_datahub/services/outbox.py
cp mini_datahub/update_checker.py src/mini_datahub/services/update_check.py
# ... etc
```

### 5. Install and Test

```bash
# Reinstall with new structure
uv sync --dev

# Test CLI
mini-datahub --version
# Should show: 0.40.0

# Test reindex
mini-datahub reindex

# Launch TUI
mini-datahub
```

### 6. Remove Old Structure

Once everything works:
```bash
# Backup first!
tar -czf old-structure-backup.tar.gz mini_datahub/

# Remove old directory
rm -rf mini_datahub/

# Remove old SQL directory
rm -rf sql/
```

## File-by-File Mapping

| Old File | New Location | Notes |
|----------|--------------|-------|
| `version.py` | Merged into `__init__.py` | Version now at top level |
| `models.py` | `core/models.py` | Pure domain models |
| `utils.py` (paths) | `infra/paths.py` | Path centralization |
| `utils.py` (text) | `utils/text.py` | Helper functions |
| `storage.py` | `infra/store.py` + `services/catalog.py` | Split I/O from orchestration |
| `index.py` (DB) | `infra/db.py` | Connection, init |
| `index.py` (FTS) | `infra/index.py` | Upsert operations |
| `index.py` (search) | `services/search.py` | Query policy |
| `config.py` (settings) | `app/settings.py` | Non-secrets |
| `config.py` (PAT) | `infra/auth.py` | Keyring ops |
| `git_ops.py` | `infra/git.py` | Local git |
| `github_integration.py` | `infra/github_api.py` | API calls |
| `pr_workflow.py` | `services/publish.py` | PR orchestration |
| `auto_pull.py` | `services/sync.py` | Pull + reindex |
| `autocomplete.py` | `services/autocomplete.py` | Suggestions |
| `outbox.py` | `services/outbox.py` | Failed PR queue |
| `update_checker.py` | `services/update_check.py` | Release check |
| `logging_setup.py` | `app/runtime.py` | Startup, logging |
| `debug_console.py` | `ui/widgets/console.py` | Shell widget |
| `tui.py` | `ui/views/home.py` | Main screen |
| `screens.py` | `ui/views/*.py` | Split by screen |
| `cli.py` | `cli/main.py` + `cli/commands.py` | Entry + commands |
| `sql/schema.sql` | `infra/sql/schema.sql` | Packaged resource |

## Configuration Updates

### pyproject.toml
✅ Already updated:
- Version: `0.40.0`
- Entry point: `mini_datahub.cli.main:main`
- Package discovery: `where = ["src"]`
- Package data: includes `infra/sql/*.sql`

### .gitignore
✅ Already updated:
- Ignores `db.sqlite` and cache
- Tracks only `data/**/metadata.yaml` and docs
- Ignores `.outbox/` and local config

## Verification Checklist

- [ ] `mini-datahub --version` shows `0.40.0`
- [ ] TUI launches without import errors
- [ ] Search works (FTS5 queries)
- [ ] Can add/edit datasets
- [ ] Save → PR creates branch and commits
- [ ] Auto-pull downloads changes
- [ ] Reindex command works
- [ ] No `ui → infra` imports (only via services)
- [ ] SQL schema loads from package
- [ ] Data directory tracking is correct (git status)

## Rollback Plan

If migration fails:
```bash
# Restore old structure
tar -xzf old-structure-backup.tar.gz

# Restore old pyproject.toml
git checkout pyproject.toml

# Reinstall
uv sync --dev
```

## Next Steps After Migration

1. **Update Documentation**
   - README with new structure
   - CHANGELOG entry for v0.40.0

2. **Setup CI**
   - App tests (pytest, ruff, black)
   - Catalog validation (metadata schema)

3. **Tag Release**
   ```bash
   git tag v0.40.0
   git push --tags
   ```

4. **Future: Catalog Repo Split**
   - When ready, `data/` can move to separate repo
   - Only need to update `DATA_DIR` and repo config
   - All code stays the same

## Questions?

See `TROUBLESHOOTING.md` or check logs in `~/.mini-datahub/logs/`.
