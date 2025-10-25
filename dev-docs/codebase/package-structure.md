# Package Structure

## Overview

This document explains the organization of the `mini_datahub` Python package, including the purpose of each module, directory structure, and import conventions.

---

## Directory Layout

```
src/mini_datahub/
├── __init__.py            # Package initialization
├── __main__.py            # Entry point for `python -m mini_datahub`
├── version.py             # Version utilities
├── version.yaml           # Version metadata
├── schema.json            # Dataset JSON schema
│
├── app/                   # Application orchestration
│   ├── __init__.py
│   ├── app_state.py       # Global application state
│   └── lifecycle.py       # App startup/shutdown
│
├── cli/                   # Command-line interface
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   └── commands/          # Command implementations
│       ├── __init__.py
│       ├── auth.py        # Authentication commands
│       ├── sync.py        # Sync commands
│       ├── search.py      # Search commands
│       └── validate.py    # Validation commands
│
├── ui/                    # Terminal user interface (Textual)
│   ├── __init__.py
│   ├── app.py             # Main TUI application
│   ├── views/             # Full-screen views
│   │   ├── __init__.py
│   │   ├── home.py        # Home dashboard
│   │   ├── search.py      # Search interface
│   │   ├── cloud_files.py # Cloud file browser
│   │   ├── settings.py    # Settings editor
│   │   └── outbox.py      # Failed upload queue
│   └── widgets/           # Reusable UI components
│       ├── __init__.py
│       ├── autocomplete.py   # Search autocomplete
│       ├── command_palette.py # Quick commands (Ctrl+P)
│       ├── console.py        # Debug console
│       └── help_overlay.py   # Help screen (F1)
│
├── services/              # Business logic orchestration
│   ├── __init__.py
│   ├── dataset_service.py    # Dataset CRUD operations
│   ├── fast_search.py        # Search orchestration
│   ├── autocomplete.py       # Autocomplete logic
│   ├── index_service.py      # FTS5 index management
│   ├── sync_manager.py       # Background sync
│   ├── catalog.py            # Catalog operations
│   ├── webdav_storage.py     # WebDAV client wrapper
│   └── outbox_manager.py     # Failed upload retry logic
│
├── core/                  # Domain models and business logic
│   ├── __init__.py
│   ├── models.py          # Pydantic domain models
│   ├── interfaces.py      # Abstract base classes
│   └── validators.py      # Business rule validation
│
├── infra/                 # Infrastructure (I/O operations)
│   ├── __init__.py
│   ├── db.py              # Database connection management
│   ├── index.py           # SQLite FTS5 index implementation
│   ├── webdav_storage.py  # WebDAV HTTP client
│   ├── local_cache.py     # Local file cache
│   ├── paths.py           # File path utilities
│   ├── config.py          # Config file handling (TOML)
│   ├── logging.py         # Logging configuration
│   └── sql/               # SQL schema files
│       ├── schema.sql     # Initial schema
│       └── migrations/    # Database migrations
│
├── auth/                  # Authentication module
│   ├── __init__.py
│   ├── credentials.py     # Keyring integration
│   ├── validator.py       # Connection validation
│   ├── setup.py           # Interactive setup wizard
│   └── doctor.py          # Diagnostics tool
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── formatting.py      # Output formatting
│   ├── yaml_utils.py      # YAML parsing/serialization
│   ├── network.py         # Network utilities
│   └── timing.py          # Performance timing decorators
│
└── internal/              # Internal/private modules
    ├── __init__.py
    └── constants.py       # App-wide constants
```

---

## Module Descriptions

### Top-Level Files

#### `__init__.py`

**Purpose:** Package initialization and public API

**Contents:**

```python
"""
Hei-DataHub - Lightweight local data hub with TUI
"""

__version__ = "0.59.0-beta"

# Public API exports
from mini_datahub.core.models import DatasetMetadata
from mini_datahub.services.fast_search import FastSearch

__all__ = [
    "DatasetMetadata",
    "FastSearch",
]
```

**Why expose these?**
- `DatasetMetadata`: Core model, useful for scripting
- `FastSearch`: Main search API

