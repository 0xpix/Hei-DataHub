"""
TUI views for Hei-DataHub.

This package contains modular screen implementations split from the monolithic home.py.
"""

from .home import HomeScreen
from .help import HelpScreen
from .dataset_detail import CloudDatasetDetailsScreen
from .dataset_edit import CloudEditDetailsScreen
from .dataset_add import AddDataScreen
from .settings import SettingsScreen
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
