"""
Fast search index service using SQLite FTS5.
Provides local, indexed search for cloud datasets with <20ms queries.

Cloud-only implementation - all indexed items are from WebDAV storage.
"""
import logging
import os
import sqlite3
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

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
        self._query_cache: dict[tuple[str, Optional[str]], list[dict[str, Any]]] = {}
        self._cache_timeout = 60  # seconds
        self._cache_timestamps: dict[tuple[str, Optional[str]], float] = {}
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
                    category TEXT,
                    spatial_coverage TEXT,
                    temporal_coverage TEXT,
                    access_method TEXT,
                    storage_location TEXT,
                    reference TEXT,
                    spatial_resolution TEXT,
                    temporal_resolution TEXT,
                    created_at INTEGER,
                    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            """)

            # Add new columns if they don't exist (migration for existing databases)
            try:
                conn.execute("ALTER TABLE items ADD COLUMN category TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN spatial_coverage TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN temporal_coverage TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN access_method TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN storage_location TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN reference TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN spatial_resolution TEXT")
            except Exception:
                pass  # Column already exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN temporal_resolution TEXT")
            except Exception:
                pass  # Column already exists

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

    @staticmethod
    def _normalise_filter(value) -> Optional[list[str]]:
        """Accept str, list[str], or None and return list[str] or None."""
        if value is None:
            return None
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and value:
            return value
        return None

    def search(
        self,
        query_text: str,
        project_filter=None,
        source_filter=None,
        format_filter=None,
        category_filter=None,
        method_filter=None,
        size_filter=None,
        sr_filter=None,
        sc_filter=None,
        tr_filter=None,
        tc_filter=None,
        limit: int = INDEX_MAX_RESULTS,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Fast local search using FTS5 index.

        Each filter accepts a single string or a list of strings.
        Multiple values for the same field are AND-ed (all must match).

        Args:
            query_text: Free text query (will be tokenized for FTS)
            project_filter: Optional project filter (str or list[str])
            source_filter: Optional source filter (str or list[str])
            format_filter: Optional format filter (str or list[str])
            category_filter: Optional category filter (str or list[str])
            method_filter: Optional access method filter (str or list[str])
            size_filter: Optional size filter (str or list[str])
            sr_filter: Optional spatial resolution filter (str or list[str])
            sc_filter: Optional spatial coverage filter (str or list[str])
            tr_filter: Optional temporal resolution filter (str or list[str])
            tc_filter: Optional temporal coverage filter (str or list[str])
            limit: Maximum results to return
            offset: Offset for pagination

        Returns:
            List of matching items with metadata
        """
        # Normalise all filters to list[str] | None
        project_filter = self._normalise_filter(project_filter)
        source_filter = self._normalise_filter(source_filter)
        format_filter = self._normalise_filter(format_filter)
        category_filter = self._normalise_filter(category_filter)
        method_filter = self._normalise_filter(method_filter)
        size_filter = self._normalise_filter(size_filter)
        sr_filter = self._normalise_filter(sr_filter)
        sc_filter = self._normalise_filter(sc_filter)
        tr_filter = self._normalise_filter(tr_filter)
        tc_filter = self._normalise_filter(tc_filter)

        # Check cache first — freeze lists so they're hashable
        def _freeze(v):
            return tuple(v) if v else None
        cache_key = (query_text,
                     _freeze(project_filter), _freeze(source_filter),
                     _freeze(format_filter), _freeze(category_filter),
                     _freeze(method_filter), _freeze(size_filter),
                     _freeze(sr_filter), _freeze(sc_filter),
                     _freeze(tr_filter), _freeze(tc_filter))
        if cache_key in self._query_cache:
            timestamp = self._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self._cache_timeout:
                cached = self._query_cache[cache_key]
                return cached[offset:offset + limit]

        conn = self.get_connection()
        try:
            params: list[Any] = []

            # Build FTS query from free-text, sanitising special chars
            fts_query = None
            if query_text and query_text.strip():
                # Tokenize and add prefix matching, but escape special characters
                tokens = query_text.strip().split()
                # Only add * for tokens >= 2 chars and alphanumeric
                fts_tokens = []
                for token in tokens:
                    if len(token) >= 2:
                        # Strip ALL FTS5-breaking special chars: : / | , " * ( ) - +
                        cleaned = ''.join(
                            c for c in token
                            if c.isalnum() or c in ('_', '.')
                        )
                        if not cleaned or len(cleaned) < 2:
                            continue
                        # Pure alphanumeric tokens get prefix wildcard
                        if cleaned.isalnum():
                            fts_tokens.append(f"{cleaned}*")
                        else:
                            # Tokens with dots/underscores — quote them
                            fts_tokens.append(f'"{cleaned}"')

                fts_query = " ".join(fts_tokens) if fts_tokens else None

            # Decide: use FTS+filters or filters-only
            if query_text and query_text.strip() and fts_query:
                # Build WHERE clauses for filters (applied to items table, not FTS)
                # Each filter is a list; every value adds its own AND clause
                where_clauses: list[str] = []

                _filter_map = [
                    (project_filter, "items.project LIKE ?", True),
                    (source_filter, "items.source LIKE ?", False),
                    (format_filter, "items.format LIKE ?", False),
                    (category_filter, "items.category LIKE ?", False),
                    (method_filter, "items.access_method LIKE ?", False),
                    (size_filter, "items.size LIKE ?", False),
                    (sr_filter, "items.spatial_resolution LIKE ?", False),
                    (sc_filter, "items.spatial_coverage LIKE ?", False),
                    (tr_filter, "items.temporal_resolution LIKE ?", False),
                    (tc_filter, "items.temporal_coverage LIKE ?", False),
                ]
                for values, clause, prefix_only in _filter_map:
                    if values:
                        for v in values:
                            where_clauses.append(clause)
                            params.append(f"{v}%" if prefix_only else f"%{v}%")

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
                        items.tags,
                        items.category,
                        items.spatial_coverage,
                        items.temporal_coverage,
                        items.access_method,
                        items.storage_location,
                        items.reference,
                        items.spatial_resolution,
                        items.temporal_resolution
                    FROM items
                    JOIN items_fts ON items.id = items_fts.rowid
                    WHERE items_fts MATCH ?
                """
                # FTS query is first param
                fts_params = [fts_query] + params

                # Add additional filters
                if where_clauses:
                    sql += " AND " + " AND ".join(where_clauses)

                sql += " ORDER BY items.mtime DESC LIMIT ? OFFSET ?"
                fts_params.extend([limit, offset])
                params = fts_params
            else:
                # No text query, just apply filters
                where_clauses: list[str] = []

                _filter_map = [
                    (project_filter, "items.project LIKE ?", True),
                    (source_filter, "items.source LIKE ?", False),
                    (format_filter, "items.format LIKE ?", False),
                    (category_filter, "items.category LIKE ?", False),
                    (method_filter, "items.access_method LIKE ?", False),
                    (size_filter, "items.size LIKE ?", False),
                    (sr_filter, "items.spatial_resolution LIKE ?", False),
                    (sc_filter, "items.spatial_coverage LIKE ?", False),
                    (tr_filter, "items.temporal_resolution LIKE ?", False),
                    (tc_filter, "items.temporal_coverage LIKE ?", False),
                ]
                for values, clause, prefix_only in _filter_map:
                    if values:
                        for v in values:
                            where_clauses.append(clause)
                            params.append(f"{v}%" if prefix_only else f"%{v}%")

                sql = """
                    SELECT
                        id, name, path, project, size, mtime, is_remote,
                        description, format, source, tags, category,
                        spatial_coverage, temporal_coverage,
                        access_method, storage_location, reference,
                        spatial_resolution, temporal_resolution
                    FROM items
                """

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

                sql += " ORDER BY mtime DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

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
                    "category": row["category"],
                    "spatial_coverage": row["spatial_coverage"],
                    "temporal_coverage": row["temporal_coverage"],
                    "access_method": row["access_method"],
                    "storage_location": row["storage_location"],
                    "reference": row["reference"],
                    "spatial_resolution": row["spatial_resolution"],
                    "temporal_resolution": row["temporal_resolution"],
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
        category: Optional[str] = None,
        spatial_coverage: Optional[str] = None,
        temporal_coverage: Optional[str] = None,
        access_method: Optional[str] = None,
        storage_location: Optional[str] = None,
        reference: Optional[str] = None,
        spatial_resolution: Optional[str] = None,
        temporal_resolution: Optional[str] = None,
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
            category: Dataset category
            spatial_coverage: Spatial coverage info
            temporal_coverage: Temporal coverage info
            access_method: How to access the data
            storage_location: Where data is stored
            reference: Reference/citation
            spatial_resolution: Spatial resolution
            temporal_resolution: Temporal resolution
        """
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO items (
                    path, name, project, tags, size, mtime, etag, is_remote,
                    description, format, source, category, spatial_coverage, temporal_coverage,
                    access_method, storage_location, reference, spatial_resolution, temporal_resolution
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    category = excluded.category,
                    spatial_coverage = excluded.spatial_coverage,
                    temporal_coverage = excluded.temporal_coverage,
                    access_method = excluded.access_method,
                    storage_location = excluded.storage_location,
                    reference = excluded.reference,
                    spatial_resolution = excluded.spatial_resolution,
                    temporal_resolution = excluded.temporal_resolution,
                    updated_at = strftime('%s', 'now')
            """, (path, name, project, tags, size, mtime, etag, int(is_remote),
                  description, format, source, category, spatial_coverage, temporal_coverage,
                  access_method, storage_location, reference, spatial_resolution, temporal_resolution))
            conn.commit()

            # Invalidate cache
            self._query_cache.clear()
            self._cache_timestamps.clear()
        finally:
            conn.close()

    def bulk_upsert(self, items: list[dict[str, Any]]) -> int:
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
                        description, format, source, category, spatial_coverage, temporal_coverage,
                        access_method, storage_location, reference, spatial_resolution, temporal_resolution
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        category = excluded.category,
                        spatial_coverage = excluded.spatial_coverage,
                        temporal_coverage = excluded.temporal_coverage,
                        access_method = excluded.access_method,
                        storage_location = excluded.storage_location,
                        reference = excluded.reference,
                        spatial_resolution = excluded.spatial_resolution,
                        temporal_resolution = excluded.temporal_resolution,
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
                    item.get("category"),
                    item.get("spatial_coverage"),
                    item.get("temporal_coverage"),
                    item.get("access_method"),
                    item.get("storage_location"),
                    item.get("reference"),
                    item.get("spatial_resolution"),
                    item.get("temporal_resolution"),
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
    def get_project_suggestions(self, prefix: str = "") -> list[str]:
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
