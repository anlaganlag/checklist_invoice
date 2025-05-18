#!/bin/bash

echo "==================================================="
echo "发票核对系统 - Mac 启动脚本"
echo "==================================================="
echo

# 设置项目路径（请根据实际情况修改）
PROJECT_PATH="/Users/username/Documents/invoice_checkList"

# 检查项目目录是否存在
if [ ! -d "$PROJECT_PATH" ]; then
    echo "[错误] 项目目录不存在: $PROJECT_PATH"
    echo "请先运行 setup_mac.sh 配置环境"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "$PROJECT_PATH/.venv" ]; then
    echo "[错误] 虚拟环境不存在"
    echo "请先运行 setup_mac.sh 配置环境"
    exit 1
fi

# 检查 Streamlit 应用文件是否存在
if [ ! -f "$PROJECT_PATH/streamlit_app.py" ]; then
    if [ -f "$PROJECT_PATH/app.py" ]; then
        echo "使用 app.py 作为主应用文件"
        APP_FILE="app.py"
    else
        echo "[错误] 找不到 Streamlit 应用文件"
        echo "请确保 streamlit_app.py 或 app.py 存在"
        exit 1
    fi
else
    APP_FILE="streamlit_app.py"
fi

# 切换到项目目录
echo "切换到项目目录: $PROJECT_PATH"
cd "$PROJECT_PATH"

# 激活虚拟环境
echo "激活虚拟环境..."
source "$PROJECT_PATH/.venv/bin/activate"

# 启动 Streamlit 应用
echo "启动 Streamlit 应用..."
echo "应用文件: $APP_FILE"
echo
echo "==================================================="
echo "Streamlit 应用正在启动，请稍候..."
echo "应用启动后将自动在浏览器中打开"
echo "按 Ctrl+C 可以停止应用"
echo "==================================================="
echo

streamlit run "$PROJECT_PATH/$APP_FILE"

echo
echo "==================================================="
echo "应用已关闭"
echo "==================================================="
