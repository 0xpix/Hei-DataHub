# CLI Commands & Integration

**Learning Goal**: Build command-line interfaces that connect to your service layer.

By the end of this page, you'll:
- Structure CLI commands with argparse
- Connect CLI to service layer
- Handle errors gracefully in CLI
- Build interactive wizards
- Create diagnostic commands
- Follow CLI best practices

---

## Why CLI Matters

**TUI vs CLI:**

- **TUI** (Terminal UI) — Interactive, visual, fullscreen
  - Good for: Browsing, exploring, complex workflows
  - Example: `hei-datahub` (no args)

- **CLI** (Command-Line Interface) — Single commands, scripting
  - Good for: Automation, scripting, one-off tasks
  - Example: `hei-datahub reindex`

**Both are important!**

---

## The CLI Architecture

```
┌────────────────────────────────────────┐
│  1. ENTRYPOINT (main.py)               │
│  - Parse arguments                     │
│  - Dispatch to handlers                │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  2. HANDLERS (handle_*)                │
│  - Validate input                      │
│  - Call service layer                  │
│  - Format output                       │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│  3. SERVICES                           │
│  - Business logic                      │
│  - Data operations                     │
└────────────────────────────────────────┘
```

**Flow:**
```bash
$ hei-datahub reindex
    ↓
main() parses args
    ↓
handle_reindex() called
    ↓
infra.index.reindex_all()
    ↓
Print results
```

---

## Building the Main Parser

**File:** `src/mini_datahub/cli/main.py`

```python
import argparse
import sys
from mini_datahub.version import __version__

def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="hei-datahub",
        description="Hei-DataHub: Local-first dataset catalog with cloud sync",
        epilog="For more help: hei-datahub <command> --help",
    )

    # Global options
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        help="Override data directory path",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. TUI (default)
    tui_parser = subparsers.add_parser("tui", help="Launch interactive TUI")

    # 2. Reindex
    reindex_parser = subparsers.add_parser("reindex", help="Rebuild search index")

    # 3. Auth
    auth_parser = subparsers.add_parser("auth", help="Manage authentication")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command")

    # auth setup
    setup_parser = auth_subparsers.add_parser("setup", help="Setup WebDAV auth")
    setup_parser.add_argument("--url", help="WebDAV URL")
    setup_parser.add_argument("--username", help="Username")
    setup_parser.add_argument("--token", help="Auth token")

    # auth status
    status_parser = auth_subparsers.add_parser("status", help="Show auth status")

    # auth clear
    clear_parser = auth_subparsers.add_parser("clear", help="Clear credentials")
    clear_parser.add_argument("--force", action="store_true", help="No confirmation")

    # Parse arguments
    args = parser.parse_args()

    # Dispatch to handlers
    if args.command == "reindex":
        handle_reindex(args)
    elif args.command == "auth":
        if args.auth_command == "setup":
            handle_auth_setup(args)
        elif args.auth_command == "status":
            handle_auth_status(args)
        elif args.auth_command == "clear":
            handle_auth_clear(args)
        else:
            auth_parser.print_help()
            sys.exit(1)
    else:
        # Default: launch TUI
        handle_tui(args)

if __name__ == "__main__":
    main()
```

**What's happening:**
1. Create main parser with global options
2. Add subparsers for commands
3. Parse `sys.argv`
4. Dispatch to appropriate handler

---

## Command Handler Pattern

### Example: Reindex Command

**Goal:** Rebuild the FTS5 search index from disk.

```python
def handle_reindex(args):
    """
    Handle the reindex subcommand.

    Args:
        args: Parsed arguments from argparse
    """
    from mini_datahub.infra.db import ensure_database
    from mini_datahub.infra.store import list_datasets, read_dataset
    from mini_datahub.infra.index import upsert_dataset

    print("Reindexing datasets from data directory...")

    # Step 1: Ensure database exists
    ensure_database()

    # Step 2: Get all datasets from disk
    dataset_ids = list_datasets()

    if not dataset_ids:
        print("No datasets found in data directory.")
        sys.exit(0)

    # Step 3: Reindex each dataset
    count = 0
    errors = []

    for dataset_id in dataset_ids:
        try:
            # Read metadata
            metadata = read_dataset(dataset_id)
            if metadata:
                # Upsert to index
                upsert_dataset(dataset_id, metadata)
                count += 1
                print(f"  ✓ Indexed: {dataset_id}")
            else:
                errors.append(f"{dataset_id}: Could not read metadata")

        except Exception as e:
            errors.append(f"{dataset_id}: {str(e)}")

    # Step 4: Report results
    print(f"\n✓ Successfully indexed {count} dataset(s)")

    if errors:
        print(f"\n⚠ Encountered {len(errors)} error(s):")
        for error in errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("All datasets indexed successfully!")
        sys.exit(0)
```

