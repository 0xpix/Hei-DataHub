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
        from hei_datahub.ui.views.home import CloudEditDetailsScreen  # noqa: F401
        print("✓ CloudEditDetailsScreen class exists")
        return True
    except ImportError as e:
        print(f"✗ Failed to import CloudEditDetailsScreen: {e}")
        return False

def test_cloud_details_has_edit_binding():
    """Test that CloudDatasetDetailsScreen has edit binding."""
    try:
        from hei_datahub.ui.views.home import CloudDatasetDetailsScreen

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
        import inspect

        from hei_datahub.ui.views.home import AddDataScreen

        # Get submit_form source
        source = inspect.getsource(AddDataScreen.submit_form)

        # Check that we removed local save logic
        has_storage_backend_check = 'storage_backend' in source
        has_save_dataset_call = 'save_dataset(' in source and 'save_to_cloud' not in source.split('save_dataset(')[0]

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
        from hei_datahub.ui.views.home import (
            AddDataScreen,  # noqa: F401
            CloudDatasetDetailsScreen,  # noqa: F401
            CloudEditDetailsScreen,  # noqa: F401
            DetailsScreen,  # noqa: F401
            EditDetailsScreen,  # noqa: F401
        )
        print("✓ All screen classes import successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Validating Cloud-Only Workflow Implementation...")
    print("-" * 50)

    results = [
        test_cloud_edit_screen_exists(),
        test_imports(),
        test_cloud_details_has_edit_binding(),
        test_add_screen_cloud_only()
    ]

    print("-" * 50)
    if all(results):
        print("✓ All checks passed!")
        sys.exit(0)
    else:
        print("✗ Some checks failed.")
        sys.exit(1)
