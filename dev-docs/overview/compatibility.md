# Version Compatibility

## Overview

This developer documentation is **versioned alongside the application code**. Each docs version corresponds to a specific app version and tracks the internal APIs, architecture, and conventions of that release.

---

## Current Version

**Developer Docs Version:** `0.56.0-beta "Precision"`
**Compatible With:** App releases `v0.56.x`
**Branch:** `docs/devs`
**Release Date:** October 5, 2025
**Status:** ✅ Active

---

## Compatibility Matrix

| Dev Docs Version | App Version | Branch | Status | Notes |
|------------------|-------------|--------|--------|-------|
| **0.56.0-beta** | v0.56.0-beta — v0.56.x | `docs/devs` | ✅ Current | Structured Search, Inline Editing |
| 0.55.2-beta | v0.55.0-beta — v0.55.2-beta | `docs/devs-v0.55` | 📦 Archived | Auto-Stash & Clean Architecture |

---

## What "Compatible With" Means

### For Contributors

If you're working on code in branch `main` at version `v0.56.1-beta`:
- ✅ **Use these docs** (v0.56.0-beta) — APIs and architecture are compatible
- ✅ Minor version bumps (`v0.56.1`, `v0.56.2`) don't break internal APIs
- ⚠️ When `v0.57.0-beta` is released, these docs may become outdated

### For Maintainers

- **PATCH bumps** (`0.56.0` → `0.56.1`): Docs don't need updates (bug fixes only)
- **MINOR bumps** (`0.56.x` → `0.57.0`): New features → Update docs, but old docs still valid for older code
- **MAJOR bumps** (`0.x` → `1.0`): Breaking changes → Archive old docs, create new version

---

## Switching Between Versions

### Viewing Older Docs

To view documentation for an older version:

```bash
# Clone the repository
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub

# Checkout the appropriate docs branch
git checkout docs/devs-v0.55

# Serve locally
mkdocs serve -f mkdocs-dev.yml
```

**Published archives** (if available):
- v0.56.x: [Current site](https://0xpix.github.io/Hei-DataHub/dev)
- v0.55.x: [Archive (if published)](https://0xpix.github.io/Hei-DataHub/dev/v0.55)

---

## Version Mismatches

### Scenario 1: You're on `main` but docs say `v0.55.x`

**Problem:** The docs are outdated.

**Solution:**
1. Check if newer docs exist: `git checkout docs/devs`
2. If not, contribute! Update the docs for the current version.

### Scenario 2: You're working on an old release (`v0.55.x`) but docs show `v0.56.x`

**Problem:** You need older docs.

**Solution:**
1. Switch to archived docs: `git checkout docs/devs-v0.55`
2. If archived docs don't exist, use git history: `git log --all -- dev-docs/`

### Scenario 3: API changed between versions

**Problem:** Code example from docs doesn't work.

**Solution:**
1. Check the [Changelog](../changelog.md) for breaking changes
2. Use `git diff` to compare API changes:
   ```bash
   git diff docs/devs-v0.55 docs/devs -- dev-docs/api-reference/services/search.md
   ```

---

## SemVer and Developer Docs

We follow **Semantic Versioning 2.0.0** with these conventions:

### `MAJOR.MINOR.PATCH-PRERELEASE`

- **MAJOR** (`0` → `1`): Breaking changes to public APIs
  - Developer docs: New major version needed
  - Old APIs deprecated or removed

- **MINOR** (`0.56` → `0.57`): New features, no breaking changes
  - Developer docs: Update docs, but old docs still valid
  - New sections added, existing sections unchanged

- **PATCH** (`0.56.0` → `0.56.1`): Bug fixes, no new features
  - Developer docs: No updates needed (or minor corrections)

- **PRERELEASE** (`-beta`, `-rc.1`): Pre-release versions
  - Developer docs: Track pre-release APIs
  - May change before stable release

### Special Case: `0.x` Versions

We're currently in `0.x` (pre-1.0), which means:

- **MINOR bumps can include breaking changes** (e.g., `0.56` → `0.57`)
- **Developer docs must track breaking changes carefully**
- **Stability improves as we approach `1.0`**

---

## Beta vs. Stable

### Beta Releases (`-beta` suffix)

- **Audience:** Early adopters, contributors, testers
- **Stability:** APIs may change between beta releases
- **Developer docs:** Track beta APIs, mark unstable features
- **Example:** `v0.56.0-beta`

### Stable Releases (no suffix)

- **Audience:** Production users
- **Stability:** APIs stable within MINOR version
- **Developer docs:** No unstable warnings
- **Example:** `v1.0.0` (future)

**Current status:** All releases are beta (pre-1.0)

---

## Deprecation Policy

When we deprecate an API or feature:

1. **Mark as deprecated** in developer docs (add warning box)
2. **Announce in changelog** with migration guide
3. **Keep working for at least 2 MINOR versions**
4. **Remove in next MAJOR version**

**Example:**

```markdown
!!! warning "Deprecated in v0.58.0"
    `old_search_function()` is deprecated and will be removed in v1.0.0.
    Use `new_search_service.search()` instead.

    Migration guide: [Migrating from old_search_function](...)
```

---

## Tracking Breaking Changes

### In Developer Docs

Every breaking change is documented:

1. **Changelog:** `dev-docs/changelog.md`
2. **API Reference:** Warning box on affected pages
3. **Migration Guide:** Step-by-step upgrade instructions

### In Code

Breaking changes are announced:

1. **Deprecation warnings** in code (Python `warnings` module)
2. **Type hint changes** (mypy will catch issues)
3. **Tests fail** if using deprecated APIs

---

## Version Upgrade Path

### From v0.55.x → v0.56.x

**Breaking Changes:**
- None (minor version bump within `0.x`)

**New Features:**
- Structured search syntax
- Inline editing in UI

**Docs Changes:**
- New API reference for structured search
- Updated UI architecture docs

**Migration:**
```bash
git checkout main
git pull
git checkout docs/devs
git pull
```

---

## FAQ

### Q: Why do developer docs have separate versioning?

**A:** Developer docs track **internal APIs and architecture**, which evolve faster than user-facing features. Separate versioning ensures docs stay accurate for contributors working on older code.

### Q: Do I need to update docs for every code change?

**A:**
- ✅ **Yes** if you change public APIs, add modules, or alter architecture
- ❌ **No** if you fix bugs without changing interfaces

### Q: How do I know if my change is "breaking"?

**A:** A change is breaking if:
- Existing code stops working without modification
- Function signatures change (parameters added/removed/reordered)
- Return types change in incompatible ways
- Modules are renamed or moved

### Q: What if I'm working on a feature branch?

**A:** Use the docs version that matches your **base branch** (usually `main`). If `main` is at `v0.56.x`, use docs for `v0.56.0-beta`.

---

## Reporting Version Issues

If you find version mismatches or compatibility problems:

1. **Check compatibility matrix** (this page)
2. **Check changelog** for migration notes
3. **Open an issue:** [Report compatibility issue](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs,compatibility)


---

## Next Steps

- **Review [Changelog](../changelog.md)** for version history
- **Check [Known Issues](../known-issues.md)** for version-specific bugs
- **Read [Versioning Policy](../versioning.md)** for detailed versioning rules
