# How Data Flows Through the App

**Learning Goal**: Understand the complete data flow from UI events to infrastructure and back.

By the end of this page, you'll:
- Trace a user action from UI → Services → Infrastructure
- Understand the 4-layer Clean Architecture
- See how search queries flow through layers
- Learn how datasets are saved and indexed
- Understand separation of concerns
- Build mental models of the system

---

## The Four-Layer Architecture

Hei-DataHub uses **Clean Architecture** (also called Hexagonal Architecture):

```
┌──────────────────────────────────────────┐
│  1. UI LAYER (Textual)                   │  ← User sees this
│  - Screens (HomeScreen, DetailsScreen)   │
│  - Widgets (Input, DataTable, Button)    │
│  - Keybindings & event handlers          │
└──────────────┬───────────────────────────┘
               │ Calls...
┌──────────────▼───────────────────────────┐
│  2. SERVICES LAYER (Business Logic)      │  ← Orchestration
│  - search.py (search_datasets)           │
│  - catalog.py (save_dataset)             │
│  - webdav_storage.py (cloud sync)        │
└──────────────┬───────────────────────────┘
               │ Calls...
┌──────────────▼───────────────────────────┐
│  3. CORE LAYER (Domain Models)           │  ← Business rules
│  - models.py (DatasetMetadata)           │
│  - queries.py (QueryParser)              │
│  - validation rules                      │
└──────────────┬───────────────────────────┘
               │ Calls...
┌──────────────▼───────────────────────────┐
│  4. INFRASTRUCTURE (Storage & Index)     │  ← Data access
│  - db.py (SQLite connection)             │
│  - index.py (FTS5 search index)          │
│  - store.py (YAML file I/O)              │
│  - github_api.py (external services)     │
└──────────────────────────────────────────┘
```

**Dependency Rule:**
Inner layers **don't know** about outer layers.
→ Infrastructure can't import from UI
→ Core can't import from Services
→ Services can import from Core and Infrastructure
→ UI can import from Services

---

## Example 1: User Searches for "climate"

Let's trace a search query through all 4 layers.

### Step 1: UI Layer (User Types)

**File:** `src/hei_datahub/ui/views/home.py`

```python
class HomeScreen(Screen):
    def on_input_changed(self, event: Input.Changed):
        """User types in search box."""
        # Step 1: Get query text
        query = event.value  # "climate"

        # Step 2: Debounce (wait 200ms)
        if self._debounce_timer:
            self._debounce_timer.stop()

        self._debounce_timer = self.set_timer(
            0.2,
            lambda: self.perform_search(query)
        )

    def perform_search(self, query: str):
        """Execute search after debounce."""
        # Step 3: Call service layer
        from hei_datahub.services.search import search_datasets

        results = search_datasets(query, limit=50)  # ← UI → Services

        # Step 4: Display results
        self.populate_table(results)
```

**What happened:**
1. User types → `on_input_changed()` fires
2. Debounce timer waits 200ms
3. Calls `search_datasets(query)` from **Services layer**
4. Gets results back
5. Updates DataTable

---

### Step 2: Services Layer (Business Logic)

**File:** `src/hei_datahub/services/search.py`

```python
def search_datasets(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search datasets with structured query support.

    Supports:
    - source:github
    - format:csv
    - date:>2025-01
    - "quoted terms"
    """
    if not query.strip():
        return []

    # Step 1: Parse query using Core layer
    from hei_datahub.core.queries import QueryParser

    parser = QueryParser()
    parsed = parser.parse(query)  # ← Services → Core

    # Step 2: If simple query, use FTS5
    if not parsed.has_field_filters():
        return _simple_fts_search(parsed.free_text_query, limit)

    # Step 3: Otherwise, use structured search
    return _structured_search(parsed, limit)


def _simple_fts_search(query: str, limit: int) -> List[Dict[str, Any]]:
    """Execute FTS5 search."""
    # Step 1: Get database connection from Infrastructure
    from hei_datahub.infra.db import get_connection

    conn = get_connection()  # ← Services → Infrastructure
    cursor = conn.cursor()

    # Step 2: Build FTS5 query
    tokens = query.split()
    fts_query = " ".join(f"{token}*" for token in tokens)  # climate*

    # Step 3: Execute SQL
    cursor.execute(
        """
        SELECT
            id,
            dataset_name,
            description,
            bm25(datasets_fts) AS rank
        FROM datasets_fts
        WHERE datasets_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (fts_query, limit)
    )

    # Step 4: Return results
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "dataset_name": row[1],
            "description": row[2],
            "rank": row[3]
        }
        for row in rows
    ]
```

