"""
ReAct 是 智能体的一个框架，里面是对Functioncalling技术进行了一层封装
如何使用？

1.在终端下载依赖包
    pip install langchain langchain-openai langchain-community langchain-core
"""

# ===========================================================================
# 本机实测版本（2026-10）：langchain 1.4.7 / langchain-core 1.7.0 /
#                        langchain-openai 1.7.2 / langgraph 1.2.17
#
# ⚠️ 版本差异（网上老教程八成对不上）：
#   ① 2023~2024 老教程：from langchain.agents import initialize_agent, AgentExecutor
#      —— 已归到 langchain_classic，别照抄
#   ② 中期写法：from langgraph.prebuilt import create_react_agent
#      —— 能用，但会打印弃用警告（提示改用 langchain.agents.create_agent）
#   ③ 现在（langchain 1.x，老师用的也是这个）：from langchain.agents import create_agent
#
# 一句话理解 ReAct：
#   ReAct = Reasoning + Acting。模型自己循环：
#       想 → 决定调哪个工具 → 看工具结果 → 再想 → 直到能回答为止。
#   上一节手写的 function calling 只是这个循环里的一圈，LangChain 把"转几圈"封装了。
#
# ⚠️ 老师代码里的一个 bug（本文件已修正，见第 3 步注释）：
#   两个工具函数都写了 num*num 却没有 return，
#   实测工具会返回 None，agent 拿不到结果，最后卡住/超时报错。
#
# 运行：python 03.ReAct的使用.py
# ===========================================================================

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# 1.导包
import os

# 使用langchain来创建Agent智能体
from langchain.agents import create_agent
# 使用聊天大模型，类似于 智普AI、openai、qwen、deepseek...
from langchain_openai import ChatOpenAI
# 使用工具函数列表
from langchain_core.tools import tool

from dotenv import load_dotenv

load_dotenv(override=True)          # 把 .env 读进环境变量，下面 os.getenv 才拿得到


# 2.定义一个大模型 => langchain语法
llm = ChatOpenAI(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),     # 注意：这个 api_key 需要我们从环境变量中获取
    base_url=os.getenv("DEEPSEEK_BASE_URL"),   # 注意：这个 base_url 也需要我们从环境变量中获取
    temperature=0,                             # 补充：温度 0，工具调用更稳定
)


# 3.我们定义一个工具，这个工具就是一个函数
# 定一个计算一个整数的平方的工具函数
@tool(description="计算一个整数的平方")
def square_num(num: int) -> int:
    print("    [工具被调用] 计算平方")
    # 计算一个整数的平方
    return num * num          # ★ 老师原版这里写的是 num*num（少了 return），
                              #   实测那样函数会返回 None，agent 拿不到结果就会卡死


# 定一个计算一个整数的立方的工具函数
@tool(description="计算一个整数的立方")
def cube_num(num: int) -> int:
    print("    [工具被调用] 计算立方")
    # 计算一个整数的立方
    return num * num * num    # ★ 同上：必须有 return


# 4.定义一个工具列表，工具列表中存放的是函数
tools = [square_num, cube_num]

# 5.创建一个智能体
agent = create_agent(
    model=llm,        # 设置我们定义的模型
    tools=tools,      # 智能体能用的工具箱
)


# 6.执行这个智能体
print("=" * 66)
print("问：计算12的平方是多少？")
print("=" * 66)
results = agent.invoke({
    "messages": [("user", "计算12的平方是多少？")]
})

# 7.输出这个结果
print("答：", results["messages"][-1].content)


# ===========================================================================
# 补充 A：把 ReAct 的"循环过程"打印出来 —— 一眼看懂它转了几圈
# ===========================================================================
print()
print("=" * 66)
print("补充 A：看看 ReAct 内部到底发生了什么")
print("=" * 66)


def ask_and_show(question: str):
    print("问：", question)
    result = agent.invoke({"messages": [("user", question)]})
    for m in result["messages"]:
        role = getattr(m, "type", "?")
        if role == "ai" and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                print(f"    [ai 思考] 我要调用 {tc['name']}({tc['args']})")
        content = getattr(m, "content", None)
        if content:
            print(f"    [{role}] {str(content).replace(chr(10), ' ')[:160]}")
    print()


ask_and_show("计算 7 的立方是多少？")
ask_and_show("先算 3 的平方，再算 4 的立方，两个结果相加等于多少？")


# ===========================================================================
# 补充 B：工具箱里加一个"查天气"的工具，看模型会不会自己挑对工具
#   —— 这才是 Agent 真正的样子：工具不止一个，用哪个由模型决定
# ===========================================================================
print("=" * 66)
print("补充 B：工具箱里再加一个天气工具，模型自己挑")
print("=" * 66)

import json
import requests

AMAP_KEY = os.getenv("AMAP_KEY", "")
AMAP_URL = "https://restapi.amap.com/v3/weather/weatherInfo"


@tool(description="查询中国某个城市的实时天气")
def get_current_weather(city: str) -> str:
    """需要实时天气时必须调用它，不要凭空猜。"""
    if not AMAP_KEY:
        return json.dumps({"error": "没有配置 AMAP_KEY"}, ensure_ascii=False)
    try:
        raw = requests.get(f"{AMAP_URL}?key={AMAP_KEY}&city={city}&extensions=base", timeout=10).text
        data = json.loads(raw)
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return json.dumps({"error": type(exc).__name__}, ensure_ascii=False)
    if data.get("status") != "1":
        return json.dumps({"error": data.get("info", "查询失败")}, ensure_ascii=False)
    lives = data.get("lives") or []
    if not lives:
        return json.dumps({"error": f"没有查到 {city}"}, ensure_ascii=False)
    w = lives[0]
    return json.dumps(
        {"location": city, "temperature": w["temperature"],
         "weather": w["weather"], "time": w["reporttime"]},
        ensure_ascii=False,
    )


# 把天气工具也塞进工具箱，重建一个智能体
agent2 = create_agent(model=llm, tools=[square_num, cube_num, get_current_weather])

print()
result = agent2.invoke({"messages": [("user", "长沙现在天气怎么样？")]})
for m in result["messages"]:
    role = getattr(m, "type", "?")
    if role == "ai" and getattr(m, "tool_calls", None):
        for tc in m.tool_calls:
            print(f"    [ai 思考] 我要调用 {tc['name']}({tc['args']})")
    content = getattr(m, "content", None)
    if content and role == "tool":
        print(f"    [tool] {content}")
print("答：", result["messages"][-1].content)

print()
print("=" * 66)
print("小结")
print("=" * 66)
print("""  手工版（02）：自己写 tools 的 JSON、自己处理 tool_calls、自己发第二次请求
  框架版（03）：@tool 装饰器 + create_agent，循环交给框架

  ReAct 的价值在那个"循环"：
     想 → 调一个工具 → 看结果 → 还想再调一个 → 直到够答为止
  "先算3的平方再算4的立方然后相加"这种问题，手工版要写死两轮，
  ReAct 会自己转两圈，还会自己把两个结果加起来。

  【注意】别忘了工具函数一定要 return —— 老师那两个函数都漏了，
     实测会返回 None，agent 拿不到结果就卡住超时。""")
