"""
submit 表单提交事件
作用：当我们在文本输入框中输入完毕内容之后，按回车键可以触发一个函数的执行

语法：
    组件.submit(fn=函数, inputs=传入的参数, outputs=函数的返回值)
    参数说明:
        fn      => 当我们点击组件之后要触发执行的函数
        inputs  => 当函数触发要运行时传入给函数执行的参数列表
        outputs => 当 fn 绑定的函数执行完毕后，返回的结果给对应的组件
"""

# ===========================================================================
# 本节最值钱的一个技巧（老师的代码里就有）：
#
#     def submit_fn(msg):
#         return f"用户输入的内容是： {msg}", ""      ← 一次返回两个值
#
#     user_input.submit(fn=submit_fn, inputs=user_input, outputs=[show, user_input])
#                                                          ↑ 第二个是输入框自己
#
#   第二个返回值是空字符串 → 写回输入框 → 输入框被清空。
#   这就是聊天框"发完一条消息，输入框自动清空"的实现原理。
#
# 其余补充：submit 与 click 双绑定、gr.Markdown 能写什么、多行输入框的回车问题、
#          最后一个"回车即问 AI"的实战。
#
# 前置条件：项目根目录的 .env 里有 DEEPSEEK_API_KEY（只有第五部分用到）
# 运行：python 14.表单提交事件.py
#    ★ 浏览器打开终端里打印的地址；关掉按 Ctrl + C
# ===========================================================================

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# 1.导包
import gradio as gr

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "deepseek-flash"

# 准备 DeepSeek 客户端（第五部分用）
load_dotenv(override=True)
api_key = os.environ.get("DEEPSEEK_API_KEY")

client = None
if api_key:
    try:
        api_key.encode("ascii")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    except UnicodeEncodeError:
        client = None


# 2.定义函数
def submit_fn(msg):
    # 注意：在python中如果函数返回多个值，我们可以使用逗号隔开，一次性返回多个值
    return f"用户输入的内容是： {msg}", ""   # 返回第二个值空字符串的目的是为了清空文本输入框中的内容


def ask_ai(question: str, temperature: float = 0.7):
    """第五部分：回车即发送，去问 AI"""
    question = (question or "").strip()
    if not question:
        return "（请先输入问题）", ""
    if client is None:
        return "（没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py）", ""
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
            temperature=float(temperature),
            extra_body={"thinking": {"type": "disabled"}},
        )
        return res.choices[0].message.content or "（空回复）", ""
    except Exception as exc:
        return f"（调用失败：{type(exc).__name__}）\n{str(exc)[:300]}", ""


# 3.搭建UI界面
with gr.Blocks(title="表单提交事件演示") as demo:
    # 编写组件
    gr.Markdown("# 标题1")
    gr.Markdown("## 标题2")
    gr.Markdown("# <center>欢迎来到我的gradio页面</center>")

    # 显示内容
    show = gr.Textbox(label="显示")
    # 让用户输入内容创建文本输入框
    user_input = gr.Textbox(placeholder="请输入你要了解的内容", label="输入框")
    # 给用户文本输入框绑定表单事件，当用户输入完毕内容后，敲回车，就将输入内容显示在 show 组件上
    user_input.submit(fn=submit_fn, inputs=user_input, outputs=[show, user_input])

    gr.Markdown(
        "> 敲回车试试：上面的「显示」填上了你输入的内容，同时**输入框自动清空了** —— "
        "靠的就是 `outputs=[show, user_input]` 加上 `return 内容, \"\"` 这半行。"
    )

    # =======================================================================
    # 补充 1：submit 和 click 可以绑在同一个输入框上
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("### 补充 1：同一个输入框，回车和按钮都能用")

    msg2 = gr.Textbox(label="输入内容", placeholder="按回车，或者点右边的按钮")
    send_btn = gr.Button("发送（click 事件）", variant="primary")
    result2 = gr.Textbox(label="输出", interactive=False)

    msg2.submit(fn=submit_fn, inputs=msg2, outputs=[result2, msg2])      # 回车
    send_btn.click(fn=submit_fn, inputs=msg2, outputs=[result2, msg2])   # 点击

    gr.Markdown("> 同一个函数可以绑在多个事件上：用户按回车也行、点按钮也行，都能提交。")

    # =======================================================================
    # 补充 2：gr.Markdown 能写什么
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("### 补充 2：gr.Markdown 里能写什么")
    gr.Markdown(
        """
**加粗**、*斜体*、`行内代码`

- 无序列表第一项
- 无序列表第二项

1. 有序列表第一步
2. 有序列表第二步

| 组件 | 作用 |
|---|---|
| Textbox | 文本输入/输出 |
| Slider | 滑块调参 |
| Button | 按钮 |
| Markdown | 显示富文本 |

```python
print("Markdown 里还能放代码块")
```

> 引用块适合写提示和注意事项。

<center>这一行是 HTML 的居中对齐（Markdown 里可以直接写 HTML）</center>
        """
    )
    gr.Markdown(
        "> 小提醒：如果上面那行**没居中**，是因为 gradio 默认会过滤一部分 HTML。"
        "可以改成 `gr.Markdown(..., sanitize_html=False)` 让它放行。"
    )

    # =======================================================================
    # 补充 3：多行输入框里回车会换行
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("### 补充 3：多行输入框（lines > 1）里按回车通常是换行")
    multi = gr.Textbox(
        label="多行输入框",
        lines=3,
        placeholder="在这里回车多半只是换行，不一定会触发 submit",
    )
    multi_out = gr.Textbox(label="多行输出", interactive=False)
    multi.submit(fn=submit_fn, inputs=multi, outputs=[multi_out, multi])
    gr.Markdown("> 所以聊天框一般用**单行**输入框（不写 lines），或者额外放个按钮兜底。")

    # =======================================================================
    # 补充 4：实战 —— 回车就能问 AI（顺便自动清空输入框）
    # =======================================================================
    gr.Markdown("---")
    gr.Markdown("### 补充 4：实战 —— 输入问题，按回车直接问 AI")
    with gr.Row():
        with gr.Column(scale=1):
            question = gr.Textbox(
                label="你的问题（单行，回车即发送）",
                placeholder="例如：用一句话解释什么是大模型，然后按回车",
            )
            temperature = gr.Slider(label="temperature", minimum=0.0, maximum=1.5, value=0.7, step=0.1)
            ask_btn = gr.Button("发送（点击）", variant="primary")
        with gr.Column(scale=2):
            answer = gr.Textbox(label="AI 的回答", lines=12)

    question.submit(fn=ask_ai, inputs=[question, temperature], outputs=[answer, question])   # 回车
    ask_btn.click(fn=ask_ai, inputs=[question, temperature], outputs=[answer, question])     # 点击


# 测试
if __name__ == "__main__":
    print("=" * 62)
    print("启动后会打印本地地址，例如 http://127.0.0.1:7860")
    print("用浏览器打开它；关掉程序按 Ctrl + C")
    print("=" * 62)
    demo.launch()
