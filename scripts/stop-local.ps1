[CmdletBinding()]
param(
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$processFile = Join-Path $runtimeDir "processes.json"

if (-not (Test-Path -LiteralPath $processFile)) {
    if (-not $Quiet) {
        Write-Host "No OMNISCIENCE runtime record exists."
    }
    exit 0
}

$runtime = Get-Content -LiteralPath $processFile -Raw | ConvertFrom-Json
if ($runtime.schema -ne "omniscience.runtime.v1" -or $runtime.repository -ne $repoRoot) {
    throw "Runtime record identity does not match this repository. No process was stopped."
}

foreach ($record in $runtime.processes) {
    $process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if (-not $process) {
        continue
    }

    $actualStartedAt = $process.StartTime.ToUniversalTime()
    $recordedStartedAt = [DateTime]::Parse($record.started_at).ToUniversalTime()
    $drift = [math]::Abs(($actualStartedAt - $recordedStartedAt).TotalSeconds)
    if ($process.ProcessName -ne $record.process_name -or $drift -gt 3) {
        throw "PID $($record.pid) no longer matches its recorded process identity. No process was stopped."
    }

    Stop-Process -Id $record.pid -Force
    if (-not $Quiet) {
        Write-Host "Stopped $($record.role) process $($record.pid)."
    }
}

Remove-Item -LiteralPath $processFile -Force

if (-not $Quiet) {
    Write-Host "OMNISCIENCE local runtime stopped." -ForegroundColor Green
}
