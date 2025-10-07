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
    """Handle the update subcommand."""
    import subprocess
    from pathlib import Path
    
    print("Updating Hei-DataHub...")
    print()
    
    # Determine the installation source
    branch = args.branch if hasattr(args, 'branch') and args.branch else "chore/uv-install-data-desktop-v0.58.x"
    repo_url = f"git+ssh://git@github.com/0xpix/Hei-DataHub.git@{branch}#egg=hei-datahub"
    
    print(f"  Source: {repo_url}")
    print(f"  Using uv tool install --upgrade...")
    print()
    
    try:
        # Run uv tool install with --upgrade flag
        result = subprocess.run(
            ["uv", "tool", "install", "--upgrade", repo_url],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ Update completed successfully!")
            print()
            print("Run 'hei-datahub --version-info' to see the new version.")
            sys.exit(0)
        else:
            print("❌ Update failed!")
            print()
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ Error: 'uv' command not found!")
        print()
        print("Please ensure UV is installed:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)


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
        action="version",
        version=f"{__app_name__} {__version__}",
    )

    parser.add_argument(
        "--version-info",
        action="store_true",
        help="Show detailed version and system information",
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

    # Paths diagnostic command
    parser_paths = subparsers.add_parser(
        "paths",
        help="Show diagnostic information about application paths"
    )
    parser_paths.set_defaults(func=handle_paths)

    # Update command
    parser_update = subparsers.add_parser(
        "update",
        help="Update Hei-DataHub to the latest version"
    )
    parser_update.add_argument(
        "--branch",
        type=str,
        default="chore/uv-install-data-desktop-v0.58.x",
        help="Git branch to install from (default: chore/uv-install-data-desktop-v0.58.x)"
    )
    parser_update.set_defaults(func=handle_update)

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

    # Parse arguments
    args = parser.parse_args()

    # Handle --version-info flag
    if hasattr(args, 'version_info') and args.version_info:
        print_version_info(verbose=True)
        sys.exit(0)

    # Initialize workspace on first run (creates dirs, copies packaged datasets)
    # This happens BEFORE any command to ensure data is always available
    from mini_datahub.infra.paths import initialize_workspace
    initialize_workspace()

    # Apply CLI config overrides
    if hasattr(args, 'set') and args.set:
        from mini_datahub.services.config import get_config
        config = get_config()
        config.parse_cli_overrides(args.set)

    # Handle keymap subcommands
    if args.command == "keymap":
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
