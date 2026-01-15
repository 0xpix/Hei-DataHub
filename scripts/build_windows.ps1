<#
.SYNOPSIS
    Builds Hei-DataHub Windows executable and NSIS installer.
.DESCRIPTION
    1. Builds standalone .exe using PyInstaller
    2. Creates NSIS setup installer
.NOTES
    Requires: Python, PyInstaller, NSIS (makensis)
#>

$ErrorActionPreference = "Continue"
$Host.UI.RawUI.WindowTitle = "Hei-DataHub Windows Build"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

function Write-Banner {
    param([string]$Text, [ConsoleColor]$Color = "Cyan")
    $width = 70
    $border = "=" * $width
    $padding = [math]::Max(0, ($width - $Text.Length - 4) / 2)
    $leftPad = " " * [math]::Floor($padding)
    $rightPad = " " * [math]::Ceiling($padding)

    Write-Host ""
    Write-Host $border -ForegroundColor $Color
    Write-Host ("||" + $leftPad + " $Text " + $rightPad + "||") -ForegroundColor $Color
    Write-Host $border -ForegroundColor $Color
    Write-Host ""
}

function Write-Step {
    param([int]$Number, [int]$Total, [string]$Text)
    Write-Host ""
    Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor DarkGray
    Write-Host "  | " -ForegroundColor DarkGray -NoNewline
    Write-Host "STEP $Number/$Total" -ForegroundColor Yellow -NoNewline
    Write-Host " | " -ForegroundColor DarkGray -NoNewline
    Write-Host "$Text" -ForegroundColor White -NoNewline
    $spaces = 52 - $Text.Length
    if ($spaces -gt 0) { Write-Host (" " * $spaces) -NoNewline }
    Write-Host "|" -ForegroundColor DarkGray
    Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor DarkGray
}

function Update-Progress {
    param([int]$Percent, [string]$Status = "")
    $width = 50
    $complete = [math]::Round($width * $Percent / 100)
    $remaining = $width - $complete

    $bar = "#" * $complete + "-" * $remaining
    $percentStr = "$Percent%".PadLeft(4)
    $statusStr = if ($Status) { " - $Status" } else { "" }
    $statusPadded = $statusStr.PadRight(35)

    # Build the line and overwrite
    $line = "  [$($bar.Substring(0, $complete))" + "$($bar.Substring($complete))] $percentStr$statusPadded"
    Write-Host "`r$line" -NoNewline
}

function Complete-Progress {
    param([string]$Status = "Complete")
    Update-Progress -Percent 100 -Status $Status
    Write-Host ""  # Move to next line
}

function Write-Success {
    param([string]$Text)
    Write-Host "  [OK] " -ForegroundColor Green -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Write-Failure {
    param([string]$Text)
    Write-Host ""  # Ensure we're on a new line
    Write-Host "  [FAIL] " -ForegroundColor Red -NoNewline
    Write-Host $Text -ForegroundColor White
}

function Format-FileSize {
    param([long]$Size)
    if ($Size -gt 1GB) { return "{0:N2} GB" -f ($Size / 1GB) }
    if ($Size -gt 1MB) { return "{0:N2} MB" -f ($Size / 1MB) }
    if ($Size -gt 1KB) { return "{0:N2} KB" -f ($Size / 1KB) }
    return "$Size bytes"
}

# ==============================================================================
# CONFIGURATION
# ==============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir

# Navigate to project root
Set-Location $ProjectRoot

$DistDir = Join-Path $ProjectRoot "dist"
$InstallerDir = Join-Path $ScriptDir "installers"
$NsisScript = Join-Path $InstallerDir "hei_datahub.nsi"

# ==============================================================================
# START BUILD
# ==============================================================================

Clear-Host
Write-Banner "HEI-DATAHUB WINDOWS BUILD" -Color Cyan

# Extract version from version.yaml
$VersionLine = Get-Content -Path "version.yaml" | Select-String "version:"
$AppVersion = $VersionLine.ToString().Split(":")[1].Trim().Trim('"').Trim("'")
$PortableName = "hei-datahub-v$AppVersion-portable.exe"
$SetupName = "hei-datahub-v$AppVersion-setup.exe"

Write-Host "  Project: " -NoNewline -ForegroundColor Gray
Write-Host "Hei-DataHub" -ForegroundColor White
Write-Host "  Version: " -NoNewline -ForegroundColor Gray
Write-Host $AppVersion -ForegroundColor Green
Write-Host "  Time:    " -NoNewline -ForegroundColor Gray
Write-Host (Get-Date -Format "yyyy-MM-dd HH:mm:ss") -ForegroundColor White
Write-Host ""

# ------------------------------------------------------------------------------
# STEP 1: Check Prerequisites
# ------------------------------------------------------------------------------

Write-Step -Number 1 -Total 3 -Text "Checking Prerequisites"

Update-Progress -Percent 0 -Status "Checking Python..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
} catch {
    Complete-Progress -Status "Failed"
    Write-Failure "Python not found"
    exit 1
}

