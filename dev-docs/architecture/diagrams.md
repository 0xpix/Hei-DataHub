# Architecture Diagrams

## Overview

This document contains visual representations of Hei-DataHub's architecture, including component diagrams, sequence diagrams, deployment views, and data flow illustrations.

---

## System Context Diagram

**High-level view of Hei-DataHub in its environment:**

```mermaid
C4Context
    title System Context Diagram - Hei-DataHub

    Person(researcher, "Researcher", "Uses Hei-DataHub to<br/>manage datasets")

    System(datahub, "Hei-DataHub", "Dataset management<br/>and search system")

    System_Ext(heibox, "HeiBox/Seafile", "Cloud storage via<br/>WebDAV (HTTPS)")
    System_Ext(keyring, "Linux Keyring", "Secure credential<br/>storage (Secret Service)")
    System_Ext(sqlite, "SQLite", "Local search index<br/>(FTS5)")

    Rel(researcher, datahub, "Uses CLI/TUI")
    Rel(datahub, heibox, "Sync datasets<br/>(WebDAV)", "HTTPS")
    Rel(datahub, keyring, "Store/retrieve<br/>credentials", "D-Bus")
    Rel(datahub, sqlite, "Search datasets", "SQL")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

---

## Container Diagram

**Internal structure of Hei-DataHub:**

```mermaid
C4Container
    title Container Diagram - Hei-DataHub Components

    Person(user, "User", "Researcher")

    Container_Boundary(datahub, "Hei-DataHub") {
        Container(cli, "CLI", "Python", "Command-line<br/>interface")
        Container(tui, "TUI", "Textual", "Terminal UI")
        Container(services, "Services", "Python", "Business logic<br/>orchestration")
        Container(core, "Core", "Python", "Domain models<br/>and logic")
        Container(infra, "Infrastructure", "Python", "I/O operations")
    }

    System_Ext(heibox, "HeiBox", "WebDAV storage")
    System_Ext(keyring, "Keyring", "Credential storage")
    ContainerDb(db, "SQLite", "Search index")

    Rel(user, cli, "Runs commands")
    Rel(user, tui, "Interacts with UI")
    Rel(cli, services, "Calls")
    Rel(tui, services, "Calls")
    Rel(services, core, "Uses")
    Rel(services, infra, "Uses")
    Rel(infra, heibox, "HTTPS requests")
    Rel(infra, keyring, "D-Bus calls")
    Rel(infra, db, "SQL queries")
```

---

## Component Diagram

**Detailed view of layer components:**

```
┌──────────────────────────────────────────────────────────────────┐
│                          UI / CLI Layer                          │
├───────────────────────────┬──────────────────────────────────────┤
│   TUI (Textual)           │   CLI (argparse)                     │
│   ├─ HomeView             │   ├─ auth commands                   │
│   ├─ SearchView           │   ├─ sync commands                   │
│   ├─ CloudFilesView       │   ├─ search commands                 │
│   ├─ SettingsView         │   └─ validate commands               │
│   ├─ OutboxView           │                                      │
│   └─ Widgets              │                                      │
│       ├─ Autocomplete     │                                      │
│       ├─ CommandPalette   │                                      │
│       └─ HelpOverlay      │                                      │
└───────────────────────────┴──────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────┐
│                         Services Layer                           │
├──────────────────────────────────────────────────────────────────┤
│  ├─ dataset_service.py     - Dataset CRUD operations             │
│  ├─ fast_search.py         - Search orchestration                │
│  ├─ autocomplete.py        - Suggestion generation               │
│  ├─ index_service.py       - FTS5 index management               │
│  ├─ sync_manager.py        - Background sync orchestration       │
│  └─ catalog.py             - Dataset catalog management          │
└──────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────┐
│                          Core Layer                              │
├──────────────────────────────────────────────────────────────────┤
│  ├─ models.py              - Pydantic domain models              │
│  │   ├─ DatasetMetadata   - Main dataset model                  │
│  │   ├─ SearchQuery       - Search parameters                   │
│  │   └─ SyncStatus        - Sync state                          │
│  ├─ interfaces.py          - Abstract base classes               │
│  │   ├─ StorageProvider   - Storage abstraction                 │
│  │   └─ SearchProvider    - Search abstraction                  │
│  └─ validators.py          - Business rule validation            │
└──────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                        │
├──────────────────────────────────────────────────────────────────┤
│  Storage:                   │  Authentication:                   │
│  ├─ webdav_storage.py       │  ├─ credentials.py                 │
│  └─ local_cache.py          │  ├─ validator.py                   │
│                             │  └─ setup.py                       │
│  Database:                  │                                    │
│  ├─ index.py (FTS5)         │  Utils:                            │
│  ├─ db.py (connections)     │  ├─ paths.py                       │
│  └─ migrations.py           │  ├─ config.py                      │
│                             │  └─ logging.py                     │
└─────────────────────────────┴────────────────────────────────────┘
```

---

## Layer Dependency Graph

**Allowed dependencies between layers:**

```mermaid
graph TD
    UI[UI Layer<br/>Textual Views & Widgets]
    CLI[CLI Layer<br/>argparse Commands]
    Services[Services Layer<br/>Orchestration]
    Core[Core Layer<br/>Domain Models]
    Infra[Infrastructure Layer<br/>I/O Operations]
    Auth[Auth Module<br/>Credential Management]

    UI -->|calls| Services
    CLI -->|calls| Services
    Services -->|uses| Core
    Services -->|uses| Infra
    Services -->|uses| Auth
    Infra -->|implements| Core
    Auth -->|uses| Core

    style Core fill:#d4edda
    style Services fill:#fff4e1
    style Infra fill:#f8d7da
    style UI fill:#e1f5ff
    style CLI fill:#e1f5ff
    style Auth fill:#ffe1e1
