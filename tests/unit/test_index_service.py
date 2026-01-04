"""
Unit tests for the index service.
"""
import tempfile
from pathlib import Path

import pytest

from hei_datahub.services.index_service import IndexService


@pytest.fixture
def temp_index():
    """Create a temporary index database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_index.db"
        index = IndexService(db_path=db_path)
        yield index


def test_index_initialization(temp_index):
    """Test that index database is created and initialized."""
    assert temp_index.db_path.exists()
    conn = temp_index.get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    assert "items" in tables
    assert "items_fts" in tables
    assert "index_meta" in tables
    conn.close()


def test_upsert_and_search(temp_index):
    """Test inserting items and searching."""
    # Insert test items
    temp_index.upsert_item(
        path="dataset-1",
        name="Climate Data 2024",
        project="climate-research",
        tags="climate temperature",
        description="Temperature measurements from 2024",
        is_remote=False,
    )

    temp_index.upsert_item(
        path="dataset-2",
        name="Rainfall Data",
        project="climate-research",
        tags="climate precipitation",
        description="Precipitation measurements",
        is_remote=True,
    )

    temp_index.upsert_item(
        path="dataset-3",
        name="Burned Area Analysis",
        project="wildfire",
        tags="fire burned-area",
        description="Wildfire burned area statistics",
        is_remote=False,
    )

    # Test free text search
    results = temp_index.search(query_text="climate")
    assert len(results) == 2
    assert all("climate" in r["name"].lower() or "climate" in r.get("description", "").lower()
               for r in results)

    # Test project filter
    results = temp_index.search(query_text="", project_filter="climate")
    assert len(results) == 2
    assert all(r["project"] == "climate-research" for r in results)

    # Test combined search
    results = temp_index.search(query_text="data", project_filter="climate")
    assert len(results) == 2

    # Test no results
    results = temp_index.search(query_text="nonexistent")
    assert len(results) == 0


def test_bulk_upsert(temp_index):
    """Test bulk insert operation."""
    items = [
        {
            "path": f"dataset-{i}",
            "name": f"Dataset {i}",
            "project": "test-project",
            "tags": "test tag",
            "description": f"Description {i}",
            "is_remote": False,
        }
        for i in range(100)
    ]

    count = temp_index.bulk_upsert(items)
    assert count == 100

    # Verify all items are searchable
    results = temp_index.search(query_text="Dataset", limit=200)
    assert len(results) == 100


def test_project_suggestions(temp_index):
    """Test project autocomplete suggestions."""
    # Insert items with different projects
    temp_index.upsert_item(
        path="d1", name="D1", project="climate-research", is_remote=False
    )
    temp_index.upsert_item(
        path="d2", name="D2", project="climate-modeling", is_remote=False
    )
    temp_index.upsert_item(
        path="d3", name="D3", project="wildfire-analysis", is_remote=False
    )

    # Get all projects
    suggestions = temp_index.get_project_suggestions()
    assert len(suggestions) == 3
    assert "climate-research" in suggestions

    # Get projects with prefix
    suggestions = temp_index.get_project_suggestions(prefix="climate")
    assert len(suggestions) == 2
    assert all(s.startswith("climate") for s in suggestions)


def test_item_count(temp_index):
    """Test counting items."""
    # Insert mixed local and remote items
    temp_index.upsert_item(path="local-1", name="L1", is_remote=False)
    temp_index.upsert_item(path="local-2", name="L2", is_remote=False)
    temp_index.upsert_item(path="remote-1", name="R1", is_remote=True)

    total, remote = temp_index.get_item_count()
    assert total == 3
    assert remote == 1


def test_cache_invalidation(temp_index):
    """Test that cache is invalidated on updates."""
    # Insert and search
    temp_index.upsert_item(path="d1", name="Dataset One", is_remote=False)
    results = temp_index.search(query_text="Dataset")
    assert len(results) == 1

    # Update item
    temp_index.upsert_item(path="d1", name="Updated Dataset", is_remote=False)
    results = temp_index.search(query_text="Updated")
    assert len(results) == 1
    assert results[0]["name"] == "Updated Dataset"


def test_metadata_storage(temp_index):
    """Test storing and retrieving metadata."""
    temp_index.set_meta("last_sync", "2025-01-01")
    assert temp_index.get_meta("last_sync") == "2025-01-01"

    # Non-existent key
    assert temp_index.get_meta("nonexistent") is None

    # Update metadata
    temp_index.set_meta("last_sync", "2025-01-02")
    assert temp_index.get_meta("last_sync") == "2025-01-02"


def test_search_with_special_characters(temp_index):
    """Test search handles special characters gracefully."""
    temp_index.upsert_item(
        path="test-1",
        name="Test: Data (2024)",
        description="Test with special chars: @#$%",
        is_remote=False,
    )

    # Should not crash
    results = temp_index.search(query_text="Test")
    assert len(results) == 1


def test_prefix_matching(temp_index):
    """Test that prefix matching works for incremental search."""
    temp_index.upsert_item(
        path="climate-1",
        name="Climate Research 2024",
        is_remote=False,
    )

    # Test prefix search (as user types)
    for prefix in ["cli", "clim", "climat", "climate"]:
        results = temp_index.search(query_text=prefix)
        assert len(results) == 1, f"Failed for prefix: {prefix}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
