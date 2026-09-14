# base 图表模板接入器（chart-fill）

> 位置：`deltas/chart-fill/`（repo 定制层；`vendor-ppt-master/` **零改动**）
> 任务来源：`tasks/T-E2E3.md` Part A ｜ 首次实战：T-02 年终述职（`docs/e2e-03-report.md`）
> 契约依据：`vendor-ppt-master/templates/charts/` 的 `README.md` + `chart-vocabulary.md`
> + `charts_index.json` + `templates/VISUALIZATION_TEMPLATE_AUTHORING.md`

## 0. 一句话结论（Part A 最重要的发现）

**base 的 33 个图表模板不是"待填槽位的骨架"，而是"渲染好的示例 + 两份契约"。**

| 事实 | 证据 |
|---|---|
| 无 `【槽位】` 标记 | `grep -o "【[^】]*】" *.svg` → 0 命中 |
| 数据已硬编码进几何 | `column_chart.svg` 的柱高按 `185/142/128/…` 写死（注释标明 `370px height, 100M=200px`） |
| 带数据模型契约 | 每个模板内嵌 `<metadata type="application/json">`，声明 `type/categories/series/values/style` |
| 带原生图表标记 | 该 metadata 挂在 `<g data-pptx-replace-with="chart">` 上 |

因此"接入"= **取两份契约（metadata 的数据模型 + 模板的视觉语言），按数据重算几何**。
本工具就是那个"重算器"——把 `deltas/layout-assets/v2/CONTRACT.md` §2.6 列为易错点的
手工坐标计算（最大值定高 / 轴与绘区边界 / 标签越界）自动化。

### 与"复制到项目"的关系（卡内异议区回应）

任务卡写"复制到测试项目 `svg_output`，填 T-02 的模拟数据"。
实测结论：**原样复制能过 checker（`blocking: 0`，见 §3），但数据是示例数据**，
无法承载 T-02 的真实数字。所以正确姿势是：

```
原样复制  = 校验契约（证明模板本身合规，属研究步骤）
重算几何  = 真正接入（把示例数据换成源数据）  ← 本工具的职责
```

两者都做了，见 §3 与 §4。

## 1. 选型：为什么是这 3 个

依据 `charts_index.json` 的 `summary`（选型规则，形如 `Pick for … Skip if …`）
对照 T-02 的信息关系：

| 页面需要表达的关系 | 选用 | `charts_index` 的选型规则 | T-02 落点 |
|---|---|---|---|
| 目标 vs 实际，带明确基线 | `bullet_chart` | Pick for 3-7 KPIs each with explicit target + actual. **Skip for items with only completion % and no target baseline (use `progress_bar_chart`).** | P07 四项考核指标（有目标值） |
| 时间序列看方向 | `line_chart` | Pick for 1-3 time-series on a continuous axis showing direction. **Skip if different units (use `dual_axis_line_chart`).** | P06 分季度收入与净利润（同单位万元 → 不用 dual_axis） |
| 单序列类目对比 | `column_chart` | Pick for single-series category value comparison, 3-8 categories. **Skip for >12 long-label items (use `horizontal_bar_chart`).** | P08 五年营业收入（5 类目、短标签） |

**被排除的候选及理由**（同样按规则，不是凭感觉）：

| 候选 | 规则原文 | 排除理由 |
|---|---|---|
| `grouped_bar_chart` | Pick for 2-4 series side-by-side … Skip if showing composition | 任务卡首推，但 T-02 的年度对比是**单序列年际变化**，不是"同类别下多序列并排"；用于 P08 会造出不存在的对比维度 |
| `dual_axis_line_chart` | Pick for 2 metrics with **different units/scales** | P06 的收入与净利润**同为万元**，规则明确说同单位应走 `line_chart` |
| `waterfall_chart` | Pick for stepwise additive/subtractive breakdown bridging start→end. Skip if **no running total** | 任务卡首推"年度增量"。T-02 原文只有"约 15 个数字/指标"，**没有利润桥式的加减项分解**，强行套用需**编造增减项**——违反 v2-1"图表数据必须来自既有事实" |
| `progress_bar_chart` | Skip if items have explicit target+actual values (use bullet_chart) | P07 有明确目标值，故用 bullet 而非 progress_bar |
| `gauge_chart` | Skip for multiple metrics | 只适用于单个受限指标 |

