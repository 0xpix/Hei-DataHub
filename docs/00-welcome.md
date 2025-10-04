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

## What Ships in v0.55.x Beta

This release includes:

- **TUI (Terminal UI):** Home screen with search, dataset details, add/edit forms
- **Search Engine:** SQLite FTS5 with BM25 ranking
- **Metadata Validation:** JSON Schema + Pydantic models
- **Storage:** YAML files (one per dataset) + SQLite index
- **GitHub Integration (Optional):**
    - Automatic PR creation from TUI
    - Auto-stash uncommitted changes
    - Configurable reviewers and labels
- **Commands:**
    - `hei-datahub` — Launch TUI
    - `hei-datahub reindex` — Rebuild search index from YAML files
    - `hei-datahub --version` — Show version information

---

## Architecture Highlights

Hei-DataHub follows **Clean Architecture** principles:

```
┌─────────────────────────────────────┐
│         UI Layer (Textual)          │  ← TUI screens, widgets
├─────────────────────────────────────┤
│      Services (Business Logic)      │  ← Search, catalog, sync, publish
├─────────────────────────────────────┤
│    Core Domain (Models & Rules)     │  ← Pydantic models, validation
├─────────────────────────────────────┤
│    Infrastructure (I/O Adapters)    │  ← SQLite, YAML, Git, GitHub API
└─────────────────────────────────────┘
```

- **No I/O in core domain:** Business rules are pure functions
- **Dependency injection:** Easy to test and extend
- **Clear boundaries:** Each layer has a single responsibility

---

## Design Philosophy

1. **Local-first:** Your data lives in plain text (YAML) and SQLite—no vendor lock-in
2. **Keyboard-driven:** Vim-style keybindings (`j/k` to navigate, `/` to search, `a` to add)
3. **Fast by default:** Search is instant; no network round-trips
4. **Validate early:** Schema validation catches errors before they spread
5. **Optional collaboration:** Use GitHub PRs when you need team review, skip it when you don't

---

## Next Steps

Ready to get started?

1. **[Getting Started](01-getting-started.md)** — Install and run Hei-DataHub
2. **[Tutorial: Your First Dataset](20-tutorials/02-first-dataset.md)** — Add your first dataset
3. **[Navigation](02-navigation.md)** — Learn the keyboard shortcuts

---

## Contributing

Hei-DataHub is open source ([MIT License](https://github.com/0xpix/Hei-DataHub/blob/main/LICENSE)).

- **Report bugs:** [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Suggest features:** [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
- **Edit docs:** Click the edit icon (✏️) on any page
