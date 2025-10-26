# Core Module Deep Dive

The `core/` module is the **heart of the business logic**. It contains:
- Data models (Pydantic)
- Query parsing
- Business rules
- Custom exceptions

**Key Principle**: This module has **NO external dependencies**. No database, no UI, no HTTP calls. It's pure Python + Pydantic.

## File Structure

```
src/mini_datahub/core/
├── __init__.py         # Package exports
├── models.py           # Pydantic data models
├── queries.py          # Query parsing & structured search
├── rules.py            # Business rules (slugify, validation)
└── errors.py           # Custom exception hierarchy
```

---

## 1. models.py - Data Models

### Purpose
Define **type-safe data structures** using Pydantic for automatic validation.

### Key Classes

#### `DatasetMetadata`
The main data model representing a complete dataset.

```python
from mini_datahub.core.models import DatasetMetadata
from datetime import date

# Create a dataset
dataset = DatasetMetadata(
    id="climate-data-2024",
    dataset_name="Climate Data 2024",
    description="Temperature and precipitation data",
    source="https://data.gov/climate",
    date_created=date(2024, 1, 1),
    storage_location="s3://bucket/climate-2024.nc",
    file_format="NetCDF",
    size="2.5GB",
    data_types=["temperature", "precipitation"],
    tags=["climate", "weather"]
)

# Validate automatically
try:
    dataset.validate()  # Raises ValidationError if invalid
except ValidationError as e:
    print(f"Invalid: {e}")

# Convert to dictionary
dataset_dict = dataset.to_dict()
# {'id': 'climate-data-2024', 'dataset_name': 'Climate Data 2024', ...}
```

**Fields Explained:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | str | ✅ | Unique slug identifier | `"climate-data-2024"` |
| `dataset_name` | str | ✅ | Human-readable name | `"Climate Data 2024"` |
| `description` | str | ✅ | Detailed description | `"Temperature data..."` |
| `source` | str | ✅ | Origin URL or library | `"https://..."` |
| `date_created` | date | ✅ | Creation date | `date(2024, 1, 1)` |
| `storage_location` | str | ✅ | Where data is stored | `"s3://bucket/..."` |
| `file_format` | str | ❌ | File format | `"NetCDF"`, `"CSV"` |
| `size` | str | ❌ | Dataset size | `"2.5GB"` |
| `data_types` | List[str] | ❌ | Types of data | `["temperature"]` |
| `tags` | List[str] | ❌ | Searchable tags | `["climate"]` |
| `used_in_projects` | List[str] | ❌ | Related projects | `["project-x"]` |
| `schema_fields` | List[SchemaField] | ❌ | Data schema | See below |

**Validation Rules:**

```python
# ID must be a valid slug
id="Climate Data"  # ❌ Invalid (spaces, capitals)
id="climate-data"  # ✅ Valid

# ID must start with alphanumeric
id="-climate"  # ❌ Invalid
id="climate-2024"  # ✅ Valid

# Fields have length limits
id="a" * 101  # ❌ Too long (max 100)
dataset_name="a" * 201  # ❌ Too long (max 200)
```

#### `SchemaField`
Defines a single field/column in the dataset schema.

```python
from mini_datahub.core.models import SchemaField

field = SchemaField(
    name="temperature",
    type="float32",
    description="Temperature in Celsius"
)
```

### Internal Workings

#### How Pydantic Validation Works

When you create a `DatasetMetadata` instance:

1. **Type Checking**: Pydantic checks each field's type
2. **Custom Validators**: Runs `@field_validator` functions
3. **Aliases**: Maps YAML keys (e.g., `dataset_name`) to Python attributes
4. **Coercion**: Converts compatible types (e.g., string dates to `date` objects)

```python
# Example: Creating from YAML data
yaml_data = {
    "id": "my-dataset",
    "dataset_name": "My Dataset",
    "date_created": "2024-01-15",  # String
    # ... more fields
}

# Pydantic converts string to date automatically
dataset = DatasetMetadata(**yaml_data)
print(type(dataset.date_created))  # <class 'datetime.date'>
```

#### Custom Validation Example

```python
@field_validator("id")
@classmethod
def validate_id(cls, v: str) -> str:
    """Ensure ID is a valid slug."""
    if not v:
        raise ValueError("ID cannot be empty")
    if not v[0].isalnum():
        raise ValueError("ID must start with alphanumeric")
    return v.lower()
```

**What this does:**
- Runs automatically when `id` field is set
- Validates format
- Converts to lowercase
- Raises `ValueError` if invalid

### Usage in the Codebase

