"""
Path management and constants for Hei-DataHub.
"""
from pathlib import Path

# Project root (where pyproject.toml lives)
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory (one folder per dataset)
DATA_DIR = PROJECT_ROOT / "data"

# Database path
DB_PATH = PROJECT_ROOT / "db.sqlite"

# JSON Schema path
SCHEMA_PATH = PROJECT_ROOT / "schema.json"

# SQL schema path
SQL_SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def ensure_directories():
    """Ensure required directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "sql").mkdir(parents=True, exist_ok=True)
