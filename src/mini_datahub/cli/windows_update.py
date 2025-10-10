"""Windows-specific update logic using external batch script to avoid file locks."""

import sys
import tempfile
import os
from rich.panel import Panel


def windows_update(args, console):
    """Windows-specific update using external batch script to avoid file locks."""

    console.print("\n[bold cyan]🪟 Windows Update[/bold cyan]\n")

    # Get branch parameter from args or ask user
    branch = getattr(args, 'branch', None)

    if not branch:
        # Show branch options
        console.print("[bold yellow]Select branch to update:[/bold yellow]")
        console.print("  [cyan]1[/cyan]. main (stable)")
        console.print("  [cyan]2[/cyan]. dev (development)")
        console.print("  [cyan]3[/cyan]. fix/windows-update-bug (current fix)")
        console.print()

        branch_choice = input("Enter choice [1-3] (default: 1): ").strip() or "1"

        branch_map = {
            "1": "main",
            "2": "dev",
            "3": "fix/windows-update-bug"
        }
        branch = branch_map.get(branch_choice, "main")

    # Confirm update
    console.print(f"\n[bold]Update to branch:[/bold] [cyan]{branch}[/cyan]")
    confirm = input("Continue? [Y/n]: ").strip().lower()

    if confirm and confirm != 'y':
        console.print("\n[yellow]Update cancelled.[/yellow]")
        sys.exit(0)

    # Create temporary batch script
    batch_content = f"""@echo off
cls
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │                                                                │
echo │              Hei-DataHub Windows Update                       │
echo │                                                                │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo Branch: {branch}
echo.
echo [1/3] Waiting for Python process to exit...
timeout /t 2 /nobreak >nul

echo [2/3] Checking if hei-datahub.exe is still running...
:WAIT_LOOP
tasklist /FI "IMAGENAME eq hei-datahub.exe" 2>NUL | find /I /N "hei-datahub.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo        Still running... waiting 2 more seconds
    timeout /t 2 /nobreak >nul
    goto WAIT_LOOP
)

echo [3/3] Running update...
echo.

uv tool install --force --python-preference only-managed git+ssh://git@github.com/0xpix/Hei-DataHub.git@{branch}

if %ERRORLEVEL% neq 0 (
    echo.
    echo ┌────────────────────────────────────────────────────────────────┐
    echo │  ERROR: Update failed!                                        │
    echo └────────────────────────────────────────────────────────────────┘
    echo.
    echo Try using HTTPS with a token:
    echo   1. Get token: https://github.com/settings/tokens
    echo   2. Run: set GH_PAT=your_token
    echo   3. Run: uv tool install --force git+https://%%GH_PAT%%@github.com/0xpix/Hei-DataHub@{branch}
    echo.
    pause
    exit /b 1
)

echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │                                                                │
echo │  ✓ Update completed successfully!                             │
echo │                                                                │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo You can now run: hei-datahub
echo.
pause
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
        temp_batch = f.name
        f.write(batch_content)

    # Execute batch script using 'call' to run in the same window
    console.print("\n[bold green]✓ Starting update...[/bold green]")
    console.print("[dim]Preparing update script...[/dim]")

    import subprocess
    import time

    # Give user a moment to see the message
    time.sleep(1)

    # Use 'call' command to run batch script in current terminal
    # Using shell=True allows the batch to continue in the same window after Python exits
    subprocess.Popen(f'call "{temp_batch}"', shell=True)

    # Give subprocess a moment to start, then exit to release the file lock
    time.sleep(0.5)

    # Exit immediately to release the file lock
    # The batch script will clear the screen and show clean output
    sys.exit(0)
