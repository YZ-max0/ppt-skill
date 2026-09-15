# T-A1 交付报告 · tables 族接入 + v2 图表坐标自动化

> 执行者：开发工程师 ｜ 日期：2026-09-15 ｜ 卡：`tasks/T-A1.md`
> 前置：T-IMG1 已关闭（`21949c4`）
> 结论：**Part A 表格接入完成**（生成版导出读回 **2/2 原生 Table**）；
> **Part B 四类图表坐标自动化完成**（**3/4 与手写版几何逐项相同**，
> 第 4 类差异来自**手写骨架自身的缺陷**）；
> 关闭 `v2/CONTRACT.md` §2.6 手工坐标风险；**发现并修复 1 个真实骨架缺陷（C-032）**，
> 记录 1 个未修缺陷（C-033）。

---

## 1. 命令表（含耗时）

环境：Windows PowerShell 5.1 + `python` 3.12.3 + python-pptx 1.0.2

| # | 阶段 | 命令/动作 | exit | 耗时 |
|---|---|---|---|---|
| A1 | 契约研究 | 读 `templates/tables/` 的 `README.md` + `table-vocabulary.md` + `tables_index.json` | — | 会话内 |
| A2 | 原样接入实测 | 3 模板原样 → checker → 导出 → 读回 | **0** | 4 s |
| A3 | 原生路径实测 | `metric_table` / `hierarchical_table` / `record_table` 加 `--native` | **0** | 5 s |
| A4 | 填充器撰写 | `deltas/table-fill/fill_table.py` | — | 会话内 |
| A5 | 生成版验证 | checker（2 页）→ 导出 → **读回 2/2 原生 Table** | **0** | 4 s |
| B1 | 重算器撰写 | `deltas/chart-fill/v2_chart_gen.py`（4 类） | — | 会话内 |
| B2 | 几何对比 | `compare_v2.py`（生成版 vs 手写版，逐项比对） | 0 | < 1 s |
| B3 | 修复 C-032 | `deltas/layout-assets/v2/donut-chart.svg` 弧长 502→754 | — | — |
| B4 | §2.6 更新 | `v2/CONTRACT.md` 标注"已自动化" | — | — |
| C1 | 合并 6 页质检 | checker / hygiene / overlap / D-2 四道 | **全 0** | 6 s |
| C2 | 导出 + 读回 | 默认导出 + `--native-charts-and-tables` | **0** | 5 s |
| C3 | 渲染 | contact sheet（6 页） | 0 | 3 s |

**机器侧总耗时 ≈ 27 秒**（A2–C3）。含迭代修复约 **12 分钟**。
> **计时口径（诚实披露）**：契约研究、两个工具撰写、README 与本文档均为 agent 会话内产出，
> wall-clock 不代表人类作者耗时。

**contact sheet（供指挥官读图）**：
`C:\Users\EDY\AppData\Local\Temp\opencode\rfinal-a1\g3_ppt169_20260915\render\contact-sheet.png`（6 页）

---

## 2. Part A · 表格契约摘要

来源：`vendor-ppt-master/templates/tables/README.md` + `tables_index.json`

### 2.1 是"渲染好的示例 + 契约"，与 charts 同模式

| 项 | 实测结果 |
|---|---|
| 是否有 `【槽位】` 标记 | **0 命中**（6 个 SVG 全无） |
| 数据是否硬编码 | 是（单元格文本直接写在几何里） |
| 是否有 `<metadata>` 数据模型 | **仅 2/6**（`record_table` / `hierarchical_table`） |
| 是否有 `data-pptx-replace-with="table"` | **仅同 2 个** |

> **结论**：tables 与 charts **同模式**，但**原生就绪度低得多**——只有 2/6 带原生标记。

### 2.2 ⚠️ 关键差异实测：`--native-charts-and-tables` 只对 2/6 生效

