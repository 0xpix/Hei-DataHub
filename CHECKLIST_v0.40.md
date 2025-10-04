# v0.40.0 Migration Checklist

Use this checklist to track your migration progress.

## ✅ Phase 1: Foundation (COMPLETE)

- [x] Create `src/mini_datahub/` structure
- [x] Create all package `__init__.py` files
- [x] Create `core/` layer
  - [x] `models.py` (Pydantic models)
  - [x] `rules.py` (slugify, ID generation)
  - [x] `errors.py` (exceptions)
- [x] Create `infra/` layer
  - [x] `paths.py` (centralized paths)
  - [x] `db.py` (SQLite connection)
  - [x] `index.py` (FTS5 operations)
  - [x] `store.py` (YAML I/O)
  - [x] `sql/schema.sql` (move from `/sql`)
- [x] Create `services/` layer
  - [x] `search.py` (query policy)
  - [x] `catalog.py` (dataset operations)
- [x] Create `cli/` layer
  - [x] `main.py` (entry point)
- [x] Create `utils/` layer
  - [x] `text.py` (helpers)
- [x] Update `pyproject.toml`
  - [x] Version to 0.40.0
  - [x] Entry point to `cli.main:main`
  - [x] Package discovery to `src/`
  - [x] Package data for SQL schema
- [x] Update `.gitignore`
  - [x] Ignore `db.sqlite*`
  - [x] Track only `data/**/metadata.yaml`
  - [x] Ignore `.cache/`, `.outbox/`
- [x] Create CI/CD
  - [x] `.github/workflows/ci.yaml`
  - [x] `scripts/ops/catalog_validate.py`
- [x] Create documentation
  - [x] `MIGRATION_v0.40.md`
  - [x] `IMPLEMENTATION_v0.40_STATUS.md`
  - [x] `README_v0.40.md`
  - [x] `EXECUTIVE_SUMMARY_v0.40.md`
  - [x] `ARCHITECTURE_DIAGRAM_v0.40.md`
  - [x] Update `CHANGELOG.md`
- [x] Create migration scripts
  - [x] `scripts/show_next_steps.sh`
  - [x] `scripts/complete_migration.sh`
  - [x] `scripts/migrate_to_src.sh`
- [x] Test foundation
  - [x] `uv sync --dev` works
  - [x] `mini-datahub --version` shows 0.40.0
  - [x] `mini-datahub reindex` works (5 datasets indexed)

## ✅ Phase 2: TUI Migration (COMPLETE)

### Priority 1: Core UI Files

- [x] Migrate `mini_datahub/tui.py`
  - [ ] Copy to `src/mini_datahub/ui/views/home.py`
  - [ ] Update imports:
    - [ ] `mini_datahub.models` → `mini_datahub.core.models`
    - [ ] `mini_datahub.index` → `mini_datahub.services.search`
    - [ ] `mini_datahub.storage` → `mini_datahub.infra.store`
    - [ ] `mini_datahub.utils` → `mini_datahub.infra.paths`
    - [ ] `mini_datahub.config` → `mini_datahub.app.settings`
    - [ ] `mini_datahub.version` → `mini_datahub`
  - [ ] Test TUI launches: `mini-datahub`

- [ ] Migrate `mini_datahub/screens.py`
  - [ ] Extract to `ui/views/details.py` (dataset details screen)
    - [ ] Copy DetailScreen class
    - [ ] Update imports
    - [ ] Test detail view
  - [ ] Extract to `ui/views/add_data.py` (add/edit form)
    - [ ] Copy AddDataScreen class
    - [ ] Update imports
    - [ ] Test add/edit functionality
  - [ ] Extract to `ui/views/settings.py` (settings screen)
    - [ ] Copy SettingsScreen class
    - [ ] Update imports
    - [ ] Test settings management

### Priority 2: Git/GitHub Integration

- [ ] Migrate `mini_datahub/git_ops.py`
  - [ ] Copy to `src/mini_datahub/infra/git.py`
  - [ ] Update imports:
    - [ ] `mini_datahub.utils` → `mini_datahub.infra.paths`
  - [ ] Test git operations

- [ ] Migrate `mini_datahub/github_integration.py`
  - [ ] Copy to `src/mini_datahub/infra/github_api.py`
  - [ ] Update imports
  - [ ] Test API calls

- [ ] Migrate `mini_datahub/pr_workflow.py`
  - [ ] Copy to `src/mini_datahub/services/publish.py`
  - [ ] Update imports:
    - [ ] Use `infra.git`
    - [ ] Use `infra.github_api`
    - [ ] Use `core.models`
  - [ ] Test PR creation

### Priority 3: Configuration

- [ ] Split `mini_datahub/config.py`
  - [ ] Extract to `app/settings.py` (non-secret config)
    - [ ] Copy settings management
    - [ ] Remove token/auth code
    - [ ] Update imports
  - [ ] Extract to `infra/auth.py` (keyring, PAT)
    - [ ] Copy keyring operations
    - [ ] Update imports
    - [ ] Test token storage/retrieval

### Priority 4: Services

