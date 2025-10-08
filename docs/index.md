
<p align="center">
    <img src="/Hei-DataHub/assets/dark_logo_inline_v1.svg" alt="Hei-DataHub Logo" width="500"/>
</p>

# The Hei-DataHub Manual

Current version: `0.57.1-beta` (2025-10-08) — Codename: `Renovation`

---

## Welcome to Hei-DataHub

**Hei-DataHub** is a local-first TUI (Terminal User Interface) for managing datasets with consistent metadata, fast full-text search, and automated PR workflows. Think of it as a lightweight data catalog for teams who want to organize datasets without complex infrastructure.

Everything runs locally—YAML files + SQLite database—no network required except for optional GitHub integration.

## What's New in v0.57-beta 📚

**[Read the full What's New guide →](whats-new/0.57-beta.md)**

**v0.57.1-beta (Oct 8, 2025)** — Bug fix patch:
- **✅ Config reload** – Theme/keybinding changes now apply without restart
- **✅ Persistent edits** – Dataset edits now save correctly across app restarts
- **✅ Search autocomplete** – Field name suggestions now work in search

**v0.57.0-beta (Oct 6, 2025)** — Documentation overhaul:
- **📖 8 new documentation pages** – How-to guides, references, troubleshooting
- **🎨 New logo design** – Multiple variants for different use cases

## What do we have so far (v0.57.x beta)

- **🏠 Local-First:** All data stored in YAML files + SQLite—no cloud dependencies
- **🔍 Fast Search:** Full-text search powered by SQLite FTS5 with structured query parsing
- **✏️ Inline Editing:** Edit datasets directly in the TUI with undo/redo and validation
- **✅ Validated Metadata:** JSON Schema + Pydantic validation ensure consistency
- **🖥️ Clean TUI:** Terminal interface built with Textual, Neovim-style keybindings
- **📦 Simple Storage:** One folder per dataset with `metadata.yaml`
- **🔄 Automated PRs:** Save → PR workflow with GitHub integration (optional)
- **� Themeable:** 12 built-in themes with easy customization
- **⌨️ Customizable:** Configure keybindings, themes, and behavior

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

### Getting Started
1. **[Welcome](getting-started/00-welcome.md)** — What Hei-DataHub is and who it's for
2. **[Getting Started](getting-started/01-getting-started.md)** — Installation and first-run checklist
3. **[Navigation](getting-started/02-navigation.md)** — Keyboard shortcuts and workflow
4. **[The Basics](getting-started/03-the-basics.md)** — Projects, datasets, fields, search, filters

### What's New
- **[0.57-beta "Renovation"](whats-new/0.57-beta.md)** — Documentation overhaul + bug fixes (Oct 2025)

### How-to Guides
- **[GitHub Workflow Guide](how-to/04-settings.md)** — Detailed PR workflow docs
- **[Your First Dataset](how-to/05-first-dataset.md)** — Create and manage data
- **[Edit Datasets](how-to/06-edit-datasets.md)** — Change metadata inline
- **[Advanced Search](how-to/07-search-advanced.md)** — Use filters and operators
- **[Customize Keybindings](how-to/08-customize-keybindings.md)** — Remap shortcuts
- **[Change Theme](how-to/09-change-theme.md)** — Choose from 12 themes

### Reference
- **[UI Guide](reference/10-ui.md)** — TUI structure, panels, status area
- **[Data & SQL](reference/11-data-and-sql.md)** — Data location, schemas, query patterns
- **[Configuration](reference/12-config.md)** — Config file, environment variables, examples
- **[Search Syntax](reference/search-syntax.md)** — Complete query reference
- **[Keybindings](reference/keybindings.md)** — All shortcuts listed (coming soon)

### Help
- **[FAQ](help/90-faq.md)** — Quick answers to common questions
- **[Troubleshooting](help/troubleshooting.md)** — Known issues and fixes

---

## Getting Help

- **Search:** Use the search bar at the top of this site
- **FAQ:** Check [FAQ & Troubleshooting](help/90-faq.md) for common issues
- **Issues:** File bugs or feature requests at [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)

---

## License

Hei-DataHub is released under the [MIT License](https://github.com/0xpix/Hei-DataHub/blob/main/LICENSE).
