#!/usr/bin/env python3
"""
Force rebuild the search index.

This script will:
1. Delete the existing index
2. Rebuild from scratch (local + remote)

Usage:
    python scripts/rebuild_index.py
"""
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def rebuild_index():
    """Rebuild the search index from scratch."""
    from mini_datahub.services.index_service import get_index_service, INDEX_DB_PATH
    from mini_datahub.services.indexer import BackgroundIndexer

    print("=" * 60)
    print("REBUILDING SEARCH INDEX")
    print("=" * 60)

    # Delete existing index
    if INDEX_DB_PATH.exists():
        print(f"\n🗑️  Deleting existing index: {INDEX_DB_PATH}")
        INDEX_DB_PATH.unlink()
    else:
        print(f"\n📝 No existing index found at {INDEX_DB_PATH}")

    # Create new index service (will initialize fresh DB)
    print("\n🔨 Creating new index database...")
    index_service = get_index_service()

    # Create indexer and run full index
    print("\n📥 Starting indexer...")
    indexer = BackgroundIndexer()

    # Force full index by clearing metadata
    index_service.set_meta("last_full_index", "0")

    # Run indexing
    print("\n⏳ Indexing local datasets...")
    await indexer._index_local_datasets()

    print("\n⏳ Indexing remote datasets (this may take a while)...")
    await indexer._index_remote_datasets()

    # Get final count
    total, remote = index_service.get_item_count()

    print("\n" + "=" * 60)
    print("✅ INDEX REBUILT SUCCESSFULLY")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   Total items: {total}")
    print(f"   Remote items: {remote}")
    print(f"   Local items: {total - remote}")
    print(f"\n💾 Index location: {INDEX_DB_PATH}")
    print(f"   Size: {INDEX_DB_PATH.stat().st_size / 1024:.1f} KB")
    print("\n✨ Index is ready to use!")
    print()


if __name__ == "__main__":
    print("\n🚀 Hei-DataHub Index Rebuild Tool\n")
    asyncio.run(rebuild_index())
