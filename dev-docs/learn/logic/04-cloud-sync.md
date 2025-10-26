# Cloud Storage & WebDAV Sync

**Learning Goal**: Integrate cloud storage using WebDAV protocol for seamless dataset synchronization.

By the end of this page, you'll:
- Understand the WebDAV protocol basics
- Implement credential storage with keyring
- List, download, and upload files via WebDAV
- Handle authentication and errors
- Build a cloud file browser
- Sync datasets between local and cloud

---

## Why WebDAV?

**WebDAV** (Web Distributed Authoring and Versioning) = HTTP extension for remote file management.

**Benefits:**
- ✅ **Standard protocol** — Works with Seafile, Nextcloud, ownCloud
- ✅ **No vendor lock-in** — Switch cloud providers easily
- ✅ **HTTP-based** — Works through firewalls
- ✅ **Authentication** — Username + password/token

**Use case in Hei-DataHub:**
- Store datasets in HeiBox (Seafile instance)
- Access datasets from anywhere
- Share datasets with collaborators
- Keep local and cloud in sync

---

## The WebDAV Protocol

### HTTP Methods

WebDAV extends HTTP with new methods:

| Method | Purpose | Example |
|--------|---------|---------|
| **PROPFIND** | List directory | Get file list |
| **GET** | Download file | Download `metadata.yaml` |
| **PUT** | Upload file | Upload new dataset |
| **MKCOL** | Create directory | Create `data/my-dataset/` |
| **DELETE** | Delete file/dir | Remove old dataset |
| **COPY** | Copy file | Duplicate dataset |
| **MOVE** | Move/rename | Rename dataset |

---

### PROPFIND Example

**Request:**
```http
PROPFIND /seafdav/my-library/data HTTP/1.1
Host: heibox.uni-heidelberg.de
Authorization: Basic dXNlcjpwYXNzd29yZA==
Depth: 1
Content-Type: application/xml

<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:resourcetype/>
    <d:getcontentlength/>
    <d:getlastmodified/>
  </d:prop>
</d:propfind>
```

**Response:**
```xml
<?xml version="1.0"?>
<d:multistatus xmlns:d="DAV:">
  <d:response>
    <d:href>/seafdav/my-library/data/climate-data/</d:href>
    <d:propstat>
      <d:prop>
        <d:resourcetype><d:collection/></d:resourcetype>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
  <d:response>
    <d:href>/seafdav/my-library/data/metadata.yaml</d:href>
    <d:propstat>
      <d:prop>
        <d:resourcetype/>
        <d:getcontentlength>1234</d:getcontentlength>
        <d:getlastmodified>Mon, 15 Jan 2025 10:30:00 GMT</d:getlastmodified>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
</d:multistatus>
```

---

## The WebDAVStorage Class

**File:** `src/mini_datahub/services/webdav_storage.py`

```python
import requests
from typing import List, Optional
from urllib.parse import quote, urljoin

class WebDAVStorage:
    """WebDAV storage backend for Seafile/HeiBox."""

    def __init__(
        self,
        base_url: str,
        library: str,
        username: str,
        password: str,
        connect_timeout: int = 5,
        read_timeout: int = 60,
    ):
        """
        Initialize WebDAV client.

        Args:
            base_url: WebDAV endpoint (e.g., https://heibox.uni-heidelberg.de/seafdav)
            library: Library/folder name (e.g., my-datasets)
            username: WebDAV username
            password: WebDAV password/token
            connect_timeout: Connection timeout (seconds)
            read_timeout: Read timeout (seconds)
        """
        self.base_url = base_url.rstrip("/")
        self.library = library.strip("/")
        self.username = username
        self.password = password

        # Build root URL: base_url/library
        self.root_url = f"{self.base_url}/{self.library}"

        # Setup session with auth
        self.session = requests.Session()
        self.session.auth = (username, password)

        # Setup retry logic for 5xx errors
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
```

**What's happening:**
1. Store connection details
2. Create `requests.Session()` with Basic Auth
3. Add retry logic for server errors
4. Build full URL: `base_url/library`

---

## Credential Storage

**Problem:** Can't hardcode passwords in config files!

**Solution:** Linux keyring (Secret Service)

### The AuthStore Interface

**File:** `src/mini_datahub/auth/credentials.py`