| 模板 | 有 marker+metadata | 加 `--native` 后读回 |
|---|---|---|
| `hierarchical_table` | ✅ | **1 个原生 Table（10×5）** |
| `record_table` | ✅ | **1 个原生 Table（7×5）** |
| `metric_table` | ❌ | **0 个 Table，37 个散落文本框** |
| `comparison_matrix` | ❌ | **0 个 Table，30 个散落文本框** |
| `feature_matrix` / `rating_matrix` | ❌ | （未单独实测，同类） |

**这意味着**：用户想"在 PPT 里编辑表格行列"，**只有 2 个模板可用**。

### 2.3 数据模型（取自 metadata）

```jsonc
{ "name": "record-table", "x": 80, "y": 150, "width": 1120, "height": 420,
  "strict_grid": true,
  "column_widths": [200, 420, 180, 140, 180],
  "row_heights":    [60, 60, 60, 60, 60, 60, 60],
  "style": { "header_fill": "#F1F5F9", "band_row": true, "border_color": "#CBD5E1",
             "padding": {"left": 12, "right": 12, "top": 6, "bottom": 6}, "valign": "middle" },
  "columns": [ {"text": "RECORD", "bold": true}, {"text": "CAPACITY", "align": "r"} ],
  "rows":    [ [ {"text": "REC-001", "color": "#475569"},
                 {"text": "120", "align": "r", "bold": true} ] ] }
```

**要点**：`rows` 是二维数组，每格是对象（`text`/`align`/`bold`/`color`）；
列级 `align` 作默认，单元格可覆盖。几何 = **列宽/行高的累加**（比图表简单）。

### 2.4 选型理由（按 `tables_index.json` 规则原文）

| 选用 | 规则原文 | 本卡用例 |
|---|---|---|
| `record_table` | *Pick for flat records addressed by stable heterogeneous fields. Skip for KPI scanning (use `metric_table`) or grouped rows and totals (use `hierarchical_table`).* | 二期交付物台账（每行一交付物，字段异构） |
| `hierarchical_table` | *Pick for grouped or indented row hierarchies across stable measure columns, **including subtotals and totals**. Skip for flat records.* | 三期预算分项（分组 + 小计 + 合计行） |
| `metric_table`（**未选**） | *Pick for operating metrics by entity with current values, changes, statuses…* | 理由：两组数据分别是"异构字段台账"与"有层级的分组"，不是同一指标族；且该模板**无原生标记**（§2.2） |
| `comparison_matrix`（**未选**） | *Pick for criteria × alternatives with prose, exact values, or mixed facts.* | 理由：**本卡无"标准 × 备选方案"交叉矩阵需求**。T-SMOKE 熟悉它只因冒烟测试用过，此处用它属"为用而用"（违反 §L-0 反向纪律） |
| `feature_matrix` / `rating_matrix` | 需要能力状态 / 单一序数标度 | 理由：无对应数据关系 |

### 2.5 生成版验证（读回数据齐全）

| 项 | 结果 |
|---|---|
| checker | `Fully passed: 2 (100%)`、`blocking: 0`、`introduced: 0` |
| 默认导出读回 | 0 个 Table（矢量形状，符合预期） |
| **`--native` 导出读回** | **2/2 原生 Table** |
| 表 1 | `budget-hierarchy` **6 行 × 5 列**，`row0=['项目','方向','实施','小计','占比']`，`row1=['实时链路改造','170','170','340','55%']` |
| 表 2 | `deliverable-record` **7 行 × 5 列**，`row0=['交付物','说明','责任方','状态','完成度']`，`row1=['源系统接入','19 个源系统完成验收','平台组','已完成','100%']` |

> **对比 base 原样**：`metric_table` 加 `--native` 仍得 **0 个 Table**；
> 本工具产出的表格 **2/2 都是原生 Table** —— 即工具**把 6 个模板的能力拉齐了**。

---

## 3. Part B · v2 图表坐标自动化

### 3.1 方案选择（卡内给了 a/b 二选一）

**选 (b) 独立 `v2_chart_gen.py`**，理由：