#### `__main__.py`

**Purpose:** Allow running as module (`python -m mini_datahub`)

**Contents:**

```python
"""
Entry point for python -m mini_datahub
"""

from mini_datahub.cli.main import main

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python -m mini_datahub --help
# Equivalent to:
hei-datahub --help
```

#### `version.py`

**Purpose:** Version utilities and metadata access

**Contents:**

```python
from pathlib import Path
import yaml

def get_version() -> str:
    """Get version from version.yaml"""
    version_file = Path(__file__).parent / "version.yaml"
    with open(version_file) as f:
        data = yaml.safe_load(f)
    return data["version"]

def get_release_name() -> str:
    """Get release name (e.g., 'Privacy')"""
    version_file = Path(__file__).parent / "version.yaml"
    with open(version_file) as f:
        data = yaml.safe_load(f)
    return data["release_name"]
```

**Usage:**
```python
from mini_datahub.version import get_version

print(f"Hei-DataHub v{get_version()}")
```

---

### Layer Modules

#### `app/` - Application Orchestration

**Purpose:** Coordinate app lifecycle and manage global state

**Key Files:**

- **`app_state.py`** - Global application state
  ```python
  class AppState:
      """Global state shared across app"""
      current_user: str | None = None
      sync_enabled: bool = True
      last_sync: datetime | None = None
  ```

- **`lifecycle.py`** - Startup/shutdown hooks
  ```python
  def startup():
      """Initialize app (config, DB, auth)"""
      load_config()
      init_database()
      validate_auth()

  def shutdown():
      """Cleanup on exit"""
      close_database()
      flush_logs()
  ```

#### `cli/` - Command-Line Interface

**Purpose:** Provide command-line access to all features

**Structure:**

```
cli/
├── main.py          # argparse setup, dispatch
└── commands/
    ├── auth.py      # auth {setup,doctor,status}
    ├── sync.py      # sync {now,status,disable}
    ├── search.py    # search [query]
    └── validate.py  # validate [dataset-id]
```

**Example Command:**

```python
# cli/commands/auth.py
def setup_command(args):
    """Run interactive auth setup wizard"""
    from mini_datahub.auth.setup import run_setup_wizard
    run_setup_wizard()
```

**CLI Design:**
- **Flat structure:** `hei-datahub auth setup` (not deeply nested)
- **Consistent naming:** Verb-noun or noun-verb
- **Help everywhere:** `--help` on every command

#### `ui/` - Terminal User Interface

**Purpose:** Interactive Textual-based TUI

**Structure:**

```
ui/
├── app.py              # Main TUI app (Textual App)
├── views/              # Full-screen views (screens)
│   ├── home.py         # Home dashboard
│   ├── search.py       # Search + results
│   ├── cloud_files.py  # Cloud file browser
│   ├── settings.py     # Settings editor
│   └── outbox.py       # Failed upload queue
└── widgets/            # Reusable components
    ├── autocomplete.py    # Dropdown suggestions
    ├── command_palette.py # Ctrl+P quick commands
    ├── console.py         # Debug console
    └── help_overlay.py    # F1 help screen
```

**View vs. Widget:**

| Type | Description | Example |
|------|-------------|---------|
| **View** | Full-screen, single focus | `SearchView` (entire search UI) |
| **Widget** | Reusable component | `AutocompleteWidget` (dropdown) |

**Textual Concepts:**
- **App:** Top-level container
- **Screen:** Full-screen view (can have multiple, stack them)
- **Widget:** UI component (button, input, etc.)

#### `services/` - Business Logic

**Purpose:** Orchestrate use cases, coordinate Core + Infra

**Key Services:**

- **`dataset_service.py`** - Dataset CRUD
  ```python
  class DatasetService:
      def save_dataset(self, metadata: DatasetMetadata) -> None:
          # 1. Validate (Core)
          # 2. Update index (Infra)
          # 3. Upload to cloud (Infra)
          # 4. Handle errors (Outbox)
  ```

