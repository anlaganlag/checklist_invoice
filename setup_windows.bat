@echo off
echo ===================================================
echo 发票核对系统 - Windows 环境配置脚本
echo ===================================================
echo.

REM 设置项目路径（请根据实际情况修改）
set PROJECT_PATH=D:\project\invoice_checkList
set REPO_URL=https://github.com/yourusername/invoice_checkList.git

REM 创建日志目录
set LOG_DIR=%PROJECT_PATH%\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG_FILE=%LOG_DIR%\setup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
echo 配置日志将保存到: %LOG_FILE%
echo.

REM 记录系统信息
echo [%date% %time%] 开始配置 Windows 环境 > "%LOG_FILE%"
echo [%date% %time%] 系统信息: >> "%LOG_FILE%"
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" >> "%LOG_FILE%"

REM 检查 Git 是否安装
echo 检查 Git 安装...
where git > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Git 未安装。请安装 Git 后重试。
    echo [%date% %time%] [错误] Git 未安装 >> "%LOG_FILE%"
    goto :error
) else (
    echo Git 已安装: 
    git --version
    git --version >> "%LOG_FILE%"
)

REM 检查项目目录是否存在
echo 检查项目目录...
if not exist "%PROJECT_PATH%" (
    echo 创建项目目录: %PROJECT_PATH%
    mkdir "%PROJECT_PATH%"
    echo [%date% %time%] 创建项目目录: %PROJECT_PATH% >> "%LOG_FILE%"
) else (
    echo 项目目录已存在: %PROJECT_PATH%
    echo [%date% %time%] 项目目录已存在: %PROJECT_PATH% >> "%LOG_FILE%"
)

REM 切换到项目目录
echo 切换到项目目录...
cd /d "%PROJECT_PATH%"
echo [%date% %time%] 切换到项目目录: %cd% >> "%LOG_FILE%"

REM 检查是否已经是 Git 仓库
if exist "%PROJECT_PATH%\.git" (
    echo 更新现有 Git 仓库...
    echo [%date% %time%] 更新现有 Git 仓库 >> "%LOG_FILE%"
    git pull >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [警告] Git pull 失败，尝试重置仓库...
        echo [%date% %time%] [警告] Git pull 失败，尝试重置仓库 >> "%LOG_FILE%"
        git fetch --all >> "%LOG_FILE%" 2>&1
        git reset --hard origin/main >> "%LOG_FILE%" 2>&1
    )
) else (
    echo 克隆 Git 仓库...
    echo [%date% %time%] 克隆 Git 仓库: %REPO_URL% >> "%LOG_FILE%"
    git clone %REPO_URL% . >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [错误] Git 克隆失败
        echo [%date% %time%] [错误] Git 克隆失败 >> "%LOG_FILE%"
        goto :error
    )
)

REM 检查 Python 是否安装
echo 检查 Python 安装...
where python > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Python 未安装。请安装 Python 3.7 或更高版本后重试。
    echo [%date% %time%] [错误] Python 未安装 >> "%LOG_FILE%"
    goto :error
) else (
    echo Python 已安装:
    python --version
    python --version >> "%LOG_FILE%"
)

REM 创建并激活虚拟环境
echo 创建并激活虚拟环境...
if not exist "%PROJECT_PATH%\.venv" (
    echo 创建新的虚拟环境...
    echo [%date% %time%] 创建新的虚拟环境 >> "%LOG_FILE%"
    python -m venv .venv >> "%LOG_FILE%" 2>&1
) else (
    echo 虚拟环境已存在
    echo [%date% %time%] 虚拟环境已存在 >> "%LOG_FILE%"
)

echo 激活虚拟环境...
call "%PROJECT_PATH%\.venv\Scripts\activate.bat"
echo [%date% %time%] 激活虚拟环境 >> "%LOG_FILE%"

REM 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
echo [%date% %time%] 升级 pip >> "%LOG_FILE%"

REM 安装依赖
echo 安装依赖...
echo [%date% %time%] 安装依赖 >> "%LOG_FILE%"

REM 检查 requirements.txt 是否存在
if exist "%PROJECT_PATH%\requirements.txt" (
    echo 使用 requirements.txt 安装依赖...
    pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
) else (
    echo requirements.txt 不存在，安装必要的包...
    pip install streamlit pandas openpyxl xlsxwriter >> "%LOG_FILE%" 2>&1
)

REM 检查安装是否成功
echo 检查依赖安装...
python -c "import streamlit; import pandas; import openpyxl; import xlsxwriter; print('所有依赖已成功安装')" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 依赖安装失败
    echo [%date% %time%] [错误] 依赖安装失败 >> "%LOG_FILE%"
    goto :error
) else (
    echo 所有依赖已成功安装
    echo [%date% %time%] 所有依赖已成功安装 >> "%LOG_FILE%"
)

REM 创建启动脚本
echo 创建启动脚本...
echo @echo off > "%PROJECT_PATH%\start_app.bat"
echo call "%PROJECT_PATH%\.venv\Scripts\activate.bat" >> "%PROJECT_PATH%\start_app.bat"
echo cd /d "%PROJECT_PATH%" >> "%PROJECT_PATH%\start_app.bat"
echo streamlit run "%PROJECT_PATH%\streamlit_app.py" >> "%PROJECT_PATH%\start_app.bat"
echo [%date% %time%] 创建启动脚本: %PROJECT_PATH%\start_app.bat >> "%LOG_FILE%"

echo.
echo ===================================================
echo 配置完成！
echo ===================================================
echo.
echo 要启动应用程序，请运行:
echo %PROJECT_PATH%\start_app.bat
echo.
echo 或者直接运行以下命令:
echo cd /d %PROJECT_PATH% ^&^& .venv\Scripts\activate ^&^& streamlit run streamlit_app.py
echo.
echo 配置日志已保存到: %LOG_FILE%
echo.
goto :end

:error
echo.
echo ===================================================
echo 配置过程中出现错误！
echo 请查看日志文件了解详情: %LOG_FILE%
echo ===================================================
exit /b 1

:end
echo 按任意键启动应用程序...
pause > nul
call "%PROJECT_PATH%\start_app.bat"
