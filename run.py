"""
项目入口：列出所有课程脚本，选一个直接运行。

用法：
    python run.py            # 交互式：显示菜单，输入编号
    python run.py 12         # 直接跑第 12 个
    python run.py 0          # 环境自检
    python run.py list       # 只看清单

为什么需要它：
    课程脚本分散在 day01/ day02/ day03 里，有的要 input()、有的要起网页服务，
    每次 cd 来 cd 去很容易跑错目录（还会导致 .env 读不到）。这里统一从项目根启动，
    并自动把工作目录切到对应 day 文件夹。
"""

import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
DAYS = ["day01", "day02", "day03"]


def collect():
    """收集所有课程脚本，按 day 分组排序"""
    items = []
    for day in DAYS:
        folder = os.path.join(ROOT, day)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.endswith(".py"):
                items.append((day, name, os.path.join(folder, name)))
    return items


def show_menu(items):
    print("=" * 70)
    print("人工智能导论 · 课程脚本运行器")
    print("=" * 70)
    print("[ 0] 环境自检            （scripts/check_env.py）")
    print("[ t] DeepSeek 连通性测试  （scripts/test_connection.py）")
    print()
    current = None
    for i, (day, name, _) in enumerate(items, start=1):
        if day != current:
            current = day
            label = {
                "day01": "day01 · AI 基础与提示词",
                "day02": "day02 · Python 基础 / 多轮对话 / 网页界面",
                "day03": "day03 · 实时信息 / 工具调用 / Agent",
            }.get(day, day)
            print(f"--- {label} ---")
        print(f"[{i:>2}] {name}")
    print()
    print("提示：输入编号后回车。带网页的课（gradio）会打印一个 http 地址，")
    print("      用浏览器打开，按 Ctrl+C 结束。")
    print("=" * 70)


def run_script(path, workdir):
    print(f"\n>>> 运行：{os.path.relpath(path, ROOT)}")
    print("-" * 70)
    # 关键：先把当前进程的缓冲刷出去，否则子进程的输出会写到文件开头、被覆盖
    sys.stdout.flush()
    try:
        code = subprocess.call([sys.executable, path], cwd=workdir)
    except KeyboardInterrupt:
        print("\n（已中断）")
        return 0
    sys.stdout.flush()
    print("-" * 70)
    print(f">>> 结束，退出码 {code}")
    return code


def main():
    items = collect()

    arg = sys.argv[1] if len(sys.argv) > 1 else None

    if arg == "list":
        show_menu(items)
        return 0

    show_menu(items)

    if arg is None:
        arg = input("请输入编号（直接回车退出）：").strip() or "q"

    if arg.lower() in ("q", "quit", "exit"):
        print("再见。")
        return 0

    if arg == "0":
        return run_script(os.path.join(ROOT, "scripts", "check_env.py"), ROOT)
    if arg.lower() == "t":
        return run_script(os.path.join(ROOT, "scripts", "test_connection.py"), ROOT)

    try:
        idx = int(arg) - 1
        day, name, path = items[idx]
    except (ValueError, IndexError):
        print(f"编号无效：{arg}")
        return 1

    return run_script(path, os.path.join(ROOT, day))


if __name__ == "__main__":
    raise SystemExit(main())
