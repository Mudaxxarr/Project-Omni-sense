[CmdletBinding()]
param(
    [ValidateSet("P0-SHELL-01", "P0-SCENARIO-01")]
    [string]$Feature = "P0-SHELL-01",
    [switch]$AllowMissingPostgres,
    [switch]$SkipRuntime
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$artifactDir = Join-Path $repoRoot "artifacts\verification\$Feature"
$screenshotArtifactDir = Join-Path $artifactDir "screenshots"
$manifestPath = Join-Path $artifactDir "manifest.json"
$featureContractPath = Join-Path $repoRoot "docs\engineering\features\$Feature.yml"
$playwrightRoot = Join-Path $repoRoot "output\playwright"
$playwrightScreenshotDir = if ($Feature -eq "P0-SCENARIO-01") {
    Join-Path $playwrightRoot "phase0-scenarios"
} else {
    Join-Path $playwrightRoot "phase0"
}
$playwrightResultsDir = Join-Path $playwrightRoot "phase0\test-results"
$playwrightJunitPath = Join-Path $playwrightRoot "phase0\test-results.xml"
$startedAt = [DateTimeOffset]::UtcNow
$checks = [System.Collections.Generic.List[object]]::new()

function Invoke-Gate {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "GATE: $Name" -ForegroundColor Cyan
    $gateStarted = [DateTimeOffset]::UtcNow
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Gate '$Name' failed with exit code $LASTEXITCODE."
    }
    $checks.Add([pscustomobject]@{
        name = $Name
        status = "passed"
        duration_ms = [math]::Round(([DateTimeOffset]::UtcNow - $gateStarted).TotalMilliseconds)
    })
}