Update-Progress -Percent 33 -Status "Checking PyInstaller..."

# Check/Install PyInstaller
try {
    python -m PyInstaller --version 2>&1 | Out-Null
} catch {
    Update-Progress -Percent 33 -Status "Installing PyInstaller..."
    pip install pyinstaller 2>&1 | Out-Null
}

Update-Progress -Percent 66 -Status "Checking NSIS..."

# Check NSIS
$NsisPaths = @("C:\Program Files (x86)\NSIS", "C:\Program Files\NSIS")
foreach ($Path in $NsisPaths) {
    if (Test-Path $Path) { $env:Path += ";$Path" }
}

$nsisFound = Get-Command "makensis" -ErrorAction SilentlyContinue

if (-not $nsisFound) {
    Complete-Progress -Status "Failed"
    Write-Failure "NSIS not found - install from https://nsis.sourceforge.io/"
    exit 1
}

Complete-Progress -Status "All prerequisites found"
Write-Success "Python: $pythonVersion"
Write-Success "PyInstaller: installed"
Write-Success "NSIS: $($nsisFound.Source)"

# ------------------------------------------------------------------------------
# STEP 2: Build Executable with PyInstaller
# ------------------------------------------------------------------------------

Write-Step -Number 2 -Total 3 -Text "Building Executable (PyInstaller)"

Update-Progress -Percent 5 -Status "Cleaning Python cache..."

# Clean Python cache to ensure fresh build
Get-ChildItem -Path "src" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "src" -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Force reinstall project
Update-Progress -Percent 10 -Status "Reinstalling project..."
pip uninstall hei-datahub -y 2>&1 | Out-Null
pip install -e . --no-cache-dir 2>&1 | Out-Null

Update-Progress -Percent 15 -Status "Cleaning previous builds..."

# Clean previous builds
Stop-Process -Name "hei-datahub" -ErrorAction SilentlyContinue
if (Test-Path "build") { Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue }
if (Test-Path "hei-datahub.spec") { Remove-Item -Force "hei-datahub.spec" -ErrorAction SilentlyContinue }

# Clear PyInstaller cache
$PyInstallerCache = Join-Path $env:LOCALAPPDATA "pyinstaller"
if (Test-Path $PyInstallerCache) { Remove-Item -Recurse -Force $PyInstallerCache -ErrorAction SilentlyContinue }

Update-Progress -Percent 20 -Status "Configuring PyInstaller..."

# Configure PyInstaller
$Sep = ";"
$DataArgs = @(
    "--add-data", "src/hei_datahub/ui/styles${Sep}hei_datahub/ui/styles",
    "--add-data", "src/hei_datahub/ui/assets${Sep}hei_datahub/ui/assets",
    "--add-data", "src/hei_datahub/assets${Sep}hei_datahub/assets",
    "--add-data", "src/hei_datahub/version.yaml${Sep}hei_datahub",
    "--add-data", "src/hei_datahub/schema.json${Sep}hei_datahub",
    "--add-data", "config.yaml${Sep}hei_datahub"
)

if (Test-Path "src/hei_datahub/infra/sql") {
    $DataArgs += "--add-data", "src/hei_datahub/infra/sql${Sep}hei_datahub/infra/sql"
}

# Check for icon - prefer generated high-res icon, fallback to source assets
$IconPath = "assets/icons/hei-datahub.ico"
if (-not (Test-Path $IconPath)) {
    $IconPath = "src/hei_datahub/assets/icons/favicon.ico"
}
if (Test-Path $IconPath) {
    $DataArgs += "--icon", $IconPath
    Write-Host "  Using icon: $IconPath" -ForegroundColor DarkGray
}

$PyInstallerArgs = @(
    "--noconfirm",
    "--onefile",
    "--console",
    "--name", "hei-datahub",
    "--clean",
    "--paths", "src",
    "--collect-all", "textual",
    "--collect-all", "rich",
    "--collect-all", "hei_datahub",
    "--hidden-import", "hei_datahub.ui.views",
    "--hidden-import", "hei_datahub.ui.views.update",
    "--hidden-import", "hei_datahub.ui.views.home",
    "--hidden-import", "hei_datahub.ui.views.main",
    "--hidden-import", "hei_datahub.services.windows_updater",
    "--hidden-import", "hei_datahub.services.update_check",
    "--hidden-import", "hei_datahub.infra.sql"
) + $DataArgs

