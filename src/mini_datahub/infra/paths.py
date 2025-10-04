"""
Centralized path management for Hei-DataHub.
All file system paths are defined here.
"""
from pathlib import Path
import os

# Project root (where pyproject.toml lives)
# In src/ layout, we need to go up 2 levels: src/mini_datahub -> src -> root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Data directory (one folder per dataset)
DATA_DIR = PROJECT_ROOT / "data"

# Database and cache
CACHE_DIR = PROJECT_ROOT / ".cache"
DB_PATH = PROJECT_ROOT / "db.sqlite"  # Root level for backward compatibility

# JSON Schema path
SCHEMA_JSON = PROJECT_ROOT / "schema.json"

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


def get_schema_sql() -> str:
    """Load SQL schema from package."""
    return SQL_SCHEMA_PATH.read_text()
