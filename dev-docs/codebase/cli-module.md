# CLI Module

## Overview

The **CLI Module** provides command-line interface access to all Hei-DataHub functionality. It uses Python's `argparse` for argument parsing and offers both interactive and non-interactive workflows.

---

## Architecture

**Layer Position:**

```
CLI Layer ← YOU ARE HERE
     ↓
Services Layer
     ↓
Core + Infrastructure
```

**Design Principles:**
- **Unix philosophy:** Do one thing well
- **Composable:** Commands can be piped together
- **Scriptable:** Suitable for automation
- **User-friendly:** Clear help messages and error handling

---

## Directory Structure

```
cli/
├── __init__.py
├── main.py                  # CLI entry point & argument parsing
├── doctor.py                # Diagnostic tool (auth doctor, etc.)
├── update_manager.py        # Update checking and installation
├── linux_update.py          # Linux-specific update logic
├── macos_update.py          # macOS-specific update logic
└── windows_update.py        # Windows-specific update logic
```

---

## Entry Point

### `main.py` - CLI Entry Point

**Purpose:** Parse arguments and dispatch to command handlers

**Structure:**

```python
def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="hei-datahub",
        description="Hei-DataHub - Lightweight data catalog with TUI"
    )

    parser.add_argument("--version", action="version",
                       version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add subcommands
    setup_reindex_command(subparsers)
    setup_auth_commands(subparsers)
    setup_sync_commands(subparsers)
    setup_search_commands(subparsers)
    setup_validate_commands(subparsers)

    args = parser.parse_args()

    # Dispatch to handler
    if args.command == "reindex":
        handle_reindex(args)
    elif args.command == "auth":
        handle_auth(args)
    # ... etc
    else:
        # No command: launch TUI
        handle_tui(args)
```

---

## Command Categories

### 1. Core Commands

#### Launch TUI (Default)

**Usage:**

```bash
hei-datahub
# or
hei-datahub tui
```

**Implementation:**

```python
def handle_tui(args):
    """Launch the terminal user interface"""
    from mini_datahub.ui.views.home import run_tui
    from mini_datahub.infra.db import ensure_database

    # Initialize database if needed
    ensure_database()

    # Launch TUI
    run_tui()
```

**Error Handling:**

```python
try:
    run_tui()
except KeyboardInterrupt:
    print("\nExiting...")
    sys.exit(0)
except Exception as e:
    print(f"Error launching TUI: {e}", file=sys.stderr)
    sys.exit(1)
```

---

#### Reindex

**Purpose:** Rebuild search index from dataset files

**Usage:**

```bash
hei-datahub reindex
hei-datahub reindex --verbose
```

**Implementation:**

```python
def handle_reindex(args):
    """Rebuild FTS5 search index from YAML files"""
    from mini_datahub.infra.store import list_datasets, read_dataset
    from mini_datahub.infra.index import upsert_dataset

    print("Reindexing datasets...")

    dataset_ids = list_datasets()
    count = 0
    errors = []

    for dataset_id in dataset_ids:
        try:
            metadata = read_dataset(dataset_id)
            upsert_dataset(dataset_id, metadata)
            count += 1
            if args.verbose:
                print(f"  ✓ Indexed: {dataset_id}")
        except Exception as e:
            errors.append(f"{dataset_id}: {e}")

    print(f"\n✓ Indexed {count} dataset(s)")

    if errors:
        print(f"\n⚠ {len(errors)} error(s):")
        for error in errors:
            print(f"  • {error}")
        sys.exit(1)
```

**When to use:**
- After bulk import of datasets
- After schema changes
- To fix corrupted index
- After upgrading versions

---

### 2. Authentication Commands

#### Setup Authentication

**Usage:**

```bash
hei-datahub auth setup
hei-datahub auth setup --url https://heibox.uni-heidelberg.de
```

**Implementation:**

```python
def handle_auth_setup(args):
    """Run interactive auth setup wizard"""
    from mini_datahub.auth.setup import run_setup_wizard

    # Interactive wizard
    if args.url:
        run_setup_wizard(url=args.url)
    else:
        run_setup_wizard()
```

**Wizard Flow:**

