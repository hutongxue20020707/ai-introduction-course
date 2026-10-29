"""
点击事件  => click
语法：
    组件.click(fn=绑定运行的函数, inputs=传入函数的参数, outputs=输出参数)
    作用：当我们点击某一个组件之后，他会触发一个函数的执行
    参数说明:
        fn      => 当我们点击组件之后要触发执行的函数
        inputs  => 当函数触发要运行时传入给函数执行的参数列表
        outputs => 当 fn 绑定的函数执行完毕后，返回的结果给对应的组件
"""

# ===========================================================================
# 补充：老师这节讲的是"事件绑定"，是 gradio 里最核心的一环
#   组件只是"显示"；绑定事件之后，页面才"活"起来。
#   常见的几种事件：
#       click    → 点击按钮/图片
#       change   → 值改变（边输入边触发）
#       submit   → 在输入框里按回车
#       release  → 松开滑块
#   本文件：第一部分照老师原样，后面补了"多输入多输出"、"其他事件"，最后接 AI。
#
# 前置条件：项目根目录的 .env 里有 DEEPSEEK_API_KEY（只有第四部分用到）
# 运行：python 13.动态绑定事件.py
#    ★ 浏览器打开终端里打印的地址；关掉按 Ctrl + C
# ===========================================================================

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# 导包
import gradio as gr

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# 准备 DeepSeek 客户端（第四部分用）
load_dotenv(override=True)
api_key = os.environ.get("DEEPSEEK_API_KEY")

client = None
if api_key:
    try:
        api_key.encode("ascii")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    except UnicodeEncodeError:
        client = None


# ---------------------------------------------------------------------------
# 定义一个函数，将年龄*2（老师课堂上的例子）
# ---------------------------------------------------------------------------
def click_fn(age):
    return age * 2


# ---------------------------------------------------------------------------
# 补充用到的几个函数
# ---------------------------------------------------------------------------
def calc(a, b):
    """多个输入、多个输出：函数返回一个元组，按顺序对到 outputs 上"""
    a = a or 0
    b = b or 0
    return a + b, a - b, a * b


def count_chars(text):
    """change 事件：一边输入一边触发"""
    text = text or ""
    return f"当前 {len(text)} 个字"


def ask_ai(question: str, temperature: float):
    """点按钮 → 调 DeepSeek"""
    question = (question or "").strip()
    if not question:
        return "（请先输入问题）"
    if client is None:
        return "（没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py）"
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
            temperature=float(temperature),
            extra_body={"thinking": {"type": "disabled"}},
        )
        return res.choices[0].message.content or "（空回复）"
    except Exception as exc:
        return f"（调用失败：{type(exc).__name__}）\n{str(exc)[:300]}"


# 搭建UI界面
with gr.Blocks(title="动态绑定事件") as demo:
    # =======================================================================
    # 一、老师课堂上的例子（原样保留）
    # =======================================================================
    gr.Markdown("## 一、老师课堂的例子：输入年龄 → 点按钮 → 输出年龄×2")

    # 创建一个输入数值框组件，Number 组件和 Textbox 组件的用法完全一样，
    # 只是 Textbox 组件可以接收字符串内容，而 Number 组件只能接收数字
    age = gr.Number(label="年龄", placeholder="请输入你的年龄")

    # 创建一个按钮组件
    run_btn = gr.Button("点击", variant="primary")

    # 创建一个输出组件，用来显示结果
    doubled = gr.Textbox(label="结果（年龄 × 2）", interactive=False)

    # 绑定点击事件：点按钮 → 执行 click_fn → 参数取 age 的值 → 结果写到 doubled
    run_btn.click(fn=click_fn, inputs=age, outputs=doubled)

    gr.Markdown(
        "> **一句话记住三个参数**：`fn` 干什么、`inputs` 从谁那儿拿、`outputs` 写到哪儿。\n"
        "> 注意 `inputs` 和 `outputs` 可以直接写单个组件，也可以写成列表。"
    )

    # =======================================================================
    # 二、补充 1：多个输入、多个输出
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("## 二、补充：多个输入 + 多个输出")

    with gr.Row():
        num_a = gr.Number(label="第一个数", value=6)
        num_b = gr.Number(label="第二个数", value=3)
    calc_btn = gr.Button("计算加减乘")

    with gr.Row():
        out_sum = gr.Textbox(label="和", interactive=False)
        out_diff = gr.Textbox(label="差", interactive=False)
        out_prod = gr.Textbox(label="积", interactive=False)

    # inputs 写成列表 → 函数按顺序收到 a, b
    # outputs 写成列表 → 函数返回的元组按顺序填进去
    calc_btn.click(fn=calc, inputs=[num_a, num_b], outputs=[out_sum, out_diff, out_prod])

    gr.Markdown("> 函数 `calc` 返回了三个值（`return 和, 差, 积`），正好对上三个 outputs。**顺序不能错。**")

    # =======================================================================
    # 三、补充 2：别的事件类型（不止 click）
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("## 三、补充：change / submit / release 这些事件")

    with gr.Row():
        with gr.Column(scale=1):
            typing_box = gr.Textbox(
                label="边打字边统计（change 事件）",
                placeholder="随便输入点什么",
            )
            char_count = gr.Textbox(label="字数", interactive=False)
            typing_box.change(fn=count_chars, inputs=typing_box, outputs=char_count)

        with gr.Column(scale=1):
            submit_box = gr.Textbox(label="按回车触发（submit 事件）", placeholder="输入后按 Enter")
            submit_echo = gr.Textbox(label="你刚刚提交的内容", interactive=False)
            submit_box.submit(fn=lambda t: f"收到：{t}", inputs=submit_box, outputs=submit_echo)

    gr.Markdown(
        "> 常用事件对照：\n"
        "> | 事件 | 什么时候触发 | 典型用途 |\n"
        "> |---|---|---|\n"
        "> | `click` | 点击 | 按钮提交 |\n"
        "> | `change` | 值一变就触发 | 实时统计、联动 |\n"
        "> | `submit` | 输入框里按回车 | 聊天框发送 |\n"
        "> | `release` | 松开滑块 | 调参后重新生成 |"
    )

    # =======================================================================
    # 四、实战：把 click 事件接到 DeepSeek 上
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("## 四、实战：点按钮让 AI 回答")

    with gr.Row():
        with gr.Column(scale=1):
            question = gr.Textbox(label="你的问题", placeholder="例如：用一句话解释什么是大模型", lines=3)
            temperature = gr.Slider(label="temperature", minimum=0.0, maximum=1.5, value=0.7, step=0.1)
            ai_btn = gr.Button("问 AI", variant="primary")
        with gr.Column(scale=2):
            ai_answer = gr.Textbox(label="AI 的回答", lines=12)

    ai_btn.click(fn=ask_ai, inputs=[question, temperature], outputs=ai_answer)
    question.submit(fn=ask_ai, inputs=[question, temperature], outputs=ai_answer)


# 启动页面
if __name__ == "__main__":
    print("=" * 62)
    print("启动后会打印本地地址，例如 http://127.0.0.1:7860")
    print("用浏览器打开它；关掉程序按 Ctrl + C")
    print("=" * 62)
    demo.launch()
