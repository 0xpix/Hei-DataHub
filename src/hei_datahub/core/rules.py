"""
Business rules: ID normalization, validation rules, slug generation.
"""
import re
from typing import Callable


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


def generate_unique_id(base_name: str, exists_check: Callable[[str], bool]) -> str:
    """
    Generate a unique dataset ID from a base name, handling collisions.

    Args:
        base_name: Base name to convert to ID (usually dataset name)
        exists_check: Function that returns True if ID already exists

    Returns:
        A unique ID (slug)
    """
    slug = slugify(base_name)
    if not slug:
        slug = "dataset"

    # Check if this ID already exists
    original_slug = slug
    counter = 1
    while exists_check(slug):
        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug


def validate_dataset_id(dataset_id: str) -> tuple[bool, str]:
    """
    Validate a dataset ID against rules.

    Args:
        dataset_id: The ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dataset_id:
        return False, "ID cannot be empty"

    if len(dataset_id) > 100:
        return False, "ID must be 100 characters or less"

    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", dataset_id):
        return False, "ID must start with alphanumeric and contain only lowercase letters, numbers, hyphens, and underscores"

    return True, ""
