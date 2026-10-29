### 🎬 无需 Key 的前端内部接口（相对稳定，主要面向影视）

这些接口来自 `movie.douban.com/j/` 路径，是豆瓣网页前端自身调用的接口，目前实测无需 API Key，但请求时通常需要带上 `User-Agent` 和 `Referer` 头。

**1. 获取分类标签**
- **地址**：`GET https://movie.douban.com/j/search_tags`
- **参数**：`type`（必需），值为 `movie`（电影）或 `tv`（电视剧）。
- **用途**：获取电影或电视剧的分类标签（如“热门”、“喜剧”、“科幻”等），用于构建筛选菜单。

**2. 按标签获取影视列表**
- **地址**：`GET https://movie.douban.com/j/search_subjects`
- **主要参数**：
    - `type`：`movie` 或 `tv`。
    - `tag`：标签名（需 URL 编码，如“热门”）。
    - `sort`：可选，`recommend`（综合推荐）、`time`（最新）、`rank`（评分）。
    - `page_limit` / `page_start`：分页参数。
- **用途**：根据标签、类型、地区等条件获取影视列表。

**3. 其他常用 `j/` 路径接口**（通常需配合有效 Cookie，且存在限流）
- **短评**：`GET https://movie.douban.com/j/review/short_comments`，参数含 `subject_id` 等。
- 注意：此类涉及 UGC（用户生成内容）的接口**合规风险较高**，豆瓣官方明确禁止未经许可的批量抓取。

### 🌐 第三方代理/镜像地址（用于访问传统的 V2 接口）

豆瓣旧版 V2 API（`api.douban.com/v2/...`）虽然官方入口受限，但可以通过社区维护的代理域名来访问，这类代理通常也**无需自行申请 Key**。

- **代理域名**：`https://douban.uieee.com`
- **用法**：将原 V2 地址中的 `api.douban.com` 替换为该域名即可。例如，获取电影 Top250：`https://douban.uieee.com/v2/movie/top250`。
- **可用端点示例**（在代理有效的前提下）：
    - 正在热映：`/v2/movie/in_theaters`
    - 即将上映：`/v2/movie/coming_soon`
    - 电影搜索：`/v2/movie/search`
    - 电影详情：`/v2/movie/subject/{id}`
- **重要提醒**：这类代理由第三方维护，**稳定性无法保证**，随时可能失效。它们主要适合开发测试或短期个人项目。

### 🔌 第三方替代 API（独立服务，非豆瓣官方）

一些第三方平台提供了基于豆瓣数据的结构化 API，通常有免费额度或完全免费，可以作为备选方案。

- **WMDB API**
    - **地址**：`https://api.wmdb.tv/api/v1/movie/search?q={keyword}&limit=5`（搜索）；`https://api.wmdb.tv/movie/api?…`（详情）。
    - **特点**：免费、无需认证，提供结构化的电影信息。
- **API Zero 豆瓣电影信息**
    - **地址**：`https://v1.apizero.cn/api/douban-movie`
    - **特点**：支持通过豆瓣 ID 或 URL 查询详情，匿名可不传 Key 调用（可能有频率限制）。

### 🧰 封装好的工具/MCP 服务器（开箱即用）

如果你不想直接处理 HTTP 请求，可以使用社区封装好的 MCP（Model Context Protocol）服务器或命令行工具，它们内部已经整合了上述可用接口。

- **`astron-douban-mcp`**：直接调用豆瓣游客态公开接口，无需额外部署，默认无需认证。
- **`moria97/douban-mcp`**：支持搜索图书、查看电影/电视剧评论等功能。
- **`yoyooyooo/douban-mcp`**：提供图书、电影、小组讨论的搜索与详情接口。
- **`opencli`**：命令行工具，支持 `douban search`、`douban top250`、`douban subject` 等命令。

### ⚠️ 使用前的关键提醒

