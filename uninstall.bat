@echo off
echo ================================
echo    YTGrab Uninstaller
echo ================================
echo.

:: Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This uninstaller requires Administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

set "INSTALLDIR=%ProgramFiles%\YTGrab"
echo Uninstalling YTGrab from: %INSTALLDIR%
echo.

:: Remove scheduled task (startup)
echo Removing startup task...
powershell -Command "Unregister-ScheduledTask -TaskName 'YTGrab' -Confirm:$false" 2>nul

:: Remove desktop shortcut
if exist "%USERPROFILE%\Desktop\YTGrab.lnk" del "%USERPROFILE%\Desktop\YTGrab.lnk"

:: Remove Start Menu shortcut
if exist "%ProgramData%\Microsoft\Windows\Start Menu\Programs\YTGrab.lnk" del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\YTGrab.lnk"

:: Remove installation directory
if exist "%INSTALLDIR%" (
    echo Removing application files...
    rmdir /S /Q "%INSTALLDIR%"
)

echo.
echo ================================
echo    Uninstallation Complete!
echo ================================
echo.
echo YTGrab has been removed from your system.
echo.
pause