```python
def run_setup_wizard(url=None):
    """Interactive setup"""
    print("Hei-DataHub Authentication Setup")
    print("=" * 40)

    # Prompt for WebDAV URL
    if not url:
        url = input("WebDAV URL: ").strip()

    # Prompt for library name
    library = input("Library name: ").strip()

    # Prompt for auth method
    print("\nAuth methods:")
    print("  1. Token (recommended)")
    print("  2. Password")
    method = input("Choose (1 or 2): ").strip()

    # Prompt for credentials
    if method == "1":
        token = getpass("Token: ")
        credential = token
    else:
        password = getpass("Password: ")
        credential = password

    # Validate connection
    print("\nValidating connection...")
    if validate_webdav_connection(url, library, credential):
        print("✓ Connection successful!")

        # Store credentials
        key_id = derive_key_id(url, library)
        store_secret(key_id, credential)

        # Save config
        save_config({
            "webdav": {
                "url": url,
                "library": library,
                "key_id": key_id
            }
        })

        print("✓ Setup complete!")
    else:
        print("✗ Connection failed. Please check your credentials.")
        sys.exit(1)
```

---

#### Doctor (Diagnostics)

**Usage:**

```bash
hei-datahub auth doctor
hei-datahub auth doctor --verbose
```

**Purpose:** Diagnose authentication and connectivity issues

**Checks:**

1. ✅ Config file exists and valid
2. ✅ Credentials stored in keyring
3. ✅ Network reachable
4. ✅ WebDAV server reachable
5. ✅ Authentication successful
6. ✅ Read permission granted
7. ✅ Write permission granted

**Implementation:**

```python
def handle_auth_doctor(args):
    """Run diagnostics"""
    from mini_datahub.cli.doctor import run_diagnostics

    results = run_diagnostics(verbose=args.verbose)

    # Print results
    print("Authentication Diagnostics")
    print("=" * 40)

    for check, passed in results.items():
        icon = "✓" if passed else "✗"
        print(f"{icon} {check}")

    # Exit code based on results
    if all(results.values()):
        print("\n✓ All checks passed!")
        sys.exit(0)
    else:
        print("\n✗ Some checks failed. See above for details.")
        sys.exit(1)
```

---

#### Status

**Usage:**

```bash
hei-datahub auth status
```

**Output:**

```
WebDAV Configuration:
  URL: https://heibox.uni-heidelberg.de
  Library: research-datasets
  Status: ✓ Connected
  Credentials: ✓ Stored in keyring
```

**Implementation:**

```python
def handle_auth_status(args):
    """Show authentication status"""
    from mini_datahub.services.config import load_config
    from mini_datahub.auth.credentials import has_secret

    config = load_config()
    webdav = config.get("webdav", {})

    print("WebDAV Configuration:")
    print(f"  URL: {webdav.get('url', 'Not configured')}")
    print(f"  Library: {webdav.get('library', 'Not configured')}")

    # Check if credentials exist
    key_id = webdav.get("key_id")
    if key_id and has_secret(key_id):
        print(f"  Credentials: ✓ Stored in keyring")
    else:
        print(f"  Credentials: ✗ Not found")
```

---

### 3. Sync Commands

#### Sync Now

**Usage:**

```bash
hei-datahub sync now
hei-datahub sync now --force
```

**Implementation:**

```python
def handle_sync_now(args):
    """Trigger immediate sync"""
    from mini_datahub.services.sync import sync_now

    print("Syncing with cloud...")

    result = sync_now(force=args.force)

    print(f"✓ Sync complete!")
    print(f"  Downloaded: {result.downloads}")
    print(f"  Uploaded: {result.uploads}")
    print(f"  Conflicts: {result.conflicts}")
```

---

#### Sync Status

**Usage:**

```bash
hei-datahub sync status
```

**Output:**

```
Sync Status:
  Last sync: 2024-10-25 14:32:15
  Next sync: 2024-10-25 14:37:15 (in 3 minutes)
  Status: ✓ Up to date
  Pending uploads: 0
  Outbox items: 2
```

---

#### Enable/Disable Sync

**Usage:**

```bash
hei-datahub sync enable
hei-datahub sync disable
```

**Implementation:**

```python
def handle_sync_enable(args):
    """Enable background sync"""
    from mini_datahub.services.config import update_config

    update_config({"sync": {"enabled": True}})
    print("✓ Background sync enabled")

def handle_sync_disable(args):
    """Disable background sync"""
    from mini_datahub.services.config import update_config

    update_config({"sync": {"enabled": False}})
    print("✓ Background sync disabled")
```

---

### 4. Search Commands

#### Search Datasets

**Usage:**

```bash
hei-datahub search "climate data"
hei-datahub search "temperature" --project research
hei-datahub search "ocean" --limit 10
hei-datahub search --json  # Output as JSON
```

**Implementation:**

```python
def handle_search(args):
    """Search datasets from CLI"""
    from mini_datahub.services.fast_search import search_indexed

    # Build query with filters
    query = args.query
    if args.project:
        query += f" project:{args.project}"

    # Execute search
    results = search_indexed(query, limit=args.limit)

    # Format output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Found {len(results)} dataset(s):\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']}")
            print(f"   ID: {result['id']}")
            if result.get('snippet'):
                print(f"   {result['snippet']}")
            print()
```

