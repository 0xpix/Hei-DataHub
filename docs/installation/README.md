# Installation Guide

> 🧱 Compatible with Hei-DataHub **v0.58.x-beta**

Welcome to the Hei-DataHub installation guide! This document provides everything you need to install and run Hei-DataHub using modern Python packaging tools.

## 📑 Table of Contents

- [Quick Start](#quick-start)
- [Installation Methods](#installation-methods)
  - [Method 1: UV (Recommended)](#method-1-uv-recommended)
  - [Method 2: Traditional pip](#method-2-traditional-pip)
  - [Method 3: Desktop Binary](#method-3-desktop-binary-linux)
- [Detailed Guides](#detailed-guides)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Quick Start

For the fastest installation experience with **UV** (private SSH access):

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# One-time run (ephemeral)
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub"

# Or install globally
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub

# Run it
hei-datahub
```

**That's it!** No cloning, no virtual environments, no hassle.

---

## Installation Methods

### Method 1: UV (Recommended)

UV is a blazingly fast Python package manager that makes installing from private repositories simple and efficient.

#### ✅ Advantages:
- **No repository cloning required**
- **Automatic dependency resolution**
- **Fast and reliable**
- **Version pinning support**
- **Works with SSH and HTTPS+token**

#### 📚 Detailed Guide:
See [UV Quick Start Guide](uv-quickstart.md) for:
- Installing UV
- Ephemeral vs persistent installation
- Version pinning
- Updating and uninstalling

#### 🔐 Private Repo Access:
See [Private Repository Access](private-repo-access.md) for:
- SSH key setup
- GitHub Personal Access Token (PAT) setup
- Troubleshooting authentication

---

### Method 2: Traditional pip

If you prefer the traditional approach or need more control:

```bash
# Clone the repository
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install with pip
pip install -e .

# Run it
hei-datahub
```

**Note:** This method requires manual virtual environment management.

---

### Method 3: Desktop Binary (Linux)

For a fully standalone experience without Python dependencies:

#### A. Desktop Launcher (for UV installations)

After installing via UV, create a desktop launcher:

```bash
bash scripts/create_desktop_entry.sh
```

This adds Hei-DataHub to your system's application menu.

#### B. Standalone Binary

Build a PyInstaller binary:

```bash
bash scripts/build_desktop_binary.sh
```

See [Desktop Version Guide](desktop-version.md) for details.

---

## Detailed Guides

Each topic has its own dedicated guide:

| Guide | Description |
|-------|-------------|
| [UV Quick Start](uv-quickstart.md) | Complete UV installation walkthrough |
| [Private Repo Access](private-repo-access.md) | SSH and token authentication setup |
| [Windows Notes](windows-notes.md) | Windows-specific installation steps |
| [Desktop Version](desktop-version.md) | Desktop launcher and binary builds |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |

---

## Troubleshooting

### Missing Data Files

If you see errors about missing data or config files after installation:

1. **For UV installations:** This should be automatic in v0.58.0+
2. **For pip installations:** Make sure you installed from the latest code
3. **Check package contents:**
   ```bash
   python -c "import hei_datahub; print(hei_datahub.__file__)"
   ```

See [Troubleshooting Guide](troubleshooting.md) for more solutions.

### Authentication Issues

If you can't access the private repository:

- **SSH:** Verify your SSH key is added to GitHub
- **Token:** Ensure your PAT has `contents:read` permission
- **Network:** Check firewall/proxy settings

See [Private Repo Access](private-repo-access.md) for detailed setup.

---

## Next Steps

Once installed, you can:

1. **Launch the TUI:**
   ```bash
   hei-datahub
   ```

2. **Check version:**
   ```bash
   hei-datahub --version
   hei-datahub --version-info
   ```

3. **Reindex datasets:**
   ```bash
   hei-datahub reindex
   ```

4. **Read the tutorials:**
   - [First Steps](../20-tutorials/01-installation.md)
   - [Adding Your First Dataset](../20-tutorials/02-first-dataset.md)
   - [Search and Filters](../20-tutorials/03-search-and-filters.md)

---

## Need Help?

- 📖 Check the [FAQ](../90-faq.md)
- 🐛 Report issues: [GitHub Issues](https://github.com/0xpix/Hei-DataHub/issues)
- 💬 Ask questions in your team's communication channel

---

**Happy data organizing!** 🎉
