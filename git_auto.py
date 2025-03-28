#!/usr/bin/env python3
import subprocess
import datetime
import sys

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
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
    except subprocess.CalledProcessError:
        print("无法获取当前分支名！")
        return

    # 执行git add .
    if not run_git_command(['git', 'add', '.']):
        return

    # 生成commit消息
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