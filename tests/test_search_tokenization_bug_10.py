"""
Test for Bug #10: Multi-term search tokenization.

Verifies that multi-term search input creates separate tags/tokens, not one combined token.
"""
import pytest

from mini_datahub.core.queries import QueryParser, ParsedQuery


def test_multi_term_tokenization_basic():
    """
    Test that space-separated terms create multiple tokens.
    
    Reproduces Bug #10:
    Input: "rainfall temp rice"
    Expected: 3 separate tokens
    Actual (before fix): 1 combined token
    """
    parser = QueryParser()
    query = "rainfall temp rice"
    
    parsed = parser.parse(query)
    
    # Should create 3 free-text terms
    free_text_terms = [t for t in parsed.terms if t.is_free_text]
    assert len(free_text_terms) == 3, \
        f"BUG #10: Expected 3 tokens, got {len(free_text_terms)}"
    
    # Verify each term
    values = [t.value for t in free_text_terms]
    assert "rainfall" in values
    assert "temp" in values
    assert "rice" in values


def test_multi_term_with_quoted_phrase():
    """
    Test that quoted phrases are preserved as single tokens.
    
    Input: a, b, "rice field"
    Expected: 3 tokens: ["a", "b", "rice field"]
    """
    parser = QueryParser()
    query = 'a b "rice field"'
    
    parsed = parser.parse(query)
    
    # Should parse free text properly
    assert parsed.free_text_query is not None
    
    # Free text should contain all terms
    assert "a" in parsed.free_text_query
    assert "b" in parsed.free_text_query
    assert "rice field" in parsed.free_text_query


def test_comma_separated_terms():
    """
    Test that comma-separated terms are tokenized.
    
    Input: "a, b, c"
    Expected: 3 tokens
    """
    parser = QueryParser()
    query = "a, b, c"
    
    parsed = parser.parse(query)
    
    # Get free text terms
    free_text_terms = [t for t in parsed.terms if t.is_free_text]
    
    # Should have 3 tokens (commas are treated as whitespace)
    assert len(free_text_terms) >= 3, \
        f"Expected at least 3 tokens from comma-separated input, got {len(free_text_terms)}"


def test_field_filters_with_free_text():
    """
    Test that field filters and free text coexist correctly.
    
    Input: "format:csv rainfall temp"
    Expected: 1 field filter + 2 free text tokens
    """
    parser = QueryParser()
    query = "format:csv rainfall temp"
    
    parsed = parser.parse(query)
    
    # Should have 1 field filter
    field_filters = [t for t in parsed.terms if not t.is_free_text]
    assert len(field_filters) == 1
    assert field_filters[0].field == "format"
    assert field_filters[0].value == "csv"
    
    # Should have free text for "rainfall temp"
    assert parsed.free_text_query is not None
    assert "rainfall" in parsed.free_text_query
    assert "temp" in parsed.free_text_query


def test_filter_badges_display_correctly():
    """
    Test that badge display logic handles multiple terms.
    
    This tests the UI layer expectation - badges should be created
    per filter, not as one combined badge.
    """
    parser = QueryParser()
    query = "format:csv source:github type:raster"
    
    parsed = parser.parse(query)
    
    # Should have 3 field filters
    field_filters = [t for t in parsed.terms if not t.is_free_text]
    assert len(field_filters) == 3, \
        f"BUG #10: Expected 3 filter badges, got {len(field_filters)}"
    
    # Each filter should be separate
    fields = {t.field for t in field_filters}
    assert fields == {"format", "source", "type"}


def test_deduplication_of_terms():
    """Test that duplicate terms are handled appropriately."""
    parser = QueryParser()
    query = "rainfall rainfall rainfall"
    
    parsed = parser.parse(query)
    
    # Current implementation may or may not dedupe - just ensure it parses
    free_text_terms = [t for t in parsed.terms if t.is_free_text]
    assert len(free_text_terms) > 0, "Should have at least one term"


def test_mixed_quotes_and_commas():
    """
    Test complex input with quotes and commas.
    
    Input: 'rainfall, "rice field", temperature'
    Expected: 3 tokens: ["rainfall", "rice field", "temperature"]
    """
    parser = QueryParser()
    query = 'rainfall, "rice field", temperature'
    
    parsed = parser.parse(query)
    
    # Free text should contain all terms
    assert parsed.free_text_query is not None
    assert "rainfall" in parsed.free_text_query
    assert "rice field" in parsed.free_text_query
    assert "temperature" in parsed.free_text_query


def test_and_semantics():
    """
    Test that multiple terms are combined with AND logic (by design).
    
    This is an integration test expectation:
    Search for "climate data" should find datasets containing BOTH words.
    """
    parser = QueryParser()
    query = "climate data"
    
    parsed = parser.parse(query)
    
    # Should have free text for both terms
    assert parsed.free_text_query is not None
    # Both terms should be in free text query
    tokens = parsed.free_text_query.split()
    assert "climate" in tokens or "climate" in parsed.free_text_query
    assert "data" in tokens or "data" in parsed.free_text_query


def test_empty_query():
    """Test that empty queries are handled gracefully."""
    parser = QueryParser()
    
    parsed = parser.parse("")
    assert len(parsed.terms) == 0
    assert parsed.free_text_query == ""
    
    parsed = parser.parse("   ")
    assert len(parsed.terms) == 0


def test_special_characters_in_free_text():
    """Test that special characters don't break tokenization."""
    parser = QueryParser()
    query = "data-2024 temp_avg rainfall.csv"
    
    parsed = parser.parse(query)
    
    # Should parse without error
    assert parsed.free_text_query is not None
    # At least some terms should be extracted
    free_text_terms = [t for t in parsed.terms if t.is_free_text]
    assert len(free_text_terms) > 0
