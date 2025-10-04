"""
CLI entrypoint for Hei-DataHub.
"""
import argparse
import sys

from mini_datahub.version import __version__, __app_name__


def handle_reindex(args):
    """Handle the reindex subcommand."""
    from mini_datahub.index import reindex_all

    print("Reindexing datasets from data directory...")
    try:
        count, errors = reindex_all()
        print(f"✓ Successfully indexed {count} dataset(s)")

        if errors:
            print(f"\n⚠ Encountered {len(errors)} error(s):")
            for error in errors:
                print(f"  • {error}")
            sys.exit(1)
        else:
            print("All datasets indexed successfully!")
            sys.exit(0)
    except Exception as e:
        print(f"✗ Reindexing failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_tui(args):
    """Handle the default TUI launch."""
    from mini_datahub.tui import run_tui
    from mini_datahub.utils import ensure_directories

    # Ensure required directories exist
    ensure_directories()

    # Launch TUI
    try:
        run_tui()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching TUI: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="mini-datahub",
        description="A local-first TUI for managing datasets with consistent metadata",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Reindex subcommand
    reindex_parser = subparsers.add_parser(
        "reindex",
        help="Rebuild search index from YAML files in data directory",
    )
    reindex_parser.set_defaults(func=handle_reindex)

    # Parse arguments
    args = parser.parse_args()

    # If no subcommand, launch TUI
    if args.command is None:
        handle_tui(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
