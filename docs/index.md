
<p align="center">
    <img src="/Hei-DataHub/assets/dark_logo_inline_v1.svg" alt="Hei-DataHub Logo" width="300"/>
</p>

# The Hei-DataHub Manual

Current version: `0.57.0-beta` (2025-10-06) — Codename: `Renovation`

---

## Welcome to Hei-DataHub

**Hei-DataHub** is a local-first TUI (Terminal User Interface) for managing datasets with consistent metadata, fast full-text search, and automated PR workflows. Think of it as a lightweight data catalog for teams who want to organize datasets without complex infrastructure.

Everything runs locally—YAML files + SQLite database—no network required except for optional GitHub integration.

## What's New in v0.57 📚

**[Read the full What's New guide →](whats-new/0.57-beta.md)**

v0.57.0-beta is a **documentation-only release**—no new features, just complete documentation for everything released in v0.56.0-beta:

- **📖 8 new documentation pages** – How-to guides, references, troubleshooting
- **✏️ Inline editing guide** – Step-by-step dataset editing instructions
- **🔍 Search syntax reference** – Complete field filter grammar
- **⌨️ Keybindings reference** – All shortcuts by mode (including Edit Mode)
- **🎨 Theme customization guide** – All 12 themes documented
- **⚠️ Known issues documented** – 8 known bugs with workarounds
- **❓ Expanded FAQ** – 8 new entries for v0.56 features

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
1. **[Welcome](00-welcome.md)** — What Hei-DataHub is and who it's for
2. **[Getting Started](01-getting-started.md)** — Installation and first-run checklist
3. **[Navigation](02-navigation.md)** — Keyboard shortcuts and workflow
4. **[The Basics](03-the-basics.md)** — Projects, datasets, fields, search, filters

### What's New
- **[0.57-beta "Renovation"](whats-new/0.57-beta.md)** — Latest features and improvements

### How-to Guides
- **[Edit Datasets](how-to/edit-datasets.md)** — Change metadata inline
- **[Advanced Search](how-to/search-advanced.md)** — Use filters and operators
- **[Customize Keybindings](how-to/customize-keybindings.md)** — Remap shortcuts
- **[Change Theme](how-to/change-theme.md)** — Choose from 12 themes
- **[Installation](how-to/01-installation.md)** — Step-by-step setup
- **[Your First Dataset](how-to/02-first-dataset.md)** — Create and manage data
- **[Search & Filters](how-to/03-search-and-filters.md)** — Find datasets fast

### Reference
- **[UI Guide](10-ui.md)** — TUI structure, panels, status area
- **[Data & SQL](11-data-and-sql.md)** — Data location, schemas, query patterns
- **[Configuration](12-config.md)** — Config file, environment variables, examples
- **[Search Syntax](reference/search-syntax.md)** — Complete query reference
- **[Keybindings](reference/keybindings.md)** — All shortcuts listed (coming soon)

### Help
- **[FAQ](90-faq.md)** — Quick answers to common questions
- **[Troubleshooting](troubleshooting.md)** — Known issues and fixes
- **[What's New](whats-new/0.57-beta.md)** — Latest features and improvements

---

## Getting Help

- **Search:** Use the search bar at the top of this site
- **FAQ:** Check [FAQ & Troubleshooting](90-faq.md) for common issues
- **Issues:** File bugs or feature requests at [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)

---

## License

Hei-DataHub is released under the [MIT License](https://github.com/0xpix/Hei-DataHub/blob/main/LICENSE).
