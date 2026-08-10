# Qualitätsprüfung: flake8, pylint, bandit, detect-secrets, pytest
# Gibt {"continue":false,...} aus und beendet mit Exit-Code 1, wenn Fehler gefunden werden.

$env:PYTHONIOENCODING = 'utf-8'

$pyFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.py$' }
$allFiles = git diff --cached --name-only --diff-filter=ACM

$ok = $true

if ($pyFiles) {
    Write-Host "--- flake8 ---"
    flake8 $pyFiles
    if ($LASTEXITCODE -ne 0) { $ok = $false }

    Write-Host "--- pylint ---"
    pylint $pyFiles
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
python -m pytest test/ --tb=short -q
if ($LASTEXITCODE -ne 0) { $ok = $false }

if (-not $ok) {
    $msg = '{"continue":false,"stopReason":"Commit blockiert: flake8/pylint/bandit/detect-secrets/pytest haben Fehler gemeldet"}'
    Write-Output $msg
    exit 1
}
