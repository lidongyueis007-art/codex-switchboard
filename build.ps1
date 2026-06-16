$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

python -m pip install -r requirements.txt

python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name "Codex Switchboard" `
  app.py

Write-Host ""
Write-Host "Built: $PSScriptRoot\dist\Codex Switchboard.exe"