Update-Progress -Percent 25 -Status "Running PyInstaller (this takes a while)..."

$EntryPoint = "src/hei_datahub/__main__.py"
python -m PyInstaller $PyInstallerArgs $EntryPoint 2>&1 | Out-Null

$ExePath = Join-Path $DistDir "hei-datahub.exe"
if (Test-Path $ExePath) {
    # Create portable version with versioned name
    $PortablePath = Join-Path $DistDir $PortableName
    Copy-Item -Path $ExePath -Destination $PortablePath -Force

    $exeSize = (Get-Item $PortablePath).Length
    Complete-Progress -Status "Executable built successfully"
    Write-Success "$PortableName ($(Format-FileSize $exeSize))"
} else {
    Complete-Progress -Status "Failed"
    Write-Failure "PyInstaller build failed"
    exit 1
}

# ------------------------------------------------------------------------------
# STEP 3: Build NSIS Installer
# ------------------------------------------------------------------------------

Write-Step -Number 3 -Total 3 -Text "Building NSIS Installer"

Update-Progress -Percent 10 -Status "Preparing files for NSIS..."

# NSIS can't access WSL paths directly, so copy to Windows temp
$WinTempDir = Join-Path $env:TEMP "hei-datahub-build"
if (Test-Path $WinTempDir) { Remove-Item -Recurse -Force $WinTempDir }
New-Item -ItemType Directory -Path $WinTempDir -Force | Out-Null

# Copy required files to Windows temp
Copy-Item -Path $ExePath -Destination $WinTempDir -Force
Copy-Item -Path $NsisScript -Destination $WinTempDir -Force

# Copy icon from installers directory (generated by generate_icon.py)
$IconPath = Join-Path $InstallerDir "hei-datahub.ico"
if (Test-Path $IconPath) {
    Copy-Item -Path $IconPath -Destination $WinTempDir -Force
    Write-Host "  Copied icon: $IconPath" -ForegroundColor DarkGray
} else {
    Write-Host "  WARNING: Icon not found at $IconPath" -ForegroundColor Yellow
    Write-Host "  Run 'make generate-icon' first" -ForegroundColor Yellow
}

Update-Progress -Percent 30 -Status "Compiling NSIS script (v$AppVersion)..."

# Run NSIS from Windows temp directory
Push-Location $WinTempDir
# Pass version and output filename to NSIS
$nsisOutput = makensis /DVERSION=$AppVersion /X"OutFile $SetupName" /V2 "hei_datahub.nsi" 2>&1
$nsisExitCode = $LASTEXITCODE
Pop-Location

if ($nsisExitCode -eq 0) {
    # Copy installer back to dist (NSIS creates it in WinTempDir because OutFile was relative or simple name)
    $SetupCmdPath = Join-Path $WinTempDir $SetupName
    if (Test-Path $SetupCmdPath) {
        Copy-Item -Path $SetupCmdPath -Destination $DistDir -Force
        $setupSize = (Get-Item (Join-Path $DistDir $SetupName)).Length
        Complete-Progress -Status "Installer built successfully"
        Write-Success "$SetupName ($(Format-FileSize $setupSize))"
    } else {
        # Fallback check if OutFile was ignored or different behavior
        Complete-Progress -Status "Failed"
        Write-Failure "Installer output not found at expected path: $SetupCmdPath"
    }
} else {
    Complete-Progress -Status "Failed"
    Write-Failure "NSIS compilation failed"
    Write-Host $nsisOutput
}

# Cleanup temp
Remove-Item -Recurse -Force $WinTempDir -ErrorAction SilentlyContinue

# ==============================================================================
# BUILD COMPLETE
# ==============================================================================

Write-Banner "BUILD SUCCESSFUL" -Color Green

Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor DarkGray
Write-Host "  |                        OUTPUT FILES                              |" -ForegroundColor DarkGray
Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor DarkGray

$portableFile = Join-Path $DistDir $PortableName
$setupFile = Join-Path $DistDir $SetupName

if (Test-Path $portableFile) {
    $size = Format-FileSize (Get-Item $portableFile).Length
    Write-Host "  |  [EXE]   $PortableName          $($size.PadRight(12))|" -ForegroundColor White
}
if (Test-Path $setupFile) {
    $size = Format-FileSize (Get-Item $setupFile).Length
    Write-Host "  |  [SETUP] $SetupName             $($size.PadRight(12))|" -ForegroundColor White
}

Write-Host "  +-------------------------------------------------------------------+" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Output: $DistDir" -ForegroundColor Gray
Write-Host ""
