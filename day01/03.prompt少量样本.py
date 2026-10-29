"""
提示词工程 => prompt engineering
    prompt => 就是AGI时代的编程语言
    prompt工程 => 就是AGI时代的软件工程
    prompt工程师就是AGI时代的 程序员
    什么是AGI？
    就是我们说的通用人工智能

prompt 提示词分类
    1.零样本
    2.少样本
    3.自洽性
    4.思维链
    5.思维树

做一个少样本的提示词 => 给AI模型学习少量的样本数据
    instruction => 我们需要给AI定一个任务描述，让AI进行学习
    example     => 示例：我们需要给AI具一格示例来学习，AI学习之后，就可以按照示例输出结果
    input_txt   => AI学习我们的示例之后，将我们的任务输入进来，让AI来解答
    output      => 限制AI的输出，包括但不限于：限制内容、格式、法律、回答长度...
"""

# ===========================================================================
# 本文件 = 老师原版 + 以下改动（DeepSeek 版）：
#   1. 智谱 ZhipuAI + glm-4  →  DeepSeek + deepseek-flash
#   2. 密钥从源码里移到 .env（源码不出现密钥）
#   3. 补了三段课堂实操：打印拼好的 prompt、用 json.loads 真解析结果、
#      零样本对照、同一个提示词连跑 3 次看稳定性
# ===========================================================================

import json
import os
import sys

# Windows 控制台默认 GBK，模型回复里若带 emoji，print 会直接崩。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

# 两个开关（同 day01 / day02）
THINKING = "disabled"        # V4 默认开思考模式，练习建议关掉
MODEL = "deepseek-flash"     # 想更强推理换成 deepseek-v4-pro

load_dotenv(override=True)   # 别让系统里同名的环境变量盖掉 .env

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise SystemExit("没有读到 DEEPSEEK_API_KEY，请确认项目目录下有 .env 文件。")
try:
    api_key.encode("ascii")
except UnicodeEncodeError:
    raise SystemExit(f"DEEPSEEK_API_KEY 里出现了中文字符（当前值：{api_key}），请检查 .env。")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ---------------------------------------------------------------------------
# 第 1 步：写出提示词的四个零件
# ---------------------------------------------------------------------------

# 1) 任务描述
instruction = "你的任务是识别用户输入的信息，提取信息中的时间(time)、地点(location)、人物(person)"

# 2) 示例（"少量样本"里的"样本"，关键就是这个）
example = """示例：
    在本周三，我和张三一起去长沙世界之窗玩了一下
    {"time": "本周三", "location": "长沙世界之窗", "person": "我和张三"}"""

# 3) 要处理的输入
input_txt = "我计划着周末和小丽一起去爬岳麓山，本来还想带张三一起去，但是他要工作，所以就算了"

# 4) 输出格式限制
output = "限制：以JSON格式进行输出，不要输出任何解释文字"

# 组装成完整提示词
prompt = f"""{instruction}

{example}

现在请处理下面这条输入：
{input_txt}

{output}"""

print("=" * 66)
print("组装好的提示词（这就是发给模型的东西）")
print("=" * 66)
print(prompt)
print()

# ---------------------------------------------------------------------------
# 第 2 步：调用模型（少样本）
# ---------------------------------------------------------------------------
res = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    extra_body={"thinking": {"type": THINKING}},
)
answer = res.choices[0].message.content or ""

print("=" * 66)
print("少样本（给了示例）的回复")
print("=" * 66)
print(answer)
print(f"(tokens：输入 {res.usage.prompt_tokens} / 输出 {res.usage.completion_tokens})")
print()


# ---------------------------------------------------------------------------
# 第 3 步：把回复当 JSON 真的解析一遍
# 模型有时会把 JSON 包在 ```json 代码块里，所以先剥掉外层再解析。
# ---------------------------------------------------------------------------
def extract_json(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    return t.strip()


try:
    data = json.loads(extract_json(answer))
    print("JSON 解析成功，可以直接拿去用：")
    for k, v in data.items():
        print(f"    {k} = {v}")
except Exception as exc:
    print("JSON 解析失败：", exc)
    print("说明模型输出里混了多余文字 —— 这正是「格式限制」要解决的问题。")
print()

# ---------------------------------------------------------------------------
# 第 4 步：对照实验 —— 去掉示例（零样本 zero-shot）
# ---------------------------------------------------------------------------
zero_shot_prompt = f"""{instruction}

现在请处理下面这条输入：
{input_txt}

{output}"""

res2 = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": zero_shot_prompt}],
    extra_body={"thinking": {"type": THINKING}},
)
answer2 = res2.choices[0].message.content or ""

print("=" * 66)
print("零样本（不给示例）的回复 —— 对比着看")
print("=" * 66)
print(answer2)
print(f"(tokens：输入 {res2.usage.prompt_tokens} / 输出 {res2.usage.completion_tokens})")
print()

# ---------------------------------------------------------------------------
# 第 5 步：同一个提示词连跑 3 次，看结果稳不稳定
# 大模型输出带随机性：本机实测过同一个提示词两次给出不同的 person 字段
# （一次含"张三"、一次不含）。所以关键任务别只看一次结果。
# ---------------------------------------------------------------------------
print("=" * 66)
print("同一个少样本提示词，连跑 3 次，看结果是否一致")
print("=" * 66)
for i in range(1, 4):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        extra_body={"thinking": {"type": THINKING}},
    )
    print(f"第 {i} 次：{r.choices[0].message.content}")
print("如果三次不完全一样 —— 这就是正常现象，不是代码写错了。")