**Loading from YAML:**
```python
# services/catalog.py
import yaml
from mini_datahub.core.models import DatasetMetadata

def load_dataset(yaml_path: str) -> DatasetMetadata:
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return DatasetMetadata(**data)  # Validates automatically
```

**Storing in Database:**
```python
# infra/store.py
def save_dataset(dataset: DatasetMetadata) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO datasets_store (...) VALUES (...)",
        (dataset.id, dataset.dataset_name, ...)
    )
```

**Converting to JSON:**
```python
# For API responses or debugging
dataset_json = dataset.model_dump_json()
# {"id": "climate-data", "dataset_name": "Climate Data", ...}
```

---

## 2. queries.py - Query Parsing

### Purpose
Parse structured search queries like `source:github format:csv "climate data"` into a structured format.

### Key Classes

#### `QueryOperator`
Enum of supported comparison operators.

```python
class QueryOperator(Enum):
    EQ = "="         # Exact match
    GT = ">"         # Greater than
    LT = "<"         # Less than
    GTE = ">="       # Greater than or equal
    LTE = "<="       # Less than or equal
    CONTAINS = ":"   # Contains (default)
```

#### `QueryTerm`
Represents a single query term (field:value or free text).

```python
@dataclass
class QueryTerm:
    field: Optional[str] = None           # Field name or None
    operator: QueryOperator = QueryOperator.CONTAINS
    value: str = ""                       # Search value
    is_free_text: bool = False            # Is this free text?
```

**Examples:**

```python
# Field query: source:webdav
QueryTerm(
    field="source",
    operator=QueryOperator.CONTAINS,
    value="webdav",
    is_free_text=False
)

# Comparison: date:>2024-01-01
QueryTerm(
    field="date_created",
    operator=QueryOperator.GT,
    value="2024-01-01",
    is_free_text=False
)

# Free text: climate
QueryTerm(
    field=None,
    operator=QueryOperator.CONTAINS,
    value="climate",
    is_free_text=True
)
```

#### `ParsedQuery`
The complete parsed query with all terms.

```python
@dataclass
class ParsedQuery:
    terms: List[QueryTerm]           # All query terms
    free_text_query: str = ""        # Combined free text for FTS

    def has_field_filters(self) -> bool:
        """Check if query has field-specific filters."""
        return any(not term.is_free_text for term in self.terms)

    def get_field_terms(self, field: str) -> List[QueryTerm]:
        """Get all terms for a specific field."""
        return [t for t in self.terms if t.field == field]
```

#### `QueryParser`
The main parser class.

### How It Works

**Input Query:**
```
source:webdav format:csv "climate data" temperature
```

**Parsing Steps:**

1. **Extract Field Patterns**
```python
# Regex: (\w+):(>=|<=|>|<)?"([^"]+)"|(\w+):(>=|<=|>|<)?(\S+)
# Matches:
# - source:webdav
# - format:csv
```

2. **Extract Quoted Text**
```python
# Regex: "([^"]+)"
# Matches: "climate data"
```

3. **Extract Remaining Free Text**
```python
# After removing field:value and quotes
# Remaining: temperature
```

4. **Build ParsedQuery**
```python
ParsedQuery(
    terms=[
        QueryTerm(field="source", value="webdav"),
        QueryTerm(field="format", value="csv"),
        QueryTerm(value="climate data", is_free_text=True),
        QueryTerm(value="temperature", is_free_text=True),
    ],
    free_text_query="climate data temperature"
)
```

### Usage Examples

#### Basic Parsing

```python
from mini_datahub.core.queries import QueryParser

parser = QueryParser()
parsed = parser.parse("source:webdav format:csv climate")

print(parsed.terms)
# [
#   QueryTerm(field='source', value='webdav'),
#   QueryTerm(field='format', value='csv'),
#   QueryTerm(value='climate', is_free_text=True)
# ]

print(parsed.free_text_query)
# "climate"

print(parsed.has_field_filters())
# True (has source and format filters)
```

#### Advanced Queries

```python
# Date range queries
query = "date:>2024-01-01 date:<2024-12-31"
parsed = parser.parse(query)

# Size comparisons
query = "size:<100MB"
parsed = parser.parse(query)

# Multiple tags
query = "tag:climate tag:temperature tag:nasa"
parsed = parser.parse(query)

# Complex mixed query
query = 'source:"NASA EARTHDATA" format:netcdf date:>2020 climate temperature'
parsed = parser.parse(query)
```

### Supported Fields

| Field | Alias | Example | Description |
|-------|-------|---------|-------------|
| `source` | - | `source:webdav` | Filter by data source |
| `format` | - | `format:csv` | Filter by file format |
| `type` | - | `type:temperature` | Filter by data type |
| `tag` | `tags` | `tag:climate` | Filter by tag |
| `date_created` | `date` | `date:>2024-01` | Filter by creation date |
| `size` | - | `size:<100MB` | Filter by dataset size |
| `name` | - | `name:climate` | Filter by dataset name |
| `id` | - | `id:my-dataset` | Filter by exact ID |
| `project` | - | `project:gideon` | Filter by project usage |

