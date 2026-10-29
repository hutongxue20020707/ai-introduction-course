"""
1.什么是gradio?
gradio是用于python快速搭建web页面应用程序

使用方法：
    1.下载依赖，在终端使用命令来下载依赖
    命令：pip install gradio 或者 python -m pip install gradio
    2.导入包      as 表示使用别名
    import gradio as gr
    3.搭建UI页面
    with gr.Blocks() as demo:
        编写UI组件
    启动网页
        demo.launch()
"""

# ===========================================================================
# 下面是本项目的补充（老师文件里没有，老师那版只有一个输入框，点了没反应）
#   在老师"三步骨架"完全不变的前提下，把组件接到 DeepSeek 上：
#       输入框 + 发送按钮 → 调用模型 → 回答显示在下面的文本框中
#   前置条件：项目根目录的 .env 里有 DEEPSEEK_API_KEY
#            （不确定就先运行 day01/07.校验环境变量配置是否成功.py）
#   运行：python 10.gradio案例.py
#   关掉：在终端按 Ctrl + C
# ===========================================================================

# 导包
import gradio as gr

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"
SYSTEM_PROMPT = "你是一个耐心的 AI 助教。回答用中文，尽量简洁。"

# 准备工作：把 DeepSeek 客户端建好（这一步老师文件里没有，因为老师那版不调模型）
load_dotenv(override=True)                    # 会自动往上找到项目根目录的 .env
api_key = os.environ.get("DEEPSEEK_API_KEY")

client = None
if api_key:
    try:
        api_key.encode("ascii")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    except UnicodeEncodeError:
        client = None


def chat_fn(question: str, history: list):
    """点「发送」时执行：把问题发给 DeepSeek，返回回答和更新后的记忆盒子。"""
    question = (question or "").strip()        # 第 07 课：先去掉两端空格

    if not question:
        return "（请先输入问题）", history

    if client is None:
        return "（没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py）", history

    if not history:                            # 第一次对话，先放个人设
        history.append({"role": "system", "content": SYSTEM_PROMPT})

    history.append({"role": "user", "content": question})

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=history,                  # 整个记忆盒子发给模型（第 03 课）
            extra_body={"thinking": {"type": "disabled"}},
        )
        answer = res.choices[0].message.content or ""
    except Exception as exc:                   # 网络/余额/密钥出错时别让网页崩
        return f"（调用失败：{type(exc).__name__}）\n{str(exc)[:300]}", history

    history.append({"role": "assistant", "content": answer})
    return answer, history


def clear_fn():
    """清空：输入框、回答、记忆盒子一起归零。"""
    return "", [], ""


# 搭建UI页面
with gr.Blocks(title="我的第一个 AI 网页") as demo:
    """
    编写UI组件：
        Textbox     => 文本输入框
            Label       => 标题
            placeholder => 输入提示
    """
    # ---- 老师课堂上演示的那个组件（原样保留，方便对照老师代码）----
    gr.Textbox(label="姓名", placeholder="请输入你的姓名")

    # ---- 下面是在同一个页面上加的"真能用"的对话组件 ----
    gr.Markdown(
        "## 和 AI 聊天\n"
        "输入问题，点「发送」或直接按回车。它会记住本次对话的上下文。"
    )

    with gr.Row():
        question = gr.Textbox(
            label="你的问题",                          # Label：标题
            placeholder="例如：用一句话解释什么是大模型",   # placeholder：输入提示
            scale=4,
        )
        send_btn = gr.Button("发送", variant="primary", scale=1)

    answer = gr.Textbox(label="AI 的回答", lines=10)
    history_state = gr.State([])               # 记忆盒子放在会话状态里
    clear_btn = gr.Button("清空对话")

    # 绑定事件：点按钮 / 按回车 → 调用 chat_fn
    send_btn.click(fn=chat_fn, inputs=[question, history_state], outputs=[answer, history_state])
    question.submit(fn=chat_fn, inputs=[question, history_state], outputs=[answer, history_state])
    clear_btn.click(fn=clear_fn, outputs=[question, history_state, answer])

# 启动网页
if __name__ == "__main__":
    print("=" * 62)
    print("启动后会打印一个本地地址，例如 http://127.0.0.1:7860")
    print("用浏览器打开它就能用了；关掉程序按 Ctrl + C")
    print("=" * 62)
    demo.launch()
