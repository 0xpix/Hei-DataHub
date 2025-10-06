# GitHub Pages Deployment Fix - Summary

## Problem
Both user docs and developer docs workflows were deploying to the same GitHub Pages site, overwriting each other. This caused:
- User docs at `https://0xpix.github.io/Hei-DataHub/` to show dev docs after dev-docs workflow ran
- Developer docs URL `https://0xpix.github.io/Hei-DataHub/dev/` returning 404

## Solution Implemented
Modified both GitHub Actions workflows (`.github/workflows/pages.yml` and `.github/workflows/dev-docs.yml`) to:

1. **Checkout both branches** - Each workflow now checks out both `main` and `docs/devs` branches
2. **Build to combined directory** - User docs build to root, dev docs build to `/dev` subdirectory
3. **Single deployment** - Upload the combined site as one artifact to GitHub Pages

## Results
- ✅ User docs: `https://0xpix.github.io/Hei-DataHub/` (from main branch)
- ✅ Developer docs: `https://0xpix.github.io/Hei-DataHub/dev/` (from docs/devs branch)
- ✅ Site switcher links work correctly between both sites

## Files Changed on `docs/devs` Branch
- `.github/workflows/dev-docs.yml` - Modified to build combined site
- `.github/workflows/pages.yml` - Modified to build combined site

## Next Steps
You need to merge these workflow changes to the `main` branch so that:
1. When you push to `main`, it builds user docs + dev docs together
2. When you push to `docs/devs`, it builds user docs + dev docs together
3. Both deployments are consistent

### To merge workflow changes to main:
```bash
git checkout main
git pull origin main
git checkout docs/devs -- .github/workflows/pages.yml .github/workflows/dev-docs.yml
git add .github/workflows/
git commit -m "fix: Update workflows to support combined user/dev docs deployment"
git push origin main
```

### Optional: Add site-switcher.js to main branch
If you want the site switcher banner on the user docs too:
```bash
git checkout main
git checkout docs/devs -- docs/assets/site-switcher.js mkdocs.yml
git add docs/assets/site-switcher.js mkdocs.yml
git commit -m "feat: Add site switcher to user docs for easy navigation to dev docs"
git push origin main
```

## How It Works
Both workflows now:
1. Check out `main` branch to `main/` directory
2. Check out `docs/devs` branch to `docs-devs/` directory
3. Build user docs: `main/` → `combined-site/`
4. Build dev docs: `docs-devs/` → `combined-site/dev/`
5. Upload `combined-site/` to GitHub Pages

This ensures both sites are always deployed together, preventing overwrites.
