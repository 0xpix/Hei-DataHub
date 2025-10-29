# Design Principles

## Overview

This document outlines the **core design principles** that guide Hei-DataHub's architecture, code organization, and feature development. These principles ensure consistency, maintainability, and security across the codebase.

---

## Foundational Principles

### 1. Clean Architecture

**Principle:** Separate concerns into layers with strict dependency rules.

```
┌─────────────────────────────────────┐
│         UI / CLI Layer              │  ← User interaction
├─────────────────────────────────────┤
│         Services Layer              │  ← Orchestration
├─────────────────────────────────────┤
│          Core Layer                 │  ← Business logic
├─────────────────────────────────────┤
│      Infrastructure Layer           │  ← I/O operations
└─────────────────────────────────────┘
```

**Dependency Rules:**

- ✅ **Outer layers depend on inner layers**
- ❌ **Inner layers NEVER depend on outer layers**
- ✅ **Core has zero external dependencies**
- ✅ **Infrastructure implements core interfaces**

**Example:**

```python
# ✅ CORRECT: Service depends on Core interface
from hei_datahub.core.interfaces import StorageProvider

class DatasetService:
    def __init__(self, storage: StorageProvider):
        self.storage = storage  # Depends on abstraction
```

```python
# ❌ WRONG: Core depends on Infrastructure
from hei_datahub.infra.webdav_storage import WebDAVStorage

class DatasetMetadata:  # Core domain model
    storage = WebDAVStorage()  # ❌ Direct dependency on concrete impl
```

**Benefits:**

- **Testability:** Mock infrastructure in tests
- **Flexibility:** Swap implementations without changing core
- **Clarity:** Clear separation of concerns

---

### 2. Security First

**Principle:** Security is a primary design constraint, not an afterthought.

**Rules:**

1. **No credentials in files**
   - Always use OS keyring (Secret Service API)
   - Config files contain **references** only
   - Never log credentials (even masked)

2. **HTTPS everywhere**
   - WebDAV over HTTPS (port 443)
   - Reject HTTP connections
   - Validate SSL certificates

3. **Principle of least privilege**
   - Request minimal permissions
   - Scope credentials to specific libraries
   - Allow read-only mode

4. **Secure defaults**
   - Auth required by default
   - SSL verification enabled
   - Private file permissions (600)

**Example:**

```python
# ✅ CORRECT: Store in keyring
from hei_datahub.auth.credentials import store_secret

store_secret(key_id="webdav-heibox-research",
             secret="my-token")
```

```python
# ❌ WRONG: Store in file
import json

config = {"webdav_token": "my-token"}  # ❌ Plaintext credentials
with open("config.json", "w") as f:
    json.dump(config, f)
```

**Security Checklist:**

- [ ] Credentials stored in keyring?
- [ ] Config file has no secrets?
- [ ] HTTPS enforced?
- [ ] Input validated?
- [ ] Error messages don't leak data?

---

### 3. Privacy by Design

**Principle:** User data privacy is paramount.

**Rules:**

1. **Local-first architecture**
   - Search index on user's machine
   - No data sent to third parties
   - User controls all data

2. **Minimal data collection**
   - No analytics
   - No telemetry
   - No usage tracking

3. **User consent**
   - Explicit setup wizard for cloud sync
   - Clear explanations of data flow
   - Optional features (not forced)

4. **Data sovereignty**
   - User chooses storage provider
   - User controls sync frequency
   - User can export all data

**Example:**

```python
# ✅ CORRECT: Local search only
def search_datasets(query: str) -> list[Dataset]:
    """Search local SQLite FTS5 index."""
    return index_service.search(query)
```

```python
# ❌ WRONG: Send to third-party API
def search_datasets(query: str) -> list[Dataset]:
    """Search via external API."""
    response = requests.post(
        "https://thirdparty.com/search",
        json={"query": query, "user": get_user_id()}  # ❌ Leaks data
    )
    return response.json()["results"]
```

---

### 4. SOLID Principles

#### Single Responsibility Principle (SRP)

**Each module has one reason to change.**

