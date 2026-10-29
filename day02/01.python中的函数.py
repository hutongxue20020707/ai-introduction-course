"""
10. python 中的函数

函数 = 把"一段要做的事"打包起来，起个名字，以后想用就喊一声。
不用函数的话，同样的代码要复制粘贴好几遍，改一处就得改好几处。

一个函数由三部分组成：

    函数名       def 名字(参数):
    参数         括号里的东西，调用时传进去
    返回值       return 后面的东西，函数做完事"交回来"的结果

老师课上的例子是一个"登录"函数：传进来用户名和密码，返回登录成功或失败。

运行：python 01.python中的函数.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# ===========================================================================
# 一、老师课堂的例子（原样保留）
# ===========================================================================

# 定义一个用户登录的函数（功能）
def login(username, password):
    if username == "admin" and password == "123456":
        return "登录成功！"
    else:
        return "登录失败！"


# 调用 login 登录方法，传入用户名和密码
zs = login("zhangsan", "123456")
ad = login("admin", "12345")
admin = login("admin", "123456")

# 打印函数返回的结果
print("[老师的例子]")
print(zs)        # zhangsan 不是 admin          → 登录失败！
print(ad)        # 密码 12345 ≠ 123456           → 登录失败！
print(admin)     # admin + 123456 都对            → 登录成功！

# ===========================================================================
# 二、函数怎么读、怎么写
# ===========================================================================
#   def login(username, password):     ← def = 定义(define)，括号里是"参数"
#       if ...: return "登录成功！"     ← return = 把结果交回去，函数立刻结束
#       else:   return "登录失败！"
#
#   login("admin", "123456")           ← 调用：把参数按位置传进去
#
#   两个关键点：
#   1) 光定义不调用，函数不会执行（上面 def 完，必须有 login(...) 那一行）
#   2) return 之后函数就结束了，后面再写代码也不会执行

print()
print("[补充 1] 演示 '光定义不调用就不会执行'")
def say_hello():
    print("    你好，我是函数内部的一行代码")

print("    这是函数外面的代码")
say_hello()          # 把上面这行注释掉，函数里那句话就不会打印
say_hello()          # 可以调用多次，不用重写代码

# ===========================================================================
# 三、补充：几个常用的写法
# ===========================================================================
print()
print("[补充 2] 有默认值的参数")

def login2(username, password="123456"):     # 默认密码
    if username == "admin" and password == "123456":
        return "登录成功！"
    return "登录失败！"

print("    不传密码：", login2("admin"))               # 用默认值 → 成功
print("    传了密码：", login2("admin", "000000"))     # 覆盖默认值 → 失败
print("    关键字参数：", login2(password="123456", username="admin"))   # 顺序可颠倒

print()
print("[补充 3] 没有 return 的函数，返回的是 None")

def print_only(text):
    print(f"    我只会打印：{text}")          # 只做事，不交结果

result = print_only("一句话")
print("    它的返回值是：", result)           # None

print()
print("[补充 4] 多个返回值（其实是一个元组）")

def min_max(nums):
    return min(nums), max(nums)

low, high = min_max([3, 1, 4, 1, 5, 9])
print(f"    最小值 {low}，最大值 {high}")

# ===========================================================================
# 四、为什么学 AI 要用函数？
#     把"调用模型"这件事打包起来。以后不管问什么，一行就够：
#         answer = ask("你的问题")
#     下一节的聊天机器人，核心就是这样一个函数。
# ===========================================================================
print()
print("[补充 5] 把调用 DeepSeek 封装成函数")

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
_api_key = os.environ.get("DEEPSEEK_API_KEY")
if _api_key:
    _client = OpenAI(api_key=_api_key, base_url="https://api.deepseek.com")

    def ask(prompt, system="你是一个耐心的 Python 助教，回答要简短"):
        """问模型一句话，返回它的回答。"""
        res = _client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            extra_body={"thinking": {"type": "disabled"}},
        )
        return res.choices[0].message.content

    # 封装之后，问问题就是一行代码
    print("    问：什么是函数？")
    print("    答：", ask("用一句话解释 python 里的函数"))
    print()
    print("    换个问题，还是同一个函数：")
    print("    答：", ask("用一句话解释什么是 API 密钥"))
else:
    print("    （没读到 DEEPSEEK_API_KEY，跳过这一部分；先跑 day01/07 校验脚本）")

# ===========================================================================
# 五、小练习
# ===========================================================================
# 1) 写一个函数 add(a, b)，返回两个数相加的结果，调用它打印出来
# 2) 写一个函数 is_even(n)，判断 n 是不是偶数，返回 True/False
# 3) 给 ask() 加一个参数 temperature，先不用管它什么意思，能传进去就行
