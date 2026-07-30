[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "valid",
        "stale",
        "duplicate",
        "contradictory",
        "denied",
        "degraded",
        "timeout",
        "recovery"
    )]
    [string]$Scenario
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$scenarioFile = Join-Path $runtimeDir "scenario.json"
$catalogPath = Join-Path $repoRoot `
    "services\core\fixtures\scenario-catalog.v1.json"

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

$catalog = Get-Content -LiteralPath $catalogPath -Raw | ConvertFrom-Json
$knownScenarios = @($catalog.scenarios | ForEach-Object { $_.id })
if ($Scenario -notin $knownScenarios) {
    throw "Scenario '$Scenario' is not present in the fixture catalog."
}

$scenarioRecord = [pscustomobject]@{
    schema = "omniscience.scenario.v1"
    scenario = $Scenario
    fixture_version = $catalog.fixture_version
    url = "http://127.0.0.1:4173/?scenario=$Scenario"
    seeded_at_utc = $catalog.anchor_utc
    deterministic = $true
}
$scenarioRecord | ConvertTo-Json |
    Set-Content -LiteralPath $scenarioFile -Encoding utf8

Write-Host "Scenario '$Scenario' is available at:" -ForegroundColor Green
Write-Host $scenarioRecord.url
Write-Host "Record: $scenarioFile"
