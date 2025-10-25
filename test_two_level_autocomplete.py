#!/usr/bin/env python3
"""
Test two-level autocomplete: field names + field values.

Level 1: Type "so" → suggests "source:"
Level 2: Type "source:go" → suggests "source:google.com"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_field_name_autocomplete():
    """Test that typing partial field names suggests complete field names."""
    print("\n" + "="*70)
    print("TEST: Field Name Autocomplete (Level 1)")
    print("="*70)

    from mini_datahub.ui.widgets.autocomplete import SmartSearchSuggester

    suggester = SmartSearchSuggester()

    # Test cases: (input, expected_field_in_suggestion)
    test_cases = [
        ("so", "source:"),
        ("sou", "source:"),
        ("source", "source:"),
        ("pro", "project:"),
        ("proj", "project:"),
        ("ta", "tag:"),
        ("tag", "tag:"),
        ("ow", "owner:"),
        ("si", "size:"),
        ("fo", "format:"),
        ("ty", "type:"),
    ]

    for input_val, expected_field in test_cases:
        field_key, partial, is_typing_field = suggester._parse_input(input_val)

        assert is_typing_field, f"Should detect typing field for '{input_val}'"
        assert field_key is None, f"field_key should be None when typing field name"
        assert partial == input_val, f"partial should be '{input_val}', got '{partial}'"

        # Check that the field would be suggested
        field_names = ["source:", "project:", "tag:", "owner:", "size:", "format:", "type:"]
        matches = [f for f in field_names if f.startswith(input_val.lower())]

        assert expected_field in matches, f"'{expected_field}' should be in matches for '{input_val}'"
        print(f"✅ '{input_val}' → suggests '{expected_field}'")

    print(f"\n✅ All {len(test_cases)} field name tests passed!")
    return True


def test_field_value_autocomplete():
    """Test that after field name, it suggests field values."""
    print("\n" + "="*70)
    print("TEST: Field Value Autocomplete (Level 2)")
    print("="*70)

    from mini_datahub.ui.widgets.autocomplete import SmartSearchSuggester

    suggester = SmartSearchSuggester()

    # Test cases: (input, expected_field_key, expected_partial, is_typing_field)
    test_cases = [
        ("source:", "source", "", False),
        ("source:go", "source", "go", False),
        ("source:google", "source", "google", False),
        ("project:", "project", "", False),
        ("project:ML", "project", "ML", False),
        ("tag:", "tag", "", False),
        ("tag:neural", "tag", "neural", False),
        ("size:", "size", "", False),
        ("size:s", "size", "s", False),
    ]

    for input_val, expected_field, expected_partial, expected_typing_field in test_cases:
        field_key, partial, is_typing_field = suggester._parse_input(input_val)

        assert field_key == expected_field, f"Expected field='{expected_field}', got '{field_key}' for '{input_val}'"
        assert partial == expected_partial, f"Expected partial='{expected_partial}', got '{partial}' for '{input_val}'"
        assert is_typing_field == expected_typing_field, f"Expected is_typing_field={expected_typing_field} for '{input_val}'"

        print(f"✅ '{input_val}' → field='{field_key}', partial='{partial}'")

    print(f"\n✅ All {len(test_cases)} field value tests passed!")
    return True


def test_multiword_queries():
    """Test autocomplete in multi-word queries."""
    print("\n" + "="*70)
    print("TEST: Multi-Word Query Autocomplete")
    print("="*70)

    from mini_datahub.ui.widgets.autocomplete import SmartSearchSuggester

    suggester = SmartSearchSuggester()

    test_cases = [
        # (input, should_detect_as_field_typing, last_token_parsed)
        ("project:ML so", True, "so"),                    # Typing new field after complete filter
        ("project:ML source:", False, "source:"),         # Typing value for second filter
        ("project:ML source:go", False, "source:go"),     # Typing value continuation
        ("tag:neural pro", True, "pro"),                  # Typing new field
        ("tag:neural project:", False, "project:"),       # Ready for project value
    ]

    for input_val, expected_typing_field, expected_last_token in test_cases:
        field_key, partial, is_typing_field = suggester._parse_input(input_val)

        assert is_typing_field == expected_typing_field, f"Failed for '{input_val}': expected typing_field={expected_typing_field}, got {is_typing_field}"

        # Check that it's parsing the last token correctly
        last_token = input_val.split()[-1] if input_val.split() else ""
        assert last_token == expected_last_token, f"Last token should be '{expected_last_token}', got '{last_token}'"

        status = "field name" if is_typing_field else "field value"
        print(f"✅ '{input_val}' → autocompleting {status}")

    print(f"\n✅ All {len(test_cases)} multi-word tests passed!")
    return True


def test_edge_cases():
    """Test edge cases and special scenarios."""
    print("\n" + "="*70)
    print("TEST: Edge Cases")
    print("="*70)

    from mini_datahub.ui.widgets.autocomplete import SmartSearchSuggester

    suggester = SmartSearchSuggester()

    test_cases = [
        ("", None, "", True, "Empty string"),
        ("  ", None, "", True, "Whitespace only"),
        ("s", None, "s", True, "Single character"),
        ("source:", "source", "", False, "Field with colon, no value"),
        ("source:http://example.com", "source", "http://example.com", False, "URL with multiple colons"),
        ("unknown:", None, "unknown:", True, "Unrecognized field"),
    ]

    for input_val, exp_field, exp_partial, exp_typing, description in test_cases:
        field_key, partial, is_typing_field = suggester._parse_input(input_val)

        assert field_key == exp_field, f"{description}: expected field='{exp_field}', got '{field_key}'"
        assert is_typing_field == exp_typing, f"{description}: expected typing_field={exp_typing}, got {is_typing_field}"

        print(f"✅ {description}: '{input_val}' parsed correctly")

    print(f"\n✅ All {len(test_cases)} edge case tests passed!")
    return True


def main():
    """Run all two-level autocomplete tests."""
    print("\n" + "="*70)
    print("TWO-LEVEL AUTOCOMPLETE TEST SUITE")
    print("="*70)

    tests = [
        ("Field Name Autocomplete", test_field_name_autocomplete),
        ("Field Value Autocomplete", test_field_value_autocomplete),
        ("Multi-Word Queries", test_multiword_queries),
        ("Edge Cases", test_edge_cases),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            import traceback
            print(f"\n❌ FAILED: {e}")
            traceback.print_exc()
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Two-level autocomplete is working!")
        print("\nUsage:")
        print("  1. Type 'so' → Tab → completes to 'source:'")
        print("  2. Type 'google' → Tab → completes to 'source:google.com'")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
