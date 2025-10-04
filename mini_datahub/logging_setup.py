"""
Logging configuration with rotating file handlers.
Respects privacy - no sensitive data logged.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    debug: bool = False,
    log_dir: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure application logging.

    Args:
        debug: Enable debug level logging
        log_dir: Log directory (defaults to ~/.mini-datahub/logs/)
        max_bytes: Max size per log file
        backup_count: Number of backup files to keep

    Returns:
        Configured logger
    """
    if log_dir is None:
        log_dir = Path.home() / ".mini-datahub" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger("mini_datahub")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler with rotation
    log_file = log_dir / "datahub.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )

    # Format with timestamp
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Console handler for errors only (don't spam terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized (debug={debug})")

    return logger


def get_logger(name: str = "mini_datahub") -> logging.Logger:
    """
    Get configured logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Log events without sensitive data
def log_pull_update(success: bool, files_changed: int = 0, error: Optional[str] = None):
    """Log pull update event."""
    logger = get_logger()
    if success:
        logger.info(f"Pull successful: {files_changed} files changed")
    else:
        logger.warning(f"Pull failed: {error}")


def log_reindex(success: bool, datasets_count: int = 0, error: Optional[str] = None):
    """Log reindex event."""
    logger = get_logger()
    if success:
        logger.info(f"Reindex complete: {datasets_count} datasets indexed")
    else:
        logger.warning(f"Reindex failed: {error}")


def log_pr_created(dataset_id: str, pr_number: Optional[int] = None):
    """Log PR creation event."""
    logger = get_logger()
    if pr_number:
        logger.info(f"PR created for dataset {dataset_id}: #{pr_number}")
    else:
        logger.warning(f"PR creation failed for dataset {dataset_id}")


def log_startup(version: str):
    """Log application startup."""
    logger = get_logger()
    logger.info(f"Application started - version {version}")


def log_shutdown():
    """Log application shutdown."""
    logger = get_logger()
    logger.info("Application shutdown")


def log_error(context: str, error: Exception):
    """Log error with context."""
    logger = get_logger()
    logger.error(f"{context}: {type(error).__name__}: {str(error)}")
