# Windows Update Helper Script
# Performs Windows-specific preflight checks before update
# Usage: .\windows_update_helper.ps1 [-Branch main] [-Force]

param(
    [string]$Branch = $null,
    [switch]$Force = $false
)

Write-Host "Hei-DataHub Windows Update Helper" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Is app currently running?
Write-Host "[1/5] Checking for running instances..." -NoNewline
$processes = Get-Process -Name "hei-datahub*" -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host " WARN" -ForegroundColor Yellow
    Write-Host "      Found $($processes.Count) running process(es):" -ForegroundColor Yellow
    $processes | ForEach-Object {
        Write-Host "      - PID $($_.Id): $($_.Name)" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "      Action: Please close all Hei-DataHub windows before updating." -ForegroundColor Yellow
    Write-Host "              Press any key to continue anyway, or Ctrl+C to cancel..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host " OK" -ForegroundColor Green
}

# Check 2: Long paths enabled?
Write-Host "[2/5] Checking long paths support..." -NoNewline
try {
    $longPathsEnabled = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
                                         -Name "LongPathsEnabled" `
                                         -ErrorAction SilentlyContinue

    if ($longPathsEnabled -and $longPathsEnabled.LongPathsEnabled -eq 1) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " WARN" -ForegroundColor Yellow
        Write-Host "      Long paths not enabled. This may cause issues with some packages." -ForegroundColor Yellow
        Write-Host "      To enable (requires Administrator):" -ForegroundColor Yellow
        Write-Host "        New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' ``" -ForegroundColor Cyan
        Write-Host "                         -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force" -ForegroundColor Cyan
        Write-Host "      Or for Git only:" -ForegroundColor Yellow
        Write-Host "        git config --system core.longpaths true" -ForegroundColor Cyan
        Write-Host ""
    }
} catch {
    Write-Host " SKIP" -ForegroundColor Yellow
    Write-Host "      Could not check (may require Administrator privileges)" -ForegroundColor Yellow
}

# Check 3: Windows Defender exclusions
Write-Host "[3/5] Checking Windows Defender exclusions..." -NoNewline
try {
    $exclusions = Get-MpPreference -ErrorAction Stop | Select-Object -ExpandProperty ExclusionPath
    $uvToolsPath = "$env:LOCALAPPDATA\uv\tools"
    $uvToolsPathNormalized = $uvToolsPath.ToLower()

    $isExcluded = $false
    foreach ($excl in $exclusions) {
        if ($excl.ToLower().Contains($uvToolsPathNormalized) -or $uvToolsPathNormalized.Contains($excl.ToLower())) {
            $isExcluded = $true
            break
        }
    }

    if ($isExcluded) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " INFO" -ForegroundColor Yellow
        Write-Host "      UV tools directory not in Defender exclusions." -ForegroundColor Yellow
        Write-Host "      This may slow down installation or cause false positives." -ForegroundColor Yellow
        Write-Host "      To add exclusion (requires Administrator):" -ForegroundColor Yellow
        Write-Host "        Add-MpPreference -ExclusionPath '$uvToolsPath'" -ForegroundColor Cyan
        Write-Host ""
    }
} catch {
    Write-Host " SKIP" -ForegroundColor Yellow
    Write-Host "      Could not check Defender (may not be installed or enabled)" -ForegroundColor Yellow
}

# Check 4: Git configuration
Write-Host "[4/5] Checking Git configuration..." -NoNewline
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "      $gitVersion" -ForegroundColor Gray

        # Check core.longpaths in Git
        $gitLongPaths = git config --get core.longpaths 2>&1
        if ($gitLongPaths -eq "true") {
            Write-Host "      Git long paths: enabled" -ForegroundColor Green
        } else {
            Write-Host "      Git long paths: not enabled (may cause issues)" -ForegroundColor Yellow
            Write-Host "        Enable with: git config --global core.longpaths true" -ForegroundColor Cyan
        }
    } else {
        Write-Host " ERROR" -ForegroundColor Red
        Write-Host "      Git not found in PATH" -ForegroundColor Red
        Write-Host "      Install from: https://git-scm.com/download/win" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host " ERROR" -ForegroundColor Red
    Write-Host "      Could not execute git command" -ForegroundColor Red
    exit 1
}

# Check 5: UV installation
Write-Host "[5/5] Checking UV installation..." -NoNewline
try {
    $uvVersion = uv --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
        Write-Host "      $uvVersion" -ForegroundColor Gray
    } else {
        Write-Host " ERROR" -ForegroundColor Red
        Write-Host "      UV not found in PATH" -ForegroundColor Red
        Write-Host "      Install with: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host " ERROR" -ForegroundColor Red
    Write-Host "      Could not execute uv command" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Preflight checks complete!" -ForegroundColor Green
Write-Host ""

# Build command arguments
$updateArgs = @()
if ($Branch) {
    $updateArgs += "--branch"
    $updateArgs += $Branch
}
if ($Force) {
    $updateArgs += "--force"
}

# Launch Python update process
Write-Host "Launching update process..." -ForegroundColor Cyan
Write-Host ""

try {
    # Call the Python CLI update handler
    if ($updateArgs.Count -gt 0) {
        hei-datahub update $updateArgs
    } else {
        hei-datahub update
    }

    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "Update completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Update failed with exit code: $exitCode" -ForegroundColor Red
        exit $exitCode
    }
} catch {
    Write-Host ""
    Write-Host "Error launching update: $_" -ForegroundColor Red
    exit 1
}
