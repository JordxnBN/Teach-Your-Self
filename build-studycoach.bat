@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if exist "dist\studycoachapp.exe" del /f "dist\studycoachapp.exe" 2>nul

echo Tip: Close studycoachapp.exe first or the new build cannot overwrite it.
echo Building StudyCoach app from StudyCoach.py...
pyinstaller --clean --noconfirm StudyCoach.spec
if errorlevel 1 (
  echo PyInstaller failed with error %ERRORLEVEL%.
  exit /b %ERRORLEVEL%
)

set "DIST=%~dp0dist\studycoachapp.exe"
if exist "%DIST%" (
  echo Build complete. Run: dist\studycoachapp.exe
  echo Portable: copy studycoachapp.exe to any folder; data\ is created next to it on first run.
) else (
  echo Warning: dist\studycoachapp.exe not found. Check PyInstaller output above.
)
endlocal
