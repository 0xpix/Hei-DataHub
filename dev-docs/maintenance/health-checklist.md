# Docs Health Checklist

## Purpose

This checklist ensures the developer documentation stays **accurate, complete, and maintainable**. Use it for:

- **Weekly reviews** by maintainers
- **Pre-release checks** before cutting a new version
- **PR reviews** when docs are updated
- **Quarterly audits** to catch drift

---

## Quick Health Check

Run these commands to catch common issues:

```bash
# 1. Check for broken links
mkdocs build -f mkdocs-dev.yml --strict

# 2. Find TODOs and FIXMEs
rg "TODO|FIXME" dev-docs/

# 3. Validate YAML
yamllint mkdocs-dev.yml

# 4. Check for missing navigation entries
diff <(find dev-docs -name "*.md" | sort) \
     <(grep -r "\.md" mkdocs-dev.yml | sort)

# 5. Find pages without cross-links
for file in dev-docs/**/*.md; do
    if ! grep -q "\[.*\](.*\.md)" "$file"; then
        echo "No links: $file"
    fi
done
```

---

## Detailed Checklist

### ✅ Content Accuracy

- [ ] **All code examples are tested and working**
  - Run each example to verify it works
  - Update examples that reference old APIs
  - Add version compatibility notes

- [ ] **Function signatures match actual code**
  - Compare API docs to source code
  - Check parameter types and defaults
  - Verify return types

- [ ] **Architecture diagrams reflect current structure**
  - Review module map for new/removed modules
  - Update data flow diagrams if logic changed
  - Check dependency graph for new deps

- [ ] **Version numbers are current**
  - Update compatibility matrix
  - Update version banners on pages
  - Check changelog for completeness

---

### 📚 Completeness

- [ ] **All public APIs documented**
  - Check [Coverage Tracker](coverage-tracker.md)
  - Document new functions added in PRs
  - Mark deprecated APIs clearly

- [ ] **All modules have overview pages**
  - Check [Module Map](../architecture/module-map.md)
  - Add pages for new modules
  - Archive pages for removed modules

- [ ] **All guides have working examples**
  - Verify examples execute without errors
  - Add missing examples
  - Remove outdated examples

- [ ] **All known issues are tracked**
  - Review [Known Issues](../known-issues.md)
  - Close resolved issues
  - Add new issues discovered

---

### 🔗 Navigation & Links

- [ ] **All internal links work**
  - Run `mkdocs build --strict` to catch broken links
  - Fix relative path errors
  - Update links when pages move

- [ ] **All pages are in navigation**
  - Check `mkdocs-dev.yml` nav section
  - Add missing pages
  - Remove orphaned entries

- [ ] **Cross-links are bidirectional**
  - If page A links to B, B should link back to A (when relevant)
  - Add "See also" sections
  - Link related concepts

- [ ] **External links are valid**
  - Check links to GitHub, external docs
  - Update links to moved resources
  - Add archive.org links for deprecated resources

---

### 📝 Formatting & Style

- [ ] **Markdown is valid**
  - No unclosed code blocks
  - No broken tables
  - No malformed lists

