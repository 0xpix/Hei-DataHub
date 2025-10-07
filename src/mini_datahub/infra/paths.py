"""
Centralized path management for Hei-DataHub.
All file system paths are defined here.
"""
from pathlib import Path
import os

# Determine workspace root
# Priority: 1) CWD if it has data/, 2) ~/.hei-datahub/, 3) fallback to package location
def _get_workspace_root() -> Path:
    """Get the workspace root directory."""
    cwd = Path.cwd()
    
    # If CWD has data/ directory, use it (development mode)
    if (cwd / "data").exists() or (cwd / "pyproject.toml").exists():
        return cwd
    
    # Otherwise use user's home directory workspace
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
    """Initialize workspace with schema and packaged datasets if needed."""
    # Ensure directories exist
    ensure_directories()
    
    # Copy schema.json if it doesn't exist
    if not SCHEMA_JSON.exists():
        try:
            package_schema = Path(__file__).parent / "schema.json"
            if package_schema.exists():
                import shutil
                shutil.copy(package_schema, SCHEMA_JSON)
                print(f"✓ Created schema.json at {SCHEMA_JSON}")
        except Exception as e:
            print(f"⚠ Could not copy schema.json: {e}")
    
    # Copy packaged datasets if data directory is empty
    if DATA_DIR.exists() and not list(DATA_DIR.iterdir()):
        try:
            # Try packaged data first (real datasets)
            package_data = Path(__file__).parent / "data"
            if package_data.exists() and list(package_data.iterdir()):
                import shutil
                for item in package_data.iterdir():
                    dest = DATA_DIR / item.name
                    if not dest.exists():
                        shutil.copytree(item, dest)
                print(f"✓ Initialized datasets in {DATA_DIR}")
            else:
                # Fallback to templates if packaged data doesn't exist
                template_data = Path(__file__).parent / "templates" / "data"
                if template_data.exists():
                    import shutil
                    for item in template_data.iterdir():
                        dest = DATA_DIR / item.name
                        if not dest.exists():
                            shutil.copytree(item, dest)
                    print(f"✓ Initialized sample data in {DATA_DIR}")
        except Exception as e:
            print(f"⚠ Could not copy data: {e}")


def get_schema_sql() -> str:
    """Load SQL schema from package."""
    return SQL_SCHEMA_PATH.read_text()
