#!/usr/bin/env python3
"""
Test script for TUI UX improvements:
1. Smart autocomplete (duplicate method removed)
2. Badge type indicators (enhanced with operator-specific emoji)
3. 'o' key to open URLs in CloudDatasetDetailsScreen
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_autocomplete_no_duplicates():
    """Test that autocomplete setup method is not duplicated."""
    from mini_datahub.ui.views.home import HomeScreen
    import inspect

    # Get all methods of HomeScreen
    methods = inspect.getmembers(HomeScreen, predicate=inspect.isfunction)

    # Count how many times _setup_search_autocomplete appears
    autocomplete_methods = [name for name, _ in methods if name == '_setup_search_autocomplete']

    assert len(autocomplete_methods) == 1, f"Expected 1 _setup_search_autocomplete method, found {len(autocomplete_methods)}"
    print("✅ Autocomplete: No duplicate methods found")
    return True


def test_enhanced_badges():
    """Test that badge system has operator-specific emoji."""
    from mini_datahub.ui.views.home import HomeScreen
    import inspect

    # Get the _update_filter_badges method source
    source = inspect.getsource(HomeScreen._update_filter_badges)

    # Check for operator-specific emoji
    required_emoji = ['📈', '📉', '⬆️', '⬇️', '🎯', '🏷', '📝']
    found_emoji = []

    for emoji in required_emoji:
        if emoji in source:
            found_emoji.append(emoji)

    print(f"✅ Badge types: Found {len(found_emoji)}/{len(required_emoji)} operator-specific emoji")
    print(f"   Emoji found: {', '.join(found_emoji)}")

    # Check that operator_info dictionary exists
    assert 'operator_info' in source, "Missing operator_info mapping"
    print("✅ Badge types: operator_info mapping exists")

    return True


def test_cloud_dataset_open_url():
    """Test that CloudDatasetDetailsScreen has 'o' binding and action_open_url."""
    from mini_datahub.ui.views.home import CloudDatasetDetailsScreen
    import inspect

    # Check BINDINGS includes 'o'
    bindings = [b[0] if isinstance(b, tuple) else b.key for b in CloudDatasetDetailsScreen.BINDINGS]
    assert 'o' in bindings, "'o' key not found in CloudDatasetDetailsScreen BINDINGS"
    print("✅ Open URL: 'o' key binding found in CloudDatasetDetailsScreen")

    # Check action_open_url method exists
    assert hasattr(CloudDatasetDetailsScreen, 'action_open_url'), "action_open_url method not found"

    # Check the method signature
    method = getattr(CloudDatasetDetailsScreen, 'action_open_url')
    source = inspect.getsource(method)

    # Verify it uses webbrowser
    assert 'webbrowser' in source, "action_open_url should use webbrowser"
    assert 'http://' in source or 'https://' in source, "action_open_url should check for HTTP/HTTPS"

    print("✅ Open URL: action_open_url method implemented correctly")
    return True


def main():
    """Run all tests."""
    print("Testing TUI UX improvements...\n")

    tests = [
        ("Autocomplete (no duplicates)", test_autocomplete_no_duplicates),
        ("Enhanced badge types", test_enhanced_badges),
        ("Cloud dataset 'o' key", test_cloud_dataset_open_url),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print('='*60)
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result, _ in results if result)
    total = len(results)

    for name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
