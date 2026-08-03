[CmdletBinding()]
param(
    [switch]$AllowMissingPostgres
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$ciArtifactRoot = "output\ci-verification"
$ciPlaywrightRoot = "$ciArtifactRoot\playwright"
$featureVerifier = Join-Path $PSScriptRoot "verify-feature.ps1"
$stopLocal = Join-Path $PSScriptRoot "stop-local.ps1"
$features = @("P0-SHELL-01", "P0-SCENARIO-01")

Push-Location $repoRoot
try {
    foreach ($feature in $features) {
        Write-Host ""
        Write-Host "CI PARITY: $feature" -ForegroundColor Cyan

        if ($AllowMissingPostgres) {
            & $featureVerifier `
                -Feature $feature `
                -ArtifactRoot $ciArtifactRoot `
                -PlaywrightRoot $ciPlaywrightRoot `
                -AllowMissingPostgres
        } else {
            & $featureVerifier `
                -Feature $feature `
                -ArtifactRoot $ciArtifactRoot `
                -PlaywrightRoot $ciPlaywrightRoot
        }

        if ($LASTEXITCODE -ne 0) {
            throw "CI parity failed for $feature with exit code $LASTEXITCODE."
        }

        & uv.exe run python -m services.core.app.ci_contract `
            --artifact-root $ciArtifactRoot `
            --feature $feature
        if ($LASTEXITCODE -ne 0) {
            throw "CI parity evidence validation failed for $feature with exit code $LASTEXITCODE."
        }
    }

    Write-Host ""
    Write-Host "Phase 0 CI parity passed for all verified features." -ForegroundColor Green
    Write-Host "Evidence: $(Join-Path $repoRoot $ciArtifactRoot)"
} finally {
    & $stopLocal -Quiet
    Pop-Location
}
