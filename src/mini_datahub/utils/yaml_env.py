"""
YAML loading utilities with environment variable expansion.

Provides functions to load YAML files with ${ENV_VAR} syntax expansion.
Used for configuration files that reference PROJECT_VERSION and PROJECT_CODENAME.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


def load_yaml_with_env(path: Path | str) -> Dict[str, Any]:
    """
    Load a YAML file with environment variable expansion.
    
    Supports ${VAR_NAME} and ${VAR_NAME:-default} syntax.
    
    Args:
        path: Path to the YAML file
        
    Returns:
        Parsed YAML data with environment variables expanded
        
    Example YAML:
        version: ${PROJECT_VERSION}
        codename: ${PROJECT_CODENAME:-Unnamed}
    """
    path = Path(path) if isinstance(path, str) else path
    
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Expand environment variables in the text
    expanded_text = os.path.expandvars(text)
    
    return yaml.safe_load(expanded_text)


def load_yaml_with_env_safe(path: Path | str, default: Any = None) -> Dict[str, Any]:
    """
    Load a YAML file with environment variable expansion, with error handling.
    
    Args:
        path: Path to the YAML file
        default: Default value to return if file doesn't exist or can't be parsed
        
    Returns:
        Parsed YAML data or default value
    """
    try:
        return load_yaml_with_env(path)
    except Exception:
        return default if default is not None else {}
