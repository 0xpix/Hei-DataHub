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
    """Handle the update subcommand with beautiful interactive UI."""
    import subprocess
    import time
    from pathlib import Path
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.markdown import Markdown
    from rich import box
    from rich.text import Text
    from rich.align import Align

    console = Console()

    # Load ASCII logo
    try:
        logo_path = Path(__file__).parent.parent / "ui" / "assets" / "ascii" / "logo_default.txt"
        if logo_path.exists():
            logo_text = logo_path.read_text()
        else:
            logo_text = None
    except:
        logo_text = None

    # Display beautiful header with logo
    console.print()

    if logo_text:
        # Display logo in cyan gradient
        logo_lines = logo_text.strip().split('\n')
        for line in logo_lines:
            console.print(f"[bold cyan]{line}[/bold cyan]", justify="center")
        console.print()
        console.print(Align.center("[bold bright_white]━━━━━━━━━━━━━ UPDATE MANAGER ━━━━━━━━━━━━━[/bold bright_white]"))
        console.print(Align.center("[dim italic]Keep your DataHub fresh and updated ✨[/dim italic]"))
    else:
        # Fallback if logo not found
        console.print(Panel.fit(
            "[bold cyan]🚀 Hei-DataHub Update Manager[/bold cyan]",
            border_style="cyan"
        ))

    console.print()
    console.print("─" * console.width, style="dim")
    console.print()

    # Check if UV is installed
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        console.print(Panel(
            "[red]❌ UV package manager is not installed![/red]\n\n"
            "📦 [bold]Install UV first:[/bold]\n"
            "[cyan]curl -LsSf https://astral.sh/uv/install.sh | sh[/cyan]",
            border_style="red",
            title="[red]Error[/red]"
        ))
        sys.exit(1)

    # Get current version in a nice box
    current_version = __version__
    version_box = Panel(
        f"[bold yellow]{current_version}[/bold yellow]",
        title="[bold]📍 Current Version[/bold]",
        border_style="yellow",
        padding=(0, 2)
    )
    console.print(version_box)
    console.print()

    # Define available branches with metadata
    branches = {
        "1": {
            "name": "main",
            "label": "✅ [bold green]main[/bold green] [dim](recommended)[/dim]",
            "description": "Stable release - tested and production-ready",
            "url": "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main",
        },
        "2": {
            "name": "chore/uv-install-data-desktop-v0.58.x",
            "label": "🧪 [bold yellow]v0.58.x[/bold yellow] [dim](beta)[/dim]",
            "description": "Latest beta - UV installation, cross-platform support, doctor diagnostics",
            "url": "git+ssh://git@github.com/0xpix/Hei-DataHub.git@chore/uv-install-data-desktop-v0.58.x",
        },
        "3": {
            "name": "develop",
            "label": "🚧 [bold red]develop[/bold red] [dim](dev/unstable)[/dim]",
            "description": "Development branch - bleeding edge, may be unstable",
            "url": "git+ssh://git@github.com/0xpix/Hei-DataHub.git@develop",
        },
    }

    # If branch specified via CLI, use it
    if hasattr(args, 'branch') and args.branch:
        selected_branch = args.branch
        selected_url = f"git+ssh://git@github.com/0xpix/Hei-DataHub.git@{selected_branch}"
        console.print(Panel.fit(
            f"[bold cyan]🎯 Using specified branch:[/bold cyan]\n[bold yellow]{selected_branch}[/bold yellow]",
            border_style="cyan"
        ))
    else:
        # Interactive branch selection
        table = Table(
            title="[bold cyan]📦 Available Versions[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold bright_white on blue",
            border_style="cyan",
            title_style="bold cyan"
        )
        table.add_column("Choice", justify="center", style="bold cyan", width=8)
        table.add_column("Version", style="bold", no_wrap=True, width=40)
        table.add_column("Description", style="dim")

        for key, branch in branches.items():
            table.add_row(f"[{key}]", branch["label"], branch["description"])

        console.print(table)
        console.print()

        choice = Prompt.ask(
            "[bold cyan]🔍 Select version to install[/bold cyan]",
            choices=list(branches.keys()),
            default="1"
        )

        selected_branch = branches[choice]["name"]
        selected_url = branches[choice]["url"]

        console.print()
        console.print(Panel.fit(
            f"[bold green]✓[/bold green] Selected: [bold cyan]{selected_branch}[/bold cyan]",
            border_style="green"
        ))

    console.print()

    # Show what's new (if updating to beta branch)
    if "0.58" in selected_branch:
        console.print(Panel(
            Markdown("""
### 🎉 What's New in v0.58.1-beta

#### ✨ New Features
- **Cross-platform data directories** - Windows & macOS support
- **Doctor diagnostics** - `hei-datahub doctor` for health checks
- **Data directory overrides** - CLI flag and env variable support
- **Windows compatibility** - Filename sanitization & reserved names

#### 🐛 Bug Fixes
- Fixed datasets not appearing on Windows/macOS
- Platform-specific path resolution
- Data seeding on first run

#### 📚 Testing
- 35+ automated tests
- Cross-platform verification scripts
- Comprehensive testing documentation
            """),
            title="[bold green]📋 Release Notes[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
        console.print()

    # Confirm update
    if not Confirm.ask(f"[bold]Continue with update?[/bold]", default=True):
        console.print("[yellow]⚠ Update cancelled[/yellow]")
        sys.exit(0)

    console.print()

    # Perform update with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:

        # Step 1: Fetching
        task1 = progress.add_task("[cyan]Fetching package from GitHub...", total=100)

        try:
            # Start the uv command
            result = subprocess.Popen(
                ["uv", "tool", "install", "--reinstall", selected_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Simulate progress (UV doesn't give us real progress)
            for i in range(30):
                time.sleep(0.1)
                progress.update(task1, advance=3)

            progress.update(task1, completed=100)
            progress.remove_task(task1)

            # Step 2: Resolving dependencies
            task2 = progress.add_task("[cyan]Resolving dependencies...", total=100)
            for i in range(20):
                time.sleep(0.05)
                progress.update(task2, advance=5)
            progress.update(task2, completed=100)
            progress.remove_task(task2)

            # Step 3: Installing
            task3 = progress.add_task("[cyan]Installing packages...", total=100)

            # Wait for process to complete while showing progress
            while result.poll() is None:
                time.sleep(0.1)
                if progress.tasks[0].completed < 95:
                    progress.update(task3, advance=2)

            progress.update(task3, completed=100)

            # Get the output
            output = result.stdout.read() if result.stdout else ""
            returncode = result.returncode

        except Exception as e:
            console.print(f"\n[red]❌ Update failed: {e}[/red]")
            sys.exit(1)

    console.print()

    if returncode == 0:
        # Success!
        console.print()
        console.print(Panel(
            "[bold green]✨ Update completed successfully! ✨[/bold green]\n\n"
            f"[dim]Updated to:[/dim] [bold cyan]{selected_branch}[/bold cyan]\n"
            f"[dim]From:[/dim] [yellow]{current_version}[/yellow] → [green]Latest[/green]",
            title="[bold green]🎉 Success[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
        console.print()

        next_steps = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 1)
        )
        next_steps.add_column("Icon", style="bold cyan")
        next_steps.add_column("Command", style="cyan")
        next_steps.add_column("Description", style="dim")

        next_steps.add_row("📋", "hei-datahub --version-info", "View detailed version information")
        next_steps.add_row("🏥", "hei-datahub doctor", "Run system health checks")
        next_steps.add_row("🚀", "hei-datahub", "Launch the application")

        console.print(Panel(
            next_steps,
            title="[bold]🎯 Next Steps[/bold]",
            border_style="cyan"
        ))
        console.print()
        sys.exit(0)
    else:
        console.print(Panel(
            "[bold red]❌ Update failed![/bold red]\n\n"
            "[dim]Check the error output above for details.[/dim]",
            border_style="red"
        ))
        console.print()
        console.print("💡 Troubleshooting:")
        console.print("   • Check your SSH keys: [cyan]ssh -T git@github.com[/cyan]")
        console.print("   • Try with a token: Set [cyan]GH_PAT[/cyan] environment variable")
        console.print("   • Run with [cyan]--branch main[/cyan] to try stable version")
        console.print()
        sys.exit(1)


def handle_doctor(args):
    """Handle doctor diagnostic command."""
    from mini_datahub.cli.doctor import run_doctor

    # Pass data-dir override if provided
    data_dir_override = getattr(args, 'data_dir', None)
    exit_code = run_doctor(data_dir_override)
    sys.exit(exit_code)


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
        help="Update Hei-DataHub to the latest version"
    )
    parser_update.add_argument(
        "--branch",
        type=str,
        default=None,
        help="Git branch to install from (if not specified, interactive selection will be shown)"
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
