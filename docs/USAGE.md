# 使用手册（USAGE）

> 从"我有一个主题"到"拿到 .pptx"的完整操作路径。
> 环境细节见 `windows-notes.md`；架构与决策见 `decisions.md`。

## 1. 路线选择指南

> 📌 **按质量需求选档位**（三档：快速出稿 / 标准 / 导演式，含校验门与耗时）见
> [`QUALITY-TIERS.md`](QUALITY-TIERS.md)。本节是其展开的操作细节。

| 判断条件 | 走这条 |
|---|---|
| ≤8 页 / 时效紧 / 内容现成 / 日常周报 | **快速通道** |
| 重要汇报（决策者/管理层/评审）/ ≥10 页 / 需要先"想清楚" | **导演式** |
| 已有成稿 PPTX，只想补备注/动画 | base 的 Enhance Native 路由 |
| 有原生 PPTX 模板要填内容 | base 的 Fill Native 路由 |

**导演式多出的三步**（也是它更慢的原因）：
- **A 受众卡**：听众身份 / 关注点 / 演讲目标 / 知识底色 / 禁忌（5 字段）
- **B 逐页导演稿**：每页 10 字段（观点标题 / 核心结论 / 页型 / 版式 / 主视觉 / 内容 / 面积预算 / 上屏文案 / 收束 / 风险）
- **B2 视觉导演（硬门禁，不得跳过）**：把内容稿压成"上屏短句"，并写明主视觉**解释什么逻辑**（不是长什么样）

## 2. 逐步操作（真实命令，含"你会看到什么"）

### 2.1 项目初始化（全部路线）

```powershell
python <vendor>\scripts\project_manager.py init <项目名> `
    --dir "C:\Users\<you>\AppData\Local\Temp\opencode\<工作目录>" `
    --format ppt169 --quick-generate
```

> ⚠️ **必须带 `--dir`**（W-6）。省掉它项目会落到默认 `projects/` 根，且 `Set-Location` 不能可靠挽救。

**你会看到**：`[OK] Project initialized: <绝对路径>`，随后提示 `Generate SVG files into svg_output/`。
目录结构：`svg_output/` + `validation/`。

### 2.2 选骨架并填充（全部路线）

从 `deltas/layout-assets/{v0,v1,v2}/` 选页型匹配的骨架，复制到 `<项目>/svg_output/P01.svg`、`P02.svg`…

**只需替换 `【槽位名】示例内容` 整体**，不要动坐标 / bounds / 字号。
填充后必须断言：产物中 `【` 计数为 **0**（W-7）。

> ⚠️ **槽位文案必须查文件，不能凭记忆**。填充前先列出骨架的全部槽位：
> ```powershell
> Select-String -Path "deltas\layout-assets\<版本>\<骨架>.svg" -Pattern '【[^】]+】' -AllMatches
> ```
> 或直接查 `v0/CONTRACT.md` §3 的逐槽位清单（含坐标与字号上限）。

#### 🧹 填充后追加：骨架卫生检查（T-FIX4 / C-011）

```powershell
python deltas\layout-assets\check_hygiene.py "<项目>\svg_output"
```

**退出码 `0` 才继续**（`2` = 发现骨架示例内容泄漏）。

> **为什么必须跑**：骨架里可能有**无 `【】` 标记**的示例内容（品牌字、示例数字、
> 示意标签）。填充只替换槽位 → 这些内容被原样带进交付物。它们在几何上完全合法，
> **`svg_quality_checker` 与 D-2 都拦不住**——真实事故 C-011 就是这样让 T-03 的品牌字
> `KB` 出现在 T-02 封面上。检查器的原理、词表与预防规则见
> [`deltas/layout-assets/HYGIENE.md`](../deltas/layout-assets/HYGIENE.md)。

#### 🔍 填充后追加：跨组重叠检查（T-FIX5 / C-015）

```powershell
python deltas\layout-assets\check_overlap.py "<项目>\svg_output"
```

**退出码 `0` 才继续**（`2` = 发现跨组重叠）。
编排建议：**③ 导演式必跑；①② 推荐**。