| 维度 | (a) 扩展 `fill_chart.py` | (b) 独立文件 ✅ |
|---|---|---|
| 契约来源 | base `templates/charts/`（带轴、刻度、原生 chart 标记） | 仓库 `deltas/layout-assets/v2/`（无轴、极简、IKB 蓝） |
| 视觉语言 | 与 v2 骨架**不同**（base 有网格轴，v2 没有） | 与 v2 骨架**逐像素同构** |
| 混在一起的风险 | 两套视觉常量在同一文件里打架 | 各管一摊，边界清晰 |

**若强行合并**，`fill_chart.py` 需按"风格开关"分叉全部几何常量——复杂度高于收益。

### 3.2 与手写版的几何对比（卡内硬要求）

用**同源数据**（取自 `v2/CONTRACT.md` §2 记录），把两侧 SVG 的关键几何数值**逐项抽出比对**：

| 类型 | 比对项 | 结果 |
|---|---|---|
| `bar-chart` | 4 根柱的 (x, y, w, h) | ✅ **[SAME]** 逐项相同 |
| `comparison-bars` | 3 条的 (x, y, w, h) | ✅ **[SAME]** 逐项相同 |
| `donut-chart` | 每段 `dasharray` + `rotate` 角度 | ✅ **[SAME]**（修复 C-032 后） |
| `line-chart` | 折线点坐标序列 | ⚠️ **[DIFF]** —— 见 C-033（**手写版自身不一致**） |

**总体：3/4 完全一致；第 4 类的差异是手写版的缺陷，不是生成版的偏差。**

### 3.3 C-032 · donut 首段弧长与数据不符（**真实缺陷，已修**）

- **现象**：手写 `v2/donut-chart.svg` 首段 `stroke-dasharray="502"`，
  而 `C = 2π×160 ≈ 1005`，故 **502 = 周长的 50%**。
  但**同一张图的图例写「软件与实施 60 万 / 硬件与培训 20 万」，脚注写「占预算四分之三」**
  —— 60/80 = **75%**，应为 **754**。
- **视觉确认**：渲染后深蓝占**半圈**，与"四分之三"文字**直接矛盾**（已附渲染证据）。
- **根因**：§2 CONTRACT 里也写着 `60 万 / 20 万 → 502/1005 与 251/1005`
  —— **文档与骨架同错**，说明是"照抄了错的中间稿"。
- **修复**：
  - 首段 `502 → 754`
  - 第二段起始角 `rotate(90) → rotate(180)`（首段结束处 = -90 + 270 = 180）
  - 第二段 `dasharray` 第二值 `1256 → 1005`（原值会导致重复绘制）
  - 同步修正 `v2/CONTRACT.md` §2.3 的旧数据值与 §2.6 记录
- **修复后**：donut 几何与生成版 **[SAME]**，checker 零 blocking，渲染为 75%/25%。

### 3.4 C-033 · line-chart 折线点数与标签数不符（**记录，未改**）

- **现象**：手写版折线有 **6 个点**（x=240/400/560/720/880/1040），
  但只标了 **3 个**类目与 3 个数值（x=240/560/1040）。
- **与文档矛盾**：§2.2 公式 `点x = 160 + i/(n-1)×960`，n=3 时为 **160/640/1120**——
  与手写的 240/560/1040 **也不一致**。
- **判定**：手写版是"**6 点趋势曲线 + 3 个标注点**"手工摆的，公式、实现、标注三者互不相同。
- **未改的理由**：改动会改变已发布的 T-03 视觉；且该骨架目前无回归用例覆盖。
  **仅记录，并建议后续如重做以生成版为准**（生成版 n 点对 n 标签，语义自洽）。

### 3.5 §2.6 更新

已把 `v2/CONTRACT.md` §2.6 从"手工坐标 + 自动化 backlog"改为
**"✅ 已自动化"**，含工具入口、双向核对结果表、C-032/C-033 记录、
以及新增的易错点「**弧长与数据不符**」。引导句同步改为"已由工具接管"。

---

## 4. 场景分工：骨架表格类页型 vs base 表格模板