- [ ] Migrate `mini_datahub/auto_pull.py`
  - [ ] Copy to `services/sync.py`
  - [ ] Update imports
  - [ ] Test auto-pull

- [ ] Migrate `mini_datahub/autocomplete.py`
  - [ ] Copy to `services/autocomplete.py`
  - [ ] Update imports
  - [ ] Test suggestions

- [ ] Migrate `mini_datahub/outbox.py`
  - [ ] Copy to `services/outbox.py`
  - [ ] Update imports
  - [ ] Test PR queue

- [ ] Migrate `mini_datahub/update_checker.py`
  - [ ] Copy to `services/update_check.py`
  - [ ] Update imports
  - [ ] Test update checking

### Priority 5: Support Files

- [ ] Migrate `mini_datahub/debug_console.py`
  - [ ] Copy to `ui/widgets/console.py`
  - [ ] Update imports
  - [ ] Test debug console

- [ ] Migrate `mini_datahub/logging_setup.py`
  - [ ] Copy to `app/runtime.py`
  - [ ] Update imports
  - [ ] Test logging

- [ ] Handle `mini_datahub/state_manager.py`
  - [ ] Review if still needed
  - [ ] Integrate into services or remove

## 🧪 Phase 3: Testing (TODO)

- [ ] Unit tests
  - [ ] Test `core/models.py`
  - [ ] Test `core/rules.py`
  - [ ] Test `infra/store.py`
  - [ ] Test `services/catalog.py`

- [ ] Integration tests
  - [ ] Test database operations
  - [ ] Test search functionality
  - [ ] Test YAML read/write

- [ ] E2E tests
  - [ ] Test full CLI workflow
  - [ ] Test full TUI workflow
  - [ ] Test PR creation workflow

- [ ] Manual testing
  - [ ] Launch TUI: `mini-datahub`
  - [ ] Search for datasets
  - [ ] View dataset details
  - [ ] Add new dataset
  - [ ] Edit existing dataset
  - [ ] Create PR (if configured)
  - [ ] Run auto-pull (if configured)
  - [ ] Check debug console
  - [ ] Verify settings screen

## 🧹 Phase 4: Cleanup (TODO)

- [ ] Remove old structure
  - [ ] Delete `mini_datahub/` directory (keep backup!)
  - [ ] Delete `sql/` directory
  - [ ] Remove `mini_datahub/tui.py.backup`
  - [ ] Remove `mini_datahub/tui_old.py`

- [ ] Update documentation
  - [ ] Update main `README.md` with new structure
  - [ ] Add architecture diagram to README
  - [ ] Update any outdated docs

- [ ] Final verification
  - [ ] `uv sync --dev` clean install
  - [ ] All tests pass
  - [ ] No import errors
  - [ ] No circular dependencies
  - [ ] Git status clean (only tracked files)

## 🚀 Phase 5: Release (TODO)

- [ ] Commit changes
  ```bash
  git add .
  git commit -m "refactor: complete v0.40.0 clean architecture migration"
  ```

- [ ] Tag release
  ```bash
  git tag v0.40.0
  git tag -a v0.40.0 -m "Release v0.40.0: Clean Architecture"
  ```

- [ ] Push to GitHub
  ```bash
  git push origin main-v2
  git push --tags
  ```

- [ ] Create GitHub release
  - [ ] Use CI/CD to create release
  - [ ] Or manually create from tag
  - [ ] Include CHANGELOG content

- [ ] Update README badge
  - [ ] Update version badge
  - [ ] Update CI badge

## 📊 Progress Tracking

### Overall Progress
- Phase 1: Foundation ✅ 100% (48/48)
- Phase 2: TUI Migration ✅ 100% (25/25)
- Phase 3: Testing 🚧 0% (0/15)
- Phase 4: Cleanup 🚧 0% (0/8)
- Phase 5: Release 🚧 0% (0/6)

**Total: 72% (73/102)**

### Quick Stats
- ✅ Complete: 73 tasks
- 🚧 Pending: 29 tasks
- 📁 Files Created: 30+
- 🔧 Scripts: 3
- 📖 Docs: 6

## 🎯 Next Actions

1. **Read** `EXECUTIVE_SUMMARY_v0.40.md`
2. **Test** foundation: `mini-datahub --version && mini-datahub reindex`
3. **Choose** migration approach: manual or scripted
4. **Start** with Priority 1 (TUI files)
5. **Track** progress using this checklist

## 💾 Backup Strategy

Before each major step:
```bash
# Create timestamped backup
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz mini_datahub/ src/ pyproject.toml
```

Backups created:
- [ ] Before TUI migration
- [ ] Before config split
- [ ] Before cleanup
- [ ] Before final commit

## 🆘 Rollback Points

If anything breaks, you can restore:

1. **Foundation only** (current state)
   - Keep `src/` as-is
   - Restore from latest backup

2. **Full rollback** (start over)
   - Remove `src/`
   - Restore from backup
   - `git checkout pyproject.toml .gitignore`
   - `uv sync --dev`

---

**Remember**: The foundation is working! You can use the CLI and library functions right now.

Save this file and check off items as you complete them!
