"""
10. langchain 中的 tool 记忆用户信息

前面学过的"记忆"（day02 的 memoryBox）是【短期记忆】：
    把 messages 列表往后传，同一段对话里记得上文；进程一关就全没了。

这一节的记忆是【长期记忆】：
    把数据存进一个 store（仓库），下【一次】调用、甚至下次启动程序都还在。
    做法：工具函数里通过 runtime.store 读写仓库。

老师的代码骨架：

    from langgraph.store.memory import InMemoryStore
    from langchain.agents import create_agent
    from langchain.tools import tool, ToolRuntime

    @tool
    def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
        store = runtime.store
        item = store.get(("users",), user_id)
        return str(item.value) if item else "Unknown user"

    @tool
    def save_user_info(user_id: str, user_info: dict, runtime: ToolRuntime) -> str:
        store = runtime.store
        store.put(("users",), user_id, user_info)
        return "Successfully saved user info."

    store = InMemoryStore()
    agent = create_agent(model, tools=[...], store=store)
    agent.invoke({...保存...})
    agent.invoke({...查询...})

运行：python 10.langchain中的tool记忆用户信息.py
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime        # ToolRuntime：运行时上下文
from langgraph.store.memory import InMemoryStore     # 内存版仓库（进程结束就清空）

load_dotenv(override=True)

MODEL = "deepseek-flash"

llm = ChatOpenAI(
    model=MODEL,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0,
)


# ===========================================================================
# 一、两个工具：一个读仓库，一个写仓库
#
#   注意 runtime 这个参数：它不是给模型看的，模型也不需要填。
#   LangChain 在调用工具时会自动把"运行时上下文"注入进来，
#   里面带着 store、当前消息、用户身份等。
#   （所以 description / 参数说明里不用、也不该提 runtime）
# ===========================================================================
@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """查找用户信息。需要用户 id，例如 abc123。"""
    print(f"    [工具] get_user_info(user_id={user_id!r})")
    store = runtime.store                                  # 拿到仓库
    item = store.get(("users",), user_id)                  # 命名空间("users",) + key=user_id
    return str(item.value) if item else "Unknown user"


@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """保存用户信息。user_id 是用户编号，user_info 是包含 name、age 等字段的字典。"""
    print(f"    [工具] save_user_info(user_id={user_id!r}, user_info={user_info})")
    store = runtime.store
    store.put(("users",), user_id, user_info)              # 存进去
    return "Successfully saved user info."


# ===========================================================================
# 二、建仓库 + 建智能体（关键是 store=store）
# ===========================================================================
store = InMemoryStore()

agent = create_agent(
    llm,
    tools=[get_user_info, save_user_info],
    store=store,                    # ← 把仓库交给智能体，工具里才拿得到 runtime.store
    system_prompt="你是一个用户信息管理助手。需要读或写用户资料时必须调用工具，不要凭空编。",
)


# ===========================================================================
# 三、两个"会话"：验证记忆能跨 invoke 保留
# ===========================================================================
def say(text: str) -> str:
    """发一句话给智能体，打印它调了哪些工具，返回最终回答"""
    result = agent.invoke({"messages": [{"role": "user", "content": text}]})
    for m in result["messages"]:
        role = getattr(m, "type", "?")
        if role == "ai" and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                print(f"    [ai 决定调用] {tc['name']}({tc['args']})")
    return str(result["messages"][-1].content)


if __name__ == "__main__":
    print("=" * 66)
    print("【会话 1】保存用户信息")
    print("=" * 66)
    print("我：保存以下用户：userid: abc123, name: Foo, age: 25")
    print("AI：", say("保存以下用户：userid: abc123, name: Foo, age: 25"))

    print()
    print("=" * 66)
    print("【会话 2】这是一个【全新的 invoke】，看它能不能记住")
    print("=" * 66)
    print("我：查一下 userid abc123 的信息")
    print("AI：", say("查一下 userid abc123 的信息"))

    print()
    print("=" * 66)
    print("【会话 3】再存一个用户，然后一次查两个")
    print("=" * 66)
    print("我：再保存一个用户：userid: xyz789, name: Bar, age: 30")
    print("AI：", say("再保存一个用户：userid: xyz789, name: Bar, age: 30"))
    print()
    print("我：abc123 和 xyz789 分别是谁？")
    print("AI：", say("abc123 和 xyz789 分别是谁？"))

    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("【直接看仓库里有什么】")
    print("=" * 66)
    for key in ("abc123", "xyz789"):
        item = store.get(("users",), key)
        print(f"  {key}: {item.value if item else '（无）'}")

    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("小结：两种记忆的区别")
    print("=" * 66)
    print("""  ┌────────────┬──────────────────────────┬──────────────────────────┐
  │            │ 短期记忆（messages）        │ 长期记忆（store）          │
  ├────────────┼──────────────────────────┼──────────────────────────┤
  │ 存在哪      │ messages 列表（对话历史）   │ store 仓库（键值存储）      │
  │ 活多久      │ 这段对话结束就没了          │ 跨会话、跨程序重启（看实现）│
  │ 谁在用      │ 所有模型调用都带            │ 只有工具里去读写           │
  │ 典型用途    │ 聊天上下文                 │ 用户档案、偏好、知识库      │
  └────────────┴──────────────────────────┴──────────────────────────┘

  【注意】InMemoryStore 是【内存版】：程序一退出就清空。
     要真正持久化，换 Redis / Postgres 版的 store（接口一样，只换实现类）。

  这就解释了为什么"AI 记得你"这件事，其实完全取决于你的程序有没有存、存哪里。""")
