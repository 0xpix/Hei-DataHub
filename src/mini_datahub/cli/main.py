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

        from mini_datahub.infra.paths import ensure_directories
        from mini_datahub.infra.db import ensure_database

        # Ensure required directories and database exist
        ensure_directories()
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

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Reindex command
    parser_reindex = subparsers.add_parser(
        "reindex",
        help="Reindex all datasets from the data directory"
    )
    parser_reindex.set_defaults(func=handle_reindex)

    # Parse arguments
    args = parser.parse_args()

    # Handle --version-info flag
    if hasattr(args, 'version_info') and args.version_info:
        print_version_info(verbose=True)
        sys.exit(0)

    # If no command specified, launch TUI
    if args.command is None:
        handle_tui(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
