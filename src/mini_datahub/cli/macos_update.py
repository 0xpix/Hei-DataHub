"""macOS-specific update logic."""

from mini_datahub.cli.linux_update import linux_update


def macos_update(args, console):
    """macOS-specific update using AtomicUpdateManager (same as Linux for now).

    This is a separate file so macOS-specific customizations can be added in the future
    without affecting Linux behavior.
    """
    # macOS can use the same logic as Linux for now
    linux_update(args, console)
