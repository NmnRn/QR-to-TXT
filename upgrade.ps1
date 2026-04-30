#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($msg)  { Write-Host "==> $msg" -ForegroundColor Cyan }
function OK($msg)    { Write-Host " OK: $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "WARN: $msg" -ForegroundColor Yellow }

$TargetDir = "$env:USERPROFILE\QR-to-TXT"

if (-not (Test-Path $TargetDir)) {
    Warn "Project folder not found: $TargetDir"
    exit 1
}

Set-Location $TargetDir

Info "Updating repository"
git pull --ff-only
OK "Repository updated"

Info "Updating Python dependencies"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".venv\Scripts\pip.exe" install --upgrade pip -q
& ".venv\Scripts\pip.exe" install -r requirements.txt -q
OK "Dependencies updated"

Info "Refreshing icon"
& ".venv\Scripts\python.exe" -c @"
from PIL import Image
img = Image.open('icon/qrtotxt.png')
img.save('icon/qrtotxt.ico', format='ICO', sizes=[(256,256),(64,64),(32,32),(16,16)])
"@

Info "Refreshing desktop shortcut"
$Desktop  = [Environment]::GetFolderPath("Desktop")
$WshShell = New-Object -ComObject WScript.Shell
$Link     = $WshShell.CreateShortcut("$Desktop\QR to TXT.lnk")
$Link.TargetPath       = (Resolve-Path ".venv\Scripts\pythonw.exe").Path
$Link.Arguments        = "`"$(Resolve-Path 'QRtoTXT.py')`""
$Link.WorkingDirectory = $TargetDir
$Link.IconLocation     = (Resolve-Path "icon\qrtotxt.ico").Path
$Link.Description      = "Decode QR codes to text"
$Link.Save()
OK "Shortcut refreshed"

OK "Upgrade completed"
