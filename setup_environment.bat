@echo off
echo 正在设置Python环境和安装依赖...

REM 检查是否已安装Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装，请访问以下链接安装Python:
    echo https://www.python.org/downloads/
    echo 安装完成后，请再次运行此脚本
    pause
    exit /b 1
)

echo Python已安装，继续设置虚拟环境...

REM 检查是否已存在虚拟环境
if not exist .venv (
    echo 创建新的虚拟环境...
    python -m venv .venv
) else (
    echo 虚拟环境已存在
)

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

echo 环境设置完成！

REM 创建启动脚本
echo @echo off > run_app.bat
echo call .venv\Scripts\activate.bat >> run_app.bat
echo streamlit run app.py >> run_app.bat
echo pause >> run_app.bat

echo 创建了启动脚本: run_app.bat
echo 要启动应用，请双击运行 run_app.bat

pause 
