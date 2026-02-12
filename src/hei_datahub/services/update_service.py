"""
Enhanced update service with silent update check on launch.

Features:
- Silent background update check on app launch (non-blocking)
- Version comparison supporting tags like "0.64.11b" (with optional suffix)
- Caching/throttling to avoid excessive API calls (6-12 hours)
- UI state management for showing update badge

Debug:
    Set HEI_DEBUG_UPDATER=1 to enable verbose update logging.
"""
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

import requests

from hei_datahub import GITHUB_REPO, __version__
from hei_datahub.services.state import get_state_manager

logger = logging.getLogger(__name__)

# Debug mode: set HEI_DEBUG_UPDATER=1 for verbose logging
_DEBUG = os.environ.get("HEI_DEBUG_UPDATER", "").strip() in ("1", "true", "yes")


def _debug(msg: str) -> None:
    """Log a debug message; use WARNING level if HEI_DEBUG_UPDATER is set."""
    if _DEBUG:
        logger.warning(f"[DEBUG-UPDATER] {msg}")
    else:
        logger.debug(msg)


# Cache settings
UPDATE_CHECK_INTERVAL_HOURS = 8  # Check every 8 hours (within 6-12 range)

# GitHub API endpoints
_RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
UPDATE_CHECK_URL = f"{_RELEASES_URL}/latest"
TAGS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/tags"

# Standard headers for GitHub API
_GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": f"Hei-DataHub/{__version__}",
}

# Pre-release suffix ordering (higher = newer)
# 'a' (alpha) < 'b' (beta) < 'rc' < stable (no suffix)
SUFFIX_ORDER = {
    'a': 1,      # alpha
    'alpha': 1,
    'b': 2,      # beta
    'beta': 2,
    'rc': 3,     # release candidate
    # No suffix (stable) = 100 (highest)
}


@dataclass
class ParsedVersion:
    """Parsed version with numeric segments and optional suffix."""

    # Numeric segments (e.g., [0, 64, 11] for "0.64.11")
    segments: Tuple[int, ...]

    # Suffix letter (e.g., 'b' for "0.64.11b", None for stable)
    suffix: Optional[str] = None

    # Suffix number (e.g., 2 for "rc2", None if just a letter)
    suffix_num: Optional[int] = None

    # Original string for display
    original: str = ""

    def is_stable(self) -> bool:
        """Check if this is a stable release (no prerelease suffix)."""
        return self.suffix is None

    def get_suffix_order(self) -> int:
        """
        Get the ordering value for the suffix.

        Returns:
            100 for stable (no suffix)
            1-3 for prereleases based on SUFFIX_ORDER
        """
        if self.suffix is None:
            return 100  # Stable is highest
        return SUFFIX_ORDER.get(self.suffix.lower(), 50)  # Unknown suffix = middle


def parse_tag_version(tag: str) -> ParsedVersion:
    """
    Parse a version tag string like "0.64.11b" into components.

    Handles:
    - Standard semver: "0.64.11"
    - With suffix letter: "0.64.11b", "0.64.11a"
    - With suffix and number: "0.64.11rc2"
    - Optional "v" prefix: "v0.64.11"
    - Beta suffix in semver style: "0.64.11-beta"

    Args:
        tag: Version tag string

    Returns:
        ParsedVersion with segments and optional suffix info
    """
    original = tag

    # Strip leading 'v' if present
    clean = tag.lstrip('v').strip()

    # Handle hyphenated prereleases like "0.64.11-beta"
    if '-' in clean:
        parts = clean.split('-', 1)
        version_part = parts[0]
        suffix_part = parts[1].lower()

        # Parse version segments
        segments = _parse_numeric_segments(version_part)

        # Parse suffix (e.g., "beta", "beta2", "rc1")
        suffix, suffix_num = _parse_suffix_part(suffix_part)

        return ParsedVersion(
            segments=segments,
            suffix=suffix,
            suffix_num=suffix_num,
            original=original
        )

    # Handle inline suffix like "0.64.11b" or "0.64.11rc2"
    # Pattern: digits.digits.digits[suffix][number]
    match = re.match(r'^([\d.]+)([a-zA-Z]+)?(\d+)?$', clean)

    if match:
        version_part = match.group(1)
        suffix = match.group(2).lower() if match.group(2) else None
        suffix_num_str = match.group(3)
        suffix_num = int(suffix_num_str) if suffix_num_str else None

        segments = _parse_numeric_segments(version_part)

        return ParsedVersion(
            segments=segments,
            suffix=suffix,
            suffix_num=suffix_num,
            original=original
        )

    # Fallback: try to extract just numeric segments
    segments = _parse_numeric_segments(clean)

    return ParsedVersion(
        segments=segments,
        suffix=None,
        suffix_num=None,
        original=original
    )


