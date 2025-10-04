-- SQLite schema for Hei-DataHub
-- Store table: holds complete JSON payload for each dataset
CREATE TABLE IF NOT EXISTS datasets_store (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,  -- JSON representation of metadata
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- FTS5 virtual table for full-text search with prefix support
CREATE VIRTUAL TABLE IF NOT EXISTS datasets_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    used_in_projects,
    data_types,
    source,
    file_format,
    tokenize = 'porter unicode61',
    prefix = '2 3 4'
);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_datasets_store_timestamp
AFTER UPDATE ON datasets_store
FOR EACH ROW
BEGIN
    UPDATE datasets_store SET updated_at = datetime('now') WHERE id = OLD.id;
END;
