# Version Management System

This project uses environment variables as the single source of truth for version and codename information.

## For Local Development

1. **Create `.env` file** (if it doesn't exist):
   ```bash
   cp .env.example .env
   ```

2. **Update version/codename** in `.env`:
   ```bash
   PROJECT_VERSION=0.58.0-beta
   PROJECT_CODENAME=NewRelease
   ```

3. **Rebuild documentation** to see changes:
   ```bash
   mkdocs build
   ```

## For CI/CD (GitHub Actions)

Set **Repository Variables** (Settings → Secrets and variables → Actions → Variables):

- `PROJECT_VERSION`: e.g., `0.58.0-beta`
- `PROJECT_CODENAME`: e.g., `NewRelease`

The workflows will automatically use these values when building documentation.

## How It Works

### Python Code

Python code reads from environment variables with fallback to `_version.py`:

```python
from mini_datahub.versioning import VERSION, CODENAME
```

Priority:
1. Environment variables (`PROJECT_VERSION`, `PROJECT_CODENAME`)
2. Fallback to `_version.py` (generated from `version.yaml`)

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

### Method 1: Environment Variables (Recommended)

**Local:**
```bash
# Edit .env
PROJECT_VERSION=0.58.0-beta
PROJECT_CODENAME=NewRelease
```

**CI/CD:**
Update Repository Variables in GitHub Settings.

### Method 2: Traditional (Still Supported)

1. Edit `version.yaml`
2. Run `python scripts/sync_version.py`
3. This regenerates `_version.py` with the new values

## Migration Notes

Historical version references in documentation (changelogs, release notes) have been preserved as-is. Only current version/codename references have been migrated to use macros.

Files that reference historical versions (e.g., "Fixed in v0.56.0") are intentionally left unchanged.
