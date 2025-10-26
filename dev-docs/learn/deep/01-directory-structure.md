# Deep Dive: Directory Structure

**Learning Goal**: Understand what every directory and file in the codebase does.

By the end of this page, you'll:
- Navigate the codebase confidently
- Know where to find specific functionality
- Understand dependencies between modules
- Know where to add new features

---

## The Big Picture

```
src/mini_datahub/
├── app/              # Application runtime & bootstrap
├── auth/             # Authentication & credential management
├── cli/              # Command-line interface
├── core/             # Domain models & business rules
├── infra/            # Infrastructure (DB, files, paths)
├── services/         # Business logic orchestration
├── ui/               # TUI views, widgets, themes
├── utils/            # Helper utilities
├── __init__.py       # Package initialization
├── __main__.py       # Entrypoint (python -m mini_datahub)
├── version.py        # Version info
└── schema.json       # Dataset metadata JSON schema
```

**Clean Architecture Layers:**

```
┌─────────────────────────────────────┐
│  UI (ui/)                           │  ← Textual screens & widgets
├─────────────────────────────────────┤
│  Services (services/)               │  ← Business logic orchestration
├─────────────────────────────────────┤
│  Core (core/)                       │  ← Domain models & rules
├─────────────────────────────────────┤
│  Infrastructure (infra/, auth/)     │  ← DB, files, external systems
└─────────────────────────────────────┘

CLI (cli/)  →  Services  →  Core  →  Infrastructure
```

**Dependency rule:** Outer layers depend on inner layers, never the reverse.

---

## 📁 `/app` — Application Runtime

**Purpose:** Bootstrap the application, manage global state, load settings.

### Files

#### `runtime.py`
**What:** Application singleton, lifecycle management
**Exports:** `App` class, `get_app()` function
**Used by:** `__main__.py`, UI screens

```python
from mini_datahub.app.runtime import get_app

app = get_app()
app.initialize()  # Load config, connect DB, etc.
```

**Key responsibilities:**
- Load configuration from TOML
- Initialize database connection
- Set up auth store
- Manage application lifecycle

---

#### `settings.py`
**What:** User preferences & configuration models
**Exports:** `Settings` Pydantic model
**Used by:** `runtime.py`, UI settings screen

```python
from mini_datahub.app.settings import Settings

settings = Settings.load()
print(settings.search.max_results)  # 50
```

**Configuration hierarchy:**
1. `~/.config/hei-datahub/config.toml` (user config)
2. Environment variables (`HEIBOX_*`)
3. Built-in defaults

---

**When to modify:**
- ✅ Add new global settings
- ✅ Change application initialization logic
- ❌ Add UI-specific state (use `ui/state.py`)
- ❌ Add business logic (use `services/`)

---

## 🔐 `/auth` — Authentication & Credentials

**Purpose:** Manage WebDAV credentials securely using system keyring.

### Files

#### `credentials.py`
**What:** Abstract credential storage with keyring backend
**Exports:** `AuthStore`, `KeyringAuthStore`, `EnvAuthStore`
**Used by:** `services/webdav_storage.py`, CLI auth commands

```python
from mini_datahub.auth.credentials import get_auth_store

store = get_auth_store(prefer_keyring=True)
store.store_secret("webdav:token:user@server", "secret123")
token = store.get_secret("webdav:token:user@server")
```

**Backends:**
- **Keyring** (Linux Secret Service, macOS Keychain, Windows Credential Vault)
- **Environment variables** (fallback: `HEIBOX_WEBDAV_TOKEN`)

---

#### `setup.py`
**What:** Interactive wizard for auth configuration
**Exports:** `run_setup_wizard()`
**Used by:** `cli/main.py` (auth setup command)

```python
from mini_datahub.auth.setup import run_setup_wizard

exit_code = run_setup_wizard(
    url="https://heibox.uni-heidelberg.de/seafdav",
    username="user123",
    token=None,  # Will prompt
)
```

---

#### `validator.py`
**What:** Test WebDAV connections
**Exports:** `validate_webdav_connection()`
**Used by:** `setup.py`, `doctor.py`

```python
from mini_datahub.auth.validator import validate_webdav_connection

is_valid = validate_webdav_connection(url, username, token)
```

---

#### `doctor.py`
**What:** Diagnose auth issues
**Exports:** `run_auth_doctor()`
**Used by:** `cli/main.py` (auth doctor command)

