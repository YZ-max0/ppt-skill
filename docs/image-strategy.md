# 图片素材策略（image-strategy）

> T-IMG1 产出 ｜ 适用：所有需要配图的 deck ｜ 前置契约见
> `vendor-ppt-master/references/svg-image-embedding.md`
> （图片嵌入）、`image-layout-spec.md`（几何计算）、`image-layout-patterns.md`（构图词汇）

## 0. 一句话结论

图片链路**已全线打通**（本卡首次实测）：`images/` 放图 → SVG 用
`<image href="../images/x.png">` 引用 → checker 过 → 导出为**内嵌 Picture shape**（非链接）。
**但"素材从哪来"是策略问题，不是技术问题**——本文件解决它。

---

## 1. 素材三来源矩阵

| 来源 | 可用性 | 依赖 | 质量 | 合规 | 推荐度 |
|---|---|---|---|---|---|
| **① 用户提供** | **立即可用** | 无 | 最高（真实场景照/真实界面） | 用户自有，责任清晰 | ⭐ **首选** |
| **② 程序生成**（PIL / 图表 / 几何图形） | **立即可用** | 仅 Pillow | 中（示意图、占位图、数据图） | 完全自有 | ⭐ 推荐（图表/示意） |
| **③ base 搜图**（`image_search.py`） | **部分可用** | 见 §1.1 | 高（真实照片） | **需查许可等级** | 有条件可用 |
| **④ base 生图**（`image_gen.py`） | **不可用** | **必需 API key** | 高（任意题材） | 各服务条款 | ❌ 当前环境不可用 |

### 1.1 `image_search.py` — 零配置 vs 需 key

base 把 provider 明确分成两类：

```python
ZERO_CONFIG_PROVIDERS = ("openverse", "wikimedia")   # 无需任何 key
KEYED_PROVIDERS = ("pexels", "pixabay")              # 需 key
```

| Provider | 环境变量 | 是否需 key | 许可注意 |
|---|---|---|---|
| `openverse` | 无 | **否**（默认启用） | 聚合源，需查 `license_tier` |
| `wikimedia` | 无 | **否**（默认启用） | 多数需署名 |
| `pexels` | `PEXELS_API_KEY` | 是 | Pexels 许可 |
| `pixabay` | `PIXABAY_API_KEY` | 是 | Pixabay 内容许可 |

**重要**：零配置 provider 也需要**网络**。本仓库当前环境（WSL 侧）**无外网**
（此前实测 `api.github.com` 连接失败），故 ③ 在本机**实际不可用**——
不是缺 key，是缺网络。**如需启用，请在 Windows 侧有网环境运行并配代理。**

> key 通过 `load_prefixed_env_file(("PEXELS_", "PIXABAY_"))` 从**共享 `.env`** 读取。
> **本仓库不申请、不硬编码任何 key**；`.env` 已在 `.gitignore` 中。

### 1.2 `image_gen.py` — 全后端都需 key

`IMAGE_BACKEND` 选择一个后端，**每个后端都需各自的 API key**（无一例外）：

| 后端 | key 环境变量 |
|---|---|
| `gemini` | `GEMINI_API_KEY`（+ `GEMINI_MODEL`/`GEMINI_BASE_URL`） |
| `openai` | `OPENAI_API_KEY`（+ `OPENAI_MODEL`/`OPENAI_BASE_URL`） |
| `qwen` | `QWEN_API_KEY` |
| `zhipu` | `ZHIPU_API_KEY` |
| `stability` / `bfl` / `ideogram` / `volcengine` / `modelscope` / `siliconflow` / `fal` / `replicate` / `openrouter` / `minimax` | 各自的 `*_API_KEY` |

另有通用 `IMAGE_API_KEY`。

**结论**：**当前环境无法使用 ④**。本卡的所有图片**均走 ② 程序生成**。

---

## 2. 图片规范

### 2.1 比例（必须与槽位一致）

| 比例 | 像素建议 | 适用骨架/页型 |
|---|---|---|
| **16:9** | 1920×1080 | `v3/image-hero`（满幅主视觉）、宽幅横幅 |
| **3:2** | 1800×1200 | 通用配图（比 4:3 更"摄影感"） |
| **4:3** | 1200×900 | `v3/image-split`（左图）、`v3/image-grid`（网格单元） |
| **1:1** | 900×900 | 头像、图标、方图网格 |

**比例契约（硬性）**：**槽位比例固定，图片按 `slice`（≈CSS `cover`）裁剪适配**。
即：图片比例不必等于槽位比例，但**重要的主体必须靠近画面中心**，
否则会被裁掉。若主体靠边，改用 `meet`（≈`contain`，会留白但完整）。

### 2.2 最小分辨率

**显示尺寸 × 2** 起步（兼顾高分屏与 PPT 缩放）：

| 槽位显示尺寸 | 最小源图 |
|---|---|
| 1280×720（满幅） | 2560×1440 |
| 520×390（左图） | 1040×780 |
| 284×213（网格单元） | 568×426 |

### 2.3 文件大小上限

- 单图 **≤ 1.5 MB**（导出时 base 默认 `--image-sizing cap`，上限 2560px；超限会重编码）
- 全 deck 图片总量建议 **≤ 15 MB**
- 照片用 **JPEG q85**；含文字/线条的截图用 **PNG**

### 2.4 命名规则

```
<用途>-<比例>[-<序号>].<ext>
例：team-4x3-01.jpg   product-16x9.png   logo-1x1.svg
```

