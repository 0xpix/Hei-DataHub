# Definition of Done

## Overview

This document defines when a feature, bug fix, or task is considered **complete** in Hei-DataHub. Use this as a checklist before marking work as done.

---

## General Criteria

### ✅ Code Complete

- [ ] **Functionality implemented** - Feature works as specified
- [ ] **Edge cases handled** - Boundary conditions covered
- [ ] **Error handling** - Failures handled gracefully
- [ ] **Type hints added** - All functions have type annotations
- [ ] **Docstrings written** - Public APIs documented
- [ ] **No TODO/FIXME** - All temporary markers resolved or converted to issues
- [ ] **Code reviewed** - At least one approval from maintainer
- [ ] **Follows conventions** - Adheres to project style guide

### ✅ Tests Complete

- [ ] **Unit tests pass** - All existing tests still passing
- [ ] **New tests added** - New code has test coverage
- [ ] **Integration tests** - I/O interactions tested (if applicable)
- [ ] **Edge cases tested** - Boundary conditions have tests
- [ ] **Test coverage ≥80%** - Aim for high coverage on new code
- [ ] **Manual testing done** - Feature tested in real environment

### ✅ Documentation Complete

- [ ] **README updated** - User-facing docs updated (if applicable)
- [ ] **Dev docs updated** - Architecture docs updated (if applicable)
- [ ] **Docstrings complete** - All public functions documented
- [ ] **CHANGELOG entry** - User-visible changes logged
- [ ] **Migration guide** - Breaking changes documented (if applicable)
- [ ] **Examples provided** - Usage examples in docs (if applicable)

### ✅ Quality Checks

- [ ] **Linting passes** - `ruff` and `black` checks pass
- [ ] **Type checking passes** - `mypy` reports no errors
- [ ] **CI/CD green** - All automated checks passing
- [ ] **No regressions** - Existing functionality unaffected
- [ ] **Performance acceptable** - No significant slowdowns

### ✅ Security & Privacy

- [ ] **No credentials in code** - Secrets in keyring only
- [ ] **Input validation** - User input sanitized
- [ ] **Logging secure** - No sensitive data in logs
- [ ] **SQL injection safe** - Parameterized queries only
- [ ] **Path traversal safe** - File paths validated

---

## Feature-Specific Criteria

### New Feature

- [ ] **Issue exists** - Feature request tracked in GitHub
- [ ] **Design approved** - Architecture reviewed before coding
- [ ] **User documentation** - How-to guide or tutorial added
- [ ] **CLI commands** - New commands documented in reference
- [ ] **Settings added** - Configuration options documented
- [ ] **Backwards compatible** - Or migration path provided
- [ ] **Performance tested** - No negative impact on existing features

**Example Checklist for "Add CSV Export":**

- [x] Feature works: Datasets can be exported to CSV
- [x] Edge cases: Empty datasets, special characters, large files
- [x] Tests: Unit tests for export logic, integration test for full flow
- [x] Docs: Added "How to Export" section to user guide
- [x] CLI: Documented `hei-datahub export` command
- [x] No regressions: Other export formats still work

### Bug Fix

- [ ] **Issue exists** - Bug tracked in GitHub
- [ ] **Root cause identified** - Understand why bug occurred
- [ ] **Fix verified** - Bug no longer reproducible
- [ ] **Regression test added** - Test prevents bug from returning
- [ ] **Related bugs checked** - Similar issues also fixed
- [ ] **No new bugs introduced** - Fix doesn't break other features

**Example Checklist for "Fix Keyring Timeout":**

- [x] Bug fixed: Keyring no longer times out on slow unlock
- [x] Root cause: Default timeout (5s) too aggressive
- [x] Solution: Increased to 8s, added --timeout flag
- [x] Test: Added test for slow keyring scenario
- [x] No regressions: Fast keyring still works normally

### Refactoring

- [ ] **Goal clear** - What improvement does this achieve?
- [ ] **No behavior change** - Functionality identical before/after
- [ ] **All tests pass** - No test changes needed (unless improving tests)
- [ ] **Metrics improved** - Code is more readable/maintainable/performant
- [ ] **No new dependencies** - Or dependencies justified

**Example Checklist for "Extract WebDAV Client":**

- [x] Goal: Improve testability and code organization
- [x] Behavior unchanged: All sync operations work identically
- [x] Tests pass: No test modifications needed
- [x] Code cleaner: WebDAV logic isolated in webdav_storage.py
- [x] No new deps: Used existing `requests` library

### Documentation

- [ ] **Accurate** - Information is correct and up-to-date
- [ ] **Complete** - No missing sections or placeholders
- [ ] **Clear** - Easy to understand for target audience
- [ ] **Examples included** - Code samples where helpful
- [ ] **Links work** - All cross-references valid
- [ ] **Spelling/grammar** - No typos or errors
- [ ] **Consistent style** - Matches existing documentation tone

**Example Checklist for "Auth & Sync Documentation":**

- [x] Accurate: All commands and examples tested
- [x] Complete: All auth commands documented
- [x] Clear: Step-by-step instructions provided
- [x] Examples: Setup wizard flow shown
- [x] Links: Cross-references to security docs
- [x] Proofread: No spelling errors
- [x] Style: Matches other architecture docs

---

## Layer-Specific Criteria

### Core Layer (Pure Logic)

- [ ] **No I/O operations** - No file, network, or database access
- [ ] **Pure functions** - Same input → same output
- [ ] **No side effects** - Functions don't modify global state
- [ ] **Fast execution** - Logic-only, should be instant
- [ ] **100% testable** - No mocks needed for unit tests

### Services Layer (Orchestration)

