"""
Tests for auth doctor command.

Test various scenarios including config missing, auth failures, network errors, and JSON output.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

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
"""
    mock_config_path.write_text(config_content)
    return mock_config_path


class TestAuthDoctor:
    """Test cases for auth doctor command."""

    @patch("mini_datahub.auth.doctor.platform.system")
    def test_non_linux_platform(self, mock_platform):
        """Test that doctor fails on non-Linux platforms."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Windows"
        exit_code = run_doctor()

        assert exit_code == 2

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    def test_config_missing(self, mock_get_config_path, mock_platform, mock_config_path):
        """Test when config file doesn't exist."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_path  # File doesn't exist

        exit_code = run_doctor()

        assert exit_code == 2  # Config issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    def test_config_missing_auth_section(self, mock_get_config_path, mock_platform, mock_config_path):
        """Test when config file exists but has no [auth] section."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_path

        # Create config without auth section
        mock_config_path.write_text("[other]\nkey = 'value'\n")

        exit_code = run_doctor()

        assert exit_code == 2  # Config issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    def test_credentials_not_found(self, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test when credentials are not found in keyring/env."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock auth store that returns None for credentials
        mock_store = Mock()
        mock_store.load_secret.return_value = None
        mock_get_auth_store.return_value = mock_store

        exit_code = run_doctor()

        assert exit_code == 2  # Config/credential issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("socket.gethostbyname")
    def test_dns_resolution_failure(self, mock_gethostbyname, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test DNS resolution failure."""
        from mini_datahub.auth.doctor import run_doctor
        import socket

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock credentials present
        mock_store = Mock()
        mock_store.load_secret.return_value = "test_token_abcd1234"
        mock_get_auth_store.return_value = mock_store

        # Mock DNS failure
        mock_gethostbyname.side_effect = socket.gaierror("DNS resolution failed")

        exit_code = run_doctor()

        assert exit_code == 5  # Network issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("socket.gethostbyname")
    @patch("socket.socket")
    @patch("requests.Session")
    def test_webdav_auth_401(self, mock_session_class, mock_socket_class, mock_gethostbyname, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test WebDAV authentication failure (401)."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock credentials present
        mock_store = Mock()
        mock_store.load_secret.return_value = "test_token_abcd1234"
        mock_get_auth_store.return_value = mock_store

        # Mock DNS success
        mock_gethostbyname.return_value = "1.2.3.4"

        # Mock socket connection success
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        # Mock WebDAV auth failure
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        exit_code = run_doctor()

        assert exit_code == 3  # Auth issue

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("socket.gethostbyname")
    @patch("socket.socket")
    @patch("requests.Session")
    def test_webdav_auth_success_skip_write(self, mock_session_class, mock_socket_class, mock_gethostbyname, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test successful WebDAV auth with --no-write flag."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock credentials present
        mock_store = Mock()
        mock_store.load_secret.return_value = "test_token_abcd1234"
        mock_get_auth_store.return_value = mock_store

        # Mock DNS success
        mock_gethostbyname.return_value = "1.2.3.4"

        # Mock socket connection success
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        # Mock WebDAV auth success
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 207
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        exit_code = run_doctor(skip_write=True)

        assert exit_code == 0  # Success

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("socket.gethostbyname")
    @patch("socket.socket")
    @patch("requests.Session")
    def test_webdav_auth_success_with_write(self, mock_session_class, mock_socket_class, mock_gethostbyname, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test successful WebDAV auth with write permission check."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock credentials present
        mock_store = Mock()
        mock_store.load_secret.return_value = "test_token_abcd1234"
        mock_get_auth_store.return_value = mock_store

        # Mock DNS success
        mock_gethostbyname.return_value = "1.2.3.4"

        # Mock socket connection success
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        # Mock WebDAV auth success and write success
        mock_session = Mock()

        def mock_request_side_effect(method, url, **kwargs):
            response = Mock()
            if method == "PROPFIND":
                response.status_code = 207
            elif method == "PUT":
                response.status_code = 201
            elif method == "DELETE":
                response.status_code = 204
            return response

        mock_session.request.side_effect = mock_request_side_effect
        mock_session.put.return_value = Mock(status_code=201)
        mock_session.delete.return_value = Mock(status_code=204)
        mock_session_class.return_value = mock_session

        exit_code = run_doctor(skip_write=False)

        assert exit_code == 0  # Success

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("socket.gethostbyname")
    @patch("socket.socket")
    @patch("requests.Session")
    def test_json_output(self, mock_session_class, mock_socket_class, mock_gethostbyname, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth, capsys):
        """Test JSON output format."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock credentials present
        mock_store = Mock()
        mock_store.load_secret.return_value = "test_token_abcd1234"
        mock_get_auth_store.return_value = mock_store

        # Mock DNS success
        mock_gethostbyname.return_value = "1.2.3.4"

        # Mock socket connection success
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        # Mock WebDAV auth success
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 207
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        exit_code = run_doctor(output_json=True, skip_write=True)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert exit_code == 0
        assert "config_found" in output
        assert "creds_present" in output
        assert "webdav_status" in output
        assert "overall" in output
        assert output["overall"] == "PASS"

    @patch("mini_datahub.auth.doctor.platform.system")
    @patch("mini_datahub.infra.config_paths.get_config_path")
    @patch("mini_datahub.auth.credentials.get_auth_store")
    @patch("socket.gethostbyname")
    @patch("socket.socket")
    @patch("requests.Session")
    def test_permission_denied(self, mock_session_class, mock_socket_class, mock_gethostbyname, mock_get_auth_store, mock_get_config_path, mock_platform, mock_config_with_auth):
        """Test write permission denied."""
        from mini_datahub.auth.doctor import run_doctor

        mock_platform.return_value = "Linux"
        mock_get_config_path.return_value = mock_config_with_auth

        # Mock credentials present
        mock_store = Mock()
        mock_store.load_secret.return_value = "test_token_abcd1234"
        mock_get_auth_store.return_value = mock_store

        # Mock DNS success
        mock_gethostbyname.return_value = "1.2.3.4"

        # Mock socket connection success
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        # Mock WebDAV auth success but write failure
        mock_session = Mock()

        def mock_request_side_effect(method, url, **kwargs):
            response = Mock()
            if method == "PROPFIND":
                response.status_code = 207
            return response

        mock_session.request.side_effect = mock_request_side_effect
        mock_session.put.return_value = Mock(status_code=403)
        mock_session_class.return_value = mock_session

        exit_code = run_doctor(skip_write=False)

        assert exit_code == 4  # Permission issue
