"""Update command handler.

Handlers return integer exit codes and avoid terminating the process.
"""


def handle_update(args) -> int:
    """Handle the update subcommand with atomic update strategy.

    Dispatches to OS-specific update modules based on the platform.
    Each OS has its own dedicated update script:
    - windows_update.py: Windows-specific logic with batch script workaround
    - linux_update.py: Linux-specific logic with AtomicUpdateManager
    - macos_update.py: macOS-specific logic (currently uses Linux implementation)

    Returns:
        int: exit code from update operation
    """
    from rich.console import Console
    import sys

    console = Console()

    # Detect OS and dispatch to appropriate update module
    # Note: These update functions may still call sys.exit internally
    # The _call_handler wrapper in main.py will catch SystemExit
    if sys.platform == "win32":
        # Windows update - import and execute
        from hei_datahub.cli.update.windows_update import windows_update
        windows_update(args, console)
        return 0  # If we get here, update succeeded
    elif sys.platform == "darwin":
        # macOS update - import and execute
        from hei_datahub.cli.update.macos_update import macos_update
        macos_update(args, console)
        return 0  # If we get here, update succeeded
    else:
        # Linux and other Unix-like systems - import and execute
        from hei_datahub.cli.update.linux_update import linux_update
        linux_update(args, console)
        return 0  # If we get here, update succeeded
