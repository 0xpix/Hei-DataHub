
Understanding Semantic Versioning (SemVer) and how Hei-DataHub applies it.

---

## What is Semantic Versioning?

**Semantic Versioning (SemVer)** is a versioning scheme that uses three numbers to convey meaning about changes:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

**Example:** `0.55.0-beta`

---

## Version Components

### MAJOR

**When to increment:** Incompatible API changes.

**What it means:**

- Breaking changes that require users to modify their code or workflows
- After **1.0.0**, any breaking change bumps MAJOR

**Examples:**

- Remove a command-line argument
- Change database schema incompatibly
- Rename core functions

**Pre-1.0 note:** With `MAJOR = 0`, many teams treat **MINOR** as "mini-major"—breaking changes may occur when bumping MINOR during the beta phase.

---

### MINOR

**When to increment:** New functionality in a backward-compatible manner.

**What it means:**

- New features added
- No breaking changes to existing functionality
- Users can upgrade safely without code changes

**Examples:**

- Add a new command (`hei-datahub export`)
- Add optional metadata fields
- Add new keyboard shortcuts

**Pre-1.0 note:** During `0.y.z` development, MINOR bumps **may** include breaking changes. Always check the Changelog.

---

### PATCH

**When to increment:** Backward-compatible bug fixes and small tweaks.

**What it means:**

- Fixes bugs without changing behavior
- Performance improvements
- Documentation updates
- No new features

**Examples:**

- Fix search ranking bug
- Fix validation error message
- Improve database indexing speed

---

### PRERELEASE

**Format:** `-alpha`, `-beta`, `-rc.1`, etc.

**What it means:**

- Version is not yet stable
- May have bugs or incomplete features
- For testing and feedback

**Ordering:**

```
0.55.0-alpha < 0.55.0-beta < 0.55.0-rc.1 < 0.55.0
```

**Current:** Hei-DataHub is in **beta** (`-beta` suffix).

---

### BUILD

**Format:** `+20250104` (optional build metadata)

**What it means:**

- Build number or commit hash
- Ignored for version precedence

**Example:** `0.55.0-beta+005500`

---

## Hei-DataHub Versioning Policy

### Beta Era (v0.55.x and earlier)

**Current status:** Hei-DataHub is in **beta**.

**Versioning rules:**

- **MAJOR = 0:** Indicates pre-1.0 development
- **MINOR bumps** (0.55 → 0.56) **may** include breaking changes
- **PATCH bumps** (0.55.0 → 0.55.1) are backward-compatible bug fixes

**Documentation tracking:**

- This manual tracks **v0.55.x (beta)**
- PATCH releases (0.55.1, 0.55.2, ...) update the **same docs line**
- MINOR releases (0.56.0, 0.57.0, ...) may introduce new docs or major updates

---

### After 1.0.0 (Stable)

**When 1.0.0 ships:**

- **Strict SemVer:** Breaking changes bump MAJOR
- **MINOR bumps:** New features only (backward-compatible)
- **PATCH bumps:** Bug fixes only

**Documentation:**

- Each MAJOR version gets its own docs
- MINOR/PATCH updates refresh the current MAJOR docs

---

## Version History

### Pre-0.50.0 (Early Development)

- Experimental features
- Rapid iteration
- Limited documentation

### 0.50.0 → 0.54.x (Beta Stabilization)

- Core features solidified
- Search engine optimized
- GitHub integration added

### **0.55.0-beta (Current)**

- **"Clean Architecture" release**
- Auto-stash for PR workflow
- Improved gitignore handling
- Dual command support (`hei-datahub` and `mini-datahub`)

---

## How to Check Your Version

### Command Line

```bash
hei-datahub --version
```

**Output:** `Hei-DataHub 0.55.0-beta`

---

### Detailed Version Info

```bash
hei-datahub --version-info
```

**Output:**

```
Hei-DataHub 0.55.0-beta
Build: 005500
Release Date: 2025-01-04
Python: 3.11.x
Platform: Linux-x86_64
Repository: https://github.com/0xpix/Hei-DataHub
```

---

### In TUI

Version displayed in:

- Settings screen footer
- Update notification (if newer version available)

---

## Upgrade Strategy

### Patch Upgrades (0.55.0 → 0.55.1)

**Safe to upgrade:** No breaking changes.

**Steps:**

```bash
cd Hei-DataHub
git pull origin main
source .venv/bin/activate
pip install -e .
```

**No data migration needed.**

---

### Minor Upgrades (0.55.x → 0.56.0)

**May have breaking changes.** Always read the Changelog first.

**Steps:**

1. **Backup data:**
    ```bash
    cp -r data/ data-backup/
    cp db.sqlite db.sqlite.backup
    ```

2. **Pull updates:**
    ```bash
    git pull origin main
    ```

