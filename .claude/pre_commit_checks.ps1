# Qualitätsprüfung: qgis_plugin_validate, flake8, pylint, bandit, detect-secrets, pytest
# Gibt {"continue":false,...} aus und beendet mit Exit-Code 1, wenn Fehler gefunden werden.

$env:PYTHONIOENCODING = 'utf-8'

$pyFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.py$' }
$allFiles = git diff --cached --name-only --diff-filter=ACM

$ok = $true

# Plain "python"/"pylint" on PATH resolve to an interpreter without 'qgis'
# on its path and (observed in practice) an older pylint that doesn't even
# know newer message IDs (e.g. possibly-used-before-assignment) - that
# produces both false import-error findings for every qgis.* import and a
# spurious "unknown-option-value" warning for the disable comments guarding
# them, blocking commits for no real reason. Use the QGIS-bundled Python
# instead wherever a check needs to resolve 'qgis' correctly, with the same
# env vars verified to work for a full local pytest run. Candidate install
# locations mirror setup_qgis_path.py.
$qgisCandidates = @(
    "C:\Program Files\QGIS 3.40.0",
    "C:\Program Files\QGIS 3.38.3",
    "C:\Program Files\QGIS 3.36.3",
    "C:\OSGeo4W64"
)
$qgisBase = $qgisCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
$qgisPython = $null
if ($qgisBase) {
    $candidatePython = Join-Path $qgisBase "apps\Python312\python.exe"
    if (Test-Path $candidatePython) { $qgisPython = $candidatePython }
}
if ($qgisPython) {
    $env:PYTHONPATH = "$qgisBase\apps\qgis\python;$qgisBase\apps\qgis\python\plugins;" + (Get-Location).Path + "\.."
    $env:QGIS_PREFIX_PATH = "$qgisBase\apps\qgis"
    $env:QT_QPA_PLATFORM = "offscreen"
    $env:PATH = "$qgisBase\bin;$qgisBase\apps\qgis\bin;$env:PATH"
} else {
    Write-Host "WARNUNG: keine QGIS-Installation gefunden (siehe setup_qgis_path.py) - pylint/pytest fallen auf 'python' zurueck, QGIS-Importe werden vermutlich fehlschlagen."
}

Write-Host "--- qgis_plugin_validate ---"
# Pure stdlib (argparse/re/zipfile/pathlib) - no QGIS import needed, plain
# python is fine. Same check as qgis-plugin-ci.yml's "structure + metadata
# validator" step.
python ci/qgis_plugin_validate.py --auto
if ($LASTEXITCODE -ne 0) { $ok = $false }

if ($pyFiles) {
    Write-Host "--- flake8 ---"
    flake8 $pyFiles
    if ($LASTEXITCODE -ne 0) { $ok = $false }

    Write-Host "--- pylint ---"
    if ($qgisPython) {
        & $qgisPython -m pylint --rcfile=pylintrc $pyFiles
    } else {
        pylint $pyFiles
    }
    if ($LASTEXITCODE -ne 0) { $ok = $false }

    Write-Host "--- bandit ---"
    bandit -r $pyFiles --skip B101
    if ($LASTEXITCODE -ne 0) { $ok = $false }
}

if ($allFiles) {
    Write-Host "--- detect-secrets ---"
    $baseline = ".secrets.baseline"
    if (-not (Test-Path $baseline)) {
        # Windows PowerShell 5.1's Out-File -Encoding utf8 prepends a BOM, which
        # detect-secrets-hook's JSON parser cannot read. Write without BOM instead.
        $scanOutput = detect-secrets scan | Out-String
        $fullPath = Join-Path (Get-Location) $baseline
        [System.IO.File]::WriteAllText($fullPath, $scanOutput, (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "Baseline erstellt: $baseline"
    }
    detect-secrets-hook --baseline $baseline $allFiles
    if ($LASTEXITCODE -ne 0) { $ok = $false }
}

Write-Host "--- pytest ---"
if ($qgisPython) {
    & $qgisPython -m pytest test/ --tb=short -q
} else {
    python -m pytest test/ --tb=short -q
}
if ($LASTEXITCODE -ne 0) { $ok = $false }

if (-not $ok) {
    $msg = '{"continue":false,"stopReason":"Commit blockiert: qgis_plugin_validate/flake8/pylint/bandit/detect-secrets/pytest haben Fehler gemeldet"}'
    Write-Output $msg
    exit 1
}
