"""
09. 认识 prompt —— 使用环境变量中的密钥

上一节（08）校验的是"环境变量配置对不对"，这一节就是把这份配置真正用起来。

为什么要绕这一圈（.env + 环境变量），不直接把密钥写进代码？

    × 写死在源码里：  client = OpenAI(api_key="sk-8da9c4f3...")
      代码是要交作业、发给同学、传到网上的 —— 密钥写进去就等于公开。
      本机真实踩过的坑：老师示例里写的是 api_key="申请秘钥"，
      有人把这四个字原样设成了系统环境变量，结果报一堆
      UnicodeEncodeError: 'ascii' codec 的错，看着跟密钥毫无关系。

    √ 放 .env 里：   client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"])
      换密钥只改 .env 一行，代码一个字不用动；
      .gitignore 还能把它挡在版本库外，不会被提交。

三种放密钥的方式，一对比就明白：

    ┌──────────────┬───────────┬─────────────┬────────────────────────┐
    │ 放法          │ 安全       │ 换密钥       │ 适用                    │
    ├──────────────┼───────────┼─────────────┼────────────────────────┤
    │ 写死在源码里   │ ✗ 会泄露  │ 要改代码     │ 只在课堂演示、根本不外传  │
    │ .env 文件     │ √ 可忽略  │ 只改一行     │ 个人项目、作业（推荐）    │
    │ 系统环境变量   │ √ 可忽略  │ 改完要重开终端│ 服务器部署、多项目共用    │
    └──────────────┴───────────┴─────────────┴────────────────────────┘

密钥的读取顺序（不写 override 时）：
    1. 系统环境变量   ← 优先级更高，是"莫名报错"的头号元凶
    2. .env 文件
本项目统一写 load_dotenv(override=True)，让 .env 说了算，避免两边不一致。

运行：python 08.认识prompt使用环境变量中的密钥.py
"""

import os
import sys

# Windows 控制台默认 GBK，防 emoji 崩
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"
THINKING = "disabled"


def mask(secret: str) -> str:
    """脱敏显示：只看前 6 位和后 4 位，中间打码。
    习惯很重要 —— 日志、截图、群里贴报错时都别把完整密钥露出去。"""
    if len(secret) <= 12:
        return "*" * len(secret)
    return secret[:6] + "*" * 6 + secret[-4:]


print("=" * 60)
print("第 1 步：从环境变量里读密钥")
print("=" * 60)

load_dotenv(override=True)                      # 把 .env 里的内容读进环境变量
api_key = os.environ.get("DEEPSEEK_API_KEY")    # 从环境变量取，源码里不出现密钥

if not api_key:
    raise SystemExit(
        "没有读到 DEEPSEEK_API_KEY。\n"
        "请先运行上一节的检查脚本：python 07.校验环境变量配置是否成功.py"
    )
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"密钥里有中文字符（当前值：{api_key}），请检查 .env。")

print(f"    读到了：{mask(api_key)}（长度 {len(api_key)}）")
print("    注意：代码里从头到尾没有出现过完整的密钥")

print()
print("=" * 60)
print("第 2 步：用这个密钥创建客户端")
print("=" * 60)

client = OpenAI(
    api_key=api_key,                        # 变量在这里被用掉，但它来自环境变量
    base_url="https://api.deepseek.com",
)
print("    client = OpenAI(api_key=<变量>, base_url='https://api.deepseek.com')")

print()
print("=" * 60)
print("第 3 步：写提示词（prompt）并提问")
print("=" * 60)

prompt = "用两句话说明：为什么密钥不能直接写在代码里？"
print(f"    prompt = {prompt!r}")

res = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    extra_body={"thinking": {"type": THINKING}},
)

print()
print("=" * 60)
print("模型的回答")
print("=" * 60)
print(res.choices[0].message.content)
print()
print(f"(tokens：输入 {res.usage.prompt_tokens} / 输出 {res.usage.completion_tokens})")

print()
print("=" * 60)
print("小结：")
print("  密钥只住在 .env 里，代码只认环境变量里的名字 DEEPSEEK_API_KEY")
print("  → 换密钥改 .env 一行；代码外发、截图、交作业都不会泄露")
print("=" * 60)
