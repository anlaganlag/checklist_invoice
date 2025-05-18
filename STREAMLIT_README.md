# 发票核对系统 - Streamlit 版本

这是一个使用 Streamlit 构建的发票核对系统，用于比较发票数据和核对清单，并生成差异报告。

## 功能特点

- 上传并处理税率文件、核对清单和发票文件
- 自动检测并处理重复 ID，避免重复比对
- 可调整价格比对的误差范围
- 生成处理后的发票、核对清单和差异报告
- 提供详细的处理日志，方便排查问题
- 支持下载处理结果和日志文件

## 安装要求

- Python 3.7 或更高版本
- 以下 Python 包:
  - streamlit
  - pandas
  - openpyxl
  - xlsxwriter

## 安装步骤

1. 确保已安装 Python 3.7 或更高版本
2. 创建并激活虚拟环境（可选但推荐）:

```bash
# 创建虚拟环境
python -m venv .venv

# 在 Windows 上激活虚拟环境
.venv\Scripts\activate

# 在 Linux/Mac 上激活虚拟环境
source .venv/bin/activate
```

3. 安装所需的包:

```bash
pip install streamlit pandas openpyxl xlsxwriter
```

## 运行应用

1. 确保已激活虚拟环境（如果使用）
2. 运行以下命令启动 Streamlit 应用:

```bash
streamlit run streamlit_app.py
```

3. 应用将在默认浏览器中打开，通常是 http://localhost:8501

## 使用说明

1. 在左侧边栏上传以下文件:
   - 税率文件 (duty_rate.xlsx)
   - 核对清单 (processing_checklist.xlsx)
   - 发票文件 (processing_invoices.xlsx)

2. 调整价格比对误差范围（默认为 1.1%）

3. 点击"开始处理"按钮

4. 在各个标签页查看结果:
   - 数据预览: 查看上传的原始数据
   - 处理结果: 查看处理后的发票、核对清单和新增税率项
   - 差异报告: 查看发票和核对清单之间的差异
   - 日志: 查看处理日志，可按日志级别筛选

5. 使用各标签页中的下载按钮下载处理结果

## 文件说明

- `streamlit_app.py`: Streamlit 应用主文件
- `input/`: 存放上传的输入文件的目录
- `output/`: 存放处理结果的目录
- `logs/`: 存放处理日志的目录

## 与命令行版本的区别

Streamlit 版本与命令行版本相比有以下改进:

1. 提供了图形用户界面，更易于使用
2. 增加了重复 ID 检测和处理功能，避免重复比对
3. 允许用户调整价格比对的误差范围
4. 提供了详细的处理日志和日志查看功能
5. 支持直接在浏览器中预览和下载处理结果

## 故障排除

如果遇到问题:

1. 检查日志标签页，查看详细的错误信息
2. 确保上传的文件格式正确
3. 尝试调整价格比对误差范围
4. 如果文件保存失败，检查输出文件是否已被其他程序打开

## 注意事项

- 应用会自动创建 `input/`、`output/` 和 `logs/` 目录
- 上传的文件将保存在 `input/` 目录中
- 处理结果将保存在 `output/` 目录中
- 日志文件将保存在 `logs/` 目录中，并按时间戳命名
