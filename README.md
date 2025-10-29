
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
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Hei-DataHub (SSH recommended)
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"

# Launch
hei-datahub
```

**Try before installing:**
```bash
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

**Pin to specific version:**
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.60.0-beta"
```

---

## ✨ What Makes It Different

### 🔐 Secure Cloud Sync
- **Interactive setup** — `hei-datahub auth setup` wizard in 60 seconds
- **Keyring storage** — No plaintext passwords, Linux keyring integration
- **WebDAV ready** — Works with Heibox, Seafile, any WebDAV server

### ⚡ Lightning Fast
- **<80ms search** — Full-text search with SQLite FTS5, zero network latency
- **<300ms startup** — Instant UI with smart caching
- **Background sync** — Never blocks the UI

### 🎯 Team-First
- **Direct cloud upload** — Share datasets instantly via Heibox/Seafile
- **No Git overhead** — Skip branches, PRs, and merge conflicts
- **Private by default** — Data stays in your institution's cloud

---

## 🚀 Quick Start

**1. Setup cloud storage (optional but recommended):**
```bash
hei-datahub auth setup   # Interactive wizard
hei-datahub auth doctor  # Verify connection
```

**2. Use the TUI:**
```bash
hei-datahub  # Launch interface
# Press '/' → search datasets
# Press 'A' → add to cloud
# Press 'E' → edit metadata
# Press '?' → help
```

**3. Learn more:**
- [WebDAV Setup Guide](https://0xpix.github.io/Hei-DataHub/installation/auth-setup-linux/)
- [Add Dataset Tutorial](https://0xpix.github.io/Hei-DataHub/how-to/add-dataset-to-cloud/)
- [Keyboard Shortcuts](https://0xpix.github.io/Hei-DataHub/getting-started/03-the-basics/)

---

## 🛠️ Development Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub
uv sync --dev && source .venv/bin/activate

# Run from source
hei-datahub     # or: mini-datahub
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
```

See [Developer Docs](https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1/) for contribution guidelines.

---

## 📦 How It Works

* `data/<id>/metadata.yaml` on cloud via WebDAV
* Local SQLite FTS5 index with background sync
* Fast search: <80ms response, zero network on keystroke
* Validation via JSON Schema + Pydantic
* Textual TUI (keyboard-first)
* Secure credentials: Linux keyring storage

Details: [Basics](https://0xpix.github.io/Hei-DataHub/getting-started/03-the-basics/)
s
---

<p align="center">
  <strong>Built with 󰋑 for research teams who want clean data organization without the overhead</strong>
</p>
