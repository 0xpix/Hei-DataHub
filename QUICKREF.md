# 🚀 Quick Reference - TUI v2.0

## Installation

```bash
# Fresh install
git clone <repo-url>
cd Hei-DataHub
uv sync --python /usr/bin/python --dev
source .venv/bin/activate

# Launch
mini-datahub

# Reindex (after schema changes)
mini-datahub reindex
```

## Keybindings Cheat Sheet

### Home / Search Screen

| Key | Action |
|-----|--------|
| `/` | Focus search (Insert mode) |
| `j` / `k` | Move selection down/up |
| `gg` | Jump to first dataset |
| `G` | Jump to last dataset |
| `o` / `Enter` | Open dataset details |
| `A` | Add new dataset |
| `Esc` | Exit Insert mode / Clear search |
| `?` | Show help |
| `q` | Quit |

### Details Screen

| Key | Action |
|-----|--------|
| `y` | Copy source to clipboard |
| `o` | Open source URL in browser |
| `q` / `Esc` | Back to search |

### Add Data Form

| Key | Action |
|-----|--------|
| `j` / `k` | Next/previous field |
| `gg` | Jump to first field |
| `G` | Jump to last field |
| `Ctrl+d` / `Ctrl+u` | Scroll half-page |
| `Tab` / `Shift+Tab` | Standard navigation |
| `Ctrl+S` | Save dataset |
| `q` / `Esc` | Cancel |

## Modes

- **Normal** (cyan) - Navigate and command
- **Insert** (green) - Edit text in search/forms

## What's New in v2.0

✅ **Incremental Search** - Type "wea" to find "weather"
✅ **Fixed Selection** - No more RowKey object errors
✅ **Scrollable Forms** - Works on small terminals (24 rows)
✅ **Focus Retention** - Search input keeps focus while typing
✅ **Zero-Query List** - See all datasets before typing
✅ **Neovim Keys** - Full keyboard control with vim-like bindings

## Common Tasks

### Search for datasets
```
Press `/` → Type "weather" → Results appear live
```

### Add a dataset
```
Press `A` → Fill required fields → `Ctrl+S` to save
```

### View details
```
Navigate with `j/k` → Press `o` or `Enter`
```

### Copy source URL
```
Open details → Press `y` → URL copied to clipboard
```

### Rebuild index
```bash
mini-datahub reindex
```

## Troubleshooting

**No results?** → Run `mini-datahub reindex`
**Focus issues?** → Press `Esc` to return to Normal mode
**Form cut off?** → Use `Ctrl+d/u` to scroll
**Database errors?** → Delete `db.sqlite`, run `mini-datahub reindex`

## Files & Locations

- **Datasets**: `data/<id>/metadata.yaml`
- **Database**: `db.sqlite` (FTS5 index)
- **Schema**: `schema.json` (JSON Schema), `sql/schema.sql` (SQLite)
- **Config**: `pyproject.toml` (dependencies)

## Quick Tests

```bash
# 1. Fresh install works
uv sync --python /usr/bin/python --dev && mini-datahub

# 2. Search works - Type `/`, enter "test"
# 3. Add works - Press `A`, fill form, `Ctrl+S`
# 4. Navigation works - Use `j/k`, `gg`, `G`
# 5. Reindex works
mini-datahub reindex
```

## Development

```bash
# Run tests
pytest

# Format code
black mini_datahub tests

# Lint
ruff check mini_datahub

# Add dependency
uv add <package-name>
```

## Documentation

- **README.md** - Full documentation
- **CHANGELOG.md** - Release notes
- **IMPLEMENTATION.md** - Technical details
- **TEST_CHECKLIST.md** - Testing guide

## Support

Report issues with:
1. Expected vs actual behavior
2. Terminal size and OS
3. Steps to reproduce
4. Error messages

---

**Version:** TUI v2.0 | **License:** MIT | **Python:** 3.9+
