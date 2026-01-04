"""
Tests for auth clear command.

Test interactive/force modes, keyring/env clearing, and edge cases.
"""
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

import pytest


@pytest.fixture
def mock_config_path(tmp_path):
    """Create a temporary config path."""
    config_dir = tmp_path / ".config" / "hei-datahub"
    config_dir.mkdir(parents=True)
    return config_dir / "config.toml"


@pytest.fixture
def mock_config_with_auth(mock_config_path):
    """Create a config file with auth section."""
    config_content = """
[auth]
method = "token"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "testuser"
key_id = "webdav:token:testuser@heibox.uni-heidelberg.de"
stored_in = "keyring"

[other]
some_setting = "value"
"""
    mock_config_path.write_text(config_content)
    return mock_config_path


@pytest.fixture
def mock_config_without_auth(mock_config_path):
    """Create a config file without auth section."""
    config_content = """
[other]
some_setting = "value"
"""
    mock_config_path.write_text(config_content)
    return mock_config_path


class TestAuthClear:
    """Test cases for auth clear command."""

    @patch("hei_datahub.auth.clear.platform.system")
    def test_non_linux_platform(self, mock_platform):
        """Test that clear fails on non-Linux platforms."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Windows"
        exit_code = run_clear()

        assert exit_code == 2

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    def test_no_config_file(self, mock_get_config_path, mock_platform, mock_config_path, capsys):
        """Test when config file doesn't exist."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_path  # File doesn't exist

        exit_code = run_clear()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Nothing to clear" in captured.out

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    def test_no_auth_section(self, mock_get_config_path, mock_platform, mock_config_without_auth, capsys):
        """Test when config exists but has no [auth] section."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_without_auth

        exit_code = run_clear()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Nothing to clear" in captured.out

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    @patch("builtins.input")
    def test_interactive_cancel(self, mock_input, mock_get_config_path, mock_platform, mock_config_with_auth, capsys):
        """Test interactive mode with user cancelling."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth
        mock_input.return_value = "n"  # User says no

        exit_code = run_clear(force=False)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Cancelled" in captured.out

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    @patch("builtins.input")
    @patch("keyring.delete_password")
    def test_interactive_confirm_keyring(self, mock_delete_password, mock_input, mock_get_config_path, mock_platform, mock_config_with_auth, capsys):
        """Test interactive mode with user confirming and keyring storage."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth
        mock_input.return_value = "y"  # User confirms

        exit_code = run_clear(force=False)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "✅ Cleared WebDAV credentials" in captured.out

        # Verify keyring delete was called
        mock_delete_password.assert_called_once()

        # Verify auth section was removed from config
        try:
            import tomllib as tomli
        except ImportError:
            import tomli

        with open(mock_config_with_auth, "rb") as f:
            config = tomli.load(f)

        assert "auth" not in config
        assert "other" in config  # Other sections preserved

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    @patch("keyring.delete_password")
    def test_force_mode_keyring(self, mock_delete_password, mock_get_config_path, mock_platform, mock_config_with_auth, capsys):
        """Test force mode (no prompt) with keyring storage."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        exit_code = run_clear(force=True)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "✅ Cleared WebDAV credentials" in captured.out
        assert "Are you sure" not in captured.out  # No prompt

        # Verify keyring delete was called
        mock_delete_password.assert_called_once()

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    def test_env_storage(self, mock_get_config_path, mock_platform, mock_config_path, capsys):
        """Test clearing with ENV storage (should show warning)."""
        from hei_datahub.auth.clear import run_clear

        # Create config with env storage
        config_content = """
[auth]
method = "token"
url = "https://heibox.uni-heidelberg.de/seafdav"
username = "testuser"
key_id = "webdav:token:testuser@heibox.uni-heidelberg.de"
stored_in = "env"
"""
        mock_config_path.write_text(config_content)

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_path

        exit_code = run_clear(force=True)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "✅ Cleared WebDAV credentials" in captured.out
        assert "Remove environment variable manually" in captured.out

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    @patch("hei_datahub.infra.config_paths.get_user_config_dir")
    @patch("keyring.delete_password")
    def test_clear_all_flag(self, mock_delete_password, mock_get_user_config_dir, mock_get_config_path, mock_platform, mock_config_with_auth, tmp_path, capsys):
        """Test --all flag to clear cached session files."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Create mock cache directory with some files
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "session_token.cache").touch()
        (cache_dir / "etag_cache.etag").touch()
        (cache_dir / "normal_file.txt").touch()

        mock_get_user_config_dir.return_value = cache_dir

        exit_code = run_clear(force=True, clear_all=True)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "✅ Cleared WebDAV credentials" in captured.out
        assert "Removed" in captured.out and "cached file(s)" in captured.out

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    @patch("keyring.delete_password")
    def test_keyring_delete_failure(self, mock_delete_password, mock_get_config_path, mock_platform, mock_config_with_auth, capsys):
        """Test graceful handling when keyring delete fails."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Make keyring delete fail
        mock_delete_password.side_effect = Exception("Keyring error")

        exit_code = run_clear(force=True)

        # Should still succeed (just log warning)
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "✅ Cleared WebDAV credentials" in captured.out

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    @patch("builtins.input")
    @patch("keyring.delete_password")
    def test_preserve_other_config_sections(self, mock_delete_password, mock_input, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test that other config sections are preserved after clearing auth."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth
        mock_input.return_value = "y"

        exit_code = run_clear(force=False)

        assert exit_code == 0

        # Verify other sections are preserved
        try:
            import tomllib as tomli
        except ImportError:
            import tomli

        with open(mock_config_with_auth, "rb") as f:
            config = tomli.load(f)

        assert "auth" not in config
        assert "other" in config
        assert config["other"]["some_setting"] == "value"

    @patch("hei_datahub.auth.clear.platform.system")
    @patch("hei_datahub.infra.config_paths.get_config_path")
    def test_idempotent(self, mock_get_config_path, mock_platform, mock_config_with_auth, capsys):
        """Test that running clear multiple times is safe (idempotent)."""
        from hei_datahub.auth.clear import run_clear

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # First clear
        exit_code1 = run_clear(force=True)
        assert exit_code1 == 0

        # Second clear (nothing to clear now)
        exit_code2 = run_clear(force=True)
        assert exit_code2 == 0

        captured = capsys.readouterr()
        assert "Nothing to clear" in captured.out
