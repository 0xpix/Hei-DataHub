# Commit Conventions

## Overview

Hei-DataHub follows the **Conventional Commits** specification for clear, structured commit messages that enable automated changelog generation and semantic versioning.

---

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Components

#### Type (Required)

The commit type describes the category of change:

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(search): add date range filters` |
| `fix` | Bug fix | `fix(auth): prevent keyring timeout` |
| `docs` | Documentation only | `docs(cli): add auth examples` |
| `style` | Code style (formatting, no logic change) | `style: format with black` |
| `refactor` | Code refactoring | `refactor(sync): extract WebDAV client` |
| `perf` | Performance improvement | `perf(search): optimize FTS5 queries` |
| `test` | Adding/fixing tests | `test(auth): add keyring tests` |
| `build` | Build system or dependencies | `build: upgrade textual to 0.47` |
| `ci` | CI/CD configuration | `ci: add coverage reporting` |
| `chore` | Maintenance tasks | `chore: update dependencies` |
| `revert` | Revert previous commit | `revert: revert "feat(search): ..."` |
| `security` | Security fixes | `security(logging): mask credentials` |

#### Scope (Optional but Recommended)

The scope specifies what part of the codebase is affected:

| Scope | Area |
|-------|------|
| `auth` | Authentication, credentials, WebDAV |
| `search` | Search, FTS5, autocomplete |
| `sync` | Background sync |
| `ui` | Terminal UI, views, widgets |
| `cli` | Command-line interface |
| `db` | Database, persistence |
| `config` | Configuration |
| `infra` | Infrastructure layer |
| `services` | Services layer |
| `core` | Core business logic |
| `docs` | Documentation |
| `tests` | Test suite |

#### Subject (Required)

- **Imperative mood**: Use "add" not "added" or "adds"
- **Lowercase**: Start with lowercase letter
- **No period**: Don't end with a period
- **50 characters max**: Keep it concise

**Good:**
```
add date range filters for FTS5 queries
fix keyring timeout on slow unlock
update authentication documentation
```

**Bad:**
```
Added date range filters.
Fixed a bug
Update docs
```

#### Body (Optional)

Explain the **what** and **why**, not the **how**.

- Wrap at 72 characters
- Separate from subject with blank line
- Use bullet points for multiple changes

**Example:**

```
feat(ui): add dark mode theme

- Add dark color scheme in theme.py
- Update widget styles for dark mode
- Add theme toggle in settings

Dark mode reduces eye strain for long sessions and
is requested by multiple users in #42.
```

#### Footer (Optional)

Reference related issues or breaking changes:

```
Closes #123
Fixes #456
Refs #789

BREAKING CHANGE: config format changed to TOML
```

---

## Examples

### Simple Commit

```
feat(search): add wildcard support
```

### Commit with Scope and Body

```
fix(auth): prevent keyring timeout on slow unlock

Increase default timeout from 5s to 8s and add
--timeout flag for users to override.

Fixes #234
```

### Breaking Change

```
feat(config)!: migrate from JSON to TOML

BREAKING CHANGE: Configuration file format changed.
Users must run `hei-datahub migrate-config` to convert
existing config.json to config.toml.

Migration tool included in this release.

Refs #156
```

### Multiple Changes

```
refactor(services): extract WebDAV client to separate module

- Move WebDAV logic from sync.py to webdav_storage.py
- Add WebDAVStorage class with clean interface
- Update tests to use new module structure
- Improve error handling for network failures

This improves testability and code organization.
```

---

## Rules

### DO ✅

- **Be specific**: Describe the actual change
- **Use imperative mood**: "add" not "added"
- **Keep subject concise**: Under 50 characters
- **Reference issues**: Use `Closes #123` or `Fixes #456`
- **Explain why**: In the body, explain motivation
- **Group related changes**: Multiple small commits > one large commit

### DON'T ❌

- **Vague messages**: "fix bug", "update code"
- **Mix unrelated changes**: One commit = one logical change
- **Forget the scope**: Always include scope when applicable
- **Skip the body**: Explain non-trivial changes
- **Use past tense**: "added feature" → "add feature"

---

## Commit Workflow

### 1. Stage Changes

```bash
# Stage specific files
git add src/mini_datahub/auth/setup.py tests/auth/test_setup.py

# Review staged changes
git diff --staged
```

### 2. Write Commit Message

```bash
# Interactive commit
git commit

# Inline commit (for simple changes)
git commit -m "feat(auth): add token validation"
```

### 3. Edit Message in Editor

If using `git commit` (recommended for complex commits):

```
feat(auth): add WebDAV token validation

- Validate token format before storing
- Add comprehensive error messages
- Update setup wizard with validation step

Token validation prevents common setup errors
where users paste malformed tokens.

Closes #145
```

### 4. Amend if Needed

```bash
# Forgot to add a file
git add forgotten_file.py
git commit --amend --no-edit

# Fix commit message
git commit --amend
```

---

## Automated Tools

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# Conventional commit linter
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security)(\(.+\))?: .{1,50}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "❌ Commit message does not follow Conventional Commits format"
    echo "Format: <type>(<scope>): <subject>"
    exit 1
fi
```

### Commitizen

Install commitizen for interactive commit creation:

```bash
pip install commitizen

# Interactive commit
cz commit
```

---

## Changelog Generation

Commits following this convention enable automated changelog:

```bash
# Generate changelog
git log --pretty=format:"%s" --grep="^feat" > CHANGELOG.md
```

**Output:**

```markdown
## [0.59.0] - 2025-10-25

### Features
- feat(auth): add WebDAV token validation
- feat(search): add date range filters
- feat(ui): add dark mode theme

### Bug Fixes
- fix(sync): prevent duplicate uploads
- fix(db): handle concurrent writes

### Performance
- perf(search): optimize FTS5 queries
```

---

## GitHub Integration

### Pull Request Title

Use the same format:

```
feat(search): add date range filters for FTS5 queries
```

### PR Description Template

```markdown
## Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Refactor

## What
Brief summary of changes.

## Why
Motivation and context.

## How
Implementation approach.

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done

## Checklist
- [ ] Follows commit conventions
- [ ] Updated documentation
- [ ] Tests pass locally

Closes #123
```

---

## Related Documentation

- **[Workflow](workflow.md)** - Full contribution workflow
- **[Architecture Overview](../architecture/overview.md)** - System architecture
- **[Versioning Policy](../versioning.md)** - Semantic versioning

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
