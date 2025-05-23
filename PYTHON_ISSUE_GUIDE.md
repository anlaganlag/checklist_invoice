# Python 环境问题解决指南

## 问题诊断

您的系统存在Python环境问题：
- Windows Store版Python检测到但不能正常工作
- `pip` 命令无法识别
- 需要重新配置Python环境

## 解决方案

### 方案一：重新安装Python（推荐）

1. **下载官方Python**
   - 访问：https://www.python.org/downloads/
   - 下载最新版本（推荐Python 3.11或3.12）

2. **正确安装**
   ```
   安装时必须勾选：
   ✓ "Add Python to PATH"
   ✓ "Install pip" 
   ✓ "Install for all users"
   ```

3. **验证安装**
   ```cmd
   python --version
   pip --version
   ```

### 方案二：使用修复脚本

运行我们提供的脚本：

1. **检查Python环境**
   ```cmd
   .\check_python.bat
   ```

2. **查看安装指导**
   ```cmd
   .\install_python.bat
   ```

3. **使用修复版安装**
   ```cmd
   .\setup_windows_fixed.bat
   ```

### 方案三：手动修复PATH

1. **查找Python安装位置**
   - 检查这些路径：
     - `C:\Python3*\`
     - `C:\Program Files\Python3*\`
     - `%LOCALAPPDATA%\Programs\Python\`

2. **添加到PATH环境变量**
   - Win+R 运行 `sysdm.cpl`
   - 高级 → 环境变量
   - 系统变量 → Path → 编辑
   - 添加Python安装目录和Scripts目录

## 常见问题

### Q: Windows Store Python不工作
A: Windows Store版Python经常有权限和路径问题，建议卸载后安装官方版本

### Q: 安装后仍然找不到python命令
A: 
1. 重启命令提示符/PowerShell
2. 检查PATH环境变量
3. 使用完整路径测试：`C:\Python311\python.exe --version`

### Q: pip安装包时出错
A: 
1. 升级pip：`python -m pip install --upgrade pip`
2. 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name`

## 验证步骤

安装完成后，运行这些命令验证：

```cmd
# 检查Python版本
python --version

# 检查pip版本  
pip --version

# 测试模块安装
python -c "import sys; print(sys.executable)"

# 测试pip安装
pip install requests
python -c "import requests; print('Success!')"
```

## 项目特定解决方案

### 使用修复版脚本
```cmd
# 运行修复版安装脚本
.\setup_windows_fixed.bat

# 脚本会自动：
# 1. 搜索可用的Python安装
# 2. 创建虚拟环境
# 3. 安装依赖包
# 4. 生成启动脚本
```

### 手动安装依赖
如果自动脚本失败，手动安装：
```cmd
# 找到Python后手动操作
C:\Python311\python.exe -m venv .venv
.venv\Scripts\activate
python -m pip install streamlit pandas openpyxl xlsxwriter
```

## 下一步

Python环境修复后：
1. 运行 `.\setup_windows_fixed.bat`
2. 运行 `.\start_app_generated.bat`
3. 项目将在浏览器中自动打开

## 需要帮助？

如果问题持续存在：
1. 检查Windows版本和用户权限
2. 临时禁用杀毒软件
3. 以管理员身份运行安装程序
4. 考虑使用Anaconda或Miniconda替代方案 