**Pattern:**
1. Import service layer functions
2. Call services
3. Format output
4. Exit with code (0 = success, 1 = error)

**Usage:**

```bash
$ hei-datahub reindex

Reindexing datasets from data directory...
  ✓ Indexed: climate-data-2023
  ✓ Indexed: covid-tracker
  ✓ Indexed: gideon-analysis

✓ Successfully indexed 3 dataset(s)
All datasets indexed successfully!
```

---

## Interactive Wizards

**Goal:** Guide user through multi-step configuration.

### Example: Auth Setup Wizard

```python
def handle_auth_setup(args):
    """Handle auth setup command."""
    from mini_datahub.auth.setup import run_setup_wizard

    exit_code = run_setup_wizard(
        url=args.url,
        username=args.username,
        token=args.token,
        non_interactive=args.non_interactive,
    )

    sys.exit(exit_code)
```

**File:** `src/mini_datahub/auth/setup.py`

```python
def run_setup_wizard(
    url: Optional[str] = None,
    username: Optional[str] = None,
    token: Optional[str] = None,
    non_interactive: bool = False,
) -> int:
    """
    Interactive setup wizard for WebDAV authentication.

    Args:
        url: WebDAV URL (if None, prompt user)
        username: Username (if None, prompt user)
        token: Auth token (if None, prompt user)
        non_interactive: If True, fail if args missing

    Returns:
        Exit code (0 = success, 1 = error)
    """
    print("🔐 WebDAV Authentication Setup\n")

    # Step 1: Get URL
    if not url:
        if non_interactive:
            print("❌ --url required in non-interactive mode")
            return 1

        print("Enter WebDAV URL:")
        print("  Example: https://heibox.uni-heidelberg.de/seafdav")
        url = input("URL: ").strip()

    if not url:
        print("❌ URL is required")
        return 1

    # Step 2: Get username
    if not username:
        if non_interactive:
            print("❌ --username required in non-interactive mode")
            return 1

        username = input("Username: ").strip()

    if not username:
        print("❌ Username is required")
        return 1

    # Step 3: Get token (secure input)
    if not token:
        if non_interactive:
            print("❌ --token required in non-interactive mode")
            return 1

        import getpass
        token = getpass.getpass("Token/Password: ")

    if not token:
        print("❌ Token is required")
        return 1

    # Step 4: Test connection
    print("\nTesting connection...")

    try:
        from mini_datahub.services.webdav_storage import WebDAVStorage

        storage = WebDAVStorage(
            base_url=url,
            library="test",
            username=username,
            password=token,
            connect_timeout=5,
        )

        # Try to list root
        files = storage.listdir("")
        print(f"✓ Connection successful! Found {len(files)} items")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1

    # Step 5: Save credentials
    print("\nSaving credentials...")

    try:
        from mini_datahub.auth.credentials import get_auth_store

        store = get_auth_store(prefer_keyring=True)
        key_id = f"webdav:token:{username}@{url}"

        store.store_secret(key_id, token)
        print(f"✓ Credentials saved to {store.strategy}")

    except Exception as e:
        print(f"⚠ Failed to save to keyring: {e}")
        print("ℹ️  Set HEIBOX_WEBDAV_TOKEN env var instead")

    # Step 6: Update config file
    from mini_datahub.infra.config_paths import get_config_path
    import tomli_w

    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "auth": {
            "method": "webdav",
            "url": url,
            "username": username,
            "stored_in": store.strategy,
            "key_id": key_id,
        }
    }

    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    print(f"✓ Configuration saved to {config_path}\n")
    print("🎉 Setup complete! Try: hei-datahub")

    return 0
```

**Usage:**

