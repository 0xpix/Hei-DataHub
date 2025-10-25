#!/usr/bin/env python3
"""
Test script for new features:
1. Auth clear with --clear-index
2. Delete dataset functionality
3. Undo/redo in CloudEditDetailsScreen
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_auth_clear_index():
    """Test auth clear automatically clears index.db."""
    print("\n" + "="*60)
    print("TEST 1: Auth clear automatically clears index.db")
    print("="*60)

    from mini_datahub.auth.clear import run_clear
    from mini_datahub.services.index_service import INDEX_DB_PATH

    # Check if index.db exists
    exists_before = INDEX_DB_PATH.exists()
    print(f"\nIndex DB exists before: {exists_before}")
    print(f"Path: {INDEX_DB_PATH}")

    if not exists_before:
        print("⚠️  Creating dummy index.db for testing...")
        INDEX_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        INDEX_DB_PATH.touch()

    # Run clear (should automatically clear index)
    print("\nRunning: auth clear --force (no --clear-index flag needed)")
    result = run_clear(force=True, clear_all=False)

    # Check if index.db was deleted
    exists_after = INDEX_DB_PATH.exists()
    print(f"\nIndex DB exists after: {exists_after}")
    print(f"Exit code: {result}")

    if not exists_after and result == 0:
        print("✅ PASS: Index DB automatically deleted with auth clear")
        return True
    else:
        print("❌ FAIL: Index DB not deleted or wrong exit code")
        return False


def test_undo_redo_structure():
    """Test that CloudEditDetailsScreen has undo/redo structure."""
    print("\n" + "="*60)
    print("TEST 2: Undo/Redo Structure in CloudEditDetailsScreen")
    print("="*60)

    from mini_datahub.ui.views.home import CloudEditDetailsScreen

    # Create instance
    test_metadata = {
        'dataset_name': 'test',
        'description': 'test description',
        'source': 'test source'
    }

    screen = CloudEditDetailsScreen('test-dataset', test_metadata)

    # Check for undo/redo attributes
    has_undo_stack = hasattr(screen, '_undo_stack')
    has_redo_stack = hasattr(screen, '_redo_stack')
    has_previous_values = hasattr(screen, '_previous_values')
    has_undo_action = hasattr(screen, 'action_undo_edit')
    has_redo_action = hasattr(screen, 'action_redo_edit')

    print(f"\nHas _undo_stack: {has_undo_stack}")
    print(f"Has _redo_stack: {has_redo_stack}")
    print(f"Has _previous_values: {has_previous_values}")
    print(f"Has action_undo_edit: {has_undo_action}")
    print(f"Has action_redo_edit: {has_redo_action}")

    # Check BINDINGS
    has_undo_binding = any('undo' in str(b).lower() for b in screen.BINDINGS)
    has_redo_binding = any('redo' in str(b).lower() for b in screen.BINDINGS)

    print(f"Has undo key binding: {has_undo_binding}")
    print(f"Has redo key binding: {has_redo_binding}")

    all_checks = all([
        has_undo_stack,
        has_redo_stack,
        has_previous_values,
        has_undo_action,
        has_redo_action,
        has_undo_binding,
        has_redo_binding
    ])

    if all_checks:
        print("✅ PASS: All undo/redo components present")
        return True
    else:
        print("❌ FAIL: Missing undo/redo components")
        return False


def test_delete_dialog():
    """Test that ConfirmDeleteDialog exists."""
    print("\n" + "="*60)
    print("TEST 3: Delete Confirmation Dialog")
    print("="*60)

    try:
        from mini_datahub.ui.views.home import ConfirmDeleteDialog

        # Create instance
        dialog = ConfirmDeleteDialog('test-dataset')

        has_confirm = hasattr(dialog, 'action_confirm')
        has_cancel = hasattr(dialog, 'action_cancel')
        has_bindings = len(dialog.BINDINGS) > 0

        print(f"\nHas action_confirm: {has_confirm}")
        print(f"Has action_cancel: {has_cancel}")
        print(f"Has key bindings: {has_bindings}")
        print(f"Number of bindings: {len(dialog.BINDINGS)}")

        if has_confirm and has_cancel and has_bindings:
            print("✅ PASS: Delete dialog properly configured")
            return True
        else:
            print("❌ FAIL: Delete dialog missing components")
            return False

    except ImportError as e:
        print(f"❌ FAIL: Could not import ConfirmDeleteDialog: {e}")
        return False


def test_delete_action():
    """Test that CloudDatasetDetailsScreen has delete action."""
    print("\n" + "="*60)
    print("TEST 4: Delete Action in CloudDatasetDetailsScreen")
    print("="*60)

    from mini_datahub.ui.views.home import CloudDatasetDetailsScreen

    # Create instance
    screen = CloudDatasetDetailsScreen('test-dataset')

    has_delete_action = hasattr(screen, 'action_delete_dataset')
    has_handle_confirmation = hasattr(screen, '_handle_delete_confirmation')
    has_delete_from_cloud = hasattr(screen, 'delete_from_cloud')

    print(f"\nHas action_delete_dataset: {has_delete_action}")
    print(f"Has _handle_delete_confirmation: {has_handle_confirmation}")
    print(f"Has delete_from_cloud: {has_delete_from_cloud}")

    # Check BINDINGS for 'd' key
    has_delete_binding = any('delete' in str(b).lower() for b in screen.BINDINGS)

    print(f"Has delete key binding: {has_delete_binding}")

    all_checks = all([
        has_delete_action,
        has_handle_confirmation,
        has_delete_from_cloud,
        has_delete_binding
    ])

    if all_checks:
        print("✅ PASS: Delete action properly configured")
        return True
    else:
        print("❌ FAIL: Delete action missing components")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESTING NEW FEATURES")
    print("="*60)

    results = []

    # Test 1: Auth clear automatically clears index
    results.append(("Auth clear auto-clears index.db", test_auth_clear_index()))

    # Test 2: Undo/Redo structure
    results.append(("Undo/Redo structure", test_undo_redo_structure()))

    # Test 3: Delete dialog
    results.append(("Delete dialog", test_delete_dialog()))

    # Test 4: Delete action
    results.append(("Delete action", test_delete_action()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
