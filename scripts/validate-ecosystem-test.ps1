# Validate the dev-only training ecosystem stack from Windows.
#
#   pwsh scripts/validate-ecosystem-test.ps1
#
# This script never talks to production. It only calls 127.0.0.1 ports declared
# in deploy/ecosystem-test/.env.

param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Continue'
$envFile = Join-Path $Root 'deploy/ecosystem-test/.env'

if ($env:OCR_ENV -in @('production', 'prod')) {
    Write-Error 'REFUSING: the training stack must not run against production'
    exit 2
}
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $Root 'deploy/ecosystem-test/.env.example') $envFile
    Write-Host 'created deploy/ecosystem-test/.env from .env.example; replace the lab passwords'
}

$config = @{}
foreach ($line in Get-Content $envFile) {
    if ($line -match '^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$') {
        $config[$Matches[1]] = $Matches[2]
    }
}

function Port([string]$name, [int]$default) {
    if ($config.ContainsKey($name) -and $config[$name]) { return [int]$config[$name] }
    return $default
}

$moodlePort = Port 'MOODLE_PORT' 8091
$authentikPort = Port 'AUTHENTIK_PORT' 9000
$netboxPort = Port 'NETBOX_PORT' 8083
$ralphPort = Port 'RALPH_PORT' 8084
$fleetPort = Port 'FLEET_PORT' 8082

$script:failures = 0
$script:skips = 0
function Pass([string]$message) { Write-Host "PASS: $message" -ForegroundColor Green }
function Fail([string]$message) { Write-Host "FAIL: $message" -ForegroundColor Red; $script:failures++ }
function Skip([string]$message) { Write-Host "SKIP: $message" -ForegroundColor Yellow; $script:skips++ }

function Code([string]$url) {
    $result = & curl.exe -s -o NUL -w '%{http_code}' --max-time 10 $url 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $result) { return '000' }
    return [string]$result
}

function Expect([string]$label, [string]$url, [string[]]$expected) {
    $code = Code $url
    if ($expected -contains $code) { Pass "$label ($code)" } else { Fail "$label (expected $($expected -join '/'), got $code)" }
}

function IsRunning([string]$service, [string]$profile) {
    $services = & docker compose --profile $profile ps --services --filter status=running 2>$null
    return $services -contains $service
}

Push-Location (Join-Path $Root 'deploy/ecosystem-test')
try {
    Write-Host '== Containers =='
    & docker compose ps

    Write-Host '== Moodle =='
    Expect 'Moodle login page' "http://127.0.0.1:$moodlePort/login/index.php" @('200')
    $dbCheck = & docker compose exec -T moodle-db /opt/bitnami/mariadb/bin/mariadb-admin -h 127.0.0.1 -uroot "-p$($config['MOODLE_DB_ROOT_PASSWORD'])" ping 2>&1
    if ($LASTEXITCODE -eq 0) { Pass 'Moodle database' } else { Fail 'Moodle database' }

    Write-Host '== Authentik (sso profile) =='
    if (IsRunning 'authentik-server' 'sso') {
        Expect 'Authentik liveness' "http://127.0.0.1:$authentikPort/-/health/live/" @('204', '200')
        Expect 'Authentik readiness' "http://127.0.0.1:$authentikPort/-/health/ready/" @('204', '200')
    } else { Skip 'Authentik profile is not running' }

    Write-Host '== NetBox (assets profile) =='
    if (IsRunning 'netbox' 'assets') {
        Expect 'NetBox login' "http://127.0.0.1:$netboxPort/login/" @('200')
        Expect 'NetBox API reachable' "http://127.0.0.1:$netboxPort/api/status/" @('200', '403')
    } else { Skip 'NetBox is not running' }

    Write-Host '== Ralph (assets profile) =='
    if (IsRunning 'ralph' 'assets') {
        Expect 'Ralph responds' "http://127.0.0.1:$ralphPort/" @('200', '302')
    } else { Skip 'Ralph is not running' }

    Write-Host '== Fleet (endpoint profile) =='
    if (IsRunning 'fleet' 'endpoint') {
        Expect 'Fleet responds' "http://127.0.0.1:$fleetPort/" @('200', '302', '307')
    } else { Skip 'Fleet is not running' }

    Write-Host '== Results =='
    Write-Host "failures: $script:failures, skipped: $script:skips"
    if ($script:failures -ne 0) {
        Write-Host 'VALIDATION FAILED' -ForegroundColor Red
        exit 1
    }
    Write-Host 'VALIDATION PASSED' -ForegroundColor Green
} finally {
    Pop-Location
}
