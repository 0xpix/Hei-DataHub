# ADR-001: Split User and Developer Documentation

**Status:** ✅ Accepted

**Date:** 2025-10-06

**Deciders:** Core Team, Project Maintainers

---

## Context

Hei-DataHub has grown from a simple TUI tool into a more complex system with:

- Multiple architectural layers (UI, Services, Core, Infrastructure)
- A growing contributor base needing deep technical documentation
- End users who need simple, task-oriented guides
- Maintainers needing release and operational documentation

Previously, all documentation lived in a single MkDocs site (`docs/` folder, published from `main` branch). This created several problems:

### Problems with Unified Documentation

1. **Audience Confusion**
   - End users overwhelmed by architectural details
   - Developers couldn't find internal APIs among user tutorials
   - Mixed content made navigation difficult

2. **Update Friction**
   - User docs need stability (change only on releases)
   - Developer docs need continuous updates (change with every code change)
   - Publishing conflicts: Can't update dev docs without affecting user docs

3. **Maintenance Burden**
   - Single changelog mixed user-facing features with internal changes
   - Review complexity: PRs touching code forced unnecessary user doc reviews
   - Versioning challenges: Dev docs version must track code, user docs track features

4. **Discoverability**
   - Contributors had to sift through user tutorials to find API references
   - No clear "developer onboarding" path
   - Architecture context scattered across multiple pages

---

## Decision

**We will split documentation into two independent sites:**

### 1. **User Documentation** (existing)
- **Audience:** End users, analysts, admins
- **Content:** Installation, tutorials, features, UI guides
- **Branch:** `main`
- **Config:** `mkdocs.yml`
- **Publishing:** GitHub Pages from `main` branch
- **URL:** `https://0xpix.github.io/Hei-DataHub`

### 2. **Developer Documentation** (new)
- **Audience:** Contributors, maintainers, integrators
- **Content:** Architecture, APIs, internals, contribution guidelines
- **Branch:** `docs/devs`
- **Config:** `mkdocs-dev.yml`
- **Publishing:** GitHub Pages from `docs/devs` branch (independent workflow)
- **URL:** `https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1` (obfuscated path for developer docs)

### Site Switcher
- Both sites will have a prominent **site switcher** at the top
- Clearly indicate which site the user is on
- One-click navigation between sites

---

## Rationale

### Why Two Sites Are Better

1. **Clear Separation of Concerns**
   - Each audience gets exactly what they need
   - No cognitive overhead from irrelevant content
   - Focused navigation structure

2. **Independent Update Cycles**
   - User docs: Updated on stable releases
   - Dev docs: Updated continuously with code changes
   - No conflicts, no coordination overhead

3. **Better Versioning**
   - User docs version with feature releases (v0.56.0)
   - Dev docs version with codebase (v0.56.0-beta, tracking internal APIs)
   - Can archive old dev docs for legacy code branches

4. **Improved Contributor Experience**
   - Single source of truth for internal APIs
   - Architecture diagrams and data flows in one place
   - Onboarding path: Overview → Architecture → API Reference → Contributing

5. **Easier Maintenance**
   - Separate changelogs: User-facing vs. internal changes
   - Separate review processes: Code reviewers check dev docs, release managers check user docs
   - No accidental breakage of user docs when updating internals

---

## Consequences

### Positive Consequences

✅ **Better user experience**
   - Users see only relevant content
   - Faster navigation (smaller site)
   - Less confusion

✅ **Better developer experience**
   - Comprehensive API references
   - Architecture context always available
   - Contribution guidelines integrated with technical docs

✅ **Faster iteration**
   - Update dev docs without waiting for releases
   - Continuous improvement of internal documentation
   - No risk of breaking user docs

✅ **Clearer ownership**
   - User docs: Product/Release managers
   - Dev docs: Code owners and contributors
   - Less coordination overhead

