"""
11. 滑块 Slider 组件

老师在课上讲的组件清单：

    编写组件
    Slider      => 滑块
        label       => 标题
        minimum     => 最小值
        maximum     => 最大值
        value       => 默认值
        step        => 步长大小
        interactive => 交互的

滑块是 gradio 里最"手感好"的组件之一：拖一下就能调参数，不用打字。
在 AI 应用里它最常见的用途就是调 temperature（温度）。

前置条件：项目根目录的 .env 里有 DEEPSEEK_API_KEY。
运行：python 11.滑块Slider组件.py
    ★ 启动后浏览器打开终端里打印的地址（通常是 http://127.0.0.1:7860）
    ★ 关掉程序：在终端按 Ctrl + C
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# 导包
import gradio as gr

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# ---------------------------------------------------------------------------
# 准备 DeepSeek 客户端（只给页面下半部分的实验用）
# ---------------------------------------------------------------------------
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
# 点「生成」时执行的函数：把滑块的值当 temperature 传给模型
#   注意：滑块传过来的可能是整数也可能是小数，统一转成 float 更稳
# ---------------------------------------------------------------------------
def ask_ai(question: str, temperature: float):
    question = (question or "").strip()
    if not question:
        return "（请先输入问题）"
    if client is None:
        return "（没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py）"

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
            temperature=float(temperature),          # ← 滑块的值直接当参数用
            extra_body={"thinking": {"type": "disabled"}},
        )
        return res.choices[0].message.content or "（空回复）"
    except Exception as exc:
        return f"（调用失败：{type(exc).__name__}）\n{str(exc)[:300]}"


# 搭建UI界面
with gr.Blocks(title="Slider 滑块组件") as demo:
    """
    编写组件
    Slider      => 滑块
        label       => 标题
        minimum     => 最小值
        maximum     => 最大值
        value       => 默认值
        step        => 步长大小
        interactive => 交互的
    """

    gr.Markdown("## 一、老师课堂上的那个滑块")
    # 老师那份代码，原样保留：一个 0~100、默认 20、步长 10 的"音量"滑块
    volume = gr.Slider(label="声音", minimum=0, maximum=100, value=20, step=10, interactive=True)

    # 补充 1：滑块的值怎么拿到？—— 加一个 .change 事件，把值实时显示出来
    volume_value = gr.Textbox(label="当前滑块的值", value="20", interactive=False)
    volume.change(fn=lambda v: str(v), inputs=volume, outputs=volume_value)
    gr.Markdown(
        "> 拖动上面的滑块，下面的数字会跟着变 —— 这就是「组件 → 事件 → 函数 → 输出」的完整链路。"
    )

    gr.Markdown("---")
    gr.Markdown("## 二、实战：用滑块调 AI 的 temperature")
    gr.Markdown(
        "**temperature（温度）** 控制回答的随机程度：\n"
        "- 0 附近：几乎每次都一样，稳定、可复现\n"
        "- 0.7 左右：有变化，比较自然（常用默认值）\n"
        "- 1.2 以上：更发散、更有创意，也更容易跑偏\n\n"
        "**本机实测**（同一句「给一家新开的咖啡店起个名字」跑两次）：\n"
        "| temperature | 第 1 次 | 第 2 次 |\n"
        "|---|---|---|\n"
        "| 0.0 | 豆语时光 | 豆语时光（完全一样）|\n"
        "| 0.7 | 豆语时光 | 半醒咖啡（开始变化）|\n"
        "| 1.5 | 豆语时光 | 豆语时光 |\n\n"
        "> 注意最后那行：温度高不代表就是「每次都不一样」，**单次实验不足以说明问题**，"
        "要多跑几次才靠谱。"
    )

    with gr.Row():
        temperature = gr.Slider(
            label="temperature（越大越发散）",
            minimum=0.0,
            maximum=1.5,
            value=0.7,
            step=0.1,
            interactive=True,
        )

    question = gr.Textbox(
        label="你的问题",
        value="给一家新开的咖啡店起个名字，只输出名字，不要解释",
        placeholder="输入问题，然后点下面的「生成」",
        lines=2,
    )
    run_btn = gr.Button("生成", variant="primary")
    output = gr.Textbox(label="AI 的回答", lines=4)

    run_btn.click(fn=ask_ai, inputs=[question, temperature], outputs=output)
    question.submit(fn=ask_ai, inputs=[question, temperature], outputs=output)


# 启动页面
if __name__ == "__main__":
    print("=" * 62)
    print("启动后会打印本地地址，例如 http://127.0.0.1:7860")
    print("用浏览器打开它；关掉程序按 Ctrl + C")
    print("=" * 62)
    demo.launch()
