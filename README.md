# 人工智能导论 · 课程实践项目（day01 – day03）

> 一条线走完：**调通一次 DeepSeek API → 会用提示词 → 会写多轮对话 → 做成网页 → 会让模型调用工具 → 写出能查天气、查豆瓣、发邮件的 Agent。**

全项目 **34 个可运行脚本**，每个都能独立跑；配套 4 份笔记和 2 份参考资料。

---

## 一、这个项目是什么

| 阶段 | 目录 | 内容 | 代码量 |
|---|---|---|---|
| 第一天 · AI 基础 | `day01/` | 认识大模型、提示词（prompt / 少样本 / 模板 / f 表达式）、流式输出、环境与密钥 | 8 课 + 4 份笔记 |
| 第二天 · Python + 多轮对话 + 网页 | `day02/` | 函数/列表/循环/字符串处理 → 多轮对话与记忆 → Gradio 网页（组件/布局/事件） | 15 课 |
| 第三天 · 工具调用与 Agent | `day03/` | 实时信息问题 → function calling → ReAct → 免 Key 接口 → 多工具 Agent → LangChain（invoke/stream/batch/Message）→ 长期记忆 → 发邮件 | 11 课 + 2 份资料 |

技术栈：**Python 3.12 + DeepSeek（OpenAI 兼容接口）+ Gradio + LangChain / LangGraph**

---

## 二、快速开始（4 步）

### 1. 确认 Python

```powershell
python --version        # 需要 3.10+，本项目在 3.12.10 上测试
```

没有的话去 <https://www.python.org/downloads/> 装，**安装第一步务必勾选 Add python.exe to PATH**。

### 2. 装依赖

