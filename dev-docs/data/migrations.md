# Database Migrations

## Introduction

Database migrations allow Hei-DataHub to evolve its schema over time while preserving user data. This document covers the migration system, how to create new migrations, and how to handle version upgrades.

---

## Migration System

### Overview

```
┌────────────────────────┐
│  Application Startup   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Check schema version   │
│ (schema_version table) │
└───────────┬────────────┘
            │
            ▼
       ┌────────┐
       │ Current│  No
       │version?├────────┐
       └────┬───┘        │
            │ Yes        │
            ▼            ▼
    ┌───────────┐  ┌─────────────┐
    │  All good │  │Apply pending│
    └───────────┘  │ migrations  │
                   └─────────────┘
```

---

### Version Tracking

**Schema Version Table:**

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);
```

**Example Data:**

```sql
SELECT * FROM schema_version ORDER BY version;
```

| version | applied_at |
|---------|------------|
| 1 | 2024-01-15 10:00:00 |
| 2 | 2024-02-20 14:30:00 |
| 3 | 2024-03-10 09:15:00 |

---

## Migration Files

### File Structure

**Location:** `src/mini_datahub/infra/migrations/`

**Naming Convention:** `{version:03d}_{description}.sql`

**Examples:**
```
migrations/
├── 001_initial_schema.sql
├── 002_add_fts_index.sql
├── 003_add_etag_field.sql
├── 004_add_remote_flag.sql
└── 005_add_project_index.sql
```

---

### Migration File Template

```sql
-- migrations/XXX_description.sql

-- ============================================
-- Migration: XXX - Description
-- Date: YYYY-MM-DD
-- Purpose: Brief explanation of changes
-- ============================================

-- Your SQL changes here
ALTER TABLE fast_search_index ADD COLUMN new_field TEXT;
CREATE INDEX idx_new_field ON fast_search_index(new_field);

-- Record migration
INSERT INTO schema_version (version) VALUES (XXX);
```

---

## Example Migrations

### Migration 001: Initial Schema

```sql
-- migrations/001_initial_schema.sql

-- ============================================
-- Migration: 001 - Initial Schema
-- Date: 2024-01-15
-- Purpose: Create initial database schema
-- ============================================

-- Create schema version table
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);

-- Create main dataset store
CREATE TABLE datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Create FTS5 search index
CREATE VIRTUAL TABLE datasets_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    tokenize = 'porter ascii'
);

-- Create fast search index
CREATE TABLE fast_search_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    project TEXT,
    tags TEXT,
    description TEXT,
    format TEXT
);

-- Indexes for fast search
CREATE INDEX idx_name ON fast_search_index(name);
CREATE INDEX idx_project ON fast_search_index(project);
CREATE INDEX idx_tags ON fast_search_index(tags);

-- Record migration
INSERT INTO schema_version (version) VALUES (1);
```

---

### Migration 002: Add FTS Index Optimization

```sql
-- migrations/002_optimize_fts.sql

-- ============================================
-- Migration: 002 - Optimize FTS Index
-- Date: 2024-02-20
-- Purpose: Add keywords column to FTS index
-- ============================================

-- Recreate FTS table with keywords column
DROP TABLE IF EXISTS datasets_fts_old;
ALTER TABLE datasets_fts RENAME TO datasets_fts_old;

CREATE VIRTUAL TABLE datasets_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    keywords,  -- NEW COLUMN
    tokenize = 'porter ascii'
);

-- Migrate data
INSERT INTO datasets_fts (id, name, description, used_in_projects, data_types, source, file_format)
SELECT id, name, description, used_in_projects, data_types, source, file_format
FROM datasets_fts_old;

-- Drop old table
DROP TABLE datasets_fts_old;

-- Record migration
INSERT INTO schema_version (version) VALUES (2);
```

---

### Migration 003: Add ETag and Remote Flag

```sql
-- migrations/003_add_etag_field.sql

-- ============================================
-- Migration: 003 - Add ETag and Remote Flag
-- Date: 2024-03-10
-- Purpose: Support WebDAV caching and remote-only datasets
-- ============================================

