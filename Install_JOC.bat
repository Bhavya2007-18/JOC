@echo off
setlocal

echo ===========================================
echo       JOC Sentinel Engine Installer
echo ===========================================
echo.

set "SOURCE_EXE=%~dp0backend\dist\JOC.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\JOC"
set "TARGET_EXE=%INSTALL_DIR%\JOC.exe"
:: Fix for Start Menu folder resolution in PowerShell
set "POWERSHELL_SCRIPT=$wshell = New-Object -ComObject WScript.Shell; $shortcut = $wshell.CreateShortcut([Environment]::GetFolderPath('ApplicationData') + '\Microsoft\Windows\Start Menu\Programs\JOC.lnk'); $shortcut.TargetPath = '%TARGET_EXE%'; $shortcut.WorkingDirectory = '%INSTALL_DIR%'; $shortcut.Description = 'JOC Optimization Engine'; $shortcut.Save()"

if not exist "%SOURCE_EXE%" (
    echo ERROR: Could not find the executable!
    echo Looked for: %SOURCE_EXE%
    echo Please ensure the project was built before installing.
    pause
    exit /b 1
)

echo [1/3] Preparing installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [2/3] Copying application files...
copy /y "%SOURCE_EXE%" "%TARGET_EXE%" >nul

echo [3/3] Registering Windows Start Menu integration...
powershell -NoProfile -Command "%POWERSHELL_SCRIPT%"

echo.
echo ===========================================
echo ✅ Installation Complete!
echo.
echo You can now press the Windows Key, type "JOC", 
echo and click on the app to launch it anytime!
echo ===========================================
pause