1. **稳定性无保障**：上述所有“免费”方案均非官方长期承诺的服务。前端内部接口和代理地址可能因豆瓣的策略调整随时失效。
2. **合规与法律风险**：特别是涉及**用户影评、短评、收藏列表**的接口，豆瓣已通过诉讼案例明确了对批量抓取并商用行为的限制。用于个人学习、非商业性的轻量查询尚可，但应避免规模化采集或用于具有商业替代性的产品。
3. **隐式限流**：即使是公开接口，也存在未明示的调用频率限制（如单 IP 日请求量限制），高频请求极易触发验证码或 IP 封禁。
4. **优先选择第三方独立 API**：如果对稳定性有要求，建议优先考虑 `WMDB` 或 `API Zero` 这类独立的第三方服务，它们通常比依赖豆瓣域名本身的方案更可控一些。

除了豆瓣相关的接口，开源社区里“即开即用”的免费小工具 API 还有很多。下面这些大多**无需注册、无需 API Key**，用 `curl` 或浏览器直接请求就能拿到 JSON 或图片，很适合个人项目、原型验证或内部小工具。

### 🌦️ 天气与地理信息

**Open-Meteo** 是目前最省事的全球天气接口，完全免费且无需认证，支持当前天气、7天预报和历史数据。
*   **调用示例**：`https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current_weather=true`

**IP 地理位置查询**有几个稳定的免 Key 选择：
*   **ip-api.com**：免费、无需 Key，海外友好，但有频率限制（免费版约 45 次/分钟）。
*   **ipwho.is**：免费、无需 Key，返回字段比较全。
*   **ipgeolocationapi.io**：免费层级每天 5,000 次，无需注册。

### 💱 汇率与金融数据

**Frankfurter** 基于欧洲央行数据，完全免费且**无需注册**，适合做简单的汇率换算。
*   **ExchangeRate-API**：免费额度约每月 1500 次，支持 160+ 货币，需要注册获取 Key。
*   **Fixer**：轻量级汇率 API，提供当前和历史汇率，有免费层级。

### 🔧 实用工具类

**二维码生成（GoQR / api.qrserver.com）**：免费且**无需 Key**，直接通过 URL 参数即可生成 PNG、SVG 等格式的二维码图片。
*   **示例**：`https://api.qrserver.com/v1/create-qr-code/?data=Hello&size=150x150`

**短链接（TinyURL / inbio）**：
*   **TinyURL** 提供免费 API，无需注册和 Key，适合快速把长链接变短。
*   **inbio** 的短链接服务同样免 Key，但匿名生成的链接会在 30 天后过期。

**手机号归属地**：`xiaoqi.icofun.cn` 提供了一个公开的免 Key 接口，可以直接查询省份、城市和运营商。
*   **示例**：`https://xiaoqi.icofun.cn/API/phone.php?phone=18888888888`

### 🎲 内容与娱乐

**随机图片 / 动物图片**：
*   **Dog CEO**：免费获取随机狗狗图片，可按品种筛选，无需认证。
*   **piccdn**：提供 7 个分类、7000+ 张图片的随机图片 API，宣称无 Key、无频率限制。

**笑话 / 趣味文本**：`icanhazdadjoke.com` 提供纯文本冷笑话，一个 `curl` 就能拿到。

**假数据 / Mock**：**JSONPlaceholder** 是前端原型和测试的经典选择，提供 posts、comments、users 等模拟 REST 资源，无需登录。

### 🧪 开发调试辅助

**httpbin.org**：用于测试 HTTP 请求的各种行为（如 header、状态码、重定向），免登录，是联调时的常用工具。

**随机用户数据**：`randomuser.me` 可以生成结构化的模拟用户信息，适合给演示项目填充数据。

### 💡 使用提醒

这类免费公开接口的共同特点是**零门槛、但无 SLA 保证**。它们在个人项目、教学演示、内部工具中非常方便，但不建议用于对稳定性有严格要求的生产环境或涉及敏感数据的场景。同时，部分接口可能存在隐式频率限制或 IP 限流，高频调用时需要注意。

如果你需要持续发掘更多接口，可以关注 GitHub 上的 **public-apis**（41万+ Star，收录 1400+ 个免费 API）和 **public-api-lists**（730+ 个，按 48 个分类整理）这类社区维护的清单项目，它们会持续更新可用资源。