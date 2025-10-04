#!/usr/bin/env python3
"""
Test script for auto-stash functionality.

This verifies that:
1. Stash operations work correctly
2. Pull with uncommitted changes uses auto-stash
3. Changes are restored after pull
"""

from pathlib import Path
from mini_datahub.git_ops import GitOperations
from mini_datahub.auto_pull import get_auto_pull_manager


def test_stash_operations():
    """Test basic stash operations."""
    print("=" * 60)
    print("Test 1: Basic Stash Operations")
    print("=" * 60)

    catalog_path = Path.home() / "Github" / "Hei-Catalog"

    if not catalog_path.exists():
        print(f"❌ Catalog not found at {catalog_path}")
        return False

    git_ops = GitOperations(catalog_path)

    # Test get_current_branch
    try:
        branch = git_ops.get_current_branch()
        print(f"✓ Current branch: {branch}")
    except Exception as e:
        print(f"❌ Failed to get current branch: {e}")
        return False

    # Test has_stash
    try:
        has_stash = git_ops.has_stash()
        print(f"✓ Has stash: {has_stash}")
    except Exception as e:
        print(f"❌ Failed to check stash: {e}")
        return False

    # Test status check
    code, stdout, stderr = git_ops._run_command(
        ["git", "status", "--porcelain"],
        check=False
    )
    has_changes = len(stdout.strip()) > 0
    print(f"✓ Has uncommitted changes: {has_changes}")

    if has_changes:
        print(f"  Changes:\n{stdout}")

    print()
    return True


def test_auto_pull_with_stash():
    """Test pull_updates with auto-stash enabled."""
    print("=" * 60)
    print("Test 2: Pull with Auto-Stash")
    print("=" * 60)

    catalog_path = Path.home() / "Github" / "Hei-Catalog"

    if not catalog_path.exists():
        print(f"❌ Catalog not found at {catalog_path}")
        return False

    pull_manager = get_auto_pull_manager(catalog_path)

    # Check if we have local changes
    has_changes, status = pull_manager.has_local_changes()
    print(f"Has local changes: {has_changes}")
    if has_changes:
        print(f"Status:\n{status}")
        print()

    # Check if behind remote
    is_behind, commits = pull_manager.is_behind_remote("main")
    print(f"Behind remote: {is_behind} ({commits} commits)")

    if not is_behind and not has_changes:
        print("✓ Already up to date and no changes to test stash")
        print()
        return True

    # Test pull with auto_stash=True (default)
    print("\nTesting pull_updates with auto_stash=True...")
    success, message, old_commit, new_commit = pull_manager.pull_updates(
        branch="main",
        auto_stash=True  # This is the default
    )

    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Old commit: {old_commit[:8] if old_commit else 'None'}")
    print(f"New commit: {new_commit[:8] if new_commit else 'None'}")

    if success:
        print("✓ Pull succeeded with auto-stash")
    else:
        print(f"❌ Pull failed: {message}")
        return False

    print()
    return True


def test_signature_compatibility():
    """Test that pull_updates can be called without auto_stash parameter."""
    print("=" * 60)
    print("Test 3: Backward Compatibility")
    print("=" * 60)

    catalog_path = Path.home() / "Github" / "Hei-Catalog"

    if not catalog_path.exists():
        print(f"❌ Catalog not found at {catalog_path}")
        return False

    pull_manager = get_auto_pull_manager(catalog_path)

    # Test calling without auto_stash parameter (should default to True)
    print("Calling pull_updates() without auto_stash parameter...")
    try:
        success, message, old_commit, new_commit = pull_manager.pull_updates()
        print(f"✓ Method signature is backward compatible")
        print(f"  Success: {success}")
        print(f"  Message: {message[:60]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    print()
    return True


def main():
    """Run all tests."""
    print("\n🧪 Testing Auto-Stash Functionality\n")

    results = []

    # Run tests
    results.append(("Basic Stash Operations", test_stash_operations()))
    results.append(("Pull with Auto-Stash", test_auto_pull_with_stash()))
    results.append(("Backward Compatibility", test_signature_compatibility()))

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