| 场景 | 用哪个 | 理由 |
|---|---|---|
| 3–5 行、行内含**一句话结论**（方案对比、风险→对策） | **v1 骨架** `comparison-rows` / `risk-rows` | 已按"名称 + 结论"排版，填槽即用；无表头/网格线，视觉更轻 |
| 需要**表头 + 网格线 + 多列数值** | **base 表格模板 + `fill_table.py`** | 骨架无表头/网格概念；表格模板天然表达"行列表头共同定位一格" |
| 需要**原生 PowerPoint 表格**（可增删行列） | **base 模板 + `--native-charts-and-tables`** | 需 marker + metadata；**骨架没有该标记** |
| 分组/缩进 + 小计/合计 | base `hierarchical_table` | 骨架无层级行概念 |
| 能力有无（√/×/部分） | base `feature_matrix` | 需要状态语义 |
| 单一序数标度评分 | base `rating_matrix` | 需要统一标度 |

**决策口诀**：*能填槽位就用骨架（快、配色统一）；要表头网格就用 base 表格（准、结构明确）；
要能在 PPT 里改行列就用 base 原生表格（真表格）。*

> ⚠️ **原生表格路径的坑**：**只对 2/6 模板生效**。若数据形态不是 `record_table` /
> `hierarchical_table` 那两类，**用 `fill_table.py` 生成**（它为任意形态产出合规 marker + metadata）。

---

## 5. 验收对照

| 验收项 | 要求 | 实测 | 结论 |
|---|---|---|---|
| tables 契约摘要 | 选型/数据模型/接入方式 | §2（含"是否同 charts 模式"的判定） | ✅ |
| ≥2 模板填充实测 | 读回数据齐全 | 2 页生成，**读回 2/2 原生 Table**，行列与单元格抽样齐全 | ✅ |
| 三步法文档 | — | `deltas/table-fill/README.md`（三步法 + 选型摘录） | ✅ |
| 场景分工 | — | README §5 + 本报告 §4 | ✅ |
| 4 类重算器可用 | 输入 JSON / 输出合规 SVG | 4/4 生成成功，checker 零 blocking | ✅ |
| 与手写版渲染一致 | 附对比图路径 | **3/4 [SAME]**；1 类差异为手写版缺陷（C-033） | ✅ |
| §2.6 更新 | — | 已标注"已自动化" + 工具入口 + 两个 C 编号 | ✅ |
| 四道质检全过 | — | checker `blocking:0 / introduced:0`；hygiene 0；overlap 0；D-2 `0 P0 / 0 P1 / 74 OK` | ✅ |
| vendor 零 diff | 必须 | `git status` 无 `vendor-ppt-master/**` | ✅ |

---

## 6. 失败模式（C-XXX）

### C-032 · donut 首段弧长与自身数据/脚注矛盾（**真实缺陷，已修**）
见 §3.3。**这是本项目第一次由"自动化工具对比"发现的手写骨架缺陷**
（此前 C-011/C-015/C-019 均靠人眼看图）。

### C-033 · line-chart 折线点数 ≠ 标签数 ≠ 文档公式（**记录，未改**）
见 §3.4。

### C-034 · Windows 侧脚本输出 emoji 触发 GBK 编码错误（**已修**）

- **现象**：`compare_v2.py` 在 Windows 控制台报
  `UnicodeEncodeError: 'gbk' codec can't encode character '\u2705'`。
- **根因**：脚本用了 `✅`/`❌`/`⚠️` 做判定标记，Windows 控制台默认 **GBK** 无法编码。
- **修复**：判定标记改为纯 ASCII `[SAME]` / `[DIFF]`，并在文件头注明原因。
- **教训**：**跨侧脚本的输出文本也受编码约束**——不只是输入路径（W-1/W-2 的延伸）。
  建议所有在 Windows 侧运行的脚本**避免非 ASCII 符号**（中文可用，emoji 不可）。

### C-035 · 宿主 TSD 加密会波及"写回 WSL 的文件"（**环境限制，已绕行**）

- **现象**：从 `/mnt/d` 复制的 `.py` 文件在 WSL 侧读出 `%TSD-Header-###%` 密文；
  甚至把明文**写入** WSL 路径后，WSL 侧读回仍是密文（而 Windows 侧始终是明文）。