---

### 5. Validation Commands

#### Validate Dataset

**Usage:**

```bash
hei-datahub validate climate-data
hei-datahub validate --all
```

**Implementation:**

```python
def handle_validate(args):
    """Validate dataset metadata against schema"""
    from mini_datahub.core.validators import validate_dataset
    from mini_datahub.infra.store import read_dataset

    if args.all:
        # Validate all datasets
        dataset_ids = list_datasets()
    else:
        dataset_ids = [args.dataset_id]

    errors = []

    for dataset_id in dataset_ids:
        try:
            metadata = read_dataset(dataset_id)
            validate_dataset(metadata)
            print(f"✓ {dataset_id}: Valid")
        except ValidationError as e:
            errors.append(f"✗ {dataset_id}: {e}")

    if errors:
        print(f"\nValidation errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
```

---

### 6. Update Commands

#### Check for Updates

**Usage:**

```bash
hei-datahub update check
hei-datahub update install
```

**Implementation:**

```python
def handle_update_check(args):
    """Check for newer version on GitHub"""
    from mini_datahub.services.update_check import check_for_updates

    print("Checking for updates...")

    update = check_for_updates()

    if update:
        print(f"✓ New version available: {update.version}")
        print(f"  Current: {__version__}")
        print(f"  Download: {update.url}")
        print(f"\nRun 'hei-datahub update install' to update")
    else:
        print("✓ You are running the latest version")
```

**Platform-Specific Updates:**

```python
def handle_update_install(args):
    """Install update (platform-specific)"""
    import platform

    system = platform.system()

    if system == "Linux":
        from mini_datahub.cli.linux_update import install_update
    elif system == "Darwin":
        from mini_datahub.cli.macos_update import install_update
    elif system == "Windows":
        from mini_datahub.cli.windows_update import install_update
    else:
        print("✗ Automatic updates not supported on this platform")
        sys.exit(1)

    install_update()
```

---

## Helper Modules

### `doctor.py` - Diagnostic Tool

**Purpose:** Comprehensive system diagnostics

**Checks:**

```python
def run_diagnostics(verbose=False):
    """Run all diagnostic checks"""
    checks = {
        "Config file exists": check_config_file(),
        "Config file valid": check_config_valid(),
        "Credentials in keyring": check_credentials(),
        "Network available": check_network(),
        "WebDAV server reachable": check_webdav_reachable(),
        "Authentication works": check_auth(),
        "Read permission granted": check_read_permission(),
        "Write permission granted": check_write_permission(),
        "Database accessible": check_database(),
        "Index operational": check_index(),
    }

    return checks
```

---

### `update_manager.py` - Update Management

**Purpose:** Check and install updates

**GitHub Release Checking:**

```python
def check_for_updates() -> UpdateInfo | None:
    """Check GitHub releases for newer version"""
    url = "https://api.github.com/repos/0xpix/Hei-DataHub/releases/latest"

    response = requests.get(url)
    data = response.json()

    latest_version = data["tag_name"].lstrip("v")

    if version.parse(latest_version) > version.parse(__version__):
        return UpdateInfo(
            version=latest_version,
            url=data["html_url"],
            release_notes=data["body"]
        )

    return None
```

---

## Output Formatting

### Colored Output

```python
class Colors:
    """ANSI color codes"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def success(message: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")

def error(message: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.RESET} {message}", file=sys.stderr)

def warning(message: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")
```

### Progress Indicators

```python
def show_progress(current: int, total: int, item: str) -> None:
    """Show progress bar"""
    percent = int((current / total) * 100)
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\r{bar} {percent}% - {item}", end="", flush=True)

    if current == total:
        print()  # New line at end
```

---

## Exit Codes

```python
EXIT_SUCCESS = 0         # Success
EXIT_ERROR = 1           # General error
EXIT_AUTH_ERROR = 2      # Authentication failed
EXIT_NETWORK_ERROR = 3   # Network error
EXIT_VALIDATION_ERROR = 4  # Validation failed
```

**Usage:**

```python
try:
    result = sync_now()
    sys.exit(EXIT_SUCCESS)
except AuthenticationError:
    error("Authentication failed")
    sys.exit(EXIT_AUTH_ERROR)
except NetworkError:
    error("Network error")
    sys.exit(EXIT_NETWORK_ERROR)
```

---

## Related Documentation

- **[UI Module](ui-module.md)** - Terminal user interface
- **[Services Module](services-module.md)** - Business logic
- **[API Reference: CLI Commands](../api-reference/cli-commands.md)** - Complete command reference

---

**Last Updated:** October 25, 2025 | **Version:** 0.59.0-beta "Privacy"
