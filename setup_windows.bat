@echo off
chcp 65001 >nul
echo ===================================================
echo Invoice Check System - Windows Setup Script
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

REM Check if Python is installed
echo Checking Python installation...
where python > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not installed. Please install Python 3.7 or higher and try again.
    echo [%date% %time%] [ERROR] Python not installed >> "%LOG_FILE%"
    goto :error
) else (
    echo Python is installed:
    python --version
    python --version >> "%LOG_FILE%"
)

REM Switch to project directory
echo Switching to project directory...
cd /d "%PROJECT_PATH%"
echo [%date% %time%] Switched to project directory: %cd% >> "%LOG_FILE%"

REM Create and activate virtual environment
echo Creating and activating virtual environment...
if not exist "%PROJECT_PATH%\.venv" (
    echo Creating new virtual environment...
    echo [%date% %time%] Creating new virtual environment >> "%LOG_FILE%"
    python -m venv .venv >> "%LOG_FILE%" 2>&1
) else (
    echo Virtual environment already exists
    echo [%date% %time%] Virtual environment already exists >> "%LOG_FILE%"
)

echo Activating virtual environment...
call "%PROJECT_PATH%\.venv\Scripts\activate.bat"
echo [%date% %time%] Activated virtual environment >> "%LOG_FILE%"

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
echo [%date% %time%] Upgraded pip >> "%LOG_FILE%"

REM Install dependencies
echo Installing dependencies...
echo [%date% %time%] Installing dependencies >> "%LOG_FILE%"

REM Check if requirements.txt exists
if exist "%PROJECT_PATH%\requirements.txt" (
    echo Using requirements.txt to install dependencies...
    pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
) else (
    echo requirements.txt not found, installing necessary packages...
    pip install streamlit pandas openpyxl xlsxwriter >> "%LOG_FILE%" 2>&1
)

REM Check installation success
echo Checking dependency installation...
python -c "import streamlit; import pandas; import openpyxl; import xlsxwriter; print('All dependencies installed successfully')" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency installation failed
    echo [%date% %time%] [ERROR] Dependency installation failed >> "%LOG_FILE%"
    goto :error
) else (
    echo All dependencies installed successfully
    echo [%date% %time%] All dependencies installed successfully >> "%LOG_FILE%"
)

REM Create startup script
echo Creating startup script...
echo @echo off > "%PROJECT_PATH%\start_app.bat"
echo chcp 65001 ^>nul >> "%PROJECT_PATH%\start_app.bat"
echo call "%PROJECT_PATH%\.venv\Scripts\activate.bat" >> "%PROJECT_PATH%\start_app.bat"
echo cd /d "%PROJECT_PATH%" >> "%PROJECT_PATH%\start_app.bat"
echo streamlit run "%PROJECT_PATH%\streamlit_app.py" >> "%PROJECT_PATH%\start_app.bat"
echo [%date% %time%] Created startup script: %PROJECT_PATH%\start_app.bat >> "%LOG_FILE%"

echo.
echo ===================================================
echo Setup completed!
echo ===================================================
echo.
echo To start the application, run:
echo %PROJECT_PATH%\start_app_windows.bat
echo.
echo Or run the following commands directly:
echo cd /d %PROJECT_PATH% ^&^& .venv\Scripts\activate ^&^& streamlit run streamlit_app.py
echo.
echo Setup log saved to: %LOG_FILE%
echo.
goto :end

:error
echo.
echo ===================================================
echo An error occurred during setup!
echo Please check the log file for details: %LOG_FILE%
echo ===================================================
pause
exit /b 1

:end
echo Press any key to start the application...
pause > nul
call "%PROJECT_PATH%\start_app_windows.bat"
