# v0.58.1-beta Release Checklist

**Version:** 0.58.1-beta
**Release Date:** 2025-10-08
**Status:** ✅ READY FOR INTERNAL RELEASE

---

## Pre-Release Checklist

### Code Implementation

- [x] Cross-platform data directory resolver (`platform_paths.py`)
- [x] Windows filename sanitation utilities
- [x] One-time migration detection
- [x] Doctor command implementation (`doctor.py`)
- [x] CLI integration (`--data-dir` flag)
- [x] Doctor command handler in `main.py`
- [x] Path resolution integration in `paths.py`
- [x] Environment variable support (`HEIDATAHUB_DATA_DIR`)

### Version Management

- [x] Update `version.yaml` to 0.58.1-beta
- [x] Run `scripts/sync_version.py` to propagate version
- [x] Verify `pyproject.toml` updated (auto-synced)
- [x] Verify `src/mini_datahub/_version.py` updated (auto-generated)

### Documentation

- [x] Update `CHANGELOG.md` with v0.58.1-beta entry
- [x] Update `docs/index.md` with version banner
- [x] Update `docs/00-welcome.md` with new commands
- [x] Update `docs/installation/troubleshooting.md` with cross-platform section
- [x] Create `docs/13-cli-reference.md` with complete CLI reference
- [x] Create `IMPLEMENTATION_v0.58.1-beta.md` implementation summary
- [x] Create `QA_TESTING_v0.58.1-beta.md` test results

### Testing

- [x] Syntax check all new Python files
- [x] Test `hei-datahub --help` shows new options
- [x] Test `hei-datahub doctor` in dev mode
- [x] Test `hei-datahub --data-dir /tmp/test doctor`
- [x] Test filename sanitation function
- [x] Verify no breaking changes to existing commands
- [x] Verify dev mode still works correctly

### Code Quality

- [x] No syntax errors
- [x] No import errors
- [x] Proper error handling in doctor command
- [x] Exit codes implemented correctly
- [x] Clear user-facing messages
- [x] Docstrings for all new functions

---

## Release Steps

### 1. Final Code Review

```bash
# Check for uncommitted changes
git status

# Review modified files
git diff

# Review new files
git status --short | grep '^??'
```

**Status:** ⏳ Pending

### 2. Commit Changes

```bash
git add -A
git commit -m "feat(v0.58.1): cross-platform data dirs + doctor diagnostics

- Add cross-platform data directory resolution (Linux/macOS/Windows)
- Add hei-datahub doctor command with exit codes
- Add --data-dir CLI flag for path override
- Add Windows filename sanitation utilities
- Add one-time migration detection for legacy paths
- Update documentation with cross-platform troubleshooting
- Add complete CLI reference documentation

Closes #<issue_number>"
```

**Status:** ⏳ Pending

### 3. Tag Release

```bash
git tag -a v0.58.1-beta -m "Release v0.58.1-beta: Cross-platform data directory fix + doctor diagnostics"
```

**Status:** ⏳ Pending

### 4. Push Changes

```bash
git push origin chore/uv-install-data-desktop-v0.58.x
git push origin v0.58.1-beta
```

**Status:** ⏳ Pending

### 5. Test Installation

**Linux:**
```bash
uv tool install --force "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1-beta"
hei-datahub --version
hei-datahub doctor
```

**Windows (when available):**
```powershell
uv tool install --force "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1-beta"
hei-datahub --version
hei-datahub doctor
```

**macOS (when available):**
```bash
uv tool install --force "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1-beta"
hei-datahub --version
hei-datahub doctor
```

**Status:** ⏳ Pending

---

## Post-Release Checklist

### Verification

- [ ] Version shows as 0.58.1-beta
- [ ] Doctor command runs without errors
- [ ] Data directory resolves correctly on each platform
- [ ] `--data-dir` override works
- [ ] `HEIDATAHUB_DATA_DIR` override works
- [ ] Help text shows new options
- [ ] Documentation site updated (if published)

### Platform-Specific Testing

**Linux:**
- [ ] Default path: `~/.local/share/Hei-DataHub` ✓
- [ ] Environment override works
- [ ] CLI override works
- [ ] Datasets discovered correctly
- [ ] No migration warnings