```

**Forbidden dependencies:**

```mermaid
graph TD
    Core[Core Layer]
    Infra[Infrastructure Layer]
    Services[Services Layer]
    UI[UI/CLI Layer]

    Core -.->|❌ NEVER| Infra
    Core -.->|❌ NEVER| Services
    Core -.->|❌ NEVER| UI
    Infra -.->|❌ NEVER| Services
    Infra -.->|❌ NEVER| UI

    style Core fill:#d4edda
    style Infra fill:#f8d7da
    style Services fill:#fff4e1
    style UI fill:#e1f5ff
```

---

## Sequence Diagrams

### 1. Search Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as SearchView<br/>(TUI)
    participant FS as fast_search<br/>(Services)
    participant IS as index_service<br/>(Services)
    participant IX as index<br/>(Infra)
    participant DB as SQLite FTS5

    User->>UI: Type "climate data"
    Note over UI: Debounce 300ms
    UI->>FS: search_indexed("climate data")
    FS->>FS: Parse query + filters
    FS->>IS: search(query, filters)
    IS->>IX: build_fts5_query()
    IX->>DB: SELECT ... MATCH 'climate data'
    DB-->>IX: Matching rows
    IX-->>IS: Raw results
    IS->>IS: Format results
    IS-->>FS: List[Dataset]
    FS->>FS: Apply ranking
    FS-->>UI: Ranked results
    UI->>UI: Update result list
    UI-->>User: Display results
```

### 2. Dataset Save Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as DatasetForm<br/>(TUI)
    participant DS as dataset_service<br/>(Services)
    participant Val as Validator<br/>(Core)
    participant IX as index<br/>(Infra)
    participant WD as webdav_storage<br/>(Infra)
    participant Cloud as HeiBox

    User->>UI: Fill form & Save
    UI->>Val: validate(metadata)
    Val->>Val: Pydantic validation
    alt Validation fails
        Val-->>UI: ValidationError
        UI-->>User: Show errors
    else Validation succeeds
        Val-->>UI: Valid metadata ✅
        UI->>DS: save_dataset(metadata)
        DS->>IX: upsert_dataset()
        IX->>IX: Update SQLite
        IX-->>DS: ✅ Indexed
        DS->>WD: write_file(path, yaml)
        WD->>Cloud: PUT /datasets/{id}/metadata.yaml
        alt Upload fails
            Cloud-->>WD: Error
            WD-->>DS: Upload failed
            DS->>DS: Save to outbox
            DS-->>UI: "Saved locally, will sync later"
        else Upload succeeds
            Cloud-->>WD: 201 Created
            WD-->>DS: ✅ Uploaded
            DS-->>UI: Success
        end
        UI-->>User: "Dataset saved!"
    end
