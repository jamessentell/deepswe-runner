$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir
try {
    & uv run deepswe @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
