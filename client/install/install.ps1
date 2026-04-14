# Nado Monitor — Telemetry Client Installer (Windows)
#
# One-line install (PowerShell as Administrator):
#   irm https://raw.githubusercontent.com/NightLemon/nado-monitor/main/client/install/install.ps1 | iex
#
# Or with parameters:
#   .\install.ps1 -ApiKey "YOUR_KEY" [-ServerUrl "https://..."] [-Upgrade] [-Uninstall]
#
#Requires -RunAsAdministrator

param(
    [string]$ApiKey = $env:NADO_API_KEY,
    [string]$ServerUrl = "https://nado-monitor.azurewebsites.net",
    [string]$PythonPath = "python",
    [switch]$Upgrade,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$TaskName = "NadoTelemetryClient"
$InstallDir = "$env:ProgramData\nado-monitor"
$RepoUrl = "https://github.com/NightLemon/nado-monitor.git"
$PipSpec = "nado-telemetry @ git+$RepoUrl#subdirectory=client"

# ── Uninstall ─────────────────────────────────────────────────────────────────
if ($Uninstall) {
    Write-Host "==> Uninstalling nado-telemetry..."
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "  Removed scheduled task."
    }
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
        Write-Host "  Removed $InstallDir."
    }
    Write-Host "==> Done."
    exit 0
}

# ── Validate ──────────────────────────────────────────────────────────────────
if (-not $ApiKey) {
    $ApiKey = Read-Host "Enter API key"
    if (-not $ApiKey) {
        Write-Error "API key is required. Use -ApiKey or set NADO_API_KEY env var."
        exit 1
    }
}

try {
    $pyVer = & $PythonPath --version 2>&1
    Write-Host "  Using $pyVer"
} catch {
    Write-Error "Python not found at '$PythonPath'. Install Python or specify -PythonPath."
    exit 1
}

# ── Install ───────────────────────────────────────────────────────────────────
Write-Host "==> Installing nado-telemetry client..."

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Create venv
$VenvDir = "$InstallDir\venv"
if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
    Write-Host "  Creating Python venv..."
    & $PythonPath -m venv $VenvDir
}
$VenvPip = "$VenvDir\Scripts\pip.exe"
$VenvPython = "$VenvDir\Scripts\python.exe"

& $VenvPip install --upgrade pip -q 2>$null

if ($Upgrade) {
    Write-Host "  Upgrading package..."
    & $VenvPip install --upgrade $PipSpec -q
} else {
    Write-Host "  Installing package..."
    & $VenvPip install $PipSpec -q
}

# Find nado-telemetry executable
$NadoExe = "$VenvDir\Scripts\nado-telemetry.exe"
if (-not (Test-Path $NadoExe)) {
    Write-Error "nado-telemetry.exe not found after install."
    exit 1
}
Write-Host "  Installed successfully."

# ── Set environment variables (machine-level) ────────────────────────────────
Write-Host "==> Configuring environment..."
[System.Environment]::SetEnvironmentVariable("NADO_SERVER_URL", $ServerUrl, "Machine")
[System.Environment]::SetEnvironmentVariable("NADO_API_KEY", $ApiKey, "Machine")
# Also set in current process for immediate task start
$env:NADO_SERVER_URL = $ServerUrl
$env:NADO_API_KEY = $ApiKey

# ── Scheduled Task ────────────────────────────────────────────────────────────
Write-Host "==> Creating scheduled task..."

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "  Replaced existing task."
}

$action = New-ScheduledTaskAction `
    -Execute $NadoExe `
    -WorkingDirectory $InstallDir

$trigger = New-ScheduledTaskTrigger -AtStartup

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Nado Monitor Telemetry Client" | Out-Null

Start-ScheduledTask -TaskName $TaskName

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==> Done! Client is running."
Write-Host ""
Write-Host "Commands:"
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'           # check status"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'         # start"
Write-Host "  Stop-ScheduledTask -TaskName '$TaskName'          # stop"
Write-Host "  .\install.ps1 -ApiKey KEY -Upgrade                # upgrade"
Write-Host "  .\install.ps1 -Uninstall                          # remove"
