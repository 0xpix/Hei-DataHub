"""
Autocomplete system for form fields.
Extracts and suggests common values from existing datasets.
"""
from pathlib import Path
from typing import Optional

from hei_datahub.infra.index import list_all_datasets


class AutocompleteManager:
    """Manage autocomplete suggestions for form fields."""

    def __init__(self):
        """Initialize autocomplete manager."""
        self.projects: set[str] = set()
        self.data_types: set[str] = set()
        self.file_formats: set[str] = set()
        self.sources: set[str] = set()

        # Normalized canonical values (lowercase -> proper case)
        self.canonical_formats = {
            'csv': 'csv',
            'json': 'json',
            'parquet': 'parquet',
            'excel': 'excel',
            'xlsx': 'xlsx',
            'txt': 'txt',
            'sql': 'sql',
            'hdf5': 'hdf5',
            'netcdf': 'netcdf',
            'zarr': 'zarr',
        }

        self.canonical_types = {
            'tabular': 'tabular',
            'timeseries': 'time-series',
            'time-series': 'time-series',
            'geospatial': 'geospatial',
            'image': 'image',
            'text': 'text',
            'audio': 'audio',
            'video': 'video',
            'graph': 'graph',
            'network': 'network',
        }

    def normalize_format(self, format_str: str) -> str:
        """
        Normalize file format to canonical form.

        Args:
            format_str: Format string to normalize

        Returns:
            Canonical format string
        """
        lower = format_str.lower().strip()
        return self.canonical_formats.get(lower, format_str)

    def normalize_data_type(self, type_str: str) -> str:
        """
        Normalize data type to canonical form.

        Args:
            type_str: Data type string to normalize

        Returns:
            Canonical data type string
        """
        lower = type_str.lower().strip()
        return self.canonical_types.get(lower, type_str)

    def load_from_catalog(self, catalog_path: Optional[Path] = None) -> int:
        """
        Load suggestions from catalog YAML files or database.

        Args:
            catalog_path: Optional path to catalog repository

        Returns:
            Number of datasets processed
        """
        count = 0

        try:
            # Try loading from database first (faster)
            datasets = list_all_datasets()

            for dataset in datasets:
                count += 1

                # Extract projects
                if 'used_in_projects' in dataset:
                    projects = dataset['used_in_projects']
                    if isinstance(projects, list):
                        self.projects.update(p.strip() for p in projects if p)
                    elif isinstance(projects, str) and projects:
                        self.projects.update(p.strip() for p in projects.split(',') if p.strip())

                # Extract data types
                if 'data_types' in dataset:
                    types = dataset['data_types']
                    if isinstance(types, list):
                        self.data_types.update(self.normalize_data_type(t) for t in types if t)
                    elif isinstance(types, str) and types:
                        self.data_types.update(self.normalize_data_type(t.strip()) for t in types.split(',') if t.strip())

                # Extract file format
                if 'file_format' in dataset:
                    fmt = dataset['file_format']
                    if fmt:
                        self.file_formats.add(self.normalize_format(str(fmt)))

                # Extract source domains
                if 'source' in dataset:
                    source = str(dataset['source'])
                    if source.startswith('http://') or source.startswith('https://'):
                        # Extract domain
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(source).netloc
                            if domain:
                                self.sources.add(domain)
                        except Exception:
                            pass

        except Exception:
            # Database loading failed - autocomplete will be empty
            # Note: Removed local YAML fallback for cloud-only architecture
            pass

        return count

    def suggest_projects(self, query: str, limit: int = 10) -> list[str]:
        """
        Get project suggestions matching query.

        Args:
            query: Search query
            limit: Maximum number of suggestions

        Returns:
            List of matching project names
        """
        if not query:
            return sorted(self.projects)[:limit]

        query_lower = query.lower()

        # Prefix matches first, then contains matches
        prefix_matches = [p for p in self.projects if p.lower().startswith(query_lower)]
        contains_matches = [p for p in self.projects if query_lower in p.lower() and p not in prefix_matches]

        results = sorted(prefix_matches) + sorted(contains_matches)
        return results[:limit]

    def suggest_data_types(self, query: str, limit: int = 10) -> list[str]:
        """
        Get data type suggestions matching query.

        Args:
            query: Search query
            limit: Maximum number of suggestions

        Returns:
            List of matching data types
        """
        if not query:
            return sorted(self.data_types)[:limit]

        query_lower = query.lower()

        prefix_matches = [t for t in self.data_types if t.lower().startswith(query_lower)]
        contains_matches = [t for t in self.data_types if query_lower in t.lower() and t not in prefix_matches]

        results = sorted(prefix_matches) + sorted(contains_matches)
        return results[:limit]

    def suggest_file_formats(self, query: str, limit: int = 10) -> list[str]:
        """
        Get file format suggestions matching query.

        Args:
            query: Search query
            limit: Maximum number of suggestions

        Returns:
            List of matching file formats
        """
        if not query:
            return sorted(self.file_formats)[:limit]

        query_lower = query.lower()

        prefix_matches = [f for f in self.file_formats if f.lower().startswith(query_lower)]
        contains_matches = [f for f in self.file_formats if query_lower in f.lower() and f not in prefix_matches]

        results = sorted(prefix_matches) + sorted(contains_matches)
        return results[:limit]

    def refresh(self, catalog_path: Optional[Path] = None) -> int:
        """
        Refresh all suggestions from catalog.

        Args:
            catalog_path: Optional path to catalog repository

        Returns:
            Number of datasets processed
        """
        self.projects.clear()
        self.data_types.clear()
        self.file_formats.clear()
        self.sources.clear()

        return self.load_from_catalog(catalog_path)


# Global autocomplete manager instance
_autocomplete_manager: Optional[AutocompleteManager] = None


def get_autocomplete_manager() -> AutocompleteManager:
    """
    Get global autocomplete manager instance.

    Returns:
        AutocompleteManager instance
    """
    global _autocomplete_manager
    if _autocomplete_manager is None:
        _autocomplete_manager = AutocompleteManager()
    return _autocomplete_manager


def refresh_autocomplete(catalog_path: Optional[Path] = None) -> int:
    """
    Refresh global autocomplete suggestions.

    Args:
        catalog_path: Optional path to catalog repository

    Returns:
        Number of datasets processed
    """
    manager = get_autocomplete_manager()
    return manager.refresh(catalog_path)
