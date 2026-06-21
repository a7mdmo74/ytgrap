# YTGrab Installer Script
# Run this as Administrator to install YTGrab

param(
    [string]$InstallDir = "$env:ProgramFiles\YTGrab"
)

Write-Host "YTGrab Installer" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host ""

# Check for administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This installer requires Administrator privileges." -ForegroundColor Yellow
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing YTGrab to: $InstallDir" -ForegroundColor Green

# Create installation directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Copy files
Write-Host "Copying application files..." -ForegroundColor Gray
Copy-Item -Path "$PSScriptRoot\dist\YTGrab\*" -Destination $InstallDir -Recurse -Force

# Create desktop shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Gray
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\YTGrab.lnk")
$Shortcut.TargetPath = "$InstallDir\YTGrab.exe"
$Shortcut.IconLocation = "$InstallDir\YTGrab.exe,0"
$Shortcut.Save()

# Create Start Menu shortcut
Write-Host "Creating Start Menu shortcut..." -ForegroundColor Gray
$StartMenuPath = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs"
$Shortcut = $WshShell.CreateShortcut("$StartMenuPath\YTGrab.lnk")
$Shortcut.TargetPath = "$InstallDir\YTGrab.exe"
$Shortcut.IconLocation = "$InstallDir\YTGrab.exe,0"
$Shortcut.Save()

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "You can now launch YTGrab from:" -ForegroundColor Cyan
Write-Host "  - Desktop shortcut" -ForegroundColor White
Write-Host "  - Start Menu" -ForegroundColor White
Write-Host "  - Or run: $InstallDir\YTGrab.exe" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
