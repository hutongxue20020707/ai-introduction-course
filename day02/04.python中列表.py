"""
13. python 列表

列表（list）= 一排格子，按顺序放东西，用中括号 [ ] 写。

    list  = ["张三", "李四", "王五", "赵六", "钱七"]
    下标  =   0       1       2       3       4

    ★ 下标从 0 开始！第一个元素是 [0]，不是 [1] —— 新手最容易搞错的地方。

为什么学 AI 要先学列表？
    上一节（12）的"记忆盒子" memoryBox 就是一个列表：
        memoryBox.append({...})   → 往末尾加一条对话
        memoryBox[-6:]            → 取最近 3 轮
    而发给模型的 messages 本身，也是"装着字典的列表"：
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    所以这节课学会了，记忆盒子才真正看得懂。

运行：python 04.python中列表.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# ===========================================================================
# 一、老师课堂的例子（变量名也跟老师保持一致，叫 list）
# ===========================================================================
list = ["张三", "李四", "王五", "赵六", "钱七"]
#  下标:  0       1       2       3       4

# 打印列表
print("[老师的例子]")
print(list)

# 通过下标来获取列表中的成员
name = list[2]
print(name)                 # 王五

# 获取列表的第 5 个成员（下标 4）
print(list[4])              # 钱七

# 获取列表的长度（列表中元素的个数）
print(len(list))            # 5

# 获取列表的最后一个成员
print(list[len(list) - 1])  # 钱七（5-1=4，所以是最后一个）

# 向列表的最后添加新的元素
list.append("赵柳")
print(list)                 # 多了一个"赵柳"

# 修改列表中的元素
list[0] = 100
print(list)                 # 第一个"张三"被换成 100（列表里可以混装不同类型）

# 删除列表中的元素
list.remove("李四")
print(list)                 # "李四"被删掉了

# ===========================================================================
# 二、补充：几个天天要用的操作
# ===========================================================================
print()
print("[补充 1] 负下标：从后面数，-1 就是最后一个")
nums = [10, 20, 30, 40, 50]
print("    最后一个：", nums[-1])     # 50
print("    倒数第二个：", nums[-2])   # 40
# 所以上一节那句 memoryBox[-6:] 就是"从倒数第 6 个取到最后"

print()
print("[补充 2] 切片：一次取一段  [开始:结束]（含头不含尾）")
print("    nums[1:4]  →", nums[1:4])    # [20, 30, 40]
print("    nums[:3]   →", nums[:3])     # 前 3 个
print("    nums[2:]   →", nums[2:])     # 从第 3 个到结尾
print("    nums[-2:]  →", nums[-2:])    # 最后 2 个（记忆盒子取最近几轮就用它）

print()
print("[补充 3] 判断在不在里面 / 数一数出现几次")
print("    30 在列表里吗：", 30 in nums)
print("    99 在列表里吗：", 99 in nums)
print("    数字 1 在 [1,2,1,3] 里出现几次：", [1, 2, 1, 3].count(1))

print()
print("[补充 4] 其他常用操作")
nums.insert(0, 5)                  # 在下标 0 处插入
print("    插入后：", nums)
last = nums.pop()                  # 弹出（拿走）最后一个
print(f"    弹出的是 {last}，剩下：", nums)
nums.sort(reverse=True)            # 排序（倒序）
print("    倒序排完：", nums)
nums.clear()                       # 清空
print("    清空后：", nums, "长度", len(nums))

print()
print("[补充 5] 下标越界会报错 —— 这是最常见的报错之一")
short = [1, 2, 3]
try:
    print(short[10])
except IndexError as exc:
    print("    报错：", exc)
    print(f"    原因：列表只有 {len(short)} 个元素（下标 0~{len(short) - 1}），你却要下标 10")
print("    取最后一个永远用 short[-1] 或 short[len(short)-1]，别写死数字")

# ===========================================================================
# 三、命名坑：老师的写法能跑，但建议改个名字
#     list 是 Python 自带的内置类型名，用它当变量名会把它"盖住"
# ===========================================================================
print()
print("[补充 6] 别用 list 当变量名")
print("    上面那个变量 list 把 Python 内置的 list 类型覆盖了：")
try:
    print("    想用内置 list() 把字符串转成列表：", list("abc"))
except TypeError as exc:
    print("    报错：", exc, "  ← 'list' 已经被我们自己的变量占用了")
print("    建议改名：names / my_list / fruits …… 想更保险可以加引号提醒自己")

# ===========================================================================
# 四、回到 AI：记忆盒子就是这么一个列表
# ===========================================================================
print()
print("[和 AI 课的连接] 记忆盒子 messages 就是个列表")

messages = []                                     # ← 记忆盒子
messages.append({"role": "user", "content": "我是张三，我喜欢吃苹果"})
messages.append({"role": "assistant", "content": "你好，张三！记住啦。"})
messages.append({"role": "user", "content": "我是谁？"})

print("    现在有", len(messages), "条记录")
print("    最后一条是：", messages[-1])            # 负下标取最后一条
print("    最近 2 轮：", messages[-2:])            # 切片取最近
print()
print("    这就是 12 节里 memoryBox 的全部真相：")
print("        提问 → append；回答 → append；发出去 → messages=整个列表；")
print("        太长了 → 用切片 [-6:] 只留最近几轮")
