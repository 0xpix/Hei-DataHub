# UV Quick Start Guide

> 🧱 Compatible with Hei-DataHub **v0.58.x-beta**

[UV](https://github.com/astral-sh/uv) is a blazingly fast Python package manager written in Rust. It makes installing packages from private Git repositories incredibly simple.

---

## 📦 Installing UV

### Linux & macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This installs UV to `~/.local/bin/uv`. Add it to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

### Windows (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

This installs UV to `%USERPROFILE%\.local\bin\uv.exe`.

### Verify Installation

```bash
uv --version
```

You should see something like: `uv 0.x.x`

---

## 🚀 Installation Methods

### Method A: Ephemeral Run (uvx)

Perfect for **one-time use** or **testing**. Nothing is installed globally.

#### Using SSH (Recommended):

```bash
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub"
```

#### Using HTTPS + Token:

```bash
export GH_PAT=ghp_xxxxxxxxxxxxx
uvx "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub"
```

**What happens:**
- UV creates a temporary virtual environment
- Installs hei-datahub and all dependencies
- Runs the application
- Cleans up when you exit

**Use case:** Quick testing, CI/CD pipelines, temporary access.

---

### Method B: Persistent Install (uv tool install)

Install Hei-DataHub **globally** for repeated use.

#### Using SSH:

```bash
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

#### Using HTTPS + Token:

```bash
export GH_PAT=ghp_xxxxxxxxxxxxx
uv tool install --from "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub" hei-datahub
```

**What happens:**
- UV installs hei-datahub to `~/.local/bin/`
- Creates an isolated environment (no conflicts with other Python projects)
- Makes `hei-datahub` command available system-wide

**Now you can run it anytime:**

```bash
hei-datahub
```

---

## 🔖 Version Pinning

### Install a Specific Version

Pin to a Git tag (e.g., `v0.58.0-beta`):

```bash
# Ephemeral
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.0-beta#egg=hei-datahub"

# Persistent
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.0-beta#egg=hei-datahub" hei-datahub
```

### Install from a Branch

Install from a specific branch (e.g., `develop`):

```bash
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@develop#egg=hei-datahub" hei-datahub
```

### Install from a Commit

Pin to a specific commit hash:

```bash
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@a1b2c3d4#egg=hei-datahub" hei-datahub
```

---

## 🔄 Updating Hei-DataHub

### Update to Latest Main

```bash
uv tool install --upgrade --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

Or simply:

```bash
uv tool upgrade hei-datahub
```

### Update to a New Version

```bash
uv tool install --upgrade --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.59.0-beta#egg=hei-datahub" hei-datahub
```

---

## 🗑️ Uninstalling

```bash
uv tool uninstall hei-datahub
```

This removes the tool and its isolated environment.

---

## 🎯 One-Liner Setup

Copy-paste this for a complete setup (SSH method):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && \
  source ~/.bashrc && \
  uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub && \
  hei-datahub --version
```

---

## 💡 Tips & Tricks

### Check Installed Tools

```bash
uv tool list
```

### Reinstall from Scratch

```bash
uv tool uninstall hei-datahub
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

### Run with Verbose Output

```bash
uv -v tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

---

## 🔍 Troubleshooting

### "Command not found: hei-datahub"

Make sure `~/.local/bin` is in your PATH:

```bash
echo $PATH | grep -q "$HOME/.local/bin" && echo "✅ In PATH" || echo "❌ Not in PATH"
```

Add it:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Authentication Errors

See [Private Repository Access](private-repo-access.md) for SSH and token setup.

### Data Files Missing

This is fixed in v0.58.0-beta. If you still see issues, see [Troubleshooting](troubleshooting.md).

---

## 📚 Next Steps

- [Private Repository Access Setup](private-repo-access.md)
- [Windows-Specific Instructions](windows-notes.md)
- [Create a Desktop Launcher](desktop-version.md)

---

**UV makes Python packaging fast and simple!** ⚡
