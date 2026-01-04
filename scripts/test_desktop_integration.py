#!/usr/bin/env python3
"""
Smoke test for desktop integration.

Tests all major functions without actually installing anything.
"""
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from hei_datahub.desktop_install import (
            ensure_desktop_assets_once,  # noqa: F401
            get_desktop_assets_status,  # noqa: F401
            get_install_paths_info,  # noqa: F401
            install_desktop_assets,  # noqa: F401
            uninstall_desktop_assets,  # noqa: F401
        )
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_asset_paths():
    """Test that packaged assets can be located."""
    print("\nTesting asset paths...")
    try:
        from hei_datahub.desktop_install import _get_asset_paths

        assets = _get_asset_paths()

        print(f"  Found {len(assets)} assets:")
        for name, path in assets.items():
            # Check if path exists (in development mode)
            exists = "✓" if Path(str(path)).exists() else "?"
            print(f"    {exists} {name}: {path}")

        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_install_paths():
    """Test that install paths can be determined."""
    print("\nTesting install paths...")
    try:
        from hei_datahub.desktop_install import _get_install_paths

        paths = _get_install_paths()

        print(f"  Determined {len(paths)} install paths:")
        for name, path in paths.items():
            if name != "icons_base":
                print(f"    • {name}: {path}")

        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_status_check():
    """Test status check function."""
    print("\nTesting status check...")
    try:
        from hei_datahub.desktop_install import get_desktop_assets_status

        status = get_desktop_assets_status()

        print(f"  Platform: {status['platform']}")
        print(f"  Installed: {status['installed']}")
        print(f"  Current version: {status['current_version']}")
        print(f"  Needs update: {status['needs_update']}")

        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_paths_info():
    """Test paths info function."""
    print("\nTesting paths info...")
    try:
        from hei_datahub.desktop_install import get_install_paths_info

        info = get_install_paths_info()
        print(info)

        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Desktop Integration Smoke Test")
    print("=" * 60)

    tests = [
        test_imports,
        test_asset_paths,
        test_install_paths,
        test_status_check,
        test_paths_info,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
