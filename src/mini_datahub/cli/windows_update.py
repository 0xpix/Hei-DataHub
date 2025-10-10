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
echo [1/3] Waiting for Python process to exit...
timeout /t 2 /nobreak >nul

echo [2/3] Checking if hei-datahub.exe is still running...
:WAIT_LOOP
tasklist /FI "IMAGENAME eq hei-datahub.exe" 2>NUL | find /I /N "hei-datahub.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Still running... waiting 2 more seconds
    timeout /t 2 /nobreak >nul
    goto WAIT_LOOP
)

echo [3/3] Running update...
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

    # Execute batch script in the same terminal using START command
    # START /B runs it in the background, allowing Python to exit immediately
    console.print("\n[bold green]✓ Starting update...[/bold green]")
    console.print("[dim]The update will continue in 3 seconds...[/dim]\n")

    import subprocess
    # Use subprocess.Popen to start the batch script without waiting
    # The batch script will wait for Python to exit before running uv
    # On Windows, we don't create a new window - it runs in the same terminal
    try:
        # Try to use CREATE_NO_WINDOW flag (Windows only)
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(['cmd.exe', '/c', temp_batch], creationflags=CREATE_NO_WINDOW)
    except:
        # Fallback for non-Windows or if flag doesn't work
        subprocess.Popen(['cmd.exe', '/c', temp_batch])

    # Exit immediately to release the file lock
    # The batch script is now running independently and will check for process exit
    sys.exit(0)
