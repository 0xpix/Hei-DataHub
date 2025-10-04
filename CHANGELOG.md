# Changelog

## v3.0.0 - Automated PR Workflow (2024-10-03)

### 🚀 **Major Feature: Save → PR Automation**

Added seamless GitHub integration for **automated Pull Request creation** when saving datasets. Contributors never need to run git commands or handle tokens directly.

#### **New Features**

1. **Settings Screen** (`S` key)
   - Configure GitHub connection (host, owner/repo, token)
   - Test connection before saving
   - Secure token storage via OS keychain (`keyring` library)
   - Catalog repository path configuration
   - Auto-assign reviewers and PR labels

2. **Automated PR Workflow**
   - Saves `data/<id>/metadata.yaml` to catalog repository
   - Creates git branch: `add/<dataset-id>-<timestamp>`
   - Commits with convention: `feat(dataset): add <id> — <name>`
   - Pushes to GitHub (central repo or fork)
   - Opens Pull Request automatically with formatted body
   - Adds labels and reviewers
   - Success toast with PR URL

3. **Central vs Fork Strategy**
   - Detects push permissions automatically
   - Team members: Push to central repo
   - External contributors: Auto-creates fork, pushes there, opens cross-repo PR
   - Fork creation handles async completion

4. **Outbox/Queue System** (`P` key)
   - Failed PR submissions saved to outbox
   - View pending, retrying, failed, and completed tasks
   - Retry individual tasks or batch retry all
   - Clear completed tasks
   - Persistent queue survives app restarts

5. **Validation Gates**
   - Remote ID uniqueness check before commit
   - Schema validation (JSON Schema + Pydantic)
   - Array normalization
   - Blocks save if validation fails

6. **Error Handling**
   - Offline: Saves locally, queues PR for later
   - Token expired: Clear message, keeps dataset
   - Rate limit: Queues for retry
   - Network errors: Friendly, actionable messages

#### **New Modules**

- `mini_datahub/config.py` - Secure configuration with keyring integration
- `mini_datahub/git_ops.py` - Git operations (branch, commit, push)
- `mini_datahub/github_integration.py` - GitHub API operations (PR, fork, test)
- `mini_datahub/pr_workflow.py` - Main workflow orchestrator
- `mini_datahub/outbox.py` - Queue system for failed tasks
- `mini_datahub/screens.py` - Settings and Outbox screens

#### **Updated Modules**

- `mini_datahub/tui.py`:
  - Integrated PR workflow into save action
  - Added Settings (`S`) and Outbox (`P`) keybindings to HomeScreen
  - Added `@work` decorator for async PR creation
  - Updated Help screen with new keybindings
  - Added CSS for Settings and Outbox screens
  - One-time nudge for GitHub configuration

#### **Dependencies Added**

- `keyring>=24.0.0` - Secure token storage in OS keychain

#### **Documentation**

- `GITHUB_WORKFLOW.md` - Comprehensive guide for PR workflow setup and usage
- `catalog-gitignore-example` - Template .gitignore for catalog repositories
- Updated `README.md` with PR workflow overview

#### **Configuration Files**

- `.datahub_config.json` - GitHub settings (git-ignored, not committed)
- `.outbox/` - Failed PR task queue (git-ignored)

#### **Breaking Changes**

- None - Fully backward compatible
- PR workflow is optional (requires manual GitHub configuration)
- Without configuration, app behaves exactly as before

#### **Migration Guide**

For existing users who want PR automation:

1. Create a separate catalog repository on GitHub
2. Clone it locally
3. Generate a fine-grained PAT with `Contents: R/W`, `Pull requests: R/W`
4. Launch app, press `S`, fill in settings
5. Test connection, save
6. Next dataset save will auto-create PR!

See `GITHUB_WORKFLOW.md` for detailed setup instructions.

---

## v2.0.0 - TUI Enhancements (Previous)

### 🎯 Five Major UX Improvements

#### 1. **Incremental Prefix Search** ✅
- **Problem**: Typing "wea" wouldn't find datasets containing "weather"
- **Solution**:
  - Updated FTS5 schema with `prefix='2 3 4'` for 2-4 character prefix indexing
  - Modified `search_datasets()` to append wildcard `*` to each token (e.g., "wea" → "wea*")
  - Now supports live incremental search as you type
- **Files Modified**: `sql/schema.sql`, `mini_datahub/index.py`

#### 2. **Fixed Row Selection Bug** ✅
- **Problem**: Clicking dataset showed `<textual.widgets._data_table.RowKey object at 0x...>` instead of details
- **Solution**: Extract dataset ID from row data using `get_row_at(cursor_row)[0]` instead of using row_key object directly
- **Files Modified**: `mini_datahub/tui.py`

