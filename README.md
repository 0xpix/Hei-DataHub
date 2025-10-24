
<p align="center">
  <img src="assets/png/Hei-datahub-logo-main.png" alt="Logo Main" width="200"/>
</p>

<p align="center">
  <img src="assets/png/Hei-datahub-logo-round.png" alt="Logo round" width="200"/>
  <img src="assets/png/Hei-datahub-logo-H.png" alt="Logo H" width="200"/>
</p>

<p align="center">
  <img src="assets/png/Hei-datahub-logo-inline.png" alt="Logo inline" width="400"/>
</p>

# Hei-DataHub

![Version](https://img.shields.io/badge/Version-0.59.0--beta-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

> Local-first TUI to catalog datasets with YAML + SQLite, fast full-text search, and one-key "save → HeiBox".

- **Latest:** 0.59-beta "Privacy" — see [What's new](https://0xpix.github.io/Hei-DataHub/whats-new/0.59-beta/)
- **Docs:** Start with [Installation Guide](https://0xpix.github.io/Hei-DataHub/installation/README/), then the [User Guide](https://0xpix.github.io/Hei-DataHub/) and [PR workflow](https://0xpix.github.io/Hei-DataHub/how-to/05-first-dataset/)

---

## Why Hei-DataHub?

- **Lightning fast:** <80ms search with SQLite FTS5, <300ms startup
- **Cloud-native:** WebDAV integration for Heibox/Seafile collaboration
- **Secure auth:** Linux keyring storage, interactive setup wizard
- **Stay consistent:** JSON Schema + Pydantic validation
- **Work local:** YAML on disk, background sync, zero network on search
- **Publish easily:** Direct cloud upload or auto-stash → branch → PR
- **Team-friendly:** Instant dataset sharing, no GitHub required
- **Easy install:** Direct from GitHub with UV - no cloning needed

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

# Configure WebDAV for cloud storage (optional, interactive wizard)
hei-datahub auth setup
```

### Version Pinning
```bash
# Install specific version
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.59.0-beta"

# Install from feature branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@release/0.59-beta"
```

**📚 Need help?** See [docs/installation](docs/installation/README.md) for:
- SSH key and PAT setup
- WebDAV authentication setup
- Troubleshooting authentication
- Updating and uninstalling
- Windows/macOS support (coming soon)

**� WebDAV Setup (for cloud storage):**
Configure Heibox/Seafile integration with the interactive wizard:
```bash
hei-datahub auth setup  # Interactive WebDAV setup
hei-datahub auth status # Check configuration
hei-datahub auth doctor # Diagnose connection issues
```
See [WebDAV Setup Guide](docs/installation/auth-setup-linux.md) for details.

**�🖥️ Desktop Integration (Linux):**
After installation, desktop integration is automatically set up on first run. You can also manage it manually:
```bash
hei-datahub desktop install   # Install desktop launcher
hei-datahub desktop uninstall # Remove desktop integration
```

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

## ✨ Key Features in v0.59-beta "Privacy"

### 🔐 WebDAV Authentication System
- **Interactive setup wizard** — `hei-datahub auth setup` with guided prompts
- **Secure credential storage** — Linux keyring integration, no plaintext secrets
- **Comprehensive diagnostics** — `hei-datahub auth doctor` for troubleshooting
- **Multiple auth methods** — Token or password-based authentication
- **ENV fallback** — Environment variable support when keyring unavailable

### ☁️ Cloud-First Data Management
- **Heibox/Seafile integration** — Direct WebDAV storage for team collaboration
- **Add to cloud** — Upload datasets directly, no GitHub required
- **Instant sharing** — Team members see changes immediately
- **Better privacy** — No Git history, data stays in your institution's cloud

### 🚀 Performance Overhaul
- **Lightning-fast startup** — UI appears in <300ms (warm cache)
- **Instant search** — <80ms response time, zero network calls on keystroke
- **Background indexing** — SQLite FTS5 with automatic updates
- **Smart caching** — Incremental sync with ETag-based validation

## Cloud-Based (Heibox/Seafile) — New in 0.59! ✨
1. **Setup** WebDAV credentials → 2. **Browse** cloud datasets (instant search) → 3. **Add** datasets directly to Heibox → 4. **Team access** immediately

```bash
# One-time setup
hei-datahub auth setup

# Launch and search (fast!)
hei-datahub
# Press '/' to search, 'A' to add
```

Guides:
- [WebDAV Setup](docs/installation/auth-setup-linux.md)
- [Add Dataset to Cloud](docs/how-to/add-dataset-to-cloud.md)

---

## Core Concepts

* `data/<id>/metadata.yaml` on cloud via WebDAV
* Local SQLite FTS5 index with background sync
* Fast search: <80ms response, zero network on keystroke
* Validation via JSON Schema + Pydantic
* Textual TUI (keyboard-first)
* Secure credentials: Linux keyring storage

Details: [Basics](https://0xpix.github.io/Hei-DataHub/getting-started/03-the-basics/)


---

**Built for teams who want to organize data without the overhead.**
