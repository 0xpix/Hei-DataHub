"""
Fast search index service using SQLite FTS5.
Provides local, indexed search for cloud datasets with <20ms queries.

Cloud-only implementation - all indexed items are from WebDAV storage.
"""
import asyncio
import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache

from hei_datahub.infra.paths import CACHE_DIR

logger = logging.getLogger(__name__)

# Configuration from environment
SEARCH_DEBOUNCE_MS = int(os.environ.get("HEI_DATAHUB_SEARCH_DEBOUNCE_MS", "200"))
INDEX_MAX_RESULTS = int(os.environ.get("HEI_DATAHUB_INDEX_MAX_RESULTS", "50"))
SYNC_INTERVAL_SEC = int(os.environ.get("HEI_DATAHUB_SYNC_INTERVAL_SEC", "900"))

# Index database path
INDEX_DB_PATH = CACHE_DIR / "index.db"


class IndexService:
    """Fast local search index with SQLite FTS5 for cloud datasets."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize index service."""
        self.db_path = db_path or INDEX_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._query_cache: Dict[Tuple[str, Optional[str]], List[Dict[str, Any]]] = {}
        self._cache_timeout = 60  # seconds
        self._cache_timestamps: Dict[Tuple[str, Optional[str]], float] = {}
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the index database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            # Create items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    project TEXT,
                    tags TEXT,
                    size INTEGER,
                    mtime INTEGER,
                    etag TEXT,
                    is_remote INTEGER NOT NULL DEFAULT 1,
                    description TEXT,
                    format TEXT,
                    source TEXT,
                    created_at INTEGER,
                    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Create FTS5 virtual table (content-full for trigger support)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
                    name,
                    path,
                    project,
                    tags,
                    description,
                    tokenize = 'porter ascii'
                )
            """)

            # Create triggers to keep FTS in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
                    INSERT INTO items_fts(rowid, name, path, project, tags, description)
                    VALUES (new.id, new.name, new.path, new.project, new.tags, new.description);
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
                    DELETE FROM items_fts WHERE rowid = old.id;
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
                    DELETE FROM items_fts WHERE rowid = old.id;
                    INSERT INTO items_fts(rowid, name, path, project, tags, description)
                    VALUES (new.id, new.name, new.path, new.project, new.tags, new.description);
                END
            """)

            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_project ON items(project)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_mtime ON items(mtime DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_is_remote ON items(is_remote)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_path ON items(path)")

            # Store index metadata
            conn.execute("""
                CREATE TABLE IF NOT EXISTS index_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            """)

            conn.commit()
            logger.info(f"Index database initialized at {self.db_path}")
        finally:
            conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get a connection to the index database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def search(
        self,
        query_text: str,
        project_filter: Optional[str] = None,
        limit: int = INDEX_MAX_RESULTS,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fast local search using FTS5 index.

        Args:
            query_text: Free text query (will be tokenized for FTS)
            project_filter: Optional project prefix filter
            limit: Maximum results to return
            offset: Offset for pagination

        Returns:
            List of matching items with metadata
        """
        # Check cache first
        cache_key = (query_text, project_filter)
        if cache_key in self._query_cache:
            timestamp = self._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self._cache_timeout:
                cached = self._query_cache[cache_key]
                return cached[offset:offset + limit]

        conn = self.get_connection()
        try:
            params: List[Any] = []

            # Build FTS query
            if query_text and query_text.strip():
                # Tokenize and add prefix matching
                tokens = query_text.strip().split()
                fts_query = " ".join(f"{token}*" for token in tokens if len(token) >= 2)

                if not fts_query:
                    fts_query = query_text  # Fallback to original

                if project_filter:
                    sql = """
                        SELECT
                            items.id,
                            items.name,
                            items.path,
                            items.project,
                            items.size,
                            items.mtime,
                            items.is_remote,
                            items.description,
                            items.format,
                            items.source,
                            items.tags
                        FROM items
                        JOIN items_fts ON items.id = items_fts.rowid
                        WHERE items_fts MATCH ?
                          AND items.project LIKE ? || '%'
                        ORDER BY items.mtime DESC
                        LIMIT ? OFFSET ?
                    """
                    params = [fts_query, project_filter, limit, offset]
                else:
                    sql = """
                        SELECT
                            items.id,
                            items.name,
                            items.path,
                            items.project,
                            items.size,
                            items.mtime,
                            items.is_remote,
                            items.description,
                            items.format,
                            items.source,
                            items.tags
                        FROM items
                        JOIN items_fts ON items.id = items_fts.rowid
                        WHERE items_fts MATCH ?
                        ORDER BY items.mtime DESC
                        LIMIT ? OFFSET ?
                    """
                    params = [fts_query, limit, offset]
            else:
                # No text query, just filter by project if provided
                if project_filter:
                    sql = """
                        SELECT
                            id, name, path, project, size, mtime, is_remote,
                            description, format, source, tags
                        FROM items
                        WHERE project LIKE ? || '%'
                        ORDER BY mtime DESC
                        LIMIT ? OFFSET ?
                    """
                    params = [project_filter, limit, offset]
                else:
                    sql = """
                        SELECT
                            id, name, path, project, size, mtime, is_remote,
                            description, format, source, tags
                        FROM items
                        ORDER BY mtime DESC
                        LIMIT ? OFFSET ?
                    """
                    params = [limit, offset]

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "name": row["name"],
                    "path": row["path"],
                    "project": row["project"],
                    "size": row["size"],
                    "mtime": row["mtime"],
                    "is_remote": bool(row["is_remote"]),
                    "description": row["description"],
                    "format": row["format"],
                    "source": row["source"],
                    "tags": row["tags"],
                })

            # Cache the full result set (before pagination)
            if not offset:  # Only cache first page queries
                self._query_cache[cache_key] = results
                self._cache_timestamps[cache_key] = time.time()

            return results

        finally:
            conn.close()

    def upsert_item(
        self,
        path: str,
        name: str,
        is_remote: bool = False,
        project: Optional[str] = None,
        tags: Optional[str] = None,
        size: Optional[int] = None,
        mtime: Optional[int] = None,
        etag: Optional[str] = None,
        description: Optional[str] = None,
        format: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        """
        Insert or update an item in the index.

        Args:
            path: Unique path identifier
            name: Display name
            is_remote: Whether this is from WebDAV
            project: Project label
            tags: Space-separated tags
            size: File size in bytes
            mtime: Modification time (unix timestamp)
            etag: ETag from WebDAV
            description: Item description
            format: File format
            source: Data source
        """
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO items (
                    path, name, project, tags, size, mtime, etag, is_remote,
                    description, format, source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    name = excluded.name,
                    project = excluded.project,
                    tags = excluded.tags,
                    size = excluded.size,
                    mtime = excluded.mtime,
                    etag = excluded.etag,
                    is_remote = excluded.is_remote,
                    description = excluded.description,
                    format = excluded.format,
                    source = excluded.source,
                    updated_at = strftime('%s', 'now')
            """, (path, name, project, tags, size, mtime, etag, int(is_remote),
                  description, format, source))
            conn.commit()

            # Invalidate cache
            self._query_cache.clear()
            self._cache_timestamps.clear()
        finally:
            conn.close()

    def bulk_upsert(self, items: List[Dict[str, Any]]) -> int:
        """
        Bulk insert/update items in a transaction.

        Args:
            items: List of item dictionaries with keys matching upsert_item parameters

        Returns:
            Number of items processed
        """
        if not items:
            return 0

        conn = self.get_connection()
        try:
            count = 0
            for item in items:
                conn.execute("""
                    INSERT INTO items (
                        path, name, project, tags, size, mtime, etag, is_remote,
                        description, format, source
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        name = excluded.name,
                        project = excluded.project,
                        tags = excluded.tags,
                        size = excluded.size,
                        mtime = excluded.mtime,
                        etag = excluded.etag,
                        is_remote = excluded.is_remote,
                        description = excluded.description,
                        format = excluded.format,
                        source = excluded.source,
                        updated_at = strftime('%s', 'now')
                """, (
                    item.get("path"),
                    item.get("name"),
                    item.get("project"),
                    item.get("tags"),
                    item.get("size"),
                    item.get("mtime"),
                    item.get("etag"),
                    int(item.get("is_remote", False)),
                    item.get("description"),
                    item.get("format"),
                    item.get("source"),
                ))
                count += 1

            conn.commit()
            logger.info(f"Bulk upserted {count} items to index")

            # Invalidate cache
            self._query_cache.clear()
            self._cache_timestamps.clear()

            return count
        finally:
            conn.close()

    def delete_item(self, path: str) -> None:
        """Delete an item from the index by path."""
        conn = self.get_connection()
        try:
            conn.execute("DELETE FROM items WHERE path = ?", (path,))
            conn.commit()

            # Invalidate cache
            self._query_cache.clear()
            self._cache_timestamps.clear()
        finally:
            conn.close()

    def clear_remote_items(self) -> None:
        """Clear all remote items from index (useful before re-syncing)."""
        conn = self.get_connection()
        try:
            conn.execute("DELETE FROM items WHERE is_remote = 1")
            conn.commit()
            logger.info("Cleared all remote items from index")

            # Invalidate cache
            self._query_cache.clear()
            self._cache_timestamps.clear()
        finally:
            conn.close()

    def get_item_count(self) -> int:
        """Get count of items in index (all are cloud datasets)."""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) as total FROM items")
            total = cursor.fetchone()["total"]
            return total
        finally:
            conn.close()

    def set_meta(self, key: str, value: str) -> None:
        """Set metadata key-value pair."""
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO index_meta (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = strftime('%s', 'now')
            """, (key, value))
            conn.commit()
        finally:
            conn.close()

    def get_meta(self, key: str) -> Optional[str]:
        """Get metadata value by key."""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT value FROM index_meta WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None
        finally:
            conn.close()

    @lru_cache(maxsize=100)
    def get_project_suggestions(self, prefix: str = "") -> List[str]:
        """Get project autocomplete suggestions."""
        conn = self.get_connection()
        try:
            if prefix:
                cursor = conn.execute("""
                    SELECT DISTINCT project
                    FROM items
                    WHERE project LIKE ? || '%' AND project IS NOT NULL
                    ORDER BY project
                    LIMIT 20
                """, (prefix,))
            else:
                cursor = conn.execute("""
                    SELECT DISTINCT project
                    FROM items
                    WHERE project IS NOT NULL
                    ORDER BY project
                    LIMIT 20
                """)

            return [row["project"] for row in cursor.fetchall()]
        finally:
            conn.close()


# Global instance (lazy-initialized)
_index_service: Optional[IndexService] = None


def get_index_service() -> IndexService:
    """Get or create the global index service instance."""
    global _index_service
    if _index_service is None:
        _index_service = IndexService()
    return _index_service