```

### 3. Background Sync Flow

```mermaid
sequenceDiagram
    autonumber
    participant Timer as Background Timer<br/>(5 min)
    participant SM as SyncManager<br/>(Services)
    participant WD as webdav_storage<br/>(Infra)
    participant Cloud as HeiBox
    participant IX as index<br/>(Infra)

    loop Every 5 minutes
        Timer->>SM: trigger_sync()
        SM->>WD: listdir("datasets")
        WD->>Cloud: PROPFIND /datasets
        Cloud-->>WD: File list + timestamps
        WD-->>SM: Remote files

        SM->>IX: get_local_files()
        IX-->>SM: Local files + timestamps

        SM->>SM: Compare timestamps

        alt Remote file newer
            SM->>WD: read_file(path)
            WD->>Cloud: GET /datasets/{id}
            Cloud-->>WD: YAML content
            WD-->>SM: File content
            SM->>IX: upsert_dataset(metadata)
            IX-->>SM: ✅ Updated locally
        end

        alt Local file newer
            SM->>IX: get_dataset(id)
            IX-->>SM: Metadata
            SM->>WD: write_file(path, yaml)
            WD->>Cloud: PUT /datasets/{id}
            Cloud-->>WD: ✅ Updated
        end

        SM-->>Timer: Sync complete
    end
```

### 4. Authentication Setup Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as auth setup<br/>(CLI)
    participant Setup as setup_wizard<br/>(Auth)
    participant Val as validator<br/>(Auth)
    participant Cred as credentials<br/>(Auth)
    participant KR as Linux Keyring
    participant WD as WebDAV Server

    User->>CLI: hei-datahub auth setup
    CLI->>Setup: run_wizard()
    Setup->>User: Prompt for URL
    User-->>Setup: https://heibox...
    Setup->>User: Prompt for library
    User-->>Setup: research-datasets
    Setup->>User: Prompt for token
    User-->>Setup: ••••••••••

    Setup->>Val: validate_connection(url, token)
    Val->>WD: PROPFIND (auth test)
    alt Auth fails
        WD-->>Val: 401 Unauthorized
        Val-->>Setup: Invalid credentials
        Setup-->>User: "Authentication failed, try again"
    else Auth succeeds
        WD-->>Val: 200 OK + file list
        Val->>WD: PUT test.txt (write test)
        WD-->>Val: 201 Created
        Val->>WD: DELETE test.txt
        WD-->>Val: 204 No Content
        Val-->>Setup: ✅ All tests passed

        Setup->>Setup: Generate key_id
        Setup->>Cred: store_secret(key_id, token)
        Cred->>KR: keyring.set_password()
        KR-->>Cred: ✅ Stored securely
        Cred-->>Setup: ✅ Saved

        Setup->>Setup: Save config.toml
        Setup-->>CLI: ✅ Setup complete
        CLI-->>User: "✅ WebDAV auth configured!"
    end
```

---

## Deployment Diagram

**Runtime environment on researcher's machine:**

