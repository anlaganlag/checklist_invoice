# 邮件通知草稿生成功能

## 功能概述

本功能为Checklist核对系统新增了自动生成邮件通知草稿的能力。当系统检测到发票与核对清单之间存在差异时，可以自动生成标准化的邮件内容，用于通知相关人员进行修正。

## 功能特点

### 1. 自动差异解析
- 自动解析差异报告中的"旧值 -> 新值"格式
- 智能提取正确的值（箭头前的值）
- 支持多种数据字段：HSN、BCD、SWS、IGST、Qty、Price、Desc

### 2. 标准化邮件格式
- 生成符合业务规范的邮件模板
- 统一的邮件结构和用词
- 专业的英文表达

### 3. 智能数据处理
- 自动过滤空值和无效数据
- 跳过相同值的比较
- 处理各种数据类型（数字、文本等）

### 4. 用户友好的界面
- 一键生成邮件草稿
- 邮件内容预览功能
- 支持复制到剪贴板
- 自动打开默认邮件客户端

## 使用方法

### 方法一：处理完成后自动生成
1. 上传必要的文件（税率文件、核对清单、发票文件）
2. 点击"开始处理"按钮
3. 系统自动处理数据并生成差异报告
4. 如果发现差异，系统会自动生成邮件草稿
5. 在页面底部查看"📧 邮件草稿已自动生成"部分
6. 点击"生成通知邮件草稿"按钮打开邮件客户端

### 方法二：在差异报告页面手动生成
1. 切换到"差异报告"标签页
2. 查看差异数据
3. 点击"生成通知邮件草稿"按钮
4. 系统会生成邮件内容并尝试打开邮件客户端
5. 在"邮件草稿预览"部分查看和复制邮件内容

## 邮件模板格式

```
-------------------------------------------------------
Hello ,

Please revise the checklist as below:
Invoice CI001_1 use HSN 85423900 BCD is 10。
Invoice CI002_2 use SWS is 2 HGST is 12 Price is 25.0。
Invoice CI003_3 use BCD is 5 SWS is 1。

Thank you!
-------------------------------------------------------
```

## 支持的字段类型

| 字段名 | 描述 | 邮件中的表达 |
|--------|------|-------------|
| HSN | 海关编码 | HSN {value} |
| BCD | 基本关税 | BCD is {value} |
| SWS | 社会福利附加费 | SWS is {value} |
| IGST | 综合商品服务税 | HGST is {value} |
| Qty | 数量 | Qty is {value} |
| Price | 价格 | Price is {value} |
| Desc | 描述 | Description is {value} |

## 技术实现

### 核心函数

#### `generate_email_draft(diff_report_df)`
- **输入**: 差异报告DataFrame
- **输出**: 格式化的邮件内容字符串
- **功能**: 解析差异数据并生成邮件草稿

#### `open_email_client(email_content, subject)`
- **输入**: 邮件内容和主题
- **输出**: 布尔值（是否成功打开邮件客户端）
- **功能**: 使用mailto协议打开默认邮件客户端

### 数据处理逻辑

1. **差异数据解析**
   ```python
   # 解析"旧值 -> 新值"格式
   correct_value = str(row['HSN']).split(' -> ')[0]
   ```

2. **空值过滤**
   ```python
   # 检查字段是否有效
   if 'HSN' in row and pd.notna(row['HSN']) and str(row['HSN']).strip():
   ```

3. **邮件内容构建**
   ```python
   # 构建修正信息
   corrections.append(f"HSN {hsn_correct}")
   email_line = f"Invoice {invoice_id} use {' '.join(corrections)}。"
   ```

## 错误处理

- **无差异数据**: 返回None，不生成邮件
- **数据解析错误**: 记录日志并返回None
- **邮件客户端打开失败**: 显示警告信息，用户可手动复制内容

## 日志记录

系统会记录以下信息：
- 邮件草稿生成开始/完成
- 处理的差异记录数量
- 错误信息和异常详情

## 兼容性

- **操作系统**: Windows, macOS, Linux
- **邮件客户端**: 支持mailto协议的所有客户端
- **浏览器**: 现代浏览器（Chrome, Firefox, Safari, Edge）

## 注意事项

1. 确保系统已安装默认邮件客户端
2. 某些企业环境可能限制mailto协议的使用
3. 如果无法自动打开邮件客户端，可以手动复制邮件内容
4. 邮件内容使用UTF-8编码，支持中英文混合

## 更新日志

### v1.1 (2025-01-XX)
- 新增邮件通知草稿生成功能
- 支持自动打开邮件客户端
- 添加邮件内容预览功能
- 完善错误处理和日志记录 