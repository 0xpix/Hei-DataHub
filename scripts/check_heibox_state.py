#!/usr/bin/env python3
"""
Quick script to download and show current state of datasets on HeiBox.
"""
import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mini_datahub.services.storage_manager import get_storage_backend

def check_heibox():
    storage = get_storage_backend()

    datasets = ["another-test", "weather", "yet-another-test", "yet-yet-another-test"]

    print("=" * 60)
    print("CURRENT STATE ON HEIBOX")
    print("=" * 60)

    for dataset_name in datasets:
        try:
            # Download to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml', delete=False) as tmp:
                tmp_path = tmp.name

            remote_path = f"{dataset_name}/metadata.yaml"
            storage.download(remote_path, tmp_path)

            # Read the YAML
            with open(tmp_path, 'r') as f:
                metadata = yaml.safe_load(f)

            # Cleanup
            import os
            os.unlink(tmp_path)

            print(f"\n📦 {dataset_name}:")
            print(f"   Name: {metadata.get('name', 'N/A')}")
            print(f"   Description: {metadata.get('description', 'N/A')}")
            print(f"   Tags: {metadata.get('tags', [])}")
            print(f"   Format: {metadata.get('format', 'N/A')}")
        except Exception as e:
            print(f"\n❌ {dataset_name}: ERROR - {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_heibox()