```python
# ✅ CORRECT: Single responsibility
class DatasetValidator:
    """Validates dataset metadata only."""
    def validate(self, metadata: dict) -> DatasetMetadata:
        return DatasetMetadata.model_validate(metadata)

class DatasetIndexer:
    """Indexes datasets only."""
    def index(self, dataset: DatasetMetadata) -> None:
        self.db.upsert_dataset(dataset.id, dataset.to_dict())
```

```python
# ❌ WRONG: Multiple responsibilities
class DatasetManager:
    """Does everything (validation, indexing, uploading, searching)."""
    def validate(self, metadata: dict) -> DatasetMetadata: ...
    def index(self, dataset: DatasetMetadata) -> None: ...
    def upload(self, dataset: DatasetMetadata) -> None: ...
    def search(self, query: str) -> list[DatasetMetadata]: ...
    # ❌ Too many reasons to change!
```

#### Open/Closed Principle (OCP)

**Open for extension, closed for modification.**

```python
# ✅ CORRECT: Extend via interface
class StorageProvider(ABC):
    @abstractmethod
    def read_file(self, path: str) -> str: ...
    @abstractmethod
    def write_file(self, path: str, content: str) -> None: ...

class WebDAVStorage(StorageProvider):
    """WebDAV implementation."""
    def read_file(self, path: str) -> str: ...
    def write_file(self, path: str, content: str) -> None: ...

class S3Storage(StorageProvider):  # ✅ Add new provider without changing core
    def read_file(self, path: str) -> str: ...
    def write_file(self, path: str, content: str) -> None: ...
```

#### Liskov Substitution Principle (LSP)

**Subtypes must be substitutable for base types.**

```python
# ✅ CORRECT: All StorageProvider implementations are interchangeable
storage: StorageProvider = WebDAVStorage()  # Can swap implementations
storage: StorageProvider = S3Storage()      # without changing client code
```

#### Interface Segregation Principle (ISP)

**Clients shouldn't depend on interfaces they don't use.**

```python
# ✅ CORRECT: Separate interfaces
class Readable(ABC):
    @abstractmethod
    def read_file(self, path: str) -> str: ...

class Writable(ABC):
    @abstractmethod
    def write_file(self, path: str, content: str) -> None: ...

class ReadOnlyStorage(Readable):  # ✅ Only implements what it needs
    def read_file(self, path: str) -> str: ...

class ReadWriteStorage(Readable, Writable):  # ✅ Composes interfaces
    def read_file(self, path: str) -> str: ...
    def write_file(self, path: str, content: str) -> None: ...
```

#### Dependency Inversion Principle (DIP)

**Depend on abstractions, not concretions.**

```python
# ✅ CORRECT: Depend on abstraction
class DatasetService:
    def __init__(self, storage: StorageProvider):  # ✅ Depends on interface
        self.storage = storage

# Inject concrete implementation
service = DatasetService(storage=WebDAVStorage())
```

```python
# ❌ WRONG: Depend on concrete class
class DatasetService:
    def __init__(self):
        self.storage = WebDAVStorage()  # ❌ Hardcoded dependency
```

---

### 5. Performance Matters

**Principle:** Responsiveness is a feature.

**Performance Targets:**

| Operation | Target | Typical |
|-----------|--------|---------|
| Simple search | <80ms | 50-80ms |
| Autocomplete | <50ms | 20-40ms |
| Dataset save | <200ms | 100-150ms |
| Startup | <2s | 1-1.5s |

**Strategies:**

1. **Cache aggressively**
   - Autocomplete cache (5 min TTL)
   - FTS5 query plan cache
   - WebDAV connection pooling

2. **Optimize database**
   - FTS5 for full-text search (BM25 ranking)
   - Indexes on frequently queried columns
   - PRAGMA optimizations

3. **Debounce user input**
   - Search bar: 300ms debounce
   - Autocomplete: 300ms debounce
   - Reduces queries by ~70%

4. **Background sync**
   - Run in separate thread
   - Don't block UI
   - Batch operations (50 items/chunk)

**Example:**

```python
# ✅ CORRECT: Debounced search
class SearchBar(Input):
    def on_change(self, event):
        self.set_timer(0.3, lambda: self.run_search(event.value))
```

