# Glossary

## A

### ADR (Architecture Decision Record)
A document that captures an important architectural decision along with its context and consequences. See [ADRs](../adr/index.md).

### Adapter Pattern
A design pattern that allows incompatible interfaces to work together. Used in Hei-DataHub for infrastructure layer components (e.g., swapping storage backends).

### API (Application Programming Interface)
The set of functions, classes, and methods that comprise the public interface of a module or system.

---

## C

### Clean Architecture
An architectural pattern that separates business logic (Core) from I/O concerns (Infrastructure), with Services orchestrating between them.

### CLI (Command-Line Interface)
The terminal-based interface for running Hei-DataHub commands like `hei-datahub reindex`.

### Core
The domain layer of Hei-DataHub containing pure business logic with no I/O dependencies. Located in `src/mini_datahub/core/`.

---

## D

### Dataset
A collection of data with consistent metadata. In Hei-DataHub, datasets are represented by YAML files in `data/*/metadata.yaml`.

### Dependency Injection (DI)
A design pattern where dependencies are provided to a component rather than created internally. Used in `app/runtime.py`.

### DoD (Definition of Done)
A checklist that defines when a feature or task is truly complete. See [Definition of Done](../contributing/definition-of-done.md).

---

## F

### FTS5 (Full-Text Search 5)
SQLite's full-text search extension used by Hei-DataHub for fast dataset search. See [SQLite FTS5 docs](https://www.sqlite.org/fts5.html).

---

## G

### Git Stash
A Git feature that temporarily saves uncommitted changes. Hei-DataHub uses auto-stash to prevent data loss during PR operations.

---

## H

### Hexagonal Architecture
See **Ports and Adapters**. Another name for the architectural pattern we use.

---

## I

### Infrastructure Layer
The layer responsible for I/O operations (database, filesystem, network). Located in `src/mini_datahub/infra/`.

### Integrator
A user who extends Hei-DataHub by writing plugins, adapters, or integrations.

---

## M

### Maintainer
A core team member responsible for reviewing PRs, managing releases, and maintaining the project.

### Metadata
Structured information about a dataset (title, description, tags, etc.). Stored in YAML format.

---

## P

### PAT (Personal Access Token)
A GitHub authentication token used for API operations. Stored securely in OS keyring.

### Ports and Adapters
An architectural pattern where the core business logic (ports) is isolated from external systems (adapters). Same as Hexagonal Architecture.

### PR (Pull Request)
A GitHub feature for proposing changes to a repository. Hei-DataHub can automatically create PRs for dataset changes.

### Pydantic
A Python library for data validation using type annotations. Used extensively in Hei-DataHub's Core layer.

---

## R

### Reindex
The process of rebuilding the FTS5 search index from YAML files. Command: `hei-datahub reindex`.

---

## S

### SemVer (Semantic Versioning)
A versioning scheme using `MAJOR.MINOR.PATCH` format. See [Versioning Policy](../versioning.md).

### Service Layer
The layer that orchestrates business logic by coordinating Core and Infrastructure. Located in `src/mini_datahub/services/`.

### Singleton Pattern
A design pattern ensuring only one instance of a class exists. Used for database connections in `infra/db.py`.

---

## T

### Textual
A Python framework for building terminal user interfaces (TUIs). Powers Hei-DataHub's UI.

### TUI (Terminal User Interface)
A text-based user interface that runs in the terminal. The main interface for Hei-DataHub.

---

## U

### uv
A fast Python package manager used by Hei-DataHub for dependency management. See [uv docs](https://github.com/astral-sh/uv).

---

## X

### XDG Base Directory Specification
A standard for organizing config files on Linux/Unix systems. Hei-DataHub respects `XDG_CONFIG_HOME` and `XDG_DATA_HOME`.

---

## Y

### YAML (YAML Ain't Markup Language)
A human-readable data serialization format. Used for dataset metadata and configuration files.

---

## Project-Specific Terms

### Auto-Stash
A feature in Hei-DataHub's git operations that automatically stashes uncommitted changes before dangerous operations (like pull or PR creation) to prevent data loss.

### Catalog Service
The service responsible for adding, updating, and deleting datasets. Located in `services/catalog.py`.

### Critter Parade
A fun UI feature (from v0.57.x-beta development notes) for displaying animated characters in the TUI.

### Dataset Inventory
Another term for the collection of datasets managed by Hei-DataHub.

### Outbox
A queue for failed PR creation attempts that can be retried later. Located in `services/outbox.py`.

### Publish Workflow
The process of saving a dataset, committing changes, pushing to GitHub, and creating a PR.

### Search DSL
The query language used for searching datasets. Supports FTS5 syntax with additional filters.

---

## Common Acronyms

| Acronym | Full Term |
|---------|-----------|
| ADR | Architecture Decision Record |
| API | Application Programming Interface |
| CI/CD | Continuous Integration / Continuous Deployment |
| CLI | Command-Line Interface |
| DB | Database |
| DI | Dependency Injection |
| DoD | Definition of Done |
| DSL | Domain-Specific Language |
| FTS | Full-Text Search |
| I/O | Input/Output |
| ORM | Object-Relational Mapping |
| PAT | Personal Access Token |
| PR | Pull Request |
| SLA | Service Level Agreement |
| SQL | Structured Query Language |
| TUI | Terminal User Interface |
| UI | User Interface |
| YAML | YAML Ain't Markup Language |

---

## Conventions

### Code Conventions

- **snake_case**: Variables and functions (`search_datasets`)
- **PascalCase**: Classes (`Dataset`, `SearchService`)
- **UPPER_CASE**: Constants (`UPDATE_CHECK_URL`)
- **_private**: Internal/private members (`_internal_function`)

### Git Conventions

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **refactor**: Code refactoring
- **test**: Adding/fixing tests
- **chore**: Maintenance

---

## Further Reading

- **Architecture:** [System Overview](../architecture/overview.md)
- **Contributing:** [Contributor Workflow](../contributing/workflow.md)
- **APIs:** [API Reference](../api-reference/overview.md)



---

**Missing a term?** [Add it to this glossary](../overview/contributing-docs.md) by submitting a PR!
