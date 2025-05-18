@echo off
echo 发票核对系统 - 直接运行模式
echo ====================================

REM 检查是否存在虚拟环境
if exist .venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，使用系统 Python
)

REM 设置输入和输出文件路径
set INPUT_DIR=input
set OUTPUT_DIR=output
set INVOICES_FILE=%INPUT_DIR%\processing_invoices.xlsx
set CHECKLIST_FILE=%INPUT_DIR%\processing_checklist.xlsx
set DUTY_RATE_FILE=%INPUT_DIR%\duty_rate.xlsx
set OUTPUT_INVOICES=%OUTPUT_DIR%\processed_invoices.xlsx
set OUTPUT_CHECKLIST=%OUTPUT_DIR%\processed_checklist.xlsx
set OUTPUT_REPORT=%OUTPUT_DIR%\processed_report.xlsx

REM 检查输入文件是否存在
if not exist %INVOICES_FILE% (
    echo 错误: 未找到发票文件 %INVOICES_FILE%
    goto :error
)

if not exist %CHECKLIST_FILE% (
    echo 错误: 未找到核对清单 %CHECKLIST_FILE%
    goto :error
)

if not exist %DUTY_RATE_FILE% (
    echo 错误: 未找到税率文件 %DUTY_RATE_FILE%
    goto :error
)

REM 确保输出目录存在
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo 输入文件:
echo   发票文件: %INVOICES_FILE%
echo   核对清单: %CHECKLIST_FILE%
echo   税率文件: %DUTY_RATE_FILE%
echo 输出文件:
echo   处理后的发票: %OUTPUT_INVOICES%
echo   处理后的核对清单: %OUTPUT_CHECKLIST%
echo   差异报告: %OUTPUT_REPORT%
echo.

REM 设置价格比对误差范围 (默认 1.1%)
set PRICE_TOLERANCE=1.1

REM 运行 Python 脚本
echo 开始处理数据...
python app.py %INVOICES_FILE% %CHECKLIST_FILE% %DUTY_RATE_FILE% %OUTPUT_INVOICES% %OUTPUT_CHECKLIST% %OUTPUT_REPORT% %PRICE_TOLERANCE%

if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo 处理完成！
echo 输出文件已保存到 %OUTPUT_DIR% 目录

REM 尝试打开结果文件
if exist %OUTPUT_REPORT% (
    echo 正在打开差异报告...
    start excel %OUTPUT_REPORT%
) else (
    echo 未生成差异报告，可能没有发现差异
)

goto :end

:error
echo.
echo 处理过程中发生错误！
echo 请检查日志文件了解详情。
exit /b 1

:end
echo.
echo 按任意键退出...
pause > nul
exit /b 0
