# ADR-003: Changelog Enforcement Policy

**Status:** ✅ Accepted

**Date:** 2025-10-06

**Deciders:** Core Team

---

## Context

With separate user and developer documentation sites, we need clear policies about changelogs:

- **Project changelog:** `docs/99-changelog.md` (user-facing)
- **Developer docs changelog:** `dev-docs/CHANGELOG.md` (internal)

Without enforcement, changelogs become stale and lose value.

---

## Decision

### Changelog Rules

**Every release PR MUST:**

1. ✅ Update **project changelog** (`docs/99-changelog.md`)
2. ✅ Update **developer docs changelog** (`dev-docs/CHANGELOG.md`)
3. ✅ Bump version in both `version.yaml` and documentation configs

**Every developer docs PR SHOULD:**
- Update `dev-docs/CHANGELOG.md` if adding/changing documentation

### Enforcement

**Automated checks (CI):**
- PR must touch changelog files (lint check)
- Version numbers must be consistent
- Build must pass for both sites

**Manual review:**
- Reviewers verify changelog entries are meaningful
- Release managers ensure both changelogs are updated

---

## Rationale

- **Keep history intact:** Changelogs are documentation of change over time
- **Improve communication:** Users and developers need different change summaries
- **Support versioning:** Changelogs help track compatibility
- **Enforce discipline:** If it's worth merging, it's worth documenting

---

## Consequences

### Positive
✅ Always up-to-date changelogs  
✅ Clear communication of changes  
✅ Better versioning and compatibility tracking

### Negative
⚠️ Extra overhead for contributors  
⚠️ CI complexity

**Mitigation:** Templates and clear guidelines.

---

## Related Decisions

- [ADR-001: Docs Split](001-docs-split.md)
- [ADR-002: Branching Strategy](002-branching-strategy.md)

---

**Status:** Accepted ✅
