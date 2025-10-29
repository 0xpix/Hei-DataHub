# Developer Documentation Site - README

> **Version:** 0.60.0-beta — "Clean-up"
> This documentation reflects the refactored architecture, improved UI polish, and codebase cleanup for Hei-DataHub.

## Overview

This is the **developer documentation site** for Hei-DataHub. It lives on the `docs/v0.60-beta-update` branch and is published independently from the user-facing documentation.

**🌐 Published Site:** https://0xpix.github.io/Hei-DataHub/dev

**📖 User Docs (separate):** https://0xpix.github.io/Hei-DataHub

---

## Purpose

This documentation is for:

- **Contributors:** Understanding architecture, APIs, and how to contribute code
- **Maintainers:** Release processes, code review standards, and maintenance procedures
- **Integrators:** Building plugins, extensions, and integrations

It is **NOT** for end users learning how to use Hei-DataHub.

---

## Repository Structure

```
dev-docs/
├── index.md                    # Homepage
├── overview/                   # Purpose, audience, compatibility
├── architecture/               # System design, module map, data flow
├── core-concepts/              # Domain model, design principles
├── codebase/                   # File-by-file tour of the entire codebase
├── api-reference/              # Function-by-function API documentation
│   ├── app/
│   ├── core/
│   ├── infra/
│   ├── services/
│   ├── ui/
│   └── cli/
├── config/                     # Configuration, environment variables
├── data/                       # Data layer, schemas, migrations
├── ui/                         # TUI architecture, views, widgets
├── extensibility/              # Plugins, adapters, extension points
├── build/                      # Build pipeline, CI/CD, releases
├── qa/                         # Testing, logging, metrics
├── performance/                # Profiling, optimization
├── security/                   # Secrets, privacy, supply chain
├── contributing/               # Contributor workflow, review standards
├── adr/                        # Architecture Decision Records
├── guides/                     # How-to guides
├── maintenance/                # Docs health, coverage tracking
├── appendices/                 # Glossary, indices, quick reference
└── assets/                     # CSS, JS, images
```

---

## Editing This Site

### Prerequisites

```bash
# Python 3.11+ required
python --version

# Install dependencies
cd /path/to/Hei-DataHub
uv sync
```

### Local Development

```bash
# Switch to the dev-docs branch
git checkout docs/v0.60-beta-update

# Serve locally (auto-reload on save)
mkdocs serve -f mkdocs-dev.yml

# Open in browser
open http://localhost:8000
```

### Build Site

```bash
# Build static site
mkdocs build -f mkdocs-dev.yml --site-dir dev-site

# Output goes to dev-site/
```

---

## Publishing

**Publishing is automated via GitHub Actions.**

Workflow: `.github/workflows/pages.yml`

**On every push to `docs/v0.60-beta-update` branch:**

1. GitHub Actions checks out the branch
2. Installs dependencies from `dev-docs/requirements.txt`
3. Builds the site with `mkdocs build -f mkdocs-dev.yml`
4. Publishes to GitHub Pages at `/x9k2m7n4p8q1/`

**Manual publish (if needed):**

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy -f mkdocs-dev.yml --remote-branch gh-pages
```

---

## Contributing to Docs

### Full Contribution Workflow

1. **Fork the repository**
2. **Create a branch:**
   ```bash
   git pull origin main
   git checkout -b feat/... OR docs/... OR fix/...
   ```
3. **Make your changes**
4. **Test locally:**
5. **Commit and push:**
   ```bash
   git add .
   git commit -m "a good commit message"
   git push origin {YOUR BRANCH}
   ```
6. **Open a PR targeting `main`**

### Commit Message Convention

Use conventional commits:

- `docs: Add API reference for X`
- `docs: Fix broken link in architecture overview`
- `docs: Update compatibility matrix for v0.56`

---

## Documentation Standards

### Every Page Must Have

- ✅ **Clear title and purpose** (first paragraph)
- ✅ **Last updated timestamp** (automated via git plugin)
- ✅ **Cross-links** to related pages
- ✅ **Code examples** where relevant
- ✅ **Diagrams** for complex topics (use Mermaid)
- ✅ **Warning/info boxes** for gotchas

### Templates

**API Reference Page:**

```markdown
# module.function

## Signature
## Purpose
## Parameters
## Returns
## Raises
## Side Effects
## Performance
## Usage Example
## See Also
```

**Guide Page:**

```markdown
# How to Do X

