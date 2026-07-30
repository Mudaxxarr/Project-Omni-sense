[CmdletBinding()]
param(
    [switch]$SkipDependencyCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $repoRoot ".runtime"
$processFile = Join-Path $runtimeDir "processes.json"
$backendLog = Join-Path $runtimeDir "backend.log"
$backendErrorLog = Join-Path $runtimeDir "backend.error.log"
$frontendLog = Join-Path $runtimeDir "frontend.log"
$frontendErrorLog = Join-Path $runtimeDir "frontend.error.log"

if (-not $SkipDependencyCheck) {
    & (Join-Path $PSScriptRoot "doctor.ps1") -AllowMissingPostgres
    if ($LASTEXITCODE -ne 0) {
        throw "Local prerequisites failed. Run scripts/doctor.ps1 for details."
    }
}

if (Test-Path -LiteralPath $processFile) {
    throw "A runtime record already exists. Run scripts/stop-local.ps1 before starting another stack."
}

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

$managedPython = (& uv.exe python find --system 3.12 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $managedPython)) {
    throw "uv could not resolve the managed Python 3.12 executable."
}
$desktopRoot = Join-Path $repoRoot "apps\desktop"
$viteEntry = Join-Path $desktopRoot "node_modules\vite\bin\vite.js"
if (-not (Test-Path -LiteralPath $viteEntry)) {
    throw "The Vite runtime is missing. Run corepack pnpm install."
}
$nodeExecutable = (Get-Command "node.exe" -ErrorAction Stop).Source
$quotedViteEntry = '"{0}"' -f $viteEntry

$previousPythonPath = $env:PYTHONPATH
$projectPythonPath = @(
    (Join-Path $repoRoot ".venv\Lib\site-packages"),
    $repoRoot
) -join [System.IO.Path]::PathSeparator
$env:PYTHONPATH = $projectPythonPath

try {
    $backend = Start-Process `
        -FilePath $managedPython `
        -ArgumentList @(
            "-m", "uvicorn", "services.core.app.main:app",
            "--host", "127.0.0.1", "--port", "8765"
        ) `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $backendLog `
        -RedirectStandardError $backendErrorLog `
        -PassThru
} finally {
    $env:PYTHONPATH = $previousPythonPath
}

$frontend = Start-Process `
    -FilePath $nodeExecutable `
    -ArgumentList @(
        $quotedViteEntry, "--host", "127.0.0.1", "--port", "4173"
    ) `
    -WorkingDirectory $desktopRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErrorLog `
    -PassThru

$runtime = [pscustomobject]@{
    schema = "omniscience.runtime.v1"
    repository = $repoRoot
    started_at = [DateTimeOffset]::UtcNow.ToString("o")
    processes = @(
        [pscustomobject]@{
            role = "backend"
            pid = $backend.Id
            process_name = $backend.ProcessName
            started_at = $backend.StartTime.ToUniversalTime().ToString("o")
        },
        [pscustomobject]@{
            role = "frontend"
            pid = $frontend.Id
            process_name = $frontend.ProcessName
            started_at = $frontend.StartTime.ToUniversalTime().ToString("o")
        }
    )
}
$runtime | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $processFile -Encoding utf8

function Wait-ForEndpoint {
    param(
        [string]$Uri,
        [string]$ExpectedText,
        [int]$Attempts = 45
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200 -and $response.Content -match [regex]::Escape($ExpectedText)) {
                return
            }
        } catch {
            # The bounded retry below handles both connection and content readiness.
        }
        Start-Sleep -Seconds 1
    }
    throw "Timed out waiting for $Uri to contain '$ExpectedText'."
}

try {
    Wait-ForEndpoint -Uri "http://127.0.0.1:8765/v1/health" -ExpectedText "omniscience-core"
    Wait-ForEndpoint -Uri "http://127.0.0.1:4173" -ExpectedText "OMNISCIENCE"
} catch {
    Write-Host "Startup failed. Recent backend error output:" -ForegroundColor Red
    if (Test-Path -LiteralPath $backendErrorLog) {
        Get-Content -LiteralPath $backendErrorLog -Tail 30
    }
    Write-Host "Recent frontend error output:" -ForegroundColor Red
    if (Test-Path -LiteralPath $frontendErrorLog) {
        Get-Content -LiteralPath $frontendErrorLog -Tail 30
    }
    & (Join-Path $PSScriptRoot "stop-local.ps1") -Quiet
    throw
}

Write-Host ""
Write-Host "OMNISCIENCE is ready." -ForegroundColor Green
Write-Host "Command centre: http://127.0.0.1:4173"
Write-Host "Core health:    http://127.0.0.1:8765/v1/health"
Write-Host "Runtime record: $processFile"
