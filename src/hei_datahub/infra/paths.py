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
import os
import sys
from pathlib import Path


def _is_installed_package() -> bool:
    """Check if running from an installed package (not development mode)."""
    if getattr(sys, 'frozen', False):
        return True
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
    except Exception:
        return False

# XDG Base Directory paths (for config/cache/state - used on all platforms)
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
XDG_CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
XDG_STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))

# Determine base directories based on install mode
if _is_installed_package():
    # Installed package: Use platform-aware data directory
    from hei_datahub.infra.platform_paths import resolve_data_directory
    PLATFORM_DATA_DIR, _ = resolve_data_directory(None)

    CONFIG_DIR = XDG_CONFIG_HOME / "hei-datahub"
    CACHE_DIR = XDG_CACHE_HOME / "hei-datahub"
    DATA_DIR = CACHE_DIR / "datasets"  # Treat local data as cache
    STATE_DIR = XDG_STATE_HOME / "hei-datahub"
    PROJECT_ROOT = PLATFORM_DATA_DIR
elif _is_dev_mode():
    # Development mode: Use repository (derive from __file__, not cwd)
    package_path = Path(__file__).resolve()
    # Go up 4 levels: infra -> hei_datahub -> src -> repo_root
    PROJECT_ROOT = package_path.parent.parent.parent.parent
    CONFIG_DIR = PROJECT_ROOT
    CACHE_DIR = PROJECT_ROOT / ".cache"
    DATA_DIR = CACHE_DIR / "datasets"
    STATE_DIR = PROJECT_ROOT
else:
    # Fallback: Use XDG directories
    CONFIG_DIR = XDG_CONFIG_HOME / "hei-datahub"
    CACHE_DIR = XDG_CACHE_HOME / "hei-datahub"
    DATA_DIR = CACHE_DIR / "datasets"
    STATE_DIR = XDG_STATE_HOME / "hei-datahub"
    PROJECT_ROOT = CACHE_DIR

# Database (in data directory)
DB_PATH = PROJECT_ROOT / "db.sqlite"


def get_data_dir() -> Path:
    """Get the root data directory."""
    if _is_installed_package():
        from hei_datahub.infra.platform_paths import resolve_data_directory
        path, _ = resolve_data_directory(None)
        return path
    elif _is_dev_mode():
        return PROJECT_ROOT
    else:
        return CACHE_DIR

# Schema paths
def _get_schema_path() -> Path:
    """Get schema.json path.

    Always prefer the packaged schema (shipped with the code) to avoid
    stale copies in user-data directories causing validation errors.
    """
    if _is_installed_package():
        # Check if PyInstaller bundled
        if getattr(sys, 'frozen', False):
             # sys._MEIPASS is the temp folder where PyInstaller extracts files
             bundled_schema = Path(sys._MEIPASS) / "hei_datahub" / "schema.json"
             if bundled_schema.exists():
                 return bundled_schema
             # Fallback check
             bundled_schema_root = Path(sys._MEIPASS) / "schema.json"
             if bundled_schema_root.exists():
                 return bundled_schema_root

        # Installed: always use the packaged schema (stays in sync with code)
        packaged_schema = Path(__file__).parent.parent / "schema.json"
        if packaged_schema.exists():
            return packaged_schema

        # Fallback: user-data directory (legacy)
        user_schema = PROJECT_ROOT / "schema.json"
        if user_schema.exists():
            return user_schema

        return packaged_schema
    else:
        # Dev mode: Use repo schema
        return PROJECT_ROOT / "schema.json"

SCHEMA_JSON = _get_schema_path()

# SQL schema (always packaged)
SQL_SCHEMA_PATH = Path(__file__).parent / "sql" / "schema.sql"

# Config files
CONFIG_FILE = CONFIG_DIR / "config.yaml"
KEYMAP_FILE = CONFIG_DIR / "keybindings.yaml"

# Logs
LOG_DIR = STATE_DIR / "logs"

# Assets (templates, etc.)
ASSETS_DIR = PROJECT_ROOT / "assets" if _is_installed_package() else PROJECT_ROOT / "assets"

# Keyring settings
KEYRING_SERVICE = "hei-datahub"
KEYRING_USERNAME = "github-token"


def ensure_directories():
    """Ensure all required directories exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
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
            if getattr(sys, 'frozen', False):
                 # Handle PyInstaller path
                 package_schema = Path(sys._MEIPASS) / "hei_datahub" / "schema.json"
                 if not package_schema.exists():
                     package_schema = Path(sys._MEIPASS) / "schema.json"
            else:
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
    except Exception:
        pass  # Templates are optional


def get_schema_sql() -> str:
    """Load SQL schema from package."""
    return SQL_SCHEMA_PATH.read_text()
