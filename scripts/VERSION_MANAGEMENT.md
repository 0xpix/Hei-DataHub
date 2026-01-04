# Version Management Guide - Hei-DataHub v0.60+

## Overview

Hei-DataHub uses `version.yaml` as the **single source of truth** for all version information.

## Quick Reference

### Update Version

**Edit only one file:**
```bash
vim version.yaml
```

**Then verify:**
```bash
python scripts/test_version.py              # Quick test
python scripts/check_version_consistency.py # Full validation
```

---

## File Structure

```
Hei-DataHub/
├── version.yaml                    # ⭐ SOURCE OF TRUTH
├── pyproject.toml                  # Auto-synced by build process
├── README.md                       # Mentions version
├── docs/_includes/version.md       # User docs version notice
├── src/hei_datahub/version.py      # Loads from version.yaml at runtime
└── scripts/
    ├── test_version.py             # Quick version test
    └── check_version_consistency.py # Full consistency check
```

---

## How It Works

### 1. Single Source of Truth: `version.yaml`

```yaml
# Example version.yaml
version: "0.60.1-beta"
codename: "Clean-up"
release_date: "2026-01-04"
compatibility: "Hei-DataHub v0.60.x (beta)"
notes: "Clean-up release - UI polish, enhanced navigation, and codebase cleanup"
# ... other metadata
```

### 2. Runtime Loading: `src/hei_datahub/version.py`

```python
# Loads version.yaml at module import
from hei_datahub.version import __version__

print(__version__)  # "0.60.1-beta"
```
print(CODENAME)     # "Clean-up"
```

**Load Priority:**
1. ✅ **Project root** `version.yaml` (development)
2. Package dir `src/hei_datahub/version.yaml` (installed/packaged)
3. Hardcoded defaults (fallback)

### 3. Validation Scripts

#### Quick Test: `scripts/test_version.py`
```bash
python scripts/test_version.py
```

**Output:**
```
**Output:**
```
✅ Version module imported successfully!
  Version:      0.60.1-beta
```
  Codename:     Clean-up
  Build Number: 006000

✅ Version module matches version.yaml!
🎉 All version checks passed!
```

#### Full Check: `scripts/check_version_consistency.py`
```bash
python scripts/check_version_consistency.py
```

**Checks:**
- ✅ `pyproject.toml` version matches
- ✅ `README.md` mentions version
- ✅ `docs/_includes/version.md` has correct version
- ✅ `version.py` loads and matches
- ✅ No legacy `mini_datahub` files exist

---

## Release Process

### Step 1: Update Version
```bash
# Edit version.yaml
vim version.yaml

# Change:
#   version: "0.60.0-beta"  →  "0.61.0-beta"
#   codename: "Clean-up"    →  "Next Feature"
#   release_date: "2025-10-28"  →  "2025-11-15"
```

### Step 2: Validate
```bash
python scripts/test_version.py
python scripts/check_version_consistency.py
```

### Step 3: Update Documentation
```bash
# Update user docs version notice
vim docs/_includes/version.md

# Update CHANGELOG.md
vim CHANGELOG.md

# Update dev docs version banners
# (if major version change)
```

### Step 4: Commit and Tag
```bash
git add version.yaml docs/_includes/version.md CHANGELOG.md
git commit -m "chore: bump version to 0.61.0-beta 'Next Feature'"
git tag v0.61.0-beta
git push origin main --tags
```

---

## Troubleshooting

### ❌ Version Mismatch Error

**Symptom:**
```
❌ MISMATCH: module=0.59.0-beta, yaml=0.60.0-beta
```

**Cause:** Cached `version.yaml` in package directory

**Fix:**
```bash
# Remove cached version file
rm -f src/hei_datahub/version.yaml

# Verify
python scripts/test_version.py
```

---

### ❌ Import Error

**Symptom:**
```
ModuleNotFoundError: No module named 'hei_datahub'
```

**Fix:**
```bash
# Ensure you're in project root
cd /path/to/Hei-DataHub

# Add src to Python path or install in editable mode
pip install -e .

# Or use the script directly (it adds src to path)
python scripts/test_version.py
```

---

### ❌ Legacy Package References

**Symptom:**
```
❌ /path/to/mini_datahub should not exist
```

**Fix:**
```bash
# Remove old package directory
rm -rf src/mini_datahub

# Verify
python scripts/check_version_consistency.py
```

---

## What Changed in v0.60

### Before (messy):
- ❌ Multiple version files (`_version.py`, `version.py`, `__init__.py`)
- ❌ Manual sync required after version updates
- ❌ References to both `mini_datahub` and `hei_datahub`
- ❌ Inconsistent version info across files

### After (clean):
- ✅ Single source: `version.yaml`
- ✅ Automatic runtime loading (no sync needed)
- ✅ All references use `hei_datahub`
- ✅ Automated validation scripts
- ✅ Clear load priority (dev → packaged → defaults)

---

## Best Practices

### ✅ DO:
- Edit `version.yaml` for version changes
- Run validation scripts before commits
- Keep version format: `MAJOR.MINOR.PATCH-beta`
- Update `CHANGELOG.md` with version changes
- Tag releases: `git tag vX.Y.Z-beta`

### ❌ DON'T:
- Don't edit `version.py` directly
- Don't create `src/hei_datahub/version.yaml` manually
- Don't use `mini_datahub` package names
- Don't skip validation before release
- Don't forget to update docs version notices

---

## Scripts Reference

### `test_version.py` - Quick Version Test

**Purpose:** Verify version module loads correctly

**Usage:**
```bash
python scripts/test_version.py
```

**When to use:**
- After editing `version.yaml`
- Quick sanity check
- Debugging version issues

---

### `check_version_consistency.py` - Full Validation

**Purpose:** Comprehensive version consistency check

**Usage:**
```bash
python scripts/check_version_consistency.py
```

**When to use:**
- Before committing version changes
- Before creating releases
- CI/CD pipeline validation
- Debugging inconsistencies

**Exit codes:**
- `0` - All checks passed ✅
- `1` - One or more checks failed ❌

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Version Check

on: [push, pull_request]

jobs:
  version-consistency:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Check version consistency
        run: python scripts/check_version_consistency.py
```

---

## Summary

**Version management is now simple:**

1. Edit `version.yaml` ✏️
2. Run `python scripts/test_version.py` ✅
3. Commit and tag 🏷️
4. Done! 🎉

**Everything else is automated!**

---

*Last updated: 2025-10-28 for Hei-DataHub v0.60.0-beta "Clean-up"*
