"""
Background indexer service for building and maintaining the search index.
Runs asynchronously without blocking the UI.
"""
import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from mini_datahub.services.index_service import get_index_service, SYNC_INTERVAL_SEC
from mini_datahub.infra.paths import DATA_DIR

logger = logging.getLogger(__name__)


class BackgroundIndexer:
    """Background indexer that scans local and remote datasets."""

    def __init__(self):
        """Initialize background indexer."""
        self.index_service = get_index_service()
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False
        self._local_indexed = False
        self._remote_indexed = False

    async def start(self) -> None:
        """Start background indexing."""
        if self._running:
            logger.warning("Background indexer already running")
            return

        self._running = True
        logger.info("Starting background indexer")

        # Start initial index build (non-blocking)
        asyncio.create_task(self._initial_index())

        # Start periodic sync task
        self._sync_task = asyncio.create_task(self._sync_loop())

    async def stop(self) -> None:
        """Stop background indexing."""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info("Background indexer stopped")

    async def _initial_index(self) -> None:
        """Perform initial index build."""
        try:
            # Always do local indexing (fast)
            await self._index_local_datasets()
            self._local_indexed = True

            # Check if we need full remote indexing
            last_index = self.index_service.get_meta("last_full_index")
            total, remote = self.index_service.get_item_count()

            # Do full remote index if:
            # 1. Never indexed before, OR
            # 2. No remote items in index, OR
            # 3. Last full index was >7 days ago
            should_full_index = (
                not last_index or
                remote == 0 or
                self._should_reindex()
            )

            if should_full_index:
                logger.info("Performing full remote index")
                await self._index_remote_datasets()
                self._remote_indexed = True
                self.index_service.set_meta("last_full_index", str(int(time.time())))
            else:
                # Do incremental sync (faster, but less thorough)
                logger.info("Performing incremental remote sync")
                await self._incremental_remote_sync()
                self._remote_indexed = True

            total, remote = self.index_service.get_item_count()
            logger.info(f"Index ready: {total} items ({remote} remote)")

        except Exception as e:
            logger.error(f"Initial indexing failed: {e}", exc_info=True)

    def _should_reindex(self) -> bool:
        """Check if full reindex is needed."""
        last_index = self.index_service.get_meta("last_full_index")
        if not last_index:
            return True

        # Reindex if last full index was >7 days ago
        last_time = int(last_index)
        return (time.time() - last_time) > (7 * 24 * 3600)

    async def _index_local_datasets(self) -> None:
        """Index local datasets from DATA_DIR."""
        if not DATA_DIR.exists():
            logger.debug("No local data directory, skipping local index")
            return

        logger.info(f"Indexing local datasets from {DATA_DIR}")
        items = []

        try:
            # Scan local data directory
            for dataset_dir in DATA_DIR.iterdir():
                if not dataset_dir.is_dir():
                    continue

                metadata_file = dataset_dir / "metadata.yaml"
                if not metadata_file.exists():
                    # Index directory without metadata
                    items.append({
                        "path": dataset_dir.name,
                        "name": dataset_dir.name,
                        "is_remote": False,
                        "mtime": int(dataset_dir.stat().st_mtime),
                        "size": self._get_dir_size(dataset_dir),
                    })
                    continue

                # Parse metadata
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = yaml.safe_load(f) or {}

                    # Extract fields
                    name = metadata.get("name", dataset_dir.name)
                    description = metadata.get("description", "")
                    keywords = metadata.get("keywords", [])
                    tags = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
                    project = metadata.get("project")
                    file_format = metadata.get("format")
                    source = metadata.get("source")

                    items.append({
                        "path": dataset_dir.name,
                        "name": name,
                        "is_remote": False,
                        "mtime": int(metadata_file.stat().st_mtime),
                        "size": self._get_dir_size(dataset_dir),
                        "project": project,
                        "tags": tags,
                        "description": description,
                        "format": file_format,
                        "source": source,
                    })

                except Exception as e:
                    logger.warning(f"Failed to parse metadata for {dataset_dir.name}: {e}")
                    # Index with basic info
                    items.append({
                        "path": dataset_dir.name,
                        "name": dataset_dir.name,
                        "is_remote": False,
                        "mtime": int(dataset_dir.stat().st_mtime),
                        "size": self._get_dir_size(dataset_dir),
                    })

            # Bulk insert
            if items:
                count = self.index_service.bulk_upsert(items)
                logger.info(f"Indexed {count} local datasets")

        except Exception as e:
            logger.error(f"Local indexing failed: {e}", exc_info=True)

    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total

    async def _index_remote_datasets(self) -> None:
        """Index remote datasets from WebDAV (shallow listing)."""
        try:
            from mini_datahub.services.config import get_config
            from mini_datahub.services.storage_manager import get_storage_backend

            config = get_config()
            storage_backend = config.get("storage.backend", "filesystem")

            if storage_backend != "webdav":
                logger.debug("Not using WebDAV backend, skipping remote index")
                return

            logger.info("Indexing remote datasets from WebDAV")
            storage = get_storage_backend()

            # List top-level directories (datasets)
            entries = await asyncio.to_thread(storage.listdir, "")
            datasets = [e for e in entries if e.is_dir]

            count = 0
            for entry in datasets:
                try:
                    # Get metadata.yaml if it exists
                    metadata_path = f"{entry.name}/metadata.yaml"
                    metadata = await self._fetch_metadata(storage, metadata_path)

                    if metadata:
                        name = metadata.get("name", entry.name)
                        description = metadata.get("description", "")
                        keywords = metadata.get("keywords", [])
                        tags = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
                        project = metadata.get("project")
                        file_format = metadata.get("format")
                        source = metadata.get("source")
                    else:
                        name = entry.name
                        description = ""
                        tags = ""
                        project = None
                        file_format = None
                        source = None

                    item = {
                        "path": entry.name,
                        "name": name,
                        "is_remote": True,
                        "size": entry.size or 0,
                        "mtime": int(entry.modified.timestamp()) if entry.modified else None,
                        "project": project,
                        "tags": tags,
                        "description": description,
                        "format": file_format,
                        "source": source,
                    }

                    # Insert immediately so it shows up in UI right away
                    self.index_service.upsert_item(
                        path=item["path"],
                        name=item["name"],
                        project=item.get("project"),
                        tags=item["tags"],
                        description=item["description"],
                        format=item.get("format"),
                        source=item.get("source"),
                        is_remote=item["is_remote"],
                        size=item.get("size"),
                        mtime=item.get("mtime"),
                    )
                    count += 1
                    logger.info(f"Indexed dataset {count}/{len(datasets)}: {name}")

                except Exception as e:
                    logger.warning(f"Failed to index remote dataset {entry.name}: {e}")
                    # Index with basic info
                    try:
                        self.index_service.upsert_item(
                            path=entry.name,
                            name=entry.name,
                            is_remote=True,
                            size=entry.size or 0,
                            mtime=int(entry.modified.timestamp()) if entry.modified else None,
                        )
                        count += 1
                    except:
                        pass

            logger.info(f"Indexed {count} remote datasets")

        except Exception as e:
            logger.error(f"Remote indexing failed: {e}", exc_info=True)

    async def _fetch_metadata(self, storage, metadata_path: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse metadata.yaml from remote storage."""
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                tmp_path = tmp.name

            try:
                await asyncio.to_thread(storage.download, metadata_path, tmp_path)

                with open(tmp_path, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)

                return metadata
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            logger.debug(f"Could not fetch metadata from {metadata_path}: {e}")
            return None

    async def _incremental_remote_sync(self) -> None:
        """Perform incremental sync of remote datasets (fetches metadata for all)."""
        try:
            from mini_datahub.services.config import get_config
            from mini_datahub.services.storage_manager import get_storage_backend

            config = get_config()
            storage_backend = config.get("storage.backend", "filesystem")

            if storage_backend != "webdav":
                return

            logger.info("Performing incremental remote sync (with metadata)")
            storage = get_storage_backend()

            # Get current remote entries
            entries = await asyncio.to_thread(storage.listdir, "")
            datasets = [e for e in entries if e.is_dir]

            # Fetch metadata for each dataset (same as full index)
            items = []
            for entry in datasets:
                try:
                    # Get metadata.yaml if it exists
                    metadata_path = f"{entry.name}/metadata.yaml"
                    metadata = await self._fetch_metadata(storage, metadata_path)

                    if metadata:
                        name = metadata.get("name", entry.name)
                        description = metadata.get("description", "")
                        keywords = metadata.get("keywords", [])
                        tags = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
                        project = metadata.get("project")
                        file_format = metadata.get("format")
                        source = metadata.get("source")
                    else:
                        name = entry.name
                        description = ""
                        tags = ""
                        project = None
                        file_format = None
                        source = None

                    items.append({
                        "path": entry.name,
                        "name": name,
                        "is_remote": True,
                        "size": entry.size or 0,
                        "mtime": int(entry.modified.timestamp()) if entry.modified else None,
                        "project": project,
                        "tags": tags,
                        "description": description,
                        "format": file_format,
                        "source": source,
                    })

                except Exception as e:
                    logger.warning(f"Failed to sync remote dataset {entry.name}: {e}")
                    # Index with basic info
                    items.append({
                        "path": entry.name,
                        "name": entry.name,
                        "is_remote": True,
                        "size": entry.size or 0,
                        "mtime": int(entry.modified.timestamp()) if entry.modified else None,
                    })

            if items:
                count = self.index_service.bulk_upsert(items)
                logger.info(f"Incrementally synced {count} remote datasets")

        except Exception as e:
            logger.error(f"Incremental sync failed: {e}", exc_info=True)

    async def _sync_loop(self) -> None:
        """Periodic sync loop."""
        while self._running:
            try:
                await asyncio.sleep(SYNC_INTERVAL_SEC)

                if not self._running:
                    break

                logger.debug("Running periodic index sync")
                await self._incremental_remote_sync()
                self.index_service.set_meta("last_sync", str(int(time.time())))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}", exc_info=True)

    def is_ready(self) -> bool:
        """Check if initial indexing is complete."""
        return self._local_indexed or self._remote_indexed

    def get_status(self) -> Dict[str, Any]:
        """Get indexer status."""
        total, remote = self.index_service.get_item_count()
        return {
            "running": self._running,
            "local_indexed": self._local_indexed,
            "remote_indexed": self._remote_indexed,
            "total_items": total,
            "remote_items": remote,
            "last_sync": self.index_service.get_meta("last_sync"),
        }


# Global instance
_indexer: Optional[BackgroundIndexer] = None


def get_indexer() -> BackgroundIndexer:
    """Get or create the global indexer instance."""
    global _indexer
    if _indexer is None:
        _indexer = BackgroundIndexer()
    return _indexer


async def start_background_indexer() -> None:
    """Start the background indexer (call this at app startup)."""
    indexer = get_indexer()
    await indexer.start()


async def stop_background_indexer() -> None:
    """Stop the background indexer (call this at app shutdown)."""
    indexer = get_indexer()
    await indexer.stop()
