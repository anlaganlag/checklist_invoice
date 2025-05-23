@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ===================================================
echo Invoice Check System - Windows Setup Script (Fixed)
echo ===================================================
echo.

REM Get current script directory as project path
set PROJECT_PATH=%~dp0
set PROJECT_PATH=%PROJECT_PATH:~0,-1%

echo Project Path: %PROJECT_PATH%

REM Create log directory
set LOG_DIR=%PROJECT_PATH%\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG_FILE=%LOG_DIR%\setup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
echo Setup log will be saved to: %LOG_FILE%
echo.

REM Record system information
echo [%date% %time%] Starting Windows environment setup > "%LOG_FILE%"
echo [%date% %time%] System info: >> "%LOG_FILE%"
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" >> "%LOG_FILE%"

REM Find Python executable
set PYTHON_CMD=
set PYTHON_FOUND=0

echo Searching for Python installation...

REM Try common Python commands
for %%P in (python py python3) do (
    %%P --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo Found working Python command: %%P
        echo [%date% %time%] Found working Python command: %%P >> "%LOG_FILE%"
        set PYTHON_CMD=%%P
        set PYTHON_FOUND=1
        goto :python_found
    )
)

REM Try common installation paths
echo Checking common Python installation paths...
for %%P in (
    "C:\Python39\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Program Files\Python39\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files (x86)\Python39\python.exe"
    "C:\Program Files (x86)\Python310\python.exe"
    "C:\Program Files (x86)\Python311\python.exe"
    "C:\Program Files (x86)\Python312\python.exe"
) do (
    if exist "%%P" (
        echo Found Python at: %%P
        "%%P" --version >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo Python version:
            "%%P" --version
            echo [%date% %time%] Found working Python at: %%P >> "%LOG_FILE%"
            set PYTHON_CMD="%%P"
            set PYTHON_FOUND=1
            goto :python_found
        )
    )
)

if %PYTHON_FOUND% EQU 0 (
    echo [ERROR] Python not found or not working
    echo [%date% %time%] [ERROR] Python not found or not working >> "%LOG_FILE%"
    echo.
    echo Please run install_python.bat for installation guidance
    goto :error
)

:python_found
echo Python command: %PYTHON_CMD%
%PYTHON_CMD% --version
%PYTHON_CMD% --version >> "%LOG_FILE%"

REM Switch to project directory
echo Switching to project directory...
cd /d "%PROJECT_PATH%"
echo [%date% %time%] Switched to project directory: %cd% >> "%LOG_FILE%"

REM Create and activate virtual environment
echo Creating and activating virtual environment...
if not exist "%PROJECT_PATH%\.venv" (
    echo Creating new virtual environment...
    echo [%date% %time%] Creating new virtual environment >> "%LOG_FILE%"
    %PYTHON_CMD% -m venv .venv >> "%LOG_FILE%" 2>&1
) else (
    echo Virtual environment already exists
    echo [%date% %time%] Virtual environment already exists >> "%LOG_FILE%"
)

echo Activating virtual environment...
call "%PROJECT_PATH%\.venv\Scripts\activate.bat"
echo [%date% %time%] Activated virtual environment >> "%LOG_FILE%"

REM Upgrade pip
echo Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
echo [%date% %time%] Upgraded pip >> "%LOG_FILE%"

REM Install dependencies
echo Installing dependencies...
echo [%date% %time%] Installing dependencies >> "%LOG_FILE%"

REM Check if requirements.txt exists
if exist "%PROJECT_PATH%\requirements.txt" (
    echo Using requirements.txt to install dependencies...
    %PYTHON_CMD% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
) else (
    echo requirements.txt not found, installing necessary packages...
    %PYTHON_CMD% -m pip install streamlit pandas openpyxl xlsxwriter >> "%LOG_FILE%" 2>&1
)

REM Check installation success
echo Checking dependency installation...
%PYTHON_CMD% -c "import streamlit; import pandas; import openpyxl; import xlsxwriter; print('All dependencies installed successfully')" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency installation failed
    echo [%date% %time%] [ERROR] Dependency installation failed >> "%LOG_FILE%"
    goto :error
) else (
    echo All dependencies installed successfully
    echo [%date% %time%] All dependencies installed successfully >> "%LOG_FILE%"
)

REM Create startup script with found Python command
echo Creating startup script...
echo @echo off > "%PROJECT_PATH%\start_app_generated.bat"
echo chcp 65001 ^>nul >> "%PROJECT_PATH%\start_app_generated.bat"
echo call "%PROJECT_PATH%\.venv\Scripts\activate.bat" >> "%PROJECT_PATH%\start_app_generated.bat"
echo cd /d "%PROJECT_PATH%" >> "%PROJECT_PATH%\start_app_generated.bat"
echo %PYTHON_CMD% -m streamlit run "%PROJECT_PATH%\streamlit_app.py" >> "%PROJECT_PATH%\start_app_generated.bat"
echo [%date% %time%] Created startup script: %PROJECT_PATH%\start_app_generated.bat >> "%LOG_FILE%"

echo.
echo ===================================================
echo Setup completed successfully!
echo ===================================================
echo.
echo Python command used: %PYTHON_CMD%
echo.
echo To start the application, run:
echo %PROJECT_PATH%\start_app_generated.bat
echo.
echo Setup log saved to: %LOG_FILE%
echo.
goto :end

:error
echo.
echo ===================================================
echo An error occurred during setup!
echo ===================================================
echo Please check the log file for details: %LOG_FILE%
echo.
echo For Python installation help, run: install_python.bat
echo.
pause
exit /b 1

:end
echo Press any key to start the application...
pause > nul
call "%PROJECT_PATH%\start_app_generated.bat" 