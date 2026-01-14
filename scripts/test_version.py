#!/usr/bin/env python3
"""
Test script to verify hei_datahub version import.
"""
import sys
from pathlib import Path

# Add src to sys.path to ensure we can import hei_datahub even if not installed
root = Path(__file__).parent.parent
src_path = root / "src"
sys.path.insert(0, str(src_path))

try:
    from hei_datahub.version import __version__
    print(f"Hei-DataHub Version: {__version__}")
except ImportError as e:
    print(f"Failed to import hei_datahub: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