```
┌───────────────────────────────────────────────────────────────────┐
│                      Researcher's Laptop (Linux)                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │               Hei-DataHub Process                       │     │
│  │                                                         │     │
│  │  ┌───────────────┐  ┌───────────────┐                  │     │
│  │  │   TUI Thread  │  │  Sync Thread  │                  │     │
│  │  │   (Textual)   │  │  (Background) │                  │     │
│  │  └───────┬───────┘  └───────┬───────┘                  │     │
│  │          │                   │                          │     │
│  │          └─────────┬─────────┘                          │     │
│  │                    │                                    │     │
│  │              ┌─────▼──────┐                             │     │
│  │              │  Services  │                             │     │
│  │              └─────┬──────┘                             │     │
│  │                    │                                    │     │
│  │         ┌──────────┴──────────┐                         │     │
│  │         │                     │                         │     │
│  │    ┌────▼────┐          ┌────▼────┐                    │     │
│  │    │  Core   │          │  Infra  │                    │     │
│  │    └─────────┘          └────┬────┘                    │     │
│  │                              │                          │     │
│  └──────────────────────────────┼──────────────────────────┘     │
│                                 │                                │
│  ┌──────────────────────────────┼──────────────────────────┐     │
│  │       Local Storage          │                          │     │
│  │                              │                          │     │
│  │  ~/.config/hei-datahub/      │                          │     │
│  │  ├─ config.toml (refs)       │                          │     │
│  │  └─ logs/                    │                          │     │
│  │                              │                          │     │
│  │  ~/.local/share/hei-datahub/ │                          │     │
│  │  ├─ db.sqlite (FTS5 index) ◄─┘                          │     │
│  │  └─ outbox/ (failed uploads)                            │     │
│  │                                                          │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │         Linux Keyring (Secret Service API)              │     │
│  │         ├─ webdav-heibox-research: "token123"           │     │
│  │         └─ (encrypted by OS)                            │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                   │
└───────────────────────────────────────┬───────────────────────────┘
                                        │
                                        │ HTTPS (443)
                                        │
                    ┌───────────────────▼────────────────────┐
                    │       HeiBox/Seafile Server            │
                    │                                        │
                    │  /research-datasets/                   │
                    │  └─ datasets/                          │
                    │      ├─ climate-data/                  │
                    │      │   └─ metadata.yaml              │
                    │      └─ ocean-temp/                    │
                    │          └─ metadata.yaml              │
                    │                                        │
                    └────────────────────────────────────────┘
```

---

## Data Flow Diagram

**How data moves through the system:**

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Validation   │ (Pydantic)
                    │   (Core)       │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  Orchestration │ (Services)
                    │                │
                    └───┬────────┬───┘
                        │        │
          ┌─────────────┘        └─────────────┐
          │                                    │
    ┌─────▼──────┐                      ┌──────▼─────┐
    │   Local    │                      │   Cloud    │
    │   Index    │                      │  Storage   │
    │  (SQLite)  │                      │  (WebDAV)  │
    └─────┬──────┘                      └──────┬─────┘
          │                                    │
          │         ┌──────────────┐           │
          └────────►│ Background   │◄──────────┘
                    │ Sync (5 min) │
                    └──────────────┘
```

**Data transformations:**

```
User Form Fields (dict)
    ↓
Pydantic Validation (DatasetMetadata)
    ↓
Services Layer (orchestration)
    ↓
    ├─ Local: JSON → SQLite FTS5 index
    └─ Cloud: YAML → WebDAV storage
```

---

## Module Organization

**Directory structure with responsibilities:**

```
src/mini_datahub/
│
├── cli/                    # CLI Layer
│   ├── commands/
│   │   ├── auth.py         - Auth commands
│   │   ├── sync.py         - Sync commands
│   │   └── search.py       - Search commands
│   └── main.py             - CLI entry point
│
├── ui/                     # UI Layer (Textual)
│   ├── views/
│   │   ├── home.py         - Home dashboard
│   │   ├── search.py       - Search interface
│   │   ├── cloud_files.py  - Cloud file browser
│   │   ├── settings.py     - Settings editor
│   │   └── outbox.py       - Failed upload queue
│   ├── widgets/
│   │   ├── autocomplete.py - Search suggestions
│   │   ├── command_palette.py - Quick commands (Ctrl+P)
│   │   └── help_overlay.py - Help screen (F1)
│   └── app.py              - TUI main app
│
├── services/               # Services Layer
│   ├── dataset_service.py  - Dataset CRUD
│   ├── fast_search.py      - Search orchestration
│   ├── autocomplete.py     - Autocomplete logic
│   ├── index_service.py    - Index management
│   ├── sync_manager.py     - Sync orchestration
│   └── catalog.py          - Catalog operations
│
├── core/                   # Core Layer
│   ├── models.py           - Pydantic domain models
│   ├── interfaces.py       - Abstract base classes
│   └── validators.py       - Business rule validation
│
├── infra/                  # Infrastructure Layer
│   ├── db.py               - Database connections
│   ├── index.py            - FTS5 implementation
│   ├── webdav_storage.py   - WebDAV client
│   ├── local_cache.py      - Local file cache
│   ├── paths.py            - Path utilities
│   ├── config.py           - Config file handling
│   └── logging.py          - Logging setup
│
├── auth/                   # Auth Module
│   ├── credentials.py      - Keyring integration
│   ├── validator.py        - Connection validation
│   └── setup.py            - Setup wizard
│
└── utils/                  # Utilities
    ├── formatting.py       - Output formatting
    ├── yaml_utils.py       - YAML parsing
    └── network.py          - Network utilities
