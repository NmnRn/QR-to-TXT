#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($msg)  { Write-Host "==> $msg" -ForegroundColor Cyan }
function OK($msg)    { Write-Host " OK: $msg" -ForegroundColor Green }
function Warn($msg)  { Write-Host "WARN: $msg" -ForegroundColor Yellow }

$TargetDir = "$env:USERPROFILE\QR-to-TXT"
$Shortcut  = "$(  [Environment]::GetFolderPath('Desktop'))\QR to TXT.lnk"

Info "Removing desktop shortcut"
if (Test-Path $Shortcut) {
    Remove-Item $Shortcut
    OK "Shortcut removed"
} else {
    Warn "Shortcut not found: $Shortcut"
}

Info "Removing project folder"
if (Test-Path $TargetDir) {
    Remove-Item $TargetDir -Recurse -Force
    OK "Project folder removed: $TargetDir"
} else {
    Warn "Project folder not found: $TargetDir"
}

OK "Uninstall completed"
