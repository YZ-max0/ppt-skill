# base 表格模板接入器（table-fill）

> 位置：`deltas/table-fill/`（repo 定制层；`vendor-ppt-master/` **零改动**）
> 任务来源：`tasks/T-A1.md` Part A ｜ 契约依据：`vendor-ppt-master/templates/tables/` 的
> `README.md` + `table-vocabulary.md` + `tables_index.json` + `VISUALIZATION_TEMPLATE_AUTHORING.md`

## 0. 一句话结论

**tables 族与 charts 族是同一个模式**：`templates/tables/` 的 6 个 SVG 是
**渲染好的示例**，不是待填槽位的骨架（实测 `grep 【】` **0 命中**），数据硬编码进几何。

但有两处**关键差异**（本卡实测）：

| 维度 | charts（33 个） | tables（6 个） |
|---|---|---|
| 数据模型 `<metadata>` | **全部**都有 | **仅 2/6** 有（`record_table` / `hierarchical_table`） |
| 原生标记 `data-pptx-replace-with="table"` | 全部有（chart） | **仅 2/6** 有 |
| 加 `--native-charts-and-tables` 的效果 | 全部生成原生 Chart | **仅那 2 个**生成原生 Table；其余 4 个拆成散落文本框 |
| 几何复杂度 | 高（坐标映射公式） | 低（网格按 `column_widths`/`row_heights` 累加） |

**实测证据**：原样导出 `metric_table` → 读回 **0 个 table shape、37 个文本框**；
原样导出 `hierarchical_table` → 读回 **1 个 table shape（10×5）**。

## 1. 为什么仍要做这个工具

表格的坐标计算（累加）比图表简单，所以 `fill_table.py` 的价值**不在"算坐标"**，而在：

1. **让 4 个无标记模板也能走原生表格路径** —— 本工具产出的 SVG **一律带**
   `data-pptx-replace-with="table"` + 完整 `<metadata>`，故 6 个模板的能力被拉齐
   （实测：生成的 2 页导出后读回 **2/2 原生 Table**，而 base 原样的 `metric_table` 是 0/1）。
2. **消除手改 6 个 SVG 的重复劳动**。
3. **与 `fill_chart.py` / `v2_chart_gen.py` 同一套 spec 与 CLI 风格**。

## 2. 选型（按 `tables_index.json` 规则原文）

`tables_index.json` 的 `summary` 是**选型规则**（`Pick for … Skip if …`），逐条对照：

| 选用 | 规则原文 | 本卡用例 |
|---|---|---|
| `record_table` | *Pick for flat records addressed by stable heterogeneous fields. Skip for KPI scanning (use `metric_table`) or grouped rows and totals (use `hierarchical_table`).* | **二期交付物台账**：每行一个交付物，字段异构（名称/说明/责任方/状态/完成度） |
| `hierarchical_table` | *Pick for grouped or indented row hierarchies across stable measure columns, including subtotals and totals. Skip for flat records (use `record_table`).* | **三期预算分项拆解**：分组缩进行 + 小计 + 合计行 |
| `metric_table`（**未选**） | *Pick for operating metrics by entity with current values, changes, statuses, or target progress inside cells. Skip if **marks leave the grid** and encode …* | 跳过理由：本卡的两组数据前者是**异构字段台账**（非同一指标族），后者有**分组层级**；且 `metric_table` 在 base 里**无原生标记**，走不了原生表格路径（见 §0） |
| `comparison_matrix` | *Pick for criteria × alternatives with prose, exact values, or mixed facts. Skip if cells encode only feature states …* | 跳过理由：本卡无"标准 × 备选方案"的交叉矩阵需求 |
| `feature_matrix` / `rating_matrix` | 需要能力状态 / 单一序数标度 | 跳过理由：无对应数据关系 |

> **卡内提及的 `comparison_matrix` 未选，理由如上**：T-SMOKE 熟悉它是因为冒烟测试用过，
> 但本批数据是"台账"与"预算层级"，用它是**为用而用**（违反 §L-0 反向纪律）。

## 3. 三步接入法（与 chart-fill 同款）

### 第 1 步 · 校验契约（原样复制看基线）

```powershell
Copy-Item <vendor>\templates\tables\<key>.svg <proj>\svg_output\P01.svg
python <vendor>\scripts\svg_quality_checker.py <proj> --quick-generate --stage final
```

实测 3 个模板原样：`blocking: 0`、`introduced: 3`（缺 `data-pptx-page-role`，advisory）。

### 第 2 步 · 读数据模型

有 metadata 的 2 个模板给出完整 schema：

