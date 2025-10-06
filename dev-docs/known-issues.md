# Known Issues - Developer Documentation Site

This page tracks issues, gaps, and TODOs specific to the **developer documentation site** itself (not the Hei-DataHub application).

For application-level known issues, see:
- [Project Known Issues (v0.56.x)](../devs/0.56.x-beta/KNOWN_ISSUES.md)

---

## Current Status

**Last Updated:** 2025-10-06  
**Developer Docs Version:** 0.56.0-beta  
**Coverage:** 🟡 In Progress (~40% complete)

---

## High Priority Gaps 🔴

### Missing API References

| Module | Status | Priority | Assignee |
|--------|--------|----------|----------|
| `services/search.py` | 📝 Stub only | HIGH | Unassigned |
| `services/catalog.py` | 📝 Stub only | HIGH | Unassigned |
| `services/publish.py` | 📝 Stub only | HIGH | Unassigned |
| `infra/db.py` | ❌ Missing | HIGH | Unassigned |
| `infra/index.py` | ❌ Missing | HIGH | Unassigned |
| `core/models.py` | ❌ Missing | HIGH | Unassigned |
| `core/rules.py` | ❌ Missing | HIGH | Unassigned |
| `ui/views/home.py` | ❌ Missing | MEDIUM | Unassigned |

### Missing Guides

- ❌ **How to add a new dataset** (step-by-step)
- ❌ **How to add a new UI view** (with keybinding example)
- ❌ **How to run performance profiling**
- ❌ **How to debug SQL queries**
- ❌ **How to test GitHub Actions locally**

### Missing Diagrams

- ❌ Complete dependency graph (graphviz or Mermaid)
- ❌ UI navigation flow diagram
- ❌ Database schema diagram (ERD)
- ❌ CI/CD pipeline visualization

---

## Medium Priority Gaps 🟡

### Incomplete Sections

| Section | Completion | Notes |
|---------|------------|-------|
| Codebase Tour | 20% | Only framework created |
| API Reference | 15% | Many modules missing |
| Performance | 30% | Profiling guide missing |
| Security | 40% | Supply chain section incomplete |
| Extensibility | 25% | Plugin examples needed |

### Missing Content

- ⚠️ **Test data and fixtures guide:** How to create test datasets
- ⚠️ **Performance SLAs:** What are acceptable latencies?
- ⚠️ **Deprecation policy:** How do we sunset features?
- ⚠️ **Code review checklist:** Detailed criteria for reviewers
- ⚠️ **Glossary terms:** Many project-specific terms undefined

---

## Low Priority / Future Enhancements 🟢

### Nice-to-Have Features

- 💡 **Interactive API explorer** (Swagger-like for Python APIs)
- 💡 **Video walkthroughs** of complex workflows
- 💡 **Automated docs coverage report** (which functions lack docs)
- 💡 **Changelog auto-generation** from commit messages
- 💡 **PDF export** of entire dev docs site

### Quality Improvements

- 🔧 **Add more code examples** to API references
- 🔧 **Cross-link all related pages** (many missing links)
- 🔧 **Standardize page templates** (some pages don't follow template)
- 🔧 **Add "Edit on GitHub" links** to all pages
- 🔧 **Improve search keywords** (add metadata to pages)

---

## Bugs & Issues 🐛

### Build Issues

- ❌ None currently

### Content Issues

| Issue | Description | Reporter | Date |
|-------|-------------|----------|------|
| #001 | Broken link in architecture overview | Auto-check | 2025-10-06 |
| #002 | Inconsistent code block formatting | Review | 2025-10-06 |

### Navigation Issues

- ⚠️ Some sections are too deeply nested (4+ levels)
- ⚠️ "Quick Reference" page doesn't exist yet

---

## Technical Debt 📊

### Documentation Technical Debt

1. **Outdated examples:** Some code snippets reference old API signatures
   - **Affected pages:** `api-reference/services/search.md` (stub)
   - **Fix:** Update after implementing full API docs

2. **Incomplete diagrams:** Several Mermaid diagrams are placeholders
   - **Affected pages:** Multiple architecture pages
   - **Fix:** Add real diagrams with actual module names

3. **Stub pages:** Many pages have only structure, no content
   - **Count:** ~60 pages
   - **Fix:** Prioritize based on contributor feedback

---

## Tracking Progress

### Docs Coverage Metrics

| Category | Total Pages | Completed | In Progress | Stub/Missing |
|----------|-------------|-----------|-------------|--------------|
| Overview | 4 | 3 | 1 | 0 |
| Architecture | 5 | 2 | 2 | 1 |
| Codebase Tour | 15 | 2 | 2 | 11 |
| API Reference | 45 | 1 | 3 | 41 |
| Guides | 20 | 3 | 5 | 12 |
| Total | **89** | **11** (~12%) | **13** (~15%) | **65** (~73%) |

**Goal:** 80% completion by end of Q4 2025

---

## How to Help

### For Contributors

**Pick an issue from the High Priority list above:**

1. Check the table to see what's missing
2. Assign yourself (comment on this page's PR or issue)
3. Follow the [Contributing to Docs](overview/contributing-docs.md) guide
4. Submit a PR

### For Maintainers

**Review and triage:**

- Add new issues to this page as they're discovered
- Update completion status regularly
- Prioritize based on contributor onboarding feedback

---

## Reporting New Issues

Found a gap or error in the dev docs?

1. **Quick fix?** → Edit the page directly (✏️ icon in top-right)
2. **Larger issue?** → [Open an issue](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs,dev-docs)
3. **Discussion needed?** → [Start a discussion](https://github.com/0xpix/Hei-DataHub/discussions/new?category=documentation)

**Use labels:**
- `docs` + `dev-docs` for developer documentation issues
- `good first issue` if suitable for new contributors
- `help wanted` if you can't fix it yourself

---

## Review Schedule

This page is reviewed:
- **Weekly:** by maintainers
- **Per release:** before cutting a new version
- **Per PR:** when docs are updated

---

## Success Criteria

We'll consider the dev docs "complete enough" when:

- ✅ All High Priority gaps are filled
- ✅ 80%+ of API functions have reference entries
- ✅ All guides have worked examples
- ✅ New contributors can onboard without asking for docs
- ✅ Zero broken links (automated check passes)

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 0.56.0-beta | 2025-10-06 | 🟡 In Progress | Initial dev docs site launch |

---

**Next Steps:**

1. Review [Docs Health Checklist](maintenance/health-checklist.md)
2. Check [Coverage Tracker](maintenance/coverage-tracker.md)
3. See [Contributing to Docs](overview/contributing-docs.md) to help close gaps
