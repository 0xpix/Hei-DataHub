# ADR 004: Developer Documentation Upgrade and Cleanup

**Status:** ✅ Accepted

**Date:** 2025-10-28

**Context:** v0.60.0-beta "Clean-up"

---

## Context

The developer documentation site (dev-docs/) needed a comprehensive upgrade to align with version **0.60.0-beta "Clean-up"**. Several issues motivated this decision:

### Problems Addressed

1. **Outdated Naming:** Documentation still referenced the legacy `mini-datahub` package name across hundreds of code examples, import statements, and CLI command references.

2. **Version Mismatch:** Documentation reflected version 0.59.x but the codebase had moved to 0.60.0-beta with significant changes:
   - UI polish and navigation improvements
   - Code cleanup and refactoring
   - Removal of deprecated features (outbox, GitHub integration)
   - Enhanced performance optimizations

3. **Structural Gaps:**
   - Missing documentation for new v0.60 features (About screen, Vim navigation, filter badges)
   - No coverage of removed features and migration paths
   - Inconsistent version banners and compatibility information

4. **Navigation Issues:**
   - Lack of cross-linking between related topics
   - No breadcrumbs or "next/previous" navigation hints
   - Missing context switchers for different documentation sites

5. **Clarity Concerns:**
   - Dense paragraphs without visual breaks
   - Missing code examples and diagrams
   - No "Why this matters" explanations for technical concepts

---

## Decision

We will perform a **comprehensive refactor and modernization** of the entire developer documentation (`dev-docs/`) to:

### 1. Rebrand from mini-datahub → hei-datahub

- **Scope:** All code samples, import paths, CLI commands, file references, and text references
- **Patterns:**
  - `from mini_datahub.core import ...` → `from hei_datahub.core import ...`
  - `mini-datahub auth setup` → `hei-datahub auth setup`
  - `src/mini_datahub/ui/app.py` → `src/hei_datahub/ui/app.py`
  - Remove dual CLI command references (only `hei-datahub` now)

### 2. Update for v0.60.0-beta

- **Version Banners:** Add to every major page:
  ```markdown
  > **Version:** 0.60.0-beta — "Clean-up"
  > This documentation reflects the refactored architecture and improved performance for Hei-DataHub.
  ```

- **Compatibility Matrix:** Update index.md and ABOUT.md to show:
  | Version | Branch | Status |
  |---------|--------|--------|
  | 0.60.0-beta | `docs/v0.60-beta-update` | ✅ Current |
  | 0.59.0-beta | `renovation/dev-docs-0.57-beta` | 📦 Archived |

- **Feature Documentation:**
  - About screen (`Ctrl+a`, Vim navigation)
  - Enhanced search filters (`source:`, `format:`, `tags:`)
  - Vim-style navigation (`gg`, `G`, `Ctrl+a`)
  - Stable scrollbars across all screens
  - Removed features (outbox, GitHub integration, PR workflow)

### 3. Improve Structure and Clarity

- **Section Summaries:** Each page starts with:
  ```markdown
  !!! info "What this section covers"
      Brief explanation of the topic and why it's important for developers.
  ```

- **Code Examples:** Add practical examples with explanations:
  ```python
  # Example: Using the search service
  from hei_datahub.services.search import FastSearchService

  search = FastSearchService()
  results = search.query("machine learning", filters={"source": "kaggle"})
  ```

- **Visual Aids:**
  - Diagram placeholders: `![Architecture Diagram](../assets/architecture-diagram.png)`
  - Tables instead of paragraphs for feature comparisons
  - Info/warning/tip callouts for key points

- **Cross-Navigation:**
  - "Next: [section]" at page ends
  - "Back to Overview" links
  - Context switcher: `:dev`, `:user`, `:tutorial`

### 4. Document the Cleanup Theme

Create new documentation sections for v0.60 cleanup:

- `refactor/core-code-cleanup.md` - Core module refactoring
- `refactor/ui-cleanup.md` - UI simplifications and removals
- `docs/cleanup.md` - Documentation restructuring

### 5. Update All File References

Ensure documentation covers all new/updated modules:

- `hei_datahub/core/` - updated models, rules, queries
- `hei_datahub/services/` - search, catalog, cloud sync
- `hei_datahub/infra/` - config, db, git
- `hei_datahub/ui/` - tui, views, widgets, themes
- `hei_datahub/cli/` - commands, auth, doctor
- `hei_datahub/utils/` - helpers, error handling

---

## Implementation

### Phase 1: Version and Naming Updates ✅

```bash
# Update site metadata
# - mkdocs-dev.yml: site_description with v0.60.0-beta
# - index.md: version banner and compatibility matrix
# - ABOUT.md: branch references

# Global find-replace across all dev-docs/*.md files
find dev-docs -name "*.md" -exec sed -i 's/mini_datahub/hei_datahub/g' {} \;
find dev-docs -name "*.md" -exec sed -i 's/mini-datahub/hei-datahub/g' {} \;
find dev-docs -name "*.md" -exec sed -i 's/Mini-DataHub/Hei-DataHub/g' {} \;
```

