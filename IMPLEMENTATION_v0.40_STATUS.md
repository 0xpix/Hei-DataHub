# v0.40.0 Restructure - Implementation Summary

## ✅ Completed

### 1. Directory Structure ✓
- Created complete `src/mini_datahub/` layout
- All layers: `app/`, `ui/`, `core/`, `services/`, `infra/`, `cli/`, `utils/`
- Package `__init__.py` files in place
- SQL schema moved to `infra/sql/schema.sql`

### 2. Core Modules ✓
- `core/models.py` - Pydantic models from old `models.py`
- `core/rules.py` - Slugify, ID generation, validation rules
- `core/errors.py` - Domain exceptions

### 3. Infrastructure Layer ✓
- `infra/paths.py` - Centralized path management (all constants)
- `infra/db.py` - SQLite connection, schema initialization
- `infra/index.py` - FTS5 upsert/delete operations
- `infra/store.py` - YAML read/write, validation
- `infra/sql/schema.sql` - Packaged SQL schema

### 4. Services Layer ✓
- `services/search.py` - FTS5 query policy
- `services/catalog.py` - Dataset save/get orchestration

### 5. Utilities ✓
- `utils/text.py` - Slugify, humanize, truncate, highlight

### 6. CLI ✓
- `cli/main.py` - Entry point with version, reindex, TUI launch
- Handles graceful errors during migration

### 7. Configuration Files ✓
- `pyproject.toml` - Updated to v0.40.0, src/ layout, package data
- `.gitignore` - Updated for data tracking (metadata only)
- `src/mini_datahub/__init__.py` - Version 0.40.0, app name

### 8. CI/CD ✓
- `.github/workflows/ci.yaml` - App tests + catalog validation
- `scripts/ops/catalog_validate.py` - Metadata validation script

### 9. Documentation ✓
- `MIGRATION_v0.40.md` - Comprehensive migration guide
- `CHANGELOG.md` - v0.40.0 entry added
- `scripts/complete_migration.sh` - Automated migration script

## 🚧 TODO (Manual Steps Required)

### 1. Copy/Migrate Remaining Files
The following files from old `mini_datahub/` need to be migrated:

**High Priority (Core Functionality):**
- `tui.py` → `ui/views/home.py` (main TUI app)
- `screens.py` → split into `ui/views/` (details, add_data, settings)
- `git_ops.py` → `infra/git.py`
- `github_integration.py` → `infra/github_api.py`
- `config.py` → split:
  - Settings → `app/settings.py`
  - Auth → `infra/auth.py`

**Medium Priority (Services):**
- `auto_pull.py` → `services/sync.py`
- `pr_workflow.py` → `services/publish.py`
- `autocomplete.py` → `services/autocomplete.py`
- `outbox.py` → `services/outbox.py`
- `update_checker.py` → `services/update_check.py`

**Low Priority (Support):**
- `debug_console.py` → `ui/widgets/console.py`
- `logging_setup.py` → `app/runtime.py`
- `state_manager.py` → integrate into services

### 2. Update All Imports
After copying files, update imports:

**Old:**
```python
from mini_datahub.models import DatasetMetadata
from mini_datahub.utils import DATA_DIR
from mini_datahub.index import search_datasets
```

**New:**
```python
from mini_datahub.core.models import DatasetMetadata
from mini_datahub.infra.paths import DATA_DIR
from mini_datahub.services.search import search_datasets
```

### 3. Split Combined Modules

**`index.py` (old) → 3 files:**
- Connection logic → `infra/db.py` (✓ done)
- Upsert/delete → `infra/index.py` (✓ done)
- Search queries → `services/search.py` (✓ done)

**`storage.py` (old) → 2 files:**
- YAML I/O → `infra/store.py` (✓ done)
- Orchestration → `services/catalog.py` (✓ done)

**`config.py` (old) → 2 files:**
- Settings/prefs → `app/settings.py` (TODO)
- Keyring/PAT → `infra/auth.py` (TODO)

### 4. Test & Verify
```bash
# Install
uv sync --dev

# Check version
mini-datahub --version  # Should show 0.40.0

# Test reindex
mini-datahub reindex

# Test TUI (will fail until tui.py is migrated)
mini-datahub
```

