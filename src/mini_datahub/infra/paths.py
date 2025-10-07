"""
Centralized path management for Hei-DataHub.
All file system paths are defined here.

XDG Base Directory Specification compliant:
- Config: ~/.config/hei-datahub/
- Data: ~/.local/share/hei-datahub/
- Cache: ~/.cache/hei-datahub/
- State: ~/.local/state/hei-datahub/
"""
from pathlib import Path
import os

def _is_installed_package() -> bool:
    """Check if running from an installed package (not development mode)."""
    package_path = Path(__file__).resolve()
    return "site-packages" in str(package_path) or ".local/share/uv" in str(package_path)

def _is_dev_mode() -> bool:
    """Check if running from repository (development mode)."""
    cwd = Path.cwd()
    return (cwd / "src" / "mini_datahub").exists() and (cwd / "pyproject.toml").exists()

# XDG Base Directory paths (for installed package)
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
XDG_DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
XDG_CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
XDG_STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))

# Determine base directories based on install mode
if _is_installed_package():
    # Installed package: Use XDG directories (completely standalone)
    CONFIG_DIR = XDG_CONFIG_HOME / "hei-datahub"
    DATA_DIR = XDG_DATA_HOME / "hei-datahub" / "datasets"
    CACHE_DIR = XDG_CACHE_HOME / "hei-datahub"
    STATE_DIR = XDG_STATE_HOME / "hei-datahub"
    PROJECT_ROOT = XDG_DATA_HOME / "hei-datahub"
elif _is_dev_mode():
    # Development mode: Use repository
    PROJECT_ROOT = Path.cwd()
    CONFIG_DIR = PROJECT_ROOT
    DATA_DIR = PROJECT_ROOT / "data"
    CACHE_DIR = PROJECT_ROOT / ".cache"
    STATE_DIR = PROJECT_ROOT
else:
    # Fallback: Use XDG directories
    CONFIG_DIR = XDG_CONFIG_HOME / "hei-datahub"
    DATA_DIR = XDG_DATA_HOME / "hei-datahub" / "datasets"
    CACHE_DIR = XDG_CACHE_HOME / "hei-datahub"
    STATE_DIR = XDG_STATE_HOME / "hei-datahub"
    PROJECT_ROOT = XDG_DATA_HOME / "hei-datahub"

# Database (in data directory per XDG)
DB_PATH = XDG_DATA_HOME / "hei-datahub" / "db.sqlite" if _is_installed_package() else PROJECT_ROOT / "db.sqlite"

# Schema paths
def _get_schema_path() -> Path:
    """Get schema.json path."""
    if _is_installed_package():
        # Installed: Use packaged schema, copy to data dir if needed
        user_schema = XDG_DATA_HOME / "hei-datahub" / "schema.json"
        if user_schema.exists():
            return user_schema
        # Return packaged schema path
        return Path(__file__).parent.parent / "schema.json"
    else:
        # Dev mode: Use repo schema
        return PROJECT_ROOT / "schema.json"

SCHEMA_JSON = _get_schema_path()

# SQL schema (always packaged)
SQL_SCHEMA_PATH = Path(__file__).parent / "sql" / "schema.sql"

# Config files
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYMAP_FILE = CONFIG_DIR / "keymap.json"

# Logs
LOG_DIR = STATE_DIR / "logs"

# Outbox for failed operations
OUTBOX_DIR = STATE_DIR / "outbox"

# Assets (templates, etc.)
ASSETS_DIR = XDG_DATA_HOME / "hei-datahub" / "assets" if _is_installed_package() else PROJECT_ROOT / "assets"

# Keyring settings
KEYRING_SERVICE = "mini-datahub"
KEYRING_USERNAME = "github-token"


def ensure_directories():
    """Ensure all required directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    if _is_installed_package():
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def initialize_workspace():
    """Initialize application on first run (for installed package)."""
    if not _is_installed_package():
        # In dev mode, just ensure directories exist
        ensure_directories()
        return

    # Ensure all directories exist
    ensure_directories()

    # Copy schema.json to user data directory
    user_schema = XDG_DATA_HOME / "hei-datahub" / "schema.json"
    if not user_schema.exists():
        try:
            package_schema = Path(__file__).parent.parent / "schema.json"
            if package_schema.exists():
                import shutil
                shutil.copy(package_schema, user_schema)
                print(f"✓ Initialized schema at {user_schema}")
        except Exception as e:
            print(f"⚠ Could not copy schema: {e}")

    # Copy packaged datasets on first run
    if not list(DATA_DIR.iterdir()):
        try:
            packaged_data = Path(__file__).parent.parent / "data"
            if packaged_data.exists() and list(packaged_data.iterdir()):
                import shutil
                dataset_count = 0
                for item in packaged_data.iterdir():
                    if item.is_dir():
                        dest = DATA_DIR / item.name
                        if not dest.exists():
                            shutil.copytree(item, dest)
                            dataset_count += 1
                if dataset_count > 0:
                    print(f"✓ Initialized {dataset_count} datasets in {DATA_DIR}")
                    print("  Indexing datasets...")
                    # Trigger reindex after copying datasets
                    try:
                        from mini_datahub.services.store import DatasetStore
                        store = DatasetStore()
                        store.reindex()
                        print(f"  ✓ Indexed {dataset_count} datasets")
                    except Exception as reindex_error:
                        print(f"  ⚠ Please run 'hei-datahub reindex' to index datasets")
        except Exception as e:
            print(f"⚠ Could not copy datasets: {e}")

    # Copy assets/templates if they exist
    try:
        packaged_templates = Path(__file__).parent.parent / "templates"
        if packaged_templates.exists():
            import shutil
            templates_dest = ASSETS_DIR / "templates"
            if not templates_dest.exists():
                shutil.copytree(packaged_templates, templates_dest)
                print(f"✓ Initialized templates in {ASSETS_DIR}")
    except Exception as e:
        pass  # Templates are optional


def get_schema_sql() -> str:
    """Load SQL schema from package."""
    return SQL_SCHEMA_PATH.read_text()
