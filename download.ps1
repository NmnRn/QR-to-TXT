#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($msg)  { Write-Host "==> $msg" -ForegroundColor Cyan }
function OK($msg)    { Write-Host " OK: $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "WARN: $msg" -ForegroundColor Yellow }

$RepoUrl   = "https://github.com/NmnRn/QR-to-TXT.git"
$TargetDir = "$env:USERPROFILE\QR-to-TXT"

# Python (>= 3.10)
Info "Checking Python"
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[0-9]|\d{2,})") {
            $python = $cmd; OK $ver; break
        }
    } catch {}
}
if (-not $python) {
    Info "Installing Python 3.12 via winget"
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    $python = "python"
    OK "Python installed"
}

# Git
Info "Checking Git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Info "Installing Git via winget"
    winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    OK "Git installed"
} else {
    OK (git --version)
}

# Clone
if (-not (Test-Path $TargetDir)) {
    Info "Cloning repository"
    git clone $RepoUrl $TargetDir
    OK "Repository cloned"
} else {
    Warn "Repository already exists at $TargetDir, skipping clone"
}

Set-Location $TargetDir

# Virtual environment
Info "Creating virtual environment"
& $python -m venv .venv
OK "Virtual environment created"

# Dependencies
Info "Installing Python dependencies"
& ".venv\Scripts\pip.exe" install --upgrade pip -q
& ".venv\Scripts\pip.exe" install -r requirements.txt -q
OK "Dependencies installed"

# Convert PNG icon -> ICO
Info "Converting icon"
& ".venv\Scripts\python.exe" -c @"
from PIL import Image
img = Image.open('icon/qrtotxt.png')
img.save('icon/qrtotxt.ico', format='ICO', sizes=[(256,256),(64,64),(32,32),(16,16)])
"@
OK "Icon converted"

# Desktop shortcut
Info "Creating desktop shortcut"
$Desktop  = [Environment]::GetFolderPath("Desktop")
$WshShell = New-Object -ComObject WScript.Shell
$Link     = $WshShell.CreateShortcut("$Desktop\QR to TXT.lnk")
$Link.TargetPath       = (Resolve-Path ".venv\Scripts\pythonw.exe").Path
$Link.Arguments        = "`"$(Resolve-Path 'QRtoTXT.py')`""
$Link.WorkingDirectory = $TargetDir
$Link.IconLocation     = (Resolve-Path "icon\qrtotxt.ico").Path
$Link.Description      = "Decode QR codes to text"
$Link.Save()
OK "Shortcut created on Desktop"
