"""
Smart tag auto-generator for dataset metadata.

Extracts meaningful keywords from metadata fields, prioritizing:
  1. Name words (including hyphenated compound words like ERA5-Land)
  2. Category
  3. File format
  4. Source (short tokens)
  5. Access method type (GEE/PY/FILE/API)
  6. Spatial and temporal coverage
  7. Description (only a few high-signal words, broad stop-word list)

Returns at most 10 lowercase tags, sorted alphabetically.
"""

# Broad stop-word list — common English words that add no search value
_STOP_WORDS = frozenset({
    "a", "about", "above", "after", "all", "also", "an", "and", "any", "are",
    "as", "at", "be", "been", "before", "being", "between", "both", "but", "by",
    "can", "could", "data", "dataset", "datasets", "did", "do", "does", "done",
    "down", "each", "few", "for", "from", "further", "get", "got", "had", "has",
    "have", "having", "here", "high", "how", "however", "if", "in", "include",
    "including", "into", "is", "it", "its", "just", "like", "low", "made", "many",
    "may", "might", "more", "most", "much", "must", "near", "new", "no", "nor",
    "not", "now", "of", "off", "on", "once", "only", "or", "other", "our", "out",
    "over", "own", "per", "provides", "rather", "same", "set", "should", "since",
    "so", "some", "such", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until",
    "up", "upon", "use", "used", "using", "various", "very", "was", "we", "well",
    "were", "what", "when", "where", "which", "while", "who", "will", "with",
    "within", "would", "yet", "you", "your",
})

# Access method prefixes to extract as tags
_ACCESS_PREFIXES = {"GEE:", "PY:", "FILE:", "API:"}


def _clean_word(word: str) -> str:
    """Lowercase, strip non-alnum except hyphens/underscores."""
    return "".join(c for c in word.lower() if c.isalnum() or c in ("-", "_")).strip("-_")


def generate_tags(metadata: dict) -> list:
    """Auto-generate up to 10 tags from metadata fields.

    Smarter than naive description-splitting: prioritises structured fields
    and keeps hyphenated compound words (e.g. ERA5-Land → era5-land).
    """
    tags: set[str] = set()

    # ── 1. Name words (highest priority) ────────────────────────────────
    name = metadata.get("name", metadata.get("dataset_name", ""))
    if name:
        for word in name.split():
            cleaned = _clean_word(word)
            if len(cleaned) > 2:
                tags.add(cleaned)

    # ── 2. Category ─────────────────────────────────────────────────────
    category = metadata.get("category", "")
    if category:
        tag = category.lower().strip().replace(" ", "-")
        if tag:
            tags.add(tag)

    # ── 3. File format ──────────────────────────────────────────────────
    file_format = metadata.get("file_format", "")
    if file_format:
        tag = file_format.strip().lower()
        if tag:
            tags.add(tag)

    # ── 4. Source (short tokens only) ───────────────────────────────────
    source = metadata.get("source", "")
    if source:
        for word in source.split():
            cleaned = _clean_word(word)
            if 2 < len(cleaned) <= 25 and cleaned not in _STOP_WORDS:
                tags.add(cleaned)

    # ── 5. Access method type ───────────────────────────────────────────
    access_method = metadata.get("access_method", "")
    if access_method:
        for prefix in _ACCESS_PREFIXES:
            if access_method.upper().startswith(prefix):
                tags.add(prefix.rstrip(":").lower())  # gee / py / file / api
                break

    # ── 6. Spatial coverage ─────────────────────────────────────────────
    spatial = metadata.get("spatial_coverage", "")
    if spatial:
        tag = spatial.strip().lower().replace(" ", "-")
        if len(tag) > 2:
            tags.add(tag)

    # ── 7. Temporal coverage ────────────────────────────────────────────
    temporal = metadata.get("temporal_coverage", "")
    if temporal:
        tag = temporal.strip().lower().replace(" ", "-")
        if len(tag) > 2:
            tags.add(tag)

    # ── 8. Description (conservative — only first 15 words, skip stop words) ─
    description = metadata.get("description", "")
    if description:
        added_from_desc = 0
        for word in description.split()[:15]:
            cleaned = _clean_word(word)
            if len(cleaned) > 3 and cleaned not in _STOP_WORDS and cleaned not in tags:
                tags.add(cleaned)
                added_from_desc += 1
                if added_from_desc >= 3:  # cap description contribution
                    break

    return sorted(tags)[:10]  # Limit to 10 tags
