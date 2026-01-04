"""Windows-specific update logic using external batch script to avoid file locks."""

import os
import sys
import tempfile


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

    # Create temporary batch script that runs in a new terminal
    batch_content = f"""@echo off
REM Wait for Python to fully exit
timeout /t 2 /nobreak >nul

REM Check if hei-datahub.exe is still running
:WAIT_LOOP
tasklist /FI "IMAGENAME eq hei-datahub.exe" 2>NUL | find /I /N "hei-datahub.exe">NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 2 /nobreak >nul
    goto WAIT_LOOP
)

cls
echo.
echo ================================================================
echo.
echo              Hei-DataHub Windows Update
echo.
echo ================================================================
echo.
echo Branch: {branch}
echo.
echo Running update...
echo.

uv tool install --force --python-preference only-managed git+ssh://git@github.com/0xpix/Hei-DataHub.git@{branch}

if %ERRORLEVEL% neq 0 (
    echo.
    echo ================================================================
    echo   ERROR: Update failed!
    echo ================================================================
    echo.
    echo Try using HTTPS with a token:
    echo   1. Get token: https://github.com/settings/tokens
    echo   2. Run: set GH_PAT=your_token
    echo   3. Run: uv tool install --force git+https://%%GH_PAT%%@github.com/0xpix/Hei-DataHub@{branch}
    echo.
    echo Press any key to open a new terminal...
    pause >nul
    start cmd
    exit
)

echo.
echo ================================================================
echo.
echo   Update completed successfully!
echo.
echo ================================================================
echo.
echo Opening new terminal in 3 seconds...
timeout /t 3 /nobreak >nul

REM Open new terminal and close this one
start cmd
exit
"""

    # Write to temp file with UTF-8 encoding
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
        temp_batch = f.name
        f.write(batch_content)

    # Execute batch script in a NEW terminal window
    console.print("\n[bold green]✓ Starting update in new window...[/bold green]")
    console.print("[dim]This terminal will close and update will run in a new window.[/dim]\n")

    import time
    time.sleep(2)

    # Launch batch in a NEW cmd window, then close this terminal
    os.system(f'start cmd /k "{temp_batch}"')

    # Small delay to ensure the new window opens
    time.sleep(0.5)

    # Exit Python and close current terminal
    # The new terminal will handle the update
    sys.exit(0)
