"""
WebDAV storage backend implementation for Seafile/Heibox integration.

Uses standard HTTP methods for WebDAV operations (PROPFIND, GET, PUT, MKCOL).
Credentials are read from environment variables for security.
"""
import logging
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote, urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes and Exceptions
# =============================================================================

@dataclass
class FileEntry:
    """Represents a file or directory entry in storage."""
    name: str
    path: str  # Full path relative to storage root
    is_dir: bool
    size: Optional[int] = None  # Size in bytes (None for directories)
    modified: Optional[datetime] = None  # Last modified timestamp
    content_type: Optional[str] = None  # MIME type (optional)

    def __str__(self) -> str:
        """Human-readable representation."""
        type_icon = "📁" if self.is_dir else "📄"
        size_str = self._format_size() if self.size else ""
        return f"{type_icon} {self.name} {size_str}"

    def _format_size(self) -> str:
        """Format file size in human-readable format."""
        if self.size is None:
            return ""

        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(self.size)
        unit_idx = 0

        while size >= 1024 and unit_idx < len(units) - 1:
            size /= 1024
            unit_idx += 1

        if unit_idx == 0:
            return f"{int(size)} {units[unit_idx]}"
        return f"{size:.1f} {units[unit_idx]}"


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class StorageAuthError(StorageError):
    """Authentication failed (401/403)."""
    pass


class StorageNotFoundError(StorageError):
    """Resource not found (404)."""
    pass


class StorageConnectionError(StorageError):
    """Connection/network error."""
    pass


# =============================================================================
# WebDAV Storage Implementation
# =============================================================================

def _mask_auth(url: str) -> str:
    """Mask authentication info in URLs for logging."""
    parsed = urlparse(url)
    if parsed.username:
        # Replace username:password@ with ***:***@
        return url.replace(f"{parsed.username}:{parsed.password}@", "***:***@")
    return url


