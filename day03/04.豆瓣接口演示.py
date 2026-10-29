"""
豆瓣电影「前端内部接口」演示（无需 API Key）

接口地址：
    https://movie.douban.com/j/search_subjects?type=movie&tag=热门&page_limit=10

参数说明：
    type        movie（电影）/ tv（电视剧）
    tag         分类标签：热门、最新、经典、豆瓣高分、动作、喜剧、科幻…
    page_limit  每页多少条
    page_start  从第几条开始（分页用，不写默认 0）

⚠️ 实测踩到的坑（本机 2026-10-26）：
    1. 不带 User-Agent 直接请求 → 豆瓣返回 HTTP 418（I'm a teapot，反爬）
       带上浏览器 UA + Referer 之后 → 200 正常
    2. json.loads(res) 会报错 —— res 是 Response 对象，不是字符串
       正确写法：res.json()  或者 json.loads(res.text)
    3. 中文 tag 直接拼在 URL 里是可以的（requests 会自动做 URL 编码）

运行：python 04.豆瓣接口演示.py     （会依次问你三个问题）
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

import json
import requests

# 2.设置接口请求头，防止豆瓣接口直接拒绝我的请求
DOUBAN_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
    "Referer": "https://movie.douban.com/",
}


# ---------------------------------------------------------------------------
# 辅助：先问一下豆瓣有哪些标签，省得用户瞎猜
# ---------------------------------------------------------------------------
def get_tags(kind="movie"):
    """GET https://movie.douban.com/j/search_tags?type=movie"""
    try:
        r = requests.get("https://movie.douban.com/j/search_tags",
                         params={"type": kind}, headers=DOUBAN_HEADERS, timeout=10)
        return r.json().get("tags", [])
    except Exception:
        return []


# ---------------------------------------------------------------------------
# 主函数：按类型 + 标签查片单（老师课堂上那个函数，补了错误处理）
# ---------------------------------------------------------------------------
def get_movie_data(type, tag, limit):
    """返回片单列表；出问题时返回空列表并打印原因。

    注意：这个函数的参数叫 type，会把内置的 type() 遮住，
          所以下面取异常类型时只能用 exc.__class__.__name__，
          不能写 type(exc) —— 那样会报 'str' object is not callable。
    """
    # 拼接完整的 url（老师的写法）
    douban_api = (f"https://movie.douban.com/j/search_subjects"
                  f"?type={type}&tag={tag}&page_limit={limit}")

    print(douban_api)

    try:
        res = requests.get(douban_api, headers=DOUBAN_HEADERS, timeout=10)
        res.raise_for_status()          # 4xx / 5xx 直接抛异常，比手动判断状态码干净
    except requests.RequestException as exc:
        print("请求失败：", exc.__class__.__name__, exc)
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status == 418:
            print("      418 = 被豆瓣反爬拦了，检查 DOUBAN_HEADERS 里的 User-Agent")
        return []

    # 老师注释里那行 json.loads(res)["subjects"] 会报错（res 不是字符串），
    # 正确写法是 res.json() 或 json.loads(res.text)
    results = res.json().get("subjects", [])
    return results


def show_table(movies, limit_hint=""):
    """把结果打印成表格，看着舒服点"""
    if not movies:
        print("（没有查到数据）")
        return
    print()
    print(f"{'排名':<5}{'评分':<7}{'片名'}")
    print("-" * 60)
    for i, m in enumerate(movies, start=1):
        score = m.get("rate") or "暂无"
        print(f"{i:<5}{score:<8}{m.get('title')}")
    print("-" * 60)
    print(f"共 {len(movies)} 条{limit_hint}")


if __name__ == "__main__":
    # 老师课堂上的三步提问
    kind = input("请选择电影或电视剧：【movie/tv】").strip() or "movie"
    tag = input("请选择电影或电视剧的分类标签（如「热门」、「喜剧」、「科幻」等）").strip() or "热门"
    limit = input("请选择要查询的数据量：【10、50、100】").strip() or "10"

    # 先亮出豆瓣支持的标签，方便对照（老师原版没有这一步）
    tags = get_tags(kind)
    if tags:
        print()
        print("豆瓣支持的标签：", "、".join(tags))
        print()

    movies = get_movie_data(kind, tag, limit)
    show_table(movies, f"（type={kind}, tag={tag}）")

    # -----------------------------------------------------------------------
    # 补充：把"查片单"做成 Agent 的工具 —— 这就是 Agent 查电影的雏形
    # -----------------------------------------------------------------------
    print()
    print("=" * 66)
    print("补充：把它做成 Agent 的工具，让模型自己查电影")
    print("=" * 66)

    import os
    from dotenv import load_dotenv
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool

    load_dotenv(override=True)
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("（没有读到 DEEPSEEK_API_KEY，跳过补充部分）")
        raise SystemExit(0)

    llm = ChatOpenAI(
        model="deepseek-flash",
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
        temperature=0,
    )

    @tool(description="按类型和标签查询豆瓣影视片单。type 取 movie 或 tv，tag 如 热门/经典/喜剧/科幻")
    def search_movies(type: str, tag: str, limit: int = 5) -> str:
        """返回片单的 JSON 字符串（片名 + 评分 + 链接）"""
        rows = get_movie_data(type, tag, limit)
        brief = [{"title": m.get("title"), "rate": m.get("rate"), "url": m.get("url")}
                 for m in rows]
        return json.dumps(brief, ensure_ascii=False)

    agent = create_agent(model=llm, tools=[search_movies])

    question = "豆瓣上评分最高的经典电影有哪些？给我推荐 3 部，带评分。"
    print("问：", question)
    result = agent.invoke({"messages": [("user", question)]})

    for m in result["messages"]:
        role = getattr(m, "type", "?")
        if role == "ai" and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                print(f"    [ai 调工具] {tc['name']}({tc['args']})")
    print()
    print("答：", result["messages"][-1].content)

    print()
    print("=" * 66)
    print("提醒")
    print("=" * 66)
    print("""  这类"前端内部接口"能用来学习，但要注意：
    · 不是官方承诺的接口，随时可能失效或被拦（418 就是例子）
    · 有隐式限流，别高频猛刷
    · 只做个人学习/轻量查询，别做批量采集或商用
  稳定性要求高的话，用官方 API 或第三方正规接口（见同目录的参考清单）。""")
