@echo off
REM BVB Checker Installer für Windows
REM Installiert BVBChecker.exe in Program Files und erstellt Desktop-Verknüpfung

setlocal enabledelayedexpansion

echo ========================================
echo BVB Checker Installation
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo FEHLER: Bitte als Administrator ausführen
    echo Rechtsklick auf install.bat ^> "Als Administrator ausführen"
    pause
    exit /b 1
)

REM Define paths
set "INSTALL_DIR=C:\Program Files\BVBChecker"
set "EXE_SOURCE=%~dp0BVBChecker.exe"
set "DESKTOP_LINK=%USERPROFILE%\Desktop\BVB Checker.lnk"

echo Installation startet...
echo.

REM Check if source executable exists
if not exist "%EXE_SOURCE%" (
    echo FEHLER: BVBChecker.exe nicht gefunden
    echo Stellen Sie sicher, dass sich BVBChecker.exe im gleichen Ordner befindet
    pause
    exit /b 1
)

REM Create installation directory
echo Erstelle Installationsverzeichnis...
if exist "%INSTALL_DIR%" (
    echo Vorherige Installation gefunden - wird überschrieben
    rmdir /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"

REM Copy executable
echo Kopiere BVBChecker.exe...
copy "%EXE_SOURCE%" "%INSTALL_DIR%\BVBChecker.exe" > nul
if %errorLevel% neq 0 (
    echo FEHLER: Konnte BVBChecker.exe nicht kopieren
    pause
    exit /b 1
)

REM Create start script
echo Erstelle Startskript...
echo @echo off > "%INSTALL_DIR%\start_bvb_checker.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\start_bvb_checker.bat"
echo echo BVB Checker wird gestartet... >> "%INSTALL_DIR%\start_bvb_checker.bat"
echo echo Browser öffnet sich automatisch >> "%INSTALL_DIR%\start_bvb_checker.bat"
echo echo. >> "%INSTALL_DIR%\start_bvb_checker.bat"
echo BVBChecker.exe >> "%INSTALL_DIR%\start_bvb_checker.bat"

REM Create uninstaller
echo Erstelle Deinstallationsskript...
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo echo BVB Checker Deinstallation >> "%INSTALL_DIR%\uninstall.bat"
echo echo ========================== >> "%INSTALL_DIR%\uninstall.bat"
echo echo. >> "%INSTALL_DIR%\uninstall.bat"
echo set /p confirm="BVB Checker wirklich deinstallieren? (j/n): " >> "%INSTALL_DIR%\uninstall.bat"
echo if /i "%%confirm%%"=="j" ( >> "%INSTALL_DIR%\uninstall.bat"
echo     echo Lösche Desktop-Verknüpfung... >> "%INSTALL_DIR%\uninstall.bat"
echo     del "%DESKTOP_LINK%" 2^>nul >> "%INSTALL_DIR%\uninstall.bat"
echo     echo Lösche Programmdateien... >> "%INSTALL_DIR%\uninstall.bat"
echo     cd /d C:\ >> "%INSTALL_DIR%\uninstall.bat"
echo     rmdir /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\uninstall.bat"
echo     echo BVB Checker wurde deinstalliert. >> "%INSTALL_DIR%\uninstall.bat"
echo ^) else ( >> "%INSTALL_DIR%\uninstall.bat"
echo     echo Deinstallation abgebrochen. >> "%INSTALL_DIR%\uninstall.bat"
echo ^) >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

REM Create desktop shortcut using PowerShell
echo Erstelle Desktop-Verknüpfung...
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_LINK%'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_bvb_checker.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'BVB Checker - Heilmittel Verordnungsbedarf prüfen'; $Shortcut.Save()}"

if %errorLevel% neq 0 (
    echo WARNUNG: Desktop-Verknüpfung konnte nicht erstellt werden
) else (
    echo Desktop-Verknüpfung erstellt
)

REM Add to Start Menu (optional)
set "STARTMENU_DIR=%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%STARTMENU_DIR%" (
    echo Füge zu Startmenü hinzu...
    powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_DIR%\BVB Checker.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_bvb_checker.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'BVB Checker - Heilmittel Verordnungsbedarf prüfen'; $Shortcut.Save()}"
)

REM Create uninstall registry entry (optional)
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BVBChecker" /v "DisplayName" /t REG_SZ /d "BVB Checker" /f > nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BVBChecker" /v "UninstallString" /t REG_SZ /d "\"%INSTALL_DIR%\uninstall.bat\"" /f > nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BVBChecker" /v "DisplayVersion" /t REG_SZ /d "1.0.0" /f > nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BVBChecker" /v "Publisher" /t REG_SZ /d "BVB Checker Team" /f > nul 2>&1

echo.
echo ========================================
echo Installation erfolgreich abgeschlossen!
echo ========================================
echo.
echo BVB Checker wurde installiert nach:
echo %INSTALL_DIR%
echo.
echo Desktop-Verknüpfung erstellt: BVB Checker
echo.
echo NUTZUNG:
echo 1. Doppelklick auf Desktop-Symbol "BVB Checker"
echo 2. Browser öffnet sich automatisch
echo 3. ICD-Codes eingeben und BVB/LHB prüfen
echo.
echo DEINSTALLATION:
echo Ausführen: %INSTALL_DIR%\uninstall.bat
echo.

REM Ask if user wants to start immediately
set /p start_now="BVB Checker jetzt starten? (j/n): "
if /i "%start_now%"=="j" (
    echo.
    echo Starte BVB Checker...
    start "" "%INSTALL_DIR%\start_bvb_checker.bat"
) else (
    echo.
    echo BVB Checker kann über die Desktop-Verknüpfung gestartet werden.
)

echo.
pause
