"""Linux-specific update logic using AtomicUpdateManager."""

import sys
from pathlib import Path
from rich.panel import Panel
from rich.align import Align
from hei_datahub.cli.update_manager import AtomicUpdateManager, UpdateError, format_error_panel
from hei_datahub import __version__


def linux_update(args, console):
    """Linux-specific update using AtomicUpdateManager."""

    # Initialize atomic update manager
    manager = AtomicUpdateManager(console=console)

    # Handle --check or --repair flags
    if getattr(args, 'check', False) or getattr(args, 'repair', False):
        console.print("\n[bold cyan]🔍 Checking Installation Health[/bold cyan]\n")
        manager.check_and_repair()
        return

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
        console.print(Align.center("[dim italic]Atomic updates • Never lose your working app ✨[/dim italic]"))
    else:
        # Fallback if logo not found
        console.print(Panel.fit(
            "[bold cyan]🚀 Hei-DataHub Update Manager[/bold cyan]\n"
            "[dim]Atomic updates • Never lose your working app[/dim]",
            border_style="cyan"
        ))

    console.print()
    console.print("─" * console.width, style="dim")
    console.print()

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

    try:
        # Run the atomic update process
        manager.run_update(
            branch=getattr(args, 'branch', None),
            force=getattr(args, 'force', False)
        )

        # Success - show next steps
        from rich.table import Table
        from rich import box

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

    except UpdateError as e:
        # Display formatted error with phase-specific guidance
        format_error_panel(e, console)
        console.print()

        # Exit with different codes based on recoverability
        sys.exit(2 if e.recoverable else 1)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Update cancelled by user[/yellow]")
        sys.exit(130)

    except Exception as e:
        # Unexpected error
        console.print()
        console.print(Panel(
            f"[bold red]Unexpected error during update:[/bold red]\n\n"
            f"{type(e).__name__}: {str(e)}\n\n"
            "[yellow]Your existing installation should still be intact.[/yellow]\n\n"
            "If this persists, please report at:\n"
            "https://github.com/0xpix/Hei-DataHub/issues",
            title="[red]Error[/red]",
            border_style="red"
        ))
        sys.exit(1)
