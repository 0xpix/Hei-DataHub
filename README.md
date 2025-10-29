
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

## ⚡ Install in 30 Seconds

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
hei-datahub
```

See [Developer Docs](https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1/) for contribution guidelines.

---

## 📦 How It Works

```
┌─────────────────┐
│  YAML Metadata  │ → Validated (JSON Schema + Pydantic)
└────────┬────────┘
         ↓
┌─────────────────┐
│  SQLite FTS5    │ → Local index, <80ms search
└────────┬────────┘
         ↓
┌─────────────────┐
│  WebDAV Cloud   │ → Sync to Heibox/Seafile
└─────────────────┘
```

**Core principles:**
- Local-first: Work offline, sync when ready
- Keyboard-driven: Textual TUI, zero mouse needed
- Schema-validated: Catch errors before they spread
- Fast: Sub-second everything

---

<p align="center">
  <strong>Built for research teams who want clean data organization without the overhead</strong>
</p>