- 全小写、连字符分隔、不含中文与空格（避免跨侧路径问题）
- 放进项目 `images/`，**SVG 里用相对路径引用**

### 2.5 SVG 引用写法

```xml
<image href="../images/team-4x3-01.jpg"
       x="80" y="170" width="520" height="390"
       preserveAspectRatio="xMidYMid slice"/>
```

- 路径 **`../images/<name>`**（`svg_output/` 的上一级 → 项目 `images/`）
- `preserveAspectRatio`：`xMidYMid slice`（cover，默认）/ `xMidYMid meet`（contain）
- 图片位用**显式注释**标记，便于检索与替换：
  `<!-- IMAGE: images/team-4x3-01.jpg 4:3 fill -->`

---

## 3. 与骨架的配合表（v3 图片骨架族）

| 骨架 | 布局 | 图片比例 | 页型 | 何时用 |
|---|---|---|---|---|
| **`v3/image-hero.svg`** | 满幅图 + 底部标题浮层（68% 黑罩） | 16:9（也吃 3:2） | 封面 / 章节页 / 愿景页 | 需要"一张图定调"时；图本身承担情绪与主张 |
| **`v3/image-split.svg`** | 左图（520×390，4:3）+ 右文三要点 | 4:3 或 1:1 | 产品页 / 案例页 / 方案页 | 图是**论据**，文字是**解释**；左右可分读 |
| **`v3/image-grid.svg`** | 3 列 × 2 行等高网格（284×213，4:3）+ 每格图注 | **统一 4:3** | 团队页 / 多案例 / 对比墙 | 需要**同规格并列比较**；六格等重 |

### 单页图文比例建议

| 页型 | 图 : 文 | 说明 |
|---|---|---|
| image-hero | 100 : 0（文字浮在图上） | 图即页面；文字只作锚点 |
| image-split | 40 : 60 | 图占左 520px，右侧留给解释 |
| image-grid | 100 : 0（图注在图下） | 网格等重，图注仅一行标签 |

### 与既有 27 骨架的分工

- **不要**把图片硬塞进无图片位的骨架（如 `three-card`）——会破坏 bounds 与视觉节奏
- 需要"图 + 结构化文字"时：`image-split`（一边图一边文）
- 需要"多图并列"时：`image-grid`
- 需要"图 + 图表对照"时：图片骨架与 `chart-fill` 图表页**分页**，不混排

---

## 4. 已知限制

| 限制 | 说明 | 应对 |
|---|---|---|
| **TSD 环境加密** | 渲染产物（PNG）会被端点加密软件加密，**WSL 侧读到的是密文** | 图片处理必须在 **Windows 侧进程**内完成；跨侧传递走 `\\wsl.localhost\...` 或临时目录（W-3/W-8） |
| **内嵌 vs 链接** | 本仓库导出为**内嵌**（`ppt/media/image_*.png`，字节与源文件一致）；**非**链接 | 交付 .pptx 时图片随文件走，无需附带 `images/` |
| **无外网** | ③ 搜图在 WSL 侧不可用（无网络，非缺 key） | 用 ① 用户提供 或 ② 程序生成 |
| **生图全需 key** | ④ 的每个后端都要 `*_API_KEY` | 当前环境不可用；如启用需在 Windows 侧配 key 与网络 |
| **`slice` 会裁剪** | 比例不符时按中心裁剪，**边缘主体会丢失** | 关键主体居中；或改用 `meet` |
| **`meet` 会缩 shape** | 实测：1:1 图放进 4:3 槽用 `meet`，导出的 **Picture shape 收缩为 300×300 并居中**（不是留白填充） | 若要求 shape 严格等于槽位，**必须用 `slice`** |
| **图片 shape 藏在 group 里** | 骨架根级 `<g>` 会成组，python-pptx 顶层 `slide.shapes` **扫不到 Picture** | 读回验证**必须递归进 group**（否则假阴性，见 §5） |
| **无 SVG 图位骨架** | v3 三骨架均为位图（PNG/JPG）设计；`<image>` 也支持 SVG，但未实测 | 需要时单独验证 |
| **图片不参与质检** | `check_hygiene`/`check_overlap` 只解析文本与几何，**不解析图片内容** | 图片内容正确性依赖人工目视 |

---

## 5. 链路实测结论（T-IMG1 Part A/C）

| 项 | 实测结果 |
|---|---|
| 引用路径 | `../images/<name>.png`（从 `svg_output/` 出发）✅ |
| checker | 含 `<image>` 的 SVG 正常通过，`blocking: 0` |
| 导出 | 图片**内嵌**为 `ppt/media/image_*.png`，字节与源文件**完全一致**（69531B = 69531B） |
| 读回 | 递归枚举得 **Picture shape**，数量/位置/显示尺寸均与 SVG 声明一致 |
| 比例 16:9→16:9 `slice` | 显示 1280×720，**无裁剪** |
| 比例 16:9→1:1 `slice` | 显示 480×480，**位图被中心裁剪**（符合 cover 语义） |
| 比例 1:1→4:3 `meet` | **Picture shape 收缩为 300×300 并居中**（非留白） |
| 图片优化 | 导出日志：`Image optimization: Enabled (preferred cap 2560 px, unchanged bytes preserved)` |

**踩坑记录（重要）**：读回验证首版只扫 `slide.shapes` **顶层**，得到"0 个 Picture"，
差点误判为"图片链路不通"。实际图片被包在 `<g>` 对应的 **group shape** 内
——必须**递归进 group** 才能读到。验证脚本见 `deltas/chart-fill/verify_picture.py`。
