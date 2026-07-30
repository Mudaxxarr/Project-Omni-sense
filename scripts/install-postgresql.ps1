[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
$isAdministrator = $principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdministrator) {
    throw "This bounded installer must be run from an Administrator-elevated PowerShell process."
}

$existingService = Get-Service -Name "postgresql*16*" -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($existingService) {
    Write-Host "PostgreSQL 16 is already installed as $($existingService.Name)." -ForegroundColor Green
    exit 0
}

Write-Host "Installing native PostgreSQL 16 on local port 5432."
Write-Host "Remote access remains disabled."

& choco.exe install postgresql16 -y --no-progress --params "'/Port:5432'"
if ($LASTEXITCODE -ne 0) {
    throw "Chocolatey PostgreSQL installation failed with exit code $LASTEXITCODE."
}

$service = Get-Service -Name "postgresql*16*" -ErrorAction Stop |
    Select-Object -First 1
if ($service.Status -ne "Running") {
    Start-Service -Name $service.Name
}

$pgIsReady = "C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"
if (-not (Test-Path -LiteralPath $pgIsReady)) {
    throw "PostgreSQL installed, but pg_isready.exe was not found at the expected native path."
}

& $pgIsReady -h 127.0.0.1 -p 5432 -t 5
if ($LASTEXITCODE -ne 0) {
    throw "PostgreSQL installed, but the local readiness probe failed."
}

Write-Host "Native PostgreSQL 16 is running on 127.0.0.1:5432." -ForegroundColor Green
