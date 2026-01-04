#!/usr/bin/env python3
"""
Test automatic index updates when adding/editing/deleting datasets.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_add_dataset():
    """Test that adding a dataset updates the index automatically."""
    from hei_datahub.services.catalog import save_dataset
    from hei_datahub.services.index_service import get_index_service

    print("\n" + "=" * 60)
    print("TEST: Add Dataset (Auto Index Update)")
    print("=" * 60)

    # Get initial count
    index = get_index_service()
    total_before, remote_before = index.get_item_count()
    print(f"\nBefore: {total_before} items ({remote_before} remote)")

    # Add a test dataset
    test_metadata = {
        "dataset_name": "Auto Index Test Dataset",
        "description": "This dataset tests automatic index updates",
        "keywords": ["test", "automation"],
        "used_in_projects": ["test-project"],
        "source": "test",
        "file_format": "csv",
    }

    print("\n📝 Adding dataset: test-auto-index...")
    success, error = save_dataset("test-auto-index", test_metadata)

    if not success:
        print(f"❌ Failed to add dataset: {error}")
        return False

    print("✅ Dataset added to store")

    # Check if index was updated
    total_after, remote_after = index.get_item_count()
    print(f"\nAfter: {total_after} items ({remote_after} remote)")

    # Search for the new dataset
    results = index.search(query_text="Auto Index Test")

    if len(results) > 0:
        print(f"✅ Dataset found in index: {results[0]['name']}")
        print(f"   Project: {results[0].get('project')}")
        print(f"   Tags: {results[0].get('tags')}")
        return True
    else:
        print("❌ Dataset NOT found in index!")
        return False


def test_delete_dataset():
    """Test that deleting a dataset updates the index automatically."""
    from hei_datahub.infra.index import delete_dataset
    from hei_datahub.services.index_service import get_index_service

    print("\n" + "=" * 60)
    print("TEST: Delete Dataset (Auto Index Update)")
    print("=" * 60)

    index = get_index_service()

    # Check if test dataset exists
    results_before = index.search(query_text="Auto Index Test")
    print(f"\nBefore delete: {len(results_before)} results for 'Auto Index Test'")

    if len(results_before) == 0:
        print("⚠️  Test dataset not found, skipping delete test")
        return True

    # Delete the dataset
    print("\n🗑️  Deleting dataset: test-auto-index...")
    delete_dataset("test-auto-index")
    print("✅ Dataset deleted from store")

    # Check if index was updated
    results_after = index.search(query_text="Auto Index Test")
    print(f"\nAfter delete: {len(results_after)} results for 'Auto Index Test'")

    if len(results_after) == 0:
        print("✅ Dataset removed from index")
        return True
    else:
        print("❌ Dataset STILL in index!")
        return False


def main():
    """Run all tests."""
    print("\n🧪 Testing Automatic Index Updates\n")

    results = []

    # Test add
    results.append(("Add Dataset", test_add_dataset()))

    # Test delete
    results.append(("Delete Dataset", test_delete_dataset()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Index updates automatically.")
    else:
        print("\n❌ Some tests failed!")

    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
