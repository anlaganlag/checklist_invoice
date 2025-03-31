import subprocess
import sys
import os

def run_script(script_name):
    print(f"\n{'='*50}")
    print(f"执行脚本: {script_name}")
    print(f"{'='*50}\n")
    
    result = subprocess.run([sys.executable, script_name], 
                           cwd=os.path.dirname(os.path.abspath(__file__)),
                           check=False)
    
    if result.returncode != 0:
        print(f"\n错误: {script_name} 执行失败，返回代码 {result.returncode}")
        sys.exit(result.returncode)
    
    print(f"\n{script_name} 执行成功!\n")

def main():
    # 按顺序执行三个脚本
    run_script("clearn_check.py")
    run_script("excel_processor.py")
    subprocess.run([sys.executable, "excel_comparison.py", 
                "checking_list.xlsx", "clean_check.xlsx", "check_report.xlsx"],
               cwd=os.path.dirname(os.path.abspath(__file__)),
               check=True)    
    print("\n所有任务已成功完成!")

if __name__ == "__main__":
    main() 