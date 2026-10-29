"""
16. python 的 in 和 not in

老师笔记原话：

    用于校验b是否包含a内容  => a in b        如果包含返回True,否则就返回False
    用于校验b是否不包含a内容 => a not in b   如果b不包含a就返回True, 否则返回False

一句话记忆：**小的在大里面** → a in b，就是"a 在不在 b 里面"。

返回值永远是布尔值 True / False，所以能直接放进 if 里当条件用。

为什么 AI 课要用它？
    · 判断用户输入是不是"退出/再见"这类命令     → 第 14、15 节就用到了
    · 检查用户说的话里有没有某个关键词           → 走不同的处理分支
    · 检查模型回复里有没有出现"错误""抱歉"之类的词 → 做兜底

运行：python 08.in和not_in的使用.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# ===========================================================================
# 一、老师课堂的例子（原样）
# ===========================================================================
a = "晴朗"
b = "今天天气好晴朗，处处好风光"

# if a in b:
#     print(f"b的内容中有包含{a}内容")
# else:
#     print(f"b的内容中没有包含{a}内容")


if a not in b:
    print(f"b的内容中没有包含{a}内容")
else:
    print(f"b的内容中有包含{a}内容")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("二、它到底返回什么：True / False")
print("=" * 62)
print(f"    a = {a!r}")
print(f"    b = {b!r}")
print()
print(f"    a in b       → {a in b}        （b 里有『晴朗』，所以是 True）")
print(f"    a not in b   → {a not in b}    （取反，所以是 False）")
print()
print(f"    换个词试试：'下雨' in b  → {'下雨' in b}")
print(f"                '下雨' not in b → {'下雨' not in b}")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("三、三个注意点")
print("=" * 62)

print("    [注意 1] 顺序别记反：小的在前面")
print(f"        '晴朗' in b   → {'晴朗' in b}     √ 对")
print(f"        b in '晴朗'   → {b in '晴朗'}     × 反了，结果必然为 False")
print("        记法：小在大里面。『晴朗』在『今天天气好晴朗…』里面。")

print()
print("    [注意 2] 区分大小写")
print(f"        'python' in 'Python 是一门语言'  → {'python' in 'Python 是一门语言'}")
print("        想忽略大小写：先两边都转小写再比")
text = "Python 是一门语言"
print(f"        text.lower() 之后再判断          → {'python' in text.lower()}")

print()
print("    [注意 3] 空格也是字符，会被算进去")
print(f"        '晴朗' in '晴朗 '   → {'晴朗' in '晴朗 '}    ← 末尾有空格照样能找到")
print(f"        '晴朗 ' in '晴朗'   → {'晴朗 ' in '晴朗'}    ← 但你要找的词自己带空格，就找不到了")
print("        → 从用户输入里找关键词之前，先 strip()（第 15 节）")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("四、不只能用在字符串上：列表、字典都能用")
print("=" * 62)

fruits = ["苹果", "香蕉", "橘子"]                 # 第 13 节的列表
print(f"    列表：{fruits}")
print(f"        '苹果' in fruits      → {'苹果' in fruits}")
print(f"        '西瓜' in fruits      → {'西瓜' in fruits}")
print(f"        '西瓜' not in fruits  → {'西瓜' not in fruits}")

print()
print("    in 用在列表上，判断的是『有没有这个元素』；")
print("    如果列表里装的是字典，判断的是『有没有这一整个字典』：")

messages = [{"role": "user", "content": "你好"}]   # 第 12 节的记忆盒子
one = {"role": "user", "content": "你好"}
print(f"        messages = {messages}")
print(f'        直接找 "你好" 这个字符串        → {"你好" in messages}   ← 找不到，因为列表里装的是字典')
print(f"        找整个字典 one                  → {one in messages}   ← 这才是对的")
print("        → 想按内容找，得遍历：any('你好' in m['content'] for m in messages)")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("五、回到 AI 课：三个真实用法")
print("=" * 62)

print("    [用法 1] 判断用户输入是不是退出命令（第 14 节那行代码的真相）")
command = "退出 "
if command.strip() in ("退出", "exit", "quit", ""):
    print(f"        用户输入 {command!r} → 是退出命令，程序结束")
else:
    print(f"        用户输入 {command!r} → 不是退出命令，继续聊天")

print()
print("    [用法 2] 检查用户说的话里有没有关键词，走不同分支")
user_says = "我最近在学人工智能，有点难"
if "人工智能" in user_says or "AI" in user_says:
    print(f"        用户说：{user_says}")
    print("        → 检测到『人工智能』关键词，可以给他推荐入门路线")
else:
    print("        → 没提到 AI，按普通问题处理")

print()
print("    [用法 3] 检查模型回复里有没有需要警惕的内容")
reply = "抱歉，我不太确定这个问题，建议你查一下官方文档。"
for word in ("抱歉", "错误", "无法"):
    if word in reply:
        print(f"        回复里出现了 {word!r} → 可以提示用户：这次回答可能不太可靠")
        break
else:
    print("        回复看起来正常")

# ---------------------------------------------------------------------------
print()
print("=" * 62)
print("六、小练习")
print("=" * 62)
print("    1) 让用户输入一句话，判断里面有没有『天气』两个字")
print("    2) 做一个命令列表 ['帮助', '清空', '退出']，用 in 判断用户输入的是不是有效命令")
print("    3) 用 not in 实现：如果输入里没有『谢谢』，就提醒 AI 回复要更礼貌一点")
