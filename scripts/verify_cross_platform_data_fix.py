#!/usr/bin/env python3
"""
Verification script for Windows/macOS data seeding bug fix.

This script verifies that the v0.58.1-beta fixes are working correctly
across all platforms.

Usage:
    python scripts/verify_cross_platform_data_fix.py
"""
import os
import platform
import sys
from pathlib import Path


def get_color_codes():
    """Get ANSI color codes (works on most terminals)."""
    return {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m',
        'bold': '\033[1m',
    }


def print_header(text):
    """Print a header."""
    c = get_color_codes()
    print(f"\n{c['bold']}{c['blue']}{'=' * 70}{c['reset']}")
    print(f"{c['bold']}{c['blue']}{text.center(70)}{c['reset']}")
    print(f"{c['bold']}{c['blue']}{'=' * 70}{c['reset']}\n")


def print_success(text):
    """Print success message."""
    c = get_color_codes()
    print(f"{c['green']}✓{c['reset']} {text}")


def print_error(text):
    """Print error message."""
    c = get_color_codes()
    print(f"{c['red']}✗{c['reset']} {text}")


def print_warning(text):
    """Print warning message."""
    c = get_color_codes()
    print(f"{c['yellow']}⚠{c['reset']} {text}")


def print_info(text):
    """Print info message."""
    c = get_color_codes()
    print(f"{c['blue']}ℹ{c['reset']} {text}")


