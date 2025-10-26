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

1. 🔴 services.search — Search query execution *(planned)*
2. 🔴 services.catalog — Dataset management *(planned)*
3. 🔴 services.publish — PR creation workflow *(planned)*
4. 🔴 core.models — Domain models *(planned)*
5. 🔴 infra.db — Database connection *(planned)*
6. 🔴 infra.index — FTS5 search operations *(planned)*

---

## Quick Navigation

### By Layer

- app Module — Application runtime *(planned)*
- core Module — Domain logic *(planned)*
- infra Module — Infrastructure *(planned)*
- services Module — Business logic *(planned)*
- ui Module — User interface *(planned)*
- cli Module — CLI entry point *(planned)*

### By Use Case

**Searching datasets:**
- services.search *(planned)*
- infra.index *(planned)*
- core.queries *(planned)*

**Managing datasets:**
- services.catalog *(planned)*
- infra.store *(planned)*
- core.models *(planned)*

**Publishing changes:**
- services.publish *(planned)*
- infra.git *(planned)*
- infra.github_api *(planned)*

**Building UI:**
- ui.views *(planned)*
- ui.widgets *(planned)*
- ui.theme *(planned)*

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