- **`fast_search.py`** - Search orchestration
  ```python
  class FastSearch:
      def search_indexed(self, query: str) -> list[DatasetMetadata]:
          # 1. Parse query (Core)
          # 2. Execute FTS5 query (Infra)
          # 3. Rank results (Services)
  ```

- **`sync_manager.py`** - Background sync
  ```python
  class SyncManager:
      def sync_now(self) -> SyncResult:
          # 1. List remote files (Infra)
          # 2. Compare with local (Infra)
          # 3. Download/upload changes (Infra)
          # 4. Update index (Infra)
  ```

**Service Responsibilities:**
- Coordinate multiple infrastructure operations
- Handle errors gracefully (outbox pattern)
- Implement retry logic
- Log operations

#### `core/` - Domain Models

**Purpose:** Pure business logic, no I/O

**Key Files:**

- **`models.py`** - Pydantic models
  ```python
  class DatasetMetadata(BaseModel):
      id: str
      dataset_name: str
      description: str
      # ... all fields

      def to_dict(self) -> dict:
          """Serialize for storage"""
          return self.model_dump(by_alias=True)
  ```

- **`interfaces.py`** - Abstract base classes
  ```python
  class StorageProvider(ABC):
      @abstractmethod
      def read_file(self, path: str) -> str: ...

      @abstractmethod
      def write_file(self, path: str, content: str) -> None: ...
  ```

- **`validators.py`** - Business rules
  ```python
  def validate_dataset_id(id: str) -> bool:
      """Validate ID format"""
      return bool(re.match(r"^[a-z0-9][a-z0-9_-]*$", id))
  ```

**Core Rules:**
- ❌ No imports from `services`, `infra`, `ui`, `cli`
- ✅ Only standard library and `pydantic`
- ✅ Pure functions, no side effects

#### `infra/` - Infrastructure

**Purpose:** I/O operations (database, HTTP, filesystem)

**Key Files:**

- **`db.py`** - Database connections
  ```python
  def get_db_connection() -> sqlite3.Connection:
      """Get or create SQLite connection"""
      return sqlite3.connect(DB_PATH)
  ```

- **`index.py`** - FTS5 index implementation
  ```python
  class Index:
      def search(self, query: str, filters: dict) -> list[dict]:
          """Execute FTS5 query"""
          sql = self.build_fts5_query(query, filters)
          return self.execute(sql)
  ```

- **`webdav_storage.py`** - WebDAV client
  ```python
  class WebDAVStorage(StorageProvider):
      def read_file(self, path: str) -> str:
          response = requests.get(self.url + path, auth=self.auth)
          response.raise_for_status()
          return response.text
  ```

- **`config.py`** - Config file handling
  ```python
  def load_config() -> dict:
      """Load config.toml"""
      with open(CONFIG_PATH) as f:
          return tomli.load(f)
  ```

**Infrastructure Rules:**
- ✅ Can import `core` (to implement interfaces)
- ❌ No imports from `services`, `ui`, `cli`
- ✅ Handle all I/O errors gracefully

#### `auth/` - Authentication

**Purpose:** Manage WebDAV credentials securely

**Key Files:**

- **`credentials.py`** - Keyring integration
  ```python
  def store_secret(key_id: str, secret: str) -> None:
      """Store credential in OS keyring"""
      keyring.set_password("hei-datahub", key_id, secret)

  def get_secret(key_id: str) -> str | None:
      """Retrieve credential from keyring"""
      return keyring.get_password("hei-datahub", key_id)
  ```

- **`validator.py`** - Connection testing
  ```python
  def validate_webdav_connection(url: str, token: str) -> bool:
      """Test WebDAV auth and permissions"""
      # 1. Test authentication (401 check)
      # 2. Test read (list files)
      # 3. Test write (create/delete test file)
  ```

- **`setup.py`** - Interactive setup
  ```python
  def run_setup_wizard() -> None:
      """Interactive auth configuration"""
      url = input("WebDAV URL: ")
      token = getpass("Token: ")
      if validate_webdav_connection(url, token):
          store_secret(key_id, token)
          save_config(url, key_id)
  ```

