# Hei-DataHub v0.58.0-beta Quick Reference

**Version:** 0.58.0-beta "Streamline"  
**Branch:** `chore/uv-install-data-desktop-v0.58.x`

---

## 🚀 Installation (One-Liners)

### Linux/macOS (SSH)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main" hei-datahub && hei-datahub
```

### Linux/macOS (Token)
```bash
export GH_PAT=ghp_xxxxx
curl -LsSf https://astral.sh/uv/install.sh | sh && uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main" hei-datahub && hei-datahub
```

### Windows (PowerShell + Token)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"; $env:GH_PAT = "ghp_xxxxx"; uv tool install "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main" hei-datahub; hei-datahub
```

---

## 📦 Essential Commands

| Action | Command |
|--------|---------|
| **Install UV** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Ephemeral run** | `uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"` |
| **Global install** | `uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main" hei-datahub` |
| **Run app** | `hei-datahub` |
| **Check version** | `hei-datahub --version` |
| **Version info** | `hei-datahub --version-info` |
| **Reindex data** | `hei-datahub reindex` |
| **Update** | `uv tool upgrade hei-datahub` |
| **Uninstall** | `uv tool uninstall hei-datahub` |

---

## 🖥️ Desktop Integration

| Action | Command |
|--------|---------|
| **Create launcher** | `bash scripts/create_desktop_entry.sh` |
| **Build binary** | `bash scripts/build_desktop_binary.sh` |
| **Test binary** | `./dist/linux/hei-datahub --version` |

---

## 🔐 Authentication

### SSH Setup (Recommended)
```bash
# 1. Generate key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add to agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Copy public key
cat ~/.ssh/id_ed25519.pub

# 4. Add to GitHub: https://github.com/settings/keys

# 5. Test
ssh -T git@github.com
```

### Token Setup (Alternative)
```bash
# 1. Create token: https://github.com/settings/tokens
#    - Fine-grained token
#    - Repository access: 0xpix/Hei-DataHub
#    - Permissions: Contents (Read-only)

# 2. Export token
export GH_PAT=ghp_xxxxxxxxxxxxx

# 3. Add to shell profile (optional)
echo 'export GH_PAT=ghp_xxxxx' >> ~/.bashrc
```

---

## 🔖 Version Pinning

| Type | Example |
|------|---------|
| **Latest (main)** | `@main` |
| **Specific tag** | `@v0.58.0-beta` |
| **Branch** | `@develop` |
| **Commit** | `@a1b2c3d4` |

**Full example:**
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.0-beta"
```

---

## 📚 Documentation Quick Links

| Guide | Path |
|-------|------|
| **Overview** | `docs/installation/README.md` |
| **UV Guide** | `docs/installation/uv-quickstart.md` |
| **Auth Setup** | `docs/installation/private-repo-access.md` |
| **Windows** | `docs/installation/windows-notes.md` |
| **Desktop** | `docs/installation/desktop-version.md` |
| **Troubleshooting** | `docs/installation/troubleshooting.md` |

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| **"uv not found"** | `export PATH="$HOME/.local/bin:$PATH"` |
| **"hei-datahub not found"** | Same as above, then `uv tool list` |
| **SSH Permission denied** | `ssh-add ~/.ssh/id_ed25519` |
| **Token auth failed** | Check `echo $GH_PAT` and token permissions |
| **Data files missing** | Upgrade to v0.58.0-beta: `uv tool upgrade hei-datahub` |
| **Desktop launcher missing** | `update-desktop-database ~/.local/share/applications` |

---

## 🧪 Testing

### Verify Installation
```bash
# Check command exists
which hei-datahub

# Check version
hei-datahub --version

# Check data files
python -c "import mini_datahub; import os; print(os.listdir(os.path.dirname(mini_datahub.__file__)))"

# Run app
hei-datahub
```

### Test Desktop Launcher
```bash
# Create launcher
bash scripts/create_desktop_entry.sh

# Verify file
ls -la ~/.local/share/applications/hei-datahub.desktop

# Validate
desktop-file-validate ~/.local/share/applications/hei-datahub.desktop

# Update database
update-desktop-database ~/.local/share/applications
```

### Test Binary Build
```bash
# Build
bash scripts/build_desktop_binary.sh

# Test
./dist/linux/hei-datahub --version

# Check size
du -h dist/linux/hei-datahub
```

---

## 📊 What's New in v0.58.0-beta

- ✅ UV-based installation (no cloning)
- ✅ SSH + token authentication
- ✅ Fixed data packaging
- ✅ Desktop launcher (Linux)
- ✅ Binary build scripts
- ✅ 6 new documentation guides
- ✅ GitHub Actions automation
- ✅ Python 3.10+ requirement

---

## 🔄 Migration from Previous Versions

### If you cloned the repo:
```bash
cd Hei-DataHub
git pull
git checkout chore/uv-install-data-desktop-v0.58.x
source .venv/bin/activate
pip install -e .
hei-datahub
```

### Switch to UV install:
```bash
# Uninstall old
pip uninstall hei-datahub mini-datahub

# Install with UV
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

---

## 🎯 Key Files

### Core Package
- `src/mini_datahub/__main__.py` - Module entry
- `src/hei_datahub/` - Alias package
- `pyproject.toml` - Package config
- `MANIFEST.in` - Data inclusion

### Scripts
- `scripts/create_desktop_entry.sh` - Desktop launcher
- `scripts/build_desktop_binary.sh` - Binary builder

### Documentation
- `docs/installation/` - All guides (6 files)
- `CHANGELOG.md` - Version history
- `IMPLEMENTATION_SUMMARY_v0.58.md` - This release summary

### CI/CD
- `.github/workflows/build-binary.yml` - Auto builds

---

## 💻 Development

### Local Testing
```bash
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub
git checkout chore/uv-install-data-desktop-v0.58.x
uv venv
source .venv/bin/activate
uv pip install -e .
hei-datahub --version-info
```

### Test UV Install (Local)
```bash
uv tool install "git+file://$(pwd)" hei-datahub-test
hei-datahub-test
uv tool uninstall hei-datahub-test
```

---

## 🌐 URLs

| Resource | URL |
|----------|-----|
| **Repository** | `git@github.com:0xpix/Hei-DataHub.git` |
| **SSH Keys** | https://github.com/settings/keys |
| **Tokens** | https://github.com/settings/tokens |
| **UV Install** | https://astral.sh/uv/install.sh |
| **Issues** | https://github.com/0xpix/Hei-DataHub/issues |

---

## 📞 Support

- 📖 **Docs:** `docs/installation/troubleshooting.md`
- 🐛 **Issues:** GitHub Issues
- 💬 **Chat:** Team communication channel

---

**Print this page for quick reference!** 🖨️
