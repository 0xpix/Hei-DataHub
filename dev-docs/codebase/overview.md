# Codebase Overview

This is your complete guide to understanding the Hei-DataHub codebase. We'll start from the ground up, assuming you've never worked with this code before.

## 🎯 What Does This Project Do?

Hei-DataHub is a **Terminal User Interface (TUI)** application that helps users:

1. **Catalog** datasets with metadata (like a library card catalog)
2. **Search** through datasets quickly (using SQLite full-text search)
3. **Sync** datasets from GitHub repositories
4. **View** dataset details in a beautiful terminal interface

Think of it as a combination of:
- File manager (browse datasets)
- Search engine (find datasets quickly)
- GitHub client (sync from repos)
- Data viewer (inspect metadata)

## 📦 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI** | [Textual](https://textual.textualize.io/) | Terminal interface framework |
| **Database** | SQLite + FTS5 | Local storage with full-text search |
| **CLI** | Typer | Command-line interface |
| **Validation** | Pydantic | Data validation and schemas |
| **Git Integration** | GitPython | Git operations |
| **HTTP** | httpx | GitHub API calls |
| **Config** | YAML + Pydantic | Configuration management |

## 🗂️ High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                  USER                           │
│           (Terminal Interface)                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│              CLI Layer                          │
│  (src/mini_datahub/cli/main.py)               │
│  • Parse commands                               │
│  • Initialize app                               │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            UI/TUI Layer                         │
│  (src/mini_datahub/ui/)                        │
│  • Screens & Views                              │
│  • Widgets & Components                         │
│  • Keybindings & Theme                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Services Layer                         │
│  (src/mini_datahub/services/)                  │
│  • search: Query datasets                       │
│  • catalog: Manage datasets                     │
│  • sync: GitHub integration                     │
│  • config: Settings management                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            Core Layer                           │
│  (src/mini_datahub/core/)                      │
│  • models: Data structures (Pydantic)           │
│  • queries: Query parsing                       │
│  • rules: Business logic validation             │
│  • errors: Custom exceptions                    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│       Infrastructure Layer                      │
│  (src/mini_datahub/infra/)                     │
│  • db: SQLite operations                        │
│  • git: Git operations                          │
│  • github_api: GitHub REST API                  │
│  • paths: File system paths                     │
│  • store: Data persistence                      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│           Data Storage                          │
│  • SQLite database (db.sqlite)                  │
│  • YAML metadata files (data/*/metadata.yaml)   │
│  • Config files (~/.config/hei-datahub/)        │
└─────────────────────────────────────────────────┘
```

## 📁 Directory Structure Explained

```
src/mini_datahub/              # Main Python package
│
├── __init__.py                # Package initialization
├── _version.py                # Auto-generated version file
├── version.py                 # Version utility functions
│
├── app/                       # Application runtime & lifecycle
│   ├── __init__.py
│   ├── runtime.py             # App initialization, startup/shutdown
│   └── settings.py            # Global settings & configuration
│
├── cli/                       # Command-line interface
│   ├── __init__.py
│   └── main.py                # Entry point (hei-datahub command)
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
│   ├── db.py                  # SQLite connection & queries
│   ├── paths.py               # File system paths & constants
│   ├── config_paths.py        # Config file locations
│   ├── git.py                 # Git operations (GitPython)
│   ├── github_api.py          # GitHub REST API client
│   ├── index.py               # Search index operations
│   └── store.py               # Persistent storage operations
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── search.py              # Search queries (FTS5)
│   ├── catalog.py             # Dataset catalog operations
│   ├── sync.py                # GitHub sync operations
│   ├── publish.py             # Publish datasets to GitHub
│   ├── autocomplete.py        # Search autocomplete
│   ├── actions.py             # User actions (open, view, etc.)
│   ├── config.py              # Config file management
│   ├── state.py               # Application state
│   ├── storage.py             # Storage operations
│   ├── outbox.py              # Outbox pattern (async ops)
│   └── update_check.py        # Check for app updates
│
├── ui/                        # Terminal user interface
│   ├── __init__.py
│   ├── theme.py               # Color schemes & styling
│   ├── views/                 # Complete screens
│   │   ├── __init__.py
│   │   ├── main_view.py       # Main catalog view
│   │   ├── search_view.py     # Search interface
│   │   ├── detail_view.py     # Dataset details
│   │   └── help_screen.py     # Help & keybindings
│   └── widgets/               # Reusable UI components
│       ├── __init__.py
│       ├── dataset_list.py    # Dataset list widget
│       ├── search_bar.py      # Search input widget
│       ├── notification.py    # Toast notifications
│       └── ...
│
└── utils/                     # Utility functions & helpers
    ├── __init__.py
    ├── text.py                # Text formatting
    ├── dates.py               # Date handling
    └── ...
```

## 🔄 Data Flow: How a Search Works

Let's trace what happens when a user searches for "climate":

### 1. User Input (UI Layer)
```
User types "climate" in search bar
↓
ui/widgets/search_bar.py → on_input() event
↓
Emits "search_requested" message
```

### 2. View Handles Event (UI Layer)
```
ui/views/main_view.py → on_search_requested()
↓
Calls services.search.search_datasets("climate")
```

### 3. Business Logic (Services Layer)
```
services/search.py → search_datasets()
↓
1. Parse query using core.queries.QueryParser
2. Build SQL query with FTS5
3. Call infra.db.execute_query()
```

### 4. Database Query (Infrastructure Layer)
```
infra/db.py → execute_query()
↓
SELECT * FROM datasets_fts WHERE datasets_fts MATCH 'climate*'
↓
Returns raw SQLite rows
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
- **External APIs** (GitHub)
- **Git operations**
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
- **Clone** GitHub repo with datasets
- **Parse** metadata files
- **Index** into local database
- **Track** updates

### 4. Search
Search uses:
- **FTS5** (Full-Text Search) in SQLite
- **BM25** ranking algorithm
- **Structured queries** (source:github, format:csv)
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
| Add GitHub API call | `infra/github_api.py` |
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
