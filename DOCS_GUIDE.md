# Documentation Guide

This repository has three separate documentation sites that are built and deployed independently.

## Documentation Sites

### 1. User Documentation (Main Site)
- **Published URL:** https://0xpix.github.io/Hei-DataHub
- **Local Dev:** `make docs-serve` (http://localhost:8000)
- **Config File:** `mkdocs.yml`
- **Source Directory:** `docs/`
- **Purpose:** User-facing documentation, installation guides, how-tos

### 2. Developer Documentation (Obfuscated Path)
- **Published URL:** https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1
- **Local Dev:** `make docs-dev-serve` (http://localhost:8001)
- **Config File:** `mkdocs-dev.yml`
- **Source Directory:** `dev-docs/`
- **Purpose:** Architecture, API reference, contributor guides

### 3. Tutorial Documentation
- **Published URL:** https://0xpix.github.io/Hei-DataHub/tutorial
- **Local Dev:** `make docs-tutorial-serve` (http://localhost:8002)
- **Config File:** `mkdocs-tutorial.yml`
- **Source Directory:** `tutorial-docs/`
- **Purpose:** Step-by-step learning guides for building with Hei-DataHub

## Quick Start

### Serve Documentation Locally

```bash
# User documentation (port 8000)
make docs-serve

# Developer documentation (port 8001)
make docs-dev-serve

# Tutorial documentation (port 8002)
make docs-tutorial-serve
```

### View All Available Make Targets
```bash
make help
```

## Manual Commands

If you prefer not to use Make:

```bash
# User docs
mkdocs serve

# Developer docs
mkdocs serve -f mkdocs-dev.yml -a localhost:8001

# Tutorial docs
mkdocs serve -f mkdocs-tutorial.yml -a localhost:8002
```

## Building Static Sites

```bash
# Build user docs
mkdocs build

# Build developer docs
mkdocs build -f mkdocs-dev.yml --site-dir dev-site

# Build tutorial docs
mkdocs build -f mkdocs-tutorial.yml --site-dir tutorial-site
```

## Deployment

All three documentation sites are automatically deployed to GitHub Pages when changes are pushed to the `main` branch via the `.github/workflows/pages.yml` workflow.

The workflow:
1. Builds user docs to `combined-site/`
2. Builds developer docs to `combined-site/x9k2m7n4p8q1/`
3. Builds tutorial docs to `combined-site/tutorial/`
4. Deploys the combined site to GitHub Pages

## Documentation Structure

```
docs/                    # User documentation
dev-docs/                # Developer documentation
tutorial-docs/           # Tutorial documentation
mkdocs.yml              # User docs config
mkdocs-dev.yml          # Developer docs config
mkdocs-tutorial.yml     # Tutorial docs config
```

## Troubleshooting

### 404 Errors on Published Site

If you're seeing 404 errors:

1. **Check the correct URL:**
   - User docs: `https://0xpix.github.io/Hei-DataHub`
   - Dev docs: `https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1` (NOT `/dev`)
   - Tutorial docs: `https://0xpix.github.io/Hei-DataHub/tutorial`

2. **Verify the workflow completed:**
   - Go to GitHub Actions tab
   - Check that "Deploy Docs to GitHub Pages" workflow succeeded

3. **Check for broken internal links:**
   - Serve docs locally and test navigation
   - Verify relative paths in markdown files

### Local Serving Issues

If `mkdocs serve` fails:

1. **Install dependencies:**
   ```bash
   pip install -r docs/requirements.txt
   pip install -r dev-docs/requirements.txt
   pip install -r tutorial-docs/requirements.txt
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.10+
   ```

3. **Clear build cache:**
   ```bash
   rm -rf site/ dev-site/ tutorial-site/
   ```

## Contributing to Documentation

1. Make changes to the appropriate `docs/`, `dev-docs/`, or `tutorial-docs/` directory
2. Test locally with `make docs-serve`, `make docs-dev-serve`, or `make docs-tutorial-serve`
3. Commit and push to `main` branch
4. GitHub Actions will automatically deploy the updated docs

## Notes

- The developer docs use an obfuscated path (`/x9k2m7n4p8q1`) for SEO/security reasons
- All three sites share the same GitHub Pages deployment
- Local development uses different ports (8000, 8001, 8002) so you can run them simultaneously