Push-Location $repoRoot
try {
    Invoke-Gate "local doctor" {
        if ($AllowMissingPostgres) {
            & (Join-Path $PSScriptRoot "doctor.ps1") -AllowMissingPostgres
        } else {
            & (Join-Path $PSScriptRoot "doctor.ps1")
        }
    }
    Invoke-Gate "Python lint" { & uv.exe run ruff check services }
    Invoke-Gate "Python types" { & uv.exe run mypy }
    Invoke-Gate "Backend tests" { & uv.exe run pytest }
    Invoke-Gate "Workspace lint" { & corepack.cmd pnpm lint }
    Invoke-Gate "Workspace types" { & corepack.cmd pnpm typecheck }
    Invoke-Gate "Workspace tests" { & corepack.cmd pnpm test }
    Invoke-Gate "Production build" { & corepack.cmd pnpm build }

    if (-not $SkipRuntime) {
        Invoke-Gate "Runtime HTTP proof" {
            & (Join-Path $PSScriptRoot "start-local.ps1") -SkipDependencyCheck
            $api = Invoke-WebRequest -Uri "http://127.0.0.1:8765/v1/health" -UseBasicParsing -TimeoutSec 5
            $ui = Invoke-WebRequest -Uri "http://127.0.0.1:4173" -UseBasicParsing -TimeoutSec 5
            if ($api.StatusCode -ne 200 -or $api.Content -notmatch "omniscience-core") {
                throw "Core API HTTP proof failed."
            }
            if ($ui.StatusCode -ne 200 -or $ui.Content -notmatch "OMNISCIENCE Command Centre") {
                throw "Command centre HTTP proof failed."
            }
            if ($Feature -eq "P0-SCENARIO-01") {
                $scenarioApi = Invoke-WebRequest `
                    -Uri "http://127.0.0.1:8765/v1/scenarios/valid" `
                    -UseBasicParsing -TimeoutSec 5
                if (
                    $scenarioApi.StatusCode -ne 200 -or
                    $scenarioApi.Content -notmatch '"contract_version":"scenario.v1"' -or
                    $scenarioApi.Content -notmatch '"entity_family_count":12'
                ) {
                    throw "Scenario API HTTP proof failed."
                }
            }
        }
        Invoke-Gate "Browser state and interaction proof" {
            & corepack.cmd pnpm --filter "@omniscience/desktop" test:e2e
        }
    }

    $sourceCommit = $null
    $previousErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $gitCommit = (
            & git.exe -c "safe.directory=$repoRoot" rev-parse --verify HEAD `
                2>$null | Out-String
        ).Trim()
        $gitCommitExitCode = $LASTEXITCODE
        $worktreeStatus = (
            & git.exe -c "safe.directory=$repoRoot" status --porcelain `
                2>$null | Out-String
        ).Trim()
        $gitStatusExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($gitCommitExitCode -eq 0 -and $gitCommit) {
        $sourceCommit = $gitCommit
    }
    if ($gitStatusExitCode -ne 0) {
        throw "Unable to read the local Git worktree status."
    }
    $featureContractHash = (
        Get-FileHash -LiteralPath $featureContractPath -Algorithm SHA256
    ).Hash.ToLowerInvariant()

    New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
    New-Item -ItemType Directory -Force -Path $screenshotArtifactDir | Out-Null

    $states = if ($Feature -eq "P0-SCENARIO-01") {
        @(
            "valid",
            "stale",
            "duplicate",
            "contradictory",
            "denied",
            "degraded",
            "timeout",
            "recovery"
        )
    } else {
        @("live", "degraded", "stale", "loading", "error")
    }
    $viewports = @("1280x720", "1440x900", "1920x1080")
    $screenshotNames = [System.Collections.Generic.List[string]]::new()
    foreach ($state in $states) {
        foreach ($viewport in $viewports) {
            $screenshotNames.Add("$state-$viewport.png")
        }
    }
    if ($Feature -eq "P0-SHELL-01") {
        $screenshotNames.Add("source-setup-1440x900.png")
    }

    if (-not $SkipRuntime) {
        foreach ($screenshotName in $screenshotNames) {
            $sourceScreenshot = Join-Path $playwrightScreenshotDir $screenshotName
            if (-not (Test-Path -LiteralPath $sourceScreenshot)) {
                throw "Expected screenshot is missing: $sourceScreenshot"
            }
            Copy-Item -LiteralPath $sourceScreenshot -Destination $screenshotArtifactDir -Force
        }

        if (-not (Test-Path -LiteralPath $playwrightJunitPath)) {
            throw "Playwright JUnit result is missing: $playwrightJunitPath"
        }
        Copy-Item -LiteralPath $playwrightJunitPath `
            -Destination (Join-Path $artifactDir "test-results.xml") -Force

        $traceRelativePath = if ($Feature -eq "P0-SCENARIO-01") {
            "phase0-scenarios-valid-fixture-is-safe-at-1440x900\trace.zip"
        } else {
            "phase0-shell-live-state-is-safe-at-1440x900\trace.zip"
        }
        $traceSource = Join-Path $playwrightResultsDir $traceRelativePath
        if (-not (Test-Path -LiteralPath $traceSource)) {
            throw "Critical-journey trace is missing: $traceSource"
        }
        Copy-Item -LiteralPath $traceSource `
            -Destination (Join-Path $artifactDir "trace.zip") -Force

        $apiEndpoint = if ($Feature -eq "P0-SCENARIO-01") {
            "http://127.0.0.1:8765/v1/scenarios/valid"
        } else {
            "http://127.0.0.1:8765/v1/health"
        }
        $apiResponse = Invoke-RestMethod -Uri $apiEndpoint -TimeoutSec 5
        $apiResponse | ConvertTo-Json -Depth 8 |
            Set-Content -LiteralPath (Join-Path $artifactDir "api-contract.json") `
                -Encoding utf8

        [pscustomobject]@{
            schema = "omniscience.audit-proof.v1"
            feature = $Feature
            events = @()
            reason = if ($Feature -eq "P0-SCENARIO-01") {
                "The fixture lab is read-only and cannot emit a business audit event."
            } else {
                "Phase 0 is an observation-only shell and emits no business audit event."
            }
        } | ConvertTo-Json -Depth 5 |
            Set-Content -LiteralPath (Join-Path $artifactDir "audit-events.json") `
                -Encoding utf8

        $browserCaseCount = $states.Count * $viewports.Count
        @(
            "Playwright assertions passed across $browserCaseCount state/viewport cases."
            "Console errors: 0"
            "Page errors: 0"
            "Failed requests and HTTP responses >= 400: 0"
            "Horizontal overflow cases: 0"
            if ($Feature -eq "P0-SCENARIO-01") {
                "Vertical overflow cases: 0"
                "Scenario switch interaction: passed"
            }
        ) | Set-Content -LiteralPath (Join-Path $artifactDir "console.log") `
            -Encoding utf8

        $visualSummary = if ($Feature -eq "P0-SCENARIO-01") {
            "Automated proof passed for all eight fixture states at 1280x720, 1440x900, and 1920x1080."
        } else {
            "Automated proof passed for all five states at 1280x720, 1440x900, and 1920x1080."
        }
        @(
            "# $Feature Visual Review"
            ""
            "Status: pending final human-style screenshot inspection"
            ""
            $visualSummary
            "Review the copied screenshots before changing the manifest status to verified."
        ) | Set-Content -LiteralPath (Join-Path $artifactDir "visual-review.md") `
            -Encoding utf8
    }

    $relativeScreenshots = @(
        $screenshotNames | ForEach-Object { "screenshots/$_" }
    )
    $apiChecks = @()
    if (-not $SkipRuntime) {
        if ($Feature -eq "P0-SCENARIO-01") {
            $apiChecks = @(
                [pscustomobject]@{
                    endpoint = "GET /v1/scenarios/valid"
                    http_status = 200
                    contract_version = $apiResponse.contract_version
                    fixture_version = $apiResponse.fixture_version
                    entity_family_count = $apiResponse.summary.entity_family_count
                    record_count = $apiResponse.summary.record_count
                    stored_at_utc = $apiResponse.clock.stored_at_utc
                    displayed_at_local = $apiResponse.clock.displayed_at_local
                    consequential_actions_enabled = `
                        $apiResponse.consequential_actions_enabled
                }
            )
        } else {
            $apiChecks = @(
                [pscustomobject]@{
                    endpoint = "GET /v1/health"
                    http_status = 200
                    service = $apiResponse.service
                    contract_version = $apiResponse.contract_version
                    runtime_status = $apiResponse.status
                    postgresql_status = $apiResponse.prerequisites.postgresql.status
                    data_connection_status = $apiResponse.data_connection.status
                }
            )
        }
    }

    [pscustomobject]@{
        schema = "omniscience.verification.v1"
        feature_id = $Feature
        source_commit = $sourceCommit
        source_worktree_dirty = [bool]$worktreeStatus
        feature_contract_sha256 = $featureContractHash
        status = "automated_gates_passed"
        visual_review_status = if ($SkipRuntime) {
            "not_run"
        } else {
            "pending_final_inspection"
        }
        started_at = $startedAt.ToString("o")
        completed_at = [DateTimeOffset]::UtcNow.ToString("o")
        commands = $checks
        database_migration_version = "none_phase0"
        fixtures = if ($Feature -eq "P0-SCENARIO-01") {
            @("phase0-fixtures.v1", "scenario.v1")
        } else {
            @("health.v1", "phase0-route-state-laboratory.v1")
        }
        roles = @("owner")
        states = if ($SkipRuntime) { @() } else { $states }
        viewports = if ($SkipRuntime) { @() } else { $viewports }
        screenshots = if ($SkipRuntime) { @() } else { $relativeScreenshots }
        api_checks = $apiChecks
        known_limitations = @(
            "No operational accounting or POS source is connected."
            "Evidence vault, audit chain, retention worker, and restore proof begin in Phase 1."
            "Owner visual North Star approval is still required for the Phase 0 exit tag."
        )
        verifier = [pscustomobject]@{
            identity = "Codex Founder Mode"
            browser_tool = "Playwright 1.62.0"
        }
    } | ConvertTo-Json -Depth 8 |
        Set-Content -LiteralPath $manifestPath -Encoding utf8

    Write-Host ""
    Write-Host "Automated gates passed for $Feature." -ForegroundColor Green
    Write-Host "Manifest: $manifestPath"
} catch {
    if (-not $SkipRuntime) {
        & (Join-Path $PSScriptRoot "stop-local.ps1") -Quiet
    }
    throw
} finally {
    Pop-Location
}
