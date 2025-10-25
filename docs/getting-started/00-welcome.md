# Welcome to Hei-DataHub

## What is Hei-DataHub?

**Hei-DataHub** is a cloud-based terminal application (TUI) designed to help **US** (researchers, data engineers, and teams) organize, search, and share datasets through seamless integration with HeiBox (WebDAV).

It's built for people who:

- Work with multiple datasets across projects and institutions
- Need fast, unified search and consistent metadata
- Want secure cloud access without managing servers or APIs
- Need to browse and manage data directly from HeiBox

---

## Problems It Solves

### Before Hei-DataHub

- Datasets scattered across folders, drives, wikis, and mysterious final_final_v3.zip files
- Metadata written in everyone’s own special dialect of YAML and chaos
- Searching means `CLICK -> CLICK -> CLICK -> ...` and pray
- Sharing datasets involves forwarding 12 email threads
- Validation? None. Just vibes, typos, and broken links everywhere

### With Hei-DataHub

- One catalog to rule them all: Every dataset neatly listed with consistent metadata.yaml files
- Lightning-fast search: Type a keyword and boom — results faster than you can blink
- Schema-powered sanity: JSON Schema makes sure no field gets left behind
- Keyboard zen: No clicking, no scrolling — just you, your terminal, and full control
- Seamless HeiBox sync: Add, browse, and share directly from the cloud
- Always works: No server drama, no setup headaches — just open and go

---

## Design Principles

1. **Cloud-first**: Everything runs directly on HeiBox (WebDAV) — no local data storage
2. **Keyboard-driven**: Vim-style navigation (j/k to move, / to search, a to add)
3. **Fast by design**: Full-text search optimized for large HeiBox directories
4. **Schema validation**: Prevents broken metadata before upload
5. **Secure & simple**: Authentication handled via `hei-datahub auth setup`
6. **Easy installation**: (New in v0.59-beta) Install and connect in seconds
7. **Cross-platform ready**: Linux-first; macOS and Windows support coming soon

---

## Next Steps

Ready to get started?

1. **[Installation Guide](../installation/README.md)** — Quick start with UV (>= v0.58)
2. **[Getting Started](01-getting-started.md)** — First launch and commands
3. **[Navigation](02-navigation.md)** — Learn the keyboard shortcuts
4. **[Tutorial: Your First Dataset](../how-to/05-first-dataset.md)** — Add your first dataset

---

## Contributing

Hei-DataHub is open source ([MIT License](https://github.com/0xpix/Hei-DataHub/blob/main/LICENSE)).

- **Report bugs:** [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Suggest features:** [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
