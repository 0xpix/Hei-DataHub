
<p align="center">
  <img src="assets/png/1.svg" alt="Hei-DataHub Logo" width="250"/>
  <img src="assets/png/8.svg" alt="Hei-DataHub Logo" width="250"/>
</p>

<p align="center">
  <img src="assets/svg/dark_logo_circle.svg" alt="Logo Circle" width="120"/>
  <img src="assets/svg/light_logo_circle.svg" alt="Logo Circle" width="120"/>
  <img src="assets/svg/dark_logo_H_large.svg" alt="Logo H Large" width="120"/>
  <img src="assets/svg/light_logo_H_large.svg" alt="Logo H Large" width="120"/>
</p>

<p align="center">
  <img src="assets/svg/dark_logo_inline_v1.svg" alt="Logo Inline v1" width="200"/>
  <img src="assets/svg/light_logo_inline_v1.svg" alt="Logo Inline v1" width="200"/>
</p>

# Hei-DataHub

![Beta](https://img.shields.io/badge/beta-0.57.2-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

> Local-first TUI to catalog datasets with YAML + SQLite, fast full-text search, and one-key "save → PR".

- **Latest:** 0.57.2-beta "Renovation" — see [What's new](https://0xpix.github.io/Hei-DataHub/whats-new/0.57-beta/)
- **Docs:** Start with [QUICKSTART](https://0xpix.github.io/Hei-DataHub/getting-started/01-getting-started/), then the [User Guide](https://0xpix.github.io/Hei-DataHub/) and [PR workflow](https://0xpix.github.io/Hei-DataHub/how-to/05-first-dataset/)

---

## Why Hei-DataHub?

- **Search fast:** SQLite FTS5 (BM25)
- **Stay consistent:** JSON Schema + Pydantic
- **Work local:** YAML on disk, no servers
- **Publish safely:** Auto-stash → branch → PR
- **Team-friendly:** Outbox retries, simple token setup

More: see the [User Guide](https://0xpix.github.io/Hei-DataHub/).

---

## 🚀 Quick Install — UV Method (v0.58.x-beta)

**No cloning required!** Install directly from the private repository:

### Ephemeral Run (SSH)
```bash
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

### Global Install (SSH)
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
hei-datahub  # or mini-datahub
```

### Install with HTTPS + Token
```bash
export GH_PAT=ghp_xxxxxxxxxxxxx  # Your GitHub Personal Access Token
uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main"
```

**📚 Need help?** See [docs/installation](docs/installation/README.md) for:
- Token/SSH setup
- Windows instructions
- Troubleshooting

**🖥️ Desktop Version (Linux):**
After installation, create a desktop launcher:
```bash
bash scripts/create_desktop_entry.sh
```

---

## Classic Install (For Development)

Linux:

```bash
git clone <your-repo-url>
cd Hei-DataHub
uv sync --dev && source .venv/bin/activate
hei-datahub     # or: mini-datahub
```

**Note:** We use [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management. Install it with:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub
uv sync --dev && source .venv/bin/activate
hei-datahub     # or: mini-datahub
```

Macos/Windows coming soon...

Check [QUICKSTART](https://0xpix.github.io/Hei-DataHub/getting-started/01-getting-started/) for details.

---

## Typical Workflow

1. **Search** (`/`) → 2. **Add/Edit** (`A`, validated) → 3. **Save → PR** (`Ctrl+S`, auto-stash) → 4. **Outbox** (`P`) if offline.

Full guide: [PR Workflow](https://0xpix.github.io/Hei-DataHub/how-to/05-first-dataset/).

---

## Core Concepts

* `data/<id>/metadata.yaml` on disk
* Local SQLite FTS5 index
* Validation via JSON Schema + Pydantic
* Textual TUI (keyboard-first)

Details: [Basics](https://0xpix.github.io/Hei-DataHub/getting-started/03-the-basics/)

---

## Troubleshooting

* Empty results? `hei-datahub reindex`
* DB issues? remove `db.sqlite` then reindex
* PR fails? check token & repo path, retry from **Outbox** (`P`)

See [TROUBLESHOOTING](https://0xpix.github.io/Hei-DataHub/help/troubleshooting/).

---

## Contributing & License

PRs welcome—style (black + ruff), tests, docs. See [Contributing](docs/contributing.md).
MIT — see [LICENSE](LICENSE).

<details>
  <summary>Repo layout (optional)</summary>

```
src/mini_datahub/  # app (UI, services, infra, core)
data/              # datasets with metadata.yaml
schema.json        # validation schema
.github/workflows/ # CI
```

More: Coming soon...

</details>

---

**Built for teams who want to organize data without the overhead.**
