"""Windows-specific update logic using external batch script to avoid file locks."""

import sys
import tempfile
import os
from rich.panel import Panel


def windows_update(args, console):
    """Windows-specific update using external batch script to avoid file locks."""

    console.print("\n[bold cyan]🪟 Windows Update Strategy[/bold cyan]\n")
    console.print("[dim]Windows locks running executables, so we'll use an external script...[/dim]\n")

    # Get branch parameter
    branch = getattr(args, 'branch', None) or 'main'

    # Create temporary batch script
    batch_content = f"""@echo off
echo.
echo =====================================
echo  Hei-DataHub Windows Update
echo =====================================
echo.
echo Updating to branch: {branch}
echo.
echo [1/2] Waiting for app to close...
timeout /t 3 /nobreak >nul
echo [2/2] Running update...
echo.

uv tool install --force --python-preference only-managed git+ssh://git@github.com/0xpix/Hei-DataHub.git@{branch}

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Update failed!
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
echo =====================================
echo  Update completed successfully!
echo =====================================
echo.
echo You can now run: hei-datahub
echo.
pause
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
        temp_batch = f.name
        f.write(batch_content)

    console.print(Panel(
        "[bold green]✓ Update script created[/bold green]\n\n"
        "The app will now:\n"
        "  1. Exit to release the executable lock\n"
        "  2. Run the update script in this window\n"
        "  3. Update will complete automatically\n\n"
        "[dim]Press any key to continue...[/dim]",
        title="[bold cyan]🚀 Ready to Update[/bold cyan]",
        border_style="cyan"
    ))

    input()  # Wait for user confirmation

    # Execute batch script in the same terminal
    console.print("\n[bold green]✓ Starting update...[/bold green]\n")

    # Use os.system to run the batch file directly, then exit
    # This works on both native Windows and WSL
    os.system(f'cmd.exe /c "{temp_batch}"')

    # Exit after the batch script completes
    sys.exit(0)
