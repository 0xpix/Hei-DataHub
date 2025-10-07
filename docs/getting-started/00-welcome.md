# Welcome to Hei-DataHub

## What is Hei-DataHub?

**Hei-DataHub** is a terminal-based application (TUI) designed to help researchers, data engineers, and teams **organize, search, and share datasets** without the overhead of complex data catalog infrastructure.

It's built for people who:

- Work with multiple datasets across projects
- Need fast search and metadata consistency
- Prefer local-first tools that don't require cloud services
- Want a keyboard-driven workflow (Vim/Neovim users will feel at home)
- Need optional GitHub integration for collaborative workflows

---

## Problems It Solves

### Before Hei-DataHub

- Datasets scattered across folders, wikis, and README files
- Inconsistent metadata formats—everyone documents differently
- No fast search—grep and manual hunting through files
- Sharing datasets means copy-pasting metadata into Slack/emails
- No validation—typos, missing fields, broken URLs

### With Hei-DataHub

- **Single source of truth:** All datasets in `data/` with consistent `metadata.yaml` files
- **Fast search:** Full-text search (FTS5) finds datasets by name, description, or project
- **Validated metadata:** JSON Schema ensures all required fields are present
- **Keyboard-first:** Add, search, edit, and publish without touching the mouse
- **Optional PR workflow:** Save → Commit → Push → Open PR in one keystroke
- **Local-first:** Everything works offline; sync with GitHub when ready

---

## Who It's For

### Data Engineers & Scientists

- Manage dataset inventory across multiple projects
- Quickly find datasets by keyword or project name
- Validate metadata before sharing with team

### Research Teams

- Maintain a shared catalog of research datasets
- Collaborate via GitHub Pull Requests
- Track dataset provenance and usage

### Solo Practitioners

- Personal dataset library with fast search
- No account signup or cloud dependencies
- Export to YAML for portability

---

## Design

1. **Local-first:** Your data lives in plain text (YAML) and SQLite—no vendor lock-in
2. **Keyboard-driven:** Vim-style keybindings (`j/k` to navigate, `/` to search, `a` to add)
3. **Fast by default:** Search is instant; no network round-trips
4. **Validate early:** Schema validation catches errors before they spread
5. **Collaboration:** Use GitHub PRs to add datasets and expand the catalog

---

## Next Steps

Ready to get started?

1. **[Getting Started](01-getting-started.md)** — Install and run Hei-DataHub
3. **[Navigation](02-navigation.md)** — Learn the keyboard shortcuts
2. **[Tutorial: Your First Dataset](../how-to/05-first-dataset.md)** — Add your first dataset

---

## Contributing

Hei-DataHub is open source ([MIT License](https://github.com/0xpix/Hei-DataHub/blob/main/LICENSE)).

- **Report bugs:** [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Suggest features:** [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
