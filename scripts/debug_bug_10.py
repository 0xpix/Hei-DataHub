#!/usr/bin/env python3
"""
Debug script to test Bug #10 fix: Multi-term badge display.

Run this to see if badges are created correctly.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mini_datahub.core.queries import QueryParser

def test_badge_creation(query: str):
    """Test how many badges would be created for a query."""
    print(f"\n{'='*60}")
    print(f"Query: '{query}'")
    print(f"{'='*60}")

    parser = QueryParser()
    parsed = parser.parse(query)

    print(f"\nTotal terms parsed: {len(parsed.terms)}")
    print(f"Free text query: '{parsed.free_text_query}'")

    # Field filter badges
    field_filters = [t for t in parsed.terms if not t.is_free_text]
    print(f"\nField filter badges ({len(field_filters)}):")
    for term in field_filters:
        print(f"  🏷 {term.field}:{term.value}")

    # Free text badges
    free_text_terms = [t for t in parsed.terms if t.is_free_text]
    print(f"\nFree text badges ({len(free_text_terms)}):")
    for term in free_text_terms:
        print(f"  📝 {term.value}")

    print(f"\nTotal badges that would appear: {len(field_filters) + len(free_text_terms)}")
    print()

if __name__ == "__main__":
    # Test cases
    test_badge_creation("the data")
    test_badge_creation("rainfall temp rice")
    test_badge_creation("format:csv source:github")
    test_badge_creation("format:csv rainfall temp")
    test_badge_creation('a b "rice field"')
    test_badge_creation("climate data weather temperature")
