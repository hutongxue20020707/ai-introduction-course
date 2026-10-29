"""
02. 认识 prompt 提示词

老师笔记原话：
    其实也就是上一个案例中 user 后面 content 的内容

也就是说 —— prompt 不是什么新东西，它就是你发给模型的那句话：
上一节课 messages 里 {"role": "user", "content": 这里} 的这个"这里"。

老师原版用的是智谱 AI（ZhipuAI + glm-4），密钥直接写在代码里。
本文件改成 DeepSeek，并且密钥从 .env 读取，不写进源码。
"""

import os
import sys

# Windows 控制台默认是 GBK 编码。模型回复里如果带 emoji（比如 ⭐），
# print 会抛 UnicodeEncodeError 直接把程序搞崩 —— 本机 2026-10-12 真实踩到。
# 这一行让"打不出来的字符"自动变成 ?，而不是崩掉。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# 两个开关（和 day01 一样）
# THINKING：V4 默认开着思考模式，先"想"再答，想的过程也计费。练习建议关掉。
# MODEL   ：想用更强的推理模型就换成 deepseek-v4-pro
# ---------------------------------------------------------------------------
THINKING = "disabled"
MODEL = "deepseek-flash"

load_dotenv(override=True)  # override=True：别让系统里同名的环境变量盖掉 .env

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请确认项目目录下有 .env 文件。")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"DEEPSEEK_API_KEY 里出现了中文字符（当前值：{api_key}），请检查 .env。")

# 创建客户端（DeepSeek 兼容 OpenAI 格式，换个 base_url 就行）
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ---------------------------------------------------------------------------
# 编写提示词 —— 这就是本节课的主角
# ---------------------------------------------------------------------------
prompt = "我想学习人工智能相关技术，需要掌握哪些技能可以找到理想的工作？"

# ---------------------------------------------------------------------------
# 写法一：老师课堂上的写法（把"人设"放在 assistant 里）
# ---------------------------------------------------------------------------
print("=" * 64)
print("写法一：role=assistant 放人设（老师课上的写法）")
print("=" * 64)

res = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "assistant", "content": "你是一名人工智能专家"},
        {"role": "user", "content": prompt},
    ],
    extra_body={"thinking": {"type": THINKING}},
)

print(res.choices[0].message.content)
print(f"(tokens：输入 {res.usage.prompt_tokens} / 输出 {res.usage.completion_tokens})")

# ---------------------------------------------------------------------------
# 写法二：更规范的写法（把"人设"放在 system 里）
# assistant 的语义是"模型自己说过的话"，用它来下指令，模型有可能理解成
# "我之前已经这样介绍过自己了"，然后接着往下说 —— 能跑，但不够准确。
# ---------------------------------------------------------------------------
print()
print("=" * 64)
print("写法二：role=system 放人设（推荐，语义更准）")
print("=" * 64)

res2 = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是一名人工智能专家"},
        {"role": "user", "content": prompt},
    ],
    extra_body={"thinking": {"type": THINKING}},
)

print(res2.choices[0].message.content)
print(f"(tokens：输入 {res2.usage.prompt_tokens} / 输出 {res2.usage.completion_tokens})")
