# Advanced: Extending Hei-DataHub

**Learning Goal**: Learn the complete workflow for extending Hei-DataHub with new functionality.

By the end of this page, you'll:
- Add new search filters
- Create custom UI components
- Extend metadata schema
- Build new screens
- Follow Clean Architecture patterns

---

## Extension Philosophy

**Clean Architecture Flow:**

```
1. Core Domain   → Define what (models, rules)
2. Services      → Define how (orchestration)
3. Infrastructure → Define where (DB, files)
4. UI            → Define interface (screens, widgets)
```

**Always start from the inside out!**

---

## Example 1: Adding a New Search Filter

**Goal:** Add `owner:alice` filter to search for datasets by owner.

### Step 1: Update Core Query Parser

**File:** `src/mini_datahub/core/queries.py`

```python
class QueryParser:
    """Parse structured search queries."""

    SUPPORTED_FIELDS = {
        "source", "format", "type", "tag", "tags",
        "date_created", "date", "size", "name", "id", "project",
        "owner",  # ← Add this
    }
```

**Test the parser:**

```python
def test_owner_filter_parsing():
    """Test that owner filter is parsed correctly."""
    parser = QueryParser()
    query = parser.parse("climate owner:alice")

    assert query.free_text_query == "climate"
    owner_terms = query.get_field_terms("owner")
    assert len(owner_terms) == 1
    assert owner_terms[0].value == "alice"
```

---

### Step 2: Update FTS Schema

**File:** `src/mini_datahub/infra/sql/schema.sql`

```sql
-- Add owner column to FTS table
CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    owner,  -- ← Add this
    tokenize = 'porter unicode61',
    prefix = '2 3 4'
);
```

**Note:** This requires a database migration!

---

### Step 3: Update Indexing Logic

**File:** `src/mini_datahub/infra/index.py`

```python
def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """Upsert a dataset into both the store and FTS index."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ... (existing store upsert code)

        # Extract owner from creators
        creators = metadata.get("creators", [])
        owner = creators[0].get("name", "") if creators else ""

        # Insert into FTS index
        cursor.execute(
            """
            INSERT INTO datasets_fts (id, name, description, used_in_projects,
                                      data_types, source, file_format, owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (dataset_id, name, description, used_in_projects,
             data_types, source, file_format, owner),  # ← Add owner
        )

        conn.commit()
    finally:
        conn.close()
```

---

### Step 4: Update Search Service

**File:** `src/mini_datahub/services/search.py`

```python
def _structured_search(parsed: ParsedQuery, limit: int) -> List[Dict[str, Any]]:
    """Execute structured search with field filters."""

    # Map field names to FTS columns
    field_mapping = {
        "name": "name",
        "description": "description",
        "project": "used_in_projects",
        "type": "data_types",
        "source": "source",
        "format": "file_format",
        "owner": "owner",  # ← Add this
    }

    # ... (rest of search logic)
```

---

### Step 5: Add Autocomplete Support

**File:** `src/mini_datahub/ui/widgets/autocomplete.py`

```python
class SmartSearchSuggester(Suggester):
    """Context-aware search suggester."""

    def _parse_input(self, value: str):
        # ...
        supported_fields = {
            "source", "project", "tag",
            "owner",  # ← Add this
            "size", "format", "type"
        }
        # ...

    async def get_suggestion(self, value: str):
        # If typing field name, suggest field names
        if is_typing_field:
            field_names = [
                "source:", "project:", "tag:",
                "owner:",  # ← Add this
                "size:", "format:", "type:"
            ]
            # ...
```

---

### Step 6: Populate Suggestions

**File:** `src/mini_datahub/services/suggestion_service.py`