---

**When to modify:**
- ✅ Add new auth backends (OAuth, SSH keys)
- ✅ Add credential validation logic
- ❌ Add WebDAV protocol logic (use `services/webdav_storage.py`)
- ❌ Add UI for auth (use `ui/views/settings.py`)

---

## 💻 `/cli` — Command-Line Interface

**Purpose:** Provide non-interactive commands for scripting and automation.

### Files

#### `main.py`
**What:** CLI entrypoint with argparse
**Exports:** `main()` function
**Used by:** `__main__.py`, shell commands

```python
from mini_datahub.cli.main import main

main()  # Parse sys.argv and dispatch
```

**Commands:**
- `hei-datahub` (default: launch TUI)
- `hei-datahub reindex` (rebuild search index)
- `hei-datahub auth setup` (interactive auth wizard)
- `hei-datahub auth status` (show current config)
- `hei-datahub doctor` (run diagnostics)

---

#### `update_manager.py`
**What:** Cross-platform update orchestration
**Exports:** `UpdateManager` class
**Used by:** `main.py` (update command)

```python
from mini_datahub.cli.update_manager import UpdateManager

manager = UpdateManager()
manager.check_for_updates()
manager.install_update(version="0.61.0")
```

---

#### `linux_update.py`, `macos_update.py`, `windows_update.py`
**What:** Platform-specific update installers
**Used by:** `update_manager.py`

---

**When to modify:**
- ✅ Add new CLI commands
- ✅ Add command-line arguments
- ❌ Add interactive UIs (use `ui/`)
- ❌ Add business logic (use `services/`)

---

## 🎯 `/core` — Domain Models & Business Rules

**Purpose:** Define the core domain of the application (datasets, queries, rules).

**No dependencies on outer layers!** This is the heart of the application.

### Files

#### `models.py`
**What:** Pydantic models for datasets
**Exports:** `Dataset`, `DatasetMetadata`, `Person`, etc.
**Used by:** Everything!

```python
from mini_datahub.core.models import Dataset, Person

dataset = Dataset(
    dataset_id="climate-2023",
    metadata={
        "dataset_name": "Climate Data 2023",
        "creators": [Person(name="Alice", orcid="0000-0001-...")],
    },
)
```

**Key models:**
- `Dataset` — Top-level dataset container
- `DatasetMetadata` — YAML/JSON metadata
- `Person` — Author/creator info
- `License` — License metadata

---

#### `queries.py`
**What:** Query data structures
**Exports:** `SearchQuery`, `FilterOptions`
**Used by:** `services/search.py`, UI

```python
from mini_datahub.core.queries import SearchQuery

query = SearchQuery(
    text="climate",
    project_filter="Earth Science",
    limit=50,
)
```

---

#### `rules.py`
**What:** Business rules & validation
**Exports:** `validate_dataset()`, `normalize_id()`
**Used by:** `services/`, `infra/store.py`

```python
from mini_datahub.core.rules import normalize_id

dataset_id = normalize_id("Climate Data 2023!")
# → "climate-data-2023"
```

---

#### `errors.py`
**What:** Domain-specific exceptions
**Exports:** `DatasetNotFoundError`, `InvalidMetadataError`
**Used by:** `services/`, `infra/`

```python
from mini_datahub.core.errors import DatasetNotFoundError

raise DatasetNotFoundError(dataset_id="missing-dataset")
```

---

**When to modify:**
- ✅ Add new domain models
- ✅ Add validation rules
- ✅ Add domain exceptions
- ❌ Add database logic (use `infra/`)
- ❌ Add UI logic (use `ui/`)
- ❌ Import from outer layers (violates Clean Architecture!)

---

## 🗄️ `/infra` — Infrastructure Layer

**Purpose:** Interface with external systems (database, filesystem, Git, GitHub API).

### Files

#### `db.py`
**What:** SQLite connection management
**Exports:** `get_connection()`, `ensure_database()`
**Used by:** `index.py`, `services/search.py`

```python
from mini_datahub.infra.db import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM datasets_fts")
```

---

#### `index.py`
**What:** FTS5 indexing operations
**Exports:** `upsert_dataset()`, `delete_dataset()`, `search_datasets()`
**Used by:** `services/index_service.py`, `services/search.py`

```python
from mini_datahub.infra.index import upsert_dataset

upsert_dataset(dataset_id="climate-2023", metadata={...})
```

