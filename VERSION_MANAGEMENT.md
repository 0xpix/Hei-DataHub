# Version Management System

This project uses `.env-version` as the **single source of truth** for version and codename information.

## Quick Start

To update version/codename everywhere:

1. Edit `.env-version`:
   ```bash
   PROJECT_VERSION=0.58.0-beta
   PROJECT_CODENAME=NewRelease
   ```

2. Commit and push:
   ```bash
   git add .env-version
   git commit -m "chore: bump version to 0.58.0-beta"
   git push
   ```

That's it! GitHub Actions will automatically:
- Update the documentation with new version/codename
- Deploy to GitHub Pages

For local docs preview:
```bash
export $(cat .env-version | xargs) && mkdocs serve
```

## For Local Development

1. **Edit `.env-version`**:
   ```bash
   PROJECT_VERSION=0.58.0-beta
   PROJECT_CODENAME=NewRelease
   ```

2. **Preview documentation locally**:
   ```bash
   export $(cat .env-version | grep -v '^#' | xargs)
   mkdocs serve
   ```

The environment variables are automatically loaded and used in docs.

## For CI/CD (GitHub Actions)

GitHub Actions automatically reads from `.env-version` file.

No repository variables needed! The workflow:
1. Loads `PROJECT_VERSION` and `PROJECT_CODENAME` from `.env-version`
2. Exports them as environment variables
3. MkDocs picks them up automatically

## How It Works

### Python Code

Python code reads from environment variables with fallback to `_version.py`:

```python
from mini_datahub.versioning import VERSION, CODENAME
```

Priority:
1. Environment variables (`PROJECT_VERSION`, `PROJECT_CODENAME`)
2. Fallback to `_version.py` (generated from `version.yaml`)

### README.md

README.md uses variable placeholders:
```markdown
![Version](https://img.shields.io/badge/version-${PROJECT_VERSION}-blue.svg)
**Latest Release:** [v${PROJECT_VERSION} "${PROJECT_CODENAME}"]
```

These are displayed as-is on GitHub, but they clearly show the intended structure.
For rendered viewing, see the documentation site.

### MkDocs Documentation

MkDocs uses the `mkdocs-macros-plugin` to inject environment variables:

```markdown
Current version: {{ project_version }}
Codename: {{ project_codename }}
```

Configuration in `mkdocs.yml`:
```yaml
extra:
  project_version: !ENV [PROJECT_VERSION, "0.0.0-dev"]
  project_codename: !ENV [PROJECT_CODENAME, "Unnamed"]
```

### YAML Configuration Files

For YAML files that the application reads, use the utility function:

```python
from mini_datahub.utils.yaml_env import load_yaml_with_env

config = load_yaml_with_env("path/to/config.yaml")
```

In your YAML files:
```yaml
version: ${PROJECT_VERSION}
codename: ${PROJECT_CODENAME}
```

## Backward Compatibility

The system maintains full backward compatibility:

- If `.env` doesn't exist, Python uses `_version.py` (generated from `version.yaml`)
- If environment variables aren't set, MkDocs uses default values
- Existing `version.yaml` and `scripts/sync_version.py` still work

## Updating Version/Codename

**One file to rule them all: `.env-version`**

```bash
# Edit .env-version
nano .env-version

# Update the values
PROJECT_VERSION=0.58.0-beta
PROJECT_CODENAME=NewRelease

# Commit and push
git add .env-version
git commit -m "chore: bump version to 0.58.0-beta"
git push
```

Done! Everything updates automatically.

## Files Involved

- **`.env-version`** - **Single source of truth** (tracked in git)
- `src/mini_datahub/versioning.py` - Python module for env-based version access
- `src/mini_datahub/_version.py` - Generated fallback (from `version.yaml`)
- `mkdocs.yml` - MkDocs config with env var bindings
- `.github/workflows/pages.yml` - CI/CD that loads `.env-version`

## Migration Notes

Historical version references in documentation (changelogs, release notes) have been preserved as-is. Only current version/codename references have been migrated to use macros.

Files that reference historical versions (e.g., "Fixed in v0.56.0") are intentionally left unchanged.

## Complete Workflow Example

When releasing version 0.58.0-beta "Packaging":

```bash
# 1. Update .env-version
cat > .env-version << 'EOF'
# Hei-DataHub Version Configuration
PROJECT_VERSION=0.58.0-beta
PROJECT_CODENAME=Packaging
EOF

# 2. (Optional) Update version.yaml for backward compat
cat > version.yaml << 'EOF'
version: "0.58.0-beta"
codename: "Packaging"
release_date: "2025-10-15"
...
EOF
python scripts/sync_version.py  # Regenerate _version.py

# 3. Preview locally (optional)
export $(cat .env-version | grep -v '^#' | xargs)
mkdocs serve

# 4. Commit and push
git add .env-version version.yaml src/mini_datahub/_version.py
git commit -m "chore: bump version to 0.58.0-beta (Packaging)"
git push

# Done! CI/CD handles the rest
```
