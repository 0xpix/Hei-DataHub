<#
.SYNOPSIS
    Builds a standalone PyInstaller binary for Hei-DataHub on Windows.
.DESCRIPTION
    This script automates the build process for the Windows executable.
    It uses 'uv' if available, otherwise falls back to 'pip'.
.EXAMPLE
    .\scripts\build_windows_exe.ps1
#>

$ErrorActionPreference = "Stop"

function Show-Progress {
    param([string]$Message)
    Write-Host "  $Message... " -NoNewline
}

function Complete-Progress {
    Write-Host "✅"
}

function Error-Progress {
    Write-Host "❌"
}

# Check for uv
$UseUv = $null
if (Get-Command "uv" -ErrorAction SilentlyContinue) {
    $UseUv = $true
} else {
    $UseUv = $false
    Write-Warning "uv not found, falling back to pip/python"
}

# Install PyInstaller
Show-Progress "Checking PyInstaller"
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller check failed"
    }
    Complete-Progress
} catch {
    Write-Host ""
    Write-Host "  Installing PyInstaller..."
    if ($UseUv) {
        uv add --dev pyinstaller
    } else {
        pip install pyinstaller
    }
    if ($LASTEXITCODE -ne 0) {
        Error-Progress
        Write-Error "Failed to install PyInstaller"
    }
}

# Clean previous builds
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\hei-datahub.exe") { Remove-Item -Force "dist\hei-datahub.exe" }
if (Test-Path "hei-datahub.spec") { Remove-Item -Force "hei-datahub.spec" }

# Build the binary
Write-Host "  Building binary (this may take a while)..."

# Note: semi-colon for path separator on Windows
$PyInstallerArgs = @(
    "--onefile",
    "--name=hei-datahub",
    "--icon=win-icon.ico",
    "--add-data=src/hei_datahub/infra/sql;hei_datahub/infra/sql",
    "--add-data=src/hei_datahub/ui/styles;hei_datahub/ui/styles",
    "--add-data=src/hei_datahub/ui/assets;hei_datahub/ui/assets",
    "--add-data=src/hei_datahub/assets;hei_datahub/assets",
    "--add-data=src/hei_datahub/version.yaml;hei_datahub",
    "--hidden-import=hei_datahub",
    "--hidden-import=hei_datahub.cli.main",
    "--hidden-import=textual",
    "--hidden-import=textual.widgets",
    "--hidden-import=textual.containers",
    "--collect-all=textual",
    "--clean",
    "src/hei_datahub/cli/main.py"
)

# Run PyInstaller
# access python directly to ensure we use the environment
if ($UseUv) {
    uv run pyinstaller $PyInstallerArgs
} else {
    python -m PyInstaller $PyInstallerArgs
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed"
}

# Organize output
Show-Progress "Organizing output"
if (-not (Test-Path "dist\windows")) {
    New-Item -ItemType Directory -Path "dist\windows" | Out-Null
}

if (Test-Path "dist\hei-datahub.exe") {
    Move-Item -Force "dist\hei-datahub.exe" "dist\windows\hei-datahub.exe"
    Complete-Progress
} else {
    Error-Progress
    Write-Error "Build failed - binary not found"
}

# Clean up spec file
if (Test-Path "hei-datahub.spec") { Remove-Item -Force "hei-datahub.spec" }

Write-Host ""
Write-Host "✅ Binary built successfully!"
Write-Host "   Location: dist\windows\hei-datahub.exe"
Write-Host ""