**What happened:**
1. Receives query from UI
2. Parses query using **Core layer** (QueryParser)
3. Calls **Infrastructure layer** (get_connection)
4. Executes SQL query
5. Returns results to UI

---

### Step 3: Core Layer (Domain Models)

**File:** `src/hei_datahub/core/queries.py`

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class QueryOperator(Enum):
    """Comparison operators for filters."""
    EQUALS = "="
    GREATER = ">"
    LESS = "<"
    CONTAINS = "~"

@dataclass
class ParsedQuery:
    """Structured representation of a search query."""
    free_text_query: str = ""
    field_filters: List[tuple] = None  # [(field, operator, value), ...]

    def has_field_filters(self) -> bool:
        return bool(self.field_filters)

class QueryParser:
    """Parse search queries into structured format."""

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse query into free text + structured filters.

        Examples:
        - "climate data" → ParsedQuery(free_text_query="climate data")
        - "source:github climate" → ParsedQuery(
            free_text_query="climate",
            field_filters=[("source", EQUALS, "github")]
          )
        - "date:>2025-01" → ParsedQuery(
            field_filters=[("date_created", GREATER, "2025-01")]
          )
        """
        import re

        # Extract field filters (e.g., source:github)
        field_pattern = r'(\w+):([<>]?)([^\s]+)'
        filters = []

        for match in re.finditer(field_pattern, query):
            field = match.group(1)
            operator_str = match.group(2)
            value = match.group(3)

            # Map operator
            if operator_str == ">":
                operator = QueryOperator.GREATER
            elif operator_str == "<":
                operator = QueryOperator.LESS
            else:
                operator = QueryOperator.EQUALS

            filters.append((field, operator, value))

        # Remove field filters from query to get free text
        free_text = re.sub(field_pattern, '', query).strip()

        return ParsedQuery(
            free_text_query=free_text,
            field_filters=filters if filters else None
        )
```

**What happened:**
1. Receives raw query string
2. Parses structured filters (`source:github`)
3. Extracts free text
4. Returns **ParsedQuery** object (domain model)

---

### Step 4: Infrastructure Layer (Database Access)

**File:** `src/hei_datahub/infra/db.py`

```python
import sqlite3
from pathlib import Path
from hei_datahub.infra.config_paths import get_db_path

_connection = None

def get_connection() -> sqlite3.Connection:
    """Get or create database connection."""
    global _connection

    if _connection is None:
        db_path = get_db_path()  # ~/.local/share/hei-datahub/datasets.db
        db_path.parent.mkdir(parents=True, exist_ok=True)

        _connection = sqlite3.connect(str(db_path))
        _connection.row_factory = sqlite3.Row  # Access by column name

        # Enable FTS5
        _connection.execute("PRAGMA journal_mode=WAL")

    return _connection


def ensure_database() -> None:
    """Create tables if they don't exist."""
    conn = get_connection()

    # Create FTS5 virtual table
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts
        USING fts5(
            id UNINDEXED,
            dataset_name,
            description,
            source,
            data_types,
            tags,
            tokenize='porter unicode61'
        )
    """)

    conn.commit()
```

**What happened:**
1. Manages SQLite connection (singleton pattern)
2. Creates FTS5 table if needed
3. Returns connection to Services layer

---

## Example 2: User Adds a Dataset

Now let's see how data flows **down** (UI → Infrastructure) when saving.

### Step 1: UI Layer (Add Dataset Form)

**File:** `src/hei_datahub/ui/views/home.py`

```python
class AddDataScreen(Screen):
    def action_save(self) -> None:
        """User clicks Save button."""
        # Step 1: Collect form data
        metadata = {
            "dataset_name": self.query_one("#input-name", Input).value,
            "description": self.query_one("#input-desc", TextArea).value,
            "source": self.query_one("#input-source", Input).value,
            "date_created": str(date.today()),
            "data_types": self._parse_tags("#input-types"),
        }

        # Step 2: Generate unique ID
        from hei_datahub.services.catalog import generate_id, save_dataset

        dataset_id = generate_id(metadata["dataset_name"])  # ← UI → Services

        # Step 3: Save dataset
        success, error = save_dataset(dataset_id, metadata)  # ← UI → Services

        if success:
            self.app.notify("✓ Dataset saved!", timeout=2)
            self.dismiss(True)  # Return to home screen
        else:
            self.app.notify(f"✗ Failed: {error}", severity="error", timeout=5)
```

**What happened:**
1. Collects form inputs
2. Calls `generate_id()` from Services
3. Calls `save_dataset()` from Services
4. Shows success/error notification

---

### Step 2: Services Layer (Orchestration)

**File:** `src/hei_datahub/services/catalog.py`

```python
from typing import Tuple, Optional
from hei_datahub.core.models import DatasetMetadata
from hei_datahub.infra.store import validate_metadata, write_dataset
from hei_datahub.infra.index import upsert_dataset

def save_dataset(dataset_id: str, metadata: dict) -> Tuple[bool, Optional[str]]:
    """
    Save dataset: validate, write YAML, and index.

    Returns:
        (success: bool, error_message: Optional[str])
    """
    # Step 1: Validate using Core layer
    success, error, model = validate_metadata(metadata)  # ← Services → Core
    if not success:
        return False, error

    try:
        # Step 2: Write to YAML file
        write_dataset(dataset_id, metadata)  # ← Services → Infrastructure

        # Step 3: Index for search
        upsert_dataset(dataset_id, metadata)  # ← Services → Infrastructure

        return True, None

    except Exception as e:
        return False, f"Failed to save: {str(e)}"


def generate_id(base_name: str) -> str:
    """Generate unique dataset ID."""
    from hei_datahub.infra.store import make_unique_id

    return make_unique_id(base_name)  # ← Services → Infrastructure
```

**What happened:**
1. Validates metadata (Core layer)
2. Writes YAML file (Infrastructure)
3. Updates search index (Infrastructure)
4. Returns success/error to UI

---

### Step 3: Core Layer (Validation)

**File:** `src/hei_datahub/infra/store.py` (validation logic)

```python
from hei_datahub.core.models import DatasetMetadata
from pydantic import ValidationError

def validate_metadata(metadata: dict) -> Tuple[bool, Optional[str], Optional[DatasetMetadata]]:
    """
    Validate metadata against schema.

    Returns:
        (is_valid, error_message, model)
    """
    try:
        # Parse with Pydantic model (Core layer)
        model = DatasetMetadata(**metadata)
        return True, None, model

    except ValidationError as e:
        # Extract first error
        error_msg = str(e.errors()[0]['msg'])
        return False, error_msg, None
```

**File:** `src/hei_datahub/core/models.py`

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class DatasetMetadata(BaseModel):
    """Domain model for dataset metadata."""

    dataset_name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    source: str
    date_created: str
    data_types: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    @validator('date_created')
    def validate_date(cls, v):
        """Ensure date is valid format."""
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("date_created must be YYYY-MM-DD format")
```

**What happened:**
1. Pydantic model defines validation rules
2. `validate_metadata()` checks required fields
3. Returns errors if invalid

---

### Step 4: Infrastructure Layer (Storage)

**File:** `src/hei_datahub/infra/store.py`

```python
import yaml
from pathlib import Path
from hei_datahub.infra.config_paths import get_datasets_dir

def write_dataset(dataset_id: str, metadata: dict) -> None:
    """Write metadata to YAML file."""
    # Step 1: Get storage path
    datasets_dir = get_datasets_dir()  # ~/.local/share/hei-datahub/datasets/
    dataset_dir = datasets_dir / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Write metadata.yaml
    yaml_path = dataset_dir / "metadata.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)


def make_unique_id(base_name: str) -> str:
    """Generate unique ID from base name."""
    import re
    from datetime import datetime

    # Step 1: Slugify
    slug = re.sub(r'[^\w\s-]', '', base_name.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')

    # Step 2: Add timestamp if ID already exists
    datasets_dir = get_datasets_dir()
    candidate_id = slug
    counter = 1

    while (datasets_dir / candidate_id).exists():
        candidate_id = f"{slug}-{counter}"
        counter += 1

    return candidate_id
```

**File:** `src/hei_datahub/infra/index.py`

```python
from hei_datahub.infra.db import get_connection

def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """Insert or update dataset in FTS5 index."""
    conn = get_connection()

    # Step 1: Delete old entry if exists
    conn.execute(
        "DELETE FROM datasets_fts WHERE id = ?",
        (dataset_id,)
    )

    # Step 2: Insert new entry
    conn.execute(
        """
        INSERT INTO datasets_fts (
            id, dataset_name, description, source, data_types, tags
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            dataset_id,
            metadata.get('dataset_name', ''),
            metadata.get('description', ''),
            metadata.get('source', ''),
            ' '.join(metadata.get('data_types', [])),
            ' '.join(metadata.get('tags', []))
        )
    )

    conn.commit()
