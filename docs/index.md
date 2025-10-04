# The Hei-DataHub Manual (v0.55.x beta)

<!-- Version banner - Auto-generated from version.yaml -->
{% include "version.md" %}

---

## Welcome to Hei-DataHub

**Hei-DataHub** is a local-first TUI (Terminal User Interface) for managing datasets with consistent metadata, fast full-text search, and automated PR workflows. Think of it as a lightweight data catalog for teams who want to organize datasets without complex infrastructure.

Everything runs locally—YAML files + SQLite database—no network required except for optional GitHub integration.

## What's in the Box (v0.55.x beta)

- **🏠 Local-First:** All data stored in YAML files + SQLite—no cloud dependencies
- **🔍 Fast Search:** Full-text search powered by SQLite FTS5 with BM25 ranking
- **✅ Validated Metadata:** JSON Schema + Pydantic validation ensure consistency
- **🖥️ Clean TUI:** Terminal interface built with Textual, Neovim-style keybindings
- **📦 Simple Storage:** One folder per dataset with `metadata.yaml`
- **🔄 Automated PRs:** Save → PR workflow with GitHub integration (optional)
- **🎯 Auto-Stash:** Automatically handles uncommitted changes during PR workflow
- **🏗️ Clean Architecture:** Layered design with clear separation of concerns

---

## Commands at a Glance

```bash
# Launch the TUI (use either command)
hei-datahub

# Reindex from YAML files
hei-datahub reindex

# Show version
hei-datahub --version
hei-datahub --version-info  # Detailed information
```

---

## Documentation Structure

This manual is organized to get you productive quickly:

1. **[Welcome](00-welcome.md)** — What Hei-DataHub is and who it's for
2. **[Getting Started](01-getting-started.md)** — Installation and first-run checklist
3. **[Navigation](02-navigation.md)** — Keyboard shortcuts and workflow
4. **[The Basics](03-the-basics.md)** — Projects, datasets, fields, search, filters
5. **[UI Guide](10-ui.md)** — TUI structure, panels, status area, customization
6. **[Data & SQL](11-data-and-sql.md)** — Data location, schemas, query patterns
7. **[Configuration](12-config.md)** — Config file, environment variables, examples
8. **[Tutorials](20-tutorials/01-installation.md)** — Step-by-step walkthroughs
9. **[FAQ](90-faq.md)** — Common issues and troubleshooting
10. **[Versioning](98-versioning.md)** — SemVer explained and release policy
11. **[Changelog](99-changelog.md)** — What's new in each release

---

## Getting Help

- **Search:** Use the search bar at the top of this site
- **FAQ:** Check [FAQ & Troubleshooting](90-faq.md) for common issues
- **Issues:** File bugs or feature requests at [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Edit This Page:** Use the edit icon (✏️) to suggest improvements

---

## License

Hei-DataHub is released under the [MIT License](https://github.com/0xpix/Hei-DataHub/blob/main/LICENSE).
