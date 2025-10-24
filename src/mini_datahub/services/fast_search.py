"""
Unified fast search using the local index.
This module provides the main search interface that never hits the network.
"""
import logging
from typing import Any, Dict, List, Optional

from mini_datahub.services.index_service import get_index_service
from mini_datahub.core.queries import QueryParser

logger = logging.getLogger(__name__)


def search_indexed(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fast search using the local index (never hits network).

    Supports:
    - Free text search
    - project: filter
    - Combined filters

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of search results
    """
    if not query or not query.strip():
        return []

    # Parse query
    project_filter = None
    query_text = query

    try:
        parser = QueryParser()
        parsed = parser.parse(query)

        # Extract project filter if present
        for term in parsed.terms:
            if not term.is_free_text and term.field == "project":
                project_filter = term.value
                break

        # Get free text part
        query_text = parsed.free_text_query or ""

    except Exception as e:
        logger.debug(f"Query parse error (using simple search): {e}")
        # Fall back to simple text search
        project_filter = None

    # Search the index
    index_service = get_index_service()
    results = index_service.search(
        query_text=query_text,
        project_filter=project_filter,
        limit=limit
    )

    # Format results to match expected structure
    formatted_results = []
    for item in results:
        formatted_results.append({
            "id": item["path"],  # Use path as ID
            "name": item["name"],
            "snippet": (item.get("description") or "")[:80],
            "metadata": {
                "dataset_name": item["name"],
                "description": item.get("description"),
                "project": item.get("project"),
                "tags": item.get("tags", "").split() if item.get("tags") else [],
                "format": item.get("format"),
                "source": item.get("source"),
                "size": item.get("size"),
                "is_remote": item.get("is_remote", False),
            },
        })

    return formatted_results


def get_all_indexed(limit: int = 200) -> List[Dict[str, Any]]:
    """
    Get all indexed items.

    Args:
        limit: Maximum number of results

    Returns:
        List of all items
    """
    index_service = get_index_service()
    results = index_service.search(
        query_text="",
        project_filter=None,
        limit=limit
    )

    # Format results
    formatted_results = []
    for item in results:
        formatted_results.append({
            "id": item["path"],
            "name": item["name"],
            "metadata": {
                "dataset_name": item["name"],
                "description": item.get("description"),
                "project": item.get("project"),
                "tags": item.get("tags", "").split() if item.get("tags") else [],
                "format": item.get("format"),
                "source": item.get("source"),
                "size": item.get("size"),
                "is_remote": item.get("is_remote", False),
            },
        })

    return formatted_results
