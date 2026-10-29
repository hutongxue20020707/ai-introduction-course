"""
12. gradio 中的布局

老师在课上讲的：

    页面中的布局是先创建行，然后在行中创建列也就是我们的组件
    总结：先写行，然后在行中创建列定义列所占的比例，再在列中定义组件

    Row     => 行
    column  => 列
    scale   => 比例

一句话记法：**行里放列，列里放组件**（Row → Column → 组件）。
不写 Column 直接往 Row 里塞组件也可以，但那样没法控制宽度比例。

前置条件：项目根目录的 .env 里有 DEEPSEEK_API_KEY（只有第三部分用到）。
运行：python 12.gradio中的布局.py
    ★ 浏览器打开终端里打印的地址；关掉按 Ctrl + C
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
# 准备 DeepSeek 客户端（给第三部分的实战用）
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


def ask_ai(question: str, temperature: float):
    """点「生成」时执行"""
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
with gr.Blocks(title="gradio 布局：Row / Column / scale") as demo:
    """
    页面中的布局是先创建行，然后在行中创建列也就是我们的组件
    总结：先写行，然后在行中创建列定义列所占的比例，再在列中定义组件

    Row     => 行
    column  => 列
    scale   => 比例
    """

    # =======================================================================
    # 一、老师课堂上的例子（原样保留）
    # =======================================================================
    gr.Markdown("## 一、老师课堂的例子：一行两列，比例 2 : 1")

    with gr.Row():                                   # 行布局
        with gr.Column(scale=2):                     # 布局列，当前列占整行中的 2 份
            gr.Textbox(placeholder="请输入你的账号", label="账号")   # 当前列中的组件
        with gr.Column(scale=1):                     # 布局列，当前列占整行中的 1 份
            gr.Slider(label="播放器", minimum=0, maximum=100, value=50, step=10, interactive=True)

    gr.Markdown("> 上面一行被切成 2:1 —— 账号框宽一些，滑块窄一些。")

    # =======================================================================
    # 二、补充：多行 + 比例对比（scale 到底怎么分宽度）
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("## 二、补充：多行，以及 scale 比例对比")

    for left_scale, right_scale in ((1, 1), (2, 1), (3, 1), (1, 3)):
        with gr.Row():
            with gr.Column(scale=left_scale):
                gr.Textbox(label=f"左列 scale={left_scale}", value=f"左：scale {left_scale}")
            with gr.Column(scale=right_scale):
                gr.Textbox(label=f"右列 scale={right_scale}", value=f"右：scale {right_scale}")

    gr.Markdown(
        "> scale 是**相对比例**，不是像素。`scale=2` 和 `scale=1` 并排，就是一宽一窄；\n"
        "> 全部写 1 就是平分。想要三栏，就往 Row 里放三个 Column。"
    )

    # =======================================================================
    # 三、实战：左右分栏的 AI 问答面板（左边输入，右边输出）
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("## 三、实战：左右分栏的 AI 问答面板")

    with gr.Row():
        # 左栏（窄）：输入区
        with gr.Column(scale=1):
            question = gr.Textbox(
                label="你的问题",
                placeholder="例如：用一句话解释什么是大模型",
                lines=3,
            )
            temperature = gr.Slider(
                label="temperature（越大越发散）",
                minimum=0.0,
                maximum=1.5,
                value=0.7,
                step=0.1,
                interactive=True,
            )
            run_btn = gr.Button("生成", variant="primary")

        # 右栏（宽）：输出区，给回答留出更多地方
        with gr.Column(scale=2):
            answer = gr.Textbox(label="AI 的回答", lines=12)

    # 绑定事件：点按钮 / 在问题框按回车，都会触发
    run_btn.click(fn=ask_ai, inputs=[question, temperature], outputs=answer)
    question.submit(fn=ask_ai, inputs=[question, temperature], outputs=answer)

    gr.Markdown("> 这就是真实 AI 产品最常见的页面结构：**左边调参数、右边看结果**。")


# 启动页面
if __name__ == "__main__":
    print("=" * 62)
    print("启动后会打印本地地址，例如 http://127.0.0.1:7860")
    print("用浏览器打开它；关掉程序按 Ctrl + C")
    print("=" * 62)
    demo.launch()