3. **Check Changelog:**
    ```bash
    cat docs/99-changelog.md
    ```

4. **Reinstall:**
    ```bash
    pip install -e .
    ```

5. **Reindex if needed:**
    ```bash
    hei-datahub reindex
    ```

---

### Major Upgrades (1.0.0 → 2.0.0)

**Breaking changes guaranteed.** Migration guide provided.

**Steps:**

1. Read migration guide (`MIGRATION_vX.md`)
2. Backup all data
3. Follow migration steps
4. Test thoroughly

---

## Staying Up to Date

### Auto-Check for Updates

**Default:** Enabled (`auto_check_updates: true`)

**Behavior:**

- On TUI launch, checks GitHub API once per week
- Displays notification if newer version available

**Disable:**

```json
{
  "auto_check_updates": false
}
```

---

### Manual Check

```bash
# Check GitHub releases
curl -s https://api.github.com/repos/0xpix/Hei-DataHub/releases/latest | grep tag_name
```

---

### Subscribe to Releases

**GitHub Watch:**

1. Go to [Hei-DataHub repo](https://github.com/0xpix/Hei-DataHub)
2. Click "Watch" → "Custom" → "Releases"
3. Get notified of new releases

---

## Release Cadence

### Current (Beta)

- **PATCH releases:** As needed (bug fixes)
- **MINOR releases:** ~1-2 months (new features)

### Post-1.0.0 (Stable)

- **PATCH releases:** Weekly or bi-weekly (bug fixes)
- **MINOR releases:** Monthly or quarterly (features)
- **MAJOR releases:** Yearly or as needed (breaking changes)

---

## Changelog Updates

**Every release PR must:**

1. Update `docs/99-changelog.md` with new version entry
2. List user-visible changes (features, fixes, breaking changes)
3. Link to relevant issues/PRs

**Example entry:**

```markdown
## [0.55.1-beta] - 2024-10-15

### Fixed

- Search ranking now correctly prioritizes name matches (#42)
- Fixed validation error for date fields with time component (#45)

### Changed

- Improved search debounce from 200ms to 150ms
```

---

## Choosing the Right Docs Version

**Rule:** Match the manual to your installed version.

**Examples:**

| Installed Version | Use These Docs |
|-------------------|----------------|
| 0.55.0-beta       | v0.55.x manual (this site) |
| 0.55.1-beta       | v0.55.x manual (this site) |
| 0.56.0-beta       | v0.56.x manual (future) |
| 1.0.0             | v1.x manual (future) |

**Tip:** Docs version shown in homepage banner.

---

## Deprecation Policy

### Pre-1.0.0

- Features may be removed without deprecation warnings
- Always check Changelog for breaking changes

### Post-1.0.0

- **Deprecation warnings:** At least one MINOR release before removal
- **Grace period:** Minimum 3 months between deprecation and removal

**Example:**

```
0.60.0: Feature X deprecated (warning added)
0.61.0: Feature X still works (warning remains)
0.62.0: Feature X removed (breaking change → bump to 0.62.0 or 1.0.0)
```

---

## Version Comparison Examples

### Is 0.55.1 newer than 0.55.0?

**Yes.** PATCH bumped (bug fixes).

### Is 0.56.0 newer than 0.55.9?

**Yes.** MINOR bumped (new features or breaking changes).

### Is 1.0.0 newer than 0.99.0?

**Yes.** MAJOR bumped (stable release, strict SemVer applies).

### Is 0.55.0-beta newer than 0.55.0-alpha?

**Yes.** Beta comes after alpha in prerelease ordering.

### Is 0.55.0 newer than 0.55.0-beta?

**Yes.** Release version is higher than prerelease.

---

## Version Pinning

If you need to pin a specific version:

```bash
# In requirements.txt
mini-datahub==0.55.0-beta

# Or in pyproject.toml
dependencies = ["mini-datahub==0.55.0"]
```

**Tip:** Pin MINOR version for stability:

```bash
mini-datahub>=0.55.0,<0.56.0
```

---

## Related Resources

- **[Changelog](99-changelog.md)** — Detailed release notes
- **[SemVer Specification](https://semver.org/)** — Official SemVer docs
- **[GitHub Releases](https://github.com/0xpix/Hei-DataHub/releases)** — All releases

---

## Questions?

- **Is version X compatible with my data?** → Check Changelog for migration notes
- **When will 1.0.0 ship?** → Watch GitHub Milestones
- **Can I stay on 0.55.x forever?** → Yes, but you'll miss bug fixes and features
- **How do I rollback?** → `git checkout v0.55.0` and reinstall

---

## Next Steps

- **[Changelog](99-changelog.md)** — See what's new in each release
- **[Getting Started](01-getting-started.md)** — Install the latest version
- **[FAQ](90-faq.md)** — Troubleshooting upgrade issues
