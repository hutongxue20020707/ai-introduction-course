"""
python 中的模板字符串（在提示词工程里也叫"提示词模板"）

同样一件事 —— "把变量塞进一段文字里"，Python 有好几种写法：

    1) 老式 % 格式化          "你好 %s" % name
    2) str.format()           "你好 {}".format(name)
    3) f 表达式（下一课 05）   f"你好 {name}"
    4) 模板字符串 Template     Template("你好 $name").substitute(name=name)

这一课的重点是第 4 种：用 $变量 占位。
它的好处是"模板"和"数据"彻底分开 —— 一大段提示词可以原样存着，
运行时再把内容填进去，特别适合提示词工程。

运行：python 04.prompt中的字符串.py
"""

from string import Template

# ---------------------------------------------------------------------------
# 一、四种写法摆在一起看
# ---------------------------------------------------------------------------
name = "张三"
print("1) % 格式化      ：", "你好，%s" % name)
print("2) str.format()  ：", "你好，{}".format(name))
print("3) f 表达式      ：", f"你好，{name}")

t = Template("你好，$name")
print("4) 模板字符串    ：", t.substitute(name=name))
print()

# 多人场景能看出区别：模板里的同一个变量会被填多次
t2 = Template("$who 你好，欢迎 $who 来到长沙")
print("同一个变量填两次：", t2.substitute(who="张三"))
print()

# ---------------------------------------------------------------------------
# 二、实战：把"少样本提示词"做成模板（对应第 03 课）
# 模板是整个写死的，只有 $ 开头的几处需要运行时填 —— 这就是它的价值
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = Template("""你的任务是识别用户输入的信息，提取信息中的时间(time)、地点(location)、人物(person)

示例：
    $example_input
    $example_output

现在请处理下面这条输入：
$input_txt

限制：以JSON格式进行输出，不要输出任何解释文字""")

filled_prompt = PROMPT_TEMPLATE.substitute(
    example_input="在本周三，我和张三一起去长沙世界之窗玩了一下",
    example_output='{"time": "本周三", "location": "长沙世界之窗", "person": "我和张三"}',
    input_txt="我计划着周末和小丽一起去爬岳麓山，本来还想带张三一起去，但是他要工作，所以就算了",
)

print("=" * 60)
print("用模板拼出来的提示词：")
print("=" * 60)
print(filled_prompt)
print()

# 换个输入再拼一次，模板一个字都不用改
filled_prompt2 = PROMPT_TEMPLATE.substitute(
    example_input="上周五，李四一个人去了橘子洲",
    example_output='{"time": "上周五", "location": "橘子洲", "person": "李四"}',
    input_txt="明天早上我和小王打算去省博物馆看展览",
)
print("换一组数据再拼一次（模板没动）：")
print(filled_prompt2)
print()

# ---------------------------------------------------------------------------
# 三、substitute 和 safe_substitute 的区别
# ---------------------------------------------------------------------------
# substitute：有占位符没填，直接报错 —— 拼提示词时推荐用它，
#             因为"缺参数"是必须立刻发现的 bug，不能带着缺陷发给模型。
try:
    Template("你好，$name").substitute()
except KeyError as exc:
    print("substitute 遇到没填的变量会报错：KeyError", exc)

# safe_substitute：没填的占位符原样留着，不报错
print("safe_substitute 不报错：", Template("你好，$name").safe_substitute())
print()

# ---------------------------------------------------------------------------
# 四、什么时候用模板字符串，什么时候用 f 表达式
# ---------------------------------------------------------------------------
print("""怎么选：
    · 模板就写在当前这几行代码旁边   -> 用 f 表达式（f"{变量}"），最方便
    · 模板很长、要重复用、想单独存成文件 -> 用 Template，模板和数据分开
    · 模板里本来就有花括号（比如 JSON 示例） -> f 表达式要写 {{ }} 很麻烦，Template 更清爽
""")
