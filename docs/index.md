
<p align="center">
    <img src="/Hei-DataHub/assets/Hei-datahub_logo_inline.svg" alt="Hei-DataHub Logo" width="500"/>
</p>

# The Hei-DataHub Manual

Current version: `{{ project_version }}` (Oct 25, 2025) — Codename: `{{ project_codename }}`

---

## Welcome to Hei-DataHub

**Hei-DataHub** is a local-first TUI (Terminal User Interface) for managing datasets with consistent metadata, fast full-text search, and automated PR workflows. Think of it as a lightweight data catalog for teams who want to organize datasets without complex infrastructure.

Everything runs locally—YAML files + SQLite database—no network required except for optional GitHub integration.

## What's New in v0.59-beta 📚

**[Read the full What's New guide →](whats-new/0.59-beta.md)**

## [0.59.0-beta] - Oct 25, 2025 - "Privacy" release

- **UV-Based Install\Update** — Direct from GitHub—no cloning required
- **Ephemeral Runs** — Test with `uvx` before installing
- **Enhanced CLI** — `hei-datahub update`, `hei-datahub --version-info`, etc.
- **Version Control** — Pin to specific tags, branches, or commits
- **Complete Packaging** — All assets and data files included automatically
- **Health Checks** — `hei-datahub doctor` command for diagnostics
- **Directory Control** — `--data-dir` flag and environment variable support
- **XDG Compliance** — Follows Linux desktop standards

## What do we have so far (v0.59.x beta)

- **Uv -Based Install/Update:** Directly from GitHub using [UV](https://astral.sh/uv/)
- **Cloud based storage:** All data stored in YAML files + SQLite in the cloud
- **Simple Storage:** One folder per dataset with `metadata.yaml`
- **Fast Search:** Full-text search powered by SQLite FTS5 with structured query parsing
- **Inline Editing:** Edit datasets directly in the TUI
- **Validated Metadata:** JSON Schema + Pydantic validation ensure consistency
- **Clean TUI:** Terminal interface built with Textual, Neovim-style keybindings
- **Themeable:** 12 built-in themes with easy customization
- **Customizable:** Configure keybindings, themes, and behavior

---

## Commands at a Glance

### Installation (UV Method - Linux)
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ephemeral run (test without installing)
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# Persistent install (recommended)
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

### Runtime Commands
```bash
# Launch the TUI (use either command)
hei-datahub

# Run system diagnostics (new from v0.58)
hei-datahub doctor

# Reindex from YAML files
hei-datahub reindex

# Show diagnostic paths
hei-datahub paths

# Show version
hei-datahub --version
hei-datahub --version-info  # Detailed information
```

### Updates & Maintenance
```bash
# Update to latest version (It can be updated from main branch or a specific branch)
hei-datahub update
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
- **[0.58-beta "Streamline"](whats-new/0.58-beta.md)** — UV installation + Desktop integration + Data directory control (Oct 2025)
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