**Auth Module Rules:**
- ✅ All credential access goes through this module
- ❌ No direct `keyring` imports elsewhere
- ✅ Mask credentials in all logs/output

#### `utils/` - Utilities

**Purpose:** Shared helper functions

**Key Files:**

- **`formatting.py`** - Output formatting
  ```python
  def format_dataset_row(dataset: DatasetMetadata) -> str:
      """Format dataset for table display"""
      return f"{dataset.id:30} {dataset.dataset_name}"
  ```

- **`yaml_utils.py`** - YAML operations
  ```python
  def safe_load_yaml(path: Path) -> dict:
      """Load YAML with error handling"""
      try:
          with open(path) as f:
              return yaml.safe_load(f)
      except yaml.YAMLError as e:
          logger.error(f"Invalid YAML in {path}: {e}")
          raise
  ```

- **`network.py`** - Network utilities
  ```python
  def is_network_available() -> bool:
      """Check if network is reachable"""
      try:
          requests.head("https://8.8.8.8", timeout=1)
          return True
      except requests.RequestException:
          return False
  ```

**Utils Guidelines:**
- ✅ Pure functions preferred
- ✅ Minimal dependencies
- ✅ Well-tested (utilities are widely used)

---

## Import Conventions

### Absolute Imports

**Always use absolute imports:**

```python
# ✅ CORRECT
from mini_datahub.core.models import DatasetMetadata
from mini_datahub.services.fast_search import FastSearch

# ❌ WRONG
from ..core.models import DatasetMetadata  # Relative import
```

**Why?**
- Clearer intent
- Easier refactoring
- Better IDE support

### Layer Imports

**Respect layer boundaries:**

```python
# ✅ CORRECT (Service → Core + Infra)
from mini_datahub.core.models import DatasetMetadata
from mini_datahub.infra.index import Index

class DatasetService:
    def __init__(self, index: Index):
        self.index = index
```

```python
# ❌ WRONG (Core → Infra)
# In core/models.py
from mini_datahub.infra.index import Index  # ❌ Violates Clean Architecture

class DatasetMetadata:
    index = Index()  # ❌ Core depends on infrastructure
```

### Circular Imports

**Avoid circular dependencies:**

```python
# ✅ CORRECT: Use TYPE_CHECKING for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mini_datahub.services.sync_manager import SyncManager

class DatasetService:
    def __init__(self, sync_manager: "SyncManager"):
        self.sync_manager = sync_manager
```

---

## Package Distribution

### Installed Package Structure

After `pip install hei-datahub`, the package is installed as:

```
site-packages/
└── mini_datahub/
    ├── __init__.py
    ├── cli/
    ├── ui/
    ├── services/
    ├── core/
    ├── infra/
    ├── auth/
    └── utils/
```

### Entry Points

**Defined in `pyproject.toml`:**

```toml
[project.scripts]
hei-datahub = "mini_datahub.cli.main:main"
mini-datahub = "mini_datahub.cli.main:main"
```

**Creates executable scripts:**
```bash
hei-datahub --help
# Executes: mini_datahub.cli.main:main()
```

---

## Testing Structure

**Tests mirror the package structure:**

```
tests/
├── unit/                  # Unit tests (fast, isolated)
│   ├── core/
│   │   └── test_models.py
│   ├── services/
│   │   └── test_fast_search.py
│   └── infra/
│       └── test_index.py
│
├── integration/           # Integration tests (multi-module)
│   ├── test_search_flow.py
│   └── test_sync_flow.py
│
└── manual/                # Manual test scripts
    └── test_webdav.py
```

**Test Naming:**
- Unit test: `test_{module}.py` (e.g., `test_models.py`)
- Function test: `test_{function_name}()` (e.g., `test_validate_id()`)

---

## Related Documentation

- **[Root Files](root-files.md)** - Project configuration files
- **[Services Module](services-module.md)** - Service layer details
- **[Core Module](core-module.md)** - Core domain logic
- **[Infrastructure Module](infra-module.md)** - I/O operations

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
