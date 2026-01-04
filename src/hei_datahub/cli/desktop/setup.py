"""Desktop integration setup command.

Handlers return integer exit codes and avoid terminating the process.
"""


def handle_setup_desktop(args) -> int:
    """Handle setup desktop command.

    Returns:
        int: 0 on success, 1 on error
    """
    import sys

    try:
        from hei_datahub.desktop_install import (
            get_desktop_assets_status,
            get_install_paths_info,
            install_desktop_assets,
        )
    except ImportError:
        print("❌ Desktop integration module not available", file=sys.stderr)
        return 1

    # Check platform
    if sys.platform != "linux" and not sys.platform.startswith("linux"):
        print("❌ Desktop integration is only available on Linux")
        print(f"   Current platform: {sys.platform}")
        return 1

    # Show current status
    status = get_desktop_assets_status()
    print("Desktop Integration Setup")
    print("=" * 60)
    print()

    print("Current Status:")
    print(f"  Installed:       {'✓ Yes' if status['installed'] else '✗ No'}")
    if status['version']:
        print(f"  Version:         {status['version']}")
    print(f"  Current version: {status['current_version']}")
    print(f"  Needs update:    {'Yes' if status['needs_update'] else 'No'}")
    print()

    # Show paths
    print(get_install_paths_info())
    print()

    # Perform installation
    force = getattr(args, 'force', False)
    getattr(args, 'no_cache_refresh', False)

    print("Installing desktop assets...")
    print()

    result = install_desktop_assets(
        user_scope=True,
        force=force,
        verbose=True
    )

    print()
    if result['success']:
        if result.get('skipped', False):
            print("✓ Desktop assets are already up-to-date")
        else:
            print("✓ Desktop assets installed successfully")
            print()
            print("Installed files:")
            for filepath in result['installed_files']:
                print(f"  • {filepath}")
            print()
            if result['cache_refreshed']:
                print("✓ Icon caches refreshed")
            else:
                print("⚠ Icon cache refresh skipped (tools not available)")
            print()
            print("The application should now appear in your launcher/app grid.")
            print("If the icon doesn't appear immediately, try:")
            print("  • Logging out and back in")
            print("  • Restarting your desktop environment")
            print("  • Running: killall -HUP gnome-shell (GNOME)")
    else:
        print(f"❌ Installation failed: {result['message']}")
        return 1

    print()
    print("=" * 60)
    return 0
