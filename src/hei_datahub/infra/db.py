"""
Database: SQLite connection and schema initialization.
"""
import sqlite3
from typing import Optional

from hei_datahub.infra.paths import DB_PATH, get_schema_sql


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database() -> None:
    """Initialize the database schema if it doesn't exist."""
    conn = get_connection()
    schema_sql = get_schema_sql()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def ensure_database() -> None:
    """Ensure database exists and has the correct schema."""
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
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


def execute_query(
    query: str,
    params: Optional[tuple] = None,
    fetch: str = "all"
) -> list:
    """
    Execute a SELECT query and return results.

    Args:
        query: SQL query string
        params: Query parameters
        fetch: 'all', 'one', or 'none'

    Returns:
        Query results
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    if fetch == "all":
        result = cursor.fetchall()
    elif fetch == "one":
        result = cursor.fetchone()
    else:
        result = []

    conn.close()
    return result


def execute_write(query: str, params: Optional[tuple] = None) -> int:
    """
    Execute an INSERT, UPDATE, or DELETE query.

    Args:
        query: SQL query string
        params: Query parameters

    Returns:
        Number of affected rows
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    rowcount = cursor.rowcount
    conn.commit()
    conn.close()

    return rowcount