### Integration with Search

The parsed query is used in `services/search.py`:

```python
def search_datasets(query: str) -> List[Dict]:
    parser = QueryParser()
    parsed = parser.parse(query)

    if parsed.has_field_filters():
        # Build SQL with WHERE clauses for each field
        sql = build_structured_query(parsed)
    else:
        # Use simple FTS5 search
        sql = f"SELECT * FROM datasets_fts WHERE datasets_fts MATCH '{parsed.free_text_query}*'"

    return execute_query(sql)
```

---

## 3. rules.py - Business Rules

### Purpose
Centralize business logic like ID generation, validation, and normalization.

### Key Functions

#### `slugify(text: str) -> str`
Convert any text to a valid dataset ID slug.

```python
from mini_datahub.core.rules import slugify

# Examples
slugify("My Dataset Name")  # → "my-dataset-name"
slugify("Climate_Data_2024")  # → "climate-data-2024"
slugify("NASA EARTH DATA!!!") # → "nasa-earth-data"
slugify("  Multiple   Spaces  ")  # → "multiple-spaces"
```

**Rules:**
1. Convert to lowercase
2. Replace spaces/underscores with hyphens
3. Remove non-alphanumeric characters (except `-` and `_`)
4. Strip leading/trailing hyphens
5. Collapse multiple hyphens to one

**Implementation:**
```python
def slugify(text: str) -> str:
    text = text.lower()                          # Step 1
    text = re.sub(r"[\s_]+", "-", text)         # Step 2
    text = re.sub(r"[^a-z0-9-_]", "", text)     # Step 3
    text = text.strip("-_")                      # Step 4
    text = re.sub(r"-+", "-", text)             # Step 5
    return text
```

#### `generate_unique_id(base_name: str, exists_check: Callable) -> str`
Generate a unique ID, handling collisions with automatic suffixes.

```python
from mini_datahub.core.rules import generate_unique_id

def dataset_exists(id: str) -> bool:
    # Check if ID already in database
    conn = get_connection()
    result = conn.execute("SELECT id FROM datasets WHERE id = ?", (id,))
    return result.fetchone() is not None

# Generate unique ID
id = generate_unique_id("My Dataset", dataset_exists)
# If "my-dataset" exists → "my-dataset-1"
# If "my-dataset-1" exists → "my-dataset-2"
# And so on...
```

**How it works:**
1. Slugify the base name: `"My Dataset"` → `"my-dataset"`
2. Check if it exists using `exists_check("my-dataset")`
3. If exists, add `-1`, `-2`, etc. until unique

**Usage in catalog:**
```python
# services/catalog.py
def create_dataset(name: str, metadata: dict) -> str:
    """Create a new dataset with auto-generated unique ID."""
    dataset_id = generate_unique_id(name, lambda id: dataset_exists(id))
    # Save dataset with this ID
    return dataset_id
```

#### `validate_dataset_id(dataset_id: str) -> tuple[bool, str]`
Validate an ID against all rules.

```python
from mini_datahub.core.rules import validate_dataset_id

# Valid IDs
is_valid, error = validate_dataset_id("my-dataset")
print(is_valid)  # True

is_valid, error = validate_dataset_id("climate_data_2024")
print(is_valid)  # True

# Invalid IDs
is_valid, error = validate_dataset_id("")
print(error)  # "ID cannot be empty"

is_valid, error = validate_dataset_id("My-Dataset")
print(error)  # "ID must contain only lowercase..."

is_valid, error = validate_dataset_id("-invalid")
print(error)  # "ID must start with alphanumeric"

is_valid, error = validate_dataset_id("a" * 101)
print(error)  # "ID must be 100 characters or less"
```

**Validation Rules:**
1. Not empty
2. Max 100 characters
3. Start with alphanumeric (a-z, 0-9)
4. Only lowercase letters, numbers, hyphens, underscores
5. Pattern: `^[a-z0-9][a-z0-9_-]*$`

### Why These Rules?

**URL-safe**: IDs can be used in URLs without encoding
```
https://example.com/datasets/climate-data-2024  ✅
https://example.com/datasets/Climate%20Data%202024  ❌
```

**File-system safe**: IDs can be folder names
```
data/climate-data-2024/  ✅
data/Climate Data 2024/  ❌ (spaces problematic)
```