#### 3. **Scrollable Add Data Form** ✅
- **Problem**: Form wouldn't scroll on small terminals (24 rows), cutting off fields and buttons
- **Solution**:
  - Wrapped entire form in `VerticalScroll` container
  - Added multiple scroll methods: `Ctrl+d/u`, `Page Down/Up`, and mouse wheel
  - Improved scroll methods to use `scroll_relative()` for reliability
  - Added `priority=True` to keybindings to prevent input fields from consuming scroll keys
  - Auto-scroll focused fields into view with `scroll_visible()`
  - CSS: Added `overflow-y: auto`, visible scrollbar, and proper padding
  - Fixed button visibility: Added `padding-bottom: 3` and `min-height: 100%` to ensure Save/Cancel buttons are always reachable
- **Files Modified**: `mini_datahub/tui.py`

#### 4. **Zero-Query Dataset Listing** ✅
- **Problem**: Empty search showed nothing, users didn't know what datasets existed
- **Solution**:
  - Added `list_all_datasets()` function to return all datasets ordered by update time
  - HomeScreen now loads all datasets on mount and when search is cleared
  - Shows "All Datasets (N total)" label
- **Files Modified**: `mini_datahub/index.py`, `mini_datahub/tui.py`

#### 5. **Neovim-Style Keybindings** ✅
- **Problem**: Only mouse/arrow key navigation, not efficient for keyboard users
- **Solution**: Added comprehensive vim-like keybindings across all screens
- **New Keybindings**:
  - **Home Screen**: `j/k` (move), `gg/G` (jump), `/` (search), `A` (add), `o` (open), `Esc` (exit mode)
  - **Details Screen**: `y` (yank/copy), `o` (open URL), `q/Esc` (back)
  - **Add Form**: `j/k` (next/prev field), `Ctrl+d/u` (scroll), `gg/G` (jump), `Ctrl+s` (save)
  - **Help Screen**: `?` (show), `q/Esc` (dismiss)
- **Mode Indicator**: Shows "Normal" vs "Insert" mode at top of screen
- **Files Modified**: `mini_datahub/tui.py`

#### 6. **Fixed Search Input Focus Loss** ✅
- **Problem**: Focus jumped to results table after first keystroke, preventing continuous typing
- **Solution**:
  - Removed all `table.focus()` calls from search update methods
  - Added `Input.Focused` and `Input.Blurred` handlers for proper mode tracking
  - Search input now retains focus until user explicitly leaves (Esc, Tab, Enter)
- **Files Modified**: `mini_datahub/tui.py`

### 🔧 Technical Details

**Debouncing**: Added 150ms debounce timer on search input to prevent excessive FTS queries while typing.

**Focus Management**: Search input maintains focus during typing; table only focused on explicit user action (Enter, navigation keys). Mode tracking uses explicit action handlers (`action_focus_search`, `action_clear_search`) rather than focus events.

**Mode System**: Implemented reactive mode tracking with visual indicator:
- **Normal Mode** (cyan): Navigate with j/k, gg/G, press `/` to search
- **Insert Mode** (green): Typing in search/forms, press `Esc` to exit
- **Note**: Removed `Input.Focused/Blurred` handlers (don't exist in Textual API)

**Help System**: Press `?` anywhere to see full keybinding reference.

**Graceful Degradation**: Search errors (FTS syntax issues) return empty results instead of crashing.

### 📦 Package Management

**uv Integration**: Switched from pip/venv to uv for faster, reproducible dependency management:
- `uv sync --python /usr/bin/python --dev` for installation
- `uv.lock` committed to repo for reproducibility
- CI uses `uv sync --frozen --dev`

### 📋 Migration Notes

**⚠️ Database Reindex Required**: The FTS5 schema changed to add prefix indexing. After pulling these changes:

```bash
# Rebuild the FTS index with new schema
mini-datahub reindex
```

Or from Python:
```python
from mini_datahub.index import reindex_all
reindex_all()
```

The TUI automatically reindexes on startup if datasets exist, so just run `mini-datahub` once.

### 🧪 Testing Checklist

- [x] Incremental search: Type "wea" → finds "weather" datasets
- [x] Row selection: Click/press Enter → opens details (no RowKey errors)
- [x] Form scrolling: Terminal height < 30 rows → form scrolls with Ctrl+d/u
- [x] Zero-query: Empty search → shows all datasets
- [x] Vim keys: j/k navigation, gg/G jumps, / search, y copy, o open
- [x] Mode indicator: Shows Normal/Insert correctly
- [x] Help screen: ? shows keybindings reference
- [x] Debouncing: Fast typing doesn't lag UI

### 📖 Updated Documentation

See README.md for complete keybinding reference and usage examples.
