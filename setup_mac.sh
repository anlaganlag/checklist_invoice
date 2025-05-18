#!/bin/bash

echo "==================================================="
echo "发票核对系统 - Mac 环境配置脚本"
echo "==================================================="
echo

# 设置项目路径（请根据实际情况修改）
PROJECT_PATH="/Users/ciiber/Documents/code/checklist_invoice"
REPO_URL="https://github.com/anlaganlag/checklist_invoice.git"

# 创建日志目录
LOG_DIR="$PROJECT_PATH/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/setup_$(date +%Y%m%d_%H%M%S).log"
echo "配置日志将保存到: $LOG_FILE"
echo

# 记录系统信息
echo "[$(date)] 开始配置 Mac 环境" > "$LOG_FILE"
echo "[$(date)] 系统信息:" >> "$LOG_FILE"
sw_vers >> "$LOG_FILE"

# 检查 Git 是否安装
echo "检查 Git 安装..."
if ! command -v git &> /dev/null; then
    echo "[错误] Git 未安装。请安装 Git 后重试。"
    echo "[$(date)] [错误] Git 未安装" >> "$LOG_FILE"
    exit 1
else
    echo "Git 已安装: $(git --version)"
    git --version >> "$LOG_FILE"
fi

# 检查项目目录是否存在
echo "检查项目目录..."
if [ ! -d "$PROJECT_PATH" ]; then
    echo "创建项目目录: $PROJECT_PATH"
    mkdir -p "$PROJECT_PATH"
    echo "[$(date)] 创建项目目录: $PROJECT_PATH" >> "$LOG_FILE"
else
    echo "项目目录已存在: $PROJECT_PATH"
    echo "[$(date)] 项目目录已存在: $PROJECT_PATH" >> "$LOG_FILE"
fi

# 切换到项目目录
echo "切换到项目目录..."
cd "$PROJECT_PATH"
echo "[$(date)] 切换到项目目录: $(pwd)" >> "$LOG_FILE"

# 检查是否已经是 Git 仓库
if [ -d "$PROJECT_PATH/.git" ]; then
    echo "更新现有 Git 仓库..."
    echo "[$(date)] 更新现有 Git 仓库" >> "$LOG_FILE"
    # 使用绝对路径执行git pull
    if ! /usr/bin/git -C "$PROJECT_PATH" pull >> "$LOG_FILE" 2>&1; then
        echo "[警告] Git pull 失败，尝试重置仓库..."
        echo "[$(date)] [警告] Git pull 失败，尝试重置仓库" >> "$LOG_FILE"
        /usr/bin/git -C "$PROJECT_PATH" fetch --all >> "$LOG_FILE" 2>&1
        /usr/bin/git -C "$PROJECT_PATH" reset --hard origin/main >> "$LOG_FILE" 2>&1
    fi
else
    echo "克隆 Git 仓库..."
    echo "[$(date)] 克隆 Git 仓库: $REPO_URL" >> "$LOG_FILE"
    if ! /usr/bin/git clone "$REPO_URL" . >> "$LOG_FILE" 2>&1; then
        echo "[错误] Git 克隆失败"
        echo "[$(date)] [错误] Git 克隆失败" >> "$LOG_FILE"
        exit 1
    fi
fi

# 检查 Python 是否安装
echo "检查 Python 安装..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python 未安装。请安装 Python 3.7 或更高版本后重试。"
    echo "[$(date)] [错误] Python 未安装" >> "$LOG_FILE"
    exit 1
else
    echo "Python 已安装: $(python3 --version)"
    python3 --version >> "$LOG_FILE"
fi

# 创建并激活虚拟环境
echo "创建并激活虚拟环境..."
if [ ! -d "$PROJECT_PATH/.venv" ]; then
    echo "创建新的虚拟环境..."
    echo "[$(date)] 创建新的虚拟环境" >> "$LOG_FILE"
    python3 -m venv .venv >> "$LOG_FILE" 2>&1
else
    echo "虚拟环境已存在"
    echo "[$(date)] 虚拟环境已存在" >> "$LOG_FILE"
fi

echo "激活虚拟环境..."
source "$PROJECT_PATH/.venv/bin/activate"
echo "[$(date)] 激活虚拟环境" >> "$LOG_FILE"

# 升级 pip
echo "升级 pip..."
python -m pip install --upgrade pip >> "$LOG_FILE" 2>&1
echo "[$(date)] 升级 pip" >> "$LOG_FILE"

# 安装依赖
echo "安装依赖..."
echo "[$(date)] 安装依赖" >> "$LOG_FILE"

# 检查 requirements.txt 是否存在
if [ -f "$PROJECT_PATH/requirements.txt" ]; then
    echo "使用 requirements.txt 安装依赖..."
    pip install -r requirements.txt >> "$LOG_FILE" 2>&1
else
    echo "requirements.txt 不存在，安装必要的包..."
    pip install streamlit pandas openpyxl xlsxwriter >> "$LOG_FILE" 2>&1
fi

# 检查安装是否成功
echo "检查依赖安装..."
if python -c "import streamlit; import pandas; import openpyxl; import xlsxwriter; print('所有依赖已成功安装')" >> "$LOG_FILE" 2>&1; then
    echo "所有依赖已成功安装"
    echo "[$(date)] 所有依赖已成功安装" >> "$LOG_FILE"
else
    echo "[错误] 依赖安装失败"
    echo "[$(date)] [错误] 依赖安装失败" >> "$LOG_FILE"
    exit 1
fi

# 创建启动脚本
echo "创建启动脚本..."
cat > "$PROJECT_PATH/start_app.sh" << EOF
#!/bin/bash
cd "$PROJECT_PATH"
source "$PROJECT_PATH/.venv/bin/activate"

# 检查8503端口是否被占用
PORT=8503
PID=\$(lsof -ti:\$PORT)
if [ -n "\$PID" ]; then
    echo "端口 \$PORT 被进程 \$PID 占用，正在终止该进程..."
    kill -9 \$PID
    echo "进程已终止"
fi

# 固定使用8503端口启动应用
streamlit run "$PROJECT_PATH/streamlit_app.py" --server.port=\$PORT
EOF
chmod +x "$PROJECT_PATH/start_app.sh"
echo "[$(date)] 创建启动脚本: $PROJECT_PATH/start_app.sh" >> "$LOG_FILE"

echo
echo "==================================================="
echo "配置完成！"
echo "==================================================="
echo
echo "要启动应用程序，请运行:"
echo "$PROJECT_PATH/start_app.sh"
echo
echo "或者直接运行以下命令:"
echo "cd $PROJECT_PATH && source .venv/bin/activate && streamlit run streamlit_app.py --server.port=8503"
echo
echo "配置日志已保存到: $LOG_FILE"
echo


"$PROJECT_PATH/start_app.sh"

