# Qualitätsprüfung für staged Python-Dateien (flake8, pylint, bandit)
# Gibt {"continue":false,...} aus und beendet mit Exit-Code 1, wenn Fehler gefunden werden.

$files = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.py$' }
if (-not $files) { exit 0 }

$ok = $true

Write-Host "--- flake8 ---"
flake8 $files
if ($LASTEXITCODE -ne 0) { $ok = $false }

Write-Host "--- pylint ---"
pylint $files
if ($LASTEXITCODE -ne 0) { $ok = $false }

Write-Host "--- bandit ---"
bandit -r $files
if ($LASTEXITCODE -ne 0) { $ok = $false }

if (-not $ok) {
    $msg = '{"continue":false,"stopReason":"Commit blockiert: flake8/pylint/bandit haben Fehler gemeldet"}'
    Write-Output $msg
    exit 1
}