```python
from abc import ABC, abstractmethod
from typing import Optional

class AuthStore(ABC):
    """Abstract interface for credential storage."""

    @abstractmethod
    def store_secret(self, key_id: str, value: str) -> None:
        """Store a secret."""
        pass

    @abstractmethod
    def load_secret(self, key_id: str) -> Optional[str]:
        """Load a secret. Returns None if not found."""
        pass

    @abstractmethod
    def available(self) -> bool:
        """Check if backend is available."""
        pass
```

---

### Keyring Implementation

```python
import keyring

class KeyringAuthStore(AuthStore):
    """Linux keyring-based storage (Secret Service)."""

    SERVICE_NAME = "hei-datahub"

    def __init__(self):
        """Initialize keyring."""
        try:
            import keyring
            self._keyring = keyring
            # Test if keyring works
            self._keyring.get_password(self.SERVICE_NAME, "test")
            self._available = True
        except Exception:
            self._available = False

    def store_secret(self, key_id: str, value: str) -> None:
        """Store secret in Linux keyring."""
        self._keyring.set_password(self.SERVICE_NAME, key_id, value)

    def load_secret(self, key_id: str) -> Optional[str]:
        """Load secret from keyring."""
        return self._keyring.get_password(self.SERVICE_NAME, key_id)

    def available(self) -> bool:
        """Check if keyring is available."""
        return self._available
```

---

### Fallback: Environment Variables

```python
import os

class EnvAuthStore(AuthStore):
    """Environment variable fallback."""

    def store_secret(self, key_id: str, value: str) -> None:
        """Cannot store in env (read-only)."""
        raise NotImplementedError("EnvAuthStore is read-only")

    def load_secret(self, key_id: str) -> Optional[str]:
        """Load from environment variable."""
        # Convert key_id to env var name
        # "webdav:token:user@host" → "HEIBOX_WEBDAV_TOKEN"
        if "token" in key_id:
            return os.getenv("HEIBOX_WEBDAV_TOKEN")
        return None

    def available(self) -> bool:
        """Always available."""
        return True
```

---

### Smart Selection

```python
def get_auth_store(prefer_keyring: bool = True) -> AuthStore:
    """
    Get best available auth store.

    Priority:
    1. Keyring (if available and preferred)
    2. Environment variables (fallback)
    """
    if prefer_keyring:
        keyring_store = KeyringAuthStore()
        if keyring_store.available():
            return keyring_store

    # Fallback to env
    return EnvAuthStore()
```

**Usage:**

```python
# Store credentials
store = get_auth_store()
store.store_secret("webdav:token:user@heibox", "my-secret-token")

# Load credentials
token = store.load_secret("webdav:token:user@heibox")
```

---

## Listing Files (PROPFIND)

**Goal:** List all files in a directory.

### Implementation

```python
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileEntry:
    """Represents a file or directory."""
    name: str
    path: str
    is_dir: bool
    size: Optional[int] = None
    modified: Optional[datetime] = None


class WebDAVStorage:
    # XML namespaces
    NS = {"d": "DAV:"}

    def listdir(self, path: str = "") -> List[FileEntry]:
        """
        List directory contents.

        Args:
            path: Path relative to library root

        Returns:
            List of FileEntry objects
        """
        url = self._get_url(path)

        # PROPFIND request
        headers = {
            "Depth": "1",  # Only immediate children
            "Content-Type": "application/xml; charset=utf-8",
        }

        propfind_xml = """<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:">
  <d:prop>
    <d:resourcetype/>
    <d:getcontentlength/>
    <d:getlastmodified/>
  </d:prop>
</d:propfind>"""

        response = self.session.request(
            "PROPFIND",
            url,
            data=propfind_xml.encode("utf-8"),
            headers=headers,
            timeout=self.read_timeout,
        )

        if response.status_code == 401:
            raise AuthError("Invalid credentials")
        elif response.status_code == 404:
            raise NotFoundError(f"Path not found: {path}")
        elif response.status_code == 207:
            # Multi-Status (success)
            return self._parse_propfind_response(response.text, path)
        else:
            response.raise_for_status()

    def _parse_propfind_response(
        self,
        xml_text: str,
        request_path: str
    ) -> List[FileEntry]:
        """Parse WebDAV XML response."""
        root = ET.fromstring(xml_text)
        entries = []

        for response in root.findall("d:response", self.NS):
            href = response.find("d:href", self.NS).text

            # Skip parent directory itself
            if self._is_parent_dir(href, request_path):
                continue

            # Extract properties
            prop = response.find(".//d:prop", self.NS)

            # Check if directory
            resourcetype = prop.find("d:resourcetype", self.NS)
            is_dir = resourcetype.find("d:collection", self.NS) is not None

            # Extract name from href
            name = self._extract_name_from_href(href)

            # File size (only for files)
            size = None
            if not is_dir:
                size_elem = prop.find("d:getcontentlength", self.NS)
                if size_elem is not None:
                    size = int(size_elem.text)

            # Last modified
            modified = None
            modified_elem = prop.find("d:getlastmodified", self.NS)
            if modified_elem is not None:
                # Parse: "Mon, 15 Jan 2025 10:30:00 GMT"
                modified = datetime.strptime(
                    modified_elem.text,
                    "%a, %d %b %Y %H:%M:%S %Z"
                )

            # Build relative path
            rel_path = f"{request_path}/{name}" if request_path else name

            entries.append(FileEntry(
                name=name,
                path=rel_path,
                is_dir=is_dir,
                size=size,
                modified=modified,
            ))

        # Sort: directories first, then alphabetically
        entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
        return entries
```

