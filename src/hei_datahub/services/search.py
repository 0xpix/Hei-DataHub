"""
Search: Query policy and search operations with structured query support.
"""
import json
import logging
from typing import Any

from hei_datahub.core.queries import ParsedQuery, QueryOperator, QueryParser
from hei_datahub.infra.db import get_connection

logger = logging.getLogger(__name__)


def search_datasets(query: str, limit: int = 50) -> list[dict[str, Any]]:
    """
    Search datasets using FTS5 with BM25 ranking and structured query support.

    Supports structured queries:
    - source:github
    - format:csv
    - date:>2025-01
    - tag:climate
    - "quoted terms"
    - project:gideon

    Args:
        query: Search query string (can include structured filters)
        limit: Maximum number of results

    Returns:
        List of search results with metadata
    """
    if not query.strip():
        return []

    # Parse the query
    parser = QueryParser()
    try:
        parsed = parser.parse(query)
    except Exception as e:
        logger.warning(f"Query parse error: {e}, falling back to simple search")
        # Fall back to simple FTS search
        return _simple_fts_search(query, limit)

    # If no structured filters, use simple FTS
    if not parsed.has_field_filters() and parsed.free_text_query:
        return _simple_fts_search(parsed.free_text_query, limit)

    # Execute structured search
    return _structured_search(parsed, limit)