- [ ] **Coordinates core & infra** - Glue between layers
- [ ] **Error translation** - Converts infra errors to domain errors
- [ ] **Transaction handling** - Manages multi-step operations
- [ ] **Logging appropriate** - Key operations logged
- [ ] **Mocks used in tests** - Infra dependencies mocked

### Infrastructure Layer (I/O)

- [ ] **Error handling** - Network/file/DB errors handled
- [ ] **Resource cleanup** - Connections closed, files released
- [ ] **Retry logic** - Transient failures retried (if applicable)
- [ ] **Timeouts configured** - Operations have reasonable timeouts
- [ ] **Integration tests** - Real I/O tested with fixtures

### UI Layer (Textual)

- [ ] **Keyboard accessible** - All actions have keybindings
- [ ] **Responsive** - UI doesn't freeze during operations
- [ ] **Error messages clear** - Users understand what went wrong
- [ ] **Help available** - `?` shows help overlay
- [ ] **Tested with pilot** - Textual pilot tests added

---

## Release Criteria

### Patch Release (0.59.1)

Bug fixes only:

- [ ] **No new features** - Only bug fixes
- [ ] **No breaking changes** - Fully backwards compatible
- [ ] **CHANGELOG updated** - All fixes listed
- [ ] **Version bumped** - Patch number incremented
- [ ] **Tests pass** - All CI checks green

### Minor Release (0.60.0)

New features, no breaking changes:

- [ ] **New features documented** - User guide updated
- [ ] **Backwards compatible** - Old code still works
- [ ] **CHANGELOG updated** - Features and fixes listed
- [ ] **Migration tested** - Upgrade from previous version works
- [ ] **Version bumped** - Minor number incremented

### Major Release (1.0.0)

Breaking changes allowed:

- [ ] **Breaking changes documented** - Migration guide provided
- [ ] **Deprecation warnings** - Users notified in advance
- [ ] **Major features complete** - Core functionality stable
- [ ] **Documentation complete** - All features documented
- [ ] **Extensive testing** - Manual + automated testing
- [ ] **Version bumped** - Major number incremented

---

## Branch-Specific Criteria

### Feature Branch

- [ ] **Descriptive name** - `feature/add-csv-export`
- [ ] **Up to date** - Rebased on latest `main`
- [ ] **No merge commits** - Clean linear history
- [ ] **Atomic commits** - Each commit is logical unit
- [ ] **All criteria met** - Above checklists completed

### Pull Request

- [ ] **Title follows conventions** - `feat(export): add CSV export`
- [ ] **Description complete** - What, why, how explained
- [ ] **Linked to issue** - `Closes #123`
- [ ] **CI checks pass** - All automated tests green
- [ ] **Approved by reviewer** - At least 1 approval
- [ ] **No merge conflicts** - Ready to merge
- [ ] **Draft removed** - Not in draft state

---

## Examples

### Example 1: Feature Complete

**Feature:** Add date range filters to search

**Checklist:**

✅ **Code Complete**
- [x] Date range parsing implemented
- [x] FTS5 query builder supports date filters
- [x] Invalid dates raise SearchError
- [x] Type hints on all new functions
- [x] Docstrings explain date format

✅ **Tests Complete**
- [x] Unit tests for date parsing
- [x] Unit tests for query builder
- [x] Integration test for end-to-end search
- [x] Edge case: invalid format
- [x] Edge case: date_after > date_before
- [x] Coverage: 85%

✅ **Documentation Complete**
- [x] Updated search documentation
- [x] Added examples to docstrings
- [x] CHANGELOG entry added
- [x] CLI reference updated

✅ **Quality Checks**
- [x] Ruff passes
- [x] Black passes
- [x] Mypy passes
- [x] CI green

**Result:** ✅ **Feature is DONE**

### Example 2: Bug Fix Complete

**Bug:** Keyring timeout on slow unlock

**Checklist:**

✅ **Code Complete**
- [x] Increased timeout from 5s to 8s
- [x] Added --timeout flag for user override
- [x] Error message explains timeout issue

✅ **Tests Complete**
- [x] Test verifies timeout respected
- [x] Test verifies --timeout flag works
- [x] Regression test added

✅ **Documentation Complete**
- [x] CLI reference updated with --timeout
- [x] CHANGELOG entry added
- [x] Troubleshooting section updated

✅ **Quality Checks**
- [x] All tests pass
- [x] No regressions

**Result:** ✅ **Bug fix is DONE**

### Example 3: NOT Done

**Feature:** Add CSV export

**Checklist:**

⚠️ **Code Complete**
- [x] Export logic implemented
- [ ] ❌ Edge case not handled: special characters in CSV
- [ ] ❌ Missing type hints on export_to_csv()

⚠️ **Tests Complete**
- [x] Happy path tested
- [ ] ❌ Missing test for special characters
- [ ] ❌ Missing test for large files

⚠️ **Documentation Complete**
- [ ] ❌ User guide not updated
- [ ] ❌ CLI reference missing export command

**Result:** ❌ **Feature is NOT DONE**

**Next Steps:**
1. Add special character handling
2. Add type hints
3. Write missing tests
4. Update documentation

---

## Quick Reference

**Is my work done?**

1. ✅ **Works:** Feature/fix functions correctly
2. ✅ **Tested:** Code has tests, tests pass
3. ✅ **Documented:** Docs updated, changelog entry
4. ✅ **Reviewed:** Approved by maintainer
5. ✅ **Quality:** Linting, typing, CI all green
6. ✅ **Secure:** No security issues

**If ALL ✅ → Work is DONE**

**If ANY ❌ → Work is NOT DONE**

---

## Related Documentation

- **[Workflow](workflow.md)** - Contribution process
- **[Code Review](code-review.md)** - Review criteria
- **[Commit Conventions](commits.md)** - Commit format
- **[Architecture Overview](../architecture/overview.md)** - System design

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
