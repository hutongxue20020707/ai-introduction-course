"""
11. langchain 中的智能体发送邮件

老师的写法：把"发邮件"这件事包成 @tool，交给智能体：

    @tool(description="用于发送邮件")
    def send_email(message):
        # 这是一个发送邮件的函数
        import smtplib
        from email.mime.text import MIMEText

        # 1.创建邮箱对象
        msg = MIMEText(message, "plain", "utf-8")
        # 2.发送人的邮箱账号
        msg["From"] = "ouf_cs@hqyj.com"
        # 3.接收人的邮箱账号
        receivers = ["407762121@qq.com"]
        # ……连接 SMTP、登录、sendmail

⚠️ 老师那次运行其实是【崩掉】的（截图里那段 traceback）：
   程序在 agent.invoke() 里抛异常，整个智能体直接挂。
   原因：工具函数里一旦出错（SMTP 连不上 / 授权码不对 / 收件人被拒），
        异常会一路往上抛，agent 没有兜住 —— 用户看到的就是一堆红色报错。

✔ 本文件在老师骨架上的四点改进：
    ① 发件账号、授权码、SMTP 服务器全部从 .env 读，不写死在代码里
    ② 工具里 try/except：失败时"返回一句错误说明"而不是抛异常
       → 模型能看到「发送失败：xxx」，然后如实转告用户，程序不会崩
    ③ 加上 Subject（主题），不加容易被判为垃圾邮件
    ④ 把"收件人 / 主题"做成参数，让模型从自然语言里自己提取

运行：python 11.langchain中的智能体发送邮件.py
    （会真的发一封邮件到你 .env 里 MAIL_TO 那个地址）
"""

import os
import smtplib
import sys
from email.header import Header
from email.mime.text import MIMEText

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# 一、邮件配置：全部来自 .env
# ---------------------------------------------------------------------------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")           # 发件人邮箱
SMTP_AUTH = os.getenv("SMTP_AUTH_CODE", "")      # SMTP 授权码（不是登录密码！）
DEFAULT_TO = os.getenv("MAIL_TO", SMTP_USER)

llm = ChatOpenAI(
    model="deepseek-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0,
)


# ---------------------------------------------------------------------------
# 二、工具：发邮件
#    参考老师的写法（MIMEText + From + receivers + smtplib），但做了上面那四点改进
# ---------------------------------------------------------------------------
@tool(description="发送邮件。需要收件人邮箱(to)、邮件正文(message)，可选主题(subject)。")
def send_email(to: str, message: str, subject: str = "来自 AI 助手的邮件") -> str:
    """用 SMTP 发送一封纯文本邮件，返回发送结果（成功或失败原因）。"""
    if not SMTP_USER or not SMTP_AUTH:
        return "发送失败：.env 里没有配置 SMTP_USER / SMTP_AUTH_CODE"

    to = (to or "").strip() or DEFAULT_TO
    if "@" not in to:
        return f"发送失败：收件人邮箱格式不对（{to}）"

    try:
        # 1.创建邮箱对象
        msg = MIMEText(message, "plain", "utf-8")
        # 2.发送人的邮箱账号
        msg["From"] = SMTP_USER
        # 3.接收人的邮箱账号
        msg["To"] = to
        # 4.主题（不加这一行，很容易被判成垃圾邮件）
        msg["Subject"] = Header(subject, "utf-8")

        # 5.连接 QQ 邮箱的 SMTP 服务器并发送（465 端口要用 SSL）
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.login(SMTP_USER, SMTP_AUTH)
            server.sendmail(SMTP_USER, [to], msg.as_string())

        return f"发送成功：已发送到 {to}，主题「{subject}」"

    except smtplib.SMTPAuthenticationError:
        # 最常见的错：把 QQ 登录密码当成授权码了
        return ("发送失败：登录被拒。QQ 邮箱必须用【SMTP 授权码】而不是登录密码；"
                "另外要确认邮箱设置里已开启 POP3/SMTP 服务。")
    except Exception as exc:
        # 关键：把异常变成"一句可读的话"返回给模型，而不是往上抛
        return f"发送失败：{exc.__class__.__name__} {exc}"


# ---------------------------------------------------------------------------
# 三、智能体
# ---------------------------------------------------------------------------
agent = create_agent(
    llm,
    tools=[send_email],
    system_prompt=("你是一个邮件助手。用户让你发邮件时，先确认收件人和内容，"
                   "然后调用 send_email 工具；工具返回结果后，如实告诉用户成功还是失败。"),
)


def say(text: str) -> str:
    """发一句话给智能体，把工具调用过程也打印出来"""
    result = agent.invoke({"messages": [{"role": "user", "content": text}]})
    for m in result["messages"]:
        if getattr(m, "type", "") == "ai" and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                args = tc["args"]
                shown = {k: (str(v)[:40] + "..." if len(str(v)) > 40 else v) for k, v in args.items()}
                print(f"    [ai 决定调用] {tc['name']}({shown})")
    return str(result["messages"][-1].content)


if __name__ == "__main__":
    print("=" * 66)
    print("【1】让智能体给你发一封邮件")
    print("=" * 66)

    question = (f"请给 {DEFAULT_TO} 发一封邮件，"
                f"主题是「DeepSeek 智能体测试」，"
                f"内容是：你好，这封邮件是由 DeepSeek 智能体通过 function calling 自动发送的，"
                f"说明「模型 + 工具」这条链路已经跑通了。")
    print("我：", question)
    print("AI：", say(question))

    print()
    print("=" * 66)
    print("【2】故意给一个错误邮箱，看工具怎么'优雅失败'")
    print("=" * 66)
    bad = send_email.invoke({"to": "这不是邮箱", "message": "测试", "subject": "测试"})
    print("  工具直接返回：", bad)
    print()
    print("  ↑ 注意：它返回的是一句【说明】，不是抛异常。")
    print("    所以即使发信失败，智能体也不会崩 —— 这就是老师那次报错的根因所在。")

    print()
    print("=" * 66)
    print("【3】换个说法再发一次（验证模型能自己提取收件人/主题）")
    print("=" * 66)
    q2 = f"帮我给 {DEFAULT_TO} 发条问候，主题叫「早上好」，正文一句话就行。"
    print("我：", q2)
    print("AI：", say(q2))

    print()
    print("=" * 66)
    print("小结")
    print("=" * 66)
    print("""  1. 工具 = 普通函数 + @tool，参数写得越清楚，模型填得越准
  2. 敏感配置（账号、授权码）一律放 .env，代码里只读不写
  3. 工具里必须 try/except，把异常变成"一句话结果"返回
     —— 否则一次失败，整个智能体就崩（老师那份就是这个问题）
  4. QQ 邮箱要点：465 + SMTP_SSL、用授权码登录、别忘 Subject""")
