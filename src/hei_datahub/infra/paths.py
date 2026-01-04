r"""
Centralized path management for Hei-DataHub.
All file system paths are defined here.

Cross-platform directory support:
- Linux: XDG Base Directory Specification (~/.local/share/Hei-DataHub)
- macOS: ~/Library/Application Support/Hei-DataHub
- Windows: %LOCALAPPDATA%\Hei-DataHub

Config still uses XDG on all platforms:
- Config: ~/.config/hei-datahub/
- Cache: ~/.cache/hei-datahub/
- State: ~/.local/state/hei-datahub/
"""
from pathlib import Path
import os
import sys

def _is_installed_package() -> bool:
    """Check if running from an installed package (not development mode)."""
    package_path = Path(__file__).resolve()
    return "site-packages" in str(package_path) or ".local/share/uv" in str(package_path)

def _is_dev_mode() -> bool:
    """Check if running from repository (development mode).

    This checks if the code is being imported from a repository structure
    (not from an installed package), regardless of the current working directory.
    """
    package_path = Path(__file__).resolve()
    # Check if __file__ is in a repo structure (has src/hei_datahub parent)
    try:
        # If we're in: /path/to/repo/src/hei_datahub/infra/paths.py
        # Then go up 4 levels: infra -> hei_datahub -> src -> repo_root
        potential_repo = package_path.parent.parent.parent.parent
        return (
            (potential_repo / "src" / "hei_datahub").exists() and
            (potential_repo / "pyproject.toml").exists() and
            "site-packages" not in str(package_path)
        )
    except:
        return False

# XDG Base Directory paths (for config/cache/state - used on all platforms)
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
XDG_DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
XDG_CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
XDG_STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))

# Get CLI override from command line args (if available)
_CLI_DATA_DIR_OVERRIDE = None
for i, arg in enumerate(sys.argv):
    if arg == '--data-dir' and i + 1 < len(sys.argv):
        _CLI_DATA_DIR_OVERRIDE = sys.argv[i + 1]
        break

# Determine base directories based on install mode
if _is_installed_package():
    # Installed package: Use platform-aware data directory
    from hei_datahub.infra.platform_paths import resolve_data_directory
    PLATFORM_DATA_DIR, _ = resolve_data_directory(_CLI_DATA_DIR_OVERRIDE)

    CONFIG_DIR = XDG_CONFIG_HOME / "hei-datahub"
    DATA_DIR = PLATFORM_DATA_DIR / "datasets"
    CACHE_DIR = XDG_CACHE_HOME / "hei-datahub"
    STATE_DIR = XDG_STATE_HOME / "hei-datahub"
    PROJECT_ROOT = PLATFORM_DATA_DIR
elif _is_dev_mode():
    # Development mode: Use repository (derive from __file__, not cwd)
    package_path = Path(__file__).resolve()
    # Go up 4 levels: infra -> hei_datahub -> src -> repo_root
    PROJECT_ROOT = package_path.parent.parent.parent.parent
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

# Database (in data directory)
DB_PATH = PROJECT_ROOT / "db.sqlite"

# Schema paths
def _get_schema_path() -> Path:
    """Get schema.json path."""
    if _is_installed_package():
        # Installed: Use packaged schema, copy to data dir if needed
        user_schema = PROJECT_ROOT / "schema.json"
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
ASSETS_DIR = PROJECT_ROOT / "assets" if _is_installed_package() else PROJECT_ROOT / "assets"

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
    user_schema = PROJECT_ROOT / "schema.json"
    if not user_schema.exists():
        try:
            package_schema = Path(__file__).parent.parent / "schema.json"
            if package_schema.exists():
                import shutil
                shutil.copy(package_schema, user_schema)
                print(f"✓ Initialized schema at {user_schema}")
        except Exception as e:
            print(f"⚠ Could not copy schema: {e}")

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
