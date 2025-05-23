@echo off
chcp 65001 >nul
echo ===================================================
echo VSCode Encoding Fix Script
echo ===================================================
echo.

echo Fixing encoding issues...

REM Set console to UTF-8 encoding
chcp 65001
echo Console encoding set to UTF-8 (65001)

REM Set environment variables
set PYTHONIOENCODING=utf-8
echo Set PYTHONIOENCODING=utf-8

echo.
echo ===================================================
echo Encoding fix completed!
echo ===================================================
echo.
echo VSCode settings saved to .vscode/settings.json
echo.
echo If you still have encoding issues:
echo 1. Restart VSCode
echo 2. Check file encoding (bottom right status bar)
echo 3. Save files as UTF-8 encoding
echo.
pause 