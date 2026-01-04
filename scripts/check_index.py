#!/usr/bin/env python3
"""
Quick script to check what's actually in the search index.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mini_datahub.services.index_service import get_index_service


def main():
    index = get_index_service()

    # Get all items
    results = index.search("", None, limit=100)

    print(f"Total items in index: {len(results)}")
    print("\n" + "=" * 80)

    for item in results:
        is_remote = item.get('is_remote', False)
        remote_indicator = "☁️" if is_remote else "📁"

        print(f"{remote_indicator} {item['path']}")
        print(f"   Name: {item['name']}")
        print(f"   Description: {item.get('description', 'N/A')[:60]}...")
        print(f"   Remote: {is_remote}")
        print()

if __name__ == "__main__":
    main()