✅ **Independent publishing**
   - Dev docs can use experimental features (new MkDocs plugins, themes)
   - Different styling to visually distinguish the sites
   - No impact on stable user docs

### Negative Consequences

⚠️ **Maintenance of two sites**
   - Two MkDocs configs to maintain
   - Two GitHub Actions workflows
   - Two sets of dependencies
   - **Mitigation:** Automation and clear ownership

⚠️ **Potential duplication**
   - Some concepts may appear in both (e.g., "What is Hei-DataHub?")
   - **Mitigation:** Cross-link aggressively, keep user docs high-level

⚠️ **Discoverability risk**
   - Users might not know dev docs exist
   - Developers might not find user docs
   - **Mitigation:** Prominent site switcher, clear signaling on both sites

⚠️ **Branching complexity**
   - Two publishing branches (`main` and `docs/devs`)
   - Must avoid accidentally merging dev docs into main
   - **Mitigation:** Document branching strategy clearly (see ADR-002)

---

## Alternatives Considered

### Alternative 1: Single Site with Audience Tabs

**Idea:** Keep one site, but use tabs or sections to separate user and developer content.

**Rejected because:**
- Still publishes from one branch → update coordination still required
- Navigation complexity: Users might accidentally click into dev sections
- Doesn't solve versioning problem (dev docs need to track code, user docs track features)
- Single changelog still mixes concerns

### Alternative 2: Separate Repository for Dev Docs

**Idea:** Create a new repo (e.g., `Hei-DataHub-dev-docs`) for developer documentation.

**Rejected because:**
- Adds friction: Contributors must update docs in a different repo
- Synchronization pain: Keeping docs in sync with code is harder
- Discoverability: Harder to find docs if not in main repo
- Tooling overhead: CI/CD setup more complex

### Alternative 3: Wiki for Developer Docs

**Idea:** Use GitHub Wiki for developer docs, keep MkDocs for user docs.

**Rejected because:**
- Wikis are less structured (no enforced navigation)
- Wikis don't support MkDocs features (Mermaid diagrams, Material theme, search)
- Wikis are harder to version and review (no PR workflow)
- Lower quality bar (anyone can edit without review)

---

## Implementation Plan

### Phase 1: Setup (Completed)
- ✅ Create `docs/devs` branch
- ✅ Create `dev-docs/` directory structure
- ✅ Create `mkdocs-dev.yml` config
- ✅ Set up GitHub Actions workflow for publishing
- ✅ Add site switcher to both sites

### Phase 2: Content Migration (In Progress)
- 🟡 Migrate developer-focused content from user docs
- 🟡 Write new architecture documentation
- 🟡 Create API references for all modules
- 🟡 Write contribution guidelines
- 🟡 Create ADRs (including this one)

### Phase 3: Refinement
- ⏳ Review and improve navigation
- ⏳ Add diagrams and examples
- ⏳ Fill coverage gaps
- ⏳ Gather feedback from contributors

---

## Related Decisions

- [ADR-002: Branching Strategy for Developer Docs](002-branching-strategy.md)
- [ADR-003: Changelog Enforcement Policy](003-changelog-enforcement.md)

---

## Success Metrics

We'll know this decision is successful if:

1. **Contributors report easier onboarding** (measured via surveys)
2. **Fewer "where do I find X?" questions** in discussions
3. **Faster PR reviews** (docs don't block code changes)
4. **Higher docs coverage** (more APIs documented)
5. **No accidental merges** between branches (process works)

---

## Review and Revision

This ADR will be reviewed after **3 months** (January 2026) to assess:

- Are both sites being maintained?
- Is the split causing more problems than it solves?
- Should we adjust the branching strategy?

---

## Notes

- This ADR establishes the principle; implementation details are ongoing
- Site switcher design is a detail, not part of this decision
- URL structure may change based on GitHub Pages configuration

---

**Status:** Accepted ✅
**Last Updated:** 2025-10-06
