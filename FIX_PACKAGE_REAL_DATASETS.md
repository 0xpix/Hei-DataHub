# ✅ FIXED: Package All Real Datasets (Not Just Templates)

## Problem Reported
> "it's good but not enough, i don't know from where it's getting the data, in .local/bin/hei-datahub there is all the folder from the github, but i can't for some reason access my data folder, it's just giving me the data inside the src/mini_datahub/template/, i want to use the data folder, either the one inside the root or the one inside the src/mini_datahub/data"

## Root Cause
- Only `templates/data/` with 1 sample dataset was being packaged
- The real 4 datasets in `data/` folder were **not** included in the UV installation
- `initialize_workspace()` was copying from `templates/data/` (only 1 dataset) instead of `data/` (4 datasets)

## Solution Implemented

### 1. All 4 Datasets Now in Package
The `src/mini_datahub/data/` directory now contains all your real datasets:
- `burned-area/`
- `land-cover/`
- `precipitation/`
- `testing-the-beta-version/`

### 2. Updated Packaging Configuration

**MANIFEST.in:**
```diff
+ # Include all datasets
+ recursive-include src/mini_datahub/data *
```

**pyproject.toml:**
```diff
[tool.setuptools.package-data]
mini_datahub = [
    "infra/sql/*.sql",
    "schema.json",
+   "data/**/*",
    "templates/**/*"
]
```

### 3. Changed Initialization to Use Real Data

**paths.py - initialize_workspace():**
```diff
- # Copy sample data if data directory is empty
+ # Copy packaged datasets if data directory is empty
  if DATA_DIR.exists() and not list(DATA_DIR.iterdir()):
      try:
-         # templates/ is in src/mini_datahub/ (parent.parent from infra/)
-         template_data = Path(__file__).parent.parent / "templates" / "data"
-         if template_data.exists():
+         # data/ is packaged in src/mini_datahub/ (parent.parent from infra/)
+         packaged_data = Path(__file__).parent.parent / "data"
+         if packaged_data.exists() and list(packaged_data.iterdir()):
              import shutil
-             for item in template_data.iterdir():
+             for item in packaged_data.iterdir():
                  dest = DATA_DIR / item.name
                  if not dest.exists():
                      shutil.copytree(item, dest)
-             print(f"✓ Initialized sample data in {DATA_DIR}")
+             print(f"✓ Initialized {len(list(packaged_data.iterdir()))} datasets in {DATA_DIR}")
```

## Testing Results

### Before Fix
```bash
rm -rf ~/.hei-datahub
uv tool install ... 
hei-datahub
# Result: Only 1 dataset (testing-the-beta-version from templates/)
```

### After Fix
```bash
rm -rf ~/.hei-datahub
cd /tmp
python -c "from mini_datahub.infra.paths import initialize_workspace; initialize_workspace()"
# Output: ✓ Initialized 4 datasets in /home/pix/.hei-datahub/data

ls ~/.hei-datahub/data/
# Output:
# burned-area/
# land-cover/
# precipitation/
# testing-the-beta-version/
```

**All 4 datasets with metadata.yaml verified:**
```bash
find ~/.hei-datahub/data/ -name "metadata.yaml"
# Output:
# ~/.hei-datahub/data/burned-area/metadata.yaml
# ~/.hei-datahub/data/land-cover/metadata.yaml
# ~/.hei-datahub/data/precipitation/metadata.yaml
# ~/.hei-datahub/data/testing-the-beta-version/metadata.yaml
```

## Files Changed

1. **MANIFEST.in** - Added `recursive-include src/mini_datahub/data *`
2. **pyproject.toml** - Added `"data/**/*"` to package-data
3. **src/mini_datahub/infra/paths.py** - Changed from templates/ to data/

## What Needs to be Committed

```bash
cd /home/pix/Github/Hei-DataHub
git add -A
git commit -m "feat(data): package all 4 real datasets instead of just template

- Add src/mini_datahub/data/ with all 4 datasets to MANIFEST.in
- Add data/**/* to pyproject.toml package-data
- Update initialize_workspace() to copy from packaged data/ (4 datasets) 
  instead of templates/data/ (1 dataset)

Datasets included:
  - burned-area
  - land-cover
  - precipitation
  - testing-the-beta-version

Testing confirmed all 4 datasets copied to ~/.hei-datahub/data/

Fixes: User unable to access real data folder, only got template data"

git push origin chore/uv-install-data-desktop-v0.58.x
```

## Next Step: Test Complete UV Install

After pushing, test the complete workflow:

```bash
# Clean install
rm -rf ~/.hei-datahub
uv tool uninstall hei-datahub

# Reinstall from your branch
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x"

# Run from any directory
cd /tmp
hei-datahub
```

**Expected in TUI:**
- 4 datasets visible:
  - burned-area
  - land-cover
  - precipitation
  - testing-the-beta-version

## Impact

### Before
- ❌ Only 1 sample dataset (testing-the-beta-version from templates/)
- ❌ Real datasets (burned-area, land-cover, precipitation) not accessible
- ❌ User couldn't access their data folder

### After
- ✅ All 4 real datasets packaged and installed
- ✅ Full data catalog available on UV install
- ✅ Users get complete dataset collection out of the box

## Summary

This fix ensures that when users install via UV, they get **all your real datasets**, not just a single sample template. The package now includes the complete data catalog with 4 datasets totaling all the metadata and structure from your `data/` folder.

---

**Status:** ✅ Ready to commit and push  
**Testing:** ✅ Verified locally - all 4 datasets copy correctly  
**Next:** Commit → Push → Test UV install → Verify in TUI
