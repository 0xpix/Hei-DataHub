"""
CLI entrypoint for Hei-DataHub.
"""
import argparse
import sys

from mini_datahub.version import __version__, __app_name__, print_version_info


def handle_reindex(args):
    """Handle the reindex subcommand."""
    from mini_datahub.infra.db import ensure_database
    from mini_datahub.infra.store import list_datasets, read_dataset
    from mini_datahub.infra.index import upsert_dataset

    print(f"Reindexing datasets from data directory...")

    # Ensure database exists
    ensure_database()

    # Get all datasets
    dataset_ids = list_datasets()

    if not dataset_ids:
        print("No datasets found in data directory.")
        sys.exit(0)

    count = 0
    errors = []

    for dataset_id in dataset_ids:
        try:
            metadata = read_dataset(dataset_id)
            if metadata:
                upsert_dataset(dataset_id, metadata)
                count += 1
                print(f"  ✓ Indexed: {dataset_id}")
            else:
                errors.append(f"{dataset_id}: Could not read metadata")
        except Exception as e:
            errors.append(f"{dataset_id}: {str(e)}")

    print(f"\n✓ Successfully indexed {count} dataset(s)")

    if errors:
        print(f"\n⚠ Encountered {len(errors)} error(s):")
        for error in errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("All datasets indexed successfully!")
        sys.exit(0)


