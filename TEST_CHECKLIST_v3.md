# Testing Checklist: GitHub PR Workflow (v3.0)

## Pre-Testing Setup

### Environment Preparation

- [ ] Fresh clone of Hei-DataHub
- [ ] `uv sync --python /usr/bin/python --dev` completed
- [ ] Virtual environment activated
- [ ] Create test catalog repository on GitHub
- [ ] Clone catalog repo locally
- [ ] Generate fine-grained PAT with correct permissions

### Test Data

- [ ] Create sample catalog repo: `test-datahub-catalog`
- [ ] Add `.gitignore` from `catalog-gitignore-example`
- [ ] Initial commit and push

---

## Test Suite 1: Settings Screen

### Access & Navigation

- [ ] Launch app: `mini-datahub`
- [ ] Press `S` from home screen → Settings opens
- [ ] Press `q` → Returns to home screen
- [ ] Press `S` again → Settings reopens (persistent)

### Form Fields

- [ ] All input fields visible and focusable
- [ ] Tab navigation works across fields
- [ ] Password field masks token (shows dots)
- [ ] Form scrollable on small terminal (24 rows)

### Save Without Token

- [ ] Fill in Owner, Repo, Username
- [ ] Leave Token empty
- [ ] Click "Save Settings"
- [ ] Should succeed with warning about no token

### Test Connection

#### Valid Credentials

- [ ] Fill in all fields with valid data
- [ ] Click "Test Connection"
- [ ] Status shows "Testing connection..."
- [ ] Success: "✓ Connected with push access" (if team member)
- [ ] Or: "✓ Connected (read-only, will use fork workflow)" (if contributor)
- [ ] App notification shows "Connection successful!"

#### Invalid Credentials

- [ ] Enter wrong token
- [ ] Click "Test Connection"
- [ ] Status shows "✗ Authentication failed: 401"
- [ ] App notification shows error

#### Non-existent Repository

- [ ] Enter non-existent repo name
- [ ] Click "Test Connection"
- [ ] Status shows "✗ Repository not found"

#### Network Offline

- [ ] Disconnect network
- [ ] Click "Test Connection"
- [ ] Status shows "✗ Connection timeout" or "Connection error"

### Save Settings

- [ ] Fill in all fields correctly
- [ ] Click "Save Settings"
- [ ] Status shows "✓ Settings saved!"
- [ ] App notification appears
- [ ] Exit and relaunch app
- [ ] Press `S` → Settings preserved (token masked)

### Remove Token

- [ ] With token saved
- [ ] Click "Remove Token"
- [ ] Status shows "Token removed"
- [ ] Token field clears
- [ ] Exit and relaunch
- [ ] Press `S` → Token field empty (confirmed removed)

### Keyboard Shortcuts

- [ ] `Ctrl+S` saves settings
- [ ] `Esc` cancels and returns to home
- [ ] `q` cancels and returns to home

---

## Test Suite 2: PR Workflow (Team Member with Push Access)

### Setup

- [ ] Configure Settings with team member credentials
- [ ] Test Connection succeeds with "push access"
- [ ] Catalog repo path points to local clone
- [ ] Local clone on `main` branch, up to date

### Happy Path: Create PR

- [ ] Press `A` to add dataset
- [ ] Fill in:
  - Name: "Test Weather Data"
  - Description: "Hourly observations"
  - Source: "https://example.com/weather.csv"
  - Storage: "s3://test-bucket/weather/"
  - (Leave other fields optional)
- [ ] Press `Ctrl+S` to save

**Expected Behavior:**

- [ ] Brief notification: "Creating PR..."
- [ ] Success notification: "✓ PR #X created!"
- [ ] Returns to Details screen
- [ ] Go to GitHub web UI → PR exists
- [ ] PR title: "Add dataset: Test Weather Data (test-weather-data)"
- [ ] PR body formatted correctly with table
- [ ] PR branch: `add/test-weather-data-<timestamp>`
- [ ] PR base: `main`
- [ ] Labels applied (if configured)
- [ ] Reviewers assigned (if configured)

### Verify Git State

```bash
cd /path/to/catalog
git log --oneline -5
# Should see commit: "feat(dataset): add test-weather-data — Test Weather Data"

git branch -a
# Should see feature branch

ls data/test-weather-data/
# Should contain metadata.yaml

cat data/test-weather-data/metadata.yaml
# Should match form data
```

### Multiple PRs

- [ ] Add second dataset: "Test Financial Data"
- [ ] Press `Ctrl+S`
- [ ] Second PR created
- [ ] Different branch name (newer timestamp)
- [ ] Both PRs visible on GitHub
- [ ] No conflicts between branches

