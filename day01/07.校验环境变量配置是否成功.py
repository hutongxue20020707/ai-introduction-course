"""
08. 校验环境变量配置是否成功

写 AI 代码之前，先确认两件事：

    1) .env 文件在不在、密钥能不能读进来
    2) 读到的"密钥"是不是真的密钥（不是占位符、没有空格、没有中文）

为什么要单独跑这一步？
因为密钥配置出错时的报错千奇百怪，最坑的是它长得完全不像"密钥问题"：

    · 401 Authentication Fails          —— 密钥错
    · UnicodeEncodeError: 'ascii' codec  —— 密钥里有中文（或被系统环境变量覆盖）
    · 模型不回复 / 回复为空               —— 有时也是配置问题

先跑一遍这个文件，能省掉一大半排查时间。

运行：python 07.校验环境变量配置是否成功.py
"""

import os
import sys

# Windows 控制台默认 GBK，避免打不出某些字符时崩掉
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

LINE = "=" * 56
passed_all = True


def check(label: str, ok: bool, hint: str = "") -> bool:
    """打印一条检查结果，返回是否通过。
    用 √ / × 而不是 emoji：Windows 控制台是 GBK，emoji 打不出来。"""
    global passed_all
    print(f"    {'√' if ok else '×'} {label}")
    if not ok:
        passed_all = False
        if hint:
            print(f"       → {hint}")
    return ok


print(LINE)
print("校验环境变量配置")
print(LINE)

# ---------------------------------------------------------------------------
# 第 1 步：当前工作目录（.env 要在这一层才能被读到）
# ---------------------------------------------------------------------------
print(f"[1/5] 当前工作目录   {os.getcwd()}")
print(f"       脚本所在目录   {os.path.dirname(os.path.abspath(__file__))}")

# ---------------------------------------------------------------------------
# 第 2 步：.env 文件在不在
# 笔记：这个脚本现在住在 day01/ 里，而 .env 放在项目根目录（agent/），
# 所以不能只看"当前目录"，要从脚本所在目录一层层往上找 ——
# 这也正是 python-dotenv 默认的查找方式（load_dotenv() 会一路往上找）。
# ---------------------------------------------------------------------------
def find_env_file(start_dir):
    """从 start_dir 开始，一层层往上找 .env，找到就返回完整路径。"""
    d = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(d, ".env")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:          # 已经到盘符根目录了
            return None
        d = parent


env_path = find_env_file(os.path.dirname(os.path.abspath(__file__)))
has_env = env_path is not None
print("[2/5] 找 .env 文件")
check("能找到 .env（从脚本目录往上找）", has_env,
      "没找到 .env；它应该放在项目根目录（day01、day02 的上一层），"
      "内容形如 DEEPSEEK_API_KEY=sk-xxx。注意 Windows 要打开“显示文件扩展名”，别弄成 .env.txt")
if has_env:
    print(f"       找到的位置：{env_path}")

# ---------------------------------------------------------------------------
# 第 3 步：依赖装没装
# ---------------------------------------------------------------------------
print("[3/5] 检查依赖")
try:
    from dotenv import load_dotenv
    check("python-dotenv 已安装", True)
except ImportError:
    check("python-dotenv 已安装", False, "执行：pip install -r requirements.txt")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# 第 4 步：把 .env 读进环境变量，然后逐项验货
# 注意顺序：要在 load_dotenv() 之前先看一眼系统里有没有同名变量，
# 否则 load_dotenv 会把它写进 os.environ，你就分不清来源了。
# ---------------------------------------------------------------------------
print("[4/5] 读取 DEEPSEEK_API_KEY")
pre_existing = os.environ.get("DEEPSEEK_API_KEY")     # 先看系统环境变量（加载前）
if has_env:
    load_dotenv(env_path, override=True)   # 指定文件；override=True 让 .env 说了算
else:
    load_dotenv(override=True)             # 没找到就交给它自己往上找
key = os.environ.get("DEEPSEEK_API_KEY", "")

if check("读到了 DEEPSEEK_API_KEY", bool(key), "检查 .env 里有没有写 DEEPSEEK_API_KEY=sk-xxx 这一行"):
    masked = key[:6] + "*" * 6 + key[-4:] if len(key) > 12 else "***"
    print(f"       当前值：{masked}（长度 {len(key)}）")

    check("首尾没有空格", key == key.strip(),
          "密钥首尾的空格会被当成密钥的一部分，导致 401")

    try:
        key.encode("ascii")
        check("只含英文字符（没有中文）", True)
    except UnicodeEncodeError:
        check("只含英文字符（没有中文）", False,
              f"当前值是「{key}」，这不是密钥；另外检查系统环境变量里有没有同名的 DEEPSEEK_API_KEY")

    check("以 sk- 开头", key.startswith("sk-"), "DeepSeek 的密钥都以 sk- 开头，格式不对就是抄错了")

# ---------------------------------------------------------------------------
# 第 5 步：系统环境变量里有没有同名变量（它的"默认"优先级比 .env 高）
# ---------------------------------------------------------------------------
print("[5/5] 检查系统环境变量（不写 override 时，它会盖掉 .env）")
if pre_existing:
    print(f"       系统里【有】同名变量，值：{pre_existing[:6]}{'*' * 6}（长度 {len(pre_existing)}）")
    if pre_existing == key:
        print("       和 .env 里的值一样，不冲突")
    else:
        print("       ⚠ 和 .env 里的值【不一样】！")
        print("         本项目用 load_dotenv(override=True)，以 .env 为准，所以不影响运行；")
        print("         但别的项目如果没写 override=True，就会用到系统里这个值 —— 正是这个坑")
        print("         导致过 'ascii codec' 编码报错。想彻底干净就去删掉这个系统变量：")
        print("         [Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY',$null,'User')")
else:
    print("       系统里没有同名变量，不会干扰 .env")
print("       （本项目统一用 load_dotenv(override=True)，.env 优先级更高）")

# ---------------------------------------------------------------------------
print(LINE)
print("结论：", "环境变量配置成功，可以开始写 AI 代码了" if passed_all else "有项目没通过，按上面 → 后面的提示修")
print(LINE)
