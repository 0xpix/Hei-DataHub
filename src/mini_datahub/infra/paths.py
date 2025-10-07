"""
Centralized path management for Hei-DataHub.
All file system paths are defined here.
"""
from pathlib import Path
import os

# Determine workspace root
# Priority: 1) Explicit dev mode, 2) CWD with data/, 3) ~/.hei-datahub/
def _get_workspace_root() -> Path:
    """Get the workspace root directory."""
    cwd = Path.cwd()

    # Check if running from source (development mode)
    # Look for src/mini_datahub in the path structure
    is_dev_mode = (cwd / "src" / "mini_datahub").exists() and (cwd / "pyproject.toml").exists()

    # Check for explicit environment variable
    env_workspace = os.environ.get("HEI_DATAHUB_WORKSPACE")
    if env_workspace:
        workspace = Path(env_workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace

    # If in development mode AND has data/, use repo root
    if is_dev_mode and (cwd / "data").exists():
        return cwd

    # If CWD has data/ subdirectory (user's workspace), use it
    if (cwd / "data").exists() and not is_dev_mode:
        return cwd

    # Default: use user's home directory workspace
    home_workspace = Path.home() / ".hei-datahub"
    home_workspace.mkdir(parents=True, exist_ok=True)
    return home_workspace

# Workspace root - where data lives
PROJECT_ROOT = _get_workspace_root()

# Data directory (one folder per dataset)
DATA_DIR = PROJECT_ROOT / "data"

# Database and cache
CACHE_DIR = PROJECT_ROOT / ".cache"
DB_PATH = PROJECT_ROOT / "db.sqlite"

# JSON Schema path - check multiple locations
def _get_schema_path() -> Path:
    """Get schema.json path, checking multiple locations."""
    # 1. Try workspace root
    workspace_schema = PROJECT_ROOT / "schema.json"
    if workspace_schema.exists():
        return workspace_schema

    # 2. Try packaged schema
    package_schema = Path(__file__).parent.parent / "schema.json"
    if package_schema.exists():
        return package_schema

    # 3. Create default in workspace
    return workspace_schema

SCHEMA_JSON = _get_schema_path()

# SQL schema is now packaged
SQL_SCHEMA_PATH = Path(__file__).parent / "sql" / "schema.sql"

# Configuration
CONFIG_DIR = Path.home() / ".mini-datahub"
CONFIG_FILE = PROJECT_ROOT / ".datahub_config.json"  # Legacy location
CONFIG_FILE_NEW = CONFIG_DIR / "config.toml"  # Future location

# Logs
LOG_DIR = CONFIG_DIR / "logs"

# Outbox for failed PRs
OUTBOX_DIR = PROJECT_ROOT / ".outbox"

# Keyring settings
KEYRING_SERVICE = "mini-datahub"
KEYRING_USERNAME = "github-token"


def ensure_directories():
    """Ensure required directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)


def initialize_workspace():
    """Initialize workspace with schema and sample data if needed."""
    # Ensure directories exist
    ensure_directories()

    # Copy schema.json if it doesn't exist
    if not SCHEMA_JSON.exists():
        try:
            # schema.json is in src/mini_datahub/ (parent.parent from infra/)
            package_schema = Path(__file__).parent.parent / "schema.json"
            if package_schema.exists():
                import shutil
                shutil.copy(package_schema, SCHEMA_JSON)
                print(f"✓ Created schema.json at {SCHEMA_JSON}")
        except Exception as e:
            print(f"⚠ Could not copy schema.json: {e}")

    # Copy sample data if data directory is empty
    if DATA_DIR.exists() and not list(DATA_DIR.iterdir()):
        try:
            # templates/ is in src/mini_datahub/ (parent.parent from infra/)
            template_data = Path(__file__).parent.parent / "templates" / "data"
            if template_data.exists():
                import shutil
                for item in template_data.iterdir():
                    dest = DATA_DIR / item.name
                    if not dest.exists():
                        shutil.copytree(item, dest)
                print(f"✓ Initialized sample data in {DATA_DIR}")
        except Exception as e:
            print(f"⚠ Could not copy sample data: {e}")


def get_schema_sql() -> str:
    """Load SQL schema from package."""
    return SQL_SCHEMA_PATH.read_text()
