# 发票核对系统 - 增强日志功能

本文档说明了对发票核对系统的日志功能增强，以帮助诊断 Streamlit 执行和脚本执行之间的差异。

## 主要改进

1. **详细的日志记录**：
   - 添加了更详细的日志记录，包括文件名和行号
   - 记录了系统环境信息、命令行参数和关键环境变量
   - 记录了数据处理的每个步骤和关键决策点

2. **重复 ID 处理**：
   - 增强了重复 ID 的检测和处理
   - 详细记录了发现的重复 ID 及其处理方式

3. **价格比对误差范围**：
   - 添加了对价格比对误差范围的明确记录
   - 支持通过命令行参数或 Streamlit 界面设置误差范围

4. **直接运行模式**：
   - 添加了直接运行模式，支持通过命令行参数运行
   - 提供了批处理文件 `run_app_direct.bat` 简化直接运行

## 日志文件位置

所有日志文件保存在 `logs` 目录中，按时间戳命名：
- Streamlit 运行日志：`streamlit_app_YYYYMMDD_HHMMSS.log`
- 直接运行日志：`app_YYYYMMDD_HHMMSS.log`

## 如何使用增强的日志功能

### 查看日志文件

1. 运行应用程序后，查看 `logs` 目录中的最新日志文件
2. 在 Streamlit 界面中，可以使用"日志"标签页查看和筛选日志

### 诊断执行差异

要诊断 Streamlit 执行和脚本执行之间的差异：

1. 使用 Streamlit 运行应用程序：
   ```
   streamlit run app.py
   ```

2. 使用批处理文件直接运行：
   ```
   run_app_direct.bat
   ```

3. 比较两种方式生成的日志文件，特别关注：
   - 输入文件的读取和处理
   - 重复 ID 的检测和处理
   - 价格比对误差范围的设置
   - 比对过程中的差异检测

## 直接运行模式

### 命令行参数

直接运行模式支持以下命令行参数：

```
python app.py <invoices_file> <checklist_file> <duty_rate_file> <output_invoices> <output_checklist> <output_report> [price_tolerance]
```

参数说明：
- `invoices_file`: 发票文件路径
- `checklist_file`: 核对清单路径
- `duty_rate_file`: 税率文件路径
- `output_invoices`: 处理后的发票输出路径
- `output_checklist`: 处理后的核对清单输出路径
- `output_report`: 差异报告输出路径
- `price_tolerance`: (可选) 价格比对误差范围，默认为 1.1%

### 使用批处理文件

批处理文件 `run_app_direct.bat` 提供了一种简单的方式来直接运行应用程序：

1. 确保输入文件位于 `input` 目录：
   - `input/processing_invoices.xlsx`
   - `input/processing_checklist.xlsx`
   - `input/duty_rate.xlsx`

2. 双击运行 `run_app_direct.bat`

3. 处理结果将保存在 `output` 目录：
   - `output/processed_invoices.xlsx`
   - `output/processed_checklist.xlsx`
   - `output/processed_report.xlsx`

## 常见问题排查

1. **结果不一致**：
   - 检查日志中的重复 ID 处理情况
   - 确认价格比对误差范围设置是否一致
   - 查看是否有数据类型转换问题

2. **处理失败**：
   - 检查日志中的异常信息
   - 确认输入文件格式是否正确
   - 检查是否有文件访问权限问题

3. **找不到差异**：
   - 检查价格比对误差范围是否设置过大
   - 确认两个文件中的 ID 是否匹配
   - 查看日志中的比对过程详情
