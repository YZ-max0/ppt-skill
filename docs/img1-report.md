# T-IMG1 交付报告 · 图片位骨架专项

> 执行者：开发工程师 ｜ 日期：2026-09-15 ｜ 卡：`tasks/T-IMG1.md`
> 前置：T-E2E6 已收官（`f37217d`）
> 结论：**图片链路首次打通并全线验证**；**3 个图片骨架入库 `v3/`**（checker 零 blocking）；
> 端到端小样 6 页四道质检全过、读回 8 个 Picture shape 正确；
> Part D 素材策略落地；2 项顺带小修完成。
> **发现 1 个流程陷阱（读回假阴性）与 1 个契约行为（`meet` 会缩 shape）。**

---

## 1. 命令表（含耗时）

环境：Windows PowerShell 5.1 + `python` 3.12.3 + python-pptx 1.0.2 + **Pillow 12.3.0**

| # | 阶段 | 命令/动作 | exit | 耗时 |
|---|---|---|---|---|
| A1 | 契约研究 | 读 `svg-image-embedding.md` / `image-layout-spec.md` / `image-layout-patterns.md` | — | 会话内 |
| A2 | 素材矩阵 | 读 `image_search.py` / `image_gen.py` 的 provider 与 key 需求 | — | 会话内 |
| A3 | 生成测试图 | `make_test_images.py`（PIL，3 张不同比例） | 0 | 1 s |
| A4 | **首次链路验证** | 单页 16:9 → checker → 导出 → 读回 Picture | **0** | 3 s |
| A4b | 三种比例对照 | 3 页（16:9→16:9 / 16:9→1:1 slice / 1:1→4:3 meet） | **0** | 4 s |
| B1 | 骨架撰写 | `image-hero` / `image-split` / `image-grid` | — | 会话内 |
| B2 | 骨架验证 | `svg_quality_checker`（3 骨架） | **0** | 2 s |
| C1 | 小样初始化 | `project_manager.py init e2e-img --dir <TEMP> --format ppt169 --quick-generate` | 0 | 1 s |
| C2 | 6 页填充 | `python example_img_deck.py <out>` | 0 | < 1 s |
| C3 | 质量门 | `svg_quality_checker.py <proj> --quick-generate --stage final --json` | **0** | 2 s |
| C4 | 导出 | `svg_to_pptx.py <proj> --quick-generate --no-notes` | **0** | 3 s |
| C5 | 跨组重叠 | `check_overlap.py` | **0** | < 1 s |
| C6 | 骨架卫生 | `check_hygiene.py` | **0** | < 1 s |
| C7 | D-2 出框 | `detect_overflow.py` | **0** | 3 s |
| C8 | D-2 标题 | `check_title_consistency.py` | **0** | 3 s |
| C9 | **读回 Picture** | `verify_picture.py`（递归） | 0 | 2 s |
| C10 | 渲染 | `render_png.py` | 0 | 3 s |

**机器侧总耗时 ≈ 22 秒**（A3–C10）。
> **计时口径（诚实披露）**：契约研究、骨架撰写、策略文档均为 agent 会话内产出，
> wall-clock 不代表人类作者耗时。

**产物**：`C:\Users\<you>\AppData\Local\Temp\opencode\t-img1\e2e-img_ppt169_20260915\exports\*.pptx`
**contact sheet（供指挥官读图）**：
`C:\Users\<you>\AppData\Local\Temp\opencode\t-img1\e2e-img_ppt169_20260915\render\contact-sheet.png`（6 页）

---

## 2. Part A · 图片嵌入契约摘要

来源：`vendor-ppt-master/references/svg-image-embedding.md`（+ `image-layout-spec.md` 几何）

### 2.1 路径规则

| 项 | 契约 | 实测确认 |
|---|---|---|
| 引用写法 | `<image href="../images/x.png" .../>` | ✅ 可用 |
| 基准目录 | SVG 在 `svg_output/`，图片在项目 `images/`（**上一级 + `images/`**） | ✅ |
| 生成期 | 保留**外部引用**（文件小、易替换） | — |
| 预览期 | `finalize_svg.py` 把图片**内嵌为 base64**，产出 `svg_final/` | 未跑（Quick 模式省略该产物） |
| 导出期 | `svg_to_pptx.py` **直接读 `svg_output/`** 的引用并转为 DrawingML | ✅ 已实测 |

### 2.2 尺寸与比例规范