```python
class SuggestionService:
    """Service for autocomplete suggestions."""

    def _build_owner_suggestions(self) -> List[SuggestionItem]:
        """Build owner suggestions from all datasets."""
        owners = set()

        for dataset_id in list_datasets():
            metadata = read_dataset(dataset_id)
            if metadata:
                creators = metadata.get("creators", [])
                for creator in creators:
                    name = creator.get("name")
                    if name:
                        owners.add(name)

        return [
            SuggestionItem(
                key="owner",
                value=owner,
                display_text=owner,
                insert_text=f"owner:{owner}",
                frequency=1,
            )
            for owner in sorted(owners)
        ]

    def rebuild_cache(self) -> None:
        """Rebuild suggestion cache."""
        # ... (existing code)

        # Add owner suggestions
        owner_suggestions = self._build_owner_suggestions()
        for item in owner_suggestions:
            self._suggestions["owner"].append(item)
```

---

### Step 7: Test the Feature

```python
def test_owner_filter_search():
    """Test searching by owner."""
    from mini_datahub.services.search import search_datasets
    from mini_datahub.infra.index import upsert_dataset

    # Setup test data
    upsert_dataset("ds1", {
        "dataset_name": "Dataset 1",
        "creators": [{"name": "Alice"}],
    })

    upsert_dataset("ds2", {
        "dataset_name": "Dataset 2",
        "creators": [{"name": "Bob"}],
    })

    # Test owner filter
    results = search_datasets("owner:alice")
    assert len(results) == 1
    assert results[0]["id"] == "ds1"
```

---

### Step 8: Run Migration

```bash
# Create migration script
$ cat > scripts/migrate_add_owner.py << 'EOF'
from mini_datahub.infra.db import get_connection
from mini_datahub.infra.index import reindex_all

# Drop old FTS table
conn = get_connection()
conn.execute("DROP TABLE IF EXISTS datasets_fts")
conn.close()

# Recreate with new schema
from mini_datahub.infra.db import init_database
init_database()

# Reindex all datasets
count, errors = reindex_all()
print(f"Reindexed {count} datasets")
EOF

$ python scripts/migrate_add_owner.py
```

---

## Example 2: Adding a New Metadata Field

**Goal:** Add `license` field to dataset metadata.

### Step 1: Update Core Models

**File:** `src/mini_datahub/core/models.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class License(BaseModel):
    """License information."""
    name: str = Field(..., description="License name (e.g., MIT, Apache-2.0)")
    url: Optional[str] = Field(None, description="License URL")
    text: Optional[str] = Field(None, description="Full license text")


class DatasetMetadata(BaseModel):
    """Dataset metadata."""
    dataset_name: str
    description: str
    # ... (existing fields)
    license: Optional[License] = None  # ← Add this
```

---

### Step 2: Update JSON Schema

**File:** `schema.json`

```json
{
  "type": "object",
  "properties": {
    "dataset_name": {"type": "string"},
    "description": {"type": "string"},
    "license": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "url": {"type": "string"},
        "text": {"type": "string"}
      },
      "required": ["name"]
    }
  }
}
```

---

### Step 3: Add to UI Edit Form

**File:** `src/mini_datahub/ui/views/edit_dataset.py`

```python
from textual.widgets import Input, TextArea, Select

class EditDatasetScreen(Screen):
    """Screen for editing dataset metadata."""

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            # ... (existing fields)

            # License section
            yield Static("License", classes="section-title")
            yield Input(placeholder="License name (e.g., MIT)", id="license_name")
            yield Input(placeholder="License URL (optional)", id="license_url")
            yield TextArea(id="license_text", classes="license-text")

        yield Footer()

    def on_mount(self) -> None:
        """Load dataset metadata."""
        # ... (load existing metadata)

        # Populate license fields
        license = metadata.get("license")
        if license:
            self.query_one("#license_name", Input).value = license.get("name", "")
            self.query_one("#license_url", Input).value = license.get("url", "")
            self.query_one("#license_text", TextArea).text = license.get("text", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle save button."""
        if event.button.id == "save":
            # ... (collect other fields)

            # Collect license
            license_name = self.query_one("#license_name", Input).value
            if license_name:
                metadata["license"] = {
                    "name": license_name,
                    "url": self.query_one("#license_url", Input).value,
                    "text": self.query_one("#license_text", TextArea).text,
                }

            # Save metadata
            write_dataset(dataset_id, metadata)
```

---

### Step 4: Display in Details View

**File:** `src/mini_datahub/ui/views/dataset_details.py`

