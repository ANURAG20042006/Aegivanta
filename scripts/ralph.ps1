# ==============================================================================
# Ralph Autonomous Execution Loop (PowerShell Runner for Windows)
# ==============================================================================
[CmdletBinding()]
param(
    [int]$MaxIterations = 25
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

$TasksFile = ".ralph	asks.json"
$PromptFile = ".ralph\prompt.md"
$PythonExe = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting Ralph Autonomous Loop for Aegivanta" -ForegroundColor Cyan
Write-Host " Max Iterations : $MaxIterations" -ForegroundColor Cyan
Write-Host " Tasks File     : $TasksFile" -ForegroundColor Cyan
Write-Host " Python Executable: $PythonExe" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$Iteration = 1
while ($Iteration -le $MaxIterations) {
    Write-Host "`n--- [Ralph Loop] Iteration $Iteration / $MaxIterations ---" -ForegroundColor Yellow

    if (-not (Test-Path $TasksFile)) {
        Write-Warning "Tasks file $TasksFile not found. Exiting loop."
        break
    }

    $PendingCount = & $PythonExe -c @"
import json
try:
    with open('$($TasksFile.Replace('', '\'))') as f:
        data = json.load(f)
    pending = [t for t in data.get('tasks', []) if t.get('status') in ('pending', 'in_progress')]
    print(len(pending))
except Exception as e:
    print(0)
"@

    if ([int]$PendingCount -eq 0) {
        Write-Host " All tasks in $TasksFile are completed!" -ForegroundColor Green
        Write-Host " Ralph loop finished successfully." -ForegroundColor Green
        exit 0
    }

    Write-Host " Pending tasks remaining: $PendingCount" -ForegroundColor Magenta
    Write-Host " Running test suite verification..." -ForegroundColor Gray
    
    & $PythonExe -m pytest -q
    
    Write-Host " Iteration $Iteration cycle complete." -ForegroundColor Green
    $Iteration++
}

Write-Host "`n Reached maximum iterations ($MaxIterations)." -ForegroundColor Yellow
