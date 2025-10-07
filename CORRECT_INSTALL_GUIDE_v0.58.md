# ✅ Correct UV Installation for hei-datahub v0.58.0-beta

## 🎯 Key Points

1. **Package name in `pyproject.toml`:** `hei-datahub`
2. **Source code directory:** `src/mini_datahub/` (internal implementation detail)
3. **Commands available:** Both `hei-datahub` and `mini-datahub` work
4. **No `#egg=` needed:** UV auto-detects package name from `pyproject.toml`

---

## ✅ CORRECT Commands

### Ephemeral Run (Test without installing)

**SSH:**
```bash
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

**Token:**
```bash
export GH_PAT=ghp_xxxxx
uvx "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@chore/uv-install-data-desktop-v0.58.x"
```

### Persistent Install (Recommended)

**SSH:**
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

**Token:**
```bash
export GH_PAT=ghp_xxxxx
uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@chore/uv-install-data-desktop-v0.58.x"
```

### After Installation

Both commands work:
```bash
hei-datahub --version
mini-datahub --version
```

Both should show: `Hei-DataHub 0.58.0-beta`

---

## 🧪 Testing Right Now (Feature Branch)

```bash
# Clean test - ephemeral
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# Install for persistent use
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# Verify version
hei-datahub --version
# Output: Hei-DataHub 0.58.0-beta

# Check it works
hei-datahub
```

---

## 🚀 After Merging to Main

Once the PR is merged to `main`, users will install with:

```bash
# SSH
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git"

# Token
export GH_PAT=ghp_xxxxx
uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub"
```

**Even simpler!** No branch specification needed.

---

## 🔧 Why Previous Command Failed

### ❌ WRONG:
```bash
uv tool install --from "git+ssh://...#egg=hei-datahub" hei-datahub
```

**Error:** `Package name (mini-datahub) provided with --from does not match install request (hei-datahub)`

**Why:** The `--from` flag is for specifying package requirements, not Git repos. Also, the old `pyproject.toml` had `name = "mini-datahub"`.

### ✅ CORRECT:
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

**Why:** 
- UV reads `pyproject.toml` which now says `name = "hei-datahub"`
- No `#egg=` fragment needed
- No `--from` flag needed for direct Git installs

---

## 📦 What Gets Installed

When you run the install, UV will:
1. Clone the repository
2. Read `pyproject.toml` → finds `name = "hei-datahub"`
3. Build the package (including all data files via `MANIFEST.in`)
4. Install to `~/.local/bin/hei-datahub` and `~/.local/bin/mini-datahub`
5. Both commands work!

---

## 🎯 Version Pinning

### Install Specific Version
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.0-beta"
```

### Install from Main
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

### Install from Feature Branch (current)
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"
```

---

## 🧹 Clean Up Old Installs

If you have old installations:

```bash
# Remove any old installs
uv tool uninstall hei-datahub
uv tool uninstall mini-datahub

# Fresh install
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# Verify
hei-datahub --version
```

---

## 💡 One-Liner Setup

**Complete fresh install (SSH):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && \
  export PATH="$HOME/.local/bin:$PATH" && \
  uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x" && \
  hei-datahub --version
```

**With token:**
```bash
export GH_PAT=ghp_xxxxx && \
  curl -LsSf https://astral.sh/uv/install.sh | sh && \
  export PATH="$HOME/.local/bin:$PATH" && \
  uv tool install "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@chore/uv-install-data-desktop-v0.58.x" && \
  hei-datahub --version
```

---

## ✅ Verification Checklist

After installation, verify:

```bash
# 1. Check UV installed it
uv tool list | grep hei-datahub

# 2. Check commands exist
which hei-datahub
which mini-datahub

# 3. Check version
hei-datahub --version
mini-datahub --version

# 4. Run the app
hei-datahub
```

---

## 🎉 Summary

**Package Name:** `hei-datahub` ✅  
**Install Command:** `uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@BRANCH"` ✅  
**Run Commands:** `hei-datahub` or `mini-datahub` ✅  
**Version:** `0.58.0-beta` ✅  
**Data Included:** Yes (via MANIFEST.in and pyproject.toml) ✅

---

**Ready to test!** 🚀
