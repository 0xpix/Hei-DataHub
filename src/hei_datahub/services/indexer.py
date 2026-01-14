"""
Background indexer service for building and maintaining the search index.
Runs asynchronously without blocking the UI.

Cloud-only implementation - indexes datasets from WebDAV storage.
"""
import asyncio
import logging
import os
import time
from typing import Any, Optional

import yaml

from hei_datahub.services.index_service import SYNC_INTERVAL_SEC, get_index_service

logger = logging.getLogger(__name__)


class BackgroundIndexer:
    """Background indexer that scans cloud datasets from WebDAV."""

    def __init__(self):
        """Initialize background indexer."""
        self.index_service = get_index_service()
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False
        self._indexed = False

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
        """Perform initial index build from cloud storage."""
        try:
            # Check if we need full cloud indexing
            last_index = self.index_service.get_meta("last_full_index")
            total = self.index_service.get_item_count()

            # Do full cloud index if:
            # 1. Never indexed before, OR
            # 2. No items in index, OR
            # 3. Last full index was >7 days ago
            should_full_index = (
                not last_index or
                total == 0 or
                self._should_reindex()
            )

            if should_full_index:
                logger.info("Performing full cloud index")
                await self._index_cloud_datasets()
                self.index_service.set_meta("last_full_index", str(int(time.time())))
            else:
                # Do incremental sync (faster, but less thorough)
                logger.info("Performing incremental cloud sync")
                await self._incremental_cloud_sync()

            self._indexed = True
            total = self.index_service.get_item_count()
            logger.info(f"Index ready: {total} cloud datasets")

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

    async def _index_cloud_datasets(self) -> None:
        """Index cloud datasets from WebDAV (shallow listing)."""
        try:
            from hei_datahub.services.storage_manager import get_storage_backend

            logger.info("Indexing cloud datasets from WebDAV")
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
                        # Support both 'tags' and 'keywords' for backwards compatibility
                        tags_list = metadata.get("tags") or metadata.get("keywords", [])
                        tags = " ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
                        # Extract project from used_in_projects list (first one if exists)
                        used_in_projects = metadata.get("used_in_projects", [])
                        project = used_in_projects[0] if used_in_projects else None
                        # Use correct field name: file_format not format
                        file_format = metadata.get("file_format")
                        source = metadata.get("source")
                        category = metadata.get("category")
                        spatial_coverage = metadata.get("spatial_coverage")
                        temporal_coverage = metadata.get("temporal_coverage")
                        access_method = metadata.get("access_method")
                        storage_location = metadata.get("storage_location")
                        reference = metadata.get("reference")
                        spatial_resolution = metadata.get("spatial_resolution")
                        temporal_resolution = metadata.get("temporal_resolution")
                        size = metadata.get("size")
                    else:
                        name = entry.name
                        description = ""
                        tags = ""
                        project = None
                        file_format = None
                        source = None
                        category = None
                        spatial_coverage = None
                        temporal_coverage = None
                        access_method = None
                        storage_location = None
                        reference = None
                        spatial_resolution = None
                        temporal_resolution = None
                        size = None

                    # Insert immediately so it shows up in UI right away
                    # Note: is_remote is always True in cloud-only mode
                    self.index_service.upsert_item(
                        path=entry.name,
                        name=name,
                        project=project,
                        tags=tags,
                        description=description,
                        format=file_format,
                        source=source,
                        category=category,
                        spatial_coverage=spatial_coverage,
                        temporal_coverage=temporal_coverage,
                        access_method=access_method,
                        storage_location=storage_location,
                        reference=reference,
                        spatial_resolution=spatial_resolution,
                        temporal_resolution=temporal_resolution,
                        is_remote=True,
                        size=entry.size or 0,
                        mtime=int(entry.modified.timestamp()) if entry.modified else None,
                    )
                    count += 1
                    logger.info(f"Indexed dataset {count}/{len(datasets)}: {name}")

                except Exception as e:
                    logger.warning(f"Failed to index cloud dataset {entry.name}: {e}")
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
                    except Exception:
                        pass

            logger.info(f"Indexed {count} cloud datasets")

        except Exception as e:
            logger.error(f"Cloud indexing failed: {e}", exc_info=True)

    async def _fetch_metadata(self, storage, metadata_path: str) -> Optional[dict[str, Any]]:
        """Fetch and parse metadata.yaml from cloud storage."""
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                tmp_path = tmp.name

            try:
                await asyncio.to_thread(storage.download, metadata_path, tmp_path)

                with open(tmp_path, encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)

                return metadata
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"Could not fetch metadata from {metadata_path}: {e}")
            return None

    async def _incremental_cloud_sync(self) -> None:
        """Perform incremental sync of cloud datasets (fetches metadata for all)."""
        try:
            from hei_datahub.services.storage_manager import get_storage_backend

            logger.info("Performing incremental cloud sync (with metadata)")
            storage = get_storage_backend()

            # Get current cloud entries
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
                        # Support both 'tags' and 'keywords' for backwards compatibility
                        tags_list = metadata.get("tags") or metadata.get("keywords", [])
                        tags = " ".join(tags_list) if isinstance(tags_list, list) else str(tags_list)
                        project = metadata.get("project")
                        file_format = metadata.get("file_format")
                        source = metadata.get("source")
                        category = metadata.get("category")
                        spatial_coverage = metadata.get("spatial_coverage")
                        temporal_coverage = metadata.get("temporal_coverage")
                        size = metadata.get("size")
                    else:
                        name = entry.name
                        description = ""
                        tags = ""
                        project = None
                        file_format = None
                        source = None
                        category = None
                        spatial_coverage = None
                        temporal_coverage = None
                        size = None

                    # is_remote is always True in cloud-only mode
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
                        "category": category,
                        "spatial_coverage": spatial_coverage,
                        "temporal_coverage": temporal_coverage,
                    })

                except Exception as e:
                    logger.warning(f"Failed to sync cloud dataset {entry.name}: {e}")
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
                logger.info(f"Incrementally synced {count} cloud datasets")

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
                await self._incremental_cloud_sync()
                self.index_service.set_meta("last_sync", str(int(time.time())))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}", exc_info=True)

    def is_ready(self) -> bool:
        """Check if initial indexing is complete."""
        return self._indexed

    def get_status(self) -> dict[str, Any]:
        """Get indexer status."""
        total = self.index_service.get_item_count()
        return {
            "running": self._running,
            "indexed": self._indexed,
            "total_items": total,
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
