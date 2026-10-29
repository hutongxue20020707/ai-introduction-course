"""
06. AI 中的流式输出

老师原版：智谱 ZhipuAI + glm-4-plus，密钥写在源码里
本版    ：DeepSeek + .env

运行：python 06.AI中的流式输出.py
"""

import os
import sys

# Windows 控制台默认 GBK，模型回复里若带 emoji，print 会直接崩。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

# 两个开关（同前几节）
THINKING = "disabled"        # 思考模式：开着会先"想"一段，流式看起来会先卡一下
MODEL = "deepseek-flash"

load_dotenv(override=True)   # 别让系统里同名的环境变量盖掉 .env

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请确认项目目录下有 .env 文件。")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"DEEPSEEK_API_KEY 里出现了中文字符（当前值：{api_key}），请检查 .env。")

# 创建客户端
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ---------------------------------------------------------------------------
# 编写提示词
# ---------------------------------------------------------------------------
prompt = "你是一名电信行业的专家，请问如何进入到在这个行业并深耕？"
print("我：", prompt)
print("AI：", end="", flush=True)

# ---------------------------------------------------------------------------
# 与 AI 进行交互：全部的"秘密"就是 stream=True 这一个开关
# ---------------------------------------------------------------------------
res = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    stream=True,                                   # ← 本节主角
    extra_body={"thinking": {"type": THINKING}},
)

# 使用循环来获取 AI 的内容并输出在控制台
for chunk in res:
    # 稳妥起见先判断 choices 是否为空（换服务商/换参数时可能出现空分片）
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta.content
    if delta:
        # end=""     → 不换行，把一小段一小段接起来
        # flush=True → 立刻刷到屏幕上；不加的话内容会攒一批才显示，看着像卡住
        print(delta, end="", flush=True)

print()   # 正文结束后补一个换行
print()
print("(本机实测：第一个字大约 0.5 秒就出现了)")


# ---------------------------------------------------------------------------
# 进阶（课上没讲，但很实用）：流式也能统计 token 消耗
# 加一个 stream_options={"include_usage": True}，最后一个分片会带上 usage
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("进阶：流式输出 + 统计 tokens")
print("=" * 60)

res2 = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "用一句话说明什么是流式输出"}],
    stream=True,
    stream_options={"include_usage": True},        # ← 让最后一个分片带用量
    extra_body={"thinking": {"type": THINKING}},
)

usage = None
for chunk in res2:
    if getattr(chunk, "usage", None):              # 带用量的那一片
        usage = chunk.usage
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)

print()
if usage:
    print(f"(tokens：输入 {usage.prompt_tokens} / 输出 {usage.completion_tokens})")
