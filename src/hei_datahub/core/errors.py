"""
Core domain errors.
"""


class DataHubError(Exception):
    """Base exception for DataHub errors."""
    pass


class ValidationError(DataHubError):
    """Raised when data validation fails."""
    pass


class StorageError(DataHubError):
    """Raised when file I/O operations fail."""
    pass


class IndexError(DataHubError):
    """Raised when database/index operations fail."""
    pass


class GitError(DataHubError):
    """Raised when Git operations fail."""
    pass


class GitHubError(DataHubError):
    """Raised when GitHub API operations fail."""
    pass


class ConfigError(DataHubError):
    """Raised when configuration is invalid."""
    pass