> **为什么必须跑**：`check_hygiene` 管内容、`svg_quality_checker` 管几何，
> 但**单组几何合法、跨组整体冲突**无人管——C-015 就是图例组与图表组
> 同在 `y=600`，两边 bounds 各自合法，checker 报 `blocking: 0`，只能靠人眼看 contact sheet 发现。
> 原理、判据与豁免机制见
> [`deltas/layout-assets/OVERLAP.md`](../deltas/layout-assets/OVERLAP.md)。

**你会看到**：`svg_output/` 下每个文件是一个完整页面（1280×720）。

#### ⚠️ 返修前提：任何返修后必须重跑质检（C-028 教训）

一旦对 **已过检的 SVG** 做任何改动（改标题、换数字、加行、改口径说明），
**必须重跑下方 2.2 的卫生/重叠检查与 2.3 的质量门**，不得“改完直接导出”。

> 原因：文字变长会破坏几何。T-E2E6 实测：按评审卡返修后，
> checker 报 `blocking: 2`（P07 脚注溢出 12.1%、P14 证据行溢出 7.4%）——
> 都是“只改了字、没重量”造成的。

### 2.3 质量门（全部路线）

```powershell
python <vendor>\scripts\svg_quality_checker.py "<项目绝对路径>" `
    --quick-generate --stage final --json
