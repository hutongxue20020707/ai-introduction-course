"""
09. 实现一个完整多轮对话功能

前面几节把零件一个个做出来了，这一节把它们拼成"能用的聊天程序"：

    input() 拿输入（06）  →  memoryBox 记历史（03）  →  调 DeepSeek
    →  流式打印（day01 的 06）  →  while 循环（05）  →  退出/清空等指令

功能清单：
    1. 一直聊，输入 退出 / 再见 / exit 结束
    2. 记住上下文（记忆盒子 memoryBox 里带着 system 人设）
    3. 打字机效果（stream=True + flush=True）
    4. 每轮显示 token 消耗（心里有数，别聊到破产）
    5. 指令：帮助 / 历史 / 清空

运行：python 09.实现一个完整多轮对话功能.py
    ★ 在【终端】里运行，它才会停下来等你打字。
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"
THINKING = "disabled"

# ---------------------------------------------------------------------------
# 1. 准备客户端（密钥从项目根目录的 .env 读，load_dotenv 会自己往上找）
# ---------------------------------------------------------------------------
load_dotenv(override=True)
api_key = os.environ.get("DEEPSEEK_API_KEY")

if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"密钥里有中文字符（当前值：{api_key}），请检查 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ---------------------------------------------------------------------------
# 2. 记忆盒子
#    第一条是 system 人设。它也是列表里的一条，清空记忆时要把这条留下来。
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = "你是一个耐心的 AI 助教。回答用中文，尽量简洁，必要时举例子。"
memoryBox = [{"role": "system", "content": SYSTEM_PROMPT}]

total_prompt_tokens = 0
total_completion_tokens = 0
round_no = 0


# ---------------------------------------------------------------------------
# 3. 一次性问答（核心函数）
# ---------------------------------------------------------------------------
def ask(prompt: str) -> str:
    """把问题塞进记忆盒子 → 流式调用 → 把回答也塞回去 → 返回回答文本。"""
    global total_prompt_tokens, total_completion_tokens

    memoryBox.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        model=MODEL,
        messages=memoryBox,                      # 整个记忆盒子发给模型
        stream=True,                             # 流式：一个字一个字吐
        stream_options={"include_usage": True},  # 让最后一片带上 token 用量
        extra_body={"thinking": {"type": THINKING}},
    )

    parts = []
    usage = None
    for chunk in stream:
        if getattr(chunk, "usage", None):
            usage = chunk.usage
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            parts.append(delta)
            print(delta, end="", flush=True)     # end="" 不换行；flush=True 立刻显示

    print()
    answer = "".join(parts)

    # 回答也要放进记忆盒子，否则模型记得"你问过什么"却不记得"它答过什么"
    memoryBox.append({"role": "assistant", "content": answer})

    if usage:
        total_prompt_tokens += usage.prompt_tokens
        total_completion_tokens += usage.completion_tokens
        print(f"(本轮 tokens：输入 {usage.prompt_tokens} / 输出 {usage.completion_tokens}"
              f"　累计：{total_prompt_tokens + total_completion_tokens})")

    return answer


# ---------------------------------------------------------------------------
# 4. 辅助功能
# ---------------------------------------------------------------------------
HELP_TEXT = """可用指令：
    退出 / 再见 / exit   结束聊天
    帮助                 显示这份说明
    历史                 看看记忆盒子里存了什么
    清空                 清空记忆（人设保留），重新开始聊
直接输入其他内容，就是和 AI 聊天。"""


def show_history():
    print(f"记忆盒子里现在有 {len(memoryBox)} 条记录：")
    for i, m in enumerate(memoryBox, start=1):
        text = m["content"].replace("\n", " ")
        if len(text) > 40:
            text = text[:40] + "..."
        print(f"    {i:>2}. [{m['role']:<9}] {text}")


def clear_memory():
    memoryBox.clear()
    memoryBox.append({"role": "system", "content": SYSTEM_PROMPT})
    print("（记忆已清空，人设保留）")


# ---------------------------------------------------------------------------
# 5. 主循环
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 62)
    print("AI 聊天助手（输入 帮助 看指令，输入 退出 结束）")
    print("=" * 62)

    while True:                                  # 第 05 课的 while 循环
        try:
            text = input("\n你：").strip()        # 第 06 课 input() + 第 07 课 strip()
        except (EOFError, KeyboardInterrupt):
            print("\n（已退出）")
            break

        if text == "":
            continue

        if text in ("退出", "再见", "exit", "quit"):
            print(f"AI：再见！这轮聊了 {round_no} 个回合，"
                  f"累计消耗 {total_prompt_tokens + total_completion_tokens} tokens。")
            break

        if text == "帮助":
            print(HELP_TEXT)
            continue

        if text == "历史":
            show_history()
            continue

        if text == "清空":
            clear_memory()
            continue

        round_no += 1
        print("AI：", end="", flush=True)
        ask(text)