def _simple_fts_search(query: str, limit: int) -> list[dict[str, Any]]:
    """
    Simple FTS5 search without structured filters.

    Args:
        query: Free text query
        limit: Maximum results

    Returns:
        List of search results
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Build FTS5 query with prefix wildcards for incremental search
        # Handle quoted phrases specially
        import re

        # Handle empty quotes - strip them out
        query = re.sub(r'""', '', query)

        # Extract quoted phrases
        quoted_phrases = re.findall(r'"([^"]+)"', query)
        # Remove quoted phrases from query
        query_no_quotes = re.sub(r'"[^"]+"', '', query)

        tokens = query_no_quotes.strip().split()

        # Add prefix wildcard to each token (for incremental search)
        # Skip tokens that are too short or look like field prefixes
        valid_tokens = []
        for token in tokens:
            # Skip very short tokens or field-like patterns
            if len(token) < 2 or token.endswith(':') or ':' in token:
                continue
            # Clean token of special chars that break FTS
            clean_token = ''.join(c for c in token if c.isalnum() or c in ('-', '_'))
            if clean_token:
                valid_tokens.append(f"{clean_token}*")

        # Add quoted phrases back - use NEAR for exact phrase matching in FTS5
        for phrase in quoted_phrases:
            # Skip empty phrases
            if not phrase.strip():
                continue
            # Use exact phrase matching with FTS5 syntax
            # Escape quotes in the phrase and use double quotes
            escaped_phrase = phrase.replace('"', '""')
            valid_tokens.append(f'"{escaped_phrase}"')

        if not valid_tokens:
            return []

        fts_query = " ".join(valid_tokens)

        # Use FTS5 MATCH with BM25 ranking
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
            payload = json.loads(row["payload"])
            results.append({
                "id": row["id"],
                "name": row["name"],
                "snippet": row["snippet"],
                "rank": row["rank"],
                "metadata": payload,
            })

        return results
    except Exception as e:
        logger.error(f"FTS search error: {e}")
        return []
    finally:
        conn.close()


def _structured_search(parsed: ParsedQuery, limit: int) -> list[dict[str, Any]]:
    """
    Execute a structured search with field filters.

    Args:
        parsed: Parsed query with structured terms
        limit: Maximum results

    Returns:
        List of filtered search results
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Build SQL query with filters
        where_clauses = []
        params = []

        # Start with FTS if there's free text
        if parsed.free_text_query:
            tokens = parsed.free_text_query.split()
            fts_query = " ".join(f"{token}*" for token in tokens if len(token) >= 2)
            if fts_query:
                where_clauses.append("datasets_fts MATCH ?")
                params.append(fts_query)

        # Add field filters using JSON extraction
        for term in parsed.terms:
            if term.is_free_text:
                continue

            # Map field names to JSON payload keys
            field_map = {
                "project": "used_in_projects",
                "source": "source",
                "category": "category",
                "method": "access_method",
                "format": "file_format",
                "size": "size",
                "sr": "spatial_resolution",
                "sc": "spatial_coverage",
                "tr": "temporal_resolution",
                "tc": "temporal_coverage",
            }

            json_field = field_map.get(term.field)
            if not json_field:
                # Unknown field - skip it silently or log warning
                logger.warning(f"Unknown field '{term.field}' in query, skipping")
                continue

            # Build condition based on operator
            # For numeric fields, cast to REAL for comparisons
            is_numeric_field = json_field in ('size', 'size_bytes')
            is_array_field = json_field in ('data_types', 'used_in_projects', 'codes')

            field_expr = f"CAST(json_extract(datasets_store.payload, '$.{json_field}') AS REAL)" if is_numeric_field else f"json_extract(datasets_store.payload, '$.{json_field}')"

            if term.operator == QueryOperator.CONTAINS:
                if is_array_field:
                    # For array fields, match whole tokens not substrings
                    # Use SQLite json_each to iterate array elements
                    # Check if value exists as a complete element in the array
                    where_clauses.append(f"""
                        EXISTS (
                            SELECT 1 FROM json_each(datasets_store.payload, '$.{json_field}')
                            WHERE value = ?
                        )
                    """)
                    params.append(term.value)
                else:
                    # For string fields, use substring matching
                    where_clauses.append(f"json_extract(datasets_store.payload, '$.{json_field}') LIKE ?")
                    params.append(f"%{term.value}%")
            elif term.operator == QueryOperator.EQ:
                where_clauses.append(f"{field_expr} = ?")
                params.append(term.value)
            elif term.operator == QueryOperator.GT:
                where_clauses.append(f"{field_expr} > ?")
                params.append(term.value)
            elif term.operator == QueryOperator.LT:
                where_clauses.append(f"{field_expr} < ?")
                params.append(term.value)
            elif term.operator == QueryOperator.GTE:
                where_clauses.append(f"{field_expr} >= ?")
                params.append(term.value)
            elif term.operator == QueryOperator.LTE:
                where_clauses.append(f"{field_expr} <= ?")
                params.append(term.value)

        # Build final SQL - always use datasets_store for structured queries
        if where_clauses:
            where_sql = " AND ".join(where_clauses)
            if parsed.free_text_query:
                # Combine FTS with field filters
                sql = f"""
                    SELECT
                        datasets_fts.id,
                        datasets_fts.name,
                        snippet(datasets_fts, 2, '<b>', '</b>', '...', 40) as snippet,
                        bm25(datasets_fts) as rank,
                        datasets_store.payload
                    FROM datasets_fts
                    JOIN datasets_store ON datasets_fts.id = datasets_store.id
                    WHERE {where_sql}
                    ORDER BY rank
                    LIMIT ?
                """
            else:
                # Field filters only, no FTS
                sql = f"""
                    SELECT
                        id,
                        json_extract(payload, '$.dataset_name') as name,
                        '' as snippet,
                        0 as rank,
                        payload
                    FROM datasets_store
                    WHERE {where_sql}
                    LIMIT ?
                """
            params.append(limit)
        else:
            # No filters, return all
            sql = """
                SELECT id, json_extract(payload, '$.dataset_name') as name, '' as snippet, 0 as rank, payload
                FROM datasets_store
                LIMIT ?
            """
            params = [limit]

        try:
            cursor.execute(sql, params)
        except Exception as e:
            logger.error(f"SQL error in structured search: {e}")
            logger.error(f"SQL: {sql}")
            logger.error(f"Params: {params}")
            # Return empty results on error
            return []

        results = []
        for row in cursor.fetchall():
            payload = json.loads(row["payload"])
            # Convert Row to dict for easier access with defaults
            row_dict = dict(row)
            results.append({
                "id": row_dict["id"],
                "name": row_dict["name"],
                "snippet": row_dict.get("snippet", ""),
                "rank": row_dict.get("rank", 0),
                "metadata": payload,
            })

        return results
    finally:
        conn.close()


def get_all_datasets(limit: int = 200) -> list[dict[str, Any]]:
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