```bash
$ hei-datahub auth setup

🔐 WebDAV Authentication Setup

Enter WebDAV URL:
  Example: https://heibox.uni-heidelberg.de/seafdav
URL: https://heibox.uni-heidelberg.de/seafdav
Username: user123
Token/Password: ••••••••

Testing connection...
✓ Connection successful! Found 3 items

Saving credentials...
✓ Credentials saved to keyring
✓ Configuration saved to ~/.config/hei-datahub/config.toml

🎉 Setup complete! Try: hei-datahub
```

---

## Diagnostic Commands

**Goal:** Help users troubleshoot issues.

### Example: Auth Status

```python
def handle_auth_status(args):
    """Handle auth status command."""
    from mini_datahub.infra.config_paths import get_config_path
    from pathlib import Path

    config_path = get_config_path()

    # Check if config exists
    if not config_path.exists():
        print("❌ No authentication configured.")
        print(f"   Config file not found: {config_path}")
        print("\nRun: hei-datahub auth setup")
        sys.exit(1)

    # Load config
    try:
        import tomllib as tomli
    except ImportError:
        import tomli

    with open(config_path, "rb") as f:
        config = tomli.load(f)

    auth_config = config.get("auth", {})

    if not auth_config:
        print("❌ No [auth] section in config")
        sys.exit(1)

    # Display status
    print("🔐 WebDAV Authentication Status\n")
    print(f"Method:     {auth_config.get('method', 'unknown')}")
    print(f"URL:        {auth_config.get('url', 'unknown')}")
    print(f"Username:   {auth_config.get('username', '-')}")
    print(f"Storage:    {auth_config.get('stored_in', 'unknown')}")
    print(f"Key ID:     {auth_config.get('key_id', 'unknown')}")
    print(f"\nConfig:     {config_path}")

    sys.exit(0)
```

**Usage:**

```bash
$ hei-datahub auth status

🔐 WebDAV Authentication Status

Method:     webdav
URL:        https://heibox.uni-heidelberg.de/seafdav
Username:   user123
Storage:    keyring
Key ID:     webdav:token:user123@heibox.uni-heidelberg.de

Config:     /home/user/.config/hei-datahub/config.toml
```

---

### Example: Doctor Command

```python
def handle_doctor(args):
    """Run diagnostic checks."""
    from mini_datahub.infra.paths import DATA_DIR, DB_PATH, CONFIG_DIR
    from mini_datahub.infra.db import get_connection

    print("🩺 Hei-DataHub Diagnostics\n")

    # Check 1: Data directory
    print("📁 Data Directory")
    if DATA_DIR.exists():
        dataset_count = len([d for d in DATA_DIR.iterdir() if d.is_dir()])
        print(f"   ✓ {DATA_DIR}")
        print(f"   ✓ {dataset_count} datasets found")
    else:
        print(f"   ✗ Not found: {DATA_DIR}")
        print(f"   ℹ️  Will be created on first use")

    print()

    # Check 2: Database
    print("🗄️  Database")
    if DB_PATH.exists():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM datasets_fts")
            count = cursor.fetchone()[0]
            print(f"   ✓ {DB_PATH}")
            print(f"   ✓ {count} datasets indexed")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    else:
        print(f"   ✗ Not found: {DB_PATH}")
        print(f"   ℹ️  Run: hei-datahub reindex")

    print()

    # Check 3: Configuration
    print("⚙️  Configuration")
    config_file = CONFIG_DIR / "config.toml"
    if config_file.exists():
        print(f"   ✓ {config_file}")
    else:
        print(f"   ✗ Not found: {config_file}")
        print(f"   ℹ️  Using defaults")

    print()

    # Check 4: Authentication
    print("🔐 Authentication")
    try:
        from mini_datahub.auth.credentials import get_auth_store

        store = get_auth_store()
        print(f"   ✓ Using {store.strategy}")

        if store.strategy == "keyring":
            print(f"   ✓ Keyring available")
        else:
            print(f"   ℹ️  Using environment variables")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n✓ Diagnostics complete")
```

**Usage:**

```bash
$ hei-datahub doctor

🩺 Hei-DataHub Diagnostics

📁 Data Directory
   ✓ /home/user/.local/share/hei-datahub/datasets
   ✓ 15 datasets found

🗄️  Database
   ✓ /home/user/.local/share/hei-datahub/db.sqlite
   ✓ 15 datasets indexed

⚙️  Configuration
   ✓ /home/user/.config/hei-datahub/config.toml

🔐 Authentication
   ✓ Using keyring
   ✓ Keyring available

✓ Diagnostics complete
```

---

