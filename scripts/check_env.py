"""
环境自检脚本：一条命令确认 Python / 依赖 / .env 是否就绪。

放在 scripts/ 目录里，所以 .env 是从【脚本所在目录往上找】的（和 load_dotenv 的行为一致）。

运行：
    在项目根目录： python scripts/check_env.py
    在 scripts/：  python check_env.py
不需要联网，也不会消耗任何 API 额度。
"""

import importlib
import os
import sys

# Windows 控制台默认 GBK，让打不出来的字符变成 ?，而不是崩掉
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

print("=" * 46)
print("环境自检")
print("=" * 46)

# 1. Python 本体
print(f"Python 版本 : {sys.version.split()[0]}")
print(f"解释器路径 : {sys.executable}")
if sys.version_info < (3, 10):
    print("[警告] 版本偏低，建议 3.10 以上；本项目在 3.12 上测试")

# 2. 依赖包
PKGS = [
    ("openai", "调 DeepSeek 用的 SDK"),
    ("dotenv", "读 .env（包名 python-dotenv）"),
    ("requests", "调高德/豆瓣等 HTTP 接口"),
    ("gradio", "做网页界面"),
    ("langchain", "Agent / ReAct 框架"),
    ("langgraph", "create_agent 的底层（store 也在这里）"),
]
all_ok = True
for name, desc in PKGS:
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, "__version__", None)
        if ver is None:
            try:
                ver = importlib.import_module(f"{name}.version").__version__
            except Exception:
                ver = "(未知)"
        print(f"[OK]   {name:<10} {str(ver):<12} {desc}")
    except ImportError:
        all_ok = False
        print(f"[缺失] {name:<10} {'':<12} {desc}  →  pip install -r requirements.txt")

# 3. .env 里有哪些变量（只看有没有，不打印值）
print("-" * 46)
try:
    from dotenv import load_dotenv, find_dotenv

    env_path = find_dotenv()
    if env_path:
        print("找到 .env :", env_path)
        load_dotenv(override=True)
    else:
        print("[警告] 没找到 .env —— 从脚本目录往上都没找到")
        print("        请把 .env.example 复制成项目根目录的 .env，再填入密钥")

    EXPECT = [
        ("DEEPSEEK_API_KEY", "DeepSeek 密钥（必需）"),
        ("DEEPSEEK_BASE_URL", "DeepSeek 接口地址"),
        ("AMAP_KEY", "高德天气 key（day03 用）"),
        ("SMTP_USER", "发件邮箱（day03/11 用）"),
        ("SMTP_AUTH_CODE", "SMTP 授权码（day03/11 用）"),
        ("MAIL_TO", "默认收件人"),
    ]
    for key, desc in EXPECT:
        val = os.getenv(key, "")
        if not val:
            print(f"[空]   {key:<20} {desc}")
            continue
        if key.endswith("KEY") or key.endswith("CODE"):
            shown = val[:6] + "*" * 6 + val[-4:] if len(val) > 12 else "***"
        else:
            shown = val
        print(f"[OK]   {key:<20} {shown:<26} {desc}")
except ImportError:
    print("[缺失] python-dotenv，无法检查 .env")

print("-" * 46)
print("结论：", "环境就绪" if all_ok else "依赖不完整，请先运行 pip install -r requirements.txt")
print("提示：想验证 DeepSeek 能不能调通，运行 python scripts/test_connection.py")