## Overview
## Prerequisites
## Steps
## Examples
## Common Issues
## Next Steps
```

---

## File Organization

### Naming Conventions

- **Lowercase with hyphens:** `api-reference/services/search.md`
- **Descriptive names:** `contributing-workflow.md` not `workflow.md`
- **Match code structure:** `api-reference/infra/db.md` mirrors `src/hei_datahub/infra/db.py`

### Directory Structure

- **One concept per directory:** `architecture/`, `api-reference/`, `guides/`
- **Nested by module:** `api-reference/services/search.md`
- **Avoid deep nesting:** Max 3 levels

---

## Documentation Coverage

### What We Document

| Category | Coverage Target | Current Status |
|----------|-----------------|----------------|
| Public APIs | 100% | 🟡 In Progress |
| Core modules | 100% | 🟡 In Progress |
| Architecture | 100% | 🟢 Complete |
| Guides | Key workflows | 🟡 In Progress |
| Known issues | All tracked | 🟢 Current |

See [Coverage Tracker](maintenance/coverage-tracker.md) for details.

### Adding New Modules

When adding a new module to the codebase:

1. **Update [Module Map](architecture/module-map.md)**
2. **Create API reference page** in `api-reference/`
3. **Update [Codebase Tour](codebase/navigation.md)**
4. **Add to [Coverage Tracker](maintenance/coverage-tracker.md)**

---

## Maintenance

### Regular Tasks

- **Weekly:** Check for broken links
- **Per release:** Update version banners and compatibility matrix
- **Per PR:** Update docs if code changes APIs or architecture
- **Monthly:** Review [Known Issues](known-issues.md) and resolve

### Health Checklist

See [Docs Health Checklist](maintenance/health-checklist.md) for full list.

**Quick checks:**

```bash
# Check for broken links
mkdocs build -f mkdocs-dev.yml --strict

# Validate YAML
yamllint mkdocs-dev.yml

# Check for TODOs
rg "TODO|FIXME" dev-docs/
```

---

## Versioning

This documentation is **versioned alongside the app**.

| Dev Docs Version | App Version | Branch | Status |
|------------------|-------------|--------|--------|
| **0.60.0-beta** | v0.60.x | `docs/v0.60-beta-update` | ✅ Current |
| 0.59.0-beta | v0.59.x | `renovation/dev-docs-0.57-beta` | 📦 Archived |
| 0.56.0-beta | v0.56.x | `docs/devs` | 📦 Archived |

**Switching versions:**

```bash
git checkout docs/v0.60-beta-update    # Current (v0.60)
git checkout renovation/dev-docs-0.57-beta    # Previous (v0.59)
```

---

## Troubleshooting

### Build Fails with "Configuration error"

**Cause:** Invalid `mkdocs-dev.yml`

**Fix:**

```bash
yamllint mkdocs-dev.yml
mkdocs build -f mkdocs-dev.yml --verbose
```

### Links Not Working Locally

**Cause:** Relative paths incorrect

**Fix:** Use `../` notation consistently. Test with `mkdocs serve`.

### Theme Not Loading

**Cause:** Missing plugin or extension

**Fix:**

```bash
uv sync
```

---

## CI/CD Integration

### GitHub Actions Workflow

Location: `.github/workflows/pages.yml`

**Triggers:**

- Push to `docs/v0.60-beta-update` branch
- Push to `main` branch (user docs)
- Push to `docs/update-tutorial-doc` branch (tutorial)
- Manual workflow dispatch

**Steps:**

1. Checkout respective branches
2. Install Python + dependencies
3. Build all 3 sites
4. Deploy to GitHub Pages (/, /x9k2m7n4p8q1/, /tutorial/)

**Verify workflow:**

```bash
# View workflow status
gh workflow view pages.yml

# Trigger manually
gh workflow run pages.yml
```

---

## Branching Strategy

- **`docs/v0.60-beta-update`** → Current dev docs (v0.60, publishes to /x9k2m7n4p8q1/)
- **`main`** → User docs (publishes to /)
- **`docs/update-tutorial-doc`** → Tutorial docs (publishes to /tutorial/)
- **`renovation/dev-docs-0.57-beta`** → Archived v0.59 dev docs

**Never merge dev docs branches into `main`** (they are independent sites).

---

## Changelog

Dev docs have their own changelog: [CHANGELOG.md](CHANGELOG.md)

**Update on every release:**

```markdown
## [0.60.0-beta] - 2025-10-28
### Added
- Comprehensive contribution guides for all types
- v0.60 upgrade documentation
### Fixed
- All documentation links and anchors
```

---

## Contact & Support

- **Questions?** [Start a Discussion](https://github.com/0xpix/Hei-DataHub/discussions)
- **Bug in docs?** [Open an Issue](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs)
- **Want to contribute?** See [Contributing to Docs](overview/contributing-docs.md)

---

## License

Same as main project: MIT License

---

**Happy documenting!** 📚✨