```

**What happened:**
1. Writes YAML file to `~/.local/share/hei-datahub/datasets/{id}/metadata.yaml`
2. Inserts into SQLite FTS5 index for searching
3. Returns success to Services layer

---

## Complete Data Flow Diagram

```
┌─── USER TYPES "climate" ────────────────────────┐
│                                                  │
│  UI Layer (home.py)                              │
│  ├─ on_input_changed(event)                     │
│  ├─ debounce_timer.set()                        │
│  └─ perform_search("climate")                   │
│      │                                           │
│      ↓                                           │
│  Services Layer (search.py)                      │
│  ├─ search_datasets("climate", limit=50)        │
│  ├─ parser.parse("climate")                     │
│  │   │                                           │
│  │   ↓                                           │
│  │  Core Layer (queries.py)                     │
│  │  └─ QueryParser.parse() → ParsedQuery        │
│  │                                               │
│  └─ _simple_fts_search("climate", 50)           │
│      │                                           │
│      ↓                                           │
│  Infrastructure Layer (db.py + index.py)         │
│  ├─ get_connection() → SQLite connection        │
│  ├─ Execute: SELECT * FROM datasets_fts         │
│  │            WHERE datasets_fts MATCH 'climate*'│
│  └─ Return: [{id, name, desc, rank}, ...]       │
│      │                                           │
│      ↓                                           │
│  Services Layer                                  │
│  └─ Return results to UI                        │
│      │                                           │
│      ↓                                           │
│  UI Layer                                        │
│  └─ populate_table(results)                     │
│      │                                           │
│      ↓                                           │
│  USER SEES SEARCH RESULTS                        │
└──────────────────────────────────────────────────┘
```

---

## Why This Architecture?

### 1. **Separation of Concerns**

Each layer has a single responsibility:
- **UI** — Display & user input
- **Services** — Business logic & orchestration
- **Core** — Domain rules & models
- **Infrastructure** — External systems (DB, files, APIs)

---

### 2. **Testability**

You can test layers independently:

```python
# Test Services without UI
def test_search_datasets():
    results = search_datasets("climate", limit=10)
    assert len(results) <= 10
    assert all('dataset_name' in r for r in results)