class WebDAVStorage:
    """WebDAV storage backend for Seafile/Heibox."""

    # WebDAV XML namespaces
    NS = {
        "d": "DAV:",
        "s": "http://sabredav.org/ns",
    }

    def __init__(
        self,
        base_url: str,
        library: str,
        username: str,
        password: str,
        connect_timeout: int = 5,
        read_timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize WebDAV storage backend.

        Args:
            base_url: Base WebDAV URL (e.g., https://heibox.uni-heidelberg.de/seafdav)
            library: Library/folder name (e.g., testing-hei-datahub)
            username: WebDAV username
            password: WebDAV password/token
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            max_retries: Max retry attempts on 5xx errors
        """
        self.base_url = base_url.rstrip("/")
        self.library = library.strip("/")
        self.username = username
        self.password = password
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

        # Build full base path: base_url/library
        self.root_url = f"{self.base_url}/{self.library}"

        # Setup session with retry logic
        self.session = requests.Session()
        self.session.auth = (username, password)

        # Retry strategy for 5xx errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "PROPFIND"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        logger.info(f"WebDAV storage initialized: {_mask_auth(self.root_url)}")

    def _get_url(self, path: str) -> str:
        """Build full URL for a given path."""
        # Normalize path (remove leading slash)
        path = path.lstrip("/")
        # URL-encode path components
        encoded_path = "/".join(quote(part, safe="") for part in path.split("/"))
        return f"{self.root_url}/{encoded_path}" if encoded_path else self.root_url

    def listdir(self, path: str = "") -> List[FileEntry]:
        """
        List directory contents using WebDAV PROPFIND.

        Args:
            path: Path relative to library root

        Returns:
            Sorted list of FileEntry objects (directories first)
        """
        url = self._get_url(path)

        # WebDAV PROPFIND request
        headers = {
            "Depth": "1",  # Only immediate children
            "Content-Type": "application/xml; charset=utf-8",
        }

        # Request specific properties
        propfind_xml = """<?xml version="1.0" encoding="utf-8"?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:resourcetype/>
    <d:getcontentlength/>
    <d:getlastmodified/>
    <d:getcontenttype/>
  </d:prop>
</d:propfind>"""

        try:
            logger.debug(f"PROPFIND {_mask_auth(url)}")
            response = self.session.request(
                "PROPFIND",
                url,
                data=propfind_xml.encode("utf-8"),
                headers=headers,
                timeout=(self.connect_timeout, self.read_timeout),
            )

            if response.status_code == 401:
                raise StorageAuthError("Authentication failed. Check HEIBOX_USERNAME and HEIBOX_WEBDAV_TOKEN.")
            elif response.status_code == 403:
                raise StorageAuthError("Access forbidden. Check permissions for this library.")
            elif response.status_code == 404:
                raise StorageNotFoundError(f"Path not found: {path}")
            elif response.status_code == 207:
                # Multi-Status response - parse XML
                return self._parse_propfind_response(response.text, path)
            else:
                response.raise_for_status()
                return []

        except requests.exceptions.Timeout:
            raise StorageConnectionError(f"Request timeout for {_mask_auth(url)}")
        except requests.exceptions.ConnectionError as e:
            raise StorageConnectionError(f"Connection failed: {str(e)}")
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"PROPFIND failed: {str(e)}")

    def _parse_propfind_response(self, xml_text: str, request_path: str) -> List[FileEntry]:
        """Parse WebDAV PROPFIND XML response."""
        try:
            root = ET.fromstring(xml_text)
            entries = []

            for response in root.findall("d:response", self.NS):
                href_elem = response.find("d:href", self.NS)
                if href_elem is None or href_elem.text is None:
                    continue

                href = href_elem.text.strip()

                # Skip the parent directory itself (PROPFIND depth=1 includes parent)
                # Extract the path part from href and compare with request path
                from urllib.parse import unquote, urlparse
                href_path = unquote(urlparse(href).path if '://' in href else href)

                # Build expected parent path
                expected_parent = f"/seafdav/{self.library}"
                if request_path:
                    expected_parent = f"{expected_parent}/{request_path}"

                # Skip if this href is the parent directory itself
                if href_path.rstrip("/") == expected_parent.rstrip("/"):
                    continue

                # Extract properties
                propstat = response.find("d:propstat", self.NS)
                if propstat is None:
                    continue

                prop = propstat.find("d:prop", self.NS)
                if prop is None:
                    continue

                # Check if it's a directory (collection)
                resourcetype = prop.find("d:resourcetype", self.NS)
                is_dir = resourcetype is not None and resourcetype.find("d:collection", self.NS) is not None

                # Extract name from href
                name = self._extract_name_from_href(href)
                if not name or name == ".":
                    continue

                # File size (only for files)
                size = None
                if not is_dir:
                    size_elem = prop.find("d:getcontentlength", self.NS)
                    if size_elem is not None and size_elem.text:
                        try:
                            size = int(size_elem.text)
                        except ValueError:
                            pass

                # Last modified
                modified = None
                modified_elem = prop.find("d:getlastmodified", self.NS)
                if modified_elem is not None and modified_elem.text:
                    try:
                        # Parse RFC 2822 date format
                        modified = datetime.strptime(
                            modified_elem.text, "%a, %d %b %Y %H:%M:%S %Z"
                        )
                    except (ValueError, AttributeError):
                        pass

                # Content type
                content_type = None
                if not is_dir:
                    ct_elem = prop.find("d:getcontenttype", self.NS)
                    if ct_elem is not None and ct_elem.text:
                        content_type = ct_elem.text

                # Build relative path
                rel_path = os.path.join(request_path, name) if request_path else name

                entries.append(
                    FileEntry(
                        name=name,
                        path=rel_path,
                        is_dir=is_dir,
                        size=size,
                        modified=modified,
                        content_type=content_type,
                    )
                )

            # Sort: directories first, then alphabetically
            entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
            return entries

        except ET.ParseError as e:
            raise StorageError(f"Failed to parse WebDAV XML response: {str(e)}")

    def _decode_href(self, href: str) -> str:
        """Decode URL-encoded href."""
        from urllib.parse import unquote
        return unquote(href)

    def _extract_name_from_href(self, href: str) -> str:
        """Extract filename/dirname from href."""
        # Remove trailing slash for directories
        href = href.rstrip("/")
        # Get last component
        name = href.split("/")[-1]
        # URL decode
        from urllib.parse import unquote
        return unquote(name)

    def download(self, remote_path: str, local_path: str) -> None:
        """
        Download file from WebDAV to local filesystem.

        Args:
            remote_path: Path in WebDAV library (e.g., "folder/file.txt")
            local_path: Local filesystem path (string or Path)
        """
        from pathlib import Path

        # Convert to Path if string
        local_path_obj = Path(local_path) if isinstance(local_path, str) else local_path

        url = self._get_url(remote_path)
        logger.info(f"Downloading from {_mask_auth(url)} to {local_path_obj}")

        try:
            response = self.session.get(url, stream=True, timeout=self.read_timeout)
            response.raise_for_status()

            # Ensure parent directory exists
            local_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Stream to file
            with open(local_path_obj, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Downloaded {remote_path} to {local_path_obj}")

        except requests.exceptions.Timeout:
            raise StorageConnectionError(f"Download timeout for {remote_path}")
        except requests.exceptions.ConnectionError as e:
            raise StorageConnectionError(f"Connection failed: {str(e)}")
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"Download failed: {str(e)}")

    def upload(self, local_path: Path, remote_path: str) -> None:
        """
        Upload a file via HTTP PUT.

        Args:
            local_path: Source local path
            remote_path: Destination path in storage
        """
        if not local_path.exists():
            raise StorageError(f"Local file not found: {local_path}")

        url = self._get_url(remote_path)

        try:
            logger.debug(f"Uploading {local_path} to {_mask_auth(url)}")

            with open(local_path, "rb") as f:
                response = self.session.put(
                    url,
                    data=f,
                    headers={
                        "If-Match": "*",  # Allow overwriting existing files
                    },
                    timeout=(self.connect_timeout, self.read_timeout),
                )

            if response.status_code == 401:
                raise StorageAuthError("Authentication failed")
            elif response.status_code == 403:
                raise StorageAuthError("Access forbidden")
            elif response.status_code == 412:
                # Precondition failed - file doesn't exist, retry without If-Match
                logger.debug("File doesn't exist, retrying without If-Match header")
                with open(local_path, "rb") as f:
                    response = self.session.put(
                        url,
                        data=f,
                        timeout=(self.connect_timeout, self.read_timeout),
                    )

            response.raise_for_status()
            logger.info(f"Uploaded {local_path} to {remote_path}")

        except requests.exceptions.Timeout:
            raise StorageConnectionError(f"Upload timeout for {remote_path}")
        except requests.exceptions.ConnectionError as e:
            raise StorageConnectionError(f"Connection failed: {str(e)}")
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"Upload failed: {str(e)}")

    def mkdir(self, remote_path: str) -> None:
        """
        Create a directory via MKCOL (idempotent).

        Args:
            remote_path: Directory path to create
        """
        # Split path and create each component
        parts = [p for p in remote_path.split("/") if p]

        for i in range(len(parts)):
            partial_path = "/".join(parts[: i + 1])
            url = self._get_url(partial_path)

            try:
                response = self.session.request(
                    "MKCOL",
                    url,
                    timeout=(self.connect_timeout, self.read_timeout),
                )

                # 201 = created, 405 = already exists (method not allowed on existing collection)
                if response.status_code in (201, 405):
                    continue
                elif response.status_code == 401:
                    raise StorageAuthError("Authentication failed")
                elif response.status_code == 403:
                    raise StorageAuthError("Access forbidden")

                response.raise_for_status()

            except requests.exceptions.Timeout:
                raise StorageConnectionError(f"MKCOL timeout for {partial_path}")
            except requests.exceptions.ConnectionError as e:
                raise StorageConnectionError(f"Connection failed: {str(e)}")
            except StorageError:
                raise
            except Exception as e:
                raise StorageError(f"MKCOL failed for {partial_path}: {str(e)}")

        logger.info(f"Created directory: {remote_path}")

    def move(self, src_path: str, dest_path: str) -> None:
        """
        Move/rename a file or directory via WebDAV MOVE method.

        Args:
            src_path: Source path
            dest_path: Destination path
        """
        src_url = self._get_url(src_path)
        dest_url = self._get_url(dest_path)

        try:
            response = self.session.request(
                "MOVE",
                src_url,
                headers={
                    "Destination": dest_url,
                    "Overwrite": "F",  # Don't overwrite existing
                },
                timeout=(self.connect_timeout, self.read_timeout),
            )

            if response.status_code == 201:
                logger.info(f"Moved {src_path} to {dest_path}")
            elif response.status_code == 204:
                logger.info(f"Moved {src_path} to {dest_path} (destination existed)")
            elif response.status_code == 401:
                raise StorageAuthError("Authentication failed")
            elif response.status_code == 403:
                raise StorageAuthError("Access forbidden")
            elif response.status_code == 404:
                raise StorageNotFoundError(f"Source path not found: {src_path}")
            elif response.status_code == 412:
                raise StorageError(f"Destination already exists: {dest_path}")
            else:
                response.raise_for_status()

        except requests.exceptions.Timeout:
            raise StorageConnectionError(f"MOVE timeout for {src_path}")
        except requests.exceptions.ConnectionError as e:
            raise StorageConnectionError(f"Connection failed: {str(e)}")
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"MOVE failed: {str(e)}")

    def exists(self, remote_path: str) -> bool:
        """
        Check if path exists via HEAD request.

        Args:
            remote_path: Path to check

        Returns:
            True if exists
        """
        url = self._get_url(remote_path)

        try:
            response = self.session.head(
                url, timeout=(self.connect_timeout, self.read_timeout)
            )
            return response.status_code in (200, 204)
        except Exception:
            return False

    def get_info(self, remote_path: str) -> Optional[FileEntry]:
        """
        Get file/directory info via PROPFIND.

        Args:
            remote_path: Path to query

        Returns:
            FileEntry or None
        """
        try:
            # List parent directory and find this entry
            parent_path = str(Path(remote_path).parent)
            if parent_path == ".":
                parent_path = ""

            entries = self.listdir(parent_path)
            name = Path(remote_path).name

            for entry in entries:
                if entry.name == name:
                    return entry

            return None
        except StorageError:
            return None

    def delete(self, remote_path: str) -> None:
        """
        Delete a file or directory via WebDAV DELETE.

        Args:
            remote_path: Path to delete (file or directory)

        Raises:
            StorageError: If deletion fails
        """
        url = self._get_url(remote_path)

        try:
            logger.info(f"Deleting {_mask_auth(url)}")
            response = self.session.delete(
                url,
                timeout=(self.connect_timeout, self.read_timeout)
            )

            if response.status_code == 401:
                raise StorageAuthError("Authentication failed (401)")
            elif response.status_code == 404:
                # Already deleted or doesn't exist
                logger.warning(f"Path not found (404): {remote_path}")
                return
            elif response.status_code not in (200, 204, 404):
                raise StorageError(f"DELETE failed with status {response.status_code}")

            logger.info(f"Deleted: {remote_path}")

        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"DELETE failed: {str(e)}")
