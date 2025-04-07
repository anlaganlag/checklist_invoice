import subprocess
import sys
import os

def run_script(script_name):
    print(f"\n{'='*50}")
    print(f"执行脚本: {script_name}")
    print(f"{'='*50}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, '-Xfrozen_modules=off', script_name], 
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=False,
            env={**os.environ, 'PYDEVD_DISABLE_FILE_VALIDATION': '1'}
        )
        
        if result.returncode != 0:
            print(f"\n错误: {script_name} 执行失败，返回代码 {result.returncode}")
            sys.exit(result.returncode)
        
        print(f"\n{script_name} 执行成功!\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 脚本执行失败: {script_name}")
        print(f"错误代码: {e.returncode}, 错误发生在第 {e.__traceback__.tb_lineno} 行")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n❌ 未知错误: {str(e)}")
        print(f"错误发生在 run_script 函数的第 {e.__traceback__.tb_lineno} 行")
        sys.exit(1)

def main():
    try:
        # 按顺序执行三个脚本
        run_script("processing_checklist.py")
        run_script("processing_invoices.py")
        subprocess.run([sys.executable, "processing_report.py", 
                    "processed_invoices.xlsx", "processed_checklist.xlsx", "processed_report.xlsx"],
                   cwd=os.path.dirname(os.path.abspath(__file__)),
                   check=True)    
        print("\n所有任务已成功完成!")
    except Exception as e:
        print(f"\n❌ 主流程执行失败: {str(e)}")
        print(f"错误发生在第 {e.__traceback__.tb_lineno} 行")
        sys.exit(1)

if __name__ == "__main__":
    main() 