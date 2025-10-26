"""
TUI views for Hei-DataHub.

This package contains modular screen implementations split from the monolithic home.py.
"""

from .home import HomeScreen
from .help import HelpScreen
from .dataset_detail import CloudDatasetDetailsScreen  # DetailsScreen removed - cloud-only workflow
from .dataset_edit import CloudEditDetailsScreen  # EditDetailsScreen removed - cloud-only workflow
from .dataset_add import AddDataScreen
from .dialogs import ConfirmCancelDialog, ConfirmDeleteDialog

__all__ = [
    "HomeScreen",
    "HelpScreen",
    "CloudDatasetDetailsScreen",
    "CloudEditDetailsScreen",
    "AddDataScreen",
    "ConfirmCancelDialog",
    "ConfirmDeleteDialog",
]
