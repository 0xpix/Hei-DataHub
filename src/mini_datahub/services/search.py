"""
Search: Query policy and search operations.
"""
from typing import Any, Dict, List

from mini_datahub.infra.db import get_connection


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
            import json
            payload = json.loads(row["payload"])
            results.append({
                "id": row["id"],
                "name": row["name"],
                "snippet": row["snippet"],
                "rank": row["rank"],
                "metadata": payload,
            })

        return results
    finally:
        conn.close()


def get_all_datasets(limit: int = 200) -> List[Dict[str, Any]]:
    """
    Get all datasets (no search filter).

    Args:
        limit: Maximum number of results

    Returns:
        List of all datasets with metadata
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, payload FROM datasets_store
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,)
        )

        results = []
        for row in cursor.fetchall():
            import json
            payload = json.loads(row["payload"])
            results.append({
                "id": row["id"],
                "name": payload.get("dataset_name", row["id"]),
                "metadata": payload,
            })

        return results
    finally:
        conn.close()
