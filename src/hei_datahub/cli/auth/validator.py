"""
WebDAV credential validation client.

Linux-only HTTP client for testing WebDAV credentials.
"""
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


ValidationResult = tuple[bool, str, int]  # (success, message, status_code)


class WebDAVValidator:
    """Validates WebDAV credentials by attempting authentication."""

    def __init__(self, url: str, username: Optional[str], credential: str, timeout: int = 8):
        """
        Initialize validator.

        Args:
            url: WebDAV endpoint URL
            username: Username (required for Seafile/WebDAV)
            credential: API token or WebDAV password
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip("/")
        self.username = username
        self.credential = credential
        self.timeout = timeout
        self.session = requests.Session()

        # Seafile WebDAV authentication:
        # - With username: Basic Auth (username, token/password)
        # - Without username: Token header (rare, for API tokens only)
        if username:
            # Standard: Basic Auth with username + (token OR password)
            self.session.auth = (username, credential)
        else:
            # Alternative: Token-only auth via custom header
            self.session.headers["Authorization"] = f"Token {credential}"

    def validate(self) -> ValidationResult:
        """
        Validate credentials by attempting HEAD or PROPFIND request.

        Returns:
            Tuple of (success: bool, message: str, status_code: int)
        """
        # Try HEAD first
        success, message, status = self._try_head()

        if success:
            return (True, message, status)

        # If HEAD unsupported (405/501), try PROPFIND
        if status in (405, 501):
            logger.info("HEAD unsupported, trying PROPFIND")
            return self._try_propfind()

        # Other errors
        return (False, message, status)

    def _try_head(self) -> ValidationResult:
        """Try HEAD request."""
        try:
            response = self.session.head(
                self.url,
                timeout=self.timeout,
                verify=True,  # Always verify TLS
                allow_redirects=True
            )

            if response.status_code == 200:
                return (True, "✅ WebDAV credentials verified.", 200)
            elif response.status_code in (401, 403):
                return (False, "Invalid credentials or insufficient permissions.", response.status_code)
            elif response.status_code == 404:
                return (False, "Server path not found (check the URL).", 404)
            elif response.status_code in (405, 501):
                # HEAD unsupported, will retry with PROPFIND
                return (False, "HEAD unsupported.", response.status_code)
            elif 500 <= response.status_code < 600:
                return (False, "Server error; try again later.", response.status_code)
            else:
                return (False, f"Unexpected status: {response.status_code}", response.status_code)

        except requests.exceptions.Timeout:
            return (False, "Request timed out; check connectivity.", 0)
        except requests.exceptions.SSLError as e:
            return (False, f"TLS/SSL error: {str(e)}", 0)
        except requests.exceptions.ConnectionError as e:
            return (False, f"Connection error: {str(e)}", 0)
        except Exception as e:
            return (False, f"Validation error: {str(e)}", 0)

    def _try_propfind(self) -> ValidationResult:
        """Try PROPFIND request with Depth: 0."""
        try:
            response = self.session.request(
                "PROPFIND",
                self.url,
                headers={"Depth": "0"},
                timeout=self.timeout,
                verify=True,
                allow_redirects=True
            )

            if response.status_code == 207:  # Multi-Status (WebDAV success)
                return (True, "✅ WebDAV credentials verified (via PROPFIND).", 207)
            elif response.status_code == 200:
                return (True, "✅ WebDAV credentials verified.", 200)
            elif response.status_code in (401, 403):
                return (False, "Invalid credentials or insufficient permissions.", response.status_code)
            elif response.status_code == 404:
                return (False, "Server path not found (check the URL).", 404)
            elif 500 <= response.status_code < 600:
                return (False, "Server error; try again later.", response.status_code)
            else:
                return (False, f"Unexpected status: {response.status_code}", response.status_code)

        except requests.exceptions.Timeout:
            return (False, "Request timed out; check connectivity.", 0)
        except requests.exceptions.SSLError as e:
            return (False, f"TLS/SSL error: {str(e)}", 0)
        except requests.exceptions.ConnectionError as e:
            return (False, f"Connection error: {str(e)}", 0)
        except Exception as e:
            return (False, f"Validation error: {str(e)}", 0)


def validate_credentials(
    url: str,
    username: Optional[str],
    credential: str,
    timeout: int = 8
) -> ValidationResult:
    """
    Validate WebDAV credentials.

    Args:
        url: WebDAV endpoint URL
        username: Username (optional for token auth)
        credential: Token or password
        timeout: Request timeout in seconds

    Returns:
        Tuple of (success, message, status_code)
    """
    validator = WebDAVValidator(url, username, credential, timeout)
    return validator.validate()
