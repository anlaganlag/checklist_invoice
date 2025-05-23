@echo off
chcp 65001 >nul
echo ===================================================
echo Python Installation and Fix Script
echo ===================================================
echo.

echo Current situation: Windows Store Python detected but not working properly
echo.

echo ===================================================
echo SOLUTION OPTIONS:
echo ===================================================
echo.

echo Option 1: Install Python from python.org (RECOMMENDED)
echo --------------------------------------------------------
echo 1. Download Python from: https://www.python.org/downloads/
echo 2. Run the installer as Administrator
echo 3. IMPORTANT: Check these boxes during installation:
echo    ✓ "Add Python to PATH"
echo    ✓ "Install pip"
echo    ✓ "Install for all users"
echo 4. After installation, restart Command Prompt/PowerShell
echo.

echo Option 2: Fix Windows Store Python
echo -----------------------------------
echo 1. Open Windows Settings
echo 2. Go to Apps ^& Features
echo 3. Search for "Python"
echo 4. Click "Advanced options"
echo 5. Click "Reset" or "Repair"
echo.

echo Option 3: Use Chocolatey (Package Manager)
echo ------------------------------------------
echo 1. Install Chocolatey first: https://chocolatey.org/install
echo 2. Run: choco install python
echo.

echo Option 4: Use Scoop (Package Manager)
echo -------------------------------------
echo 1. Install Scoop first: https://scoop.sh/
echo 2. Run: scoop install python
echo.

echo ===================================================
echo VERIFICATION STEPS:
echo ===================================================
echo After installing Python, verify with these commands:
echo   python --version
echo   python -m pip --version
echo   pip --version
echo.

echo If you see version numbers, Python is working correctly!
echo.

echo ===================================================
echo QUICK FIX FOR CURRENT SESSION:
echo ===================================================
echo If you have Python installed elsewhere, try:
echo   C:\Python39\python.exe --version
echo   C:\Python310\python.exe --version
echo   C:\Python311\python.exe --version
echo   C:\Python312\python.exe --version
echo.

echo ===================================================
echo NEXT STEPS AFTER FIXING PYTHON:
echo ===================================================
echo 1. Run: .\setup_windows.bat
echo 2. Run: .\start_app_windows.bat
echo.

pause 