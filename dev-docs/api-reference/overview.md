# API Reference Overview

Welcome to the Hei-DataHub API reference documentation. This section provides detailed documentation for every public module, class, and function in the codebase.

---

## Structure

The API reference is organized by layer, following the Clean Architecture pattern:

```
api-reference/
├── app/          # Application runtime & settings
├── cli/          # Command-line interface
├── core/         # Domain logic (pure, no I/O)
├── infra/        # Infrastructure (I/O adapters)
├── services/     # Business logic orchestration
└── ui/           # Terminal user interface
```

---

## How to Read API Docs

Each API entry follows this structure:

### Signature
The function/class signature with type hints

### Purpose
What does it do and when should you use it?

### Parameters
Detailed parameter documentation with types, defaults, and validation rules

### Returns
Return type and what it represents

### Raises
Exceptions that can be raised and when

### Side Effects
Any state changes or I/O operations

### Performance
Complexity, typical latency, memory usage

### Usage Examples
Working code examples showing correct usage

### See Also
Links to related APIs and concepts

---

## Coverage Status

See [Coverage Tracker](../maintenance/coverage-tracker.md) for current documentation status.

**Priority modules to document:**

1. 🔴 [services.search](services/search.md) — Search query execution
2. 🔴 [services.catalog](services/catalog.md) — Dataset management
3. 🔴 [services.publish](services/publish.md) — PR creation workflow
4. 🔴 [core.models](core/models.md) — Domain models
5. 🔴 [infra.db](infra/db.md) — Database connection
6. 🔴 [infra.index](infra/index.md) — FTS5 search operations

---

## Quick Navigation

### By Layer

- [app Module](app/runtime.md) — Application runtime
- [core Module](core/models.md) — Domain logic
- [infra Module](infra/db.md) — Infrastructure
- [services Module](services/search.md) — Business logic
- [ui Module](ui/theme.md) — User interface
- [cli Module](cli/main.md) — CLI entry point

### By Use Case

**Searching datasets:**
- [services.search](services/search.md)
- [infra.index](infra/index.md)
- [core.queries](core/queries.md)

**Managing datasets:**
- [services.catalog](services/catalog.md)
- [infra.store](infra/store.md)
- [core.models](core/models.md)

**Publishing changes:**
- [services.publish](services/publish.md)
- [infra.git](infra/git.md)
- [infra.github_api](infra/github_api.md)

**Building UI:**
- [ui.views](ui/views.md)
- [ui.widgets](ui/widgets.md)
- [ui.theme](ui/theme.md)

---

## Conventions

### Type Hints

We use Python type hints throughout:

```python
def function_name(param: str, optional: Optional[int] = None) -> List[str]:
    ...
```

### Error Handling

Functions either:
- Return `Result[T, Error]` types (functional style)
- Raise explicit exceptions (documented in "Raises" section)

### Async Functions

Marked with `async` keyword:

```python
async def async_function() -> Awaitable[str]:
    ...
```

---

## Contributing

Found an API not documented? See [Contributing to Docs](../overview/contributing-docs.md).

Every public function should have:
- ✅ Signature with type hints
- ✅ Purpose statement
- ✅ Parameter documentation
- ✅ Return value documentation
- ✅ Exception documentation
- ✅ At least one usage example

---

**Status:** 🔴 Work in Progress (~5% complete)  
**Goal:** 100% API coverage by Q1 2026