| 项 | 契约 | 实测确认 |
|---|---|---|
| 显示尺寸 | `width`/`height` 由 SVG 声明（槽位固定） | ✅ 与读回值一致 |
| 适配模式 | `preserveAspectRatio="xMidYMid slice"`（≈cover）为默认 | ✅ `slice` 中心裁剪 |
| 裁剪合法性 | crop boundary 由 `image-layout-spec.md` 计算（contain/fill 两套公式） | 未逐条核对公式 |
| `clipPath` | **仅** `<image>` 上**有条件允许** | 未使用 |
| 导出优化 | `--image-sizing cap`（上限 2560px，未改动的**保留原始字节**） | ✅ 日志确认 + 字节一致 |

### 2.3 打包（导出 PPTX）时的行为 —— **关键实测**

| 项 | 实测结果 |
|---|---|
| 内嵌 or 链接 | **内嵌**：包内出现 `ppt/media/image_043c7a53afcc0172.png` |
| 字节一致性 | **69531 B（源文件）→ 69531 B（包内）**，完全一致（未触发重编码） |
| Shape 类型 | DrawingML **Picture shape**（`MSO_SHAPE_TYPE.PICTURE`） |
| 定位 | 读回位置 `(0,0)`、显示 `1280×720`，与 SVG 声明一致 |

### 2.4 素材可行性矩阵

| 渠道 | 脚本 | 是否需 key | 本环境可用性 |
|---|---|---|---|
| **零配置搜图** | `image_search.py`（`openverse`/`wikimedia`） | **否** | ❌ **无外网**（非缺 key） |
| 需 key 搜图 | `image_search.py`（`pexels` 需 `PEXELS_API_KEY`；`pixabay` 需 `PIXABAY_API_KEY`） | 是 | ❌ 缺 key + 缺网 |
| 生图 | `image_gen.py`（14 个后端） | **全部**需 key（`GEMINI_API_KEY` / `OPENAI_API_KEY` / `QWEN_API_KEY` / `ZHIPU_API_KEY` / `IMAGE_API_KEY` …） | ❌ |
| **程序生成** | **PIL**（本卡自写） | 否 | ✅ **本卡全部图片走此路** |
| 用户提供 | — | 否 | ✅ 推荐（生产环境首选） |

> **本仓库未申请、未硬编码任何 key**；`.env` 已在 `.gitignore`。
> 零配置 provider 也需网络——本环境 WSL 侧无外网，故③实际不可用。

### 2.5 首次链路验证数据（A3/A4）

测试图（PIL 生成，带网格/对角线/四角标记，便于目视判断裁剪与变形）：

| 文件 | 像素 | 比例 | 大小 |
|---|---|---|---|
| `hero-16x9.png` | 1920×1080 | 1.7778 | 67.9 KB |
| `split-4x3.png` | 1200×900 | 1.3333 | 38.1 KB |
| `grid-1x1.png` | 900×900 | 1.0000 | 24.2 KB |

**三种比例组合的对照实测**：

| # | 源比例 → 槽位比例 | 模式 | 读回显示 | 读回位图 | 判定 |
|---|---|---|---|---|---|
| 1 | 16:9 → 16:9 | `slice` | 640×360 (1.7778) | 1920×1080 (1.7778) | ✅ 无裁剪 |
| 2 | 16:9 → 1:1 | `slice` | 480×480 (1.0000) | 1920×1080 (1.7778) | ✅ 中心裁剪（符合 cover） |
| 3 | 1:1 → 4:3 | `meet` | **300×300** (1.0000) | 900×900 (1.0000) | ⚠️ **shape 收缩并居中** |

> 第 3 行是**契约行为发现**：`meet` 不是"在槽位内留白"，而是
> **Picture shape 收缩到图片自身比例并居中**。若要求 shape 严格等于槽位几何，**必须用 `slice`**。
> 已记入 `v3/CONTRACT.md` v3-3 与 `docs/image-strategy.md` §4。

**TSD 环境下图片读写路径确认**：图片经 `\\wsl.localhost\Ubuntu\...` 从 WSL 传入 Windows 侧
项目 `images/`，导出后可正常读回；**渲染产物（PNG）仍受加密限制**，
contact sheet 需由窗口侧读取（沿用既有 W-8 流程）。

---

## 3. Part B · 3 个图片位骨架（`deltas/layout-assets/v3/`）

| 骨架 | 用途 | 图片位 | 槽位数 | checker |
|---|---|---|---|---|
| `image-hero.svg` | 大图 + 标题浮层 | 满幅 1280×720（16:9，底部 68% 黑罩） | 3 | ✅ 0/0 |
| `image-split.svg` | 左图右文 | 左 520×390（**精确 4:3**）+ 右文 540px | 11 | ✅ 0/0 |
| `image-grid.svg` | 3×2 网格 + 图注 | 6 格 × **284×213（精确 4:3）** | 14 | ✅ 0/0 |

