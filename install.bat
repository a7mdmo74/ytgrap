@echo off
echo ================================
echo    YTGrab Installer
echo ================================
echo.

:: Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This installer requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

set "INSTALLDIR=%ProgramFiles%\YTGrab"
echo Installing YTGrab to: %INSTALLDIR%
echo.

:: Create installation directory
if not exist "%INSTALLDIR%" mkdir "%INSTALLDIR%"

:: Copy files
echo Copying application files...
xcopy /E /I /Y "%~dp0dist\YTGrab\*" "%INSTALLDIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy files!
    pause
    exit /b 1
)

:: Copy browser extension
echo Copying browser extension...
xcopy /E /I /Y "%~dp0browser_extension" "%INSTALLDIR%\browser_extension"
if %errorlevel% neq 0 (
    echo WARNING: Could not copy browser extension.
)

:: Verify the exe exists
if not exist "%INSTALLDIR%\YTGrab.exe" (
    echo ERROR: YTGrab.exe not found after copy!
    pause
    exit /b 1
)

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $desk = [Environment]::GetFolderPath('Desktop'); $s = $WshShell.CreateShortcut([System.IO.Path]::Combine($desk, 'YTGrab.lnk')); $s.TargetPath = '%INSTALLDIR%\YTGrab.exe'; $s.IconLocation = '%INSTALLDIR%\YTGrab.exe,0'; $s.Save()"

:: Create Start Menu shortcut
echo Creating Start Menu shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $s = $WshShell.CreateShortcut([System.IO.Path]::Combine($env:ProgramData, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'YTGrab.lnk')); $s.TargetPath = '%INSTALLDIR%\YTGrab.exe'; $s.IconLocation = '%INSTALLDIR%\YTGrab.exe,0'; $s.Save()"

:: Add to Windows startup (runs as background service)
echo Adding to Windows startup...
powershell -Command "New-ScheduledTask -TaskName 'YTGrab' -Description 'YTGrab Download Manager' -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Action (New-ScheduledTaskAction -Execute '%INSTALLDIR%\YTGrab.exe' -Argument '--service') -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Days 365)) -Force"

echo.
echo ================================
echo    Installation Complete!
echo ================================
echo.
echo YTGrab will now:
echo   - Start automatically when you log in
echo   - Run in system tray (background)
echo   - Detect videos from browser extension
echo.
echo You can launch YTGrab from:
echo   - Desktop shortcut
echo   - Start Menu
echo   - System tray icon
echo.
pause
