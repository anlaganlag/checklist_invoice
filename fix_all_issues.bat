@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ===================================================
echo 一键修复所有问题 - 完整解决方案
echo ===================================================
echo.

set PROJECT_PATH=%~dp0
set PROJECT_PATH=%PROJECT_PATH:~0,-1%

echo 当前项目路径: %PROJECT_PATH%
echo.

echo ===================================================
echo 步骤 1: 检查和修复编码问题
echo ===================================================

REM 设置编码环境变量
set PYTHONIOENCODING=utf-8
set LANG=zh_CN.UTF-8

echo ✓ 设置编码环境变量

REM 确保VSCode设置存在
if not exist "%PROJECT_PATH%\.vscode" mkdir "%PROJECT_PATH%\.vscode"

echo ✓ 创建VSCode设置目录

echo ===================================================
echo 步骤 2: 搜索Python安装
echo ===================================================

set PYTHON_CMD=
set PYTHON_FOUND=0

echo 正在搜索Python安装...

REM 尝试常用Python命令
for %%P in (python py python3) do (
    echo 测试命令: %%P
    %%P --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✓ 找到可用的Python命令: %%P
        %%P --version
        set PYTHON_CMD=%%P
        set PYTHON_FOUND=1
        goto :python_found
    )
)

echo 搜索常见安装路径...
REM 搜索常见安装路径
for %%P in (
    "C:\Python39\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "C:\Program Files\Python39\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python312\python.exe"
) do (
    if exist "%%P" (
        echo 找到Python: %%P
        "%%P" --version >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo ✓ 确认可用: %%P
            "%%P" --version
            set PYTHON_CMD="%%P"
            set PYTHON_FOUND=1
            goto :python_found
        )
    )
)

if !PYTHON_FOUND! EQU 0 (
    echo ❌ 未找到可用的Python安装
    echo.
    echo ===================================================
    echo 需要安装Python
    echo ===================================================
    echo 请访问: https://www.python.org/downloads/
    echo 下载并安装Python，确保勾选：
    echo ✓ "Add Python to PATH"
    echo ✓ "Install pip"
    echo.
    echo 安装完成后，重新运行此脚本
    goto :error
)

:python_found
echo.
echo ===================================================
echo 步骤 3: 设置Python环境
echo ===================================================

echo 使用Python: !PYTHON_CMD!
echo 当前目录: %PROJECT_PATH%
cd /d "%PROJECT_PATH%"

REM 创建虚拟环境
if not exist "%PROJECT_PATH%\.venv" (
    echo 创建虚拟环境...
    !PYTHON_CMD! -m venv .venv
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ 虚拟环境创建失败
        goto :error
    )
    echo ✓ 虚拟环境创建成功
) else (
    echo ✓ 虚拟环境已存在
)

REM 激活虚拟环境
echo 激活虚拟环境...
call "%PROJECT_PATH%\.venv\Scripts\activate.bat"

REM 升级pip
echo 升级pip...
!PYTHON_CMD! -m pip install --upgrade pip
if !ERRORLEVEL! NEQ 0 (
    echo ⚠ pip升级失败，继续安装依赖
)

echo.
echo ===================================================
echo 步骤 4: 安装项目依赖
echo ===================================================

REM 安装依赖
if exist "%PROJECT_PATH%\requirements.txt" (
    echo 使用requirements.txt安装依赖...
    !PYTHON_CMD! -m pip install -r requirements.txt
) else (
    echo 安装必要的依赖包...
    !PYTHON_CMD! -m pip install streamlit pandas openpyxl xlsxwriter
)

if !ERRORLEVEL! NEQ 0 (
    echo ❌ 依赖安装失败
    goto :error
)

echo ✓ 依赖安装成功

REM 验证安装
echo 验证安装...
!PYTHON_CMD! -c "import streamlit; import pandas; import openpyxl; import xlsxwriter; print('All packages imported successfully')"
if !ERRORLEVEL! NEQ 0 (
    echo ❌ 模块导入验证失败
    goto :error
)

echo ✓ 所有模块验证通过

echo.
echo ===================================================
echo 步骤 5: 创建启动脚本
echo ===================================================

REM 创建启动脚本
echo 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%PROJECT_PATH%"
echo call "%PROJECT_PATH%\.venv\Scripts\activate.bat"
echo echo 正在启动发票核对系统...
echo !PYTHON_CMD! -m streamlit run "%PROJECT_PATH%\streamlit_app.py"
echo pause
) > "%PROJECT_PATH%\start_app_final.bat"

echo ✓ 启动脚本创建完成: start_app_final.bat

echo.
echo ===================================================
echo ✅ 所有问题修复完成！
echo ===================================================
echo.
echo 📋 修复内容：
echo ✓ 编码问题已解决
echo ✓ Python环境已配置
echo ✓ 虚拟环境已创建
echo ✓ 依赖包已安装
echo ✓ 启动脚本已生成
echo.
echo 🚀 启动应用：
echo 运行: start_app_final.bat
echo.
echo 或者手动启动：
echo cd %PROJECT_PATH%
echo .venv\Scripts\activate
echo streamlit run streamlit_app.py
echo.

echo 是否现在启动应用？(Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    echo 正在启动应用...
    call "%PROJECT_PATH%\start_app_final.bat"
) else (
    echo 稍后运行 start_app_final.bat 启动应用
)

goto :end

:error
echo.
echo ===================================================
echo ❌ 修复过程中出现错误
echo ===================================================
echo.
echo 请尝试以下解决方案：
echo 1. 以管理员身份运行此脚本
echo 2. 检查网络连接（下载依赖需要）
echo 3. 临时禁用杀毒软件
echo 4. 手动安装Python: https://www.python.org/downloads/
echo.
pause
exit /b 1

:end
echo.
echo 修复完成！按任意键退出...
pause > nul 