**沿用全部骨架硬标准**：根级 `<g>` 全带 `data-pptx-bounds`、根 `<svg>` 带
`data-pptx-page-role`、多行文本用单 `<text>` + 多 `<tspan>`、字号仅用既有档位、
层级字号差 ≥6pt、占位文案按最长内容撰写。

**图片位标记**：采用卡内要求的**显式注释**形式：

```xml
<!-- IMAGE: images/split-4x3.png 4:3 fill -->
```

**比例契约**：槽位比例固定，图片按 `slice`（cover）裁剪适配（`v3-2`）。

**验证**：从 **repo 位置**跑 `svg_quality_checker` → `Fully passed: 3 (100%)`、
`blocking: 0`、`introduced: 0`；hygiene / overlap 亦 exit 0。

### 3.1 骨架撰写期间踩到的 3 个坑（均已修）

| 坑 | 现象 | 修法 |
|---|---|---|
| 多行文本拆成兄弟 `<text>` | checker 报"Detected 3 paragraph-like line run(s) split across sibling `<text>` elements" | 合并为单 `<text>` + 多 `<tspan>`（契约 §3 硬标准） |
| 图注 bounds 过窄 | P03 报 3 处 `vertical 7.2%` 溢出 | 按文本 bbox 公式（`top=y-0.85×size`、`bottom=y+0.35×size`）重算 bounds |
| 网格几何超底 | 原打算图片 308×231 → 底部 726 > 720 | 重算为 284×213，整页收在 688 |

---

## 4. Part C · 端到端小样（6 页）

**设计**：用 v3 图片骨架改造 T-05 BP 的结构，作"图片增强小样"——
3 页走图片骨架，2 页保留图表（对照：图表页不受图片改造影响），1 页纯文字锚点（对照）。

| 页 | 骨架 | 图片位 | 图片 |
|---|---|---|---|
| P01 | `v3/image-hero` | 1（满幅） | `hero-16x9.png` |
| P02 | `v3/image-split` | 1（520×390） | `split-4x3.png` |
| P03 | `v3/image-grid` | 6（284×213 ×6） | `grid-1x1.png` |
| P04 | `chart-fill` area | — | — （图表对照） |
| P05 | `chart-fill` waterfall | — | — （图表对照） |
| P06 | `v2/quote-hero` | — | — （纯文字对照） |

**素材声明**：全部图片为 **PIL 程序生成的测试图**，**未引入任何外部图片素材**。

### 4.1 四道质检 + 读回结果

| 检查 | 结果 |
|---|---|
| `svg_quality_checker` | `Fully passed: 6 (100%)`、`blocking: 0`、`introduced: 0`、exit 0 |
| 导出 | `POSTFLIGHT status=passed quality_gate=passed slides=6 warning_categories=0` |
| `check_hygiene` | `[OK] 未发现示例内容泄漏`，exit 0 |
| `check_overlap` | `[OK] 未发现跨组重叠`，exit 0 |
| D-2 出框 | `0 P0 / 0 P1`，exit 0 |
| D-2 标题 | 0 项 P1，exit 0 |
| **读回 Picture shape** | **8 个**（1+1+6+0+0+0），位置/尺寸全部与 SVG 声明一致 |
| 渲染 | 6 页 PNG + contact sheet（1770×578） |

**读回详情（递归枚举）**：

| 页 | Picture 数 | 显示尺寸 | 位图尺寸 | 判定 |
|---|---|---|---|---|
| P01 | 1 | 1280×720 (1.7778) | 1920×1080 (1.7778) | ✅ 比例一致，未裁剪 |
| P02 | 1 | 520×390 (1.3333) | 1200×900 (1.3333) | ✅ 比例一致，未裁剪 |
| P03 | 6 | 284×213 (1.3333) ×6 | 900×900 (1.0000) | ✅ `slice` 中心裁剪（预期） |
| P04–P06 | 0 | — | — | ✅ 无图页正确无 Picture |

### 4.2 视觉验证（executor 自查）

contact sheet 目视确认：

- **P01**：满幅蓝底图，`1920 x 1080` 与 `ASPECT 1.7778:1` 标注清晰可见，
  四角标记与对角线**完整未裁** → 证明 16:9→16:9 无裁剪
