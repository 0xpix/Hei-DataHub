@echo off
REM Windows Update Script for Hei-DataHub
REM This script updates the app from outside the running executable to avoid file locks
REM Usage: windows_update.bat [branch_name]

setlocal

echo.
echo =====================================
echo  Hei-DataHub Windows Update Helper
echo =====================================
echo.

REM Get branch parameter (default to main)
set BRANCH=%1
if "%BRANCH%"=="" set BRANCH=main

echo Updating to branch: %BRANCH%
echo.

REM Check if hei-datahub is running
echo [1/4] Checking for running instances...
tasklist /FI "IMAGENAME eq hei-datahub.exe" 2>NUL | find /I /N "hei-datahub.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo WARNING: Hei-DataHub is currently running!
    echo.
    echo Please close all Hei-DataHub windows before continuing.
    echo Press any key when ready, or Ctrl+C to cancel...
    pause >nul
    echo.
)

REM Check UV is installed
echo [2/4] Checking UV installation...
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: UV not found in PATH
    echo.
    echo Install UV from: https://docs.astral.sh/uv/getting-started/installation/
    echo.
    pause
    exit /b 1
)

REM Check Git is installed
echo [3/4] Checking Git installation...
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Git not found in PATH
    echo.
    echo Install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

REM Perform the update
echo [4/4] Running update...
echo.

uv tool install --force --python-preference only-managed git+ssh://git@github.com/0xpix/Hei-DataHub.git@%BRANCH%

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Update failed!
    echo.
    echo Try using HTTPS with a token instead:
    echo   1. Get a token from: https://github.com/settings/tokens
    echo   2. Run: set GH_PAT=your_token_here
    echo   3. Run: uv tool install --force --python-preference only-managed git+https://%%GH_PAT%%@github.com/0xpix/Hei-DataHub@%BRANCH%
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