**Example:**

```python
storage = WebDAVStorage(
    base_url="https://heibox.uni-heidelberg.de/seafdav",
    library="my-datasets",
    username="user123",
    password="my-token",
)

# List root directory
files = storage.listdir("")
for f in files:
    icon = "📁" if f.is_dir else "📄"
    print(f"{icon} {f.name}")

# Output:
# 📁 climate-data
# 📁 covid-analysis
# 📄 README.md
```

---

## Downloading Files (GET)

**Goal:** Download a file from cloud to local disk.

```python
class WebDAVStorage:
    def download(self, remote_path: str, local_path: str) -> None:
        """
        Download file from WebDAV.

        Args:
            remote_path: Path in cloud (e.g., "data/metadata.yaml")
            local_path: Local filesystem path
        """
        from pathlib import Path

        url = self._get_url(remote_path)
        local_path_obj = Path(local_path)

        # GET request with streaming
        response = self.session.get(url, stream=True, timeout=self.read_timeout)
        response.raise_for_status()

        # Ensure parent directory exists
        local_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write to file in chunks
        with open(local_path_obj, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
```

**Example:**

```python
storage.download(
    remote_path="climate-data/metadata.yaml",
    local_path="/tmp/metadata.yaml"
)
print("Downloaded!")
```

---

## Uploading Files (PUT)

**Goal:** Upload a local file to cloud.

```python
class WebDAVStorage:
    def upload(self, local_path: str, remote_path: str) -> None:
        """
        Upload file to WebDAV.

        Args:
            local_path: Local filesystem path
            remote_path: Path in cloud
        """
        from pathlib import Path

        url = self._get_url(remote_path)
        local_path_obj = Path(local_path)

        if not local_path_obj.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        # PUT request
        with open(local_path_obj, 'rb') as f:
            response = self.session.put(
                url,
                data=f,
                timeout=self.read_timeout,
            )

        response.raise_for_status()
```

**Example:**

```python
storage.upload(
    local_path="/home/user/datasets/climate-2025/metadata.yaml",
    remote_path="climate-2025/metadata.yaml"
)
print("Uploaded!")
```

---

## Creating Directories (MKCOL)

**Goal:** Create a new directory in cloud.

```python
class WebDAVStorage:
    def mkdir(self, path: str) -> None:
        """
        Create directory in WebDAV.

        Args:
            path: Directory path to create
        """
        url = self._get_url(path)

        # MKCOL request
        response = self.session.request("MKCOL", url, timeout=self.connect_timeout)

        if response.status_code == 405:
            # Already exists (Method Not Allowed)
            return

        response.raise_for_status()
```

---

## Error Handling

### Custom Exceptions

```python
class StorageError(Exception):
    """Base storage error."""
    pass

class StorageAuthError(StorageError):
    """Authentication failed."""
    pass

class StorageConnectionError(StorageError):
    """Connection failed."""
    pass

class StorageNotFoundError(StorageError):
    """Path not found."""
    pass
```

