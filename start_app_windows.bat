@echo off
chcp 65001 >nul
echo ===================================================
echo Invoice Check System - Windows Startup Script
echo ===================================================
echo.

REM Get current script directory as project path
set PROJECT_PATH=%~dp0
set PROJECT_PATH=%PROJECT_PATH:~0,-1%

echo Project Path: %PROJECT_PATH%

REM Check if virtual environment exists
if not exist "%PROJECT_PATH%\.venv" (
    echo [ERROR] Virtual environment does not exist
    echo Please run setup_windows.bat to configure the environment first
    goto :error
)

REM Check if Streamlit app file exists
if not exist "%PROJECT_PATH%\streamlit_app.py" (
    if exist "%PROJECT_PATH%\app.py" (
        echo Using app.py as main application file
        set APP_FILE=app.py
    ) else (
        echo [ERROR] Cannot find Streamlit app file
        echo Please ensure streamlit_app.py or app.py exists
        goto :error
    )
) else (
    set APP_FILE=streamlit_app.py
)

REM Switch to project directory
echo Switching to project directory: %PROJECT_PATH%
cd /d "%PROJECT_PATH%"

REM Activate virtual environment
echo Activating virtual environment...
call "%PROJECT_PATH%\.venv\Scripts\activate.bat"

REM Start Streamlit app
echo Starting Streamlit application...
echo App file: %APP_FILE%
echo.
echo ===================================================
echo Streamlit app is starting, please wait...
echo The app will open automatically in your browser
echo Press Ctrl+C to stop the application
echo ===================================================
echo.

streamlit run "%PROJECT_PATH%\%APP_FILE%"

goto :end

:error
echo.
echo ===================================================
echo Startup failed!
echo ===================================================
pause
exit /b 1

:end
echo.
echo ===================================================
echo Application closed
echo ===================================================
pause
