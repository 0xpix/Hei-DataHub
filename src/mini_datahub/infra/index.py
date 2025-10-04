"""
Index: FTS5 full-text search operations.
"""
import json
from typing import Any, Dict, List, Tuple

from mini_datahub.infra.db import get_connection, ensure_database


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


def delete_dataset(dataset_id: str) -> None:
    """
    Delete a dataset from both store and FTS index.

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


def get_dataset_from_store(dataset_id: str) -> Dict[str, Any]:
    """
    Get dataset payload from store.

    Args:
        dataset_id: Dataset ID

    Returns:
        Dataset metadata dictionary, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT payload FROM datasets_store WHERE id = ?",
            (dataset_id,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["payload"])
        return None
    finally:
        conn.close()


def list_all_datasets(limit: int = 100) -> List[Dict[str, Any]]:
    """
    List all datasets ordered by most recently updated.

    Args:
        limit: Maximum number of results

    Returns:
        List of dataset info dictionaries with id, name, snippet, rank, metadata
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


def reindex_all() -> Tuple[int, List[str]]:
    """
    Reindex all datasets from the data directory.

    Returns:
        Tuple of (count, errors) - number of datasets indexed and list of error messages
    """
    from mini_datahub.infra.store import list_datasets, read_dataset

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
