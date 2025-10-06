# Contributing to Developer Documentation

## Overview

This developer documentation site is a **living document** maintained by the community. Your contributions help make Hei-DataHub more accessible to contributors, maintainers, and integrators.

---

## Why Contribute to Docs?

- ✅ **Help future you:** Document what you learned so you don't forget
- ✅ **Onboard others faster:** Clear docs reduce questions
- ✅ **Improve code quality:** Writing docs reveals design issues
- ✅ **Build reputation:** Good docs are as valuable as good code

---

## What Needs Documentation?

### High Priority

1. **Missing API references** — See [Known Issues](../known-issues.md#missing-api-references)
2. **Incomplete guides** — How-tos for common tasks
3. **Missing diagrams** — Architecture visualizations
4. **Outdated examples** — Code snippets that don't work

### Medium Priority

5. **Cross-links** — Connect related pages
6. **Glossary entries** — Define project-specific terms
7. **Performance notes** — Document hotspots and optimizations
8. **Test examples** — Show how to test specific modules

### Low Priority (Nice-to-Have)

9. **Video walkthroughs** — Screencasts of complex workflows
10. **Interactive examples** — Runnable code snippets
11. **Translations** — Non-English documentation

---

## Quick Contribution Paths

### Path 1: Fix a Typo (2 minutes)

1. Click the **✏️ Edit icon** (top-right of any page)
2. Make your change on GitHub
3. Submit a PR (auto-created)

### Path 2: Improve a Page (15 minutes)

1. Open the page in your IDE
2. Add missing information, examples, or diagrams
3. Test locally: `mkdocs serve -f mkdocs-dev.yml`
4. Commit and push
5. Open a PR

### Path 3: Add a New Page (1-2 hours)

1. Follow [Full Contribution Workflow](#full-workflow) below
2. Create the page with proper structure
3. Add to navigation in `mkdocs-dev.yml`
4. Cross-link from related pages
5. Update [Coverage Tracker](../maintenance/coverage-tracker.md)

---

## Full Workflow

### Step 1: Set Up Local Environment

```bash
# Clone the repository (if not already)
git clone https://github.com/YOUR_USERNAME/Hei-DataHub.git
cd Hei-DataHub

# Checkout the dev-docs branch
git checkout docs/devs
git pull origin docs/devs

# Install docs dependencies
pip install -r dev-docs/requirements.txt

# Verify setup
mkdocs serve -f mkdocs-dev.yml
# Open http://localhost:8000
```

### Step 2: Create a Branch

```bash
# Create a feature branch
git checkout -b docs/add-search-api-reference

# Verify you're on the right branch
git branch
# * docs/add-search-api-reference
#   docs/devs
```

### Step 3: Make Changes

#### For API Reference Pages

Use this template:

```markdown
# module.function_name

**Module:** `mini_datahub.services.search`  
**Added in:** v0.56.0  
**Status:** ✅ Stable

---

## Signature

\`\`\`python
def search_datasets(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
) -> List[Dataset]:
    """
    Search datasets using FTS5 full-text search.
    
    Args:
        query: Search query string (FTS5 syntax)
        filters: Optional filters (tags, date range, etc.)
        limit: Maximum number of results
    
    Returns:
        List of matching datasets, sorted by relevance
        
    Raises:
        SearchError: If query syntax is invalid
        DatabaseError: If database connection fails
    """
\`\`\`

---

## Purpose

Brief description of what this function does and when to use it.

---

## Parameters

### `query: str`

- **Required:** Yes
- **Description:** Search query in FTS5 syntax
- **Example:** `"precipitation OR rainfall"`
- **Validation:** Must not be empty

### `filters: Optional[Dict[str, Any]]`

- **Required:** No
- **Default:** `None`
- **Description:** Additional filters to apply
- **Allowed keys:**
  - `tags: List[str]` — Filter by tags
  - `date_range: Tuple[date, date]` — Filter by date
- **Example:** `{"tags": ["climate", "weather"]}`

### `limit: int`

- **Required:** No
- **Default:** `100`
- **Description:** Maximum number of results
- **Range:** `1` to `1000`

---

## Returns

**Type:** `List[Dataset]`

**Description:** List of datasets matching the query, sorted by relevance score (descending).

**Empty case:** Returns `[]` if no matches found.

---

## Raises

### `SearchError`

**When:** Query syntax is invalid (e.g., unmatched quotes)

**Example:**
\`\`\`python
try:
    results = search_datasets('invalid: query:')
except SearchError as e:
    print(f"Invalid query: {e}")
\`\`\`

### `DatabaseError`

**When:** Database connection fails or FTS5 index is corrupted

**Recovery:** Reindex the database with `hei-datahub reindex`

---

## Side Effects

- Reads from SQLite database (no writes)
- May trigger FTS5 index optimization if table is large

---

## Performance

- **Typical latency:** <10ms for 1000s of datasets
- **Complexity:** O(log n) due to FTS5 index
- **Memory:** O(k) where k = number of results
- **Bottleneck:** Network I/O if database is on NFS

**Optimization tip:** Use `limit` to reduce memory usage

---

## Usage Examples

### Basic Search

\`\`\`python
from mini_datahub.services import search

results = search.search_datasets("climate data")
for dataset in results:
    print(f"{dataset.name}: {dataset.title}")
\`\`\`

### Search with Filters

\`\`\`python
results = search.search_datasets(
    query="precipitation",
    filters={"tags": ["climate"]},
    limit=50
)
\`\`\`

### Handling Errors

\`\`\`python
try:
    results = search.search_datasets(user_query)
except search.SearchError:
    print("Invalid query syntax")
except search.DatabaseError:
    print("Database error - try reindexing")
\`\`\`

---

## See Also

- [FTS5 Documentation](https://www.sqlite.org/fts5.html)
- [Query DSL](../../core-concepts/query-dsl.md)
- [Indexing Strategy](../../data/indexing.md)
- [services.catalog](../services/catalog.md)

---

## Notes

- Uses SQLite FTS5 extension (must be compiled in)
- Query syntax: See [FTS5 docs](https://www.sqlite.org/fts5.html#full_text_query_syntax)
- Results are cached in memory for repeated queries

---

## History

| Version | Change |
|---------|--------|
| v0.56.0 | Added `filters` parameter |
| v0.55.0 | Initial implementation |
```

#### For Guide Pages

Use this template:

```markdown
# How to Do X

## Overview

Brief description of what this guide teaches.

## Prerequisites

- What you need before starting
- Links to setup guides

## Steps

### Step 1: First Action

Description and example.

### Step 2: Next Action

Description and example.

## Complete Example

Full working example.

## Common Issues

### Issue 1

**Symptom:**  
**Cause:**  
**Solution:**

## Next Steps

- Related guides
- Further reading
```

### Step 4: Test Locally

```bash
# Serve and preview
mkdocs serve -f mkdocs-dev.yml

# Check for broken links
mkdocs build -f mkdocs-dev.yml --strict

# Look for common issues
grep -r "TODO" dev-docs/
grep -r "FIXME" dev-docs/
```

### Step 5: Update Navigation

If adding a new page, update `mkdocs-dev.yml`:

```yaml
nav:
  - API Reference:
    - services Module:
      - search: api-reference/services/search.md
      - catalog: api-reference/services/catalog.md
      - publish: api-reference/services/publish.md  # <-- Add here
```

### Step 6: Cross-Link

Add links from related pages:

```markdown
See also: [services.publish](../api-reference/services/publish.md)
```

### Step 7: Update Coverage Tracker

Add to [Coverage Tracker](../maintenance/coverage-tracker.md):

```markdown
| services.publish | ✅ Complete | 2025-10-06 |
```

### Step 8: Commit and Push

```bash
# Stage changes
git add dev-docs/

# Commit with conventional commit message
git commit -m "docs(api): add reference for services.publish"

# Push to your fork
git push origin docs/add-search-api-reference
```

### Step 9: Open a Pull Request

1. Go to [github.com/0xpix/Hei-DataHub/pulls](https://github.com/0xpix/Hei-DataHub/pulls)
2. Click **New Pull Request**
3. Select:
   - Base: `docs/devs`
   - Compare: `docs/add-search-api-reference`
4. Fill out PR template (see below)
5. Submit

---

## PR Template for Docs

```markdown
## What

Added API reference for `services.publish` module.

## Why

This module was undocumented, making it hard for contributors to understand
how the PR publishing workflow works.

## Changes

- Added `api-reference/services/publish.md` with full function signatures
- Added usage examples for `publish_dataset()`
- Updated navigation in `mkdocs-dev.yml`
- Cross-linked from `architecture/data-flow.md`
- Updated coverage tracker

## Checklist

- [x] Tested locally with `mkdocs serve`
- [x] No broken links (`mkdocs build --strict`)
- [x] Added to navigation
- [x] Cross-linked from related pages
- [x] Updated coverage tracker
- [x] Followed template structure

## Preview

(Optional: Add screenshots of rendered page)
```

---

## Review Process

### What Reviewers Check

- ✅ **Accuracy:** Is the information correct?
- ✅ **Completeness:** Are all sections filled out?
- ✅ **Clarity:** Is it easy to understand?
- ✅ **Examples:** Are there working examples?
- ✅ **Links:** Do all links work?
- ✅ **Formatting:** Is Markdown valid?

### Response Time

- **Simple fixes:** 1-2 days
- **New pages:** 3-5 days
- **Large additions:** 1 week

### Addressing Feedback

```bash
# Make requested changes
git checkout docs/add-search-api-reference

# Edit files
# Commit
git commit -m "docs: address review feedback"

# Push (PR auto-updates)
git push origin docs/add-search-api-reference
```

---

## Style Guide

### Voice and Tone

- **Active voice:** "We use FTS5" (not "FTS5 is used")
- **Present tense:** "The function returns..." (not "will return")
- **Direct:** "You should..." (not "One should...")
- **Friendly but professional:** Avoid jargon, explain acronyms

### Formatting

- **Headings:** Use Title Case for H1, Sentence case for others
- **Code:** Use `backticks` for inline code, triple backticks for blocks
- **Emphasis:** Use **bold** for important terms, *italic* for emphasis
- **Lists:** Use `-` for unordered, `1.` for ordered

### Code Examples

- Always use syntax highlighting: ```python
- Show imports: `from mini_datahub.services import search`
- Use real, working code (not pseudocode)
- Add comments to explain non-obvious parts

### Diagrams

- Use Mermaid for flowcharts, sequence diagrams, class diagrams
- Use ASCII art for simple diagrams
- Use images for complex diagrams (store in `dev-docs/assets/`)

---

## Common Mistakes

### ❌ Don't Do This

**Incomplete API reference:**
```markdown
# search_datasets

This function searches datasets.
```

**No examples:**
```markdown
Use `search_datasets()` to search.
```

**Broken links:**
```markdown
See [this page](../some-page-that-doesnt-exist.md)
```

### ✅ Do This Instead

**Complete API reference:**
```markdown
# search_datasets

## Signature
\`\`\`python
def search_datasets(query: str) -> List[Dataset]:
\`\`\`

## Purpose
Searches datasets using FTS5 full-text search...

## Parameters
...

## Returns
...

## Examples
...
```

---

## Getting Help

- **Not sure what to document?** → Check [Known Issues](../known-issues.md)
- **Don't know the details?** → Ask in [Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
- **Stuck on formatting?** → See [MkDocs Material Reference](https://squidfunk.github.io/mkdocs-material/reference/)

---

## Recognition

All contributors are recognized in:

- **Git history:** Your commits are永久 preserved
- **GitHub Contributors graph:** Visible on repository
- **This page:** Thank you! 🙏

---

**Ready to contribute?** Pick an issue from [Known Issues](../known-issues.md) and get started!