```

---

## State Machine Diagrams

### Dataset Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: User creates dataset
    Draft --> Validating: User saves
    Validating --> Invalid: Validation fails
    Validating --> Indexed: Validation succeeds
    Invalid --> Draft: User corrects errors
    Indexed --> Uploading: Background upload
    Uploading --> Failed: Network error
    Uploading --> Synced: Upload succeeds
    Failed --> Outbox: Retry later
    Outbox --> Uploading: Retry attempt
    Synced --> Indexed: User edits locally
    Indexed --> Uploading: User saves changes
    Synced --> [*]: User deletes
```

### Sync State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: App starts
    Idle --> Checking: Timer triggers (5 min)
    Idle --> Checking: User triggers sync
    Checking --> Comparing: Got remote file list
    Comparing --> Downloading: Remote newer
    Comparing --> Uploading: Local newer
    Comparing --> Idle: No changes
    Downloading --> Indexing: Downloaded successfully
    Uploading --> Idle: Uploaded successfully
    Indexing --> Idle: Index updated
    Downloading --> Error: Network failure
    Uploading --> Error: Network failure
    Error --> Idle: Log error
    Error --> Outbox: Save to retry queue
```

---

## Network Communication

**WebDAV protocol usage:**

```
┌──────────────────────────────────────────────────────────────┐
│                      Hei-DataHub                             │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            │ HTTPS (TLS 1.2+)
                            │ Port 443
                            │
                    ┌───────▼────────┐
                    │ WebDAV Methods │
                    ├────────────────┤
                    │ PROPFIND       │ - List files + metadata
                    │ GET            │ - Download file
                    │ PUT            │ - Upload file
                    │ DELETE         │ - Remove file
                    │ MKCOL          │ - Create directory
                    └───────┬────────┘
                            │
                            │
                    ┌───────▼────────────────────────┐
                    │   HeiBox/Seafile WebDAV        │
                    │                                │
                    │   /library-id/datasets/        │
                    │   ├─ dataset-1/                │
                    │   │   └─ metadata.yaml         │
                    │   └─ dataset-2/                │
                    │       └─ metadata.yaml         │
                    └────────────────────────────────┘
```

**Request flow:**

```python
# List files
PROPFIND /library-id/datasets/
Authorization: Bearer token123
Depth: 1

# Download file
GET /library-id/datasets/climate-data/metadata.yaml
Authorization: Bearer token123

# Upload file
PUT /library-id/datasets/climate-data/metadata.yaml
Authorization: Bearer token123
Content-Type: text/yaml

id: climate-data
dataset_name: Climate Model Data
...
```

---

## Threading Model

```
┌─────────────────────────────────────────────────────────────┐
│                       Main Thread                           │
│                                                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │           Textual UI (Event Loop)                │       │
│  │   ├─ Handle user input                           │       │
│  │   ├─ Render views                                │       │
│  │   └─ Update widgets                              │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Async communication
                       │ (queues, signals)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Background Thread                          │
│                                                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Sync Manager (Timer Loop)                │       │
│  │   ├─ Check for updates (every 5 min)            │       │
│  │   ├─ Download remote changes                    │       │
│  │   └─ Upload local changes                       │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Communication:
- Main → Background: Signal to sync now
- Background → Main: Notify sync complete
- Shared state: Protected by locks
```

---

## Related Documentation

- **[Architecture Overview](overview.md)** - High-level architecture
- **[Data Flow](data-flow.md)** - Detailed data flow explanations
- **[Design Principles](design-principles.md)** - Guiding principles

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
