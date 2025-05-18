import subprocess
import sys
import os
import logging
import datetime

# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"run_all_tasks_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def run_script(script_name, args=None):
    separator = "="*50
    print(f"\n{separator}")
    print(f"执行脚本: {script_name}")
    print(f"{separator}\n")

    logging.info(f"Starting script: {script_name}")
    if args:
        logging.info(f"Script arguments: {args}")

    try:
        cmd = [sys.executable, '-Xfrozen_modules=off', script_name]
        if args:
            cmd.extend(args)

        logging.info(f"Command: {' '.join(cmd)}")
        logging.info(f"Working directory: {os.path.dirname(os.path.abspath(__file__))}")

        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=False,
            env={**os.environ, 'PYDEVD_DISABLE_FILE_VALIDATION': '1'},
            capture_output=True,
            text=True
        )

        # Log stdout and stderr
        if result.stdout:
            logging.info(f"Script output:\n{result.stdout}")
        if result.stderr:
            logging.warning(f"Script errors:\n{result.stderr}")

        if result.returncode != 0:
            error_msg = f"\n错误: {script_name} 执行失败，返回代码 {result.returncode}"
            print(error_msg)
            logging.error(error_msg)
            sys.exit(result.returncode)

        success_msg = f"\n{script_name} 执行成功!\n"
        print(success_msg)
        logging.info(success_msg)
    except subprocess.CalledProcessError as e:
        error_msg = f"\n❌ 脚本执行失败: {script_name}"
        print(error_msg)
        logging.error(error_msg)

        detail_msg = f"错误代码: {e.returncode}, 错误发生在第 {e.__traceback__.tb_lineno} 行"
        print(detail_msg)
        logging.error(detail_msg)

        if e.stdout:
            logging.info(f"Script output:\n{e.stdout}")
        if e.stderr:
            logging.error(f"Script errors:\n{e.stderr}")

        sys.exit(e.returncode)
    except Exception as e:
        error_msg = f"\n❌ 未知错误: {str(e)}"
        print(error_msg)
        logging.error(error_msg)

        detail_msg = f"错误发生在 run_script 函数的第 {e.__traceback__.tb_lineno} 行"
        print(detail_msg)
        logging.error(detail_msg)
        logging.exception("Exception details:")

        sys.exit(1)

def main():
    logging.info("="*50)
    logging.info("STARTING MAIN WORKFLOW")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Command line arguments: {sys.argv}")
    logging.info("="*50)

    try:
        # Check if command line arguments were provided
        if len(sys.argv) > 1:
            logging.info(f"Command line arguments detected: {sys.argv[1:]}")

            # If arguments are provided, use them directly with processing_report.py
            if len(sys.argv) >= 7:
                invoices_file = sys.argv[1]
                checklist_file = sys.argv[2]
                duty_rate_file = sys.argv[3]
                output_invoices = sys.argv[4]
                output_checklist = sys.argv[5]
                output_report = sys.argv[6]

                logging.info(f"Using provided arguments:")
                logging.info(f"  Invoices file: {invoices_file}")
                logging.info(f"  Checklist file: {checklist_file}")
                logging.info(f"  Duty rate file: {duty_rate_file}")
                logging.info(f"  Output invoices: {output_invoices}")
                logging.info(f"  Output checklist: {output_checklist}")
                logging.info(f"  Output report: {output_report}")

                # Call processing_report.py with the provided arguments
                run_script("processing_report.py", [
                    invoices_file,
                    checklist_file,
                    duty_rate_file,
                    output_invoices,
                    output_checklist,
                    output_report
                ])
            else:
                logging.warning(f"Insufficient arguments provided. Expected 6, got {len(sys.argv)-1}")
                logging.info("Falling back to default workflow")
                # 按顺序执行三个脚本
                run_script("processing_checklist.py")
                run_script("processing_invoices.py")
                run_script("processing_report.py")
        else:
            logging.info("No command line arguments provided, using default workflow")
            # 按顺序执行三个脚本
            run_script("processing_checklist.py")
            run_script("processing_invoices.py")
            run_script("processing_report.py")

        success_msg = "\n所有任务已成功完成!"
        print(success_msg)
        logging.info(success_msg)
    except Exception as e:
        error_msg = f"\n❌ 主流程执行失败: {str(e)}"
        print(error_msg)
        logging.error(error_msg)

        detail_msg = f"错误发生在第 {e.__traceback__.tb_lineno} 行"
        print(detail_msg)
        logging.error(detail_msg)
        logging.exception("Exception details:")

        sys.exit(1)
    finally:
        logging.info("="*50)
        logging.info("WORKFLOW COMPLETED")
        logging.info("="*50)

if __name__ == "__main__":
    main()