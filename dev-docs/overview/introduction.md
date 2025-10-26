# Introduction to Developer Documentation

## Purpose

This developer documentation site exists to **demystify the internals** of Hei-DataHub for anyone who needs to understand, modify, extend, or maintain the codebase.

Unlike the [user manual](https://0xpix.github.io/Hei-DataHub) which focuses on *using* the tool, this site focuses on *building* and *evolving* the tool.

---

## Why a Separate Developer Site?

### The Problem

Mixing user-facing documentation with deep technical internals creates confusion:

- **Users** get overwhelmed with implementation details they don't need
- **Developers** can't find architectural context buried among tutorials
- **Documentation drift:** Technical docs lag behind code changes when mixed with stable user docs
- **Publishing conflicts:** User docs need stability; developer docs need frequent iteration

### The Solution

Two independent documentation sites with clear boundaries:

| Aspect | User Docs | Developer Docs |
|--------|-----------|----------------|
| **Audience** | End users, analysts, admins | Contributors, maintainers, integrators |
| **Content** | Features, tutorials, UI guides | Architecture, APIs, internals |
| **Branch** | `main` | `docs/devs` |
| **Update Frequency** | Stable releases | Continuous (every commit) |
| **Publishing** | GitHub Pages from `main` | GitHub Pages from `docs/devs` |
| **Config File** | `mkdocs.yml` | `mkdocs-dev.yml` |

---

## What This Site Covers

### ✅ In Scope

- **Architecture:** System design, module boundaries, data flow
- **Codebase tour:** Every file, every function, every extension point
- **API reference:** Signatures, parameters, return types, side effects, errors
- **Development workflows:** Setup, testing, debugging, profiling
- **Contribution guidelines:** How to submit code, review standards, DoD
- **Release process:** Versioning, changelogs, CI/CD, deployment
- **Configuration internals:** Where settings live, precedence rules, defaults
- **Data layer details:** Schemas, migrations, indexing, performance
- **UI/TUI internals:** View lifecycle, state management, rendering pipeline
- **Extensibility:** Official extension points, plugin architecture
- **Quality standards:** Testing strategy, logging, metrics, coverage
- **Performance:** Hotspots, profiling, optimization playbooks
- **Security:** Secrets handling, data privacy, supply chain

### ❌ Out of Scope (See User Docs Instead)

- How to install Hei-DataHub as an end user
- How to search datasets using the TUI
- Tutorial: "Your first dataset"
- Keyboard shortcuts from a user perspective
- Troubleshooting common user issues
- Feature announcements and release notes for users

---

## Documentation Philosophy

### Principles We Follow

1. **Explain, Don't Just Reference**
   - Bad: "See `db.py` for database logic"
   - Good: "`db.py` manages SQLite connections using a singleton pattern. It exposes `get_connection()` which lazily initializes the connection on first call..."

2. **Show the Why, Not Just the What**
   - Document *decisions* and *tradeoffs*, not just APIs
   - Link to ADRs (Architecture Decision Records) for context

3. **Keep It Current**
   - Docs are code. Outdated docs are worse than no docs.
   - Every feature PR must update relevant docs sections.

4. **Progressive Disclosure**
   - Start with high-level overviews
   - Drill down into details as needed
   - Use collapsible sections for deep dives

5. **Examples Over Abstractions**
   - Show real code snippets
   - Walk through actual data flows
   - Include diagrams for complex interactions

6. **Consistency in Templates**
   - Every API entry follows the same structure
   - Every module page has the same sections
   - Predictable navigation reduces cognitive load

---

## Documentation Structure

### Top-Level Navigation

```
Developer Docs
├── Overview (you are here)
│   ├── Introduction
│   ├── Audience & Scope
│   ├── Version Compatibility
│   └── Contributing to Docs
├── Architecture
│   ├── System Overview
│   ├── Module Map
│   ├── Data Flow
│   └── Dependency Graph
├── Core Concepts
│   ├── What is "Core"?
│   ├── Platform Constraints
│   └── Domain Model
├── Codebase Tour
│   ├── Every file explained
│   └── Extension points highlighted
├── API Reference
│   ├── Function-by-function entries
│   └── Signatures, errors, performance
├── Configuration
├── Data Layer
├── UI/TUI Layer
├── Extensibility
├── Build & Release
├── Quality Assurance
├── Performance
├── Security
├── Contributing
├── Decisions & Roadmap (ADRs)
├── Known Issues
└── Maintenance
```

### Page Templates

Each major section follows a consistent template:

**Module/API Pages:**
```markdown
# Module Name

## Purpose
## Location
## Dependencies
## Public API
  - Function signatures
  - Parameters & return types
  - Errors raised
  - Performance notes
## Usage Examples
## Extension Points
## Common Pitfalls
## Related Modules
## Tests
```

**Guide Pages:**
```markdown
# Guide Title

## Overview
## Prerequisites
## Step-by-Step Instructions
## Examples
## Common Issues & Solutions
## Next Steps
```

---

## How to Navigate This Site

### For First-Time Contributors

**Recommended path (15-20 minutes):**

1. [System Overview](../architecture/overview.md) — Understand the big picture
2. [Module Map](../architecture/module-map.md) — Learn where things live
3. [Data Flow](../architecture/data-flow.md) — Trace how data moves
4. [Contributor Workflow](../contributing/workflow.md) — Learn the process

Then dive into the specific module you're working on.

### For Experienced Contributors

Use the search bar (top right) or jump directly to:

- [API Reference](../api-reference/overview.md) for function signatures
- [Codebase Overview](../codebase/overview.md) to find a specific file
- [Performance](../performance/overview.md) when optimizing
- [Known Issues](../known-issues.md) before starting work

### For Maintainers

Essential pages to bookmark:

- [Release Process](../build/releases.md)
- [Changelog Policy](../build/changelog.md)
- [Code Review Guide](../contributing/code-review.md)
- [Definition of Done](../contributing/definition-of-done.md)
- [Docs Health Checklist](../maintenance/health-checklist.md)

---

## Version Compatibility

This documentation site is **versioned alongside the app**.

| **Current Docs Version** | **Compatible With** | **Branch** |
|--------------------------|---------------------|------------|
| **0.56.0-beta "Precision"** | App v0.56.x | `docs/devs` |

### What This Means

- If you're working on **v0.56.x code**, these docs are accurate
- If you're on a different version, switch branches:
  ```bash
  git checkout docs/devs-v0.55  # (if available)
  ```
- Version mismatch? → Check [Compatibility Matrix](compatibility.md)

---

## Who Maintains This Site?

This documentation is a **community effort**.

- **Primary maintainers:** Core team members
- **Contributors:** Anyone who submits a PR
- **Ownership model:** Each module's docs are maintained by that module's code owners

### Maintenance Responsibilities

- **Code authors:** Update docs when changing APIs
- **Reviewers:** Verify docs are updated in PRs
- **Release managers:** Update version banners and compatibility notes
- **Everyone:** Flag gaps in [Known Issues](../known-issues.md)

---

## Quality Standards

### Every Page Should Have

- ✅ **Clear purpose statement** at the top
- ✅ **Last updated timestamp** (automated via git plugin)
- ✅ **Related pages** cross-linked
- ✅ **Code examples** where relevant
- ✅ **Diagrams** for complex topics
- ✅ **Warning blocks** for gotchas

### We Avoid

- ❌ Stubs ("TODO: Fill this in later")
- ❌ Copy-pasted docstrings without context
- ❌ Broken links
- ❌ Outdated examples
- ❌ Jargon without explanation

---

## Contributing to This Site

See [Contributing to Docs](contributing-docs.md) for the full guide.

Quick start:

1. **Found a typo?** → Click the ✏️ edit icon (top-right of any page)
2. **Missing information?** → [Open an issue](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs)
3. **Want to add a section?** → Submit a PR targeting `docs/devs` branch

---

## Feedback & Questions

- **Something unclear?** → [Start a discussion](https://github.com/0xpix/Hei-DataHub/discussions)
- **Docs bug?** → [Report it](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs,bug)
- **Suggestion?** → [Feature request](https://github.com/0xpix/Hei-DataHub/issues/new?labels=docs,enhancement)

---

**Next:** [Audience & Scope](audience.md) →
