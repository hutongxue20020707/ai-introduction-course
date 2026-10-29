"""
08. langchain 的模型 Batch 调用

老师课堂上收 3 个问题、一次性批量问模型：

    prompt = []                          # 定义一个列表保存用户的多个问题
    for i in range(1, 4):                # 循环 3 次，接收用户的 3 个问题
        ipt = input(f"请输入你的第{i}个问题：")
        prompt.append(ipt)               # 把它们都放进列表

    res = llm.batch(prompt)              # 调用模型，批量处理多个问题

    for i in res:                        # 输出每个回答
        print(i.content)
        print("=" * 50)

前两节的分工（配上这一节就齐了）：
    invoke()   一个问题 → 一个答案
    stream()   一个问题 → 边生成边收（打字机）
    batch()    一堆问题 → 一次性提交，并发跑完再一起给

为什么 batch 快？它内部是【并发】发请求的（默认线程池），
3 个问题不是"1+1+1"的耗时，而是"最慢那个"的耗时。

注意：batch 会同时打出去 N 个请求 —— 注意账号的并发限制和余额。

运行：python 08.langchain的模型Batch调用.py     （会连着问你 3 个问题）
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # 使用ChatOpenAI来创建模型

load_dotenv(override=True)  # 读取环境变量中的内容

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
    prompt = []                            # 定义一个列表保存用户的多个问题
    for i in range(1, 4):                  # 循环 3 次，接收用户的 3 个问题
        ipt = input(f"请输入你的第{i}个问题：").strip()
        if not ipt:
            ipt = f"用一句话解释第 {i} 个常识知识点"   # 直接回车就用默认问题
        prompt.append(ipt)                 # 把问题添加到列表中

    print()
    print("=" * 66)
    print("【1】老师的写法：llm.batch(prompt)")
    print("=" * 66)

    t0 = time.time()
    # 调用模型，批次处理多个问题
    res = llm.batch(prompt)
    batch_cost = time.time() - t0

    # 在控制台输出大模型回复的内容
    for q, message in zip(prompt, res):
        print(f"问：{q}")
        print(f"答：{message.content}")
        print("=" * 50)

    print(f"（batch 总耗时 {batch_cost:.2f}s）")

    # =======================================================================
    # 二、batch 到底快多少？和"串行三次 invoke"比一比
    # =======================================================================
    print()
    print("=" * 66)
    print("【2】实测对比：串行 invoke ×3  vs  batch 一次")
    print("=" * 66)

    t0 = time.time()
    serial_results = [llm.invoke(q) for q in prompt]     # 一个一个问，等前一个答完再问下一个
    serial_cost = time.time() - t0

    print(f"  串行三次 invoke ：{serial_cost:.2f}s   ← 1 + 1 + 1 的等待叠加")
    print(f"  一次 batch      ：{batch_cost:.2f}s   ← 并发，约等于'最慢那个'的耗时")
    if batch_cost > 0:
        print(f"  提速约 {serial_cost / batch_cost:.1f} 倍")

    print()
    print("  两边答案都对应得上（顺序一一对应），但内容不会逐字相同 ——")
    print("  模型有随机性，同一个问题问两次本来就不一样（见 day01 第 02 课的'随机性'）：")
    for q, a, b in zip(prompt, res, serial_results):
        one = str(a.content).replace("\n", " ")[:20]
        two = str(b.content).replace("\n", " ")[:20]
        print(f"    问题：{q}")
        print(f"        batch 答：{one}…")
        print(f"        串行  答：{two}…")
        print()

    # =======================================================================
    # 三、几个使用细节
    # =======================================================================
    print()
    print("=" * 66)
    print("【3】batch 的几个细节")
    print("=" * 66)

    # ① 返回的是 list[AIMessage]，顺序和输入一一对应
    print("  ① 返回类型：", type(res).__name__, "，长度", len(res), "，顺序与输入一一对应")

    # ② 可以限制并发数（防止一次性打太多请求被限流）
    t0 = time.time()
    res_lim = llm.batch(prompt, config={"max_concurrency": 1})
    print(f"  ② 用 max_concurrency=1 强制串行：{time.time() - t0:.2f}s（比并发慢，但不会被限流打挂）")

    # ③ batch 里也可以放"多轮对话"：每一项是一条完整的消息列表
    convs = [
        [{"role": "user", "content": "用一句话解释什么是函数"}],
        [{"role": "system", "content": "你只回答一个字"},
         {"role": "user", "content": "1+1 等于几"}],
    ]
    res2 = llm.batch(convs)
    print("  ③ 每一项可以是一条完整对话（带各自的 system）：")
    for c in res2:
        print("     -", str(c.content).replace("\n", " ")[:60])

    print()
    print("=" * 66)
    print("小结：三个方法怎么选")
    print("=" * 66)
    print("""  invoke()  单个问题、要完整答案          → 最简单
  stream()  单个问题、要即时看到输出      → 聊天界面必备
  batch()   一批问题一起处理              → 跑评测、批量翻译、批量总结时最省时间

  一句话：内容多就 batch，要看到就 stream，只有一个问题就 invoke。""")
