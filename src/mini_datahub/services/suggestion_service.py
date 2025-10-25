"""
Smart autocomplete suggestion service for Hei-DataHub.

Provides context-aware search suggestions from indexed metadata:
- Field-specific suggestions (source:, project:, tag:, owner:, size:)
- Ranked by frequency, recency, and prefix match
- Cached with TTL for performance
"""

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from mini_datahub.services.index_service import INDEX_DB_PATH

logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    """A single autocomplete suggestion."""
    key: Optional[str]  # "project", "source", "tag", "owner", "size", None for free text
    value: str
    display: str  # Shown in popup
    insert_text: str  # What to insert into input
    meta: Optional[str] = None  # e.g., "23 datasets"
    score: float = 0.0


class SuggestionService:
    """
    Provides smart autocomplete suggestions from metadata.

    Features:
    - Context-aware suggestions based on key prefix
    - Ranking by frequency, recency, and prefix match
    - Size bucket suggestions (tiny, small, medium, large, xl)
    - Caching with TTL for performance
    """

    # Size buckets in bytes
    SIZE_BUCKETS = {
        "tiny": (0, 10 * 1024 * 1024),  # <10MB
        "small": (10 * 1024 * 1024, 100 * 1024 * 1024),  # 10-100MB
        "medium": (100 * 1024 * 1024, 1024 * 1024 * 1024),  # 100MB-1GB
        "large": (1024 * 1024 * 1024, 10 * 1024 * 1024 * 1024),  # 1-10GB
        "xl": (10 * 1024 * 1024 * 1024, float('inf')),  # >10GB
    }

    def __init__(self, db_path: Optional[Path] = None, cache_ttl: int = 300):
        """
        Initialize suggestion service.

        Args:
            db_path: Path to index database
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.db_path = db_path or INDEX_DB_PATH
        self.cache_ttl = cache_ttl

        # Caches with timestamps
        self._cache: Dict[str, List[str]] = {}
        self._cache_time: Dict[str, float] = {}

        # Usage tracking
        self._init_usage_table()

    def _init_usage_table(self) -> None:
        """Initialize the suggestion_usage table."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS suggestion_usage (
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    last_used_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                    PRIMARY KEY (key, value)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_key ON suggestion_usage(key)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_last_used ON suggestion_usage(last_used_at DESC)
            """)
            conn.commit()
            logger.debug("suggestion_usage table initialized")
        finally:
            conn.close()

    def _get_cached_or_fetch(self, cache_key: str, fetch_fn) -> List[str]:
        """Get from cache or fetch fresh data."""
        now = time.time()

        # Check cache
        if cache_key in self._cache:
            cache_time = self._cache_time.get(cache_key, 0)
            if now - cache_time < self.cache_ttl:
                return self._cache[cache_key]

        # Fetch fresh data
        data = fetch_fn()
        self._cache[cache_key] = data
        self._cache_time[cache_key] = now
        return data

    def invalidate_cache(self) -> None:
        """Invalidate all caches (call after reindex)."""
        self._cache.clear()
        self._cache_time.clear()
        logger.debug("Suggestion cache invalidated")

    def _get_distinct_values(self, field: str) -> List[str]:
        """Get distinct non-null values for a field."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                f"SELECT DISTINCT {field} FROM items WHERE {field} IS NOT NULL AND {field} != '' ORDER BY {field}"
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def _get_distinct_tags(self) -> List[str]:
        """Get distinct tags (tags are stored as comma-separated)."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT DISTINCT tags FROM items WHERE tags IS NOT NULL AND tags != ''")
            tags_set: Set[str] = set()
            for row in cursor.fetchall():
                tags_str = row[0]
                if tags_str:
                    # Split by comma and clean up
                    for tag in tags_str.split(','):
                        tag = tag.strip()
                        if tag:
                            tags_set.add(tag)
            return sorted(tags_set)
        finally:
            conn.close()

    def _get_size_bucket(self, size_bytes: int) -> Optional[str]:
        """Get size bucket name for given size in bytes."""
        for bucket_name, (min_size, max_size) in self.SIZE_BUCKETS.items():
            if min_size <= size_bytes < max_size:
                return bucket_name
        return None

    def _get_size_distribution(self) -> Dict[str, int]:
        """Get count of datasets in each size bucket."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("SELECT size FROM items WHERE size IS NOT NULL")
            distribution = {bucket: 0 for bucket in self.SIZE_BUCKETS.keys()}

            for row in cursor.fetchall():
                size_bytes = row[0]
                bucket = self._get_size_bucket(size_bytes)
                if bucket:
                    distribution[bucket] += 1

            return distribution
        finally:
            conn.close()

    def _get_usage_stats(self, key: str, value: str) -> Tuple[int, int]:
        """
        Get usage statistics for a key:value pair.

        Returns:
            (count, last_used_at) tuple
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT count, last_used_at FROM suggestion_usage WHERE key = ? AND value = ?",
                (key, value)
            )
            row = cursor.fetchone()
            if row:
                return (row[0], row[1])
            return (0, 0)
        finally:
            conn.close()

    def track_usage(self, key: str, value: str) -> None:
        """
        Track usage of a suggestion (increment count, update timestamp).

        Args:
            key: Filter key (e.g., "project", "source")
            value: Filter value (e.g., "ML-Research")
        """
        conn = sqlite3.connect(self.db_path)
        try:
            now = int(time.time())
            conn.execute("""
                INSERT INTO suggestion_usage (key, value, count, last_used_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(key, value) DO UPDATE SET
                    count = count + 1,
                    last_used_at = ?
            """, (key, value, now, now))
            conn.commit()
            logger.debug(f"Tracked usage: {key}:{value}")
        finally:
            conn.close()

    def _calculate_score(
        self,
        value: str,
        typed: str,
        count: int,
        last_used_at: int,
        max_count: int,
        max_last_used: int
    ) -> float:
        """
        Calculate suggestion score.

        Score = 2.0 * prefix_match + 1.5 * freq_norm + 1.2 * recency_norm + 0.5 * alphabetical_boost
        """
        # Prefix match (exact case-insensitive)
        prefix_match = 1.0 if value.lower().startswith(typed.lower()) else 0.0

        # Frequency normalization
        freq_norm = count / max_count if max_count > 0 else 0.0

        # Recency normalization
        now = int(time.time())
        recency_norm = 0.0
        if max_last_used > 0:
            # Normalize to [0, 1], with recent items scoring higher
            age = now - last_used_at
            max_age = now - max_last_used if max_last_used > 0 else 1
            recency_norm = 1.0 - (age / max(max_age, 1))

        # Alphabetical boost (earlier in alphabet gets slight boost)
        alphabetical_boost = 1.0 - (ord(value[0].lower()) - ord('a')) / 26.0 if value else 0.0

        score = (
            2.0 * prefix_match +
            1.5 * freq_norm +
            1.2 * recency_norm +
            0.5 * alphabetical_boost
        )

        return score

    def get_suggestions(
        self,
        key: Optional[str],
        typed: str,
        max_suggestions: int = 10
    ) -> List[Suggestion]:
        """
        Get ranked suggestions for a key prefix.

        Args:
            key: Filter key ("project", "source", "tag", "owner", "size", or None for free text)
            typed: Partial value typed by user
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of ranked suggestions
        """
        if key == "size":
            return self._get_size_suggestions(typed, max_suggestions)
        elif key == "project":
            return self._get_field_suggestions("project", typed, max_suggestions)
        elif key == "source":
            return self._get_field_suggestions("source", typed, max_suggestions)
        elif key == "tag":
            return self._get_tag_suggestions(typed, max_suggestions)
        elif key == "owner":
            return self._get_field_suggestions("project", typed, max_suggestions)  # Using project as owner for now
        else:
            return self._get_free_text_suggestions(typed, max_suggestions)

    def _get_size_suggestions(self, typed: str, max_suggestions: int) -> List[Suggestion]:
        """Get size bucket suggestions."""
        distribution = self._get_cached_or_fetch("size_distribution", self._get_size_distribution)

        suggestions = []
        for bucket_name in self.SIZE_BUCKETS.keys():
            if not typed or bucket_name.lower().startswith(typed.lower()):
                count = distribution.get(bucket_name, 0)
                meta = f"{count} datasets" if count > 0 else None

                suggestions.append(Suggestion(
                    key="size",
                    value=bucket_name,
                    display=f"size:{bucket_name}",
                    insert_text=f"size:{bucket_name} ",
                    meta=meta,
                    score=2.0 if bucket_name.lower().startswith(typed.lower()) else 1.0
                ))

        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:max_suggestions]

    def _get_tag_suggestions(self, typed: str, max_suggestions: int) -> List[Suggestion]:
        """Get tag suggestions."""
        all_tags = self._get_cached_or_fetch("tags", self._get_distinct_tags)

        # Filter by typed prefix
        matching_tags = [tag for tag in all_tags if not typed or typed.lower() in tag.lower()]

        # Get usage stats and calculate scores
        suggestions = []
        max_count = 1
        max_last_used = 1

        # Get max values for normalization
        for tag in matching_tags:
            count, last_used = self._get_usage_stats("tag", tag)
            max_count = max(max_count, count)
            max_last_used = max(max_last_used, last_used)

        # Create suggestions with scores
        for tag in matching_tags:
            count, last_used = self._get_usage_stats("tag", tag)
            score = self._calculate_score(tag, typed, count, last_used, max_count, max_last_used)

            suggestions.append(Suggestion(
                key="tag",
                value=tag,
                display=f"tag:{tag}",
                insert_text=f"tag:{tag} ",
                meta=f"used {count}x" if count > 0 else None,
                score=score
            ))

        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:max_suggestions]

    def _get_field_suggestions(self, field: str, typed: str, max_suggestions: int) -> List[Suggestion]:
        """Get suggestions for a specific field (project, source, owner)."""
        all_values = self._get_cached_or_fetch(field, lambda: self._get_distinct_values(field))

        # Filter by typed prefix
        matching_values = [v for v in all_values if not typed or typed.lower() in v.lower()]

        # Get usage stats and calculate scores
        suggestions = []
        max_count = 1
        max_last_used = 1

        # Get max values for normalization
        for value in matching_values:
            count, last_used = self._get_usage_stats(field, value)
            max_count = max(max_count, count)
            max_last_used = max(max_last_used, last_used)

        # Create suggestions with scores
        for value in matching_values:
            count, last_used = self._get_usage_stats(field, value)
            score = self._calculate_score(value, typed, count, last_used, max_count, max_last_used)

            suggestions.append(Suggestion(
                key=field,
                value=value,
                display=f"{field}:{value}",
                insert_text=f"{field}:{value} ",
                meta=f"used {count}x" if count > 0 else None,
                score=score
            ))

        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:max_suggestions]

    def _get_free_text_suggestions(self, typed: str, max_suggestions: int) -> List[Suggestion]:
        """Get free text suggestions (recent queries, frequent terms)."""
        # For now, return empty - can be enhanced with recent query history
        return []


# Singleton instance
_suggestion_service: Optional[SuggestionService] = None


def get_suggestion_service() -> SuggestionService:
    """Get the global suggestion service instance."""
    global _suggestion_service
    if _suggestion_service is None:
        _suggestion_service = SuggestionService()
    return _suggestion_service
