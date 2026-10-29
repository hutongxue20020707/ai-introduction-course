"""
什么是function calling ?
Function calling 是2023年的时候OpenAI 实现的技术
作用：赋予AI大模型具有调用外部工具的能力（扩展模型的技能）
functioncalling又叫做functioncall, 工具调用, 函数调用
"""

# ===========================================================================
# 【function calling 的工作流程】（老师课上那张 functioncalling流程图.png）
#
#   ① 用户提问："今天长沙的天气怎么样？"
#         │
#         ▼
#   ┌──────────────┐   ② messages + tools    ┌──────────────┐
#   │  你的程序    │ ──────────────────────> │  AI 服务器   │
#   │  (python)    │ <────────────────────── │  (DeepSeek)  │
#   └──────────────┘   response(tool_calls)  └──────────────┘
#         │
#         │ ③ 本地执行 get_current_weather(city)
#         ▼
#   ┌────────────────────────┐
#   │ 高德天气接口（真实数据） │  restapi.amap.com/v3/weather/weatherInfo
#   └────────────────────────┘
#         │  拿到 {"location":"长沙","temperature":"18",...}
#         │ ③ 按 role="tool" + tool_call_id 回填进 messages
#         ▼
#   ┌──────────────┐  messages（含工具结果）  ┌──────────────┐
#   │  你的程序    │ ──────────────────────> │  AI 服务器   │
#   │              │ <────────────────────── │              │
#   └──────────────┘   response（自然语言）   └──────────────┘
#         │
#         ▼
#   ④ 显示给用户："长沙今天阴，18℃，体感偏凉…"
#
#   文字版流程图见同目录的 functioncalling流程图.md
#
# ---------------------------------------------------------------------------
# 老师这一版的关键变化（和上一版对比着看）：
#
#   上一版：json.loads(res)["lives"][0] → print(整个字典)
#   这一版：先抽 4 个字段 → 组装成小字典 → json.dumps(..., ensure_ascii=False)
#           → 返回 JSON 字符串，交给大模型
#
# 为什么要抽字段？
#   高德返回十来项（province/adcode/humidity/windpower…），
#   模型其实只需要时间、地点、天气、温度。给得越干净，它越不容易说错，
#   而且 token 更省。
#
# 为什么一定要 json.dumps？
#   function calling 里 tool 的 content 必须是【字符串】，
#   不能直接塞字典。ensure_ascii=False 是为了别把中文变成 \u6b63\u6c5f 这种转义。
#
# 运行：python 02.functioncalling.py     （会提示你输入城市名）
# ===========================================================================

# 导包
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

import json          # python发送请求返回json格式的数据
import requests      # 发送请求
from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# 创建客户端
load_dotenv(override=True)                 # 会自动往上找到项目根目录的 .env
api_key = os.environ.get("DEEPSEEK_API_KEY")
AMAP_KEY = os.environ.get("AMAP_KEY", "")

if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 请求查询天气接口地址(高德地图)
AMAP_URL = "https://restapi.amap.com/v3/weather/weatherInfo"


# ---------------------------------------------------------------------------
# 调用高德地图API接口查询天气
# ---------------------------------------------------------------------------
def get_current_weather(city):
    """查询城市天气，返回 JSON 字符串（只包含我们真正需要的 4 个字段）。"""
    if not AMAP_KEY:
        return json.dumps({"error": "没有配置 AMAP_KEY"}, ensure_ascii=False)

    # 拼接完整的url
    weather_url = f"{AMAP_URL}?key={AMAP_KEY}&city={city}&extensions=base"

    # 利用网络发送请求
    try:
        res = requests.get(weather_url, timeout=10).text
    except requests.RequestException as exc:
        return json.dumps({"error": f"请求失败：{type(exc).__name__}"}, ensure_ascii=False)

    # 保险 1：高德失败时也返回 HTTP 200，必须看 status
    try:
        data = json.loads(res)
    except json.JSONDecodeError:
        return json.dumps({"error": "返回的不是 JSON"}, ensure_ascii=False)

    if data.get("status") != "1":
        return json.dumps({"error": data.get("info", "查询失败")}, ensure_ascii=False)

    # 保险 2：lives 可能是空列表，直接 [0] 会 IndexError
    lives = data.get("lives") or []
    if not lives:
        return json.dumps({"error": f"没有查到 {city} 的天气数据"}, ensure_ascii=False)

    # 利用网络请求返回的结果，获取我们真正想要的数据
    results = lives[0]
    # print(results)          # ← 整个字典长这样（上一版就是直接把它交给模型）

    # 将我们需要的数据抽取出来
    weather_info = {
        "location": city,
        "temperature": results["temperature"],
        "weather": results["weather"],
        "time": results["reporttime"],
    }

    # 把 weather_info 字典转换成json格式的字符串，交给AI大模型
    return json.dumps(weather_info, ensure_ascii=False)


