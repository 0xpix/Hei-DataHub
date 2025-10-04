"""
Indexing module: SQLite FTS5 operations for fast search.
"""
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mini_datahub.storage import list_datasets, read_dataset
from mini_datahub.utils import DB_PATH, SQL_SCHEMA_PATH


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Initialize the database schema if it doesn't exist."""
    conn = get_connection()

    # Read schema SQL
    with open(SQL_SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    # Execute schema creation
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def ensure_database() -> None:
    """Ensure database exists and has the correct schema."""
    if not DB_PATH.exists():
        init_database()
    else:
        # Verify tables exist
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='datasets_store'"
        )
        if not cursor.fetchone():
            init_database()
        conn.close()


def upsert_dataset(dataset_id: str, metadata: dict) -> None:
    """
    Upsert a dataset into both the store and FTS index.

    Args:
        dataset_id: Dataset ID
        metadata: Full metadata dictionary
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Store the complete JSON payload
        payload = json.dumps(metadata)
        cursor.execute(
            """
            INSERT INTO datasets_store (id, payload, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = datetime('now')
            """,
            (dataset_id, payload),
        )

        # Remove old FTS entry if exists
        cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))

        # Insert into FTS index
        # Flatten list fields to space-separated strings for FTS
        name = metadata.get("dataset_name", "")
        description = metadata.get("description", "")
        used_in_projects = " ".join(metadata.get("used_in_projects", []))
        data_types = " ".join(metadata.get("data_types", []))
        source = metadata.get("source", "")
        file_format = metadata.get("file_format", "")

        cursor.execute(
            """
            INSERT INTO datasets_fts (id, name, description, used_in_projects, data_types, source, file_format)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (dataset_id, name, description, used_in_projects, data_types, source, file_format),
        )

        conn.commit()
    finally:
        conn.close()


def search_datasets(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search datasets using FTS5 with BM25 ranking and prefix support.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of search results with metadata
    """
    if not query.strip():
        return []

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Build FTS5 query with prefix wildcards for incremental search
        # Split query into tokens and add * for prefix matching
        tokens = query.strip().split()
        if not tokens:
            return []

        # Add prefix wildcard to each token (for incremental search)
        fts_query = " ".join(f"{token}*" for token in tokens if len(token) >= 2)

        if not fts_query:
            return []

        # Use FTS5 MATCH with BM25 ranking
        # snippet() provides highlighted excerpts
        cursor.execute(
            """
            SELECT
                datasets_fts.id,
                datasets_fts.name,
                snippet(datasets_fts, 2, '<b>', '</b>', '...', 40) as snippet,
                bm25(datasets_fts) as rank,
                datasets_store.payload
            FROM datasets_fts
            JOIN datasets_store ON datasets_fts.id = datasets_store.id
            WHERE datasets_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, limit),
        )

        results = []
        for row in cursor.fetchall():
            result = {
                "id": row["id"],
                "name": row["name"],
                "snippet": row["snippet"],
                "rank": row["rank"],
                "metadata": json.loads(row["payload"]),
            }
            results.append(result)

        return results
    except Exception as e:
        # If FTS query fails (e.g., syntax error), return empty results
        return []
    finally:
        conn.close()


def list_all_datasets(limit: int = 100) -> List[Dict[str, Any]]:
    """
    List all datasets ordered by most recently updated.

    Args:
        limit: Maximum number of results

    Returns:
        List of dataset info dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, payload, updated_at
            FROM datasets_store
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        results = []
        for row in cursor.fetchall():
            metadata = json.loads(row["payload"])
            # Create a snippet from description
            description = metadata.get("description", "")
            snippet = description[:100] + "..." if len(description) > 100 else description

            result = {
                "id": row["id"],
                "name": metadata.get("dataset_name", ""),
                "snippet": snippet,
                "rank": 0,  # No ranking for list view
                "metadata": metadata,
            }
            results.append(result)

        return results
    finally:
        conn.close()


def get_dataset_by_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a dataset by ID from the store.

    Args:
        dataset_id: Dataset ID

    Returns:
        Metadata dictionary or None
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT payload FROM datasets_store WHERE id = ?", (dataset_id,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["payload"])
        return None
    finally:
        conn.close()


def reindex_all() -> Tuple[int, List[str]]:
    """
    Reindex all datasets from the data directory.

    Returns:
        Tuple of (count, errors) - number of datasets indexed and list of error messages
    """
    ensure_database()

    # Clear existing indexes
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_store")
    cursor.execute("DELETE FROM datasets_fts")
    conn.commit()
    conn.close()

    # Reindex all datasets
    dataset_ids = list_datasets()
    count = 0
    errors = []

    for dataset_id in dataset_ids:
        try:
            metadata = read_dataset(dataset_id)
            if metadata:
                upsert_dataset(dataset_id, metadata)
                count += 1
        except Exception as e:
            errors.append(f"Failed to index {dataset_id}: {str(e)}")

    return count, errors


def delete_dataset(dataset_id: str) -> None:
    """
    Delete a dataset from the database (not from disk).

    Args:
        dataset_id: Dataset ID
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM datasets_store WHERE id = ?", (dataset_id,))
        cursor.execute("DELETE FROM datasets_fts WHERE id = ?", (dataset_id,))
        conn.commit()
    finally:
        conn.close()


def get_vocabulary(field: str) -> List[str]:
    """
    Get unique values for a field across all datasets.
    Used for autocomplete suggestions.

    Args:
        field: Field name (e.g., 'projects', 'data_types', 'file_format')

    Returns:
        List of unique values
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query the JSON field
        if field == 'projects':
            cursor.execute(
                """
                SELECT DISTINCT json_extract(data, '$.used_in_projects')
                FROM datasets_store
                WHERE json_extract(data, '$.used_in_projects') IS NOT NULL
                """
            )
        elif field == 'data_types':
            cursor.execute(
                """
                SELECT DISTINCT json_extract(data, '$.data_types')
                FROM datasets_store
                WHERE json_extract(data, '$.data_types') IS NOT NULL
                """
            )
        elif field == 'file_format':
            cursor.execute(
                """
                SELECT DISTINCT json_extract(data, '$.file_format')
                FROM datasets_store
                WHERE json_extract(data, '$.file_format') IS NOT NULL
                """
            )
        else:
            return []

        results = set()
        for row in cursor.fetchall():
            value = row[0]
            if not value:
                continue

            # Parse JSON arrays
            import json
            try:
                if isinstance(value, str) and value.startswith('['):
                    items = json.loads(value)
                    if isinstance(items, list):
                        results.update(str(item) for item in items if item)
                    else:
                        results.add(str(value))
                else:
                    results.add(str(value))
            except Exception:
                results.add(str(value))

        return sorted(results)
    finally:
        conn.close()
