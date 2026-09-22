$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$preferredPython = Join-Path $repoRoot 'services/ingestion-service/.venv/Scripts/python.exe'

if (-not (Test-Path $preferredPython)) {
    $preferredPython = $null
}

if (-not $preferredPython) {
    $candidates = @(
        (Join-Path $repoRoot 'services/document-service/.venv/Scripts/python.exe'),
        (Join-Path $repoRoot 'services/ingestion-service/.venv/Scripts/python.exe'),
        (Join-Path $repoRoot 'services/embedding-service/.venv/Scripts/python.exe')
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $preferredPython = $candidate
            break
        }
    }
}

if (-not $preferredPython) {
    Write-Error "No service virtual environment Python was found. Create one for the needed service, for example: cd services/ingestion-service; py -m venv .venv"
    exit 1
}

$scriptPath = Join-Path $repoRoot 'scripts/start-all.py'

& $preferredPython $scriptPath
exit $LASTEXITCODE