```powershell
cd F:\项目文件夹\智能体\agent
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置密钥

```powershell
copy .env.example .env
```

打开 `.env`，把里面的占位符换成你自己的（至少填 `DEEPSEEK_API_KEY`）。详见下面「五、.env 变量说明」。

### 4. 自检 → 运行

```powershell
python scripts/check_env.py        # 环境体检：Python / 依赖 / .env
python scripts/test_connection.py  # 真调一次 DeepSeek，验证密钥
python run.py                      # 显示所有课程，输入编号直接跑
```

---

## 三、目录结构

```
agent/
├─ run.py                     ← 入口：列出所有课，选一个运行
├─ requirements.txt
├─ .env                       ← 你自己的密钥（已被 .gitignore 排除，不要外传）
├─ .env.example               ← 密钥模板
├─ .gitignore
├─ .trae/.ignore              ← 让 TraeCode 的 AI 不去索引 .env
├─ scripts/
│   ├─ check_env.py           ← 环境自检（Python/依赖/.env）
│   └─ test_connection.py     ← DeepSeek 连通性测试
├─ day01/   8 课 + 4 份笔记
├─ day02/   15 课
└─ day03/   11 课 + 2 份资料
```

运行脚本时**不用`cd`进子目录**，统一用 `python run.py` 或 `python day01/01.认识大模型.py`（从项目根运行即可）。

---

## 四、课程导航

### day01 · AI 基础与提示词

| # | 文件 | 学什么 |
|---|---|---|
| 01 | `01.认识大模型.py` | 第一次调用 DeepSeek：base_url / 模型名 / 打印回复（附完整笔记） |
| 02 | `02.认识prompt提示词.py` | prompt 是什么、system 与 assistant 的区别、提示词结构（附笔记） |
| 03 | `03.prompt少量样本.py` | few-shot：示例如何决定输出的**格式**（附笔记） |
| 04 | `04.prompt中的字符串.py` | `string.Template` 把提示词做成模板 |
| 05 | `05.f表达式.py` | f-string：把变量塞进字符串 |
| 06 | `06.AI中的流式输出.py` | `stream=True` 打字机效果（附笔记） |
| 07 | `07.校验环境变量配置是否成功.py` | 5 项体检：目录 / .env / 依赖 / 密钥格式 / 系统变量 |
| 08 | `08.认识prompt使用环境变量中的密钥.py` | 密钥隔离：源码里不出现密钥 + 脱敏显示 |

### day02 · Python 基础 / 多轮对话 / 网页界面

| # | 文件 | 学什么 |
|---|---|---|
| 01 | `01.python中的函数.py` | 函数、参数、返回值；把调模型封装成 `ask()` |
| 02 | `02.多轮对话的问题.py` | 为什么模型"失忆" |
| 03 | `03.多轮对话记忆功能的实现.py` | 记忆盒子 `memoryBox`（附 token 逐轮增长实测） |
| 04 | `04.python中列表.py` | 列表：下标、切片、append、越界 |
| 05 | `05.while.py` | 循环：for / while / break / continue |
| 06 | `06.接收用户在控制台输入信息.py` | `input()` 的两个坑 |
| 07 | `07.去除两端多余的空格.py` | `strip()` 与输入清洗 |
| 08 | `08.in和not_in的使用.py` | 成员判断：命令识别、关键词分支 |
| 09 | `09.实现一个完整多轮对话功能.py` | 命令行聊天机器人（流式 + 帮助/历史/清空） |
| 10 | `10.gradio案例.py` | 第一个网页：Blocks + Textbox + 接 DeepSeek |
| 11 | `11.滑块Slider组件.py` | Slider 调 temperature，实测温度对输出的影响 |
| 12 | `12.gradio中的布局.py` | Row / Column / scale 排版 |
| 13 | `13.动态绑定事件.py` | `click` 事件三件套：fn / inputs / outputs |
| 14 | `14.表单提交事件.py` | `submit` 回车触发 + 多返回值清空输入框 |
| 15 | `15.自定义大模型回复页面.py` | 完整 AI 问答页面（4 组件 + 记忆 + 清空） |

### day03 · 实时信息 / 工具调用 / Agent

| # | 文件 | 学什么 |
|---|---|---|
| 01 | `01.大模型回复实时信息的问题.py` | 模型为什么答不了"今天天气" |
| 02 | `02.functioncalling.py` | 手工版 function calling + 真实高德天气接口 |
| 03 | `03.ReAct的使用.py` | LangChain ReAct：`@tool` + `create_agent` |
| 04 | `04.豆瓣接口演示.py` | 免 Key 的豆瓣接口（含 418 反爬实测） |
| 05 | `05.ReAct结合接口来实现智能体的调用.py` | 天气 + 豆瓣双工具，模型自己挑 |
| 06 | `06.langchain的模型调用.py` | `invoke()`：LangChain 调模型的地基 |
| 07 | `07.langchain的模型流式输出.py` | `stream()` + 人设对比 + 空分片处理 |
| 08 | `08.langchain的模型Batch调用.py` | `batch()` 批量并发（实测快 2.3 倍） |
| 09 | `09.langchain的Message消息.py` | `SystemMessage` / `HumanMessage` / `AIMessage` |
| 10 | `10.langchain中的tool记忆用户信息.py` | 长期记忆：`InMemoryStore` + `ToolRuntime` |
| 11 | `11.langchain中的智能体发送邮件.py` | 真发邮件：SMTP + `try/except` 优雅失败 |

参考资料：`functioncalling流程图.md`（流程图 + 代码对照）、`参考-无需Key的免费接口清单.md`。

---

## 五、.env 变量说明

| 变量 | 必需 | 用途 | 从哪儿拿 |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | ✅ | 调 DeepSeek | <https://platform.deepseek.com/api_keys> |
| `DEEPSEEK_BASE_URL` | 建议 | 接口地址，换供应商只改这里 | `https://api.deepseek.com` |
| `AMAP_KEY` | day03 用 | 高德天气接口 | <https://console.amap.com>（选**Web服务**类型） |
| `SMTP_HOST` / `SMTP_PORT` | day03/11 用 | 邮件服务器 | `smtp.qq.com` / `465` |
| `SMTP_USER` | day03/11 用 | 发件邮箱 | 你的邮箱 |
| `SMTP_AUTH_CODE` | day03/11 用 | SMTP **授权码**（不是登录密码） | 邮箱设置 → 开启 POP3/SMTP → 生成授权码 |
| `MAIL_TO` | 可选 | 默认收件人 | 一般填自己方便测试 |

