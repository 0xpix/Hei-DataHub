# ADR-002: Branching Strategy for Developer Docs

**Status:** ✅ Accepted

**Date:** 2025-10-06

**Deciders:** Core Team

---

## Context

With the decision to split user and developer documentation (see [ADR-001](001-docs-split.md)), we need a clear branching strategy for:

- Publishing independent sites from different branches
- Preventing accidental merges that could break either site
- Versioning docs alongside code changes
- Archiving docs for older versions

---

## Decision

### Primary Branches

**1. `main` branch**
- User-facing documentation
- Published to: `https://0xpix.github.io/Hei-DataHub`
- Config: `mkdocs.yml`
- Directory: `docs/`

**2. `docs/devs` branch**
- Developer documentation
- Published to: `https://0xpix.github.io/Hei-DataHub/dev` (or separate URL)
- Config: `mkdocs-dev.yml`
- Directory: `dev-docs/`

**These branches are independent and never merged into each other.**

### Workflow Rules

**For user docs changes:**
```bash
git checkout main
# Edit docs/
git commit -m "docs: update user tutorial"
git push origin main
# GitHub Actions publishes to main site
```

**For developer docs changes:**
```bash
git checkout docs/devs
# Edit dev-docs/
git commit -m "docs: add API reference"
git push origin docs/devs
# GitHub Actions publishes to dev site
```

---

## Rationale

### Why `docs/devs` as Branch Name?

Considered options:
- `dev-docs` ✅ **Chosen** (clear, descriptive, follows `docs/` pattern)
- `developer-docs` (too long)
- `gh-pages-dev` (implementation detail, not semantic)

### Why Independent Branches?

- **No merge conflicts:** Changes to one site can't break the other
- **Clear separation:** Git history shows which site was updated
- **Independent CI/CD:** Each branch has its own workflow
- **Easy to reason about:** No need to cherry-pick or rebase

---

## Consequences

### Positive
✅ Clean separation of concerns  
✅ No accidental merges  
✅ Independent publishing pipelines  
✅ Clear ownership (main = release team, docs/devs = developers)

### Negative
⚠️ Code changes don't automatically flow to dev docs  
⚠️ Must remember to switch branches when editing docs  
⚠️ Two separate git histories

**Mitigation:** Clear documentation, branch protection rules.

---

## Implementation

### Branch Protection Rules

On GitHub, configure:

**`main` branch:**
- Require PR reviews for `docs/` changes
- Require status checks to pass
- Do not allow force pushes

**`docs/devs` branch:**
- Require PR reviews for `dev-docs/` changes
- Require MkDocs build to pass
- Do not allow force pushes
- **Block merges from or to `main`**

### GitHub Actions

Two separate workflows:

**`.github/workflows/pages.yml`** (user docs)
- Triggers on push to `main`
- Builds from `mkdocs.yml`
- Publishes to root of GitHub Pages

**`.github/workflows/dev-docs.yml`** (developer docs)
- Triggers on push to `docs/devs`
- Builds from `mkdocs-dev.yml`
- Publishes to `/dev` subdirectory or custom domain

---

## Alternatives Considered

### Alternative 1: Single Branch with Two Workflows

Keep everything in `main`, use GitHub Actions `paths` filters to publish different sites.

**Rejected:**
- Doesn't solve versioning problem
- Docs for older versions hard to maintain
- Changes to code structure would trigger both builds

### Alternative 2: Use Tags for Versions

Tag docs at release time (e.g., `docs-v0.56.0`), build from tags.

**Rejected:**
- Complex to maintain
- Hard to update docs after release
- Doesn't solve continuous dev docs updates

---

## Related Decisions

- [ADR-001: Docs Split](001-docs-split.md)
- [ADR-003: Changelog Enforcement](003-changelog-enforcement.md)

---

**Status:** Accepted ✅