**Key functions:**
- `upsert_dataset()` — Insert/update in FTS5 index
- `delete_dataset()` — Remove from index
- `search_datasets()` — FTS5 MATCH query
- `reindex_all()` — Rebuild entire index

---

#### `store.py`
**What:** Filesystem-based JSON storage
**Exports:** `read_dataset()`, `write_dataset()`, `list_datasets()`
**Used by:** `services/`, CLI reindex

```python
from mini_datahub.infra.store import read_dataset, write_dataset

metadata = read_dataset("climate-2023")
write_dataset("climate-2023", metadata)
```

**Directory structure:**
```
~/.local/share/hei-datahub/datasets/
├── climate-2023/
│   └── metadata.yaml
├── covid-tracker/
│   └── metadata.yaml
└── ...
```

---

#### `paths.py`
**What:** Application data paths
**Exports:** `DATA_DIR`, `DB_PATH`, `CONFIG_DIR`
**Used by:** Everything!

```python
from mini_datahub.infra.paths import DATA_DIR, DB_PATH

print(DATA_DIR)   # ~/.local/share/hei-datahub/datasets
print(DB_PATH)    # ~/.local/share/hei-datahub/db.sqlite
```

---

#### `config_paths.py`
**What:** Configuration file paths
**Exports:** `get_config_path()`, `get_keymap_path()`
**Used by:** `app/settings.py`, `ui/keybindings.py`

---

#### `platform_paths.py`
**What:** Platform-specific path resolution (XDG, AppData, etc.)
**Exports:** `get_data_dir()`, `get_config_dir()`
**Used by:** `paths.py`

**Platform support:**
- **Linux:** XDG Base Directory (`~/.local/share`, `~/.config`)
- **macOS:** `~/Library/Application Support`, `~/Library/Preferences`
- **Windows:** `%APPDATA%`, `%LOCALAPPDATA%`

---

#### `git.py`
**What:** Git repository operations
**Exports:** `clone_repo()`, `pull_repo()`, `get_commit_hash()`
**Used by:** `services/publish.py`

---

#### `github_api.py`
**What:** GitHub REST API client
**Exports:** `get_latest_release()`, `download_asset()`
**Used by:** `cli/update_manager.py`

---

#### `/sql`
**What:** SQL schema files
**Files:**
- `create_fts.sql` — CREATE VIRTUAL TABLE for FTS5
- `migrations/` — Schema migrations

---

**When to modify:**
- ✅ Add new database tables
- ✅ Add new external integrations (S3, APIs)
- ✅ Change file storage format
- ❌ Add business logic (use `services/`)
- ❌ Add UI logic (use `ui/`)

---

## 🧩 `/services` — Business Logic

**Purpose:** Orchestrate operations across multiple infrastructure components.

**This is where complex workflows live!**

### Files

#### `search.py`
**What:** Full-text search orchestration
**Exports:** `SearchService` class
**Used by:** `ui/views/home.py`

```python
from mini_datahub.services.search import SearchService

service = SearchService()
results = service.search(query="climate", limit=50)
```

**Workflow:**
1. Parse query
2. Call `infra/index.py` for FTS5 search
3. Enrich results with metadata
4. Return ranked results

---

#### `autocomplete.py`
**What:** Suggestion generation
**Exports:** `AutocompleteManager`
**Used by:** `ui/widgets/autocomplete.py`

```python
from mini_datahub.services.autocomplete import AutocompleteManager

manager = AutocompleteManager()
manager.build_cache()  # Extract all terms
suggestions = manager.suggest_projects("cli", limit=5)
```

---

#### `webdav_storage.py`
**What:** WebDAV protocol implementation
**Exports:** `WebDAVStorage` class
**Used by:** `services/sync.py`, UI cloud browser

```python
from mini_datahub.services.webdav_storage import WebDAVStorage

storage = WebDAVStorage(
    base_url="https://heibox.uni-heidelberg.de/seafdav",
    library="my-library",
    username="user",
    password="token",
)

files = storage.listdir("datasets")
storage.download("datasets/climate.yaml", "local.yaml")
```

---

#### `sync.py`
**What:** Cloud synchronization orchestration
**Exports:** `SyncService`
**Used by:** UI sync buttons

```python
from mini_datahub.services.sync import SyncService

service = SyncService(storage=webdav_storage)
service.upload_dataset("climate-2023")
service.download_dataset("remote-dataset")
```