-- Add ETag column for WebDAV caching
ALTER TABLE fast_search_index ADD COLUMN etag TEXT;

-- Add remote flag (0 = local, 1 = cloud-only)
ALTER TABLE fast_search_index ADD COLUMN is_remote INTEGER DEFAULT 0;

-- Create index for remote filtering
CREATE INDEX idx_remote ON fast_search_index(is_remote);

-- Record migration
INSERT INTO schema_version (version) VALUES (3);
```

---

### Migration 004: Add Updated Timestamp

```sql
-- migrations/004_add_updated_timestamp.sql

-- ============================================
-- Migration: 004 - Add Updated Timestamp
-- Date: 2024-04-05
-- Purpose: Track last update time for datasets
-- ============================================

-- Add updated_at to fast_search_index (if not exists)
ALTER TABLE fast_search_index ADD COLUMN updated_at TEXT;

-- Set default for existing rows
UPDATE fast_search_index
SET updated_at = datetime('now')
WHERE updated_at IS NULL;

-- Record migration
INSERT INTO schema_version (version) VALUES (4);
```

---

## Migration Runner

### Implementation

**Location:** `src/mini_datahub/infra/db.py`

```python
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

def get_current_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version from database"""
    cursor = conn.cursor()

    # Check if schema_version table exists
    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='schema_version'
        """
    )

    if not cursor.fetchone():
        return 0  # No migrations applied yet

    # Get max version
    cursor.execute("SELECT MAX(version) FROM schema_version")
    result = cursor.fetchone()
    return result[0] if result[0] is not None else 0

def run_migrations(conn: sqlite3.Connection) -> int:
    """Apply all pending migrations"""
    current_version = get_current_schema_version(conn)
    logger.info(f"Current schema version: {current_version}")

    # Get all migration files
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        logger.warning("No migration files found")
        return current_version

    applied_count = 0

    for migration_file in migration_files:
        # Extract version from filename (e.g., "003_add_etag.sql" → 3)
        version_str = migration_file.stem.split("_")[0]
        try:
            version = int(version_str)
        except ValueError:
            logger.warning(f"Invalid migration filename: {migration_file.name}")
            continue

        # Skip if already applied
        if version <= current_version:
            continue

        # Apply migration
        logger.info(f"Applying migration {version}: {migration_file.name}")

        try:
            with open(migration_file, "r") as f:
                sql = f.read()

            # Execute migration SQL
            conn.executescript(sql)
            conn.commit()

            logger.info(f"Migration {version} applied successfully")
            applied_count += 1

        except sqlite3.Error as e:
            logger.error(f"Migration {version} failed: {e}")
            conn.rollback()
            raise

    if applied_count > 0:
        final_version = get_current_schema_version(conn)
        logger.info(f"Applied {applied_count} migrations. New version: {final_version}")
    else:
        logger.info("No pending migrations")

    return get_current_schema_version(conn)

