"""
14. 接收用户在控制台输入的内容

老师笔记原话：

    当我们想要将一个内容输出在控制台中时，可以使用        print()
    当我们想要从控制台接受用户输入的内容时，可以使用      input()
        注意：
            input会阻止代码往后继续运行
            input函数得到的结果一定是一个字符串类型

这两条"注意"非常关键，本项目把它们都实测了一遍（见下面 [注意 1] [注意 2]）。

为什么 AI 课要学 input()？
    前几节我们把对话写死在代码里（p1、p2）。有了 input()，
    才能真正"你一句、我一句"地聊天 —— 下一节的聊天机器人就靠它。

运行：python 06.接收用户在控制台输入信息.py
    ★ 必须在【终端】里运行，它才会停下来等你打字。
      TraeCode 的"输出"面板是只读的，在那儿打字没人理你。
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# ===========================================================================
# 一、老师课堂的例子（原样）
# ===========================================================================
print("程序开始")

name = input("请输入你的姓名：")
age = input("请输入你的年龄：")
print(f"你的名字是：{name},{type(name)}")
print(f"你的年龄是：{age},{type(age)}")

print("程序结束")

# ===========================================================================
# 二、两个注意点，逐个验证
# ===========================================================================
print()
print("=" * 60)
print("[注意 1] input() 会把程序「卡」在那里，直到你按下回车")
print("=" * 60)
print("    上面那两次 input 就是这样：不输入内容，后面的代码一步都不会执行。")
print("    → 这就是老师说的「input 会阻止代码往后继续运行」。")

print()
print("=" * 60)
print("[注意 2] input() 得到的结果一定是【字符串】")
print("=" * 60)
print(f"    你刚输入的年龄是 {age!r}，类型是 {type(age)}")
print("    注意：即使你输入的是 18，拿到手的也是字符串 '18'，不是数字 18")
print()
print(f"    验证一下：'18' + '18' 得到的是 {age + age!r}   ← 字符串拼接，不是加法")
print("    想当数字用，必须先转换：")
try:
    print(f"        int(age) + 18   → {int(age) + 18}")
    print(f"        float(age) / 2  → {float(age) / 2}")
except ValueError:
    print(f"        （你输入的是 {age!r}，不是数字，所以转换失败 —— 正好演示了 ValueError）")

# ---------------------------------------------------------------------------
# 乱输入会怎样？ValueError
# ---------------------------------------------------------------------------
print()
print("    [演示] 如果输入的不是数字，int() 会报错：")
try:
    int("十八岁")
except ValueError as exc:
    print(f"        报错：{exc}")
    print("        → 所以真实项目里要判断输入是否合法，或者用 try/except 兜住")

# ---------------------------------------------------------------------------
# 类型转换速查
# ---------------------------------------------------------------------------
print()
print("    转换速查：")
print("        int('18')     →", int("18"), "  字符串转整数")
print("        float('1.5')  →", float("1.5"), "  字符串转小数")
print("        str(123)      →", repr(str(123)), "  数字转字符串")
print("        bool('')      →", bool(""), "  空字符串是 False，非空是 True")

# ===========================================================================
# 三、小实战：while + input = 能一直聊下去
#     （复习第 07 课的循环；这里先不接 AI，只做本地问答）
# ===========================================================================
print()
print("=" * 60)
print("小实战：连续问答（输入 退出 就结束）")
print("=" * 60)

while True:                                   # 第 07 课学的 while
    question = input("你：")

    if question.strip() in ("退出", "exit", "quit", ""):
        print("系统：好的，结束。")
        break                                 # 跳出循环

    # 这里先用最简单的本地逻辑回应，下一节换成真正的 AI
    print(f"系统：你说的是「{question}」，一共 {len(question)} 个字。")

# ===========================================================================
# 四、预告：把 input() 接到 AI 上，就是聊天机器人了
#     把 CHAT_WITH_AI 改成 True 试试（要有 .env 里的密钥）
# ===========================================================================
CHAT_WITH_AI = False

if CHAT_WITH_AI:
    import os

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(override=True)
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("没有读到 DEEPSEEK_API_KEY，请先运行 day01/07.校验环境变量配置是否成功.py")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    memoryBox = []                            # 第 12 课的记忆盒子（列表）

    print()
    print("=" * 60)
    print("和 AI 聊天（输入 退出 结束）")
    print("=" * 60)
    while True:
        question = input("你：")
        if question.strip() in ("退出", "exit", "quit", ""):
            print("AI：再见！")
            break

        memoryBox.append({"role": "user", "content": question})     # 第 13 课：列表 append
        res = client.chat.completions.create(
            model="deepseek-flash",
            messages=memoryBox,                                     # 整个记忆盒子发给 AI
            extra_body={"thinking": {"type": "disabled"}},
        )
        answer = res.choices[0].message.content
        memoryBox.append({"role": "assistant", "content": answer})
        print("AI：", answer)

# ===========================================================================
# 五、常见问题
# ===========================================================================
# 1) 程序一闪而过 / 没等我输入就结束
#    → 大多数是把输入重定向了（比如 IDE 的"输出"面板），或者点的是"运行但不进终端"。
#      在 TraeCode 里用【终端】标签页运行：终端 → 新建终端 → python 14.xxx.py
#
# 2) EOFError: EOF when reading a line
#    → 程序在等输入，但输入流已经结束了（比如用管道喂完数据了）。
#      交互运行时不会遇到；写自动化测试时会遇到，可以给 input 配一个默认值。
#
# 3) ValueError: invalid literal for int()
#    → 输入的字符串不能转成数字（输入了"十八"却要 int），要自己判断或用 try/except。
#
# 4) 想让 input 有默认值（什么都不输入就用默认）：
#      text = input("请输入（直接回车=张三）：").strip() or "张三"
#
# 5) 用管道 / 文件给程序喂中文输入时出现乱码（本机写这一节时实测踩到）
#    → Python 读 stdin 用的是【本地编码】（中文 Windows 是 GBK），
#      而你的输入文件往往是 UTF-8 保存的 —— 编码不一致，中文就变成 "锘垮紶涓?"。
#      手动在终端里打字不会有这个问题（终端走的是 Unicode 通道）。
#      要写自动化测试时，把输入文件按 ANSI(GBK) 保存即可：
#          Set-Content -Path in.txt -Value @('张三','18','退出') -Encoding Default