```

**你会看到**：`[OK] P01.svg - Passed` … 与结尾 `Fully passed: N (100%)`。
**要求**：`blocking: 0`。若有 error，按其给出的 `content (...)` 坐标精确调整（W-5）。

### 2.4 导出 PPTX

```powershell
python <vendor>\scripts\svg_to_pptx.py "<项目绝对路径>" --quick-generate --no-notes
```

**你会看到**：`[Done] Saved: <项目>\exports\<名称>_<时间戳>.pptx` 与
`[POSTFLIGHT] status=passed quality_gate=passed slides=N`。

> 需要演讲者备注时把 `--no-notes` 换成 `--with-notes`（先用 base `executor-notes` 契约写 `notes/total.md`）。

### 2.5 后置质检（推荐）

```powershell
python deltas\pptx-fill-check\detect_overflow.py "<导出.pptx>" --json -o ovf.json
python deltas\pptx-fill-check\check_title_consistency.py "<导出.pptx>" --json -o title.json
```

**你会看到**：`detect_overflow` 的 `P0/P1/OK` 计数（退出码 0=无 P0，2=有 P0）；
`check_title_consistency` 的发现列表。详见 §5。

### 2.6 渲染验证（可选但推荐）

```powershell
python deltas\render-preview\render_png.py "<导出.pptx>" -o "<输出目录>"
```

**你会看到**：每页 `slide-NN.png`（1280×720）+ `contact-sheet.png`（网格缩略图）。
**注意**：产物被安全软件加密，**不要用 WSL 工具读这些 PNG**（W-8），
需在 Windows 上打开 contact sheet 目视。

### 2.7 导演式的额外步骤（在 2.1 之前）

1. 写 **A 受众卡**（5 字段）
2. 写 **B 逐页导演稿**（每页 10 字段）——只写内容结构，**不写颜色/字体/坐标**
3. 过 **B2 门禁**：逐页给出"上屏短句 + 主视觉承担的逻辑"，与 B 稿区分记录
4. 门禁通过后才进入 §2.1 的项目初始化与填充

## 3. 骨架库索引（24 个）

### v0 · 基础六件套（`deltas/layout-assets/v0/`）

| 骨架 | 用途 | 适配页型 |
|---|---|---|
| `cover.svg` | 封面（主标题+副题+信息行） | 开场 |
| `bullets.svg` | 要点列表（3–4 条带编号+说明） | 成果/清单 |
| `two-col-compare.svg` | 双栏对比（左右各 5 槽位） | 风险/对策、A/B |
| `timeline.svg` | 时间轴（3 节点+小结） | 计划/路径 |
| `kpi-hero.svg` | 数据大字（3 个数字） | 指标/成绩 |
| `closing.svg` | 结尾收束（标题+核心句） | 收尾 |

### v1 · 结构扩展十件套（`deltas/layout-assets/v1/`）

| 骨架 | 用途 | 适配页型 |
|---|---|---|
| `toc.svg` | 汇报导览（5 段编号） | 目录 |
| `three-card.svg` | 三卡并列（等重） | 并列论据/诉求 |
| `layered-arch.svg` | 分层架构（3 层，各带职责） | 架构/分层 |
| `process-steps.svg` | 四步流程 + 边界说明 | 机制/步骤 |
| `comparison-rows.svg` | 三行对比（名称+结论） | 方案对比 |
| `budget-4.svg` | 四项金额 + 合计 | 预算拆分 |
| `risk-rows.svg` | 三行风险→对策（橙红语义） | 风险 |
| `metrics-3.svg` | 三项验收指标 | 验收标准 |
| `decision-3.svg` | 三条决策请求（深色） | 决策/请求 |
| `sentence-hero.svg` | 结尾主张句 | 收尾 |

### v2 · 图表与视觉锚点八件套（`deltas/layout-assets/v2/`）

**图表族**（静态 SVG 几何，数据→坐标映射见 `v2/CONTRACT.md` §2）

| 骨架 | 用途 | 上限 |
|---|---|---|
| `bar-chart.svg` | 柱状对比（最大值定高） | ≤6 柱 |
| `line-chart.svg` | 趋势折线 + 关键点标注 | ≤8 点 |
| `donut-chart.svg` | 占比环形 + 中心主数据 | ≤4 段 |
| `comparison-bars.svg` | 横向对比条（数值右对齐） | ≤5 项 |

**视觉锚点族**（增强表现力）

| 骨架 | 用途 | 要点 |
|---|---|---|
| `cover-bold.svg` | 强化封面 | 大色块 + 52pt 标题（≤12 字） |
| `section-hero.svg` | 章节封页 | 240pt 章节号（**仅供 ≥3 章 deck**） |
| `evidence-wall.svg` | 证据墙 | 2×2 矩阵，末格深底反白 |
| `quote-hero.svg` | 金句/主张页 | 大引号 + 大留白 |

**填写契约**：`v0/CONTRACT.md`（通用硬标准）+ `v2/CONTRACT.md`（图表映射与锚点规则，含**深色页预算 ≤15%**）。

## 4. 常见场景配方（基于 T-01/T-03 实战）

### 周报 6 页（快速通道）

```
P01 cover          封面
P02 bullets        本周完成 N 项
P03 two-col-compare 风险与对策
P04 timeline(v0) 或 three-card(v1)  下周计划
P05 kpi-hero(v0) 或 three-card(v1)  关键数据/需要的支持
P06 closing        总结
```

### 方案 20 页（导演式，参考 T-03 实战）

```
P01 cover-bold       封面（视觉锚点）
P02 toc              导览
P03 two-col-compare  背景/瓶颈
P04-P06 layered-arch/process-steps  现状问题（2-3 页）
P07-P09 three-card/layered-arch      需求与目标
P10-P12 process-steps/comparison-rows 方案与能力
P13-P15 timeline/three-card          实施路径与里程碑
P16 bar-chart        预算（图表）
P17 evidence-wall    ROI 证据（视觉锚点）
P18 risk-rows        风险与对策
P19 comparison-bars  验收指标（图表）
P20 decision-3 或 section-hero       决策请求
P21 quote-hero       金句收尾（视觉锚点）
```

**节奏建议**：深色锚点页 ≤15% 页数；锚点之间至少隔 3–4 页普通页。

## 5. 工具用法与结果解读

### 5.1 `svg_quality_checker.py`（base，质量门）

```powershell
python <vendor>\scripts\svg_quality_checker.py "<proj>" --quick-generate --stage final --json
```
- 读 `Fully passed: N (100%)` 与 `blocking: 0`
- `introduced` 是"本次新增的建议项"，也应力求 0
- 报告 JSON：`<proj>/validation/svg_quality_report.json`

### 5.2 `detect_overflow.py`（出框检测）

```powershell
python deltas\pptx-fill-check\detect_overflow.py "<pptx>" [--tolerance 1.2]
```
- **判据按 wrap 分轴**：`wrap=True` 走垂直（折行数）；`wrap=False` 走水平（最长段宽度比）
- 档位：`≤1.0` OK ｜ `1.0–tolerance` P1 ｜ `>tolerance` P0
- `autofit`（`TEXT_TO_FIT_SHAPE` / `SHAPE_TO_FIT_TEXT`）一律软放行
- **退出码**：`0`=无 P0 ｜ `2`=有 P0

### 5.3 `check_title_consistency.py`（标题字号一致性）

```powershell
python deltas\pptx-fill-check\check_title_consistency.py "<pptx>"
```
- **占位符路径**：按 placeholder role 分组（template-fill 产物）
- **自由设计路径**：**页面主标题通道**——每页只取字号最大的标题候选做跨页比较
  （特征 subtier 方案已按止损条款弃用）
- ⚠️ **已知边界**：同页非主标题的字号漂移**不再被检测**（有意的取舍）

### 5.4 `render_png.py`（渲染预览）

```powershell
python deltas\render-preview\render_png.py "<pptx>" -o "<outdir>" [--width 1920 --height 1080]
```
- 渲染器：本机为 **WPS Office 提供的 PowerPoint COM**
- 产出 `slide-NN.png` + `contact-sheet.png`
- ⚠️ 产物被加密（W-8），图片处理须在 Windows 进程内完成

## 6. 环境注意（W-1~W-8）

| 编号 | 一句话 | 详情 |
|---|---|---|
| W-1 | 导出四步序列：`init` → lock → checker → `svg_to_pptx` | `windows-notes.md` |
| W-2 | 控制台中文乱码 ≠ 数据损坏（看文件字节） | 同上 |
| W-3 | 跨侧调用用 `C:\...` 路径 | 同上 |
| W-4 | lock 脚手架需填真实值 | 同上 |
| W-5 | 手写 SVG 契约速查 | 同上 |
| W-6 | `init` 必须带 `--dir` | 同上 |
| W-7 | 填充后断言 `【` 归零 | 同上 |
| W-8 | 渲染产物加密，图片处理走 Windows | 同上 |

## 7. 能力边界

| 边界 | 说明 |
|---|---|
| **两步质检路径不同** | 占位符路径（template-fill）用 role 分组；自由设计路径用主标题通道 |
| **同页检测已移除** | 自由设计路径不再检测同页非主标题漂移（止损取舍） |
| **单一渲染器** | 仅 WPS COM 可用；LibreOffice 未安装 |
| **图表是静态几何** | 数据变化需按 `v2/CONTRACT.md` 公式手工重算坐标；非 PowerPoint 数据图表 |
| **视觉评审需人工** | 加密限制使自动化无法目视；contact sheet 需人在 Windows 上看 |
| **无图片素材支持** | 骨架为文字/几何；图片页需自行扩展 |

## 8. 如何发起一次制作（请求模板，复制即用）

给 AI 执行者的六输入项：

```
请制作一份 PPT。

1. 主题：<一句话说明要讲什么>
2. 受众：<谁听 + 人数 + 他们最关心什么>
3. 页数：<6-8 页 / 18-22 页 / 其他>
4. 时长：<5-8 分钟 / 20-30 分钟 / 其他>
5. 素材：<文档路径 / 数据 / 仅口头描述；无则写"无素材，允许自拟并标注假设">
6. 风格偏好：<简洁克制（默认）/ 视觉增强 / 其他；或指定骨架>
```

**补充说明（可选）**：
- 是否需要演讲者备注（逐字稿 or 提词卡）
- 是否有指定的骨架页型或配色
- 交付形态（仅 .pptx / 需要 contact sheet 预览）

**执行者会**：定路线 → 产导演稿（若导演式）→ 选骨架填充 → 过 checker → 导出 → D-2 质检 →（可选）渲染。
