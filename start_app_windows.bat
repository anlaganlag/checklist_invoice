@echo off
echo ===================================================
echo 发票核对系统 - Windows 启动脚本
echo ===================================================
echo.

REM 设置项目路径（请根据实际情况修改）
set PROJECT_PATH=D:\project\invoice_checkList

REM 检查项目目录是否存在
if not exist "%PROJECT_PATH%" (
    echo [错误] 项目目录不存在: %PROJECT_PATH%
    echo 请先运行 setup_windows.bat 配置环境
    goto :error
)

REM 检查虚拟环境是否存在
if not exist "%PROJECT_PATH%\.venv" (
    echo [错误] 虚拟环境不存在
    echo 请先运行 setup_windows.bat 配置环境
    goto :error
)

REM 检查 Streamlit 应用文件是否存在
if not exist "%PROJECT_PATH%\streamlit_app.py" (
    if exist "%PROJECT_PATH%\app.py" (
        echo 使用 app.py 作为主应用文件
        set APP_FILE=app.py
    ) else (
        echo [错误] 找不到 Streamlit 应用文件
        echo 请确保 streamlit_app.py 或 app.py 存在
        goto :error
    )
) else (
    set APP_FILE=streamlit_app.py
)

REM 切换到项目目录
echo 切换到项目目录: %PROJECT_PATH%
cd /d "%PROJECT_PATH%"

REM 激活虚拟环境
echo 激活虚拟环境...
call "%PROJECT_PATH%\.venv\Scripts\activate.bat"

REM 启动 Streamlit 应用
echo 启动 Streamlit 应用...
echo 应用文件: %APP_FILE%
echo.
echo ===================================================
echo Streamlit 应用正在启动，请稍候...
echo 应用启动后将自动在浏览器中打开
echo 按 Ctrl+C 可以停止应用
echo ===================================================
echo.

streamlit run "%PROJECT_PATH%\%APP_FILE%"

goto :end

:error
echo.
echo ===================================================
echo 启动失败！
echo ===================================================
pause
exit /b 1

:end
echo.
echo ===================================================
echo 应用已关闭
echo ===================================================
pause
