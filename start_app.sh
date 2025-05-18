#!/bin/bash
cd "/Users/ciiber/Documents/code/checklist_invoice"
source "/Users/ciiber/Documents/code/checklist_invoice/.venv/bin/activate"

# 检查8503端口是否被占用
PORT=8503
PID=$(lsof -ti:$PORT)
if [ -n "$PID" ]; then
    echo "端口 $PORT 被进程 $PID 占用，正在终止该进程..."
    kill -9 $PID
    echo "进程已终止"
fi

# 固定使用8503端口启动应用
streamlit run "/Users/ciiber/Documents/code/checklist_invoice/streamlit_app.py" --server.port=$PORT