---

## Test Suite 3: PR Workflow (External Contributor - Fork)

### Setup

- [ ] Create new GitHub account or use non-team account
- [ ] Generate PAT for this account
- [ ] Configure Settings with contributor credentials
- [ ] Test Connection: "read-only, will use fork workflow"

### Fork Creation

- [ ] Add dataset (any valid data)
- [ ] Press `Ctrl+S`
- [ ] Notification: "Creating PR..." (may take longer)
- [ ] Fork created automatically on contributor account
- [ ] Check GitHub: Fork exists at `contributor/test-datahub-catalog`

### Cross-Repo PR

- [ ] PR created successfully
- [ ] PR head: `contributor:add/dataset-<timestamp>`
- [ ] PR base: `your-org:main`
- [ ] PR visible on **original repo** (not fork)
- [ ] Maintainers can review and merge

---

## Test Suite 4: Offline Handling

### Save While Offline

- [ ] Disconnect network
- [ ] Add dataset: "Offline Test Dataset"
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Dataset saved locally (check YAML file)
- [ ] Warning notification: "Saved locally. Couldn't publish PR. Retry from Outbox."
- [ ] No error crash

### Outbox Queue

- [ ] Press `P` to open Outbox
- [ ] Task visible in table:
  - Dataset ID: `offline-test-dataset`
  - Status: `⏳ pending` or `❌ failed`
  - Created timestamp
  - Error message snippet

### Retry from Outbox

- [ ] Reconnect network
- [ ] In Outbox, select the task
- [ ] Press `R` to retry

**Expected:**

- [ ] Status changes to `🔄 retrying`
- [ ] After success: "✓ PR #X created!"
- [ ] Status changes to `✅ completed`
- [ ] Task remains in outbox (until cleared)

### Retry All Pending

- [ ] Create 3 datasets while offline
- [ ] Press `P` → 3 pending tasks
- [ ] Reconnect network
- [ ] Click "Retry All Pending"
- [ ] All tasks processed
- [ ] 3 PRs created on GitHub

### Clear Completed

- [ ] With completed tasks in outbox
- [ ] Click "Clear Completed"
- [ ] Completed tasks removed
- [ ] Pending/failed tasks remain

---

## Test Suite 5: Validation & Error Handling

### Duplicate ID (Local)

- [ ] Add dataset with ID: `test-dup`
- [ ] Save (PR created)
- [ ] Add another dataset
- [ ] Manually set ID to: `test-dup`
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Local validation fails (before git)
- [ ] Error: "Dataset ID already exists"
- [ ] Form stays open
- [ ] No commit or PR created

### Duplicate ID (Remote)

- [ ] Merge a dataset PR with ID: `remote-dup`
- [ ] In local app, add dataset
- [ ] Set ID to: `remote-dup`
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Remote uniqueness check fails
- [ ] Error: "Dataset ID 'remote-dup' already exists in repository"
- [ ] No commit or PR

### Invalid ID Format

- [ ] Add dataset
- [ ] Set ID to: `UPPERCASE`
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Validation fails
- [ ] Error shows pattern requirement
- [ ] Form stays open

### Missing Required Fields

- [ ] Add dataset
- [ ] Leave Description empty
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Validation fails
- [ ] Error: "Description is required"
- [ ] Focus moves to Description field

### Network Errors

#### Push Fails (No Network)

- [ ] Start adding dataset (network on)
- [ ] Disconnect network mid-save
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Git operations fail
- [ ] Task queued to outbox
- [ ] Friendly error message

#### GitHub API Fails

- [ ] Revoke token on GitHub
- [ ] Add dataset
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Push may succeed (git uses credentials)
- [ ] PR creation fails
- [ ] Task queued to outbox
- [ ] Error: "Authentication failed"

---

## Test Suite 6: Edge Cases

### Catalog Path Not Git Repo

- [ ] Settings: Set catalog path to non-git directory
- [ ] Add dataset, save

**Expected:**

- [ ] Error: "Not a git repository"
- [ ] Dataset saved locally only
- [ ] Task not queued (invalid config)

### Catalog Path Doesn't Exist

- [ ] Settings: Set path to `/does/not/exist`
- [ ] Add dataset, save

**Expected:**

- [ ] Error: "Catalog repository path does not exist"
- [ ] Dataset saved locally

### Branch Name Collision

- [ ] Manually create branch: `add/test-123-20241003-1200`
- [ ] Add dataset with exact same ID and timestamp

**Expected:**

