"""
演示大模型回复实时信息内容：
    如:
        今天天气怎么样？

"""

# ===========================================================================
# 老师的原版（智谱）：
#     import os
#     from zhipuai import ZhipuAI
#     client = ZhipuAI(api_key=os.getenv("zhipuai_api_key"))
#     res = client.chat.completions.create(
#         model="glm-4",
#         messages=[
#             {"role": "assistant", "content": "你是一个天气预报小助手"},
#             {"role": "user", "content": "长沙今天天气怎么样？"}
#         ]
#     )
#     print(res.choices[0].message.content)
#
# 本文件换成 DeepSeek，结构完全一样。
# 下面还会解释：为什么它答不上来，以及三种解决办法（重点是下一节的 function calling）。
#
# 运行：python 01.大模型回复实时信息的问题.py
# ===========================================================================

# 1.导包
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# 2.创建客户端
load_dotenv(override=True)
api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 3.与AI进行交互
print("=" * 66)
print("问：长沙今天天气怎么样？")
print("=" * 66)

res = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "assistant", "content": "你是一个天气预报小助手"},
        {"role": "user", "content": "长沙今天天气怎么样？"},
    ],
    extra_body={"thinking": {"type": "disabled"}},
)

# 4.在控制台打印大模型的回复内容
print(res.choices[0].message.content)

# ===========================================================================
# 现象：它答不上来（本机实测的原话）
#
#   我目前没有联网，无法实时获取长沙今天的天气情况。
#   建议你打开天气App，或搜索“长沙天气”查看最新预报。
#
# 为什么会这样？
#   1. 大模型的"知识"来自训练数据，训练数据有截止日期，之后的事它不知道。
#   2. 它不知道自己不知道 —— 有时候它会一本正经地编一个天气给你（幻觉）。
#   3. 它不能上网、不能查数据库、不能读你电脑里的文件 —— 它只能"说话"。
#
# 三种解决办法（从简单到工程化）：
#   ① 把实时数据手动塞进提示词
#         res = client.chat.completions.create(..., messages=[
#             {"role": "system", "content": "今天长沙的天气是：多云转晴，22~29℃"},
#             {"role": "user", "content": "长沙今天天气怎么样？"}])
#         —— 能答对，但数据得你自己去拿，而且每次都要手动改。
#
#   ② function calling（函数调用）★ 下一节 02.functioncalling.py
#         —— 你告诉模型"我有个查天气的工具"，模型自己判断要不要用、
#            该传什么参数；你在本地执行，再把结果交给它总结成自然语言。
#
#   ③ 联网搜索 / RAG（检索增强）
#         —— 让程序先去搜/去查，把搜到的内容当资料塞进提示词。
#
# 一句话：模型负责"说"，实时数据要靠"你的程序"去拿，然后喂给它。
# ===========================================================================

print()
print("=" * 66)
print("对照实验：如果把天气数据直接塞进提示词，它就能答了")
print("=" * 66)

res2 = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是一个天气预报小助手。"},
        {"role": "system", "content": "参考资料：今天长沙多云转晴，22~29℃，东南风 2 级。"},
        {"role": "user", "content": "长沙今天天气怎么样？"},
    ],
    extra_body={"thinking": {"type": "disabled"}},
)
print(res2.choices[0].message.content)
print()
print("↑ 同样的模型，只因为提示词里多了那一行实时数据，答案就靠谱了。")
print("  下一节要学的 function calling，就是让「拿数据」这一步自动化。")
