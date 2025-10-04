"""
Text utilities: slugify, humanize, formatting.
"""
import re
from typing import Optional


def slugify(text: str) -> str:
    """
    Convert text to a valid slug for use as dataset ID.

    Args:
        text: Input text (e.g., dataset name)

    Returns:
        A lowercase slug with hyphens
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove any character that isn't alphanumeric, hyphen, or underscore
    text = re.sub(r"[^a-z0-9-_]", "", text)
    # Remove leading/trailing hyphens
    text = text.strip("-_")
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    return text


def humanize_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable string (e.g., "1.2 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Input text
        length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def highlight(text: str, query: str) -> str:
    """
    Highlight search query in text (case-insensitive).

    Args:
        text: Text to search in
        query: Query to highlight

    Returns:
        Text with <mark> tags around matches
    """
    if not query:
        return text

    # Simple case-insensitive replacement
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", text)
