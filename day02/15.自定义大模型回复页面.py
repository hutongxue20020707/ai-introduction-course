"""
1.大模型的调用
    流程:
        1.导包
        2.创建客户端
        3.创建一个记忆盒子
        4.定义一个函数与大模型进行交互

2.搭建UI页面
    流程:
        1.导包        import gradio as gr
        2.搭建UI页面   with gr.Blocks() as demo:
        3.编写4个组件
            3.1 标题组件
            3.2 用户输入框组件
            3.3 用户问题展示组件
            3.4 AI大模型回复内容展示组件
        4.当用户在输入框组件输入完毕问题之后，敲回车键，就调用AI大模型进行内容回答，
          并将答案显示在 AI大模型回复内容展示组件
"""

# ===========================================================================
# 这一节 = 前 14 节的合体：
#   day01/01 认识大模型      → 会调接口
#   day01/06 流式输出        → （本节先用非流式，想加就照 day02/09 的写法）
#   day02/03 记忆盒子        → memoryBox 记住上下文
#   day02/13 事件绑定 click  → 这次用 submit（回车）
#   day02/14 表单提交        → 一次返回多个值，顺手清空输入框
#
# 前置条件：项目根目录的 .env 里有 DEEPSEEK_API_KEY
# 运行：python 15.自定义大模型回复页面.py
#    ★ 浏览器打开终端里打印的地址；关掉按 Ctrl + C
# ===========================================================================

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# ===========================================================================
# 一、大模型的调用
# ===========================================================================

# 1.导包
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

MODEL = "deepseek-flash"
SYSTEM_PROMPT = "你是一个耐心的 AI 助教。回答用中文，尽量简洁，必要时举例说明。"

# 2.创建客户端（密钥从项目根目录的 .env 读）
load_dotenv(override=True)
api_key = os.environ.get("DEEPSEEK_API_KEY")

client = None
if api_key:
    try:
        api_key.encode("ascii")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    except UnicodeEncodeError:
        client = None

# 3.创建一个记忆盒子
#    第一条是 system 人设。注意：清空对话时要把它留下来。
memoryBox = [{"role": "system", "content": SYSTEM_PROMPT}]


# 4.定义一个函数与大模型进行交互
#    返回值有 3 个，对上 UI 里的 3 个输出：
#       ① 用户问的问题（显示到"用户问题展示组件"）
#       ② AI 的回答（显示到"AI回复展示组件"）
#       ③ 空字符串（写回输入框 → 把它清空，这是 day02/14 学的技巧）
def chat_fn(question: str):
    question = (question or "").strip()          # 去掉两端空格，空输入直接拦掉

    if not question:
        return "", "（请先输入问题）", ""

    if client is None:
        return question, "（没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py）", ""

    memoryBox.append({"role": "user", "content": question})

    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=memoryBox,                  # 整个记忆盒子发给模型 → 它就能记住上文
            extra_body={"thinking": {"type": "disabled"}},
        )
        answer = res.choices[0].message.content or "（空回复）"
    except Exception as exc:                     # 网络/余额/密钥出错时别把页面搞崩
        return question, f"（调用失败：{type(exc).__name__}）\n{str(exc)[:300]}", ""

    memoryBox.append({"role": "assistant", "content": answer})

    return question, answer, ""


def clear_fn():
    """补充：清空对话（记忆盒子只留人设，两个展示框也清空）"""
    memoryBox.clear()
    memoryBox.append({"role": "system", "content": SYSTEM_PROMPT})
    return "", "", ""


# ===========================================================================
# 二、搭建UI页面
# ===========================================================================

# 1.导包（gradio 已在上面导入）

# 2.搭建UI页面
with gr.Blocks(title="我的 AI 问答页面") as demo:
    # 3.编写组件

    # 3.1 标题组件
    gr.Markdown("# 我的 AI 问答页面")
    gr.Markdown("> 在下面的输入框里输入问题，**敲回车**即可得到回答；它会记住本次对话的上下文。")

    # 3.2 用户输入框组件
    user_input = gr.Textbox(
        label="请输入你的问题",
        placeholder="例如：用一句话解释什么是大模型，然后按回车",
    )

    # 3.3 用户问题展示组件（只用来显示，不能编辑）
    question_show = gr.Textbox(label="你问的是", interactive=False)

    # 3.4 AI大模型回复内容展示组件
    answer_show = gr.Textbox(label="AI 的回答", lines=12, interactive=False)

    # 补充：清空对话的按钮（老师流程里没有，但调试多轮对话时很好用）
    with gr.Row():
        clear_btn = gr.Button("清空对话")

    # 4.绑定事件：在输入框里敲回车 → 调大模型 → 答案显示在回复组件里
    #   inputs  只传输入框
    #   outputs 传三个：问题展示、回答展示、输入框自己（第三个用来清空）
    user_input.submit(
        fn=chat_fn,
        inputs=user_input,
        outputs=[question_show, answer_show, user_input],
    )

    clear_btn.click(fn=clear_fn, outputs=[question_show, answer_show, user_input])

    gr.Markdown(
        "---\n"
        "> **四个组件对应关系**：3.1 标题（Markdown）→ 3.2 输入框（Textbox）"
        "→ 3.3 问题展示（Textbox，只读）→ 3.4 回答展示（Textbox，只读）。\n"
        "> 回车之后 `chat_fn` 返回三个值，按顺序填进 `outputs` 的三个组件里。"
    )


# 启动页面
if __name__ == "__main__":
    print("=" * 62)
    print("启动后会打印本地地址，例如 http://127.0.0.1:7860")
    print("用浏览器打开它；关掉程序按 Ctrl + C")
    print("=" * 62)
    demo.launch()
