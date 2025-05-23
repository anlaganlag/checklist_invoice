# VSCode 和 Windows 中文乱码解决指南

## 问题现象

在Windows环境下运行批处理文件或Python脚本时，中文字符显示为乱码，如：
- `鍙戠エ鏍稿绯荤粺` 而不是 `发票核对系统`
- `璇峰厛杩愯` 而不是 `请先运行`

## 根本原因

这是因为Windows默认使用GBK/GB2312编码，而现代开发通常使用UTF-8编码造成的编码不匹配。

## 解决方案

### 方法一：运行自动修复脚本（推荐）

1. 双击运行 `fix_encoding.bat`
2. 重启VSCode
3. 重新运行项目

### 方法二：手动设置VSCode

#### 1. 设置VSCode编码
打开VSCode，按 `Ctrl+Shift+P`，输入 `Preferences: Open Settings (JSON)`，添加以下配置：

```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": true,
    "terminal.integrated.shellArgs.windows": ["-NoExit", "-Command", "chcp 65001"],
    "[bat]": {
        "files.encoding": "gbk"
    }
}
```

#### 2. 设置文件编码
1. 在VSCode右下角状态栏点击编码格式（如 `GBK`）
2. 选择 `Reopen with Encoding`
3. 选择 `UTF-8`

#### 3. 保存为UTF-8编码
1. 在VSCode右下角点击编码格式
2. 选择 `Save with Encoding`
3. 选择 `UTF-8`

### 方法三：设置Windows控制台

#### 临时设置（当前会话有效）
```cmd
chcp 65001
```

#### 永久设置
1. 打开注册表编辑器（`regedit`）
2. 导航到：`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Command Processor`
3. 新建字符串值：`Autorun`
4. 值：`chcp 65001 >nul`

### 方法四：设置环境变量

在系统环境变量中添加：
- `PYTHONIOENCODING=utf-8`
- `LANG=zh_CN.UTF-8`

## 文件特定解决方案

### 批处理文件 (.bat)
在批处理文件开头添加：
```bat
@echo off
chcp 65001 >nul
```

### Python文件 (.py)
在文件开头添加：
```python
# -*- coding: utf-8 -*-
```

### PowerShell
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## 验证解决方案

运行以下命令验证编码设置：

```cmd
# 检查当前代码页
chcp

# 应该显示：Active code page: 65001

# 测试中文显示
echo 测试中文显示
```

## 项目特定修复

### 1. 更新的文件
- `start_app_windows.bat` - 修复了硬编码路径问题
- `setup_windows.bat` - 修复了硬编码路径问题
- `.vscode/settings.json` - 添加了VSCode编码设置

### 2. 新增的文件
- `fix_encoding.bat` - 自动编码修复脚本
- `ENCODING_FIX_GUIDE.md` - 本指南文件

### 3. 关键修改
1. 在所有批处理文件开头添加了 `chcp 65001 >nul`
2. 修复了硬编码的项目路径，使用相对路径
3. 添加了VSCode工作区编码设置

## 常见问题

### Q: 修复后仍然有乱码
A: 
1. 完全重启VSCode
2. 检查文件是否保存为UTF-8编码
3. 确认系统区域设置

### Q: 批处理文件执行报错
A:
1. 检查路径是否正确
2. 确认Python和虚拟环境已正确安装
3. 以管理员身份运行

### Q: PowerShell中仍有乱码
A:
在PowerShell配置文件中添加：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

## 测试步骤

1. 运行 `fix_encoding.bat`
2. 重启VSCode
3. 运行 `setup_windows.bat`
4. 运行 `start_app_windows.bat`
5. 检查是否还有乱码

## 预防措施

1. 始终使用UTF-8编码保存文件
2. 在项目根目录添加 `.editorconfig` 文件：
   ```
   root = true
   
   [*]
   charset = utf-8
   end_of_line = lf
   insert_final_newline = true
   trim_trailing_whitespace = true
   ```

3. 在Git中设置自动转换：
   ```bash
   git config --global core.autocrlf true
   ```

通过以上步骤，应该可以完全解决VSCode和Windows环境下的中文乱码问题。 