> ⚠️ `.env` 里有真实密钥，已被 `.gitignore` 和 `.trae/.ignore` 排除 —— 不要提交、不要截图、不要发群里。

---

## 六、公共脚本

| 脚本 | 作用 | 用法 |
|---|---|---|
| `run.py` | 列出全部课程，输入编号直接运行 | `python run.py` |
| `scripts/check_env.py` | 环境体检（Python / 依赖 / .env 变量是否齐） | `python scripts/check_env.py` |
| `scripts/test_connection.py` | 真调一次 DeepSeek，验证密钥、地址、模型名 | `python scripts/test_connection.py` |

---

## 七、常见问题速查

| 现象 | 原因 / 解决 |
|---|---|
| `401 Authentication Fails` | 密钥错/过期；或 `.env` 里带了空格、引号 |
| `402 Insufficient Balance` | 余额不足，去平台充值 |
| `NotFoundError` / model not found | 模型名写错（旧名 `deepseek-chat`/`deepseek-reasoner` 已停用），用 `deepseek-flash` |
| 回复是空的 | `max_tokens` 太小，被"思考模式"吃光了；调大或关思考 |
| `UnicodeEncodeError: 'gbk'` | 控制台打不出 emoji；脚本已统一加 `sys.stdout.reconfigure(errors="replace")` |
| `UnicodeEncodeError: 'ascii'` | 密钥里有中文，或系统里有个同名的环境变量（先 `echo $env:DEEPSEEK_API_KEY`） |
| 请求超时、但网络没问题 | `.env` 没读到 → `base_url` 变成 `None`，请求打到了 api.openai.com（先跑 `check_env.py`） |
| 豆瓣接口 `418` | 没带 User-Agent，被反爬拦了（见 `day03/04`） |
| 高德接口返回 `status: "0"` | HTTP 200 也可能是失败，要看 `info` 字段（多为 key 类型不对） |
| 网页打不开 / 端口占用 | 同一个时间只能开一个 gradio（默认 7860）；关掉前一个或看终端打印的新端口 |
| `__pycache__` 里跑出来的副本 | 别在缓存目录里运行，删掉 `__pycache__` 即可 |

更多细节见各课笔记（`day01/*.md`）。

---

## 八、建议的学习顺序

1. **先跑通环境**：`check_env.py` → `test_connection.py`
2. **按 day01 顺序走**：理解"调用 → 提示词 → 格式控制 → 流式"
3. **day02 前 9 课是 Python 基础**，讲得很细；第 9 课是命令行版聊天机器人
4. **day02 第 10–15 课**做网页，先跑起来再改参数
5. **day03 是重点**：02（手工工具）→ 03（框架）→ 05（多工具）→ 06/07/08（invoke/stream/batch）→ 10/11（记忆、发邮件）

如果时间紧，**最低限度跑通这条链**：#01 → #02 → #03 → day02/09 → day02/15 → day03/05。

---

## 九、说明

- 本项目用于课程学习与练习，部分接口（豆瓣 `j/` 路径）是**网页前端内部接口**，非官方长期承诺，有隐式限流，请勿高频抓取或用于商用；稳定性要求高时请改用官方 API。
- 模型输出具有随机性，"同一次问两次结果不同"是正常现象，不要用单次结果给提示词下结论。
- 所有笔记、代码均为学习记录，欢迎继续往下补课。
