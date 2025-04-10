# PowerShell脚本用于设置Python环境和安装依赖

Write-Host "正在设置Python环境和安装依赖..." -ForegroundColor Green

# 检查是否已安装Python
try {
    $pythonVersion = python --version
    Write-Host "已检测到Python：$pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python未安装，请访问以下链接安装Python:" -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "安装完成后，请再次运行此脚本" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host "继续设置虚拟环境..." -ForegroundColor Green

# 检查是否已存在虚拟环境
if (-not (Test-Path -Path ".venv")) {
    Write-Host "创建新的虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "虚拟环境已存在" -ForegroundColor Yellow
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "环境设置完成！" -ForegroundColor Green


Read-Host "按Enter键退出" 