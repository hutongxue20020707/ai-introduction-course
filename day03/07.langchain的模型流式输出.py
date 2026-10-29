"""
07. langchain 的模型流式输出

老师课堂上的完整代码：

    llm = ChatOpenAI(model=..., api_key=..., base_url=...)
    prompt = input("请输入你的问题：")

    # 使用流式输出大模型的回复内容
    res = llm.stream(
        input=[
            {"role": "system", "content": "你是一个语文老师"},
            {"role": "user", "content": prompt}
        ]
    )

    # 使用迭代器对象，打印每个chunk的内容
    for chunk in res:
        print(chunk.content, end="")

三个关键点：
    ① input 里给的是【消息列表】：system 定人设，user 提问
    ② stream() 返回"迭代器"，for 一次拿一小片（chunk）
    ③ chunk.content 是这一小片的正文，end="" 不换行 → 打字机效果

本文件在老师这几行之外补了四件实测内容：
    · input 的三种写法（字符串 / 元组 / 字典）
    · 同一个问题换不同 system 人设，回答差别有多大
    · 流式 vs 非流式：首字延迟差多少
    · 思考模式会推一堆"空 content"分片 —— 必须跳过

运行：python 07.langchain的模型流式输出.py     （会提示你输入问题）
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # 使用ChatOpenAI来创建模型

load_dotenv(override=True)

# 使用ChatOpenAI来创建模型
llm = ChatOpenAI(
    model="deepseek-flash",                    # 选择对应的模型
    api_key=os.getenv("DEEPSEEK_API_KEY"),     # 从环境变量中获取密钥
    base_url=os.getenv("DEEPSEEK_BASE_URL"),   # 从环境变量中获取 接口地址
)

if __name__ == "__main__":
    prompt = input("请输入你的问题：").strip() or "用三句话讲清楚什么是比喻句"

    # =======================================================================
    # 一、老师课堂上的写法（原样，只多了 flush=True）
    # =======================================================================
    print()
    print("=" * 66)
    print('【1】老师的写法：input=[system, user] 两个字典 + stream()')
    print("=" * 66)
    print("答：", end="", flush=True)

    t0 = time.time()
    # 使用流式输出大模型的回复内容
    res = llm.stream(
        input=[
            {"role": "system", "content": "你是一个语文老师"},
            {"role": "user", "content": prompt},
        ]
    )

    # 使用迭代器对象，打印每个chunk的内容
    for chunk in res:
        print(chunk.content, end="", flush=True)   # 老师原版没有 flush=True

    stream_cost = time.time() - t0
    print()
    print(f"\n（总耗时 {stream_cost:.2f}s；注意开头那段空白是思考模式在'想'，第 4 步会解释）")

    # =======================================================================
    # 二、input 的三种写法
    # =======================================================================
    print()
    print("=" * 66)
    print("【2】input 的三种写法（都能用，效果一样）")
    print("=" * 66)
    print("""    llm.stream("帮我解释比喻句")                                   # ① 直接传字符串
    llm.stream([("user", "帮我解释比喻句")])                           # ② 元组：(角色, 内容)
    llm.stream([{"role": "user", "content": "帮我解释比喻句"}])         # ③ 字典：和 day01 的 messages 完全一致

  三种写法等价，区别只是"写得快"还是"看得清楚"。
  想要人设，就得用 ② 或 ③ 把 system 消息也塞进去。

  三种角色和 day01 学的完全一样：
      system  人设 / 规则        user  用户提问        assistant  模型之前的回答""")

    # =======================================================================
    # 三、人设到底有多大影响？同一个问题换三个 system
    # =======================================================================
    print()
    print("=" * 66)
    print("【3】同一个问题 + 不同 system 人设 = 不同的回答风格")
    print("=" * 66)

    question = "解释一下「比喻」这种修辞"
    personas = [
        ("你是一个语文老师", "语文老师"),
        ("你是一个幼儿园老师，要用小朋友听得懂的话说", "幼儿园老师"),
        ("你是一个网络段子手，说话要幽默、带梗", "段子手"),
    ]
    for sys_prompt, label in personas:
        r = llm.invoke([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": question},
        ])
        text = str(r.content).replace("\n", " ")
        print(f"\n  【{label}】{text[:110]}{'…' if len(text) > 110 else ''}")

    print("\n  ↑ 同一个模型、同一个问题，只换 system，语气和讲法就完全不同。")
    print("    这就是为什么有人写提示词要花很多功夫在 system 上。")

    # =======================================================================
    # 四、流式 vs 非流式 / 空分片 / chunk 结构
    # =======================================================================
    print()
    print("=" * 66)
    print("【4】实测：流式到底省了什么")
    print("=" * 66)

    t0 = time.time()
    one = llm.invoke([{"role": "user", "content": prompt}])
    invoke_cost = time.time() - t0
    print(f"  非流式 invoke()：总耗时 {invoke_cost:.2f}s —— 这段时间屏幕上一个字都没有")

    t0 = time.time()
    first_chunk_at = None
    first_text_at = None
    chunks = []
    print("\n  流式 stream()：", end="", flush=True)
    for chunk in llm.stream([{"role": "user", "content": prompt}]):
        elapsed = time.time() - t0
        if first_chunk_at is None:
            first_chunk_at = elapsed
        chunks.append(chunk)
        if chunk.content and first_text_at is None:
            first_text_at = elapsed
        print(chunk.content, end="", flush=True)

    total = time.time() - t0
    empty = sum(1 for c in chunks if not c.content)
    print()
    print(f"\n    第一片到达   ：{first_chunk_at:.2f}s")
    print(f"    第一个正文字 ：{first_text_at:.2f}s   ← 用户真正看到字的时刻")
    print(f"    分片 {len(chunks)} 片（空正文 {empty} 片）　总耗时 {total:.2f}s")

    print()
    if first_text_at < invoke_cost:
        print(f"  这次流式提前了 {invoke_cost - first_text_at:.2f}s 出字 —— 打字机效果明显。")
    else:
        print(f"  这次流式反而更晚出字（{first_text_at:.2f}s vs 非流式 {invoke_cost:.2f}s）。")
        print("  不是流式失效了，而是【思考模式】占了大头：模型'想'多久每次都不一样，")
        print("  而'想'的过程不产生正文，所以首字被拖住了。")
    print()
    print("  怎么理解这件事：")
    print("    · 关掉思考 / 降低思考强度时，流式的首字优势最明显（零点几秒就出字）")
    print("    · 开着思考时，首字延迟主要由'想'决定，流式省的是'边生成边显示'")
    print("    · 但无论哪种情况，流式都不会让你对着白屏干等 —— 一有字就立刻显示")

    valid = [c for c in chunks if c.content]
    print()
    print("  chunk 长什么样（AIMessageChunk）：")
    for i, c in enumerate(valid[:5], start=1):
        print(f"    第{i}个有效片  内容={c.content!r}")
    print(f"  拼起来 = {len(''.join(c.content for c in chunks))} 个字")

    print()
    print("  【为什么会有一堆空分片？】")
    print("    V4 默认开着思考模式：模型先'想'再答，想的过程也以流推送，")
    print("    但 LangChain 没把推理内容放进 chunk.content，所以那些片是空字符串。")
    print("    → 所以 老师那句 print(chunk.content) 在思考阶段会刷空行，")
    print("      做 Gradio 界面时更要 if chunk.content: 再累加，否则界面会闪。")

    # =======================================================================
    print()
    print("=" * 66)
    print("小结")
    print("=" * 66)
    print("""  流式三句话：
    ① res = llm.stream(...)        拿到的是"迭代器"，不是完整答案
    ② for chunk in res:            一次给你一小片
    ③ chunk.content + end=""       不换行地接起来 = 打字机

  和 06 节的分工：
    invoke()  一次性给完，代码简单，但用户要干等
    stream()  边生成边给，体验好，但要处理空分片

  想让人设起作用：input 里加 {"role": "system", "content": "..."}""")
