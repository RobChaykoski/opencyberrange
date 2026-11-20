# One-command seed for the local Moodle LTI 1.3 showcase.
#
#   pwsh scripts/ecosystem_seed/seed_showcase.ps1
#
# The training stack and OpenCyberRange backend must already be running.

param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
)

$ErrorActionPreference = 'Stop'
$python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

& $python (Join-Path $Root 'scripts/ecosystem_seed/seed_showcase.py') @args
exit $LASTEXITCODE
