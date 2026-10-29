"""
12. 多轮对话记忆功能的实现

老师给的两步思路：
    1. 我们可以定义一个记忆盒子，将我们的问题和AI回复的内容都保存到里面去
    2. 当我们与AI进行交互时，直接让AI先读取之前的对话记录，然后再来回答问题

上一节（11）我们看到问题：不带历史，模型就"失忆"。
这一节把"记忆盒子"做出来 —— 代码改动其实非常小，只有 4 处：

    · 多一个列表         memoryBox = []
    · 提问前，把问题放进去 memoryBox.append({"role": "user", ...})
    · 调用时传整个记忆盒子  messages=memoryBox       （而不是只传当前这一句）
    · 拿到回答后，把回答也放进去 memoryBox.append({"role": "assistant", ...})

老师原版：智谱 ZhipuAI + function_fn(prompt) + memoryBox
本版    ：DeepSeek + .env，结构完全一致

运行：python 03.多轮对话记忆功能的实现.py
"""

import os
import sys

# Windows 控制台默认 GBK，防 emoji 崩
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# ---------------------------------------------------------------------------
# 1. 创建客户端
# ---------------------------------------------------------------------------
load_dotenv(override=True)
api_key = os.environ.get("DEEPSEEK_API_KEY")

if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请先运行 python day01/07.校验环境变量配置是否成功.py")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"密钥里有中文字符（当前值：{api_key}），请检查 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ---------------------------------------------------------------------------
# 2. 定义一个记忆盒子
#    它就是一个普通的列表，里面按顺序存对话：
#        [{"role": "user", "content": "..."},
#         {"role": "assistant", "content": "..."},
#         {"role": "user", "content": "..."}, ...]
# ---------------------------------------------------------------------------
memoryBox = []

usage_log = []      # 顺手记录每轮消耗的 token，用来观察"历史越长越贵"


# ---------------------------------------------------------------------------
# 3. 定义一个与AI交互的函数
# ---------------------------------------------------------------------------
def function_fn(prompt):
    # 参数中的这个 prompt 就是我们用户的提示词(问题)
    # 我们需要将这个问题添加到记忆盒子中去
    memoryBox.append({"role": "user", "content": prompt})

    # 当我们与AI进行交互的时候，直接就将这个记忆盒子给AI读取
    res = client.chat.completions.create(
        model=MODEL,
        messages=memoryBox,
    )

    answer = res.choices[0].message.content
    usage_log.append(res.usage)

    # AI 的回答也要放进记忆盒子。
    # 少了这一步，模型下次只记得"我问过什么"，却不记得"它自己答过什么"，
    # 对话就接不上了（这是最容易漏的一行）。
    memoryBox.append({"role": "assistant", "content": answer})

    # 将AI的回复消息返回出去
    return answer


# ---------------------------------------------------------------------------
# 4. 主程序
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 62)
    print("第 1 轮对话")
    print("=" * 62)
    print("我：我是张三，我喜欢吃苹果")
    print("AI：", function_fn("我是张三，我喜欢吃苹果"))

    print()
    print("=" * 62)
    print("第 2 轮对话（对比上一节：这次应该答得出来）")
    print("=" * 62)
    print("我：我是谁？我喜欢什么？")
    print("AI：", function_fn("我是谁？我喜欢什么？"))

    print()
    print("=" * 62)
    print("第 3 轮：换个话题，再回头问一次")
    print("=" * 62)
    print("我：推荐一种适合当早餐的水果")
    print("AI：", function_fn("推荐一种适合当早餐的水果"))
    print()
    print("我：那我是谁来着？")
    print("AI：", function_fn("那我是谁来着？"))
    print("（聊了别的话题，它依然记得你叫张三 —— 因为记忆盒子一直在带着）")

    # -----------------------------------------------------------------------
    # 看看记忆盒子里现在装了什么
    # -----------------------------------------------------------------------
    print()
    print("=" * 62)
    print(f"记忆盒子现在装了 {len(memoryBox)} 条记录")
    print("=" * 62)
    for i, m in enumerate(memoryBox, start=1):
        text = m["content"].replace("\n", " ")
        print(f"  {i}. [{m['role']:<9}] {text[:34]}{'...' if len(text) > 34 else ''}")

    # -----------------------------------------------------------------------
    # 重要观察：历史越长，越贵
    # -----------------------------------------------------------------------
    print()
    print("=" * 62)
    print("每轮的 token 消耗（注意输入那一列）")
    print("=" * 62)
    for i, u in enumerate(usage_log, start=1):
        print(f"  第 {i} 轮：输入 {u.prompt_tokens:>4}  /  输出 {u.completion_tokens:>4}")
    print()
    print("  看出来了吗：输入的 token 一轮比一轮多。")
    print("  因为每一轮都要把「之前所有对话」重新发一遍 —— 这就是记忆的代价。")
    print("  聊得越久越贵，到一定程度还会超出模型的上下文长度限制。")

    # -----------------------------------------------------------------------
    # 优化思路：只保留最近几轮
    # -----------------------------------------------------------------------
    print()
    print("=" * 62)
    print("优化思路：记忆盒子别无限长大，只留最近几轮")
    print("=" * 62)

    def trim_memory(memory, keep_rounds=3):
        """只保留最近的 keep_rounds 轮对话（1 轮 = 1 问 + 1 答，共 2 条）。
        如果有 system 人设消息，要单独拿出来放在最前面，不能一起截掉。"""
        return memory[-keep_rounds * 2:]

    print(f"  当前 {len(memoryBox)} 条 → 只留最近 3 轮（6 条）后：{len(trim_memory(memoryBox))} 条")
    print("  真实项目里的做法：设一个上限，超了就丢掉最老的，或者把老对话压缩成一句摘要。")

    # -----------------------------------------------------------------------
    # 想不想真的"聊天"？把下面的开关改成 True 就是交互式聊天（会一直等你输入）
    # -----------------------------------------------------------------------
    CHAT_MODE = False

    if CHAT_MODE:
        print()
        print("=" * 62)
        print("交互式聊天（输入 再见 或 exit 退出）")
        print("=" * 62)
        while True:                                   # 第 07 课学的 while 循环
            question = input("你：")
            if question.strip() in ("再见", "exit", "quit", ""):
                print("AI：再见！和你聊天很开心。")
                break
            print("AI：", function_fn(question))