def handle_tui(args):
    """Handle the default TUI launch."""
    # Import here to avoid loading heavy UI dependencies for CLI commands
    try:
        # Import the TUI runner from new location
        from mini_datahub.ui.views.home import run_tui
        from mini_datahub.infra.db import ensure_database

        # Ensure database exists (workspace already initialized in main())
        ensure_database()

        # Launch TUI
        run_tui()

    except ImportError as e:
        print("❌ TUI module import error:", str(e), file=sys.stderr)
        print("See MIGRATION_v0.40.md for details.", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching TUI: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def handle_keymap_export(args):
    """Handle keymap export command."""
    import yaml
    from mini_datahub.services.config import get_config
    from mini_datahub.infra.config_paths import get_keybindings_export_path

    config = get_config()
    keybindings = config.get_keybindings()

    output_path = get_keybindings_export_path(args.output)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump({"keybindings": keybindings}, f, default_flow_style=False)
        print(f"✓ Exported keybindings to: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to export keybindings: {e}", file=sys.stderr)
        sys.exit(1)


def handle_keymap_import(args):
    """Handle keymap import command."""
    import yaml
    from mini_datahub.services.config import get_config
    from mini_datahub.infra.config_paths import get_keybindings_export_path

    config = get_config()
    input_path = args.input

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        keybindings = data.get('keybindings', {})
        if not keybindings:
            print(f"⚠ No keybindings found in {input_path}")
            sys.exit(1)

        # Validate and import
        config.update_keybindings(keybindings)
        print(f"✓ Imported keybindings from: {input_path}")
        print(f"✓ Applied {len(keybindings)} keybinding sets")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Failed to import keybindings: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_auth_setup(args):
    """Handle auth setup command."""
    from mini_datahub.auth.setup import run_setup_wizard

    exit_code = run_setup_wizard(
        url=args.url,
        username=args.username,
        token=args.token,
        password=args.password,
        library=getattr(args, 'library', None),
        store=args.store,
        no_validate=args.no_validate,
        overwrite=args.overwrite,
        timeout=args.timeout,
        non_interactive=args.non_interactive,
    )
    sys.exit(exit_code)


def handle_auth_status(args):
    """Handle auth status command."""
    from mini_datahub.infra.config_paths import get_config_path
    from pathlib import Path

    config_path = get_config_path()

    if not config_path.exists():
        print("❌ No authentication configured.")
        print(f"   Config file not found: {config_path}")
        print("\nRun: hei-datahub auth setup")
        sys.exit(1)

    try:
        # Python 3.11+ has tomllib built-in
        try:
            import tomllib as tomli
        except ImportError:
            import tomli

        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_config = config.get("auth", {})

        if not auth_config:
            print("❌ No [auth] section in config")
            sys.exit(1)

        print("🔐 WebDAV Authentication Status\n")
        print(f"Method:     {auth_config.get('method', 'unknown')}")
        print(f"URL:        {auth_config.get('url', 'unknown')}")
        print(f"Username:   {auth_config.get('username', '-')}")
        print(f"Storage:    {auth_config.get('stored_in', 'unknown')}")
        print(f"Key ID:     {auth_config.get('key_id', 'unknown')}")
        print(f"\nConfig:     {config_path}")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error reading config: {e}", file=sys.stderr)
        sys.exit(1)


def handle_auth_doctor(args):
    """Handle auth doctor command."""
    from mini_datahub.auth.doctor import run_doctor

    exit_code = run_doctor(
        output_json=args.json,
        skip_write=args.no_write,
        timeout=getattr(args, 'timeout', 8),
    )
    sys.exit(exit_code)


def handle_auth_clear(args):
    """Handle auth clear command."""
    from mini_datahub.auth.clear import run_clear

    exit_code = run_clear(
        force=args.force,
        clear_all=args.all,
    )
    sys.exit(exit_code)


def handle_keymap_import(args):
    """Handle keymap import command."""
    import yaml
    from mini_datahub.services.config import get_config
    from pathlib import Path

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if "keybindings" not in data:
            print("❌ Invalid keymap file: missing 'keybindings' key", file=sys.stderr)
            sys.exit(1)

        config = get_config()
        config.update_user_config({"keybindings": data["keybindings"]})

        print(f"✓ Imported keybindings from: {input_path}")
        print("ℹ️  Changes will take effect immediately in running app or on next start")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to import keybindings: {e}", file=sys.stderr)
        sys.exit(1)


def handle_update(args):
    """Handle the update subcommand with atomic update strategy.

    Dispatches to OS-specific update modules based on the platform.
    Each OS has its own dedicated update script:
    - windows_update.py: Windows-specific logic with batch script workaround
    - linux_update.py: Linux-specific logic with AtomicUpdateManager
    - macos_update.py: macOS-specific logic (currently uses Linux implementation)
    """
    from rich.console import Console
    import sys

    console = Console()

    # Detect OS and dispatch to appropriate update module
    if sys.platform == "win32":
        # Windows update - import and execute
        from mini_datahub.cli.windows_update import windows_update
        windows_update(args, console)
    elif sys.platform == "darwin":
        # macOS update - import and execute
        from mini_datahub.cli.macos_update import macos_update
        macos_update(args, console)
    else:
        # Linux and other Unix-like systems - import and execute
        from mini_datahub.cli.linux_update import linux_update
        linux_update(args, console)


def handle_doctor(args):
    """Handle doctor diagnostic command."""
    from mini_datahub.cli.doctor import run_doctor

    # Pass data-dir override if provided
    data_dir_override = getattr(args, 'data_dir', None)
    exit_code = run_doctor(data_dir_override)
    sys.exit(exit_code)


def handle_setup_desktop(args):
    """Handle setup desktop command."""
    try:
        from hei_datahub.desktop_install import (
            install_desktop_assets,
            get_install_paths_info,
            get_desktop_assets_status,
        )
    except ImportError:
        print("❌ Desktop integration module not available", file=sys.stderr)
        sys.exit(1)

    import sys

    # Check platform
    if sys.platform != "linux" and not sys.platform.startswith("linux"):
        print("❌ Desktop integration is only available on Linux")
        print(f"   Current platform: {sys.platform}")
        sys.exit(1)

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
    no_cache_refresh = getattr(args, 'no_cache_refresh', False)

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
        sys.exit(1)

    print()
    print("=" * 60)
    sys.exit(0)


def handle_uninstall(args):
    """Handle uninstall command."""
    try:
        from hei_datahub.desktop_install import uninstall_desktop_assets
    except ImportError:
        print("❌ Desktop integration module not available", file=sys.stderr)
        sys.exit(1)

    import sys

    # Check platform
    if sys.platform != "linux" and not sys.platform.startswith("linux"):
        print("Desktop integration is only available on Linux (nothing to uninstall)")
        sys.exit(0)

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
    sys.exit(0)


def handle_paths(args):
    """Handle paths diagnostic command."""
    from mini_datahub.infra import paths
    import os

    print("Hei-DataHub Paths Diagnostic")
    print("=" * 60)
    print()

    # Installation mode
    is_installed = paths._is_installed_package()
    is_dev = paths._is_dev_mode()

    print(f"Installation Mode:")
    if is_installed:
        print("  ✓ Installed package (standalone)")
    elif is_dev:
        print("  ✓ Development mode (repository)")
    else:
        print("  ⚠ Fallback mode")
    print()

    # XDG directories
    print(f"XDG Base Directories:")
    print(f"  XDG_CONFIG_HOME: {paths.XDG_CONFIG_HOME}")
    print(f"  XDG_DATA_HOME:   {paths.XDG_DATA_HOME}")
    print(f"  XDG_CACHE_HOME:  {paths.XDG_CACHE_HOME}")
    print(f"  XDG_STATE_HOME:  {paths.XDG_STATE_HOME}")
    print()

    # Application paths
    print(f"Application Paths:")
    print(f"  Config:    {paths.CONFIG_DIR}")
    print(f"    Exists:  {'✓' if paths.CONFIG_DIR.exists() else '✗'}")
    print(f"  Data:      {paths.DATA_DIR}")
    print(f"    Exists:  {'✓' if paths.DATA_DIR.exists() else '✗'}")
    if paths.DATA_DIR.exists():
        dataset_count = len(list(paths.DATA_DIR.iterdir()))
        print(f"    Datasets: {dataset_count}")
    print(f"  Cache:     {paths.CACHE_DIR}")
    print(f"    Exists:  {'✓' if paths.CACHE_DIR.exists() else '✗'}")
    print(f"  State:     {paths.STATE_DIR}")
    print(f"    Exists:  {'✓' if paths.STATE_DIR.exists() else '✗'}")
    print(f"  Logs:      {paths.LOG_DIR}")
    print(f"    Exists:  {'✓' if paths.LOG_DIR.exists() else '✗'}")
    print()

    # Important files
    print(f"Important Files:")
    print(f"  Database:  {paths.DB_PATH}")
    print(f"    Exists:  {'✓' if paths.DB_PATH.exists() else '✗'}")
    if paths.DB_PATH.exists():
        size_bytes = paths.DB_PATH.stat().st_size
        size_kb = size_bytes / 1024
        print(f"    Size:    {size_kb:.1f} KB")
    print(f"  Schema:    {paths.SCHEMA_JSON}")
    print(f"    Exists:  {'✓' if paths.SCHEMA_JSON.exists() else '✗'}")
    print(f"  Config:    {paths.CONFIG_FILE}")
    print(f"    Exists:  {'✓' if paths.CONFIG_FILE.exists() else '✗'}")
    print(f"  Keymap:    {paths.KEYMAP_FILE}")
    print(f"    Exists:  {'✓' if paths.KEYMAP_FILE.exists() else '✗'}")
    print()

    # Environment variables
    print(f"Environment Variables:")
    for var in ['XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME']:
        val = os.environ.get(var, '<not set>')
        print(f"  {var}: {val}")
    print()

    print("=" * 60)
    sys.exit(0)


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="mini-datahub",
        description=f"{__app_name__} - A local-first TUI for managing datasets",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information with ASCII art",
    )

    parser.add_argument(
        "--version-info",
        action="store_true",
        help="Show detailed version and system information",
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        metavar="PATH",
        help=(
            "Override data directory location. "
            "Examples: "
            "Linux: ~/.local/share/Hei-DataHub | "
            "macOS: ~/Library/Application Support/Hei-DataHub | "
            "Windows: C:\\Users\\<User>\\AppData\\Local\\Hei-DataHub"
        ),
    )

    parser.add_argument(
        "--set",
        action="append",
        metavar="KEY=VALUE",
        help="Set config override for this session (e.g., --set search.debounce_ms=200)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Reindex command
    parser_reindex = subparsers.add_parser(
        "reindex",
        help="Reindex all datasets from the data directory"
    )
    parser_reindex.set_defaults(func=handle_reindex)

    # Doctor diagnostic command
    parser_doctor = subparsers.add_parser(
        "doctor",
        help="Run system diagnostics and health checks"
    )
    parser_doctor.set_defaults(func=handle_doctor)

    # Paths diagnostic command
    parser_paths = subparsers.add_parser(
        "paths",
        help="Show diagnostic information about application paths"
    )
    parser_paths.set_defaults(func=handle_paths)

    # Update command
    parser_update = subparsers.add_parser(
        "update",
        help="Update Hei-DataHub to the latest version (atomic - never breaks existing install)"
    )
    parser_update.add_argument(
        "--branch",
        type=str,
        default=None,
        help="Git branch to install from (if not specified, interactive selection will be shown)"
    )
    parser_update.add_argument(
        "--force",
        action="store_true",
        help="Skip preflight safety checks (use with caution)"
    )
    parser_update.add_argument(
        "--check",
        action="store_true",
        help="Check installation health and offer to repair if broken"
    )
    parser_update.add_argument(
        "--repair",
        action="store_true",
        help="Repair a broken installation (alias for --check)"
    )
    parser_update.set_defaults(func=handle_update)

    # Desktop integration command with subcommands
    parser_desktop = subparsers.add_parser(
        "desktop",
        help="Manage desktop integration (Linux only)"
    )
    desktop_subparsers = parser_desktop.add_subparsers(dest="desktop_command")

    parser_desktop_install = desktop_subparsers.add_parser(
        "install",
        help="Install desktop integration (icons and .desktop entry)"
    )
    parser_desktop_install.add_argument(
        "--force",
        action="store_true",
        help="Force reinstall even if already up-to-date"
    )
    parser_desktop_install.add_argument(
        "--no-cache-refresh",
        action="store_true",
        help="Skip refreshing icon caches"
    )
    parser_desktop_install.set_defaults(func=handle_setup_desktop)

    parser_desktop_uninstall = desktop_subparsers.add_parser(
        "uninstall",
        help="Uninstall desktop integration (removes launcher and icons)"
    )
    parser_desktop_uninstall.set_defaults(func=handle_uninstall)

    # Keymap commands
    parser_keymap = subparsers.add_parser(
        "keymap",
        help="Manage custom keybindings"
    )
    keymap_subparsers = parser_keymap.add_subparsers(dest="keymap_command")

    parser_keymap_export = keymap_subparsers.add_parser(
        "export",
        help="Export current keybindings to a file"
    )
    parser_keymap_export.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output file path (default: ~/.hei-datahub/keybindings.yaml)"
    )
    parser_keymap_export.set_defaults(func=handle_keymap_export)

    parser_keymap_import = keymap_subparsers.add_parser(
        "import",
        help="Import keybindings from a file"
    )
    parser_keymap_import.add_argument(
        "input",
        help="Input file path"
    )
    parser_keymap_import.set_defaults(func=handle_keymap_import)

    # Auth commands (Linux only)
    parser_auth = subparsers.add_parser(
        "auth",
        help="Manage WebDAV authentication (Linux only)"
    )
    auth_subparsers = parser_auth.add_subparsers(dest="auth_command")

    parser_auth_setup = auth_subparsers.add_parser(
        "setup",
        help="Interactive setup wizard for WebDAV credentials",
        aliases=["config"]
    )
    parser_auth_setup.add_argument(
        "--url",
        type=str,
        help="WebDAV URL"
    )
    parser_auth_setup.add_argument(
        "--username",
        type=str,
        help="Username (optional for token auth)"
    )
    parser_auth_setup.add_argument(
        "--token",
        type=str,
        help="WebDAV token"
    )
    parser_auth_setup.add_argument(
        "--password",
        type=str,
        help="WebDAV password"
    )
    parser_auth_setup.add_argument(
        "--library",
        type=str,
        help="Library/folder name in WebDAV (e.g., Testing-hei-datahub)"
    )
    parser_auth_setup.add_argument(
        "--store",
        choices=["keyring", "env"],
        help="Force storage backend (keyring or env)"
    )
    parser_auth_setup.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip credential validation"
    )
    parser_auth_setup.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing config without prompting"
    )
    parser_auth_setup.add_argument(
        "--timeout",
        type=int,
        default=8,
        help="Validation timeout in seconds (default: 8)"
    )
    parser_auth_setup.add_argument(
        "--non-interactive",
        action="store_true",
        help="Non-interactive mode (requires --url and --token or --password)"
    )
    parser_auth_setup.set_defaults(func=handle_auth_setup)

    parser_auth_status = auth_subparsers.add_parser(
        "status",
        help="Show current authentication status"
    )
    parser_auth_status.set_defaults(func=handle_auth_status)

    parser_auth_doctor = auth_subparsers.add_parser(
        "doctor",
        help="Run WebDAV authentication diagnostics"
    )
    parser_auth_doctor.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser_auth_doctor.add_argument(
        "--no-write",
        action="store_true",
        help="Skip write permission tests"
    )
    parser_auth_doctor.add_argument(
        "--timeout",
        type=int,
        default=8,
        help="Network timeout in seconds (default: 8)"
    )
    parser_auth_doctor.set_defaults(func=handle_auth_doctor)

    parser_auth_clear = auth_subparsers.add_parser(
        "clear",
        help="Clear stored WebDAV credentials"
    )
    parser_auth_clear.add_argument(
        "--force",
        action="store_true",
        help="Skip interactive confirmation"
    )
    parser_auth_clear.add_argument(
        "--all",
        action="store_true",
        help="Also remove cached session files"
    )
    parser_auth_clear.set_defaults(func=handle_auth_clear)

    # Add 'setup' as top-level alias for 'auth setup'
    parser_setup = subparsers.add_parser(
        "setup",
        help="Alias for 'auth setup' - configure WebDAV authentication (Linux)"
    )
    parser_setup.add_argument(
        "--url",
        type=str,
        help="WebDAV URL"
    )
    parser_setup.add_argument(
        "--username",
        type=str,
        help="Username (optional for token auth)"
    )
    parser_setup.add_argument(
        "--token",
        type=str,
        help="WebDAV token"
    )
    parser_setup.add_argument(
        "--password",
        type=str,
        help="WebDAV password"
    )
    parser_setup.add_argument(
        "--library",
        type=str,
        help="Library/folder name in WebDAV (e.g., Testing-hei-datahub)"
    )
    parser_setup.add_argument(
        "--store",
        choices=["keyring", "env"],
        help="Force storage backend (keyring or env)"
    )
    parser_setup.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip credential validation"
    )
    parser_setup.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing config without prompting"
    )
    parser_setup.add_argument(
        "--timeout",
        type=int,
        default=8,
        help="Validation timeout in seconds (default: 8)"
    )
    parser_setup.add_argument(
        "--non-interactive",
        action="store_true",
        help="Non-interactive mode (requires --url and --token or --password)"
    )
    parser_setup.set_defaults(func=handle_auth_setup)

    # Parse arguments
    args = parser.parse_args()

    # Handle --version flag (simple display with dog ASCII)
    if hasattr(args, 'version') and args.version:
        print_version_info(verbose=False)
        sys.exit(0)

    # Handle --version-info flag (detailed display with dog ASCII)
    if hasattr(args, 'version_info') and args.version_info:
        print_version_info(verbose=True)
        sys.exit(0)

    # Initialize workspace on first run (creates dirs, copies packaged datasets)
    # This happens BEFORE any command to ensure data is always available
    from mini_datahub.infra.paths import initialize_workspace
    initialize_workspace()

    # Ensure desktop assets are installed (Linux only, idempotent, fast)
    # This happens automatically on first run after workspace initialization
    try:
        from hei_datahub.desktop_install import ensure_desktop_assets_once
        # Only show message if actually installing (not if already present)
        if ensure_desktop_assets_once(verbose=False):
            # Installed for first time - show a subtle message
            print("✓ Desktop integration installed")
    except ImportError:
        pass  # Desktop integration module not available
    except Exception:
        pass  # Silently ignore errors during auto-install

    # Apply CLI config overrides
    if hasattr(args, 'set') and args.set:
        from mini_datahub.services.config import get_config
        config = get_config()
        config.parse_cli_overrides(args.set)

    # Handle desktop subcommands
    if args.command == "desktop":
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(1)
    # Handle keymap subcommands
    elif args.command == "keymap":
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(1)
    # Handle auth subcommands
    elif args.command == "auth":
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(1)
    # If no command specified, launch TUI
    elif args.command is None:
        handle_tui(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