> **对任务卡建议方向的一处修正**：卡内建议"年度增量用 `waterfall`"。
> 按 `charts_index.json` 的 `Skip if no running total` 与 v2-1 纪律，
> **T-02 无利润桥数据，不应使用 waterfall**；年度增量改用 `column_chart`（年际对比）表达。
> 这是"以文档说法为准"的落实，已记入报告 §4。

## 2. 用法

```powershell
# 生成 T-02 示例三页（column / line / bullet）
python deltas\chart-fill\fill_chart.py --demo -o <outdir>\

# 单页：从 JSON 规格生成
python deltas\chart-fill\fill_chart.py --type bullet --spec p07.json -o P07.svg
```

数据规格（JSON）：

```jsonc
// column / line
{ "title": "…", "subtitle": "…", "unit": "万元",
  "categories": ["2021","2022"],
  "series": [{ "name": "营业收入", "values": [3200, 3850], "color": "#002FA7" }],
  "note": "口径说明…" }

// bullet
{ "title": "…", "items": [{ "name":"营业收入","target":6000,"actual":6240,"unit":" 万元" }],
  "note": "…" }
```

配套的骨架填充器（T-02 全篇通用）：

```powershell
python deltas\chart-fill\fill_skeleton.py        # 由调用方 import 使用，见 docstring
```

## 3. 三步接入法（可被后续 30 个模板复用）

### 第 1 步 · 校验契约（证明模板本身合规）

```powershell
# 原样复制到 svg_output，跑 checker
Copy-Item <vendor>\templates\charts\<key>.svg <proj>\svg_output\P01.svg
python <vendor>\scripts\svg_quality_checker.py <proj> --quick-generate --stage final
```

实测（3 个模板原样）：`blocking: 0` / exit 0；唯一提示是
`introduced: 3` —— `page SVG is missing root data-pptx-page-role`。
**这是 advisory，不是错误**；补一行根属性即可消除（第 3 步已内建）：

```xml
<svg … data-pptx-page-role="content">
```

### 第 2 步 · 读数据模型

从模板的 `<metadata type="application/json">` 取字段清单：

| 模板 | type | 数据字段 |
|---|---|---|
| `column_chart` | `column` | `categories[]`, `series[{name,values}]`, `style.colors` |
| `line_chart` | `line` | `categories[]`, `series[{name,values}]` |
| `bullet_chart` | （无 metadata） | 逐行 `Target`/`Actual`/达成率写在几何里（见下） |
| `waterfall_chart` | `waterfall` | `values[]`, `subtotals[]` |

### 第 3 步 · 按公式重算几何

各类型的映射公式（照 `v2/CONTRACT.md` §2 的口径，绘图区统一为
`x∈[160,1160]`、`y∈[190,560]`）：

| 类型 | 公式 |
|---|---|
| column | `柱高 = 值 / nice_max(最大值) × (560-190)`；`组中心 = 160 + 槽宽×(i+0.5)` |
| line | `点x = 160 + (i/(n-1))×1000`；`点y = 560 - (值/nice_max)×370` |
| bullet | 轨道满宽 = `目标×1.25`；`实际条长 = 实际/(目标×1.25) × 轨道宽`；目标标尺落在 `目标/(目标×1.25)` 处 |

`nice_max()` 把最大值上取整到 1/1.2/1.5/2/2.5/3/4/5/6/8/10×10ⁿ，避免刻度出现 `1850` 这种数。

**视觉语言对齐**：生成器输出仓库既有语义色（`#002FA7` 主色 / `#FF6B35` 风险 /
`#0F172A` 正文 / `#64748B` 次级 / `#E2E8F0` 网格），**不沿用模板自带的 Tailwind 色**
（`#3B82F6`/`#10B981`/`#F59E0B` 等），以符合 `v2/CONTRACT.md` v2-2 语义色纪律。
即：**借模板的几何契约，不借它的配色**。

## 4. 场景分工：v2 骨架（4 个）vs base 模板（33 个）

两者不是替代关系。判据是"**数据是否需要按源值重算几何**"：

