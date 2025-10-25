# Codebase Overview

This is your complete guide to understanding the Hei-DataHub codebase. We'll start from the ground up, assuming you've never worked with this code before.

## 🎯 What Does This Project Do?

Hei-DataHub is a **cloud-first Terminal User Interface (TUI)** application that helps users:

1. **Catalog** datasets with metadata in HeiBox/Seafile cloud storage
2. **Search** through datasets instantly using SQLite FTS5 (full-text search)
3. **Sync** datasets between cloud (WebDAV) and local cache
4. **Authenticate** securely with credentials stored in OS keyring
5. **Collaborate** with teams via shared cloud libraries
6. **View** dataset details in a beautiful terminal interface

Think of it as a combination of:
- Cloud file manager (WebDAV client for HeiBox/Seafile)
- Search engine (instant FTS5 search over thousands of datasets)
- Sync client (background synchronization)
- Secure credential manager (Linux keyring integration)
- Data viewer (inspect and edit metadata)

## 📦 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI** | [Textual](https://textual.textualize.io/) | Terminal interface framework |
| **Database** | SQLite + FTS5 | Local search index with full-text search |
| **Cloud Storage** | WebDAV (HeiBox/Seafile) | Primary dataset storage and team collaboration |
| **CLI** | argparse | Command-line argument parsing |
| **Validation** | Pydantic v2 + JSON Schema | Data validation and schemas |
| **Authentication** | keyring + Secret Service | Secure credential storage |
| **HTTP** | requests | WebDAV client with retry logic |
| **Config** | TOML | Configuration file format |
| **Package Manager** | uv | Fast, reproducible package installation |