### 5. Clean Up
Once everything works:
```bash
# Remove old structure
rm -rf mini_datahub/
rm -rf sql/

# Commit
git add .
git commit -m "refactor: complete migration to v0.40.0 clean architecture"
git tag v0.40.0
git push --tags
```

## 📋 Migration Checklist

- [x] Create src/ structure
- [x] Core domain models
- [x] Infrastructure: paths, db, index, store
- [x] Services: search, catalog
- [x] Utils: text helpers
- [x] CLI entrypoint
- [x] Update pyproject.toml
- [x] Update .gitignore
- [x] CI/CD workflow
- [x] Catalog validation script
- [x] Documentation (migration guide, changelog)
- [x] Migration automation script
- [ ] Migrate TUI (tui.py → ui/views/)
- [ ] Migrate Git operations
- [ ] Migrate GitHub API
- [ ] Migrate config/auth
- [ ] Migrate services (sync, publish, autocomplete, outbox)
- [ ] Update all imports
- [ ] Test full workflow
- [ ] Remove old structure
- [ ] Tag release

## 🎯 Quick Start (After Migration)

```bash
# 1. Backup (automated)
./scripts/complete_migration.sh

# 2. Manual: Copy remaining files
# See "TODO" section above

# 3. Manual: Update imports in copied files
# Change old imports to new layer-based imports

# 4. Test
uv sync --dev
mini-datahub --version
mini-datahub reindex
mini-datahub  # Launch TUI

# 5. Clean up (once verified)
rm -rf mini_datahub/ sql/
git add . && git commit -m "refactor: v0.40.0 clean architecture"
```

## 🆘 Rollback

If anything breaks:
```bash
# Find your backup file
ls -lt backup-*.tar.gz | head -1

# Restore
tar -xzf backup-pre-v0.40-TIMESTAMP.tar.gz
git checkout pyproject.toml .gitignore
uv sync --dev
```

## 📚 Key Files Created

### Source Code
- `src/mini_datahub/__init__.py` - Version 0.40.0
- `src/mini_datahub/core/` - Domain models & rules
- `src/mini_datahub/infra/` - I/O adapters
- `src/mini_datahub/services/` - Orchestration
- `src/mini_datahub/cli/main.py` - Entry point

### Configuration
- `pyproject.toml` - v0.40.0, src/ layout
- `.gitignore` - Data tracking rules

### CI/CD
- `.github/workflows/ci.yaml` - Full pipeline
- `scripts/ops/catalog_validate.py` - Validation

### Documentation
- `MIGRATION_v0.40.md` - Complete guide
- `CHANGELOG.md` - What changed
- `scripts/complete_migration.sh` - Automation

## 🏗️ Architecture Benefits

### Separation of Concerns
- **Core**: Pure domain logic (no I/O)
- **Infra**: Tech adapters (DB, files, git, HTTP)
- **Services**: Orchestration (calls infra + core)
- **UI**: Textual views (calls services only)

### Dependency Rules
```
UI ──→ Services ──→ Infra
        ↓            ↓
       Core    ←────┘
```

### Testability
- Core: Unit test with no mocks
- Services: Mock infra layer
- Infra: Integration tests
- UI: E2E tests

### Future-Proofing
- Easy to swap DB (change infra/db.py)
- Easy to swap git provider (change infra/github_api.py)
- Easy to split catalog repo (change paths only)
- Easy to add REST API (new cli/ or api/ layer)

## 🎉 What's Better

1. **Clear boundaries** - No more "where does this go?"
2. **No cyclic deps** - Clean import graph
3. **Testable** - Each layer mocked independently
4. **Documented** - Architecture in README
5. **CI validated** - Both code and data
6. **Packaged properly** - SQL schema ships with app
7. **Version visible** - Shows in CLI and TUI
8. **Single repo ready** - Data tracked correctly
9. **Split ready** - Easy to move catalog later
10. **Professional** - Beta-quality structure

---

## Next: Complete the Migration

Use this as your checklist. Once all checkboxes are ✓, you'll have a
clean, maintainable codebase ready for v1.0!
