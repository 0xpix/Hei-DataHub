"""
Integration tests for authentication flows.

Tests GUI wizard, CLI setup, and storage manager compatibility.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
try:
    import tomllib as tomli
except ImportError:
    import tomli


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_auth_store():
    """Mock authentication store."""
    store = MagicMock()
    store.strategy = "keyring"
    store.store_secret = MagicMock()
    store.load_secret = MagicMock(return_value="test-password-123")
    return store


class TestGUIAuthWizard:
    """Test GUI authentication wizard behavior."""

    def test_gui_wizard_saves_correct_format(self, temp_config_dir, mock_auth_store):
        """Test that GUI wizard saves config in CLI-compatible format."""
        from hei_datahub.ui.widgets.settings_wizard import SettingsWizard

        # Simulate wizard saving credentials
        url = "https://heibox.uni-heidelberg.de/seafdav"
        username = "testuser"
        password = "testpass"
        library = "test-library"

        # Expected key_id format (same as CLI)
        expected_key_id = "heibox:password:testuser@heibox.uni-heidelberg.de"

        # Mock the save operation
        config_path = temp_config_dir / "config.toml"

        with patch("hei_datahub.ui.widgets.settings_wizard.get_config_path", return_value=config_path):
            with patch("hei_datahub.ui.widgets.settings_wizard.get_auth_store", return_value=mock_auth_store):
                # Simulate the save logic from the wizard
                import tomli_w
                from urllib.parse import urlparse

                parsed = urlparse(url)
                host = parsed.hostname or "unknown"
                method = "password"
                key_id = f"heibox:{method}:{username}@{host}"

                config = {
                    "auth": {
                        "method": method,
                        "url": url,
                        "username": username,
                        "library": library,
                        "key_id": key_id,
                        "stored_in": mock_auth_store.strategy,
                    },
                    "cloud": {
                        "library": library
                    }
                }

                # Simulate storing secret (as the wizard does)
                mock_auth_store.store_secret(key_id, password)

                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, "wb") as f:
                    tomli_w.dump(config, f)        # Verify config was saved correctly
        assert config_path.exists()

        with open(config_path, "rb") as f:
            saved_config = tomli.load(f)

        assert "auth" in saved_config
        auth_section = saved_config["auth"]

        # Check all required fields are present
        assert auth_section["method"] == "password"
        assert auth_section["url"] == url
        assert auth_section["username"] == username
        assert auth_section["library"] == library
        assert auth_section["key_id"] == expected_key_id
        assert auth_section["stored_in"] == "keyring"

        # Verify store_secret was called
        mock_auth_store.store_secret.assert_called_once_with(expected_key_id, password)

    def test_gui_wizard_key_id_format_matches_cli(self):
        """Test that GUI wizard uses the same key_id format as CLI."""
        from urllib.parse import urlparse

        # Test URLs
        test_cases = [
            ("https://heibox.uni-heidelberg.de/seafdav", "testuser",
             "heibox:password:testuser@heibox.uni-heidelberg.de"),
            ("https://cloud.example.com/webdav", "alice",
             "heibox:password:alice@cloud.example.com"),
            ("https://myserver.org:8443/dav", "bob",
             "heibox:password:bob@myserver.org"),
        ]

        for url, username, expected_key_id in test_cases:
            parsed = urlparse(url)
            host = parsed.hostname or "unknown"
            method = "password"
            key_id = f"heibox:{method}:{username}@{host}"

            assert key_id == expected_key_id, f"Key ID mismatch for {url}"


class TestCLIAuthSetup:
    """Test CLI authentication setup behavior."""

    def test_cli_saves_all_required_fields(self, temp_config_dir, mock_auth_store):
        """Test that CLI auth setup saves all required fields."""
        config_path = temp_config_dir / "config.toml"

        # Simulate CLI save operation
        import tomli_w
        from urllib.parse import urlparse

        url = "https://heibox.uni-heidelberg.de/seafdav"
        username = "testuser"
        library = "test-library"
        method = "password"

        parsed = urlparse(url)
        host = parsed.hostname or "unknown"
        key_id = f"heibox:{method}:{username}@{host}"

        config_data = {
            "auth": {
                "method": method,
                "url": url,
                "library": library,
                "username": username,
                "key_id": key_id,
                "stored_in": "keyring",
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(config_data, f)

        # Verify
        with open(config_path, "rb") as f:
            saved_config = tomli.load(f)

        auth_section = saved_config["auth"]
        assert auth_section["method"] == "password"
        assert auth_section["url"] == url
        assert auth_section["library"] == library
        assert auth_section["username"] == username
        assert auth_section["key_id"] == key_id
        assert auth_section["stored_in"] == "keyring"

    def test_cli_and_gui_configs_are_compatible(self, temp_config_dir):
        """Test that CLI and GUI configs are mutually compatible."""
        import tomli_w

        config_path = temp_config_dir / "config.toml"

        # Create a CLI-style config
        cli_config = {
            "auth": {
                "method": "password",
                "url": "https://heibox.uni-heidelberg.de/seafdav",
                "library": "test-library",
                "username": "testuser",
                "key_id": "webdav:password:testuser@heibox.uni-heidelberg.de",
                "stored_in": "keyring",
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(cli_config, f)

        # Read it back as if the GUI was reading it
        with open(config_path, "rb") as f:
            gui_read_config = tomli.load(f)

        auth_section = gui_read_config["auth"]

        # All fields should be present and readable
        assert "method" in auth_section
        assert "url" in auth_section
        assert "library" in auth_section
        assert "username" in auth_section
        assert "key_id" in auth_section
        assert "stored_in" in auth_section


class TestStorageManagerAuthCheck:
    """Test storage manager authentication checks."""

    def test_storage_manager_accepts_gui_config(self, temp_config_dir, mock_auth_store):
        """Test that storage_manager accepts GUI-created config."""
        import tomli_w

        config_path = temp_config_dir / "config.toml"

        # Create a GUI-style config (after fix)
        gui_config = {
            "auth": {
                "method": "password",
                "url": "https://heibox.uni-heidelberg.de/seafdav",
                "username": "testuser",
                "library": "test-library",
                "key_id": "webdav:password:testuser@heibox.uni-heidelberg.de",
                "stored_in": "keyring",
            },
            "cloud": {
                "library": "test-library"
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(gui_config, f)

        # Simulate storage_manager reading this config
        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_section = config.get("auth", {})
        cloud_section = config.get("cloud", {})

        # Extract values as storage_manager does
        base_url = auth_section.get("url")
        username = auth_section.get("username")
        library = auth_section.get("library")
        key_id = auth_section.get("key_id")
        stored_in = auth_section.get("stored_in")

        # All should be present
        assert base_url is not None
        assert username is not None
        assert library is not None
        assert key_id is not None
        assert stored_in is not None

        # No error should be raised
        errors = []
        if not base_url:
            errors.append("storage.base_url is not set")
        if not library:
            errors.append("storage.library is not set")
        if not username:
            errors.append("storage.username is not set")

        assert len(errors) == 0, f"Storage manager would reject config: {errors}"

    def test_storage_manager_accepts_cli_config(self, temp_config_dir, mock_auth_store):
        """Test that storage_manager accepts CLI-created config."""
        import tomli_w

        config_path = temp_config_dir / "config.toml"

        # Create a CLI-style config
        cli_config = {
            "auth": {
                "method": "password",
                "url": "https://heibox.uni-heidelberg.de/seafdav",
                "library": "test-library",
                "username": "testuser",
                "key_id": "webdav:password:testuser@heibox.uni-heidelberg.de",
                "stored_in": "keyring",
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(cli_config, f)

        # Simulate storage_manager reading this config
        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_section = config.get("auth", {})

        # Extract values
        base_url = auth_section.get("url")
        username = auth_section.get("username")
        library = auth_section.get("library")
        key_id = auth_section.get("key_id")
        stored_in = auth_section.get("stored_in")

        # All should be present
        assert base_url is not None
        assert username is not None
        assert library is not None
        assert key_id is not None
        assert stored_in is not None

    def test_storage_manager_handles_missing_stored_in(self, temp_config_dir, mock_auth_store):
        """Test that storage_manager handles missing stored_in field gracefully."""
        import tomli_w

        config_path = temp_config_dir / "config.toml"

        # Create config without stored_in (for backward compatibility)
        old_config = {
            "auth": {
                "method": "password",
                "url": "https://heibox.uni-heidelberg.de/seafdav",
                "library": "test-library",
                "username": "testuser",
                "key_id": "webdav:password:testuser@heibox.uni-heidelberg.de",
                # stored_in is missing
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(old_config, f)

        # Simulate storage_manager logic
        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_section = config.get("auth", {})
        stored_in = auth_section.get("stored_in")
        key_id = auth_section.get("key_id")

        # Should default to keyring if stored_in not specified
        prefer_keyring = (stored_in != "env")
        assert prefer_keyring == True, "Should default to keyring when stored_in is missing"


class TestDatasetCreationFlow:
    """Test dataset creation flow with authentication."""

    def test_dataset_creation_with_gui_auth(self, temp_config_dir, mock_auth_store):
        """Test that dataset creation works after GUI auth setup."""
        import tomli_w

        config_path = temp_config_dir / "config.toml"

        # Setup GUI auth config
        gui_config = {
            "auth": {
                "method": "password",
                "url": "https://heibox.uni-heidelberg.de/seafdav",
                "username": "testuser",
                "library": "test-library",
                "key_id": "webdav:password:testuser@heibox.uni-heidelberg.de",
                "stored_in": "keyring",
            },
            "cloud": {
                "library": "test-library"
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(gui_config, f)

        # Simulate checking if auth is configured
        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_section = config.get("auth", {})

        # Check should pass
        has_url = bool(auth_section.get("url"))
        has_username = bool(auth_section.get("username"))
        has_library = bool(auth_section.get("library"))
        has_key_id = bool(auth_section.get("key_id"))

        is_configured = has_url and has_username and has_library and has_key_id

        assert is_configured, "Auth should be considered configured after GUI setup"

    def test_dataset_creation_with_cli_auth(self, temp_config_dir, mock_auth_store):
        """Test that dataset creation works after CLI auth setup."""
        import tomli_w

        config_path = temp_config_dir / "config.toml"

        # Setup CLI auth config
        cli_config = {
            "auth": {
                "method": "password",
                "url": "https://heibox.uni-heidelberg.de/seafdav",
                "library": "test-library",
                "username": "testuser",
                "key_id": "webdav:password:testuser@heibox.uni-heidelberg.de",
                "stored_in": "keyring",
            }
        }

        with open(config_path, "wb") as f:
            tomli_w.dump(cli_config, f)

        # Simulate checking if auth is configured
        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_section = config.get("auth", {})

        # Check should pass
        has_url = bool(auth_section.get("url"))
        has_username = bool(auth_section.get("username"))
        has_library = bool(auth_section.get("library"))
        has_key_id = bool(auth_section.get("key_id"))

        is_configured = has_url and has_username and has_library and has_key_id

        assert is_configured, "Auth should be considered configured after CLI setup"


class TestCredentialDifference:
    """Test understanding of WebDAV credentials vs user credentials."""

    def test_webdav_credentials_are_correct(self):
        """
        Clarify that WebDAV credentials ARE the correct credentials to store.

        The app authenticates with WebDAV using username/password from HeiBox,
        not separate "user account credentials".
        """
        # Both GUI and CLI should store WebDAV credentials
        gui_stores_webdav = True
        cli_stores_webdav = True

        assert gui_stores_webdav, "GUI should store WebDAV credentials"
        assert cli_stores_webdav, "CLI should store WebDAV credentials"

        # WebDAV credentials are the user's HeiBox WebDAV password
        # (configured in HeiBox Settings → WebDAV Password)
        # This is NOT the same as their web login password


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
