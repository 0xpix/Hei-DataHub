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

        from mini_datahub.infra.paths import initialize_workspace
        from mini_datahub.infra.db import ensure_database

        # Initialize workspace (creates dirs, schema, sample data)
        initialize_workspace()
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
