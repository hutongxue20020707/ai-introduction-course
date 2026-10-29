"""
09. langchain 的 Message 消息

老师课堂上的写法：用【消息对象】而不是字典

    messages = [
        SystemMessage("你是一个文学小说智能小助手"),        # 设置系统消息背景
        HumanMessage("请帮我统计中文最受欢迎的10部经典文学小说…")  # 设置用户提问消息
    ]

    res = llm.stream(messages)                            # 使用大模型的流式输出

    for chunk in res:                                     # 循环输出回复
        print(chunk.content, end="")

到这一节，LangChain 里表示"一条消息"的方式已经有三种了：
    ① 字符串                   "你好"
    ② 元组                     ("user", "你好")
    ③ 字典                     {"role": "user", "content": "你好"}
    ④ 消息对象（本节）           HumanMessage("你好")

它们是等价的，只是越往后信息越完整、越适合做复杂逻辑。

运行：python 09.langchain的Message消息.py
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI                       # 使用ChatOpenAI来创建模型

# 本节的主角：四种消息类
from langchain_core.messages import (                          # 消息对象的工厂
    SystemMessage,      # 系统消息：定人设、定规则
    HumanMessage,       # 人类消息：用户的提问
    AIMessage,          # AI 消息：模型之前的回答（多轮对话塞历史用）
    ToolMessage,        # 工具消息：function calling 里工具返回的结果
)

load_dotenv(override=True)

# 使用ChatOpenAI来创建模型
llm = ChatOpenAI(
    model="deepseek-flash",                    # 选择对应的模型
    api_key=os.getenv("DEEPSEEK_API_KEY"),     # 从环境变量中获取密钥
    base_url=os.getenv("DEEPSEEK_BASE_URL"),   # 从环境变量中获取 接口地址
)

if __name__ == "__main__":
    # =======================================================================
    # 一、老师课堂上的写法（原样）
    # =======================================================================
    print("=" * 66)
    print("【1】老师的写法：SystemMessage + HumanMessage")
    print("=" * 66)

    # 设置消息内容
    messages = [
        SystemMessage("你是一个文学小说智能小助手"),      # 设置系统消息背景
        HumanMessage("请帮我统计中文最受欢迎的 10 部经典文学小说有哪些？"
                     "用编号列出书名 + 一句话简介，不要展开太多"),  # 设置用户提问消息
    ]

    # 使用大模型的流式输出
    res = llm.stream(messages)

    # 在控制台使用循环输出大模型回复的内容
    print("答：", end="", flush=True)
    for chunk in res:
        print(chunk.content, end="", flush=True)
    print()

    # =======================================================================
    # 二、四种消息类各是什么
    # =======================================================================
    print()
    print("=" * 66)
    print("【2】四种消息类型，对应 day01 学的三种角色")
    print("=" * 66)
    print("""  SystemMessage  人设 / 规则        ==>  {"role": "system",    "content": ...}
  HumanMessage   用户的提问          ==>  {"role": "user",      "content": ...}
  AIMessage      模型之前的回答      ==>  {"role": "assistant", "content": ...}
  ToolMessage    工具调用的返回值    ==>  {"role": "tool",      "content": ...}  （function calling 用）

  四种写法等价（以 user 消息为例）：
      "你好"                                # 字符串（等价于一条 user 消息）
      ("user", "你好")                      # 元组
      {"role": "user", "content": "你好"}    # 字典
      HumanMessage("你好")                  # 消息对象 ★ 本节

  用对象的好处：有属性可以读、可以判断类型，写多轮对话/日志时更清楚。""")

    # 看一眼消息对象的属性
    m = HumanMessage("你好")
    print()
    print("  消息对象的属性：")
    print(f"    type    = {m.type!r}      ← 'human' / 'system' / 'ai' / 'tool'")
    print(f"    content = {m.content!r}")
    print(f"    repr    = {m!r}"[:80])

    # =======================================================================
    # 三、多轮对话：把 AIMessage 也塞回列表里
    # =======================================================================
    print()
    print("=" * 66)
    print("【3】多轮对话：Message 对象怎么'记住上文'")
    print("=" * 66)

    history = [
        SystemMessage("你是一个简洁的助手，回答不超过两句话。"),
        HumanMessage("我叫张三，我在长沙，我喜欢科幻小说"),
    ]
    first = llm.invoke(history)
    print("  第 1 轮  我：我叫张三，我在长沙，我喜欢科幻小说")
    print("          AI：", str(first.content).replace("\n", " ")[:70])

    # 关键：把模型的回答作为 AIMessage 也放进历史
    history.append(AIMessage(first.content))
    history.append(HumanMessage("我是谁？适合看什么书？"))

    second = llm.invoke(history)
    print("  第 2 轮  我：我是谁？适合看什么书？")
    print("          AI：", str(second.content).replace("\n", " ")[:90])
    print()
    print(f"  现在 history 里有 {len(history)} 条消息：")
    for h in history:
        print(f"    [{h.type:<7}] {str(h.content)[:40]}")

    # =======================================================================
    # 四、想批量问？batch 也能收消息列表
    # =======================================================================
    print()
    print("=" * 66)
    print("【4】和 08 节的 batch 组合：一次问多个'带人设'的问题")
    print("=" * 66)

    convs = [
        [SystemMessage("你只回答一个字"), HumanMessage("1+1 等于几")],
        [SystemMessage("你是语文老师"), HumanMessage("「春风又绿江南岸」的'绿'是什么用法")],
    ]
    results = llm.batch(convs)
    for i, r in enumerate(results, start=1):
        print(f"  第{i}个：{str(r.content).replace(chr(10), ' ')[:60]}")

    print()
    print("=" * 66)
    print("小结")
    print("=" * 66)
    print("""  Message 对象 = 消息的"面向对象"写法
    SystemMessage(人设) → HumanMessage(提问) → （模型回 AIMessage）→ 再 HumanMessage…

  多轮对话的秘密仍然是 day01 那一句：
    把历史一条条留住，每次把整个列表发过去。

  什么时候用对象、什么时候用字典？
    · 简单脚本：字典最快、最直观
    · 要做类型判断、拼历史、加 ToolMessage：用对象更省心""")
