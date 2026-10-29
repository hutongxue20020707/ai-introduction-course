"""
from multiprocessing.connection import Client


这是注释
开发步骤
1.下载包（依赖资源）：pip install requests
2.导入包（模块资源）：from zhipuai import Zhipuai
3.创建客户端
client = Zhipuai(api_key="申请秘钥")
4.我们与模型交互
res=client.chat.completions.create("你好")
model="glm-4",#设置模型为glm-4
messages=[]
"""

# ============================================================================
# day01 最终案例：调用 DeepSeek 大模型，并把回复打印在控制台
# 运行：python 01.认识大模型.py
# ============================================================================

import os
import sys

# Windows 控制台默认 GBK，模型回复里若带 emoji（如 ⭐），print 会直接崩。
# 这一行让"打不出来的字符"自动变成 ?，而不是崩掉。（2026-10-12 真实踩到）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

# ----------------------------------------------------------------------------
# 思考模式开关
# DeepSeek V4 默认开启"思考模式"：模型先想一段再回答，想的过程同样计费。
# 实测（2026-09-20，问"只回复两个字：通了"）：
#   开启思考 -> 输出 121 tokens（其中思考 119）
#   关闭思考 -> 输出 1 token
# 日常练习关掉它，又快又省；数学题、逻辑推理题再打开。
# ----------------------------------------------------------------------------
THINKING = "disabled"      # "enabled" 开 / "disabled" 关
MODEL = "deepseek-flash"   # 想用更强的推理模型就换成 deepseek-v4-pro

# override=True 很重要：否则如果系统里碰巧有个同名的环境变量（比如误设的
# DEEPSEEK_API_KEY=申请秘钥），它会盖掉 .env 里的真密钥，报一堆看不懂的错。
load_dotenv(override=True)  # 读取同目录下的 .env 文件

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请确认项目目录下有 .env 文件。")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(
        f"DEEPSEEK_API_KEY 里出现了中文字符（当前值：{api_key}）。\n"
        "密钥只能由英文字母、数字和 - 组成，且以 sk- 开头。请检查 .env。"
    )

# DeepSeek 兼容 OpenAI 接口格式，所以用 openai 这个包，只改 base_url
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是一个耐心的 Python 助教，回答要简短。"},
        {"role": "user", "content": "用一句话解释什么是大语言模型。"},
    ],
    stream=False,
    extra_body={"thinking": {"type": THINKING}},
)

message = response.choices[0].message

print("=" * 40)
print("AI：", message.content)          # 这就是"AI 回复的内容"
print("=" * 40)

# 思考模式开着时，思考过程在 reasoning_content 里（不在 content 里）
reasoning = getattr(message, "reasoning_content", None)
if reasoning:
    print(f"（模型思考了 {len(reasoning)} 字，此处省略。想看就改成 print(reasoning)）")

# 关心费用时可以打印 token 用量
if response.usage:
    print(f"本次消耗 tokens：输入 {response.usage.prompt_tokens}，输出 {response.usage.completion_tokens}")
