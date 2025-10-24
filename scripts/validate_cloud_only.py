#!/usr/bin/env python3
"""
Quick validation script for cloud-only workflow changes.
Tests that the CloudEditDetailsScreen class exists and is properly integrated.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_cloud_edit_screen_exists():
    """Test that CloudEditDetailsScreen is defined."""
    try:
        from mini_datahub.ui.views.home import CloudEditDetailsScreen
        print("✓ CloudEditDetailsScreen class exists")
        return True
    except ImportError as e:
        print(f"✗ Failed to import CloudEditDetailsScreen: {e}")
        return False

def test_cloud_details_has_edit_binding():
    """Test that CloudDatasetDetailsScreen has edit binding."""
    try:
        from mini_datahub.ui.views.home import CloudDatasetDetailsScreen

        # Check bindings
        bindings = CloudDatasetDetailsScreen.BINDINGS
        has_edit = any(b[0] == 'e' or (hasattr(b, 'key') and b.key == 'e') for b in bindings)

        if has_edit:
            print("✓ CloudDatasetDetailsScreen has 'e' key binding")
        else:
            print("✗ CloudDatasetDetailsScreen missing 'e' key binding")
            print(f"  Found bindings: {bindings}")

        # Check method exists
        if hasattr(CloudDatasetDetailsScreen, 'action_edit_cloud_dataset'):
            print("✓ CloudDatasetDetailsScreen has action_edit_cloud_dataset method")
        else:
            print("✗ CloudDatasetDetailsScreen missing action_edit_cloud_dataset method")
            return False

        return has_edit
    except Exception as e:
        print(f"✗ Failed to check CloudDatasetDetailsScreen: {e}")
        return False

def test_add_screen_cloud_only():
    """Test that AddDataScreen only saves to cloud."""
    try:
        from mini_datahub.ui.views.home import AddDataScreen
        import inspect

        # Get submit_form source
        source = inspect.getsource(AddDataScreen.submit_form)

        # Check that we removed local save logic
        has_storage_backend_check = 'storage_backend' in source
        has_save_dataset_call = 'save_dataset(' in source and 'save_to_cloud' not in source.split('save_dataset(')[0]
        has_pr_workflow_local = 'PRWorkflow()' in source and 'save_dataset' in source

        if has_storage_backend_check:
            print("⚠ AddDataScreen.submit_form still has storage_backend check")
            return False

        if has_save_dataset_call:
            print("⚠ AddDataScreen.submit_form still calls save_dataset() for local save")
            return False

        if 'save_to_cloud' in source:
            print("✓ AddDataScreen.submit_form uses cloud-only save")
            return True
        else:
            print("✗ AddDataScreen.submit_form doesn't call save_to_cloud")
            return False

    except Exception as e:
        print(f"✗ Failed to check AddDataScreen: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all necessary imports work."""
    try:
        from mini_datahub.ui.views.home import (
            CloudDatasetDetailsScreen,
            CloudEditDetailsScreen,
            AddDataScreen,
            DetailsScreen,
            EditDetailsScreen,
        )
        print("✓ All screen classes import successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_cloud_only_filtering():
    """Test that search and load functions filter for cloud-only datasets."""
    try:
        from mini_datahub.ui.views.home import HomeScreen
        import inspect

        # Check load_all_datasets filters cloud only
        load_source = inspect.getsource(HomeScreen.load_all_datasets)
        if 'is_remote' in load_source and 'cloud_results' in load_source:
            print("✓ load_all_datasets filters for cloud-only datasets")
        else:
            print("⚠ load_all_datasets may not filter for cloud-only")
            return False

        # Check perform_search filters cloud only
        search_source = inspect.getsource(HomeScreen.perform_search)
        if 'is_remote' in search_source and 'cloud_results' in search_source:
            print("✓ perform_search filters for cloud-only datasets")
        else:
            print("⚠ perform_search may not filter for cloud-only")
            return False

        return True

    except Exception as e:
        print(f"✗ Failed to check cloud filtering: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Cloud-Only Workflow Validation")
    print("=" * 60)
    print()

    tests = [
        ("Import Test", test_imports),
        ("CloudEditDetailsScreen Exists", test_cloud_edit_screen_exists),
        ("CloudDatasetDetailsScreen Edit Binding", test_cloud_details_has_edit_binding),
        ("AddDataScreen Cloud-Only", test_add_screen_cloud_only),
        ("Cloud-Only Filtering", test_cloud_only_filtering),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        result = test_func()
        results.append(result)
        print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"✗ SOME TESTS FAILED ({passed}/{total} passed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
