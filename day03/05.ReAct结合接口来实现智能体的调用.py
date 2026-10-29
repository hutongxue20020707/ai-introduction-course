"""
05. ReAct 结合接口来实现智能体的调用

思路（老师的）：
    把两个"接口"都封装成工具，交给 create_agent，
    让模型自己判断用户这句话该调哪个工具：
        · 高德天气接口 → get_current_weather
        · 豆瓣电影接口 → get_movie_data

⚠️ 老师代码里的一个设计问题（本文件已修正，值得记牢）：
    老师把工具写成了「无参数 + 函数内部 input() 取城市」：

        @tool(description="查询城市实时天气，输入中文城市名，例如：北京、上海、长沙")
        def get_current_weather():                 # ← 没有参数
            city = input("请输入你要查询天气的城市：")

    这样在 Agent 里跑不通，三个原因：
      1. 工具是给【程序】调用的，模型只会把参数以 JSON 传给工具；
         函数没有参数 → 模型想传 city 也传不进来。
      2. 函数里的 input() 会阻塞，等你在键盘上敲 —— 无人值守直接 EOFError。
      3. LangChain 靠"参数名 + 类型注解 + docstring"生成参数说明书，
         没参数就等于没有说明书，模型根本不知道要提供城市。

    ✔ 正确写法：要模型提供的值，一律写成【参数 + 类型注解 + docstring】，
      这样模型才知道"调用这个工具要传 city"。

运行：python 05.ReAct结合接口来实现智能体的调用.py
"""

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

import requests
from dotenv import load_dotenv

# 使用langchain来创建Agent智能体
from langchain.agents import create_agent
# 使用聊天大模型
from langchain_openai import ChatOpenAI
# 使用工具函数列表
from langchain_core.tools import tool

load_dotenv(override=True)

MODEL = "deepseek-flash"
AMAP_KEY = os.getenv("AMAP_KEY", "")

# 1.定义大模型
llm = ChatOpenAI(
    model=MODEL,
    api_key=os.getenv("DEEPSEEK_API_KEY"),     # 从环境变量获取
    base_url=os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
    temperature=0,
)

# 2.接口相关配置
DOUBAN_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
    "Referer": "https://movie.douban.com/",
}
AMAP_URL = "https://restapi.amap.com/v3/weather/weatherInfo"


# ===========================================================================
# 工具 1：查天气（高德接口）
#   注意参数 city —— 模型会把用户说的城市填进来
# ===========================================================================
@tool(description="查询中国城市的实时天气，输入中文城市名，例如：北京、上海、长沙")
def get_current_weather(city: str) -> str:
    """调用高德地图 API 查实时天气，返回 JSON 字符串。"""
    if not AMAP_KEY:
        return json.dumps({"error": "没有配置 AMAP_KEY"}, ensure_ascii=False)

    weather_url = f"{AMAP_URL}?key={AMAP_KEY}&city={city}&extensions=base"
    try:
        res = requests.get(weather_url, timeout=10).text
        data = json.loads(res)
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return json.dumps({"error": exc.__class__.__name__}, ensure_ascii=False)

    # 高德失败也返回 HTTP 200，必须看 status
    if data.get("status") != "1":
        return json.dumps({"error": data.get("info", "查询失败")}, ensure_ascii=False)

    lives = data.get("lives") or []
    if not lives:
        return json.dumps({"error": f"没查到 {city} 的天气"}, ensure_ascii=False)

    w = lives[0]
    return json.dumps(
        {"city": w.get("city", city), "weather": w.get("weather"),
         "temperature": w.get("temperature"), "wind": f"{w.get('winddirection')}风 {w.get('windpower')}级",
         "humidity": w.get("humidity"), "reporttime": w.get("reporttime")},
        ensure_ascii=False,
    )


# ===========================================================================
# 工具 2：查影视片单（豆瓣接口）
#   type / tag / limit 三个参数，模型自己从用户话里提取
# ===========================================================================
@tool(description="查询豆瓣影视片单。type 取 movie 或 tv；tag 如 热门/最新/经典/豆瓣高分/动作/喜剧/科幻；limit 为返回条数（默认5）")
def get_movie_data(type: str, tag: str, limit: int = 5) -> str:
    """调用豆瓣 j/search_subjects 接口，返回片名+评分+链接的 JSON 字符串。"""
    douban_api = (f"https://movie.douban.com/j/search_subjects"
                  f"?type={type}&tag={tag}&page_limit={limit}")

    try:
        res = requests.get(douban_api, headers=DOUBAN_HEADERS, timeout=10)
        res.raise_for_status()                      # 检查 HTTP 状态码，4xx/5xx 直接抛异常
    except requests.RequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status == 418:
            return json.dumps({"error": "418 被豆瓣反爬拦了"}, ensure_ascii=False)
        return json.dumps({"error": exc.__class__.__name__}, ensure_ascii=False)

    subjects = res.json().get("subjects", [])       # 获取返回的字段结果
    brief = [{"title": m.get("title"), "rate": m.get("rate"), "url": m.get("url")}
             for m in subjects]
    return json.dumps(brief, ensure_ascii=False)


# ===========================================================================
# 3.智能体
# ===========================================================================
agent = create_agent(
    model=llm,
    tools=[get_current_weather, get_movie_data],     # 工具箱：两个不同来源的接口
)

print("=" * 70)
print("【工具说明书】LangChain 根据参数注解自动生成（模型就是靠这个选工具的）")
print("=" * 70)
for t in (get_current_weather, get_movie_data):
    print(f"· {t.name}")
    print(f"  描述：{t.description}")
    print(f"  参数：{t.args}")
print()


# ===========================================================================
# 4.演示：同一套智能体，看它怎么按问题挑工具
# ===========================================================================
def ask(question: str):
    print("=" * 70)
    print("问：", question)
    print("=" * 70)

    result = agent.invoke({"messages": [("user", question)]})

    for m in result["messages"]:
        role = getattr(m, "type", "?")
        if role == "ai" and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                print(f"    [ai 决定调用] {tc['name']}({tc['args']})")
        if role == "tool":
            print(f"    [接口返回]    {str(m.content)[:160]}")
    print()
    print("答：", result["messages"][-1].content)
    print()


if __name__ == "__main__":
    ask("长沙今天天气怎么样？")
    ask("豆瓣上有哪些值得看的经典电影？给我 3 部，带评分")
    ask("北京天气怎么样？顺便推荐 2 部豆瓣科幻高分片")

    print("=" * 70)
    print("小结")
    print("=" * 70)
    print("""  03 节：一个工具（平方/立方）—— 模型只是"会用工具"
  05 节：多个不同来源的工具（高德/豆瓣）—— 模型要"选对工具、填对参数"

  写工具的三条硬规矩：
    ① 必须有参数 + 类型注解（模型靠它填参数）
    ② docstring / description 写清楚"什么时候用、参数是什么"（模型靠它选工具）
    ③ 绝对不要在工具里用 input()（工具是给程序调用的，不是给人交互的）""")
