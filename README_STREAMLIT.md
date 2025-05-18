# 发票核对系统 - Streamlit 应用

这是一个基于 Streamlit 的发票核对系统，用于处理和比较发票数据、核对清单和税率信息。

## 功能特点

- 上传和处理三种类型的文件：
  - 税率文件 (duty_rate.xlsx)
  - 核对清单 (processing_checklist.xlsx)
  - 发票文件 (processing_invoices*.xlsx)
- 数据预览功能，可以在处理前查看上传的文件内容
- 自动处理和标准化数据
- 生成差异报告，显示发票和核对清单之间的差异
- 识别新增税率项并生成报告
- 提供处理结果的下载功能

## 安装和运行

### 前提条件

- Python 3.6 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载此仓库到本地
2. 在项目目录中创建并激活虚拟环境（可选但推荐）

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python -m venv .venv
   source .venv/bin/activate
   ```

3. 安装所需依赖

   ```bash
   pip install -r requirements.txt
   ```

### 运行应用

1. 在项目目录中运行以下命令启动 Streamlit 应用：

   ```bash
   streamlit run app.py
   ```

2. 应用将在默认浏览器中自动打开，通常是 http://localhost:8501

## 使用指南

1. **上传文件**：
   - 在左侧边栏上传税率文件、核对清单和发票文件
   - 所有三个文件都必须上传才能进行处理

2. **数据预览**：
   - 在"数据预览"选项卡中查看上传的文件内容
   - 对于发票文件，可以选择不同的工作表进行预览

3. **处理数据**：
   - 上传所有文件后，点击"开始处理"按钮
   - 系统将自动处理数据并生成结果

4. **查看结果**：
   - 在"处理结果"选项卡中查看处理后的发票、核对清单和新增税率项
   - 可以下载处理后的文件

5. **查看差异报告**：
   - 在"差异报告"选项卡中查看发票和核对清单之间的差异
   - 可以下载差异报告

## 文件结构说明

### 输入文件

1. **税率文件 (duty_rate.xlsx)**：
   - 包含商品名称和对应的税率信息
   - 必须包含以下列：Item Name, HSN1, HSN2, Final BCD, Final SWS, Final IGST

2. **核对清单 (processing_checklist.xlsx)**：
   - 包含海关核对清单信息
   - 必须包含以下列：Item#, P/N, Desc, Qty, Price, HSN, Duty, Welfare, IGST

3. **发票文件 (processing_invoices*.xlsx)**：
   - 包含多个工作表，每个工作表代表一个发票
   - 工作表名称应以 CI- 开头
   - 必须包含以下列：Item#, P/N, Desc, Qty, Price

### 输出文件

1. **处理后的发票 (processed_invoices.xlsx)**：
   - 标准化和处理后的发票数据

2. **处理后的核对清单 (processed_checklist.xlsx)**：
   - 标准化和处理后的核对清单数据

3. **差异报告 (processed_report.xlsx)**：
   - 显示发票和核对清单之间的差异

4. **新增税率项 (added_new_items.xlsx)**：
   - 包含在发票中发现但在税率文件中不存在的商品

## 常见问题

**Q: 如何准备发票文件？**  
A: 发票文件应包含多个工作表，每个工作表代表一个发票。工作表名称应以 CI- 开头，例如 CI-2023-INV。

**Q: 如何处理"new item"提示？**  
A: 当系统在发票中发现税率文件中不存在的商品时，会在 added_new_items.xlsx 文件中记录这些商品。您需要在税率文件中添加这些商品的税率信息，然后重新处理数据。

**Q: 为什么我的文件无法上传？**  
A: 确保您的文件格式为 .xlsx，并且文件结构符合系统要求。

**Q: 如何解决处理过程中的错误？**  
A: 检查您的输入文件是否符合系统要求，特别是列名和数据格式。如果问题仍然存在，请查看错误消息以获取更多信息。

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。
