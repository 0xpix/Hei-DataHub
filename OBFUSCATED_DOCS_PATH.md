# Obfuscated Developer Docs Path

## Overview
The developer documentation is now deployed to an obfuscated path to prevent casual discovery.

## URLs

### Before:
- User Docs: `https://0xpix.github.io/Hei-DataHub/`
- Dev Docs: `https://0xpix.github.io/Hei-DataHub/dev/` ❌ (easily guessable)

### After:
- User Docs: `https://0xpix.github.io/Hei-DataHub/`
- Dev Docs: `https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1/dev/` ✅ (obfuscated)

## Access Method

The developer docs are **only accessible via the vim command**:

1. Go to the user manual: `https://0xpix.github.io/Hei-DataHub/`
2. Press `:` (colon key)
3. Type `dev`
4. Press Enter
5. You'll be redirected to the obfuscated path

## Security Benefits

✅ **Not guessable** - Random alphanumeric string in path  
✅ **Not indexed** - Search engines won't easily find it  
✅ **Not discoverable** - No direct links from user docs  
✅ **Vim command required** - Must know the special command  

## Technical Implementation

### Files Changed:

**Main Branch:**
- `docs/assets/vim-navigation.js` - Updated devDocsUrl to obfuscated path
- `.github/workflows/pages.yml` - Builds dev docs to obfuscated path

**docs/devs Branch:**
- `docs/assets/vim-navigation.js` - Updated devDocsUrl
- `.github/workflows/dev-docs.yml` - Builds to obfuscated path  
- `mkdocs-dev.yml` - Updated site_url

### Obfuscation String:
`x9k2m7n4p8q1` - This is the secret path segment

## Changing the Obfuscation Key

If you want to change the obfuscated path in the future:

1. Choose a new random string (e.g., `a7j3h9m2k5n8`)
2. Update in **both branches** (main and docs/devs):
   - `docs/assets/vim-navigation.js` - config.devDocsUrl
   - `.github/workflows/pages.yml` - build path
   - `.github/workflows/dev-docs.yml` - build path (docs/devs branch)
   - `mkdocs-dev.yml` - site_url (docs/devs branch)
3. Commit and push both branches
4. Wait for GitHub Actions to redeploy

### Generate Random String:

```bash
# On Linux/Mac:
openssl rand -hex 6 | cut -c1-12

# Or:
cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 12 | head -n 1
```

## Important Notes

⚠️ **This is security through obscurity**, not true authentication  
⚠️ Anyone with the URL can still access the docs  
⚠️ The path may leak through browser history, logs, etc.  
⚠️ For true security, consider adding authentication (GitHub Pages doesn't support this natively)

## Testing

After deployment, verify:

1. ✅ User docs work: `https://0xpix.github.io/Hei-DataHub/`
2. ✅ Obfuscated dev docs work: `https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1/dev/`
3. ✅ Old dev docs 404: `https://0xpix.github.io/Hei-DataHub/dev/` (should not exist)
4. ✅ Vim command works: Type `:dev` on user manual

## Status

- ✅ Committed to main branch
- ✅ Committed to docs/devs branch
- ⏳ Waiting for GitHub Actions deployment
- ⏳ Will be live after next push triggers workflow
