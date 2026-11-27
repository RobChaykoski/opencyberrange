#Requires -Version 5.1
<#
.SYNOPSIS
Run the blackbox Karate security and privacy suite against a Docker deployment.

.DESCRIPTION
Creates disposable identities inside the backend container, writes a runtime
fixture, opens an SSH tunnel to the private backend, runs Karate, then deletes
the identities and the fixture. The fixture file is created by the test run and
is removed afterwards unless -KeepFixture is supplied.

.PARAMETER BaseUrl
Local tunnel URL. Default http://127.0.0.1:18000.

.PARAMETER SshHost
SSH host that runs the Docker deployment. Required: set OCR_TEST_SSH_HOST
or pass -SshHost.

.PARAMETER BackendContainer
Backend container name. Default ocr-backend.

.PARAMETER Port
Local tunnel port. Default 18000.

.PARAMETER Tags
Optional Karate tag expression, for example "@security".

.PARAMETER KeepFixture
Keep target/security-fixture.json after the run for debugging.
#>
param(
    [string]$BaseUrl = "http://127.0.0.1:18000",
    [string]$SshHost = $env:OCR_TEST_SSH_HOST,
    [string]$BackendContainer = "ocr-backend",
    [int]$Port = 18000,
    [string]$Tags = "",
    [switch]$KeepFixture
)

$ErrorActionPreference = "Stop"
if (-not $SshHost) {
    throw "Set OCR_TEST_SSH_HOST (or pass -SshHost) to the Docker host that runs the deployment."
}
$KarateDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $KarateDir "..\..")
$ToolsDir = Join-Path $KarateDir ".tools"
$TargetDir = Join-Path $KarateDir "target"
$FixturePath = Join-Path $TargetDir "security-fixture.json"
$ReportsDir = Join-Path $TargetDir "reports"
$Jar = Join-Path $ToolsDir "karate-1.5.1.jar"
$JarUrl = "https://github.com/karatelabs/karate/releases/download/v1.5.1/karate-1.5.1.jar"
$JarSha256 = "0E4EEB77D7B17534AF6AEA9C025753DCDE7DED3785F8C3682D3C783A63867311"
$Tunnel = $null
$Fixture = $null

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Port([int]$PortNumber, [int]$TimeoutSeconds = 30) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect("127.0.0.1", $PortNumber)
            $client.Close()
            return $true
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }
    return $false
}

function Ensure-Karate {
    if (Test-Path $Jar) {
        $hash = (Get-FileHash $Jar -Algorithm SHA256).Hash
        if ($hash -eq $JarSha256) { return }
        Remove-Item $Jar -Force
    }
    New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
    Write-Step "Downloading Karate 1.5.1"
    Invoke-WebRequest -Uri $JarUrl -OutFile $Jar -UseBasicParsing
    $hash = (Get-FileHash $Jar -Algorithm SHA256).Hash
    if ($hash -ne $JarSha256) {
        throw "Karate jar checksum mismatch: $hash"
    }
}

function Invoke-RemotePython([string]$ScriptPath, [string]$Arguments) {
    $command = "type `"$ScriptPath`" | ssh $SshHost `"docker exec -i $BackendContainer python - $Arguments`""
    $output = cmd /c $command 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "remote python failed ($LASTEXITCODE): $output"
    }
    return $output
}

try {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

    $java = Get-Command java -ErrorAction SilentlyContinue
    if (-not $java) { throw "Java is required (Karate 1.5.1 needs Java 11 or newer)." }
    Ensure-Karate

    $runId = (Get-Date -Format "yyyyMMddHHmmss") + "-" + (Get-Random -Minimum 1000 -Maximum 9999)
    Write-Step "Provisioning disposable identities ($runId)"
    $lines = Invoke-RemotePython (Join-Path $KarateDir "tools\provision_fixture.py") $runId
    $jsonLine = $lines | Where-Object { $_ -match '^\s*\{' } | Select-Object -Last 1
    if (-not $jsonLine) { throw "Fixture provisioning returned no JSON: $lines" }
    $Fixture = $jsonLine | ConvertFrom-Json
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($FixturePath, ($Fixture | ConvertTo-Json -Depth 8), $utf8)
    Write-Step "Fixture written to $FixturePath"

    Write-Step "Opening tunnel 127.0.0.1:$Port -> $SshHost backend"
    $Tunnel = Start-Process -FilePath "ssh" -ArgumentList @(
        "-N", "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=15",
        "-L", "127.0.0.1:${Port}:127.0.0.1:8000", $SshHost
    ) -PassThru -WindowStyle Hidden
    if (-not (Test-Port $Port 30)) {
        throw "Tunnel did not become ready on port $Port."
    }

    Write-Step "Running Karate"
    Push-Location $KarateDir
    try {
        $karateArgs = @(
            "-DbaseUrl=$BaseUrl",
            "-DfixturePath=$FixturePath",
            "-jar", $Jar,
            "-o", $ReportsDir
        )
        if ($Tags) { $karateArgs += @("-t", $Tags) }
        $karateArgs += "features"
        & java @karateArgs
        $karateExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    Write-Host "Karate exit code: $karateExit"
    if (Test-Path (Join-Path $ReportsDir "karate-reports\karate-summary.html")) {
        Write-Host "Report: $(Join-Path $ReportsDir 'karate-reports\karate-summary.html')"
    }
} finally {
    if (Test-Path $FixturePath) {
        Write-Step "Cleaning up disposable identities"
        try {
            $fixtureJson = Get-Content -Raw -LiteralPath $FixturePath
            $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($fixtureJson))
            $cleanupLines = Invoke-RemotePython (Join-Path $KarateDir "tools\cleanup_fixture.py") $encoded
            $cleanupLine = $cleanupLines | Where-Object { $_ -match '^\s*\{' } | Select-Object -Last 1
            if ($cleanupLine) {
                $result = $cleanupLine | ConvertFrom-Json
                Write-Host "Cleanup: requested=$($result.requested) remaining=$($result.remaining)"
                if ([int]$result.remaining -ne 0) {
                    Write-Warning "Some fixture identities remain. Fixture kept at $FixturePath"
                    $KeepFixture = $true
                }
            } else {
                Write-Warning "Cleanup returned no JSON. Fixture kept at $FixturePath"
                $KeepFixture = $true
            }
        } catch {
            Write-Warning "Cleanup failed: $_. Fixture kept at $FixturePath"
            $KeepFixture = $true
        }
    }
    if (-not $KeepFixture -and (Test-Path $FixturePath)) {
        Remove-Item $FixturePath -Force
        Write-Host "Removed $FixturePath"
    }
    if ($Tunnel -and -not $Tunnel.HasExited) {
        Stop-Process -Id $Tunnel.Id -Force
        Write-Host "Closed tunnel"
    }
}

if ($null -eq $karateExit) { exit 1 }
exit $karateExit
