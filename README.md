
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

![Version](https://img.shields.io/badge/Version-0.60.0--beta-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

> Local-first TUI to catalog datasets with YAML + SQLite, fast full-text search, and one-key "save → HeiBox".

- **Latest:** 0.60-beta "Clean-up" — see [What's new](https://0xpix.github.io/Hei-DataHub/whats-new/0.60-beta/)
- **Docs:** Start with [Installation Guide](https://0xpix.github.io/Hei-DataHub/installation/README/) and then the [User Guide](https://0xpix.github.io/Hei-DataHub/)

---

## 🚀 Quick Install — UV Method (v0.60.x-beta)

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
hei-datahub

# Configure WebDAV for cloud storage (optional, interactive wizard)
hei-datahub auth setup
```

### Version Pinning
```bash
# Install specific version
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.60.0-beta"

# Install from feature branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@release/0.60-beta"
```

**📚 WebDAV Setup (for cloud storage):**

Configure Heibox/Seafile integration with the interactive wizard:
```bash
hei-datahub auth setup  # Interactive WebDAV setup
hei-datahub auth status # Check configuration
hei-datahub auth doctor # Diagnose connection issues
```
See [WebDAV Setup Guide](docs/installation/auth-setup-linux.md) for details.

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
hei-datahub
```

**macOS/Windows:** Coming soon in future releases.

Check [QUICKSTART](https://0xpix.github.io/Hei-DataHub/getting-started/01-getting-started/) for details.

---

## ✨ Key Features in v0.59+ "Privacy"

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
**Setup** WebDAV credentials → **Browse** cloud datasets (instant search) → **Add** datasets directly to Heibox → **Team access** immediately

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
s
---

**Built for teams who want to organize data without the overhead.**