```python
def compose(self) -> ComposeResult:
    # ... (existing content)

    # License section
    license = self.metadata.get("license")
    if license:
        yield Static(f"**License:** {license.get('name')}")
        if license.get("url"):
            yield Static(f"  URL: {license.get('url')}")
```

---

## Example 3: Adding a New Screen

**Goal:** Add a "Statistics" screen showing dataset stats.

### Step 1: Create Screen File

**File:** `src/mini_datahub/ui/views/statistics.py`

```python
"""Statistics screen showing dataset insights."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Vertical

class StatisticsScreen(Screen):
    """Screen displaying dataset statistics."""

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("📊 Dataset Statistics", classes="title")

            # Stats table
            table = DataTable()
            table.add_columns("Metric", "Value")
            yield table

        yield Footer()

    def on_mount(self) -> None:
        """Load statistics when screen mounts."""
        from mini_datahub.infra.store import list_datasets
        from mini_datahub.infra.index import get_connection

        # Count datasets
        dataset_ids = list_datasets()
        total_datasets = len(dataset_ids)

        # Count by source
        conn = get_connection()
        cursor = conn.execute(
            "SELECT source, COUNT(*) FROM datasets_fts GROUP BY source"
        )
        sources = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()

        # Populate table
        table = self.query_one(DataTable)
        table.add_row("Total Datasets", str(total_datasets))
        table.add_row("", "")  # Spacer

        for source, count in sources.items():
            table.add_row(f"  {source}", str(count))
```

---

### Step 2: Add Navigation Keybinding

**File:** `src/mini_datahub/ui/views/home.py`

```python
class HomeScreen(Screen):
    """Main home screen."""

    BINDINGS = [
        # ... (existing bindings)
        ("s", "open_statistics", "Statistics"),
    ]

    def action_open_statistics(self) -> None:
        """Open statistics screen."""
        from mini_datahub.ui.views.statistics import StatisticsScreen
        self.app.push_screen(StatisticsScreen())
```

---

### Step 3: Add TCSS Styling

**File:** `src/mini_datahub/ui/styles/default.tcss`

```css
/* Statistics screen styles */
StatisticsScreen {
    background: $background;
}

StatisticsScreen .title {
    text-align: center;
    padding: 1;
    color: $accent;
}

StatisticsScreen DataTable {
    height: 100%;
    margin: 1 2;
}
```

---

## Example 4: Adding a Custom Widget

**Goal:** Create a "TagPill" widget for displaying tags.

### Step 1: Create Widget File

**File:** `src/mini_datahub/ui/widgets/tag_pill.py`

```python
"""Tag pill widget for displaying badges."""
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text

class TagPill(Widget):
    """A pill-shaped tag widget."""

    DEFAULT_CSS = """
    TagPill {
        width: auto;
        height: 1;
        padding: 0 1;
        background: $boost;
        color: $text;
        border: round $primary;
    }

    TagPill:hover {
        background: $primary;
        color: $background;
    }
    """

    label = reactive("")

    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self.label = label

    def render(self) -> Text:
        """Render the tag."""
        return Text(f"#{self.label}", style="bold")

    def on_click(self) -> None:
        """Handle click event."""
        # Emit custom event
        self.post_message(self.TagClicked(self.label))

    class TagClicked(Message):
        """Tag was clicked."""

        def __init__(self, label: str):
            super().__init__()
            self.label = label
```

---

### Step 2: Use Widget in Screen

**File:** `src/mini_datahub/ui/views/dataset_details.py`

```python
from mini_datahub.ui.widgets.tag_pill import TagPill
from textual.containers import Horizontal

def compose(self) -> ComposeResult:
    # ... (existing content)

    # Display tags
    tags = self.metadata.get("keywords", [])
    if tags:
        yield Static("Tags:", classes="label")
        with Horizontal(classes="tags-container"):
            for tag in tags:
                yield TagPill(tag)


def on_tag_pill_tag_clicked(self, event: TagPill.TagClicked) -> None:
    """Handle tag click."""
    # Search for datasets with this tag
    from mini_datahub.ui.views.home import HomeScreen

    home = self.app.query_one(HomeScreen)
    home.search_input.value = f"tag:{event.label}"
    self.app.pop_screen()
```

