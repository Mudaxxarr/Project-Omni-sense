[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$AllowMissingPostgres
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Name,
        [ValidateSet("ready", "warning", "missing")]
        [string]$Status,
        [string]$Detail,
        [bool]$Required = $true
    )

    $results.Add([pscustomobject]@{
        name = $Name
        status = $Status
        detail = $Detail
        required = $Required
    })
}

function Get-CommandVersion {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    $resolved = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $resolved) {
        return $null
    }

    $output = & $resolved.Source @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        return $null
    }
    return (($output | Out-String).Trim())
}

$nodeVersion = Get-CommandVersion -Command "node.exe" -Arguments @("--version")
if ($nodeVersion -and ([version]($nodeVersion.TrimStart("v"))).Major -ge 22) {
    Add-Check "Node.js" "ready" $nodeVersion
} else {
    Add-Check "Node.js" "missing" "Node.js 22 or newer is required."
}

$pnpmVersion = Get-CommandVersion -Command "corepack.cmd" -Arguments @("pnpm", "--version")
if ($pnpmVersion) {
    Add-Check "pnpm" "ready" $pnpmVersion
} else {
    Add-Check "pnpm" "missing" "Corepack could not resolve the pinned pnpm version."
}

$uvVersion = Get-CommandVersion -Command "uv.exe" -Arguments @("--version")
if ($uvVersion) {
    Add-Check "uv" "ready" $uvVersion
} else {
    Add-Check "uv" "missing" "uv is required to provision the pinned Python runtime."
}

$pythonVersion = $null
if ($uvVersion) {
    Push-Location $repoRoot
    try {
        $pythonVersion = Get-CommandVersion -Command "uv.exe" -Arguments @("run", "python", "--version")
    } finally {
        Pop-Location
    }
}
if ($pythonVersion -and $pythonVersion -match "Python 3\.12\.") {
    Add-Check "Python" "ready" $pythonVersion
} else {
    Add-Check "Python" "missing" "The project requires its pinned Python 3.12 runtime."
}

$pgRoot = "C:\Program Files\PostgreSQL\16"
$pgIsReady = Get-Command "pg_isready.exe" -ErrorAction SilentlyContinue
if (-not $pgIsReady) {
    $bundledPgIsReady = Join-Path $pgRoot "bin\pg_isready.exe"
    if (Test-Path -LiteralPath $bundledPgIsReady) {
        $pgIsReady = [pscustomobject]@{ Source = $bundledPgIsReady }
    }
}
$pgService = Get-Service -Name "postgresql*16*" -ErrorAction SilentlyContinue |
    Select-Object -First 1

if ($pgService -and $pgService.Status -eq "Running" -and $pgIsReady) {
    $pgProbe = & $pgIsReady.Source -h 127.0.0.1 -p 5432 -t 2 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Check "PostgreSQL 16" "ready" (($pgProbe | Out-String).Trim())
    } else {
        Add-Check "PostgreSQL 16" "missing" "The service exists but did not accept the local readiness probe."
    }
} elseif ($AllowMissingPostgres) {
    Add-Check "PostgreSQL 16" "warning" "Not installed. Runtime verification is limited to the degraded Phase 0 state." $false
} else {
    Add-Check "PostgreSQL 16" "missing" "Native PostgreSQL 16 is required for the Phase 0 exit gate."
}

$systemDrive = Get-PSDrive -Name ([System.IO.Path]::GetPathRoot($repoRoot).TrimEnd("\").TrimEnd(":"))
$freeGb = [math]::Round($systemDrive.Free / 1GB, 1)
if ($freeGb -ge 10) {
    Add-Check "Free disk" "ready" "$freeGb GB available"
} else {
    Add-Check "Free disk" "missing" "$freeGb GB available; at least 10 GB is required."
}

$computer = Get-CimInstance Win32_ComputerSystem -ErrorAction SilentlyContinue
if ($computer) {
    $memoryGb = [math]::Round($computer.TotalPhysicalMemory / 1GB, 1)
    if ($memoryGb -ge 8) {
        Add-Check "Memory" "ready" "$memoryGb GB installed"
    } else {
        Add-Check "Memory" "warning" "$memoryGb GB installed; 8 GB or more is recommended." $false
    }
}

$failed = @($results | Where-Object { $_.required -and $_.status -ne "ready" })

if ($Json) {
    [pscustomobject]@{
        schema = "omniscience.doctor.v1"
        ready = $failed.Count -eq 0
        checked_at = [DateTimeOffset]::UtcNow.ToString("o")
        checks = $results
    } | ConvertTo-Json -Depth 5
} else {
    Write-Host ""
    Write-Host "OMNISCIENCE local doctor" -ForegroundColor Cyan
    Write-Host "Repository: $repoRoot"
    Write-Host ""
    foreach ($check in $results) {
        $color = switch ($check.status) {
            "ready" { "Green" }
            "warning" { "Yellow" }
            default { "Red" }
        }
        Write-Host ("[{0}] {1}: {2}" -f $check.status.ToUpper(), $check.name, $check.detail) -ForegroundColor $color
    }
}

if ($failed.Count -gt 0) {
    exit 1
}
