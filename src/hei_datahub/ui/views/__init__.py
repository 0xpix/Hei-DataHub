"""
TUI views for Hei-DataHub.

This package contains modular screen implementations split from the monolithic home.py.
"""

from .dataset_add import AddDataScreen
from .dataset_detail import CloudDatasetDetailsScreen
from .dataset_edit import CloudEditDetailsScreen
from .home import HomeScreen
from .settings import SettingsScreen

# Note: HelpScreen, SettingsWizard, and dialogs are in ui/widgets/
# Import them directly from there when needed to avoid circular imports

__all__ = [
    "HomeScreen",
    "CloudDatasetDetailsScreen",
    "CloudEditDetailsScreen",
    "AddDataScreen",
    "SettingsScreen",
]
