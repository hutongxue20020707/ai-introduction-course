"""
06. langchain 的模型调用

老师课堂上最短的一段代码，但它是后面所有东西的地基：

    llm = ChatOpenAI(model=..., api_key=..., base_url=...)
    res = llm.invoke("你的问题")
    print(res.content)

对比一下之前用 openai SDK 的写法（day01）：

    client = OpenAI(...)
    res = client.chat.completions.create(model=..., messages=[...])
    print(res.choices[0].message.content)

LangChain 把"取正文"这一步简化成了 res.content，而且返回的是一个
AIMessage 对象（除了正文还带着 token 用量、结束原因等元数据）。

运行：python 06.langchain的模型调用.py     （会提示你输入问题）
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv

# 使用聊天大模型，类似于 智普AI、openai、qwen、deepseek...
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

# ⚠️ 排查小技巧（本机真实踩过）：
#   load_dotenv() 的 .env 是【从当前脚本所在目录往上找】的，不是从"终端当前目录"找。
#   如果 .env 里没读到 DEEPSEEK_BASE_URL，ChatOpenAI 的 base_url 就是 None，
#   请求会默认打到 https://api.openai.com —— 然后报 OpenAITimeoutError，
#   看着像"网络问题"，其实是"配置没读到"。
#   出问题先打印这三个值：
#       print("base_url =", os.getenv("DEEPSEEK_BASE_URL"))
#       print("key      =", (os.getenv("DEEPSEEK_API_KEY") or "")[:8], "...")
#       print("llm.base_url =", getattr(llm, "openai_api_base", None))
print("base_url 读到了：", os.getenv("DEEPSEEK_BASE_URL"))

# ===========================================================================
# 一、老师课堂上的三行（原样）
# ===========================================================================
llm = ChatOpenAI(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),       # 从环境变量获取
    base_url=os.getenv("DEEPSEEK_BASE_URL"),     # 从环境变量获取
)

if __name__ == "__main__":
    prompt = input("请输入你的问题：").strip() or "你是谁呀？"

    # 调用模型
    res = llm.invoke(prompt)

    # 在控制台输出大模型回复的内容
    print()
    print("=" * 66)
    print("res.content（就是回复正文）：")
    print("=" * 66)
    print(res.content)

    # -----------------------------------------------------------------------
    # 补充 1：res 到底是个什么东西？
    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("补充 1：res 是一个 AIMessage 对象，不止有正文")
    print("=" * 66)
    print("类型：", type(res).__name__)
    print("正文：", str(res.content).replace("\n", " ")[:80], "...")

    meta = getattr(res, "response_metadata", None) or {}
    usage = getattr(res, "usage_metadata", None)
    print("模型名：", meta.get("model_name"))
    print("结束原因：", meta.get("finish_reason"))
    if usage:
        print("token 用量：", usage)
    else:
        print("token 用量：", meta.get("token_usage"))

    # -----------------------------------------------------------------------
    # 补充 2：想带"人设 / 多轮历史"怎么办？传 messages 列表
    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("补充 2：带 system 人设 + 多轮历史（和 day01 的 messages 是一回事）")
    print("=" * 66)

    messages = [
        ("system", "你是一个只用三句话回答的助手，回答要口语化。"),
        ("user", prompt),
    ]
    res2 = llm.invoke(messages)
    print(res2.content)

    # -----------------------------------------------------------------------
    # 补充 3：流式输出 —— 用 llm.stream()，一块块取
    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("补充 3：流式输出 llm.stream()（打字机效果，对应 day01 的第 06 课）")
    print("=" * 66)
    for chunk in llm.stream("用两句话介绍你自己"):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print()

    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("小结：LangChain 里调模型就三件事")
    print("=" * 66)
    print("""  ① llm = ChatOpenAI(...)       —— 建客户端（换供应商只改 model/base_url）
  ② res = llm.invoke(...)       —— 发请求（可以传字符串，也可以传 messages 列表）
  ③ res.content                 —— 取正文

  常用的三个方法：
     invoke()   一次性拿完整回答，返回 AIMessage
     stream()   流式，一块块吐（打字机效果）
     batch()    一次发多个问题（批量处理时快很多）

  后面所有东西（工具、ReAct 智能体）都是在这个 llm 上继续搭的。""")
