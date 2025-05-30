#!/usr/bin/env python3
import subprocess
import datetime
import sys
import argparse

def run_git_command(command):
    try:
        # 检查脚本执行权限
        if sys.platform == 'win32':
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        else:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✓ {' '.join(command) if isinstance(command, list) else command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 错误: {' '.join(command) if isinstance(command, list) else command}")
        print(f"  {e.stderr.strip()}")
        return False
    except PermissionError:
        print(f"✗ 错误: 没有足够的权限执行命令")
        return False

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='自动执行Git操作')
    parser.add_argument('-m', '--message', help='自定义commit消息')
    parser.add_argument('message', nargs='?', help='位置参数形式的commit消息')
    args = parser.parse_args()

    # 检查是否在Git仓库中
    if not run_git_command(['git', 'rev-parse', '--is-inside-work-tree']):
        print("当前目录不是Git仓库！")
        return

    # 检查远程仓库连接状态
    if not run_git_command(['git', 'remote', 'get-url', 'origin']):
        print("未配置远程仓库！")
        return

    # 获取当前分支名
    try:
        if sys.platform == 'win32':
            branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', text=True, shell=True).strip()
        else:
            branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"无法获取当前分支名！错误信息: {e.stderr if hasattr(e, 'stderr') else ''}")
        return

    # 执行git add .
    if not run_git_command(['git', 'add', '.']):
        return

    # 使用自定义commit消息或生成默认消息
    if args.message:
        commit_message = args.message
    elif args.message is not None:  # 检查位置参数
        commit_message = args.message
    else:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"Auto commit at {timestamp}"

    # 执行git commit
    if not run_git_command(['git', 'commit', '-m', commit_message]):
        return

    # 执行git push
    if not run_git_command(['git', 'push', 'origin', branch]):
        return

    print(f"\n✨ 成功完成所有Git操作！")

if __name__ == '__main__':
    main()