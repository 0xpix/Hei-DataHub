
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

![Version](https://img.shields.io/badge/Version-0.61.0--beta-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

> Local-first TUI to catalog datasets with YAML + SQLite, fast full-text search, and one-key cloud sync via WebDAV.

---

## 🚀 Install

**Linux (UV recommended):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
hei-datahub
```

**Windows:**
Download `hei-datahub-setup.exe` from [Releases](https://github.com/0xpix/Hei-DataHub/releases).

---

## ⚡ Features

- **Fast search** — <80ms full-text search with SQLite FTS5
- **Cloud sync** — Direct upload to Heibox/Seafile via WebDAV
- **Keyboard-first** — Vim-style navigation, no mouse needed
- **Secure** — Credentials stored in system keyring

---

## 🎹 Quick Usage

```bash
hei-datahub              # Launch TUI
hei-datahub auth setup   # Configure WebDAV (optional)
```

| Key | Action |
|-----|--------|
| `/` | Search datasets |
| `A` | Add to cloud |
| `E` | Edit metadata |
| `?` | Help |

---

## 🛠️ Development

```bash
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub
uv sync --dev && source .venv/bin/activate
hei-datahub
```

---

<p align="center">
  <strong>Built for research teams who want clean data organization without overhead</strong>
</p>