### Retry Logic

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Retry strategy
retry_strategy = Retry(
    total=3,                # 3 retry attempts
    backoff_factor=0.5,     # Wait 0.5s, 1s, 2s between retries
    status_forcelist=[500, 502, 503, 504],  # Retry on server errors
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
```

**Result:** Automatically retries on server errors!

---

## Building a Cloud File Browser

**Goal:** TUI widget to browse cloud files.

**File:** `src/mini_datahub/ui/views/cloud_files.py`

```python
from textual.screen import Screen
from textual.widgets import DirectoryTree, Header, Footer
from mini_datahub.services.webdav_storage import WebDAVStorage

class CloudFilesScreen(Screen):
    """Browse cloud files via WebDAV."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "open_file", "Open"),
        ("d", "download", "Download"),
    ]

    def __init__(self, storage: WebDAVStorage):
        super().__init__()
        self.storage = storage
        self.current_path = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="file-list")
        yield Footer()

    def on_mount(self) -> None:
        """Load root directory."""
        self.load_directory("")

    def load_directory(self, path: str) -> None:
        """Load and display directory contents."""
        try:
            files = self.storage.listdir(path)

            # Format file list
            lines = []
            for f in files:
                icon = "📁" if f.is_dir else "📄"
                size = f"{f.size:,} bytes" if f.size else ""
                lines.append(f"{icon} {f.name}  {size}")

            # Update display
            file_list = self.query_one("#file-list", Static)
            file_list.update("\n".join(lines))

        except Exception as e:
            self.app.notify(f"Error: {e}", severity="error")

    def action_download(self) -> None:
        """Download selected file."""
        # Get selected file...
        # Download to local disk...
        pass
```

---

## Syncing Datasets

**Goal:** Sync local datasets to cloud.

```python
def sync_dataset_to_cloud(dataset_id: str, storage: WebDAVStorage) -> None:
    """
    Upload dataset to cloud storage.

    Args:
        dataset_id: Dataset ID
        storage: WebDAV storage instance
    """
    from mini_datahub.infra.paths import DATA_DIR

    local_dir = DATA_DIR / dataset_id
    if not local_dir.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_id}")

    # Create remote directory
    storage.mkdir(f"data/{dataset_id}")

    # Upload all files
    for local_file in local_dir.rglob("*"):
        if local_file.is_file():
            # Build relative path
            rel_path = local_file.relative_to(local_dir)
            remote_path = f"data/{dataset_id}/{rel_path}"

            # Upload
            print(f"Uploading {rel_path}...")
            storage.upload(str(local_file), remote_path)

    print(f"✓ Synced {dataset_id} to cloud")
```

---

## What You've Learned

✅ **WebDAV protocol** — PROPFIND, GET, PUT, MKCOL methods
✅ **Credential storage** — Keyring with env fallback
✅ **Listing files** — Parse XML PROPFIND responses
✅ **Download/upload** — Stream files efficiently
✅ **Error handling** — Retry logic, custom exceptions
✅ **TUI integration** — Cloud file browser
✅ **Dataset sync** — Upload to cloud storage

---

## Try It Yourself

### Exercise 1: Test WebDAV Connection

```python
from mini_datahub.services.webdav_storage import WebDAVStorage

storage = WebDAVStorage(
    base_url="https://heibox.uni-heidelberg.de/seafdav",
    library="testing-hei-datahub",
    username="your-username",
    password="your-token",
)

# List root
files = storage.listdir("")
for f in files:
    print(f"{'[DIR]' if f.is_dir else '[FILE]'} {f.name}")
```

---

### Exercise 2: Implement Bidirectional Sync

**Goal:** Sync changes in both directions (local ↔ cloud).

**Hint:**

```python
def sync_bidirectional(dataset_id: str, storage: WebDAVStorage):
    # 1. Compare local vs cloud files
    # 2. Upload newer local files
    # 3. Download newer cloud files
    # 4. Resolve conflicts
    pass
```

---

### Exercise 3: Add Progress Bars

**Goal:** Show upload/download progress.

**Hint:**

```python
from tqdm import tqdm

def download_with_progress(storage, remote_path, local_path):
    response = storage.session.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(local_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
```

---

## Next Steps

Now you understand cloud storage integration. Next, let's explore **CLI commands and how they connect to services**.

**Next:** [CLI Integration](05-cli-integration.md)

---

## Further Reading

- [WebDAV RFC 4918](https://datatracker.ietf.org/doc/html/rfc4918)
- [Seafile WebDAV Extension](https://manual.seafile.com/extension/webdav/)
- [Python keyring Library](https://github.com/jaraco/keyring)
- [Hei-DataHub Auth & Sync](../../architecture/auth-and-sync.md)