## 🗂️ High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                  USER                           │
│           (Terminal Interface)                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│              CLI Layer                          │
│  (src/mini_datahub/cli/main.py)                │
│  • Parse commands (auth, reindex, doctor, etc.) │
│  • Initialize workspace & logging               │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Authentication Layer                   │
│  (src/mini_datahub/auth/)                      │
│  • WebDAV credential management                 │
│  • Keyring integration                          │
│  • Connection validation                        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            UI/TUI Layer                         │
│  (src/mini_datahub/ui/)                        │
│  • Screens & Views (home, search, settings)     │
│  • Widgets & Components (autocomplete, etc.)    │
│  • Keybindings & Theme                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Services Layer                         │
│  (src/mini_datahub/services/)                  │
│  • search: FTS5 queries & autocomplete          │
│  • catalog: CRUD for datasets                   │
│  • sync: Cloud ↔ Local synchronization         │
│  • webdav_storage: WebDAV client                │
│  • storage_backend: Abstract storage interface  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            Core Layer                           │
│  (src/mini_datahub/core/)                      │
│  • models: Data structures (Pydantic)           │
│  • queries: Query parsing & filters             │
│  • rules: Business logic validation             │
│  • errors: Custom exceptions                    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│       Infrastructure Layer                      │
│  (src/mini_datahub/infra/)                     │
│  • db: SQLite FTS5 operations                   │
│  • paths: XDG Base Directory paths              │
│  • config_paths: Config file resolution         │
│  • store: YAML/JSON file I/O                    │
│  • index: Search index management               │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│           Data Storage                          │
│  • Cloud: HeiBox/Seafile (WebDAV) [Primary]     │
│  • Local Cache: ~/.cache/hei-datahub/datasets/  │
│  • Search Index: ~/.local/share/.../db.sqlite   │
│  • Config: ~/.config/hei-datahub/config.toml    │
│  • Keyring: OS-managed encrypted credentials    │
└─────────────────────────────────────────────────┘
```

## 📁 Directory Structure Explained

```
src/mini_datahub/              # Main Python package
│
├── __init__.py                # Package initialization
├── version.py                 # Version info and display
│
├── app/                       # Application runtime & lifecycle
│   ├── __init__.py
│   ├── runtime.py             # App initialization, startup/shutdown
│   └── settings.py            # Global settings & configuration
│
├── auth/                      # ⭐ Authentication management (NEW v0.57+)
│   ├── __init__.py
│   ├── setup.py               # Interactive WebDAV setup wizard
│   ├── credentials.py         # Keyring integration for secure storage
│   ├── validator.py           # WebDAV connection validation
│   ├── doctor.py              # Diagnostic tool for auth troubleshooting
│   └── clear.py               # Clear credentials and reset auth
│
├── cli/                       # Command-line interface
│   ├── __init__.py
│   ├── main.py                # Entry point (hei-datahub command)
│   ├── doctor.py              # System health diagnostics
│   ├── linux_update.py        # Linux update manager
│   ├── windows_update.py      # Windows update manager
│   ├── macos_update.py        # macOS update manager
│   └── update_manager.py      # Cross-platform update logic
│
├── core/                      # Core domain logic (framework-agnostic)
│   ├── __init__.py
│   ├── models.py              # Pydantic models (DatasetMetadata, etc.)
│   ├── queries.py             # Query parsing & operators
│   ├── rules.py               # Business rules & validation
│   └── errors.py              # Custom exceptions
│
├── infra/                     # Infrastructure layer (external integrations)
│   ├── __init__.py
│   ├── db.py                  # SQLite connection & FTS5 queries
│   ├── paths.py               # File system paths & workspace init
│   ├── config_paths.py        # XDG Base Directory config resolution
│   ├── platform_paths.py      # Cross-platform path handling
│   ├── index.py               # Search index operations (FTS5)
│   └── store.py               # YAML/JSON file I/O
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── search.py              # FTS5 search queries
│   ├── fast_search.py         # Optimized search with caching
│   ├── autocomplete.py        # Tag/field autocomplete suggestions
│   ├── suggestion_service.py  # Context-aware autocomplete
│   ├── catalog.py             # Dataset CRUD operations
│   ├── sync.py                # Cloud ↔ Local synchronization
│   ├── webdav_storage.py      # ⭐ WebDAV storage backend (HeiBox/Seafile)
│   ├── filesystem_storage.py  # Local filesystem storage backend
│   ├── storage_backend.py     # Abstract storage interface (Protocol)
│   ├── storage_manager.py     # Multi-backend storage coordinator
│   ├── indexer.py             # Background indexing service
│   ├── index_service.py       # Index management and optimization
│   ├── actions.py             # Complex user workflows
│   ├── config.py              # Config file management (TOML)
│   ├── state.py               # Application state
│   ├── storage.py             # Atomic file writes, backup/restore
│   ├── outbox.py              # Failed operation retry queue
│   ├── update_check.py        # App version checking
│   └── performance.py         # Performance monitoring
│
├── ui/                        # Terminal user interface
│   ├── __init__.py
│   ├── theme.py               # Color schemes & styling
│   ├── keybindings.py         # Keybinding management
│   ├── views/                 # Complete screens
│   │   ├── __init__.py
│   │   ├── home.py            # Main TUI launcher
│   │   ├── cloud_files.py     # Cloud file browser
│   │   ├── outbox.py          # Outbox/queue viewer
│   │   ├── settings.py        # Settings screen
│   │   ├── settings_menu.py   # Settings menu
│   │   └── user_config.py     # User config editor
│   ├── widgets/               # Reusable UI components
│   │   ├── __init__.py
│   │   ├── autocomplete.py    # Autocomplete widget
│   │   ├── command_palette.py # Command palette
│   │   ├── console.py         # Debug console
│   │   └── help_overlay.py    # Help overlay
│   └── assets/                # UI assets
│       └── loader.py          # Asset loading
│
├── utils/                     # Utility functions & helpers
│   ├── __init__.py
│   ├── text.py                # Text formatting utilities
│   └── async_utils.py         # Async/await helpers
│
└── internal/                  # Internal utilities (not public API)
    └── ...