| 场景 | 用哪个 | 理由 |
|---|---|---|
| 数据固定、已知值少（≤6 项）、页内还要排文字 | **v2 骨架**（`bar-chart` / `comparison-bars` / `donut-chart` / `line-chart`） | 静态几何已按公式摆好，填充槽位即用；与 v0/v1 骨架同源，配色天然一致 |
| 数据需要按源值重算（刻度/归一化/多序列） | **base 模板 + `fill_chart.py`** | 模板自带轴、网格、刻度、图例、`chart-plot-area` 标记，重算器负责坐标 |
| 需要原生 PowerPoint 数据图表（可在 PPT 里改数） | base 模板 + `--native-charts-and-tables` | 模板带 `data-pptx-replace-with="chart"` + JSON payload；v2 骨架**没有**该标记 |
| 目标 vs 实际（业绩考核） | base `bullet_chart` | v2 骨架无此页型 |
| 瀑布/漏斗/桑基/雷达等特殊关系 | base 对应模板 | v2 只有 4 个图表族 |

**决策口诀**：*能填槽位就用 v2（快、配色统一）；要算坐标就用 base（准、带轴）；要能改数就用 base 原生（真图表）。*

**原生图表注意事项**（`references/native-data-interface.md`）：
原生路由是 data-object-first，**可能失真**——标记内的局部标签、标注、KPI 会丢失或归一化。
需要与设计稿像素级一致时，用默认 SVG-fallback 导出（不传 `--native-charts-and-tables`）。

## 5. 已知边界

- 本工具实现 **6 个模板**（column / line / **dual_axis** / **progress** / **area** / bullet）。
  其余 27 个按 §3 三步法可逐个补齐。
- **渲染器必须按规则声明的项数上限自证**（C-016 教训）：`charts_index` 说 `progress_bar_chart` 支持 3-8 项，而初版写死行高 92px，6 项即溢出画布（checker blocking=3）。现已改为行高自适应 `min(86, 512/(n-1))`；新增类型时请按上限项数各跑一次 checker。
- **图例必须独立于类目标签行**（C-015 教训）：初版把图例基线设为 `CAT_Y=600`，与横轴类目标签同排，导致图例压字；现独立为 `LEGEND_Y=648`。该缺陷 checker 拦不住（图例与类目分属两个 `<g>`，各自 bounds 均合法），只能靠渲染后目视发现。
- `bullet_chart` 在 base 里**无 metadata**，其数据模型是从几何反推的（轨道三段 + 目标线 + 达成率）。
  也因此它**不带原生图表标记**，`--native-charts-and-tables` 对它无效（仍是矢量形状）。
- 原生图表路由实测：对带标记的 `column_chart` 导出 `--native-charts-and-tables` 后，
  包内生成 `ppt/charts/chart201.xml`，python-pptx 读到 **1 个 native chart shape** →
  路由可用。但注意它**只对该页生效**（无标记的页仍走矢量回退），且样式会被 PowerPoint 归一化。
- 图表为静态 SVG 几何时不含数据绑定；改数需重跑本工具。

## 5.1 类型清单与依据（T-E2E4 后）

| 类型 | `charts_index` 规则 | 关键几何 |
|---|---|---|
| `column` | Pick for single-series category … 3-8 categories | 柱高 = 值/nice_max × 370 |
| `line` | Pick for 1-3 time-series … showing direction | 点均匀分布；末点标注 |
| `bullet` | Pick for 3-7 KPIs with explicit target + actual | 轨道满宽 = 目标×1.25；目标标尺 |
| `dual_axis` | Pick for 2 metrics with **different units/scales** | 左右两套刻度；右轴刻度另绘 |
| `progress` | Pick for 3-8 items each with a **completion %** | 行高自适应，8 项也落在画布内 |
| `area` | Pick for 1-2 **cumulative** trend series emphasizing volume | 折线 + 闭合多边形 |

> 选型务必**逐条对照规则原文**，不要按直觉。T-E2E4 的完整选型理由表见
> `docs/e2e-04-report.md` §2（含一处与契约措辞的偏差记录 C-017）。

## 5.2 逐字稿校验器（`check_notes.py`）

D-4 逐字稿轨道的自动校验（P-2 篇幅 / P-3 口语化 / P-7 总时长 / P-9 一一对应 / P-10 纯净性）：

```powershell
python deltas\chart-fill\check_notes.py <项目>\notes\total.md <项目>\svg_output <现场分钟数>
```

- P-7 总时长**强依赖语速假设**，故输出 150/180/200/240 字-分钟的**灵敏度区间**，而非单点结论。
- 封面/章节/纯过渡页按 P-2 明文豁免 150 字下限。

## 6. 依赖

仅 Python 标准库（`argparse` / `json` / `math` / `re` / `xml.etree`）。
无第三方依赖；不修改 vendor。