```jsonc
{
  "name": "record-table", "x": 80, "y": 150, "width": 1120, "height": 420,
  "strict_grid": true,
  "column_widths": [200, 420, 180, 140, 180],
  "row_heights":    [60, 60, 60, 60, 60, 60, 60],
  "style": { "header_fill": "...", "band_row": true, "border_color": "...",
             "padding": {"left": 12, ...}, "valign": "middle" },
  "columns": [ {"text": "RECORD", "bold": true}, {"text": "CAPACITY", "align": "r"} ],
  "rows":    [ [ {"text": "REC-001"}, {"text": "120", "align": "r", "bold": true} ] ]
}
```

**要点**：`rows` 是**二维数组**，每格是对象（`text` / `align` / `bold` / `color`）；
列对齐在 `columns[i].align` 上作为默认值，单元格可覆盖。

### 第 3 步 · 按数据重算几何

表格几何 = **累加**：`x_i = x0 + Σ(前面列宽)`、`y_j = y0 + Σ(前面行高)`。
本工具已实现，只需给 JSON：

```jsonc
{ "name": "deliverable-record",
  "title": "二期交付物台账", "subtitle": "…",
  "columns": [{"text":"交付物","bold":true}, {"text":"完成度","align":"r","bold":true}],
  "column_widths": [200, 420, 180, 140, 180],
  "rows": [[{"text":"源系统接入"}, {"text":"100%","align":"r","bold":true}]],
  "note": "口径：…" }
```

**视觉纪律**：工具产出使用仓库语义色（`#F0F0EE` 表头底 / `#0F172A` 正文 /
`#E2E8F0` 边框 / `#002FA7` 主色 / `#FF6B35` 负向），**不沿用** base 模板的
Tailwind 色（`#F1F5F9`/`#475569`），以符合 `v2/CONTRACT.md` v2-2。
即：**借模板的网格契约与 metadata schema，不借它的配色**。

## 4. 用法

```powershell
# 生成 T-A1 示例两页（record_table + hierarchical_table 形态）
python deltas\table-fill\fill_table.py --demo -o <outdir>\

# 单页：从 JSON 规格生成
python deltas\table-fill\fill_table.py --spec t.json -o P01.svg

# 读回验证（递归枚举 Table shape / 行列 / 单元格抽样）
python deltas\table-fill\verify_table.py <导出.pptx>
```

**读回验证注意（C-029 教训）**：本仓库骨架的根级 `<g>` 会成组，
**必须递归进 group** 才能读到 shape，否则得到"0 个表"的假阴性。

## 5. 场景分工：现有骨架的表格类页型 vs base 表格模板

| 场景 | 用哪个 | 理由 |
|---|---|---|
| 3–5 行、行内含**一句话结论**（如"方案对比""风险→对策"） | **v1 骨架** `comparison-rows` / `risk-rows` | 骨架已按"名称 + 结论"排版，填槽位即用；无表头/网格线，视觉更轻 |
| 需要**明确的行列表头 + 网格线 + 多列数值** | **base 表格模板 + `fill_table.py`** | 骨架无表头/网格概念；表格模板天然表达"行列表头共同定位一格" |
| 需要**原生 PowerPoint 表格**（可在 PPT 里增删行列） | **base 模板 + `--native-charts-and-tables`** | 需 `data-pptx-replace-with="table"` + metadata；**骨架没有该标记** |
| 分组/缩进 + 小计/合计 | base `hierarchical_table` | 骨架无层级行概念 |
| 能力有无（√/×/部分） | base `feature_matrix` | 需要状态语义 |
| 单一序数标度评分 | base `rating_matrix` | 需要统一标度 |

**决策口诀**：
*能填槽位就用骨架（快、配色统一）；要表头网格就用 base 表格（准、结构明确）；
要能在 PPT 里改行列就用 base 原生表格（真表格）。*

> ⚠️ **后两条在 base 里有坑**：原生表格路径**只对 2/6 模板生效**（`record_table` /
> `hierarchical_table`）。若需要原生表格且数据形态不是这两类，**用本工具生成**
> （它会为任意数据形态产出合规的 `replace-with="table"` + metadata）。

## 6. 已知边界

- 本工具实现**通用表格**（任意列数/行数）；`feature_matrix` / `rating_matrix` 的
  特殊单元格语义（状态标记、序数标度圆点）**未实现**。
- base 的 4 个无标记模板**不能**通过 `--native-charts-and-tables` 变成原生表格
  ——这是 base 的现状，不是本工具的问题；本工具绕开了它。
- 表格内容不参与 `check_hygiene` / `check_overlap` 的**语义**判断（只查文本存在与几何）。
- 原生表格路由会**归一化样式**（base 警告原文：native objects may normalize styling）；
  要求像素级一致时用默认导出。
- 本工具**不修改 vendor**。

## 7. 依赖

仅 Python 标准库（`argparse` / `json`）。读回验证额外需 `python-pptx`（已在环境中）。