def check_platform_detection():
    """Verify platform detection works correctly."""
    print_header("Platform Detection")

    try:
        from mini_datahub.infra.platform_paths import get_os_type, get_os_default_data_dir

        os_type = get_os_type()
        default_dir = get_os_default_data_dir()

        print_info(f"Detected OS: {os_type}")
        print_info(f"Platform system: {platform.system()}")
        print_info(f"Default data directory: {default_dir}")

        # Verify OS detection matches platform
        system = platform.system().lower()
        if system == 'darwin' and os_type != 'darwin':
            print_error(f"OS detection mismatch: got {os_type}, expected darwin")
            return False
        elif system in ('windows', 'win32') and os_type != 'windows':
            print_error(f"OS detection mismatch: got {os_type}, expected windows")
            return False
        elif system not in ('darwin', 'windows', 'win32') and os_type != 'linux':
            print_error(f"OS detection mismatch: got {os_type}, expected linux")
            return False

        # Verify default directory is platform-appropriate
        if os_type == 'darwin' and 'Library/Application Support' not in str(default_dir):
            print_error("macOS default path doesn't contain 'Library/Application Support'")
            return False
        elif os_type == 'windows' and 'AppData' not in str(default_dir):
            print_error("Windows default path doesn't contain 'AppData'")
            return False
        elif os_type == 'linux' and '.local/share' not in str(default_dir):
            print_error("Linux default path doesn't contain '.local/share'")
            return False

        print_success("Platform detection working correctly")
        return True

    except Exception as e:
        print_error(f"Platform detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_data_resolution():
    """Verify data directory resolution with precedence."""
    print_header("Data Directory Resolution")

    try:
        from mini_datahub.infra.platform_paths import resolve_data_directory

        # Test 1: Default resolution
        print_info("Test 1: Default resolution (no overrides)")
        default_path, reason = resolve_data_directory()
        if reason != 'default':
            print_error(f"Expected reason 'default', got '{reason}'")
            return False
        print_success(f"Default path: {default_path}")

        # Test 2: Environment variable override
        print_info("\nTest 2: Environment variable override")
        test_env_path = "/tmp/test-env-override"
        os.environ['HEIDATAHUB_DATA_DIR'] = test_env_path
        env_path, reason = resolve_data_directory()
        if reason != 'env':
            print_error(f"Expected reason 'env', got '{reason}'")
            del os.environ['HEIDATAHUB_DATA_DIR']
            return False
        if test_env_path not in str(env_path):
            print_error(f"Expected path containing '{test_env_path}', got '{env_path}'")
            del os.environ['HEIDATAHUB_DATA_DIR']
            return False
        print_success(f"Environment override working: {env_path}")
        del os.environ['HEIDATAHUB_DATA_DIR']

        # Test 3: CLI override (highest priority)
        print_info("\nTest 3: CLI override (highest priority)")
        test_cli_path = "/tmp/test-cli-override"
        os.environ['HEIDATAHUB_DATA_DIR'] = "/tmp/should-be-overridden"
        cli_path, reason = resolve_data_directory(test_cli_path)
        if reason != 'cli':
            print_error(f"Expected reason 'cli', got '{reason}'")
            del os.environ['HEIDATAHUB_DATA_DIR']
            return False
        if test_cli_path not in str(cli_path):
            print_error(f"Expected path containing '{test_cli_path}', got '{cli_path}'")
            del os.environ['HEIDATAHUB_DATA_DIR']
            return False
        print_success(f"CLI override working: {cli_path}")
        del os.environ['HEIDATAHUB_DATA_DIR']

        print_success("\nData directory resolution working correctly")
        return True

    except Exception as e:
        print_error(f"Data resolution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_windows_filename_sanitization():
    """Verify Windows filename sanitization."""
    print_header("Windows Filename Sanitization")

    try:
        from mini_datahub.infra.platform_paths import sanitize_windows_filename

        test_cases = [
            ('test\\file', 'test_file', 'backslash removal'),
            ('test/file', 'test_file', 'forward slash removal'),
            ('test:file', 'test_file', 'colon removal'),
            ('test*file', 'test_file', 'asterisk removal'),
            ('test?file', 'test_file', 'question mark removal'),
            ('test"file', 'test_file', 'quote removal'),
            ('test<file', 'test_file', 'less-than removal'),
            ('test>file', 'test_file', 'greater-than removal'),
            ('test|file', 'test_file', 'pipe removal'),
            ('CON', 'CON_file', 'reserved name CON'),
            ('PRN', 'PRN_file', 'reserved name PRN'),
            ('AUX', 'AUX_file', 'reserved name AUX'),
            ('NUL', 'NUL_file', 'reserved name NUL'),
            ('COM1', 'COM1_file', 'reserved name COM1'),
            ('LPT1', 'LPT1_file', 'reserved name LPT1'),
            ('test.', 'test', 'trailing dot removal'),
            ('test ', 'test', 'trailing space removal'),
            ('valid-file.txt', 'valid-file.txt', 'valid filename unchanged'),
        ]

        all_passed = True
        for input_name, expected, description in test_cases:
            result = sanitize_windows_filename(input_name)
            if result == expected:
                print_success(f"{description}: '{input_name}' → '{result}'")
            else:
                print_error(f"{description}: expected '{expected}', got '{result}'")
                all_passed = False

        if all_passed:
            print_success("\nWindows filename sanitization working correctly")
        else:
            print_error("\nSome Windows filename sanitization tests failed")

        return all_passed

    except Exception as e:
        print_error(f"Windows sanitization check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_packaged_data_structure():
    """Verify packaged data structure is correct."""
    print_header("Packaged Data Structure")

    try:
        import mini_datahub
        pkg_path = Path(mini_datahub.__file__).parent

        print_info(f"Package location: {pkg_path}")

        # Check for data directory
        data_dir = pkg_path / "data"
        if not data_dir.exists():
            print_error(f"Data directory not found at {data_dir}")
            return False

        print_success(f"Data directory found: {data_dir}")

        # Expected datasets
        expected_datasets = [
            'burned-area',
            'land-cover',
            'precipitation',
            'testing-the-beta-version'
        ]

        found_datasets = []
        for item in data_dir.iterdir():
            if item.is_dir():
                found_datasets.append(item.name)
                metadata_file = item / "metadata.yaml"
                if metadata_file.exists():
                    print_success(f"  Dataset: {item.name} (has metadata.yaml)")
                else:
                    print_warning(f"  Dataset: {item.name} (missing metadata.yaml)")

        # Check if all expected datasets are present
        missing = set(expected_datasets) - set(found_datasets)
        extra = set(found_datasets) - set(expected_datasets)

        if missing:
            print_error(f"Missing datasets: {', '.join(missing)}")
            return False

        if extra:
            print_info(f"Extra datasets found: {', '.join(extra)}")

        print_success(f"\nAll {len(expected_datasets)} expected datasets present")
        return True

    except Exception as e:
        print_error(f"Package structure check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_installation_mode():
    """Check if running from installed package vs dev mode."""
    print_header("Installation Mode Detection")

    try:
        from mini_datahub.infra import paths

        is_installed = paths._is_installed_package()
        is_dev = paths._is_dev_mode()

        print_info(f"Installed package mode: {is_installed}")
        print_info(f"Development mode: {is_dev}")

        if is_installed:
            print_success("Running from installed package (expected for UV install)")
        elif is_dev:
            print_success("Running in development mode (expected when running from repo)")
        else:
            print_warning("Running in fallback mode")

        # Check paths
        print_info(f"\nCurrent paths:")
        print_info(f"  PROJECT_ROOT: {paths.PROJECT_ROOT}")
        print_info(f"  DATA_DIR: {paths.DATA_DIR}")
        print_info(f"  CONFIG_DIR: {paths.CONFIG_DIR}")

        return True

    except Exception as e:
        print_error(f"Installation mode check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    c = get_color_codes()

    print(f"\n{c['bold']}Cross-Platform Data Fix Verification (v0.58.1-beta){c['reset']}")
    print(f"Python {sys.version}")
    print(f"Platform: {platform.platform()}")

    checks = [
        ("Platform Detection", check_platform_detection),
        ("Data Directory Resolution", check_data_resolution),
        ("Windows Filename Sanitization", check_windows_filename_sanitization),
        ("Packaged Data Structure", check_packaged_data_structure),
        ("Installation Mode Detection", check_installation_mode),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Check '{name}' crashed: {e}")
            results[name] = False

    # Summary
    print_header("Verification Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")

    print(f"\n{c['bold']}Result: {passed}/{total} checks passed{c['reset']}")

    if passed == total:
        print_success("\n✅ All verification checks passed!")
        print_info("\nThe Windows/macOS data seeding bug fix appears to be working correctly.")
        return 0
    else:
        print_error(f"\n❌ {total - passed} check(s) failed")
        print_info("\nPlease review the errors above and fix any issues.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