def _parse_numeric_segments(version_str: str) -> Tuple[int, ...]:
    """
    Parse numeric version segments from string like "0.64.11".

    Args:
        version_str: Version string with dot-separated numbers

    Returns:
        Tuple of integers
    """
    segments = []
    for part in version_str.rstrip('.').split('.'):
        # Extract leading digits from each part
        digits = re.match(r'^\d+', part)
        if digits:
            segments.append(int(digits.group()))

    # Ensure at least 3 segments for comparison
    while len(segments) < 3:
        segments.append(0)

    return tuple(segments)


def _parse_suffix_part(suffix_str: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Parse suffix string like "beta", "beta2", "rc1", "b".

    Args:
        suffix_str: Suffix portion of version

    Returns:
        Tuple of (suffix_name, suffix_number)
    """
    match = re.match(r'^([a-zA-Z]+)(\d+)?$', suffix_str)
    if match:
        suffix = match.group(1).lower()
        suffix_num = int(match.group(2)) if match.group(2) else None
        return suffix, suffix_num
    return None, None


def compare_versions(a: str, b: str) -> int:
    """
    Compare two version strings.

    Rules:
    1. Compare numeric segments first (major.minor.patch...)
    2. If numeric segments equal:
       - Stable (no suffix) > prerelease
       - Between prereleases: a < b < rc < stable
       - If same suffix type, compare suffix numbers

    Args:
        a: First version string
        b: Second version string

    Returns:
        -1 if a < b, 0 if a == b, 1 if a > b

    Examples:
        compare_versions("0.64.10", "0.64.11b") -> -1  (0.64.10 < 0.64.11b)
        compare_versions("0.64.11", "0.64.11b") -> 1   (stable > beta)
        compare_versions("0.64.11a", "0.64.11b") -> -1 (alpha < beta)
        compare_versions("0.64.11b", "0.64.12") -> -1  (0.64.11 < 0.64.12)
        compare_versions("0.64.11rc1", "0.64.11rc2") -> -1
    """
    va = parse_tag_version(a)
    vb = parse_tag_version(b)

    # 1. Compare numeric segments
    max_len = max(len(va.segments), len(vb.segments))

    seg_a = va.segments + (0,) * (max_len - len(va.segments))
    seg_b = vb.segments + (0,) * (max_len - len(vb.segments))

    for i in range(max_len):
        if seg_a[i] < seg_b[i]:
            return -1
        if seg_a[i] > seg_b[i]:
            return 1

    # 2. Numeric segments are equal - compare suffixes
    order_a = va.get_suffix_order()
    order_b = vb.get_suffix_order()

    if order_a < order_b:
        return -1
    if order_a > order_b:
        return 1

    # 3. Same suffix type - compare suffix numbers (rc1 < rc2)
    num_a = va.suffix_num or 0
    num_b = vb.suffix_num or 0

    if num_a < num_b:
        return -1
    if num_a > num_b:
        return 1

    return 0


def is_newer_version(latest: str, current: str) -> bool:
    """
    Check if latest version is newer than current.

    Args:
        latest: Latest version from GitHub
        current: Current installed version

    Returns:
        True if latest > current
    """
    return compare_versions(latest, current) > 0


@dataclass
class UpdateCheckResult:
    """Result of an update check."""
    has_update: bool
    current_version: str
    latest_version: str
    release_url: str = ""
    release_notes: str = ""
    error: Optional[str] = None
    from_cache: bool = False


def fetch_latest_tag(force: bool = False) -> Optional[str]:
    """
    Fetch the latest release tag from GitHub.

    Strategy:
    1. Try /releases (list) — pick highest version (handles pre-releases).
    2. Fall back to /releases/latest.
    3. Fall back to /tags.

    Args:
        force: Bypass cache and fetch fresh

    Returns:
        Latest tag string (without 'v' prefix), or None on error
    """
    state = get_state_manager()

    _debug(f"fetch_latest_tag called (force={force}), current __version__={__version__}")

    # Check cache first (unless forced)
    if not force:
        cached_tag = state.get_preference("last_known_latest_tag")
        last_check = state.get_last_update_check()

        if cached_tag and last_check:
            age = datetime.now() - last_check
            if age < timedelta(hours=UPDATE_CHECK_INTERVAL_HOURS):
                _debug(f"Using cached tag: {cached_tag} (age: {age})")
                return cached_tag

    # --- Strategy 1: /releases list (best — handles pre-releases) ---
    tag = _fetch_latest_from_releases_list(state)
    if tag:
        return tag

    # --- Strategy 2: /releases/latest (only returns non-prerelease) ---
    try:
        _debug(f"Trying /releases/latest: {UPDATE_CHECK_URL}")
        response = requests.get(
            UPDATE_CHECK_URL,
            timeout=10,
            headers=_GITHUB_HEADERS,
        )
        _debug(f"/releases/latest status={response.status_code}")

        if response.status_code == 200:
            data = response.json()
            tag = data.get("tag_name", "").lstrip('v')

            if tag:
                state.set_preference("last_known_latest_tag", tag)
                state.set_last_update_check()
                _debug(f"Got latest release tag: {tag}")
                return tag

        if response.status_code == 403:
            _handle_rate_limit(response)

    except requests.exceptions.Timeout:
        logger.warning("Timeout fetching /releases/latest")
    except requests.exceptions.ConnectionError:
        logger.warning("No internet connection for update check")
    except Exception as e:
        logger.error(f"Error fetching /releases/latest: {e}")

    # --- Strategy 3: /tags ---
    tag = _fetch_latest_from_tags(state)
    if tag:
        return tag

    # Return cached value on error (if available)
    cached = state.get_preference("last_known_latest_tag")
    if cached:
        _debug(f"Returning cached tag on error: {cached}")
    return cached


def _fetch_latest_from_releases_list(state) -> Optional[str]:
    """
    Fetch the highest version from the full releases list.

    This handles repos that only have pre-releases (no 'latest').
    Filters out drafts but includes pre-releases.
    """
    try:
        _debug(f"Trying /releases list: {_RELEASES_URL}")
        response = requests.get(
            _RELEASES_URL,
            timeout=10,
            headers=_GITHUB_HEADERS,
            params={"per_page": 30},
        )
        _debug(f"/releases list status={response.status_code}")

        if response.status_code == 403:
            _handle_rate_limit(response)
            return None

        if response.status_code != 200:
            return None

        releases = response.json()
        if not releases:
            _debug("No releases found in list")
            return None

        # Collect non-draft tags
        tag_names: list[str] = []
        for rel in releases:
            if rel.get("draft", False):
                continue
            tag = rel.get("tag_name", "").lstrip('v').strip()
            if tag:
                tag_names.append(tag)

        if not tag_names:
            _debug("All releases are drafts or have no tags")
            return None

        # Sort using our version comparison and pick the highest
        tag_names.sort(
            key=lambda t: (
                parse_tag_version(t).segments,
                parse_tag_version(t).get_suffix_order(),
                parse_tag_version(t).suffix_num or 0,
            )
        )
        latest = tag_names[-1]

        state.set_preference("last_known_latest_tag", latest)
        state.set_last_update_check()
        _debug(f"Highest version from releases list: {latest}")
        return latest

    except requests.exceptions.Timeout:
        logger.warning("Timeout fetching /releases list")
    except requests.exceptions.ConnectionError:
        logger.warning("No internet connection for /releases list")
    except Exception as e:
        logger.error(f"Error fetching /releases list: {e}")

    return None


def _handle_rate_limit(response) -> None:
    """Log a helpful message when GitHub API rate-limits us."""
    remaining = response.headers.get("X-RateLimit-Remaining", "?")
    reset_ts = response.headers.get("X-RateLimit-Reset", "")
    reset_str = ""
    if reset_ts:
        try:
            reset_dt = datetime.fromtimestamp(int(reset_ts))
            reset_str = f" (resets at {reset_dt:%H:%M:%S})"
        except Exception:
            pass
    logger.warning(
        f"GitHub API rate limited. Remaining: {remaining}{reset_str}. "
        f"Update check skipped."
    )
    _debug(f"Rate limit headers: {dict(response.headers)}")


def _fetch_latest_from_tags(state) -> Optional[str]:
    """
    Fetch the latest tag when no releases exist.

    Finds the highest version tag using our comparison logic.
    """
    try:
        _debug(f"Trying /tags: {TAGS_URL}")
        response = requests.get(
            TAGS_URL,
            timeout=10,
            headers=_GITHUB_HEADERS,
            params={"per_page": 50},
        )
        _debug(f"/tags status={response.status_code}")

        if response.status_code == 403:
            _handle_rate_limit(response)
            return None

        if response.status_code != 200:
            return None

        tags = response.json()
        if not tags:
            _debug("No tags found")
            return None

        # Find the highest version tag
        tag_names = [t.get("name", "").lstrip('v') for t in tags if t.get("name")]

        if not tag_names:
            return None

        # Sort using our version comparison
        tag_names.sort(
            key=lambda t: (
                parse_tag_version(t).segments,
                parse_tag_version(t).get_suffix_order(),
                parse_tag_version(t).suffix_num or 0,
            )
        )
        latest = tag_names[-1]

        # Cache result
        state.set_preference("last_known_latest_tag", latest)
        state.set_last_update_check()
        _debug(f"Highest version from tags: {latest}")
        return latest

    except requests.exceptions.Timeout:
        logger.warning("Timeout fetching /tags")
    except requests.exceptions.ConnectionError:
        logger.warning("No internet for /tags")
    except Exception as e:
        logger.error(f"Error fetching tags: {e}")
    return None


def check_for_updates_silent(force: bool = False) -> Optional[UpdateCheckResult]:
    """
    Perform a silent (non-blocking) update check.

    Uses caching to avoid excessive API calls.
    Does not show any UI - just returns the result.

    Args:
        force: Bypass the throttle cache and always fetch from network.
               Use on app startup so a freshly-published release is
               detected immediately.

    Returns:
        UpdateCheckResult or None if check was skipped/failed
    """
    state = get_state_manager()

    # Check if we should skip (throttling) — skipped when force=True
    if not force:
        last_check = state.get_last_update_check()
        if last_check:
            age = datetime.now() - last_check
            if age < timedelta(hours=UPDATE_CHECK_INTERVAL_HOURS):
                # Use cached result
                cached_available = state.get_preference("last_known_update_available")
                cached_tag = state.get_preference("last_known_latest_tag")

                if cached_tag:
                    logger.debug(f"Using cached update check (age: {age})")
                    return UpdateCheckResult(
                        has_update=bool(cached_available),
                        current_version=__version__,
                        latest_version=cached_tag,
                        from_cache=True
                    )
                # No cache, but within throttle window - skip
                return None

    # Perform fresh check
    _debug("Performing silent update check…")

    latest_tag = fetch_latest_tag(force=True)

    if not latest_tag:
        _debug("Could not fetch latest version from any source")
        return UpdateCheckResult(
            has_update=False,
            current_version=__version__,
            latest_version=__version__,
            error="Could not fetch latest version"
        )

    # Compare versions
    has_update = is_newer_version(latest_tag, __version__)

    _debug(
        f"Version comparison: current={__version__} "
        f"(parsed={parse_tag_version(__version__)}), "
        f"latest={latest_tag} "
        f"(parsed={parse_tag_version(latest_tag)}), "
        f"has_update={has_update}"
    )

    # Cache the result
    state.set_preference("last_known_update_available", has_update)
    state.set_preference("last_known_latest_tag", latest_tag)

    logger.info(f"Update check: current={__version__}, latest={latest_tag}, has_update={has_update}")

    return UpdateCheckResult(
        has_update=has_update,
        current_version=__version__,
        latest_version=latest_tag
    )


def get_cached_update_state() -> Optional[UpdateCheckResult]:
    """
    Get the cached update state without making a network request.

    Useful for UI components that need to show update badge immediately.

    Returns:
        UpdateCheckResult from cache, or None if no cache
    """
    state = get_state_manager()

    cached_tag = state.get_preference("last_known_latest_tag")
    cached_available = state.get_preference("last_known_update_available")

    if cached_tag is None:
        return None

    return UpdateCheckResult(
        has_update=bool(cached_available),
        current_version=__version__,
        latest_version=cached_tag,
        from_cache=True
    )


def clear_update_cache() -> None:
    """Clear the update check cache to force a fresh check."""
    state = get_state_manager()
    state.set_preference("last_known_latest_tag", None)
    state.set_preference("last_known_update_available", None)
    # Reset last check time by setting it far in the past
    state.set_last_update_check(datetime.min)
    logger.info("Update cache cleared")


def trigger_update() -> UpdateCheckResult:
    """
    Trigger the update workflow (called by Ctrl+U).

    This forces a fresh check and returns the result.
    The caller should then decide whether to show the update screen.

    Returns:
        UpdateCheckResult with fresh data
    """
    _debug("Triggering update check (user-initiated)…")
    _debug(f"Current __version__ = {__version__}")

    # Import and log install method for debugging
    try:
        from hei_datahub.infra.install_method import get_install_info
        info = get_install_info()
        _debug(f"Install method: {info.method.value}, command: {info.update_command}")
    except Exception as e:
        _debug(f"Could not detect install method: {e}")

    # Force fresh check
    clear_update_cache()
    result = check_for_updates_silent()

    if result is None:
        # Should not happen after cache clear, but handle it
        return UpdateCheckResult(
            has_update=False,
            current_version=__version__,
            latest_version=__version__,
            error="Update check failed"
        )

    return result
