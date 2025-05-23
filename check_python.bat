@echo off
chcp 65001 >nul
echo ===================================================
echo Python Environment Check Script
echo ===================================================
echo.

echo Checking Python installation...

REM Check common Python installations
set PYTHON_FOUND=0

echo Checking for python command...
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ python command found:
    python --version
    set PYTHON_FOUND=1
    goto :check_pip
)

echo Checking for py command...
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ py command found:
    py --version
    set PYTHON_FOUND=1
    goto :check_pip_py
)

echo Checking for python3 command...
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ python3 command found:
    python3 --version
    set PYTHON_FOUND=1
    goto :check_pip3
)

REM Check common installation paths
echo Checking common Python installation paths...
for %%P in (
    "C:\Python*\python.exe"
    "C:\Program Files\Python*\python.exe"
    "C:\Program Files (x86)\Python*\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"
    "%APPDATA%\Local\Programs\Python\Python*\python.exe"
) do (
    if exist "%%P" (
        echo ✓ Found Python at: %%P
        "%%P" --version
        set PYTHON_FOUND=1
        goto :found_python
    )
)

if %PYTHON_FOUND% EQU 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    goto :error
)

:check_pip
echo.
echo Checking pip...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ pip found:
    python -m pip --version
    goto :success
) else (
    echo ❌ pip not working with python command
    goto :fix_pip
)

:check_pip_py
echo.
echo Checking pip with py...
py -m pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ pip found:
    py -m pip --version
    goto :suggest_py
) else (
    echo ❌ pip not working with py command
    goto :fix_pip
)

:check_pip3
echo.
echo Checking pip with python3...
python3 -m pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ pip found:
    python3 -m pip --version
    goto :suggest_python3
) else (
    echo ❌ pip not working with python3 command
    goto :fix_pip
)

:found_python
echo.
echo Found Python installation but command not in PATH
goto :fix_path

:suggest_py
echo.
echo ===================================================
echo SOLUTION: Use 'py' command instead of 'python'
echo ===================================================
echo Your Python is installed but use 'py' command:
echo   py -m pip install package_name
echo   py script.py
goto :end

:suggest_python3
echo.
echo ===================================================
echo SOLUTION: Use 'python3' command instead of 'python'
echo ===================================================
echo Your Python is installed but use 'python3' command:
echo   python3 -m pip install package_name
echo   python3 script.py
goto :end

:fix_pip
echo.
echo ===================================================
echo SOLUTION: Install/Fix pip
echo ===================================================
echo Try these commands:
echo   python -m ensurepip --upgrade
echo   python -m pip install --upgrade pip
goto :end

:fix_path
echo.
echo ===================================================
echo SOLUTION: Fix PATH environment variable
echo ===================================================
echo Python is installed but not in PATH
echo 1. Search "Environment Variables" in Windows Start menu
echo 2. Click "Environment Variables..."
echo 3. Under "System Variables", find and select "Path"
echo 4. Click "Edit..." and add Python installation directory
goto :end

:success
echo.
echo ===================================================
echo ✅ Python and pip are working correctly!
echo ===================================================
goto :end

:error
echo.
echo ===================================================
echo ❌ Python installation required
echo ===================================================
echo Please install Python from: https://www.python.org/downloads/
echo During installation, make sure to check:
echo ✓ "Add Python to PATH"
echo ✓ "Install pip"
goto :end

:end
echo.
pause 