**Result:** All 100+ references to `mini-datahub` replaced with `hei-datahub`.

### Phase 2: Architecture Documentation

**Updated Files:**
- `architecture/overview.md` - Add v0.60 modular core structure
- `architecture/auth-and-sync.md` - WebDAV only (remove GitHub references)
- `architecture/data-flow.md` - Update with current flow diagrams
- `architecture/module-map.md` - Reflect latest module structure

**New Content:**
- Diagram placeholders for key architectural concepts
- "Why it matters" sections explaining design decisions
- Performance characteristics for each component

### Phase 3: UI/TUI Documentation

**Updated Files:**
- `ui/architecture.md` - Remove outbox, add About screen
- `ui/views.md` - Update view list and responsibilities
- `ui/widgets.md` - New widgets and updated patterns
- `ui/theming.md` - Current theme structure
- `ui/keybindings.md` - Vim navigation keybindings

**Removed References:**
- Outbox screen and workflow
- GitHub PR integration
- Cloud file preview (replaced by direct WebDAV)

### Phase 4: Codebase and API Reference

**Updated Files:**
- `codebase/overview.md` - Current package structure
- `codebase/module-walkthrough.md` - Updated file paths
- `api-reference/cli-commands.md` - v0.60 commands
  - `hei-datahub auth setup`
  - `hei-datahub auth status`
  - `hei-datahub auth clear`
  - `hei-datahub doctor`

### Phase 5: Configuration and Data

**Updated Files:**
- `config/overview.md` - `.hei-datahub/config.json` structure
- `config/environment.md` - WebDAV configuration
- `data/storage.md` - Current schema and migrations

**New Content:**
- Keyring usage examples
- WebDAV connection setup
- Secure credential storage patterns

### Phase 6: Build and Performance

**Updated Files:**
- `build/pipeline.md` - Correct package names in build configs
- `build/ci-cd.md` - Updated CI workflows
- `performance/overview.md` - v0.60 optimizations
- `performance/hotspots.md` - Current performance characteristics

### Phase 7: Visual Enhancements

**Additions:**
- Version notice banners on all major pages
- Breadcrumb navigation
- "Next/Previous" page hints
- Summary boxes with key takeaways
- Info callouts for important notes
- Context switcher buttons (Dev | User | Tutorial)

---

## Consequences

### Positive

✅ **Accurate and Current:** Documentation now reflects the actual v0.60.0-beta codebase

✅ **Consistent Branding:** All references use `hei-datahub` naming

✅ **Improved Usability:** Better navigation, examples, and visual structure

✅ **Reduced Confusion:** No outdated or conflicting information

✅ **Easier Onboarding:** New contributors can follow accurate guides

✅ **Better Maintenance:** Clear structure makes future updates easier

### Negative

⚠️ **Breaking Changes for Old Links:** External links to old paths may break

⚠️ **Migration Effort:** Users on older versions may find different info

⚠️ **One-Time Cost:** Significant effort to update all documentation

### Mitigations

- **Redirects:** Configure GitHub Pages redirects for common old paths
- **Compatibility Notes:** Add warnings for version-specific differences
- **Changelog:** Document all breaking changes in CHANGELOG.md
- **Archive Old Docs:** Keep 0.59 docs available on archived branch

---

## Related

- **ADR 003:** Changelog Enforcement (ensured we document this change)
- **ADR 002:** Branching Strategy (docs updated on feature branch)
- **ADR 001:** Docs Split (dev docs vs user docs separation)

---

## Alternatives Considered

### Alternative 1: Incremental Updates

**Approach:** Update docs gradually as features are added

**Rejected Because:**
- Creates inconsistent state where some docs are updated, others not
- Risk of missing critical updates
- Harder to test and review piecemeal changes

### Alternative 2: Automated Migration Scripts

**Approach:** Build scripts to automatically update all references

**Rejected Because:**
- Context-aware replacements (e.g., in code comments) need human review
- Risk of incorrect replacements in edge cases
- Still need manual content improvements beyond just renaming

### Alternative 3: Start from Scratch

**Approach:** Rewrite all documentation from ground up

**Rejected Because:**
- Loses valuable existing explanations and examples
- Too time-consuming for v0.60 release timeline
- Much of the existing structure and content is still valid

---

## Status: Implemented ✅

**Implementation Date:** 2025-10-28

**Branch:** `docs/v0.60-beta-update`

**Pull Request:** TBD (after completion)

**Tag:** `v0.60-beta` (after merge)

---

## References

- [CHANGELOG.md](../CHANGELOG.md) - v0.60.0-beta release notes
- `version.yaml` (project root) - Version metadata
- `mkdocs-dev.yml` (project root) - Documentation site configuration
- [Developer Docs Index](../index.md) - Updated homepage

---

**Last Updated:** 2025-10-28
