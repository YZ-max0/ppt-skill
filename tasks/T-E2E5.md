# 任务卡 T-E2E5 · T-05 BP 路演（导演式精品）（P1 · 预计 4-6 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-FIX5 已关闭

## 目标

T-05 = **视觉冲击 + 财务数据**的最强靶场：投资人路演，15-18 页，财务模型 12 个数字。
这是"效果更好"（用户核心目标）的终极场景——③ 导演式 + v2 锚点 + chart-fill 图表全上。

## 输入

| 材料 | 路径 |
|---|---|
| T-05 原文 | `tests/test-sets/v1/inputs.md`（T-05 节） |
| 导演式规范 | `deltas/director.md`（完整四阶段；B2 硬门禁） |
| 图表接入 | `deltas/chart-fill/README.md`（三步法；本次预计扩展财务类图表） |
| 质检三件套 | checker + D-2 + `check_hygiene` + `check_overlap`（新） |
| 视觉标准 | `visual-review-01/02/03.md`（锚点节奏）、`v2/CONTRACT.md`（深色预算 ≤15%、字号差 ≥6pt） |

## 执行

1. **A/B/B2 完整导演流程**（B2 未过不得进 C）；Director 稿全文入报告
2. **页面配方**（BP 惯例，按导演稿实际调整）：
   痛点 → 方案 → 市场（数据来源页）→ 产品 → 商业模式 → 竞争 → 团队 → 财务（图表）→ 融资需求 → 远景
   目标 15-18 页；**单页密度上限**（BP 观众 5 人近距离看，一页一核心）
3. **图表**：财务模型 12 数字 → 按图表契约选型（候选：`column`/`line`/`waterfall`——**逐个对照
   `charts_index.json` 规则**，如无 running total 则不用 waterfall）；市场数据用 `area` 或 `bar`；
   预计需扩展 `fill_chart.py` 1-2 类
4. **视觉锚点**：cover-bold 封面 + ≥2 处锚点（quote-hero/evidence-wall/深色决策页）；深色预算合规
5. **质检**：checker + D-2 + hygiene + overlap 全过
6. **交付** `docs/e2e-05-report.md`：命令表 / 导演稿全文 / 图表选型理由表 / 验收对照 /
   C-XXX / 耗时 / 未验证项 / 《建议》

## 验收标准

- [ ] 15-18 页全链路；四道质检全过（checker/D-2/hygiene/overlap）
- [ ] 财务/市场 ≥3 页图表（选型按契约记录理由）
- [ ] 视觉锚点 ≥3 处（含封面）；深色页 ≤15%
- [ ] 报告完整；vendor 零 diff
- [ ] 提交：`feat(e2e): T-05 investor BP + finance charts (T-E2E5)`

## 异议区

BP 的单页密度与"一页一核心"可能冲突（12 个财务数字要分散在几页）——按导演稿的"面积预算"字段裁决
并按实记录；如遇 `charts_index` 无匹配模板的财务关系（如 unit economics），如实报告并给替代方案。
