"""
11. 多轮对话的问题

注意标题 —— 这一节不是教你怎么"实现"多轮对话，而是先让你**亲眼看到问题**：

    第 1 次问：我是张三，我喜欢吃苹果
    第 2 次问：我是谁？我喜欢什么？
    模型答不上来 —— 因为它压根不记得第 1 次说过什么。

为什么？因为每调用一次接口，都是"独立的一次请求"：
你发过去的 messages 里有什么，模型就看到什么。上一次的对话没有带上，它就看不见。

    所以：**大模型本身没有记忆，记忆是我们自己在代码里维护的。**

（下一节才讲怎么把历史带上，这一节先把这个坑挖明白。）

老师原版：智谱 ZhipuAI + os.getenv("zhipuai_api_key")，用 function_fn() 封装对话
本版    ：DeepSeek + .env，同样用一个函数把"对话"封装起来

运行：python 02.多轮对话的问题.py
"""

import os
import sys

# Windows 控制台默认 GBK，防 emoji 崩
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# 创建客户端
load_dotenv(override=True)                      # 把 .env 读进环境变量
api_key = os.environ.get("DEEPSEEK_API_KEY")    # 老师用的是 os.getenv("zhipuai_api_key")，同一招

if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请先运行 python day01/07.校验环境变量配置是否成功.py")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"密钥里有中文字符（当前值：{api_key}），请检查 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# ---------------------------------------------------------------------------
# 使用函数封装大模型对话功能
# （函数名沿用老师的 function_fn；真实项目里建议起个有意义的名字，比如 ask / chat）
# 注意看：这个函数只接收一句 prompt，每次调用都是"从头开始"的一次对话。
# ---------------------------------------------------------------------------
def function_fn(prompt):
    # 在这个函数中与AI模型进行交互
    res = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    # 将AI的回复消息返回出去
    return res.choices[0].message.content


# ---------------------------------------------------------------------------
# if __name__ == "__main__": 是什么意思？
# 只有"直接运行这个文件"时，下面的代码才会执行；
# 如果这个文件被别的文件 import 进去，下面的代码就不执行。
# 作用：把"功能（函数）"和"测试/演示代码"分开。
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 编写提示词
    p1 = "我是张三，我喜欢吃苹果"
    p2 = "我是谁？我喜欢什么？"

    print("=" * 60)
    print("第 1 次对话")
    print("=" * 60)
    print("我：", p1)
    print("AI：", function_fn(p1))

    print()
    print("=" * 60)
    print("第 2 次对话（只发这一句，没带上面的历史）")
    print("=" * 60)
    print("我：", p2)
    print("AI：", function_fn(p2))
    print()
    print("↑ 看到问题了吗：它不知道你是谁，也不知道你喜欢什么。")
    print("  因为第 2 次请求里只有「我是谁？我喜欢什么？」这一句，")
    print("  第 1 次说的「我是张三，我喜欢吃苹果」根本没发过去。")

    # -----------------------------------------------------------------------
    # 验证一下：把历史一起发过去，它就答得出来了
    # 做法：messages 里按顺序放上 [第一句] [它的回答] [第二句]
    # 这正是下一节要做的事 —— 自己维护一个 messages 列表
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("对照实验：把历史一起带上再问一次")
    print("=" * 60)

    history = [
        {"role": "user", "content": p1},
        {"role": "assistant", "content": "你好，张三！很高兴认识你，苹果是很健康的水果。"},
        {"role": "user", "content": p2},
    ]
    res = client.chat.completions.create(model=MODEL, messages=history)
    print("我：", p2)
    print("AI：", res.choices[0].message.content)
    print()
    print("↑ 这次答对了。区别只有一个：messages 里多放了前面两轮内容。")

    print()
    print("=" * 60)
    print("小结")
    print("=" * 60)
    print("  模型不会自己记住上一句话 —— 每次请求都要把「历史」重新发过去。")
    print("  所以我们要在代码里维护一个 messages 列表：")
    print("      用户问一句 → 追加进去")
    print("      模型答一句 → 也追加进去")
    print("      下次提问时，把这个列表整个发过去")