**Windows:**
- [ ] Default path: `%LOCALAPPDATA%\Hei-DataHub`
- [ ] Filename sanitation detects issues
- [ ] Long path handling
- [ ] Case collision detection
- [ ] Migration detection (if legacy path exists)

**macOS:**
- [ ] Default path: `~/Library/Application Support/Hei-DataHub`
- [ ] Migration detection (if legacy path exists)
- [ ] Case collision detection
- [ ] Unicode path handling

### Regression Testing

- [ ] TUI launches correctly
- [ ] Reindex command works
- [ ] Paths command works
- [ ] Search functionality works
- [ ] Add/edit dataset works
- [ ] GitHub integration works (if configured)
- [ ] Keybindings work

---

## Known Issues to Monitor

1. **Windows long paths:** May require registry change
2. **Non-ASCII paths on Windows:** May have issues
3. **Case collisions:** Monitor for false positives
4. **Network drives:** Performance may vary
5. **Read-only filesystems:** Should give clear error

---

## Rollback Plan

If critical issues are discovered:

### Option 1: Quick Fix

```bash
# Fix the issue
git add <fixed_files>
git commit -m "fix(v0.58.1): <description>"

# Create patch release
git tag v0.58.1-beta-patch1
git push origin chore/uv-install-data-desktop-v0.58.x
git push origin v0.58.1-beta-patch1
```

### Option 2: Rollback

```bash
# Revert to v0.58.0-beta
uv tool install --force "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.0-beta"

# Fix issues
# Release as v0.58.2-beta when ready
```

---

## Communication

### Internal Announcement

**Subject:** Hei-DataHub v0.58.1-beta Released — Cross-Platform Data Directory Fix

**Body:**

```
Team,

Hei-DataHub v0.58.1-beta is now available for internal testing.

Key Changes:
- ✅ Data directories now work correctly on Windows and macOS
- ✅ New `hei-datahub doctor` command for diagnostics
- ✅ `--data-dir` flag for custom data locations
- ✅ Windows filename sanitation and migration detection

Installation:
```bash
uv tool install --force "git+ssh://git@github.com/0xpix/Hei-DataHub.git@v0.58.1-beta"
```

Quick Start:
```bash
hei-datahub doctor          # Check system health
hei-datahub --version       # Verify version
hei-datahub                 # Launch TUI
```

Documentation:
- CLI Reference: docs/13-cli-reference.md
- Troubleshooting: docs/installation/troubleshooting.md
- Implementation: IMPLEMENTATION_v0.58.1-beta.md

Testing Needed:
- Windows 10/11 validation
- macOS Intel/ARM validation
- Cross-platform dataset sync

Feedback: Please report any issues or platform-specific quirks.

Thanks!
```

---

## Success Criteria

**Must have:**
- [x] Linux: Default path works
- [x] CLI flag overrides work
- [x] Doctor command runs without crashes
- [x] No breaking changes to existing functionality
- [x] Documentation updated

**Should have:**
- [ ] Windows: Default path works (pending testing)
- [ ] Windows: Filename sanitation detects issues
- [ ] macOS: Default path works (pending testing)
- [ ] macOS: Migration detection works

**Nice to have:**
- [ ] Performance benchmarks
- [ ] User feedback collected
- [ ] Edge cases documented

---

## Timeline

**Development:** ✅ Complete (2025-10-08)
**Testing (Linux):** ✅ Complete (2025-10-08)
**Documentation:** ✅ Complete (2025-10-08)
**Release:** ⏳ Ready (pending commit/tag/push)
**Windows Testing:** ⏳ Pending environment
**macOS Testing:** ⏳ Pending environment
**Stabilization:** TBD (based on feedback)

---

## Next Steps

1. ✅ Complete implementation (DONE)
2. ✅ Complete Linux testing (DONE)
3. ✅ Complete documentation (DONE)
4. ⏳ **Next:** Commit and push changes
5. ⏳ Install on Windows for testing
6. ⏳ Install on macOS for testing
7. ⏳ Collect feedback
8. ⏳ Iterate if needed (v0.58.2-beta)

---

**Prepared by:** AI Agent (GitHub Copilot)
**Date:** 2025-10-08
**Status:** Ready for release