def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize database and run migrations"""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Run migrations
    run_migrations(conn)

    return conn
```

---

### Application Startup

```python
# In src/mini_datahub/__main__.py or app initialization

from mini_datahub.infra.db import init_database
from mini_datahub.infra.paths import get_data_dir

def main():
    # Initialize database (runs migrations automatically)
    db_path = get_data_dir() / "datasets.db"
    conn = init_database(db_path)

    # Application logic...
```

---

## Creating New Migrations

### Step-by-Step Guide

#### 1. Determine Next Version

```bash
ls src/mini_datahub/infra/migrations/
# Output: 001_initial.sql, 002_optimize.sql, 003_add_etag.sql
# Next version: 004
```

#### 2. Create Migration File

```bash
touch src/mini_datahub/infra/migrations/004_add_new_field.sql
```

#### 3. Write Migration SQL

```sql
-- migrations/004_add_new_field.sql

-- ============================================
-- Migration: 004 - Add New Field
-- Date: 2024-05-01
-- Purpose: Add 'last_accessed' field for usage tracking
-- ============================================

-- Add new column
ALTER TABLE fast_search_index ADD COLUMN last_accessed TEXT;

-- Set default for existing rows
UPDATE fast_search_index
SET last_accessed = datetime('now')
WHERE last_accessed IS NULL;

-- Create index
CREATE INDEX idx_last_accessed ON fast_search_index(last_accessed);

-- Record migration
INSERT INTO schema_version (version) VALUES (4);
```

#### 4. Test Migration

```python
# test_migration.py
import sqlite3
from pathlib import Path
from mini_datahub.infra.db import run_migrations

# Test on empty database
test_db = Path("/tmp/test_migration.db")
test_db.unlink(missing_ok=True)

conn = sqlite3.connect(str(test_db))
run_migrations(conn)

# Verify version
cursor = conn.cursor()
cursor.execute("SELECT MAX(version) FROM schema_version")
print(f"Final version: {cursor.fetchone()[0]}")

# Verify schema
cursor.execute("PRAGMA table_info(fast_search_index)")
print("Columns:", [row[1] for row in cursor.fetchall()])

conn.close()
```

#### 5. Test on Production Database (Backup First!)

```bash
# Backup production database
cp ~/.local/share/mini-datahub/datasets.db ~/backup-$(date +%Y%m%d).db

# Run application (migrations run automatically)
mini-datahub

# Verify
sqlite3 ~/.local/share/mini-datahub/datasets.db \
  "SELECT version, applied_at FROM schema_version ORDER BY version;"
```

---

## Migration Best Practices

### 1. Always Backup Before Migration

```bash
# Automated backup in migration runner
def run_migrations(conn: sqlite3.Connection) -> int:
    current_version = get_current_schema_version(conn)

    # Create backup before any migrations
    if current_version > 0:
        db_path = Path(conn.execute("PRAGMA database_list").fetchone()[2])
        backup_path = db_path.with_suffix(f".backup-v{current_version}")

        import shutil
        shutil.copy2(db_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

    # Apply migrations...
```

---

### 2. Make Migrations Idempotent

```sql
-- ✅ GOOD: Safe to run multiple times
ALTER TABLE fast_search_index ADD COLUMN IF NOT EXISTS new_field TEXT;

-- ❌ BAD: Fails if already exists
ALTER TABLE fast_search_index ADD COLUMN new_field TEXT;
```

---

### 3. Use Transactions

```sql
-- Wrap all changes in BEGIN/COMMIT
BEGIN TRANSACTION;

ALTER TABLE fast_search_index ADD COLUMN new_field TEXT;
CREATE INDEX idx_new_field ON fast_search_index(new_field);

INSERT INTO schema_version (version) VALUES (5);

COMMIT;
```

---

### 4. Test Migrations on Empty and Populated Databases

```python
# Test 1: Empty database
test_empty_db()

# Test 2: Database with 1,000 datasets
test_populated_db(dataset_count=1000)

# Test 3: Large database (10,000 datasets)
test_large_db(dataset_count=10000)
```

---

### 5. Document Breaking Changes

```sql
-- ============================================
-- Migration: 005 - Rename Column (BREAKING)
-- Date: 2024-06-01
-- Purpose: Rename 'project' to 'primary_project'
--
-- BREAKING CHANGE:
-- - Old queries using 'project' will fail
-- - Update all code referencing this column
-- ============================================

ALTER TABLE fast_search_index RENAME COLUMN project TO primary_project;

INSERT INTO schema_version (version) VALUES (5);
```

---

## Rollback Strategies

### Manual Rollback

```bash
# 1. Stop application
systemctl --user stop hei-datahub

# 2. Restore backup
cp ~/backup-20240501.db ~/.local/share/mini-datahub/datasets.db

# 3. Restart application
systemctl --user start hei-datahub
```

---

### Migration Rollback (Advanced)

**Down Migrations (Not Implemented):**

```sql
-- migrations/down/004_rollback_new_field.sql

-- Remove column added in migration 004
ALTER TABLE fast_search_index DROP COLUMN last_accessed;

-- Remove index
DROP INDEX IF EXISTS idx_last_accessed;

-- Decrement version
DELETE FROM schema_version WHERE version = 4;
```

**Rollback Runner:**

```python
def rollback_migration(conn: sqlite3.Connection, target_version: int) -> None:
    """Rollback to target version"""
    current_version = get_current_schema_version(conn)

    if target_version >= current_version:
        logger.warning("Target version is not lower than current")
        return

    # Apply down migrations in reverse order
    for version in range(current_version, target_version, -1):
        down_file = MIGRATIONS_DIR / "down" / f"{version:03d}_rollback.sql"

        if not down_file.exists():
            raise ValueError(f"No rollback migration for version {version}")

        logger.info(f"Rolling back migration {version}")

        with open(down_file, "r") as f:
            sql = f.read()

        conn.executescript(sql)
        conn.commit()
```

---

## Data Migrations

### Migrating Data Structure

```sql
-- migrations/006_normalize_projects.sql

-- ============================================
-- Migration: 006 - Normalize Projects
-- Date: 2024-07-01
-- Purpose: Extract projects into separate table
-- ============================================

-- Create projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Create dataset-project relationship table
CREATE TABLE dataset_projects (
    dataset_id TEXT NOT NULL,
    project_id INTEGER NOT NULL,
    PRIMARY KEY (dataset_id, project_id),
    FOREIGN KEY (dataset_id) REFERENCES datasets_store(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Migrate existing data
INSERT OR IGNORE INTO projects (name)
SELECT DISTINCT project
FROM fast_search_index
WHERE project IS NOT NULL;

INSERT INTO dataset_projects (dataset_id, project_id)
SELECT
    fsi.path,
    p.id
FROM fast_search_index fsi
JOIN projects p ON p.name = fsi.project
WHERE fsi.project IS NOT NULL;

-- Drop old column (optional)
-- ALTER TABLE fast_search_index DROP COLUMN project;

-- Record migration
INSERT INTO schema_version (version) VALUES (6);
```

---

## Version Compatibility

### Checking Version Compatibility

```python
MINIMUM_SUPPORTED_VERSION = 3
CURRENT_VERSION = 6

def check_version_compatibility(conn: sqlite3.Connection) -> None:
    """Check if database version is compatible"""
    current = get_current_schema_version(conn)

    if current < MINIMUM_SUPPORTED_VERSION:
        raise ValueError(
            f"Database version {current} is too old. "
            f"Minimum supported version is {MINIMUM_SUPPORTED_VERSION}. "
            f"Please upgrade your database."
        )

    if current > CURRENT_VERSION:
        raise ValueError(
            f"Database version {current} is newer than application version {CURRENT_VERSION}. "
            f"Please upgrade the application."
        )
```

---

## Troubleshooting

### Migration Failed

**Symptom:** Migration fails partway through

**Solution:**

```bash
# 1. Restore from backup
cp ~/backup-20240501.db ~/.local/share/mini-datahub/datasets.db

# 2. Fix migration SQL

# 3. Test migration on copy
cp ~/.local/share/mini-datahub/datasets.db /tmp/test.db
sqlite3 /tmp/test.db < migrations/004_add_field.sql

# 4. Re-run application
mini-datahub
```

---

### Migration Applied but Schema Wrong

**Symptom:** Migration marked as applied but changes not present

**Diagnosis:**

```sql
-- Check schema_version
SELECT * FROM schema_version;

-- Check actual schema
PRAGMA table_info(fast_search_index);

-- Check indexes
SELECT name FROM sqlite_master WHERE type='index';
```

**Solution:**

```python
# Manually fix schema
cursor.execute("ALTER TABLE fast_search_index ADD COLUMN missing_field TEXT")

# Or rebuild from scratch
rebuild_database()
```

---

## Related Documentation

- **[Schema](schema.md)** - Database schema reference
- **[Storage](storage.md)** - Storage architecture
- **[Data Layer Overview](overview.md)** - High-level overview

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