```

## 🔄 Data Flow: How a Search Works

Let's trace what happens when a user searches for "climate":

### 1. User Input (UI Layer)
```
User types "climate" in search bar
↓
ui/widgets/autocomplete.py → on_input() event
↓
Triggers autocomplete suggestions
↓
Emits "search_requested" message
```

### 2. View Handles Event (UI Layer)
```
ui/views/home.py → on_search_requested()
↓
Calls services.fast_search.search_datasets("climate")
```

### 3. Business Logic (Services Layer)
```
services/fast_search.py → search_datasets()
↓
1. Parse query using core.queries.QueryParser
2. Check cache for recent identical query
3. Build FTS5 SQL query with filters
4. Call infra.index.fts_search()
```

### 4. Database Query (Infrastructure Layer)
```
infra/index.py → fts_search()
↓
infra/db.py → get_connection() [singleton]
↓
Execute SQL: SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'climate*'
↓
Returns raw SQLite rows with relevance scores
```

### 5. Transform Results (Services Layer)
```
services/search.py
↓
Convert SQLite rows to dictionaries
↓
Return List[Dict[str, Any]]
```

### 6. Display Results (UI Layer)
```
ui/views/main_view.py
↓
Update dataset_list widget with results
↓
User sees updated list in terminal
```

## 🎨 Layering Principles

### Core Layer (Pure Business Logic)
- **No external dependencies** (no UI, no database imports)
- **Pydantic models only** for data structures
- **Business rules** and validation
- Can be tested in isolation

### Infrastructure Layer (External Integrations)
- **Database operations** (SQLite)
- **File system** operations
- **WebDAV sync** (cloud storage)
- Can be mocked in tests

### Services Layer (Orchestration)
- **Combines** core + infra layers
- **Coordinates** multiple operations
- **Transforms** data between layers
- Business logic that needs external resources

### UI Layer (Presentation)
- **Textual widgets** and screens
- **User interactions** and keybindings
- **Visual styling** and themes
- **Event handling**

## 🧪 Testing Strategy

```
tests/
├── test_*.py                  # Unit tests for individual functions
├── services/                  # Service layer tests
│   └── test_*.py
├── ui/                        # UI component tests
│   └── test_*.py
└── integration/               # End-to-end tests
    └── test_*.py
```

**Testing Philosophy:**
- Core layer: 100% unit test coverage (pure Python)
- Services layer: Integration tests with mocked DB
- UI layer: Snapshot tests + interaction tests
- Infrastructure: Integration tests with real SQLite

## 🚀 Entry Point Flow

When you run `hei-datahub`:

```python
# 1. CLI entry point
src/mini_datahub/cli/main.py:main()

# 2. Initialize runtime
app.runtime.initialize_app()
  ↓
  • Load config from ~/.config/hei-datahub/config.yaml
  • Connect to database (db.sqlite)
  • Run migrations if needed
  • Index datasets from data/ folder

# 3. Start TUI
ui.app.App().run()
  ↓
  • Load theme
  • Mount main view
  • Start event loop
  • Handle keybindings

# 4. Wait for user input
# User interacts with UI...

# 5. Shutdown
app.runtime.shutdown()
  ↓
  • Close database connections
  • Save state
  • Clean up
```

## 📖 Key Concepts

### 1. Dataset
A dataset is:
- **Metadata file**: `data/my-dataset/metadata.yaml`
- **Actual data**: Files in same directory (CSV, NetCDF, etc.)
- **Database record**: Row in `datasets_store` table

### 2. Catalog
The catalog is:
- **Collection** of all known datasets
- **SQLite database** with FTS5 index
- **File system** structure in `data/` folder

### 3. Sync
Syncing means:
- **Download** catalog from WebDAV
- **Parse** metadata files
- **Index** into local database
- **Track** updates

### 4. Search
Search uses:
- **FTS5** (Full-Text Search) in SQLite
- **BM25** ranking algorithm
- **Structured queries** (source:webdav, format:csv)
- **Prefix matching** (autocomplete)

## 🔍 Where to Look for...

| Feature | File/Directory |
|---------|---------------|
| Add a new keybinding | `ui/views/main_view.py` (BINDINGS) |
| Change search algorithm | `services/search.py` |
| Add a database field | `schema.json` + `core/models.py` |
| Add a new screen | `ui/views/` (new file) |
| Add a CLI command | `cli/main.py` |
| Change theme colors | `ui/theme.py` |
| Add WebDAV sync logic | `infra/webdav.py` |
| Add business rule | `core/rules.py` |
| Add utility function | `utils/` |

## 🎓 Learning Path

**For absolute beginners:**

1. Start with [Getting Started](../quickstart/getting-started.md)
2. Make [Your First Contribution](../quickstart/first-contribution.md)
3. Read [Package Structure](#-directory-structure-explained) above
4. Explore one module at a time:
   - [Core Module](core-module.md) (simplest, pure Python)
   - [Infrastructure Module](infra-module.md) (database & APIs)
   - [Services Module](services-module.md) (business logic)
   - [UI Module](ui-module.md) (terminal interface)

**For experienced developers:**

1. Read [Architecture Overview](../architecture/overview.md)
2. Check [API Reference](../api-reference/overview.md)
3. Dive into specific services you're interested in
4. Review [ADRs](../adr/index.md) for design decisions

---

**Next**:
- [Root Files Explained →](root-files.md)
- [Package Structure →](package-structure.md)
- [Core Module Deep Dive →](core-module.md)