```python
# ❌ WRONG: Search on every keystroke
class SearchBar(Input):
    def on_change(self, event):
        self.run_search(event.value)  # ❌ Triggers 10+ queries for "climate"
```

---

### 6. Fail Gracefully

**Principle:** Handle errors without crashing or losing data.

**Error Handling Rules:**

1. **Validate early**
   - Pydantic validation at boundaries
   - Reject invalid input immediately
   - Show clear error messages

2. **Use outbox pattern**
   - If upload fails → Save to outbox
   - Retry in background
   - User can continue working

3. **Log errors, not secrets**
   - Log context, not credentials
   - Mask tokens in logs
   - Include enough info for debugging

4. **Provide fallbacks**
   - If cloud sync fails → Use cached data
   - If search fails → Show last results
   - If validation fails → Suggest fixes

**Example:**

```python
# ✅ CORRECT: Outbox pattern
try:
    webdav_storage.write_file(path, yaml_content)
except (ConnectionError, TimeoutError) as e:
    logger.warning(f"Upload failed: {e}. Saving to outbox.")
    outbox.add(dataset_id=dataset.id, content=yaml_content)
    # User notified, retry later
```

```python
# ❌ WRONG: Crash on error
webdav_storage.write_file(path, yaml_content)
# ❌ No error handling, app crashes if network fails
```

---

### 7. Test at All Levels

**Principle:** Comprehensive testing builds confidence.

**Testing Strategy:**

```
┌─────────────────────────────────────┐
│         E2E Tests (5%)              │  ← Full user workflows
├─────────────────────────────────────┤
│     Integration Tests (25%)         │  ← Multi-module interactions
├─────────────────────────────────────┤
│       Unit Tests (70%)              │  ← Individual functions
└─────────────────────────────────────┘
```

**Test Pyramid:**

1. **Unit Tests (70%)**
   - Test individual functions
   - Mock all I/O
   - Fast (<1ms per test)

2. **Integration Tests (25%)**
   - Test module interactions
   - Use test doubles for infrastructure
   - Medium speed (10-100ms per test)

3. **E2E Tests (5%)**
   - Test full user workflows
   - Use real infrastructure (test instance)
   - Slow (1-10s per test)

**Example:**

```python
# ✅ CORRECT: Unit test with mocks
def test_search_with_filters():
    mock_index = Mock(spec=IndexService)
    mock_index.search.return_value = [{"id": "test-dataset"}]

    service = FastSearch(index=mock_index)
    results = service.search_indexed("query project:test")

    mock_index.search.assert_called_once_with(
        query_text="query",
        filters={"project": ["test"]}
    )
```

**Test Coverage Goals:**

- **Overall:** >80% line coverage
- **Core logic:** >90% coverage
- **Infrastructure:** >70% coverage (I/O is hard to test)

---

### 8. Document for Humans

**Principle:** Code is read more than written.

**Documentation Rules:**

1. **Docstrings for public APIs**
   - Explain what, not how
   - Include examples
   - Document parameters and return types

2. **Comments for non-obvious logic**
   - Explain **why**, not what
   - Clarify trade-offs
   - Note gotchas

3. **README for modules**
   - Explain module purpose
   - Show usage examples
   - Link to related docs

**Example:**

```python
# ✅ CORRECT: Good docstring
def search_indexed(
    query_text: str,
    filters: dict[str, list[str]] | None = None
) -> list[DatasetMetadata]:
    """
    Search indexed datasets using FTS5.

    Combines full-text search with optional filters (project, tags).

    Args:
        query_text: Search query (FTS5 syntax supported)
        filters: Optional filters like {"project": ["project1"]}

    Returns:
        List of matching datasets, ranked by BM25 relevance.

    Example:
        >>> results = search_indexed("climate", {"project": ["research"]})
        >>> print(results[0].dataset_name)
        'Climate Model Data'
    """
    ...
```

```python
# ❌ WRONG: Useless docstring
def search_indexed(query_text, filters=None):
    """Search datasets."""  # ❌ Doesn't explain anything
    ...
```

---

### 9. Convention Over Configuration

