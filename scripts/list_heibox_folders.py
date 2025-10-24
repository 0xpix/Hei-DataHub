#!/usr/bin/env python3
"""List all folders on HeiBox."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mini_datahub.services.storage_manager import get_storage_backend

storage = get_storage_backend()
entries = storage.listdir("")
folders = [e.name for e in entries if e.is_dir]

print("Folders on HeiBox:")
for folder in sorted(folders):
    print(f"  - {folder}")
