"""
DeepSeek 连通性测试：验证「密钥 + 地址 + 模型名」三件套是否真的能用。

运行：
    在项目根目录： python scripts/test_connection.py
会真实发起一次极小的 API 调用（约 10 个 token，几厘钱）。
不想花额度就把下面的 DRY_RUN 改成 True，只做本地检查。
"""

import os
import sys
import time

# Windows 控制台默认 GBK，模型回复里若带 emoji，print 会直接崩
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

DRY_RUN = False           # True = 只做本地检查
MODEL = "deepseek-flash"  # 想测 V4-Pro 就换成 deepseek-v4-pro
MAX_TOKENS = 200

# 思考模式：V4 默认开启（先"想"再答，想的过程也计费）。
# 实测同一个问题：开 121 tokens（思考 119）vs 关 1 token。
THINKING = "disabled"     # "enabled" / "disabled" / None

LINE = "-" * 52

print(LINE)
print("DeepSeek 连接测试")
print(LINE)

# ---------- 1. 依赖 ----------
try:
    from dotenv import load_dotenv
    import openai
    from openai import OpenAI
except ImportError as exc:
    print("[失败] 依赖没装好：", exc)
    print("       请执行：pip install -r requirements.txt")
    raise SystemExit(1)

print("[1/4] 依赖检查        OK    openai", getattr(openai, "__version__", "?"))

# ---------- 2. 密钥 ----------
load_dotenv(override=True)
key = os.environ.get("DEEPSEEK_API_KEY", "")
base_url = os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"

if not key:
    print("[2/4] 读取密钥        失败：没读到 DEEPSEEK_API_KEY")
    print("       请把 .env.example 复制成项目根目录的 .env，并填入密钥")
    raise SystemExit(1)
if key != key.strip():
    print("[2/4] 读取密钥        失败：密钥首尾有空格，会直接 401")
    raise SystemExit(1)
try:
    key.encode("ascii")
except UnicodeEncodeError:
    print(f"[2/4] 读取密钥        失败：密钥里有中文字符（{key}）")
    print("       也可能是系统里有个同名的用户环境变量，先 echo $env:DEEPSEEK_API_KEY 看看")
    raise SystemExit(1)

print(f"[2/4] 读取密钥        OK    {key[:6]}{'*' * 6}{key[-4:]}（长度 {len(key)}）")

# ---------- 3. 地址与模型 ----------
print(f"[3/4] 目标接口        {base_url}")
print(f"                      模型 {MODEL}，思考模式 {THINKING}")

if DRY_RUN:
    print(LINE)
    print("DRY_RUN 模式：本地检查全部通过，未发起真实调用。")
    raise SystemExit(0)

# ---------- 4. 真实调用 ----------
client = OpenAI(api_key=key, base_url=base_url, timeout=30.0)
extra = {} if THINKING is None else {"extra_body": {"thinking": {"type": THINKING}}}
started = time.time()

try:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "只回复两个字：通了"}],
        max_tokens=MAX_TOKENS,
        **extra,
    )
except Exception as exc:
    name = exc.__class__.__name__
    status = getattr(exc, "status_code", None)
    print("[4/4] 调用接口        失败")
    print("       异常类型：", name, "" if status is None else f"(HTTP {status})")
    if name == "AuthenticationError" or status == 401:
        print("       原因：密钥无效 / 已删除 / 复制不完整")
    elif status == 402 or "Insufficient Balance" in str(exc):
        print("       原因：账户余额不足 → 到 platform.deepseek.com 充值")
    elif name == "NotFoundError" or ("model" in str(exc).lower() and status == 404):
        print("       原因：模型名不对 → 用 deepseek-flash 或 deepseek-v4-pro")
        print("             （旧名 deepseek-chat / deepseek-reasoner 已于 2026-07-24 停用）")
    elif name in ("APIConnectionError", "APITimeoutError"):
        print("       原因：网络不通 → 关掉 VPN/代理重试")
    elif name == "RateLimitError" or status == 429:
        print("       原因：请求太频繁 → 等几秒再试")
    else:
        print("       原始信息：", str(exc)[:300])
    raise SystemExit(1)

elapsed = time.time() - started
message = resp.choices[0].message
content = message.content or ""
reasoning = getattr(message, "reasoning_content", None)
usage = getattr(resp, "usage", None)

print(f"[4/4] 调用接口        OK    耗时 {elapsed:.2f}s")
print(LINE)
print("模型回复：", content if content.strip() else "（空）")
if reasoning:
    print(f"（思考内容 {len(reasoning)} 字，已省略）")
if usage:
    detail = getattr(usage, "completion_tokens_details", None)
    rt = getattr(detail, "reasoning_tokens", None) if detail else None
    print(f"本次 tokens：输入 {usage.prompt_tokens} / 输出 {usage.completion_tokens}"
          + (f"（其中思考 {rt}）" if rt else ""))
print(LINE)
print("结论：", "连接正常，可以开始跑课程脚本了（python run.py）" if content.strip() else "接口通了但回复为空，检查 MAX_TOKENS")