**Principle:** Sensible defaults reduce cognitive load.

**Defaults:**

- **Config location:** `~/.config/hei-datahub/config.toml`
- **Database location:** `~/.local/share/hei-datahub/db.sqlite`
- **WebDAV path:** `/datasets`
- **Sync interval:** 5 minutes
- **Search limit:** 50 results

**Override via:**

- Environment variables (`HEI_DATAHUB_CONFIG_PATH`)
- CLI flags (`--config`, `--db-path`)
- Config file (`sync.interval_minutes = 10`)

**Example:**

```python
# ✅ CORRECT: Sensible defaults
class Config:
    config_path: Path = Path.home() / ".config" / "hei-datahub" / "config.toml"
    db_path: Path = Path.home() / ".local" / "share" / "hei-datahub" / "db.sqlite"
    sync_interval: int = 5  # minutes
```

---

### 10. Developer Experience (DX)

**Principle:** Make the codebase a joy to work with.

**DX Practices:**

1. **Fast feedback loops**
   - Unit tests run in <5s
   - Linting in <2s
   - Type checking in <5s

2. **Clear error messages**
   - Show what went wrong
   - Suggest how to fix it
   - Include relevant context

3. **Easy setup**
   - One-command install (`uv sync`)
   - Setup wizard for config
   - Sample data for testing

4. **Helpful tooling**
   - `Makefile` for common tasks
   - Pre-commit hooks (optional)
   - `hei-datahub auth doctor` for diagnostics

**Example:**

```python
# ✅ CORRECT: Helpful error message
raise ValidationError(
    "Invalid date format. Expected 'YYYY-MM-DD', got '{value}'. "
    "Example: '2024-01-15'"
)
```

```python
# ❌ WRONG: Cryptic error
raise ValueError(f"Bad date: {value}")  # ❌ No guidance
```

---

## Trade-offs & Decisions

### Chosen Trade-offs

| Decision | Trade-off | Rationale |
|----------|-----------|-----------|
| **SQLite for search** | Complexity vs. dependency | Avoid Elasticsearch for simpler deployment |
| **FTS5 instead of FTS3** | Performance vs. compatibility | FTS5 has better ranking (BM25) |
| **Last-write-wins sync** | Simplicity vs. conflict detection | Rare conflicts, simple resolution |
| **Textual TUI** | Limited UI vs. lightweight | Terminal-based fits research workflow |
| **Python 3.11+** | Modern features vs. legacy support | Type hints, match/case improve DX |

### Rejected Alternatives

| Alternative | Why Rejected |
|-------------|--------------|
| **Separate search service** | Too complex for target use case |
| **Real-time sync (inotify)** | Battery drain, complexity |
| **CRDTs for conflict resolution** | Overkill for single-user workflows |
| **GraphQL API** | No need for API (local-first) |
| **React/Electron UI** | Heavyweight, against Unix philosophy |

---

## Evolution of Principles

### v0.57.x → v0.58.x

- **Added:** Privacy by design (removed GitHub dependency)
- **Added:** Security first (keyring integration)
- **Removed:** GitHub-specific auth flows

### v0.58.x → v0.59.x

- **Added:** Outbox pattern for resilience
- **Added:** Read-only mode for shared datasets
- **Improved:** Error handling and user feedback

---

## Checklist for New Features

When adding a feature, ask:

- [ ] Does it follow Clean Architecture?
- [ ] Does it respect layer boundaries?
- [ ] Are credentials handled securely?
- [ ] Is user privacy protected?
- [ ] Does it meet performance targets?
- [ ] Is error handling comprehensive?
- [ ] Are there unit tests?
- [ ] Is the public API documented?
- [ ] Do defaults make sense?
- [ ] Is the DX good?

---

## Related Documentation

- **[Architecture Overview](overview.md)** - System architecture
- **[Data Flow](data-flow.md)** - Data movement through layers
- **[Security & Privacy](security-privacy.md)** - Security implementation details
- **[Contributing Workflow](../contributing/workflow.md)** - Development process

---

**Last Updated:** October 29, 2025 | **Version:** 0.60.0-beta "Clean-up"
