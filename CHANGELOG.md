## [0.58.1-beta] — 2025-10-09

### 🐛 Fixed

- **Data directory** — Data now loads correctly on linux:
    - **Linux:** `~/.local/share/Hei-DataHub`
- **Filename handling:** Unified globbing and case-sensitivity across OSes
- **Re-design some of the CLI output** for clarity and consistency
### ✨ Added

- **`hei-datahub doctor`** — Full system diagnostics with clear, actionable output
    - **Exit codes:** 0 = OK, 1 = dir issue, 2 = permission, 3 = data
    - Checks: OS info, data directory, datasets, DB, migrations, filenames
- **`--data-dir` flag** — Override data directory for any command (highest priority)
- **`HEIDATAHUB_DATA_DIR`** — Environment variable for persistent override

### 📦 Notes

- Internal build only — no PyPI/public release
- Fully backward-compatible with 0.58.0-beta

---

## [0.58.0-beta] — 2025-10-07 “Streamline”

### ✨ Added

- **UV-based installation**
    - Install directly from private repo via SSH / HTTPS (for now will be changed later)
    - Supports version pinning, `uvx` ephemeral runs, and `uv tool install`
    - Full guides for only Linux, (macOS, and Windows will come in future releases)

- **Packaged data & assets** — All configs, schemas, and resources now included
- **Linux desktop integration**
    - `.desktop` launcher script and standalone PyInstaller build
    - Optional AppImage support

- **Comprehensive docs**
    - New `docs/installation/` section with setup and troubleshooting guides
    - Updated main README with quickstart examples

### 🔧 Changed

- Package renamed to **`hei-datahub`** (alias `mini-datahub` still works, will be **deprecated** later)
- New `src/hei_datahub/` structure
- Both `hei-datahub` and `mini-datahub` commands available

### 🐛 Fixed

* Missing data files in installs
* Import and module-not-found errors after installation

