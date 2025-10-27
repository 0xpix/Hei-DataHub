"""Desktop integration uninstall command.

Handlers return integer exit codes and avoid terminating the process.
"""


def handle_uninstall(args) -> int:
    """Handle uninstall command.

    Returns:
        int: 0 on success, 1 on error
    """
    import sys

    try:
        from hei_datahub.desktop_install import uninstall_desktop_assets
    except ImportError:
        print("❌ Desktop integration module not available", file=sys.stderr)
        return 1

    # Check platform
    if sys.platform != "linux" and not sys.platform.startswith("linux"):
        print("Desktop integration is only available on Linux (nothing to uninstall)")
        return 0

    print("Uninstalling Desktop Integration")
    print("=" * 60)
    print()

    result = uninstall_desktop_assets(verbose=True)

    print()
    if result['success']:
        if result['removed_files']:
            print(f"✓ Removed {len(result['removed_files'])} file(s)")
            print()
            print("Desktop launcher and icons have been removed.")
        else:
            print("✓ No desktop assets found (already uninstalled)")
    else:
        print(f"⚠ Uninstall completed with warnings: {result['message']}")

    print()
    print("=" * 60)
    return 0
