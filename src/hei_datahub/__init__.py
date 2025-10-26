"""
Hei-DataHub - A local-first TUI for managing datasets with consistent metadata.

This is an alias package that imports from mini_datahub for backwards compatibility
and to support the hei-datahub name in UV installations.
"""
# from mini_datahub import *  # noqa: F401, F403
# from mini_datahub.version import __version__, __app_name__  # noqa: F401

__all__ = ["__version__", "__app_name__"]