**Database-friendly**: No special characters that need escaping
```sql
SELECT * FROM datasets WHERE id = 'climate-data-2024'  ✅
SELECT * FROM datasets WHERE id = 'climate:data/2024'  ❌
```

---

## 4. errors.py - Exception Hierarchy

### Purpose
Define custom exceptions for different error scenarios.

### Exception Hierarchy

```
Exception (Python built-in)
└── DataHubError (base for all app errors)
    ├── ValidationError (data validation failures)
    ├── StorageError (file I/O failures)
    ├── IndexError (database failures)
    ├── SyncError (sync/cloud storage failures)
    └── ConfigError (configuration problems)
```

### Usage Examples

#### ValidationError
```python
from mini_datahub.core.errors import ValidationError
from mini_datahub.core.models import DatasetMetadata

try:
    dataset = DatasetMetadata(
        id="Invalid ID!",  # Contains invalid characters
        # ... other fields
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Handle invalid data
```

#### StorageError
```python
from mini_datahub.core.errors import StorageError

try:
    with open(dataset_path) as f:
        data = yaml.safe_load(f)
except IOError as e:
    raise StorageError(f"Failed to load dataset: {e}")
```

#### IndexError (Database)
```python
from mini_datahub.core.errors import IndexError as DataHubIndexError

try:
    conn.execute("INSERT INTO datasets ...")
except sqlite3.Error as e:
    raise DataHubIndexError(f"Database operation failed: {e}")
```

#### SyncError
```python
from mini_datahub.core.errors import SyncError

try:
    webdav_client.download(remote_path)
except httpx.HTTPError as e:
    raise SyncError(f"WebDAV sync failed: {e}")
```

#### ConfigError
```python
from mini_datahub.core.errors import ConfigError

def load_config(path: str):
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    # ... load config
```

### Error Handling Patterns

#### Try-Catch-Reraise
```python
def load_and_validate_dataset(path: str) -> DatasetMetadata:
    """Load dataset from YAML and validate."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        return DatasetMetadata(**data)
    except IOError as e:
        # Convert to domain error
        raise StorageError(f"Failed to read {path}: {e}")
    except pydantic.ValidationError as e:
        # Convert to domain error
        raise ValidationError(f"Invalid dataset metadata: {e}")
```

#### Catch All DataHub Errors
```python
from mini_datahub.core.errors import DataHubError

try:
    dataset = catalog.load_dataset("my-dataset")
    result = search.search_datasets("climate")
    sync.sync_from_webdav()
except DataHubError as e:
    # Catch any application error
    logger.error(f"Operation failed: {e}")
    ui.show_error_notification(str(e))
```

---

## Testing the Core Module

The core module is **pure Python** with no external dependencies, making it easy to test.

### Example Tests

```python
# tests/test_core_models.py
from mini_datahub.core.models import DatasetMetadata
from mini_datahub.core.errors import ValidationError
import pytest
from datetime import date


def test_valid_dataset():
    """Test creating a valid dataset."""
    dataset = DatasetMetadata(
        id="test-dataset",
        dataset_name="Test Dataset",
        description="A test dataset",
        source="https://example.com",
        date_created=date.today(),
        storage_location="/data/test"
    )
    assert dataset.id == "test-dataset"


def test_invalid_id_raises_error():
    """Test that invalid ID raises ValidationError."""
    with pytest.raises(ValidationError):
        DatasetMetadata(
            id="Invalid ID!",  # Spaces and special chars
            # ... other required fields
        )


def test_slugify():
    """Test slug generation."""
    from mini_datahub.core.rules import slugify

    assert slugify("My Dataset") == "my-dataset"
    assert slugify("Climate_Data") == "climate-data"
    assert slugify("NASA!!!") == "nasa"
```

---

## Summary

The `core/` module is:

✅ **Framework-agnostic** - Pure Python + Pydantic
✅ **Testable** - No external dependencies
✅ **Type-safe** - Full type hints and validation
✅ **Reusable** - Can be used in CLI, API, or UI

**Key Files:**
- `models.py` - Data structures (DatasetMetadata)
- `queries.py` - Query parsing (structured search)
- `rules.py` - Business rules (slugify, validation)
- `errors.py` - Exception hierarchy

**Next Steps:**
- [Infrastructure Module →](infra-module.md) (Database & APIs)
- [Services Module →](services-module.md) (Business logic)
- [API Reference →](../api-reference/overview.md) (Detailed API docs - *core module docs planned*)

---

**Practice Exercise:**

Try adding a new field to `DatasetMetadata`:

1. Add `license: Optional[str]` to the model
2. Add validation that license must be one of ["MIT", "Apache-2.0", "GPL-3.0", "CC-BY-4.0"]
3. Update `schema.json` with the new field
4. Write tests for the validation
