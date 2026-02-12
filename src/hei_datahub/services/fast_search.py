"""
Unified fast search using the local index.
This module provides the main search interface that never hits the network.
"""
import logging
from typing import Any

from hei_datahub.core.queries import QueryParser
from hei_datahub.services.index_service import get_index_service

logger = logging.getLogger(__name__)


def _search_all(limit: int = 200) -> list[dict[str, Any]]:
    """
    Return all indexed items (used by all:* tag).

    Args:
        limit: Maximum number of results

    Returns:
        List of all items formatted for display
    """
    index_service = get_index_service()
    results = index_service.search(query_text="", limit=limit)

    formatted_results = []
    for item in results:
        formatted_results.append({
            "id": item["path"],
            "name": item["name"],
            "snippet": (item.get("description") or "")[:80],
            "metadata": {
                "dataset_name": item["name"],
                "description": item.get("description"),
                "project": item.get("project"),
                "tags": item.get("tags", "").split() if item.get("tags") else [],
                "format": item.get("format"),
                "file_format": item.get("format"),
                "source": item.get("source"),
                "size": item.get("size"),
                "category": item.get("category"),
                "spatial_coverage": item.get("spatial_coverage"),
                "temporal_coverage": item.get("temporal_coverage"),
                "spatial_resolution": item.get("spatial_resolution"),
                "temporal_resolution": item.get("temporal_resolution"),
                "access_method": item.get("access_method"),
                "is_remote": item.get("is_remote", False),
            },
        })

    return formatted_results


def search_indexed(query: str, limit: int = 50) -> list[dict[str, Any]]:
    """
    Fast search using the local index (never hits network).

    Supports:
    - Free text search
    - project: filter
    - source: filter
    - format: filter
    - tag: filter
    - Combined filters

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of search results
    """
    if not query or not query.strip():
        return []

    # Special keyword: plain 'all' returns every dataset
    if query.strip().lower() == "all":
        return _search_all(limit)

    # Parse query — collect ALL values per field so multiple tags
    # for the same field act as AND filters (narrowing results)
    project_filters: list[str] = []
    source_filters: list[str] = []
    format_filters: list[str] = []
    category_filters: list[str] = []
    method_filters: list[str] = []
    size_filters: list[str] = []
    sr_filters: list[str] = []
    sc_filters: list[str] = []
    tr_filters: list[str] = []
    tc_filters: list[str] = []
    query_text = query

    try:
        parser = QueryParser()
        parsed = parser.parse(query)

        # Collect all field filter values (multiple values = AND)
        for term in parsed.terms:
            if not term.is_free_text:
                if term.field == "project":
                    project_filters.append(term.value)
                elif term.field == "source":
                    source_filters.append(term.value)
                elif term.field == "format":
                    format_filters.append(term.value)
                elif term.field == "category":
                    category_filters.append(term.value)
                elif term.field == "method":
                    method_filters.append(term.value)
                elif term.field == "size":
                    size_filters.append(term.value)
                elif term.field == "sr":
                    sr_filters.append(term.value)
                elif term.field == "sc":
                    sc_filters.append(term.value)
                elif term.field == "tr":
                    tr_filters.append(term.value)
                elif term.field == "tc":
                    tc_filters.append(term.value)

        # Get free text part
        query_text = parsed.free_text_query or ""

    except Exception as e:
        logger.debug(f"Query parse error (using simple search): {e}")
        # Fall back to simple text search
        project_filters = []
        source_filters = []
        format_filters = []
        category_filters = []
        method_filters = []
        size_filters = []
        sr_filters = []
        sc_filters = []
        tr_filters = []
        tc_filters = []

    # Search the index
    index_service = get_index_service()
    results = index_service.search(
        query_text=query_text,
        project_filter=project_filters or None,
        source_filter=source_filters or None,
        format_filter=format_filters or None,
        category_filter=category_filters or None,
        method_filter=method_filters or None,
        size_filter=size_filters or None,
        sr_filter=sr_filters or None,
        sc_filter=sc_filters or None,
        tr_filter=tr_filters or None,
        tc_filter=tc_filters or None,
        limit=limit
    )

    # Fallback: if structured filters returned nothing, try using filter
    # values as free-text search (catches cases where metadata columns
    # are empty but the value appears in name/description/tags)
    if not results and not query_text:
        all_filter_values = (
            project_filters + source_filters + format_filters +
            category_filters + method_filters + size_filters +
            sr_filters + sc_filters + tr_filters + tc_filters
        )
        if all_filter_values:
            fallback_text = " ".join(all_filter_values)
            logger.debug(f"Structured search empty, FTS fallback: '{fallback_text}'")
            results = index_service.search(
                query_text=fallback_text,
                limit=limit,
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
                "file_format": item.get("format"),
                "source": item.get("source"),
                "size": item.get("size"),
                "category": item.get("category"),
                "spatial_coverage": item.get("spatial_coverage"),
                "temporal_coverage": item.get("temporal_coverage"),
                "is_remote": item.get("is_remote", False),
            },
        })

    return formatted_results


def get_all_indexed(limit: int = 200) -> list[dict[str, Any]]:
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
                "file_format": item.get("format"),
                "source": item.get("source"),
                "size": item.get("size"),
                "category": item.get("category"),
                "spatial_coverage": item.get("spatial_coverage"),
                "temporal_coverage": item.get("temporal_coverage"),
                "is_remote": item.get("is_remote", False),
            },
        })

    return formatted_results