---

#### `index_service.py`
**What:** High-level indexing operations
**Exports:** `IndexService`
**Used by:** CLI reindex, UI refresh

```python
from mini_datahub.services.index_service import IndexService

service = IndexService()
service.rebuild_index()  # Reindex all datasets
```

---

#### `catalog.py`
**What:** Dataset catalog management
**Exports:** `CatalogService`
**Used by:** UI dataset list, CLI export

---

#### `publish.py`
**What:** Dataset publishing workflows
**Exports:** `publish_to_git()`
**Used by:** CLI publish command

---

**When to modify:**
- ✅ Add complex workflows (multi-step operations)
- ✅ Coordinate multiple infra components
- ✅ Add caching/performance optimizations
- ❌ Add domain models (use `core/`)
- ❌ Add database queries (use `infra/`)
- ❌ Add UI components (use `ui/`)

---

## 🎨 `/ui` — Terminal User Interface

**Purpose:** Textual-based TUI with screens, widgets, and themes.

### Directory Structure

```
ui/
├── views/           # Fullscreen application screens
├── widgets/         # Reusable UI components
├── styles/          # TCSS stylesheets
├── assets/          # Images, logos
├── keybindings.py   # Global keyboard shortcuts
└── theme.py         # Color themes
```

---

### `/ui/views` — Application Screens

#### `home.py`
**What:** Main screen with search & results
**Exports:** `HomeScreen`
**Used by:** `__main__.py` (default screen)

```python
from mini_datahub.ui.views.home import HomeScreen

app.push_screen(HomeScreen())
```

**Features:**
- Search input with autocomplete
- Results list with BM25 ranking
- Keybindings (Enter, /, g, Ctrl+R)

---

#### `cloud_files.py`
**What:** WebDAV file browser
**Exports:** `CloudFilesScreen`
**Used by:** Home screen navigation

```python
from mini_datahub.ui.views.cloud_files import CloudFilesScreen

app.push_screen(CloudFilesScreen(storage=webdav_storage))
```

---

#### `settings.py`
**What:** Settings editor
**Exports:** `SettingsScreen`
**Used by:** Home screen navigation

---

#### `outbox.py`
**What:** Pending uploads manager
**Exports:** `OutboxScreen`
**Used by:** Cloud sync workflow

---

### `/ui/widgets` — Reusable Components

#### `autocomplete.py`
**What:** Dropdown suggestion list
**Exports:** `AutocompleteWidget`
**Used by:** `home.py`

```python
from mini_datahub.ui.widgets.autocomplete import AutocompleteWidget

autocomplete = AutocompleteWidget(
    suggestions=["climate", "covid", "gideon"],
    on_select=self.handle_suggestion,
)
```

---

#### `command_palette.py`
**What:** Fuzzy command finder
**Exports:** `CommandPalette`
**Used by:** Global keybinding (Ctrl+P)

---

#### `help_overlay.py`
**What:** Keybinding cheat sheet
**Exports:** `HelpOverlay`
**Used by:** Global keybinding (?)

---

### `/ui/styles`

- `default.tcss` — Default theme colors & layout
- `dark.tcss` — Dark theme overrides
- `light.tcss` — Light theme overrides

---

**When to modify:**
- ✅ Add new screens/widgets
- ✅ Change UI layout/styling
- ✅ Add keybindings
- ❌ Add business logic (use `services/`)
- ❌ Add database queries (use `infra/`)

---

## 🛠️ `/utils` — Helper Utilities

**Purpose:** Generic helper functions with no business logic.

### Files

#### `async_utils.py`
**What:** Async helpers for Textual
**Exports:** `run_async()`, `debounce()`
**Used by:** UI screens

```python
from mini_datahub.utils.async_utils import debounce

@debounce(delay=0.3)
async def on_input_changed(self, event):
    await self.perform_search()
```

---

#### `text.py`
**What:** String manipulation
**Exports:** `truncate()`, `highlight()`, `normalize_whitespace()`
**Used by:** UI rendering, search

```python
from mini_datahub.utils.text import truncate

title = truncate("Very Long Dataset Name Here", max_length=20)
# → "Very Long Dataset..."
```

---

**When to modify:**
- ✅ Add generic utilities
- ❌ Add domain-specific logic (use `core/` or `services/`)

---

## 🏗️ Root Files

### `__init__.py`
**What:** Package initialization
**Exports:** `__version__`