# Test Core without database
def test_query_parser():
    parser = QueryParser()
    parsed = parser.parse("source:github climate")
    assert parsed.free_text_query == "climate"
    assert parsed.field_filters == [("source", EQUALS, "github")]
```

---

### 3. **Flexibility**

Want to switch from SQLite to PostgreSQL?
→ Only change Infrastructure layer!

Want to switch from Textual to a web UI?
→ Only change UI layer!

---

## What You've Learned

✅ **4-layer architecture** — UI → Services → Core → Infrastructure
✅ **Dependency rule** — Inner layers don't import outer layers
✅ **Search flow** — User input → FTS5 query → results → display
✅ **Save flow** — Form data → validation → YAML + index
✅ **Separation of concerns** — Each layer has one job
✅ **Why it matters** — Testability, flexibility, maintainability

---

## Try It Yourself

### Exercise 1: Trace a Delete Operation

**Goal:** Follow the flow when a user deletes a dataset.

**Hint:** Start in `home.py`:

```python
def action_delete_dataset(self, dataset_id: str):
    # 1. Show confirmation dialog
    # 2. Call service layer
    # 3. Update UI
    pass
```

Trace through:
1. UI layer: Confirmation dialog
2. Services layer: Delete orchestration
3. Infrastructure: Remove YAML, delete from index

---

### Exercise 2: Add a New Search Filter

**Goal:** Add support for `project:gideon` filter.

**Steps:**

1. **Core layer**: Update `QueryParser` to recognize `project` field

2. **Services layer**: Update `_structured_search()` to handle project filter

3. **Infrastructure layer**: Ensure `used_in_projects` is indexed

4. **Test**: Search for `project:gideon` — should filter results!

---

### Exercise 3: Implement Update Flow

**Goal:** Trace how editing a dataset updates both YAML and index.

**Hint:** See `EditDetailsScreen` in `home.py` (lines 1681-2100).

**Flow:**
1. User edits form → `action_save()`
2. Service: `update_dataset(id, new_metadata)`
3. Infrastructure: Overwrite YAML, re-index
4. UI: Refresh details screen

---

## Next Steps

Now you understand **how data flows**. Next, let's dive deep into the **database and search implementation**.

**Next:** [Database & FTS5 Search](02-database.md)

---

## Further Reading

- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Hei-DataHub Architecture Docs](../../architecture/overview.md)
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)
