#!/usr/bin/env python3
"""
Quick test script to verify Phase 6A implementation works.
"""

def test_imports():
    """Test all new modules import correctly."""
    print("Testing imports...")
    from mini_datahub.version import __version__, __app_name__, GITHUB_REPO
    from mini_datahub.auto_pull import get_auto_pull_manager
    from mini_datahub.state_manager import get_state_manager
    from mini_datahub.update_checker import check_for_updates
    from mini_datahub.autocomplete import get_autocomplete_manager
    from mini_datahub.debug_console import DebugConsoleScreen
    from mini_datahub.logging_setup import setup_logging

    print(f"✓ All imports successful")
    print(f"  App: {__app_name__}")
    print(f"  Version: {__version__}")
    print(f"  Repo: {GITHUB_REPO}")


def test_version():
    """Test version management."""
    print("\nTesting version management...")
    from mini_datahub.version import __version__
    assert __version__ == "3.0.0", f"Unexpected version: {__version__}"
    print(f"✓ Version: {__version__}")


def test_state_manager():
    """Test state management."""
    print("\nTesting state manager...")
    from mini_datahub.state_manager import get_state_manager

    state = get_state_manager()

    # Reset session flags first (in case left over from previous run)
    state.reset_session_flags()

    # Test commit tracking
    state.set_last_indexed_commit("abc123")
    assert state.get_last_indexed_commit() == "abc123"
    print("✓ Commit tracking works")

    # Test session flags
    assert state.should_prompt_pull() == True
    state.set_dont_prompt_pull_this_session(True)
    assert state.should_prompt_pull() == False
    print("✓ Session flags work")

    # Test preferences
    state.set_preference("test_key", "test_value")
    assert state.get_preference("test_key") == "test_value"
    print("✓ Preferences work")


def test_autocomplete():
    """Test autocomplete manager."""
    print("\nTesting autocomplete...")
    from mini_datahub.autocomplete import get_autocomplete_manager

    manager = get_autocomplete_manager()

    # Add some test data
    manager.projects.add("Project A")
    manager.projects.add("Project B")
    manager.data_types.add("tabular")
    manager.file_formats.add("csv")

    # Test suggestions
    projects = manager.suggest_projects("proj", limit=5)
    assert len(projects) == 2, f"Expected 2 projects, got {len(projects)}"
    print(f"✓ Project suggestions: {projects}")

    # Test normalization
    normalized = manager.normalize_data_type("TimeSeries")
    assert normalized == "time-series", f"Expected 'time-series', got '{normalized}'"
    print("✓ Data type normalization works")


def test_auto_pull():
    """Test auto-pull manager."""
    print("\nTesting auto-pull...")
    from mini_datahub.auto_pull import get_auto_pull_manager
    from mini_datahub.config import get_github_config
    from pathlib import Path

    config = get_github_config()

    if not config.catalog_repo_path:
        print("⚠ Catalog path not configured, skipping auto-pull test")
        return

    # Create manager with catalog path
    manager = get_auto_pull_manager(Path(config.catalog_repo_path))
    assert manager.catalog_path == Path(config.catalog_repo_path).expanduser()
    print(f"✓ AutoPullManager created with path: {manager.catalog_path}")

    # Test network check (may fail if offline, that's ok)
    try:
        has_network = manager.check_network_available()
        print(f"✓ Network check works (result: {has_network})")
    except Exception:
        print("✓ Network check works (no network available)")


def test_logging():
    """Test logging setup."""
    print("\nTesting logging...")
    from mini_datahub.logging_setup import setup_logging, log_startup
    from pathlib import Path

    # Setup logging
    logger = setup_logging(debug=True)
    log_startup("3.0.0-test")

    # Check log file exists
    log_file = Path.home() / ".mini-datahub" / "logs" / "datahub.log"
    assert log_file.exists(), "Log file not created"
    print(f"✓ Log file created: {log_file}")

    # Check log content
    with open(log_file, 'r') as f:
        content = f.read()
        assert "Application started" in content, "Startup log not found"
    print("✓ Logging works")


def test_update_checker():
    """Test update checker."""
    print("\nTesting update checker...")
    from mini_datahub.update_checker import parse_version, format_update_message

    # Test version parsing
    v1 = parse_version("3.0.0")
    v2 = parse_version("v3.1.0")
    v3 = parse_version("2.9.0")

    assert v1 == (3, 0, 0), f"Expected (3, 0, 0), got {v1}"
    assert v2 == (3, 1, 0), f"Expected (3, 1, 0), got {v2}"
    assert v3 == (2, 9, 0), f"Expected (2, 9, 0), got {v3}"
    print("✓ Version parsing works")

    # Test comparison
    assert v2 > v1, "Version comparison failed"
    assert v1 > v3, "Version comparison failed"
    print("✓ Version comparison works")

    # Test message formatting
    update_info = {
        "has_update": True,
        "current_version": "3.0.0",
        "latest_version": "3.1.0",
        "release_url": "https://github.com/0xpix/Hei-DataHub/releases/tag/v3.1.0"
    }
    message = format_update_message(update_info)
    assert "3.1.0" in message, "Version not in message"
    assert "3.0.0" in message, "Current version not in message"
    print("✓ Message formatting works")


def test_config_extensions():
    """Test config extensions."""
    print("\nTesting config extensions...")
    from mini_datahub.config import get_github_config

    config = get_github_config()

    # Test new fields exist
    assert hasattr(config, "auto_check_updates")
    assert hasattr(config, "suggest_from_catalog_values")
    assert hasattr(config, "background_fetch_interval_minutes")
    assert hasattr(config, "debug_logging")
    print("✓ Config has new fields")

    # Test default values
    assert config.auto_check_updates == True
    assert config.suggest_from_catalog_values == True
    assert config.background_fetch_interval_minutes == 0
    assert config.debug_logging == False
    print("✓ Default values correct")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 6A Implementation Test Suite")
    print("=" * 60)

    try:
        test_imports()
        test_version()
        test_state_manager()
        test_autocomplete()
        test_auto_pull()
        test_logging()
        test_update_checker()
        test_config_extensions()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPhase 6A implementation is working correctly!")
        print("\nNext steps:")
        print("1. Try running: uv run mini-datahub")
        print("2. Press : to open debug console")
        print("3. Type 'version' to see app info")
        print("4. Press U to test pull (if you have a catalog repo)")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
