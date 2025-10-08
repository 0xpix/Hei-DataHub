#!/usr/bin/env python3
"""
Interactive test for Bug #10 fix.

This script helps verify that badge display works correctly.
Run the actual app and compare with these expected results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mini_datahub.core.queries import QueryParser

def analyze_query(query: str):
    """Analyze what badges should appear for a given query."""
    print(f"\n{'='*70}")
    print(f"QUERY: '{query}'")
    print(f"{'='*70}")

    parser = QueryParser()
    try:
        parsed = parser.parse(query)

        # Count badges
        field_badges = [t for t in parsed.terms if not t.is_free_text]
        text_badges = [t for t in parsed.terms if t.is_free_text]

        print(f"\nExpected badges in UI:")
        print(f"  • Field filters: {len(field_badges)}")
        for term in field_badges:
            print(f"    - 🏷 {term.field}:{term.value}")

        print(f"  • Free text terms: {len(text_badges)}")
        for term in text_badges:
            print(f"    - 📝 {term.value}")

        total = len(field_badges) + len(text_badges)
        print(f"\n  ⚠️  TOTAL BADGES SHOULD APPEAR: {total}")

        if total == 1:
            print(f"  ⚠️  If you see only 1 badge in the app, Bug #10 NOT fixed!")
        else:
            print(f"  ✅ If you see {total} badges in the app, Bug #10 IS fixed!")

    except Exception as e:
        print(f"\nError parsing query: {e}")

def main():
    print("\n" + "="*70)
    print("BUG #10 FIX VERIFICATION - Badge Display Test")
    print("="*70)
    print("\nTest these queries in the actual app and compare with expected results:")

    test_queries = [
        "the data",
        "rainfall temp rice",
        "climate weather",
        "format:csv source:github",
        "format:csv rainfall temp",
        "burned area precipitation",
        "land cover climate data",
    ]

    for query in test_queries:
        analyze_query(query)

    print("\n" + "="*70)
    print("HOW TO TEST IN THE APP:")
    print("="*70)
    print("1. Run: hei-datahub")
    print("2. Press '/' to focus search")
    print("3. Type one of the queries above")
    print("4. Look at the badges below the search box")
    print("5. Compare the number of badges with the expected count above")
    print("\n" + "="*70)
    print("EXPECTED BEHAVIOR (Bug #10 FIXED):")
    print("="*70)
    print("• Query 'the data' → 2 separate badges: [📝 the] [📝 data]")
    print("• Query 'rainfall temp rice' → 3 badges: [📝 rainfall] [📝 temp] [📝 rice]")
    print("\n" + "="*70)
    print("BROKEN BEHAVIOR (Bug #10 NOT fixed):")
    print("="*70)
    print("• Query 'the data' → 1 combined badge: [📝 \"the data\"]")
    print("• Query 'rainfall temp rice' → 1 badge: [📝 \"rainfall temp rice\"]")
    print("\n")

if __name__ == "__main__":
    main()
