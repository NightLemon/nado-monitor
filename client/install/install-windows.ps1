# Install Nado Telemetry Client as a Windows Scheduled Task
# Run as Administrator

#Requires -RunAsAdministrator

param(
    [string]$PythonPath = "python",
    [string]$ClientDir = (Split-Path -Parent $PSScriptRoot),
    [string]$ConfigPath = ""
)

# Validate python exists
try {
    & $PythonPath --version | Out-Null
} catch {
    Write-Error "Python not found at '$PythonPath'. Specify -PythonPath."
    exit 1
}

# Install the package
Write-Host "Installing nado-telemetry package..."
& $PythonPath -m pip install $ClientDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install nado-telemetry package."
    exit 1
}

# Find the nado-telemetry entry point
$nadoCmd = & $PythonPath -c "import shutil; print(shutil.which('nado-telemetry') or '')" 2>$null
if (-not $nadoCmd) {
    # Fallback: use python -m
    $nadoCmd = $PythonPath
    $arguments = "-m nado_telemetry.cli"
} else {
    $arguments = ""
}

if ($ConfigPath) {
    $arguments += " -c `"$ConfigPath`""
}

$taskName = "NadoTelemetryClient"

# Remove existing task if present
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing scheduled task."
}

$action = New-ScheduledTaskAction `
    -Execute $nadoCmd `
    -Argument $arguments `
    -WorkingDirectory $ClientDir

$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Nado Monitor Telemetry Client"

Write-Host ""
Write-Host "Scheduled task '$taskName' created successfully."
Write-Host "To start now: Start-ScheduledTask -TaskName '$taskName'"
Write-Host "To remove:    Unregister-ScheduledTask -TaskName '$taskName'"