- **P02**：左图右文结构成立，图内 `1200 x 900` 标注与网格线完整
- **P03**：六格网格等高对齐，格内图为中心裁剪后的方图（四角标记被裁、中心十字保留）
  → **反向印证 `slice` 的裁剪行为符合预期**
- **P04/P05**：图表页不受图片改造影响，形态与此前一致
- **P06**：纯文字锚点页仍成立

> 图内的**对角线 + 网格 + 四角标记**是刻意的"变形探针"：
> 若被非等比拉伸，对角线会弯折、网格间距会不均。目视确认**无拉伸变形**。

---

## 5. Part D · 素材策略文档

已交付 `docs/image-strategy.md`（四段完整）：

1. **三种素材来源矩阵**：用户提供（首选）/ 程序生成（推荐用于图表与示意）/
   base 搜图（零配置 provider `openverse`+`wikimedia` 无需 key，但**本环境无外网**）/
   base 生图（**14 个后端全部需 key**，当前不可用）
2. **图片规范**：比例（16:9/3:2/4:3/1:1）、最小分辨率（**显示尺寸 ×2**）、
   大小上限（单图 ≤1.5MB、全 deck ≤15MB）、命名规则（全小写连字符、无中文）、
   SVG 引用写法
3. **骨架配合表**：v3 三骨架的适用页型 + 单页图文比例建议 + 与既有 27 骨架的分工
4. **已知限制**：TSD 加密、内嵌 vs 链接、无外网、生图需 key、`slice` 会裁剪、
   **`meet` 会缩 shape**、**图片 shape 藏在 group 里**、图片内容不参与质检

---

## 6. 顺带小修（已完成）

| 项 | 内容 | 验证 |
|---|---|---|
| `deltas/director.md` §2 | 阶段表登记 **B3 · 内容终检（评审卡）**，列为硬门禁 | ✅ 已核对 |
| `deltas/director.md` §8 | 标题改为"B3 阶段"，补阶段定位、分流规则、返修须重跑质检 | ✅ 已核对 |
| `docs/USAGE.md` §2.2/2.3 | 增补"**任何返修后必须重跑质检流程**"（C-028 教训） | ✅ 已核对 |

---

## 7. 失败模式（C-XXX）

### C-029 · 读回验证的"假阴性"陷阱（**差点误判链路不通，已修**）

- **现象**：首次读回验证报 **`TOTAL picture shapes = 0`**，
  但同一 PPTX 的包内**明确存在** `ppt/media/image_*.png`（69531 B）。
  一度倾向得出"图片链路不通"的错误结论。
- **根因**：验证脚本只扫 `slide.shapes` **顶层**。
  本仓库骨架的根级 `<g>` 在导出时会变成 **group shape**，图片被**包在 group 里**，
  顶层遍历**看不到**。递归进 group 后立刻读到 1 个 Picture，尺寸与声明一致。
- **教训**：**"没找到" ≠ "不存在"**。凡按 shape 类型统计，**必须递归**。
  验证脚本已修（`verify_picture.py` 用 `iter_pictures()` 递归），并在文件头记录此坑。
- **推广**：该陷阱对所有"按类型枚举 shape"的检查都成立（含文本框、图表、表格）。

### C-030 · `meet` 会改变 Picture shape 尺寸（**契约行为，已记录**）

- **现象**：1:1 图放进 4:3 槽、用 `meet` 时，读回显示尺寸为 **300×300 并居中**，
  而**不是**槽位的 400×300 内留白。
- **含义**：`meet`（contain）下 **shape 本身会收缩到图片比例**。
- **影响**：若设计意图是"shape 占满槽位、图在其中留白"，用 `meet` 得不到该效果；
  若要求 shape 严格等于槽位几何，**必须用 `slice`**。
- **处置**：记入 `v3/CONTRACT.md` v3-3 与 `docs/image-strategy.md` §4。

### C-031 · 图片骨架撰写的三个几何坑（**已修**）

见 §3.1：多行文本拆兄弟元素（违反 §3 硬标准）、图注 bounds 过窄（溢出 7.2%）、
网格几何超底（726 > 720）。三者均被 checker 拦下并修复。
**说明骨架库既有硬标准确实在起作用**。

---

## 8. 验收对照

