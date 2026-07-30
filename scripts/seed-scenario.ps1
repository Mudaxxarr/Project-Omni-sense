[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("live", "degraded", "stale", "loading")]
    [string]$Scenario
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$scenarioFile = Join-Path $runtimeDir "scenario.json"

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

$query = if ($Scenario -eq "live") { "" } else { "?state=$Scenario" }
$scenarioRecord = [pscustomobject]@{
    schema = "omniscience.scenario.v1"
    scenario = $Scenario
    url = "http://127.0.0.1:4173/$query"
    seeded_at = [DateTimeOffset]::UtcNow.ToString("o")
}
$scenarioRecord | ConvertTo-Json | Set-Content -LiteralPath $scenarioFile -Encoding utf8

Write-Host "Scenario '$Scenario' is available at:" -ForegroundColor Green
Write-Host $scenarioRecord.url
Write-Host "Record: $scenarioFile"