- [ ] **Code blocks have syntax highlighting**
  - Add language tags: ```python
  - Use consistent indentation
  - Remove commented-out code

- [ ] **Headers follow hierarchy**
  - One H1 per page
  - No skipped levels (H1 → H3)
  - Descriptive titles

- [ ] **Lists are formatted consistently**
  - Use `-` for unordered lists
  - Use `1.` for ordered lists
  - Indent nested lists properly

---

### 🧪 Technical Correctness

- [ ] **Error handling examples are complete**
  - Show try/except blocks
  - Document all raised exceptions
  - Provide recovery strategies

- [ ] **Performance notes are accurate**
  - Update Big-O complexity if algorithms changed
  - Verify latency claims
  - Update bottleneck descriptions

- [ ] **Security notes are up to date**
  - Review secrets handling
  - Check for hardcoded credentials in examples
  - Verify encryption recommendations

---

### 🔄 Maintenance

- [ ] **Changelog is up to date**
  - Check [CHANGELOG.md](../CHANGELOG.md)
  - Add entries for all changes
  - Follow changelog format

- [ ] **Coverage tracker is current**
  - Update [Coverage Tracker](coverage-tracker.md)
  - Mark completed pages
  - Add new pages to tracker

- [ ] **ADRs reflect current decisions**
  - Review [ADRs](../adr/index.md)
  - Mark superseded ADRs
  - Add new ADRs for major decisions

- [ ] **Known issues are triaged**
  - Prioritize [Known Issues](../known-issues.md)
  - Assign owners
  - Set target resolution dates

---

## Weekly Review Tasks

Run these checks every week:

### Monday: Link Check
```bash
mkdocs build -f mkdocs-dev.yml --strict
```

### Wednesday: Content Review
- Review 5 random pages for accuracy
- Check for outdated examples
- Update version notes if needed

### Friday: Coverage Check
- Review [Coverage Tracker](coverage-tracker.md)
- Assign one missing page to write
- Close completed items

---

## Pre-Release Checklist

Before cutting a new release:

- [ ] **Update version compatibility matrix**
  - Update [Compatibility](../overview/compatibility.md)
  - Update version banners site-wide
  - Update `mkdocs-dev.yml` site version

- [ ] **Review breaking changes**
  - Document API changes in affected pages
  - Add deprecation warnings
  - Update migration guides

- [ ] **Update changelog**
  - Finalize [CHANGELOG.md](../CHANGELOG.md)
  - Move "Unreleased" to new version
  - Add release date

- [ ] **Build and test locally**
  ```bash
  mkdocs build -f mkdocs-dev.yml --strict
  ```

- [ ] **Push to dev-docs branch**
  ```bash
  git checkout docs/devs
  git add dev-docs/
  git commit -m "docs: prepare for v0.XX.0 release"
  git push origin docs/devs
  ```

---

## Quarterly Audit

Every 3 months, run a comprehensive audit:

### 1. Content Accuracy Audit
- Review all architecture diagrams
- Verify all code examples
- Check all API signatures
- Update performance benchmarks

### 2. Completeness Audit
- Check API coverage: Are all public functions documented?
- Check guide coverage: Are all common workflows documented?
- Check troubleshooting: Are all common issues documented?

### 3. Style Consistency Audit
- Check formatting consistency
- Verify voice and tone
- Ensure templates are followed

### 4. User Feedback Review
- Review GitHub issues tagged `docs`
- Review discussions about documentation
- Survey contributors about docs quality

---

## Automated Checks (CI)

Our CI pipeline runs these checks on every PR:

- ✅ **MkDocs build passes** (`mkdocs build --strict`)
- ✅ **YAML is valid** (`yamllint`)
- ✅ **No TODOs in merged docs** (grep check)
- ✅ **Changelog updated** (if code changed)
- ✅ **Version consistency** (all version strings match)

---

## Health Metrics

Track these metrics monthly:

| Metric | Target | Current |
|--------|--------|---------|
| **API Coverage** | >90% | 🟡 15% |
| **Broken Links** | 0 | 🟢 0 |
| **Outdated Pages** | <10% | 🟡 Unknown |
| **Time to Find Info** | <5 min | 🟡 Unknown |
| **Contributor Onboarding** | <30 min | 🔴 Unknown |

**Status:**
- 🟢 Green: Meeting target
- 🟡 Yellow: Needs improvement
- 🔴 Red: Urgent action needed

---

## Common Issues and Fixes

### Issue: Broken Links After Refactoring

**Symptom:** `mkdocs build --strict` fails with "Page not found"

**Fix:**
1. Find broken links: `mkdocs build -f mkdocs-dev.yml --strict`
2. Use search and replace to update all occurrences
3. Test: `mkdocs serve -f mkdocs-dev.yml`

### Issue: Outdated Code Examples

**Symptom:** Examples don't work anymore

**Fix:**
1. Find all code blocks: `rg '```python' dev-docs/`
2. Test each example
3. Update or remove broken examples
4. Add version compatibility notes

### Issue: Missing Cross-Links

**Symptom:** Pages feel isolated

**Fix:**
1. Add "See Also" section to every page
2. Link related concepts
3. Link to parent/child pages
4. Link to API references from guides

---

## Tools and Resources

### Helpful Commands

```bash
# Find large pages (>500 lines)
find dev-docs -name "*.md" -exec wc -l {} \; | sort -rn | head -10

# Find pages with no code examples
for file in dev-docs/**/*.md; do
    if ! grep -q '```' "$file"; then
        echo "No examples: $file"
    fi
done

# List all external links
rg 'https?://' dev-docs/ --no-filename | sort -u

# Find pages without "See Also" section
for file in dev-docs/**/*.md; do
    if ! grep -qi "see also" "$file"; then
        echo "No 'See Also': $file"
    fi
done
```

### Useful MkDocs Plugins

- `mkdocs-git-revision-date-localized-plugin`: Show last modified date
- `mkdocs-minify-plugin`: Minify HTML/CSS/JS
- `mkdocs-mermaid2-plugin`: Render Mermaid diagrams

---

## Assigning Ownership

Each section of the docs should have an owner:

| Section | Owner | Backup |
|---------|-------|--------|
| Overview | Maintainers | Contributors |
| Architecture | Core Team | Maintainers |
| API Reference | Code Authors | Maintainers |
| Guides | Contributors | Maintainers |
| ADRs | Core Team | - |
| Known Issues | Maintainers | - |

---

## Questions?

- **How often should I run this checklist?** → At least weekly (quick check), monthly (detailed), quarterly (full audit)
- **What if I find issues?** → [Open an issue](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs) or fix it yourself
- **Who is responsible?** → Everyone! But maintainers are ultimately accountable

---

## Next Steps

- Review [Coverage Tracker](coverage-tracker.md) for gaps
- Check [Known Issues](../known-issues.md) for priorities
- See [Contributing to Docs](../overview/contributing-docs.md) to help improve docs

---

**Last Audit:** 2025-10-06  
**Next Audit:** 2026-01-06