| 验收项 | 要求 | 实测 | 结论 |
|---|---|---|---|
| 契约摘要 | 路径/比例/关系/打包行为 | §2.1–2.3 四项齐备 | ✅ |
| 素材可行性矩阵 | 离线可用 / 需 key 分类 + 环境变量名 | §2.4（**全部 key 名已列出，未申请未硬编码**） | ✅ |
| 首次链路验证 | 3 张不同比例 + checker + 导出 + 读回 | §2.5（3 比例对照 + 读回数据） | ✅ |
| 3 骨架入库 v3 | 零 blocking | `Fully passed: 3 (100%)`、`blocking: 0` | ✅ |
| 端到端小样 ≥2 页图片骨架 | 四道质检全过 | **3 页**图片骨架（hero/split/grid）；四道全过 | ✅ |
| 读回图片 shape 正确 | — | **8 个** Picture，尺寸/位置正确 | ✅ |
| 渲染图可读 | — | 6 页 contact sheet，无变形 | ✅ |
| `docs/image-strategy.md` | 四段完整 | §1 矩阵 / §2 规范 / §3 配合表 / §4 限制 | ✅ |
| 顺带小修 | 两项 | director.md §2+§8、USAGE 返修须重跑 | ✅ |
| vendor 零 diff | 必须 | `git status` 无 `vendor-ppt-master/**` | ✅ |

---

## 9. 未验证项（诚实披露）

| 项 | 说明 |
|---|---|
| **图片内容正确性** | `check_hygiene` / `check_overlap` **不解析图片内容**；图片是否贴切完全依赖人工目视 |
| **`svg_final/` 预览产物** | Quick 模式省略该产物，未验证 base64 内嵌预览路径 |
| **`clipPath` 圆角裁剪** | 契约允许但不强制，本轮未使用 |
| **SVG 格式图片** | `<image>` 契约支持 `image/svg+xml`，本轮仅实测位图 |
| **搜图/生图实跑** | ③④ 因**无外网 + 无 key** 未实跑，仅做静态契约分析（provider 名与 key 名已确认） |
| **图片优化触发条件** | 本轮源图均未超 2560px，故走"保留原始字节"分支；**超限重编码**分支未实测 |
| **投影环境** | 未在偏色投影下验证图片色彩表现 |
| **L3 人工评审** | ⚠️ **待指挥官读图**——真实图片观感需人类裁决（沿用 visual-review 流程） |

---

## 10. 《建议》

1. **读回验证统一用递归遍历**（C-029 教训）。本仓库的根级 `<g>` 必然成组，
   凡"按 shape 类型枚举"的脚本都必须递归；建议把该工具作为通用件，
   供后续任何"读回校验"复用（已落在 `deltas/chart-fill/verify_picture.py`）。
2. **图片内容需要人工闸**。四道自动质检对图片内容完全无感。
   建议在 `USAGE.md` 的图片流程中明写"**图片页必须人工目视**"，
   并在 contact sheet 交付时标注哪些页含图。
3. **补充"图片位 → 素材"的占位协议**。当素材未就绪时，本卡用 PIL 生成占位图；
   建议在 `v3/CONTRACT.md` 明确"**占位图必须带可识别标记**（如本卡的网格+标注）"，
   避免占位图被误当成品交付。
4. **图片骨架可继续扩**。当前 3 个。后续可考虑：
   `image-band`（图带 + 下方要点）、`image-compare`（A/B 双图对照）、
   `image-hero-split`（大图 + 侧栏数据）——分别对应 `image-layout-patterns.md` 的
   `#P1-04` / `#P3-03` / `#P3-19`。
5. **若需启用搜图/生图**，需同时满足：**有外网**（WSL 侧当前无）
   + 配好对应 `*_API_KEY`（`.env`）。建议在有网的 Windows 侧环境单独验证一次，
   并把 `image_search.py --dry-run` 纳入前置检查。
6. **`meet` 的使用需谨慎**（C-030）。除非明确接受"shape 收缩"，否则默认用 `slice`。

---

## 11. 附录 · 新增文件清单

| 文件 | 说明 |
|---|---|
| `deltas/layout-assets/v3/image-hero.svg` | 满幅图 + 标题浮层 |
| `deltas/layout-assets/v3/image-split.svg` | 左图右文 |
| `deltas/layout-assets/v3/image-grid.svg` | 3×2 网格 + 图注 |
| `deltas/layout-assets/v3/CONTRACT.md` | v3 填写契约（引用路径/比例契约/`meet` 行为/槽位表） |
| `docs/image-strategy.md` | 素材策略（四段） |
| `deltas/chart-fill/verify_picture.py` | 读回验证（**递归**枚举 Picture shape） |
| `deltas/chart-fill/make_test_images.py` | PIL 测试图生成器（带变形探针） |
| `deltas/chart-fill/example_img_deck.py` | 端到端小样构建脚本（可复现） |