```python
from mini_datahub import __version__
print(__version__)  # "0.61.0"
```

---

### `__main__.py`
**What:** Entrypoint for `python -m mini_datahub`
**Exports:** Nothing (runs CLI or TUI)

```python
# Dispatch logic:
if len(sys.argv) > 1:
    # Has arguments → run CLI
    from mini_datahub.cli.main import main
    main()
else:
    # No arguments → launch TUI
    from mini_datahub.ui.views.home import HomeScreen
    app.run(HomeScreen())
```

---

### `version.py`
**What:** Version string from `version.yaml`
**Exports:** `__version__`
**Used by:** CLI `--version`, update checker

---

### `schema.json`
**What:** JSON Schema for dataset metadata
**Used by:** Validation, documentation

---

## 📊 Dependency Graph

```
┌─────────────────────────────────────────────┐
│  UI Layer                                   │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐ │
│  │  views/ │  │ widgets/ │  │ keybinds   │ │
│  └────┬────┘  └─────┬────┘  └──────┬─────┘ │
└───────┼────────────┼──────────────┼────────┘
        │            │              │
┌───────▼────────────▼──────────────▼────────┐
│  Services Layer                            │
│  ┌────────┐  ┌─────────┐  ┌────────────┐  │
│  │ search │  │autocmpl │  │ webdav     │  │
│  └───┬────┘  └────┬────┘  └─────┬──────┘  │
└──────┼────────────┼─────────────┼─────────┘
       │            │             │
┌──────▼────────────▼─────────────▼─────────┐
│  Core Layer                               │
│  ┌────────┐  ┌─────────┐  ┌──────────┐   │
│  │ models │  │ queries │  │  rules   │   │
│  └────────┘  └─────────┘  └──────────┘   │
└───────────────────────────────────────────┘
       │            │             │
┌──────▼────────────▼─────────────▼─────────┐
│  Infrastructure Layer                     │
│  ┌──────┐  ┌───────┐  ┌───────┐  ┌────┐  │
│  │  db  │  │ index │  │ store │  │git │  │
│  └──────┘  └───────┘  └───────┘  └────┘  │
└───────────────────────────────────────────┘
```

**Key rules:**
- UI → Services → Core → Infrastructure
- Core never imports from outer layers
- Infrastructure can be swapped (e.g., PostgreSQL instead of SQLite)

---

## 🎯 Finding Features

### "Where is...?"

**Search functionality?**
- UI: `ui/views/home.py` (`on_input_changed`)
- Service: `services/search.py` (`SearchService`)
- Infrastructure: `infra/index.py` (`search_datasets`)

**Dataset storage?**
- JSON files: `infra/store.py` (`read_dataset`, `write_dataset`)
- FTS5 index: `infra/index.py` (`upsert_dataset`)

**WebDAV cloud sync?**
- Protocol: `services/webdav_storage.py` (`WebDAVStorage`)
- Auth: `auth/credentials.py` (`KeyringAuthStore`)
- UI: `ui/views/cloud_files.py` (`CloudFilesScreen`)

**CLI commands?**
- Entrypoint: `cli/main.py` (`main()`)
- Handlers: `cli/main.py` (`handle_reindex`, `handle_auth_setup`)

**Autocomplete suggestions?**
- Service: `services/autocomplete.py` (`AutocompleteManager`)
- UI: `ui/widgets/autocomplete.py` (`AutocompleteWidget`)
- Integration: `ui/views/home.py` (autocomplete dropdown)

**Keybindings?**
- Global: `ui/keybindings.py`
- Screen-specific: `ui/views/home.py` (`BINDINGS`)

**Configuration?**
- Models: `app/settings.py` (`Settings`)
- Paths: `infra/config_paths.py`
- Loading: `app/runtime.py`

---

## ✅ What You've Learned

✅ **Directory structure** — 8 main directories with clear purposes
✅ **Clean Architecture** — UI → Services → Core → Infrastructure
✅ **Dependency rules** — Inner layers never depend on outer layers
✅ **Where to find features** — Quick reference for common tasks
✅ **When to modify** — Guidelines for each directory

---

## Next Steps

Now that you understand the overall structure, let's dive into specific subsystems.

**Next:** [Authentication System Deep Dive](02-auth.md)

---

## Further Reading

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Directory Structure Best Practices](https://docs.python-guide.org/writing/structure/)
