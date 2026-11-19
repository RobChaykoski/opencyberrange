# Seed the dev-only training ecosystem with fake data from Windows.
#
#   pwsh scripts/ecosystem_seed/seed_all.ps1
#
# Every record created here is synthetic. Never point this at production.

param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
)

$ErrorActionPreference = 'Stop'
if ($env:OCR_ENV -in @('production', 'prod')) {
    Write-Error 'REFUSING: the training stack must not run against production'
    exit 2
}

Push-Location (Join-Path $Root 'deploy/ecosystem-test')
try {
    $config = @{}
    foreach ($line in Get-Content '.env') {
        if ($line -match '^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$') { $config[$Matches[1]] = $Matches[2] }
    }
    $trainingPassword = if ($env:TRAINING_PASSWORD) { $env:TRAINING_PASSWORD } else { 'TrainLab!2026#Student' }

    Write-Host '== Moodle =='
    & docker compose exec -T -e "TRAINING_PASSWORD=$trainingPassword" moodle php /seed/seed_moodle.php
    if ($LASTEXITCODE -ne 0) { throw 'Moodle seed failed' }

    $assetsRunning = (& docker compose --profile assets ps --services --filter status=running 2>$null)
    if ($assetsRunning -contains 'netbox') {
        Write-Host '== NetBox =='
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $tokenOutput = & docker compose exec -T netbox /opt/netbox/netbox/manage.py shell --no-imports `
            -c "from users.models import Token, User; u=User.objects.get(username='admin'); t=Token.objects.create(version=1, user=u); print('TOKEN='+t.token)" 2>&1
        $ErrorActionPreference = $previousPreference
        $token = ($tokenOutput | Select-String -Pattern '^TOKEN=(.+)$' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Last 1)
        $netboxPort = if ($config['NETBOX_PORT']) { $config['NETBOX_PORT'] } else { '8083' }
        $netboxHost = if ($config['NETBOX_BIND']) { $config['NETBOX_BIND'] } else { '127.0.0.1' }
        if ($token) {
            $env:NETBOX_URL = "http://${netboxHost}:$netboxPort"
            $env:NETBOX_TOKEN = $token
            $python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }
            & $python (Join-Path $Root 'scripts/ecosystem_seed/seed_netbox.py')
        } else {
            Write-Host 'could not create a NetBox API token; create one in the NetBox UI and run:'
            Write-Host "  `$env:NETBOX_TOKEN='<token>'; python scripts/ecosystem_seed/seed_netbox.py"
        }
    } else {
        Write-Host 'SKIP: NetBox is not running'
    }

    foreach ($entry in @(
        @('assets', 'ralph', 'RALPH_PORT', 'Ralph'),
        @('endpoint', 'fleet', 'FLEET_PORT', 'Fleet'),
        @('sso', 'authentik-server', 'AUTHENTIK_PORT', 'Authentik')
    )) {
        $running = (& docker compose --profile $entry[0] ps --services --filter status=running 2>$null)
        if ($running -contains $entry[1]) {
            $port = if ($config[$entry[2]]) { $config[$entry[2]] } else { '0000' }
            Write-Host "$($entry[3]) is running at http://127.0.0.1:$port/ - use fake users and fake assets only."
        } else {
            Write-Host "SKIP: $($entry[3]) is not running"
        }
    }

    $ssoRunning = (& docker compose --profile sso ps --services --filter status=running 2>$null)
    if ($ssoRunning -contains 'authentik-server') {
        Write-Host '== Authentik seed =='
        & docker compose exec -T -e "TRAINING_PASSWORD=$trainingPassword" authentik-server ak shell -c "exec(open('/seed/seed_authentik.py').read())"
    }

    $assetsRunning = (& docker compose --profile assets ps --services --filter status=running 2>$null)
    if ($assetsRunning -contains 'ralph') {
        Write-Host '== Ralph admin =='
        & docker compose exec -T -w /opt/ralph/ralph-core ralph /opt/ralph/ralph-core/bin/ralph migrate --noinput
        & docker compose exec -T -w /opt/ralph/ralph-core `
            -e "RALPH_ADMIN_USER=$($config['RALPH_ADMIN_USER'])" `
            -e "RALPH_ADMIN_EMAIL=$($config['RALPH_ADMIN_EMAIL'])" `
            -e "RALPH_ADMIN_PASSWORD=$trainingPassword" `
            ralph /opt/ralph/ralph-core/bin/python /seed/seed_ralph.py
    }

    $endpointRunning = (& docker compose --profile endpoint ps --services --filter status=running 2>$null)
    if ($endpointRunning -contains 'fleet') {
        Write-Host '== Fleet admin =='
        $fleetPort = if ($config['FLEET_PORT']) { $config['FLEET_PORT'] } else { '8082' }
        $fleetHost = if ($config['FLEET_BIND']) { $config['FLEET_BIND'] } else { '127.0.0.1' }
        $env:FLEET_URL = "http://${fleetHost}:$fleetPort"
        $env:FLEET_ADMIN_EMAIL = if ($config['FLEET_ADMIN_EMAIL']) { $config['FLEET_ADMIN_EMAIL'] } else { 'admin@example.invalid' }
        $env:FLEET_ADMIN_NAME = if ($config['FLEET_ADMIN_NAME']) { $config['FLEET_ADMIN_NAME'] } else { 'Training Admin' }
        $env:FLEET_ADMIN_PASSWORD = $trainingPassword
        $python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }
        & $python (Join-Path $Root 'scripts/ecosystem_seed/seed_fleet.py')
    }

    Write-Host 'Seeding complete.'
} finally {
    Pop-Location
}
