
<p align="center">
  <img src="assets/png/Hei-datahub-logo-main.png" alt="Hei-DataHub Logo Main" width="200"/>
</p>

<p align="center">
  <img src="assets/png/Hei-datahub-logo-inline.png" alt="Logo inline" width="250"/>
</p>

<p align="center">
  <img src="assets/png/Hei-datahub-logo-round.png" alt="Logo Inline v1" width="200"/>
  <img src="assets/png/Hei-datahub-logo-H.png" alt="Logo Inline v1" width="200"/>
</p>

# Hei-DataHub

![WIN-SUCKS](https://img.shields.io/badge/WIN-SUCKS-0.59.0--beta-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

> Local-first TUI to catalog datasets with YAML + SQLite, fast full-text search, and one-key "save → PR".

- **Latest:** 0.58.3-beta "Streamline `Windows SUCKS`" — see [What's new](https://0xpix.github.io/Hei-DataHub/whats-new/0.58-beta/)
- **Docs:** Start with [Installation Guide](https://0xpix.github.io/Hei-DataHub/installation/README/), then the [User Guide](https://0xpix.github.io/Hei-DataHub/) and [PR workflow](https://0xpix.github.io/Hei-DataHub/how-to/05-first-dataset/)

---

## Why Hei-DataHub?

- **Search fast:** SQLite FTS5 (BM25)
- **Stay consistent:** JSON Schema + Pydantic
- **Work local:** YAML on disk, no servers
- **Publish safely:** Auto-stash → branch → PR
- **Team-friendly:** Outbox retries, simple token setup
- **Easy install:** Direct from GitHub with UV—no cloning needed
- **Desktop ready:** Linux launcher for application menu integration

More: see the [User Guide](https://0xpix.github.io/Hei-DataHub/).

---

## 🚀 Quick Install — UV Method (v0.59.x-beta)

**Linux users:** No cloning required! Install directly from the private repository with modern UV tooling.

### Prerequisites

```bash
# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Ephemeral Run (Try without installing)
```bash
# With SSH (recommended)
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# With HTTPS + Personal Access Token
export GH_PAT=ghp_xxxxxxxxxxxxx
uvx "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main"
```

### Persistent Install (Recommended)
```bash
# With SSH (recommended)
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# With HTTPS + Token
export GH_PAT=ghp_xxxxxxxxxxxxx
uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main"

# Run the application
hei-datahub  # or mini-datahub
```

### Version Pinning
```bash
# Install specific version
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1-beta"

# Install from feature branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

**📚 Need help?** See [docs/installation](docs/installation/README.md) for:
- SSH key and PAT setup
- Troubleshooting authentication
- Updating and uninstalling
- Windows/macOS support (coming soon)

**🖥️ Desktop Integration (Linux):**
After installation, create a desktop launcher to access from your application menu:
```bash
bash scripts/create_desktop_entry.sh
```
This creates a `.desktop` entry compatible with GNOME, KDE, XFCE, and other desktop environments.

---

## Development Install

For contributors who want to modify the code:

**Linux:**

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub

# Install with development dependencies
uv sync --dev && source .venv/bin/activate

# Run from source
hei-datahub     # or: mini-datahub
```

**macOS/Windows:** Coming soon in future releases.

Check [QUICKSTART](https://0xpix.github.io/Hei-DataHub/getting-started/01-getting-started/) for details.

---

## ✨ Key Features in v0.58-beta

### 🎯 Modern Installation
- **UV-based installation** — Install directly from GitHub without cloning
- **Ephemeral runs** — Test with `uvx` before committing to installation
- **Version pinning** — Lock to specific tags, branches, or commits
- **Dual authentication** — SSH keys or HTTPS with Personal Access Tokens

### 🗂️ Data Management
- **XDG-compliant paths** — Linux uses `~/.local/share/Hei-DataHub`
- **Auto-initialization** — First run creates workspace with sample datasets
- **Complete packaging** — All data files, configs, and assets included
- **Persistent storage** — UV installs always use home directory workspace

### 🖥️ Desktop Integration (Linux)
- **Application menu entry** — Launch from GNOME, KDE, XFCE, etc.
- **XDG desktop integration** — Follows Linux desktop standards
- **Auto-detection** — Finds installed executable automatically
- **One-command setup** — Simple script creates launcher

### 🔧 System Diagnostics
- **`hei-datahub doctor`** — Comprehensive health checks
- **Exit codes** — Clear status for scripting (0=healthy, 1-3=issues)
- **Actionable output** — Specific suggestions for fixing problems
- **Cross-platform** — Detects OS-specific data directories

### 📊 Data Directory Control
- **`--data-dir` flag** — Override workspace location from CLI
- **Environment variable** — Set `HEIDATAHUB_DATA_DIR` for persistence
- **Clear precedence** — CLI > env var > OS default
- **Migration detection** — Notifies about legacy path locations

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
