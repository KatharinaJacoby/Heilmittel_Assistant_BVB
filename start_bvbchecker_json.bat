@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM ===============================
REM BVBChecker Starter (JSON mode)
REM ===============================

REM --- Configuration ---
set "APP_DIR=C:\Program Files\BVBChecker"
set "RULES_FORMAT=json"
set "RULES_JSON=%APP_DIR%\app\rules\rules.json"
set "KBV_VERSION=2025-01-01"
set "HOST=127.0.0.1"
set "PORT=8000"

REM --- Launch service ---
if exist "%APP_DIR%\BVBChecker.exe" (
  echo Starting BVBChecker (JSON rules) from "%APP_DIR%"
  START "" /D "%APP_DIR%" "%APP_DIR%\BVBChecker.exe"
) else (
  echo [ERROR] BVBChecker.exe nicht gefunden unter "%APP_DIR%".
  echo Bitte Installation pruefen.
  exit /b 1
)

REM --- Give it a moment to bind the port, then open UI ---
timeout /t 2 >nul
START "" http://%HOST%:%PORT%/
echo BVBChecker gestartet. Das Fenster kann geschlossen werden.
ENDLOCAL
