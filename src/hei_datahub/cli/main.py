"""
CLI entrypoint for Hei-DataHub.
"""
import argparse
import os
import sys
from pathlib import Path

from hei_datahub.version import __version__, __app_name__, print_version_info

# Import handlers from organized modules
from hei_datahub.cli.data import handle_reindex
from hei_datahub.cli.config import handle_keymap_export, handle_keymap_import
from hei_datahub.cli.system import handle_tui, handle_paths, handle_doctor
from hei_datahub.cli.desktop import handle_setup_desktop, handle_uninstall
from hei_datahub.cli.update import handle_update
from hei_datahub.cli.auth import (
    handle_auth_setup,
    handle_auth_status,
    handle_auth_doctor,
    handle_auth_clear,
)


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="hei-datahub",
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
        help="Clear stored WebDAV credentials and search index"
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
    from hei_datahub.infra.paths import initialize_workspace, _is_dev_mode
    initialize_workspace()

    # Ensure desktop assets are installed (Linux only, idempotent, fast)
    # This happens automatically on first run after workspace initialization
    # Skip in dev mode, if explicitly disabled, or if running from repo root (dev heuristic)
    is_repo_root = (Path.cwd() / "pyproject.toml").exists() and (Path.cwd() / "src" / "hei_datahub").exists()

    if not _is_dev_mode() and not os.environ.get("HEI_DATAHUB_SKIP_DESKTOP_INSTALL") and not is_repo_root:
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
        from hei_datahub.services.config import get_config
        config = get_config()
        config.parse_cli_overrides(args.set)

    # Dispatch commands centrally and ensure the entrypoint is the only place
    # that terminates the process. Handlers should return integer exit codes.
    def _call_handler(func, args):
        try:
            rc = func(args)
            # If handler returned None, treat as success
            return 0 if rc is None else int(rc)
        except SystemExit as se:
            # Preserve explicit exit codes from legacy handlers
            code = se.code
            try:
                return 0 if code is None else int(code)
            except Exception:
                return 1
        except Exception as e:
            # Unexpected exception in handler -> non-zero exit
            import traceback
            print(f"❌ Command failed: {e}", file=sys.stderr)
            traceback.print_exc()
            return 1

    if args.command == "desktop":
        if hasattr(args, 'func'):
            sys.exit(_call_handler(args.func, args))
        else:
            parser.print_help()
            sys.exit(1)
    # Handle keymap subcommands
    elif args.command == "keymap":
        if hasattr(args, 'func'):
            sys.exit(_call_handler(args.func, args))
        else:
            parser.print_help()
            sys.exit(1)
    # Handle auth subcommands
    elif args.command == "auth":
        if hasattr(args, 'func'):
            sys.exit(_call_handler(args.func, args))
        else:
            parser.print_help()
            sys.exit(1)
    # If no command specified, launch TUI
    elif args.command is None:
        sys.exit(_call_handler(handle_tui, args))
    else:
        # Generic dispatch for other commands
        if hasattr(args, 'func'):
            sys.exit(_call_handler(args.func, args))
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
