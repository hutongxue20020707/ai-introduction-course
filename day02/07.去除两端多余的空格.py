"""
15. 去除两端空格

用户输入的内容，经常带着多余的空格：

    "  张三  "          ← 打字时习惯性多敲了空格
    "退出 "             ← 手滑多敲了一下
    "  你好\n"          ← 从别处复制粘贴过来的

这些空格看着不起眼，但会实实在在搞坏程序：

    · "退出 " != "退出"     → 用户明明输了退出，程序却判断不出来
    · 拼出来的提示词里多几个空格，模型理解也会受点影响
    · 当文件名、数据库字段、密码校验时更是致命的

解决办法 —— 三个方法：

    s.strip()   去掉两端（最常用）
    s.lstrip()  只去左边
    s.rstrip()  只去右边

    注意：只去【两端】，中间的空格原样保留。

运行：python 07.去除两端多余的空格.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

print("=" * 62)
print("一、三个方法长什么样")
print("=" * 62)

raw = "   今天天气好晴朗   "
print(f"原始字符串：[{raw}]")
print(f"    长度：{len(raw)}")

print()
print(f"strip()  两端都去：[{raw.strip()}]      长度 {len(raw.strip())}")
print(f"lstrip() 只去左边：[{raw.lstrip()}]")
print(f"rstrip() 只去右边：[{raw.rstrip()}]")

print()
print("★ 关键：中间的空格不会被去掉")
middle = "今天 天气 真好"
print(f"    [{middle}]  strip() 之后 → [{middle.strip()}]")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("二、strip() 默认去掉哪些字符")
print("=" * 62)
# 不传参数时，默认去掉的是"空白字符"：空格、制表符 \t、换行 \n、回车 \r
messy = " \t 带着制表符和换行的文本 \n "
print(f"    原始：[{messy}]  长度 {len(messy)}")
print(f"    strip 后：[{messy.strip()}]  长度 {len(messy.strip())}")

# 也可以指定要去掉的字符（比如两端的引号、逗号）
quoted = '"你好，世界"，'
strip_chars = '"' + "，"
print()
print(f"    原始：[{quoted}]")
print(f"    去掉两端的引号和逗号后：[{quoted.strip(strip_chars)}]")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("三、最容易踩的两个坑")
print("=" * 62)

# 坑 1：strip() 不会改变原字符串
s = "  前后有空格  "
s.strip()                     # ← 这行的结果被丢掉了
print(f"    坑1 直接 s.strip()：[{s}]          ← 原字符串没变！")
s = s.strip()                 # 必须赋值回去
print(f"        赋值之后 s = s.strip()：[{s}]")
print("        原因：python 的字符串是【不可变】的，所有处理都返回新字符串")

# 坑 2：忘了 strip，判断就会失效
print()
user_input = "退出 "          # 用户在"退出"后面多敲了一个空格
print(f"    坑2 用户输入：[{user_input!r}]")
print(f"        直接比较 user_input == '退出'         → {user_input == '退出'}")
print(f"        加 strip 后比较                        → {user_input.strip() == '退出'}")

print()
print("    ★ 这就是第 14 节那句代码的由来：")
print("          if question.strip() in ('退出', 'exit', 'quit', ''):")
print("      不写 .strip()，用户输入『退出 』就退不出去，程序会一直卡在循环里。")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("四、和 AI 课的关系：处理用户输入的标准姿势")
print("=" * 62)

def clean(text):
    """清洗用户输入：去掉两端空白，内部多个空格合并成一个（可选）"""
    return text.strip()

print("    在聊天程序里，input() 拿到的内容第一件事就是 clean()：")
for demo in ["  你好  ", "退出 ", "  什么是大模型", "  ", "再见"]:
    c = clean(demo)
    flag = "（空输入）" if c == "" else ""
    print(f"        原始 {demo!r:>16}  →  清洗后 {c!r:<14} {flag}")

print()
print("    处理顺序建议：input() → strip() → 判断是否为空/是否为退出命令 → 再发给模型")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("五、配合 input() 跑一下（在终端里试试）")
print("=" * 62)
print("    下面这行取消注释就能测：")
print("        text = input('随便输点什么（可带空格）：')")
print("        print(f'原文[{text}] → 清洗后[{text.strip()}]')")

# 想直接体验的话，把下面两行前面的 # 去掉
# text = input("随便输点什么（可带空格）：")
# print(f"    原文：[{text}]   清洗后：[{text.strip()}]")