- [ ] Branch creation should handle collision
- [ ] Or unique timestamp ensures no collision

### Very Long Dataset Name

- [ ] Add dataset with 200-character name
- [ ] Save

**Expected:**

- [ ] ID truncated/generated appropriately
- [ ] Commit message not broken
- [ ] PR title not broken

### Special Characters in Name

- [ ] Name: "Test & Data (2024) – Version #1"
- [ ] Save

**Expected:**

- [ ] ID slugified correctly: `test-data-2024-version-1`
- [ ] No git errors

### URL Probe During Save

- [ ] Add dataset with valid HTTP URL
- [ ] Click "Probe URL" (fills format/size)
- [ ] Press `Ctrl+S`

**Expected:**

- [ ] Probed data included in metadata
- [ ] Probed data in PR body

---

## Test Suite 7: Integration with Existing Features

### Search Index Updated

- [ ] Add dataset via PR workflow
- [ ] Dataset saved and PR created
- [ ] Return to home screen
- [ ] Search for dataset name

**Expected:**

- [ ] Dataset appears in search results
- [ ] FTS5 index automatically updated

### Details Screen

- [ ] After PR creation, view dataset details
- [ ] All fields displayed correctly
- [ ] `y` copies source to clipboard
- [ ] `o` opens source URL (if valid)

### Help Screen

- [ ] Press `?` from home screen
- [ ] Help shows `S` for Settings
- [ ] Help shows `P` for Outbox
- [ ] Help updated with new features

---

## Test Suite 8: Performance & UX

### Response Time

- [ ] Save with PR: Should complete in < 5 seconds (good network)
- [ ] Settings Test Connection: < 3 seconds
- [ ] Outbox retry: < 5 seconds
- [ ] No UI freezing during operations

### Notifications

- [ ] All notifications visible and readable
- [ ] Timeout appropriate (3-5 seconds)
- [ ] Error notifications red
- [ ] Success notifications default/green
- [ ] Warnings yellow

### Progress Indicators

- [ ] "Creating PR..." shows during save
- [ ] "Testing connection..." shows during test
- [ ] "Retrying..." shows in outbox

---

## Test Suite 9: Security

### Token Storage

- [ ] Save token in Settings
- [ ] Check file system: Token NOT in `.datahub_config.json`
- [ ] Check keychain:

```bash
# macOS
security find-generic-password -s "mini-datahub" -w

# Should output token
```

### Config File Permissions

- [ ] Check `.datahub_config.json` permissions:

```bash
ls -la .datahub_config.json
# Should NOT contain token in plain text
```

### Git Ignore

- [ ] Check `.datahub_config.json` in `.gitignore`
- [ ] Check `.outbox/` in `.gitignore`
- [ ] Try `git status` → Should not show config/outbox

---

## Test Suite 10: Multi-User Workflow

### User A (Maintainer)

- [ ] Configure with team credentials
- [ ] Add dataset "User A Dataset"
- [ ] PR created in central repo
- [ ] Merge PR on GitHub

### User B (Contributor)

- [ ] Configure with external credentials
- [ ] Pull catalog repo: `git pull`
- [ ] Reindex: `mini-datahub reindex`
- [ ] Search for "User A Dataset"

**Expected:**

- [ ] User A's dataset visible to User B
- [ ] User B can view details

### User B Adds Dataset

- [ ] Add "User B Dataset"
- [ ] PR created from fork
- [ ] User A sees PR on GitHub
- [ ] User A reviews and merges

### User A Pulls Update

- [ ] Pull catalog repo
- [ ] Reindex
- [ ] User B's dataset visible

---

## Regression Tests (Ensure v2.0 Features Still Work)

- [ ] Incremental search (type "wea" finds "weather")
- [ ] Zero-query list (datasets shown before typing)
- [ ] Neovim keybindings (`j/k`, `gg/G`, `/`)
- [ ] Scrollable Add Data form (`Ctrl+d/u`)
- [ ] URL probe (HEAD request)
- [ ] Copy to clipboard (`y` in details)
- [ ] Open URL in browser (`o` in details)
- [ ] Help screen (`?`)
- [ ] Reindex CLI: `mini-datahub reindex`

---

## Final Checklist

- [ ] All 10 test suites passed
- [ ] No crashes or unhandled exceptions
- [ ] All notifications clear and helpful
- [ ] Documentation accurate
- [ ] README updated
- [ ] CHANGELOG complete
- [ ] Migration guide tested

---

## Known Issues / TODOs

- Document any issues found during testing here
- Link to GitHub issues

---

**Testing Complete! 🎉**