---

## Example 5: Adding a Service

**Goal:** Add a "RecentDatasetsService" to track recently viewed datasets.

### Step 1: Create Service File

**File:** `src/mini_datahub/services/recent_datasets.py`

```python
"""Service for tracking recently viewed datasets."""
from pathlib import Path
from typing import List
import json
import time

class RecentDatasetsService:
    """Track recently viewed datasets."""

    MAX_RECENT = 10

    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self._recent: List[dict] = []
        self._load()

    def _load(self) -> None:
        """Load recent datasets from cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self._recent = json.load(f)
            except Exception:
                self._recent = []

    def _save(self) -> None:
        """Save recent datasets to cache."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self._recent, f, indent=2)

    def add(self, dataset_id: str, name: str) -> None:
        """Add dataset to recent list."""
        # Remove if already exists
        self._recent = [r for r in self._recent if r["id"] != dataset_id]

        # Add to front
        self._recent.insert(0, {
            "id": dataset_id,
            "name": name,
            "timestamp": time.time(),
        })

        # Trim to max
        self._recent = self._recent[:self.MAX_RECENT]

        self._save()

    def get_recent(self, limit: int = 5) -> List[dict]:
        """Get recent datasets."""
        return self._recent[:limit]
```

---

### Step 2: Register Service

**File:** `src/mini_datahub/app/runtime.py`

```python
from mini_datahub.services.recent_datasets import RecentDatasetsService
from mini_datahub.infra.paths import STATE_DIR

class App:
    """Application runtime."""

    def __init__(self):
        # ... (existing initialization)

        # Initialize recent datasets service
        recent_cache = STATE_DIR / "recent.json"
        self.recent_datasets = RecentDatasetsService(recent_cache)
```

---

### Step 3: Use Service in UI

**File:** `src/mini_datahub/ui/views/dataset_details.py`

```python
def on_mount(self) -> None:
    """Load dataset when screen mounts."""
    # ... (load metadata)

    # Track as recently viewed
    from mini_datahub.app.runtime import get_app
    app = get_app()
    app.recent_datasets.add(
        dataset_id=self.dataset_id,
        name=self.metadata.get("dataset_name", "Unknown")
    )
```

---

## Extension Patterns

### 1. Always Start from Core

```
✅ Good:
  1. Add to core/models.py (domain model)
  2. Add to services/ (business logic)
  3. Add to infra/ (persistence)
  4. Add to ui/ (presentation)

❌ Bad:
  1. Add to UI first
  2. Realize you need a model
  3. Hack it in
```

---

### 2. Use Dependency Injection

```python
# ✅ Good (testable)
class SearchService:
    def __init__(self, db_connection):
        self.conn = db_connection

# ❌ Bad (hard to test)
class SearchService:
    def __init__(self):
        self.conn = get_connection()  # Global state
```

---

### 3. Emit Events, Don't Call Directly

```python
# ✅ Good (loosely coupled)
class TagPill(Widget):
    def on_click(self):
        self.post_message(self.TagClicked(self.label))

# ❌ Bad (tightly coupled)
class TagPill(Widget):
    def on_click(self):
        self.app.search(f"tag:{self.label}")  # Direct dependency
```

---

## What You've Learned

✅ **Clean Architecture flow** — Core → Services → Infra → UI
✅ **Adding search filters** — Query parser, FTS schema, autocomplete
✅ **Adding metadata fields** — Models, schema, UI forms
✅ **Creating screens** — Screen file, navigation, styling
✅ **Building widgets** — Custom widget class, TCSS, events
✅ **Adding services** — Service class, registration, usage
✅ **Extension patterns** — Start from core, DI, events

---

## Next Steps

Now let's optimize performance and debug issues.

**Next:** [Performance Optimization](02-performance.md)

---

## Further Reading

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Textual Widget Development](https://textual.textualize.io/guide/widgets/)
- [Pydantic Models](https://docs.pydantic.dev/latest/)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)
