# 🚀 Quick Start Guide - v0.50-beta

## Installation

```bash
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub
uv sync
source .venv/bin/activate
```

## Usage

```bash
# Launch TUI
hei-datahub

# Show version
hei-datahub --version

# Show detailed info
hei-datahub --version-info

# Rebuild index
hei-datahub reindex

# Show help
hei-datahub --help
```

## TUI Keys

| Key | Action |
|-----|--------|
| `/` | Search |
| `j/k` | Navigate |
| `Enter` | View details |
| `A` | Add dataset |
| `S` | Settings |
| `U` | Pull updates |
| `R` | Refresh |
| `q` | Quit |

## Make Commands

```bash
make run       # Launch TUI
make reindex   # Rebuild index
make clean     # Clean build files
```

## What's New in v0.50

✨ Enhanced version system
✨ Dual command support (`hei-datahub` + `mini-datahub`)
✨ Comprehensive version info (`--version-info`)
✨ Clean repository (40+ old files removed)
✨ All migration bugs fixed

## Documentation

- `RELEASE_v0.50.md` - Full release notes
- `CHANGELOG_v0.50.md` - Detailed changelog
- `COMPLETE_v0.50.md` - Migration summary
- `COMMAND_SETUP.md` - Running without uv
- `BUGFIX_MIGRATION_ERRORS.md` - Bug fixes

## Support

Repository: https://github.com/0xpix/Hei-DataHub
Issues: https://github.com/0xpix/Hei-DataHub/issues

---

**Version:** 0.50.0-beta
**Codename:** Clean Architecture
**Released:** October 4, 2025
