# 🔧 Critical Fixes for v0.58.0-beta Installation Issues

## Issues Identified

### Issue 1: Package Name Mismatch
**Problem:** `pyproject.toml` has `name = "hei-datahub"` but the actual source package is `mini_datahub`

**Impact:** UV install fails with:
```
error: Package name (`mini-datahub`) provided with `--from` does not match install request (`hei-datahub`)
```

### Issue 2: Main Branch Not Updated
**Problem:** Testing from `main` branch which still has v0.56.0-beta

**Impact:** Users getting old version when installing from main

### Issue 3: Python Import Context
**Problem:** `uvx` runs in temporary environment, then user tries to import in system Python

**Impact:** `ModuleNotFoundError: No module named 'mini_datahub'`

---

## 🔨 Fixes Required

### Fix 1: Keep Backward Compatible Package Name

**Decision:** Keep `mini-datahub` as primary package name for backward compatibility

**Change in `pyproject.toml`:**
```toml
[project]
name = "mini-datahub"  # Keep as mini-datahub
version = "0.58.0-beta"
```

**Reasoning:**
- Existing users have `mini-datahub` installed
- Source code uses `mini_datahub` package
- Easier migration path
- Both `mini-datahub` and `hei-datahub` commands work (via scripts)

### Fix 2: Update All Documentation

**Correct UV commands:**
```bash
# Ephemeral (SSH)
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=mini-datahub"

# Persistent (SSH)
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=mini-datahub" mini-datahub

# With token
export GH_PAT=ghp_xxxxx
uv tool install --from "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main#egg=mini-datahub" mini-datahub
```

**Both commands work after install:**
```bash
hei-datahub --version
mini-datahub --version
```

### Fix 3: Testing Instructions

**For testing feature branch:**
```bash
# Option 1: Ephemeral test
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub"

# Option 2: Persistent install with custom name
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub" hei-datahub-test

# Test it
hei-datahub-test --version

# Cleanup
uv tool uninstall hei-datahub-test
```

**After merge to main:**
```bash
# This will work correctly
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=mini-datahub" mini-datahub
hei-datahub --version  # Should show 0.58.0-beta
```

---

## 📝 Files to Update

### 1. pyproject.toml
Change package name back to `mini-datahub`

### 2. README.md
Update all UV examples to use `mini-datahub`

### 3. All documentation in docs/installation/
- `README.md`
- `uv-quickstart.md`
- `private-repo-access.md`
- `windows-notes.md`
- Update all examples

### 4. Reference documents
- `QUICK_REFERENCE_v0.58.md`
- `FINAL_CHECKLIST_v0.58.md`
- `IMPLEMENTATION_SUMMARY_v0.58.md`

### 5. Scripts
- Update validation script examples

---

## ✅ Correct Working Examples

### Ephemeral Run
```bash
# This WORKS
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub"
```

### Persistent Install
```bash
# This WORKS
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub" mini-datahub

# Then run
hei-datahub --version  # or mini-datahub --version
```

### Verifying Package Contents
```bash
# After install, check in the UV tool environment
uv tool run --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub" python -c "import mini_datahub; import os; print(os.listdir(os.path.dirname(mini_datahub.__file__)))"
```

---

## 🎯 Action Items

1. **Revert package name** to `mini-datahub` in `pyproject.toml`
2. **Update all documentation** with correct `mini-datahub` examples
3. **Test the corrected commands**
4. **Update README** with accurate UV examples
5. **Commit all fixes**
6. **Test from feature branch** before merging

---

## 💡 Why This Approach?

**Package Name:** `mini-datahub`
- Source code is in `mini_datahub/` directory
- Existing installations use this name
- Backward compatible

**Command Names:** Both `hei-datahub` AND `mini-datahub`
- Defined in `[project.scripts]`
- Users can use either command
- Marketing name vs. package name separation

**Repository Name:** `Hei-DataHub` (marketing name)
**Package Name:** `mini-datahub` (technical name)
**Command Names:** `hei-datahub` or `mini-datahub` (user choice)

---

## 🧪 Final Test Sequence

```bash
# 1. Ephemeral test (should work immediately)
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub"

# 2. Install for testing
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x#egg=mini-datahub" mini-datahub-test

# 3. Verify version
mini-datahub-test --version  # Should show 0.58.0-beta

# 4. Test both commands
hei-datahub-test --version
mini-datahub-test --version

# 5. Cleanup
uv tool uninstall mini-datahub-test
```

---

**Status:** Ready to fix and test properly! 🚀