## Error Handling Best Practices

### 1. Exit Codes

```python
# Success
sys.exit(0)

# User error (bad input, missing file)
sys.exit(1)

# System error (permission denied, network error)
sys.exit(2)
```

---

### 2. User-Friendly Messages

```python
# ❌ Bad
print("FileNotFoundError: [Errno 2] No such file or directory: '/tmp/data.yaml'")

# ✅ Good
print("❌ Dataset not found: /tmp/data.yaml")
print("   Try: hei-datahub reindex")
```

---

### 3. Colored Output

```python
from rich.console import Console

console = Console()

# Success (green)
console.print("✓ Operation successful", style="green")

# Warning (yellow)
console.print("⚠ Warning: Using fallback", style="yellow")

# Error (red)
console.print("❌ Error: Connection failed", style="red")

# Info (blue)
console.print("ℹ️  Tip: Use --help for options", style="blue")
```

---

## Testing CLI Commands

```python
# File: tests/cli/test_reindex.py

import subprocess
import sys

def test_reindex_command():
    """Test reindex command."""
    result = subprocess.run(
        [sys.executable, "-m", "mini_datahub.cli.main", "reindex"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Successfully indexed" in result.stdout


def test_auth_status_no_config():
    """Test auth status with missing config."""
    result = subprocess.run(
        [sys.executable, "-m", "mini_datahub.cli.main", "auth", "status"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "No authentication configured" in result.stdout
```

---

## What You've Learned

✅ **CLI structure** — Main parser + subparsers + handlers
✅ **Handler pattern** — Validate → call services → format output
✅ **Interactive wizards** — Multi-step guided setup
✅ **Diagnostic commands** — Help users troubleshoot
✅ **Error handling** — Exit codes, user-friendly messages
✅ **Testing** — Subprocess-based CLI tests

---

## Try It Yourself

### Exercise 1: Add `list` Command

**Goal:** List all datasets with IDs and names.

```python
def handle_list(args):
    """List all datasets."""
    from mini_datahub.infra.index import list_all_datasets

    datasets = list_all_datasets()

    if not datasets:
        print("No datasets found")
        sys.exit(0)

    print(f"Found {len(datasets)} dataset(s):\n")

    for ds in datasets:
        metadata = ds.get('metadata', {})
        name = metadata.get('dataset_name', 'Unknown')
        print(f"  {ds['id']:30} {name}")

    sys.exit(0)
```

**Add to parser:**

```python
list_parser = subparsers.add_parser("list", help="List all datasets")
```

**Usage:**

```bash
$ hei-datahub list

Found 3 dataset(s):

  climate-data-2023              Climate Data Analysis 2023
  covid-tracker                  COVID-19 Tracker
  gideon-analysis                Gideon Project Analysis
```

---

### Exercise 2: Add `export` Command

**Goal:** Export dataset metadata to JSON.

```python
def handle_export(args):
    """Export dataset to JSON."""
    import json
    from mini_datahub.infra.index import get_dataset_from_store

    dataset_id = args.dataset_id
    output_file = args.output or f"{dataset_id}.json"

    # Get dataset
    metadata = get_dataset_from_store(dataset_id)

    if not metadata:
        print(f"❌ Dataset not found: {dataset_id}")
        sys.exit(1)

    # Write JSON
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Exported to {output_file}")
    sys.exit(0)
```

---

### Exercise 3: Add Progress Bars

**Goal:** Show progress during reindex.

```python
from tqdm import tqdm

def handle_reindex(args):
    dataset_ids = list_datasets()

    with tqdm(total=len(dataset_ids), desc="Indexing") as pbar:
        for dataset_id in dataset_ids:
            metadata = read_dataset(dataset_id)
            upsert_dataset(dataset_id, metadata)
            pbar.update(1)

    print("✓ Reindex complete")
```

---

## Next Steps

Congratulations! You've completed the **Logic** section. Now let's dive deep into the codebase structure.

**Next:** [Directory Structure Deep Dive](../deep/01-directory-structure.md)

---

## Further Reading

- [Python argparse Tutorial](https://docs.python.org/3/howto/argparse.html)
- [Click Framework](https://click.palletsprojects.com/) (alternative to argparse)
- [Rich Console](https://rich.readthedocs.io/) (beautiful terminal output)
- [Hei-DataHub CLI Reference](../../api-reference/cli-commands.md)