# 定义一个列表，用于保存用户和系统对话消息
messages = []


# ---------------------------------------------------------------------------
# 第二部分（补充）：把这个函数做成工具交给模型 = 真正的 function calling
#
# 准备一个 tools => 工具箱列表
# ---------------------------------------------------------------------------
tools = [                                       # 工具箱列表
    {
        "type": "function",                     # 工具的类型：是一个函数
        "function": {                           # 函数的详细描述
            "name": "get_current_weather",      # 外部函数的名称
            "description": "获取当前天气",       # 外部函数的详细描述信息
            "parameters": {                     # 外部函数的参数
                "type": "object",               # 参数的数据类型是 Object 类型
                "properties": {                 # 外部函数参数的属性
                    "city": {
                        "type": "string",       # 外部函数参数的数据类型
                        "description": "城市名称, 如: 长沙, 北京",   # 外部函数参数的详细描述信息
                    }
                },
                "required": ["city"],           # 外部函数参数的必填项
            },
        },
    }
]


def chat(question: str) -> str:
    """问模型 → 它说要调工具 → 本地执行 → 结果回填 → 它总结成人话"""
    dialog = list(messages)                      # 复制一份，别把全局列表改脏
    dialog.append({"role": "user", "content": question})

    # 与AI大模型交互
    res = client.chat.completions.create(
        model=MODEL,
        messages=dialog,
        tools=tools,                             # AI大模型可以使用的工具箱
        extra_body={"thinking": {"type": "disabled"}},
    )

    msg = res.choices[0].message

    if not msg.tool_calls:
        return msg.content or "（模型没有回答）"

    print("   模型决定调用工具：")
    for tc in msg.tool_calls:
        print(f"      name    ：{tc.function.name}")
        print(f"      arguments：{tc.function.arguments}")

    # 再次追加message消息内容的时候，需要添加一个 model_dump()
    # （把 SDK 对象转成普通字典再放进列表，后面序列化才不会出问题）
    dialog.append(msg.model_dump())

    # 取出返回结果中需要的字段对应的值
    # 注意：老师课堂上只处理了 tool_calls[0]（一次调用一个城市）；
    #       这里用 for 循环，模型一次要调 3 个城市也能全处理。
    for tc in res.choices[0].message.tool_calls:
        tool_call_id = tc.id                                # 工具id
        role = "tool"                                       # 角色
        name = tc.function.name                             # 工具名称
        args = json.loads(tc.function.arguments)
        content = get_current_weather(args.get("city", "")) # 查询天气返回值

        print(f"      → 执行 {name}  返回：{content}")

        dialog.append({
            "role": role,
            "tool_call_id": tool_call_id,
            "name": name,          # 老师写法里带了 name；DeepSeek/OpenAI 都接受。
                                   # 如果换成某些严格兼容的服务报 400，把 name 去掉即可
            "content": content,
        })

    # 第二次与AI交互：模型拿着工具结果，组织成人话
    res2 = client.chat.completions.create(
        model=MODEL,
        messages=dialog,
        tools=tools,
        extra_body={"thinking": {"type": "disabled"}},
    )
    return res2.choices[0].message.content or "（模型没有回答）"


if __name__ == "__main__":
    location = input("请输入你要查询天气的城市：")

    # ---------- 第一部分：老师课堂上的写法（把函数跑通，看看它返回什么）----------
    print()
    print("=" * 66)
    print(f"【第一部分】直接调用查询天气函数：{location}")
    print("=" * 66)
    result_text = get_current_weather(location)
    print("返回的 JSON 字符串：")
    print("   ", result_text)
    print("ensure_ascii=False 的效果（中文原样输出）；换成 True 会变成：")
    print("   ", json.dumps(json.loads(result_text), ensure_ascii=True))

    # 老师那几句：准备对话消息
    messages.append({"role": "system", "content": "你是一个天气预报小助手，需要根据用户的地址查询当地的天气"})
    messages.append({"role": "user", "content": location})

    # ---------- 第二部分：把函数交给模型，让它自己决定什么时候调 ----------
    print()
    print("=" * 66)
    print(f"【第二部分】让大模型调用这个工具：{location}今天天气怎么样？")
    print("=" * 66)
    print("答：", chat(f"{location}今天天气怎么样？"))

    print()
    print("=" * 66)
    print("【第二部分续】那北京和上海呢？（看看模型会不会拆成两次调用）")
    print("=" * 66)
    print("答：", chat("那北京和上海呢？"))

    print()
    print("=" * 66)
    print("小结")
    print("=" * 66)
    print("""  函数的返回值 → 只留 4 个字段，并 json.dumps 成字符串
  模型的 tool_calls → 告诉你调谁、传什么参数
  你的程序 → 真正去请求高德，再把 JSON 字符串回填给模型
  → 模型负责说，程序负责动手，这才是 function calling。""")