- **影响**：**同一文件在两侧的"可读性"不对称**——Windows 读得到、WSL 读不到。
- **绕行**：所有涉及 repo 文件的读写与执行**一律在 Windows 侧完成**（本次即如此）。
- **教训**：这解释并强化了既有 W-3/W-8；**新增一条**：此加密不仅影响"渲染产物 PNG"，
  **也影响 repo 内的文本文件在 WSL 侧的读取**（此前只有 `charts_index.json` 被注意到）。

---

## 7. 未验证项（诚实披露）

| 项 | 说明 |
|---|---|
| `feature_matrix` / `rating_matrix` | 未实测（无对应数据关系）；其特殊单元格语义（状态标记、序数圆点）**本工具未实现** |
| 原生表格的**视觉保真度** | 只验证了行列数与单元格文本；**样式是否被 PowerPoint 归一化未做像素级对比** |
| 表格内容正确性 | 四道质检不解析表格语义；内容是否恰当依赖人工目视 |
| C-033 的影响面 | 未排查是否有**已交付 deck** 使用了该 line-chart 骨架 |
| v2 生成版的 `nice_max` | 默认 `auto_max=False`（按数据最大值定高，与手写版一致）；`auto_max=True` 分支未用于对比 |
| 投影环境 | 未在偏色投影下验证 |
| L3 人工评审 | ⚠️ **待指挥官读图**（contact sheet 路径见 §1） |

---

## 8. 《建议》

1. **把"几何回归比对"固化为常规步骤**（C-032 的直接价值）。本次靠 `compare_v2.py`
   发现了手写骨架的弧长错误——**这是继"人眼看图"之后的第二类发现手段**。
   建议：任何"生成器 ↔ 手写资产"并存的场景都加一次逐项比对。
2. **回填 `feature_matrix` / `rating_matrix` 的原生标记**。这两个模板缺 marker+metadata，
   导致它们在 PPT 里不可编辑。建议按 `record_table` 的 schema 补齐（属 vendor 改动，
   需另开卡；本仓库可按"只读 vendor"原则，用 `fill_table.py` 侧绕开）。
3. **修复 C-033 或明确弃用**。当前 `line-chart` 骨架的"6 点曲线 + 3 标签"是不自洽的；
   建议要么按 §2.2 公式重画（3 点 3 标签），要么在骨架注释里写明"这是趋势示意，非数据点"。
4. **所有跨侧脚本避免 emoji**（C-034）。判定标记用 `[OK]`/`[FAIL]`/`[WARN]` 即可。
5. **文档与骨架需交叉验证**。C-032 的根因是"文档抄了错的中间稿"——
   `v2/CONTRACT.md` §2.3 与骨架同错。建议在文档里给关键数值标注"来源与校验方式"。
6. **`table-fill` 补两个矩阵族**。若后续有"能力对照/评分矩阵"需求，
   建议按 `feature_matrix` / `rating_matrix` 的契约补实现（含状态标记与序数圆点）。

---

## 9. 附录 · 新增文件清单

| 文件 | 说明 |
|---|---|
| `deltas/table-fill/fill_table.py` | 表格填充器（任意列数/行数 → 合规 SVG + 原生 marker/metadata） |
| `deltas/table-fill/README.md` | 三步法 + 选型摘录 + **场景分工** + 原生路径的坑 |
| `deltas/table-fill/verify_table.py` | 读回验证（**递归**枚举 Table shape / 行列 / 单元格抽样） |
| `deltas/chart-fill/v2_chart_gen.py` | **v2 四类图表数据→几何重算器** |
| `deltas/chart-fill/compare_v2.py` | 生成版 vs 手写版**几何逐项比对**工具 |
| `deltas/layout-assets/v2/donut-chart.svg` | **C-032 修复**（弧长 502→754，角度与 dasharray 修正） |
| `deltas/layout-assets/v2/CONTRACT.md` | §2.6 标注"已自动化" + C-032/C-033 记录 + §2.3 数据值修正 |
