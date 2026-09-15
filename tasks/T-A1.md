# 任务卡 T-A1 · 工程收尾批：tables 接入 + v2 图表坐标自动化（P1 · 预计 3-5 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-IMG1 已关闭
> 完成后：能力面 100%（文字/图表/图片/表格四要素）+ 图表坐标风险关闭。

## Part A · tables 族接入（复用 chart-fill 同款三步法）

1. 读 `vendor-ppt-master/templates/tables/` 的 `README.md` + `table-vocabulary.md` + `tables_index.json`
   → **表格契约摘要**（选型规则 / 数据模型 / 接入方式——先判断它们是否同 charts 一样"渲染好的示例 + 契约"）
2. 选 **2-3 个**模板实测接入（建议 `metric_table` + `comparison_matrix`（T-SMOKE 已熟悉）+ 1 个新类型如
   `hierarchical_table`；选型按 `tables_index.json` 规则并记录理由）
3. 产物：`deltas/table-fill/`（`fill_table.py` + `README.md`：三步法适配 + 选型摘录 +
   **场景分工**（现有骨架的表格类页型 vs base 表格模板））
4. 验证：填充真实数据 → checker 零 blocking → 导出 → **读回表格结构**
   （python-pptx：表格 shape 计数 / 行列数 / 单元格文本抽查）

## Part B · v2 图表坐标自动化（关闭 `v2/CONTRACT.md` §2.6 风险）

目标：v2 骨架覆盖的 4 类（`bar-chart` / `line-chart` / `donut-chart` / `comparison-bars`）支持
"数据 → 几何"重算，**数据变化不再需要手工算坐标**。

方案（执行者定，二选一或组合）：
- a) 扩展 `fill_chart.py` 支持 "v2 风格" 输出（复用 v2 骨架视觉语言 + 既有 `nice_max` 公式）
- b) 独立 `v2_chart_gen.py`

硬要求：
- 输入 JSON（对齐既有 spec 格式）；输出**合规 SVG**（过 checker 零 blocking）
- **视觉与 v2 手写骨架一致**：同数据下渲染对比（新生成 vs 手写版），差异在可接受范围
- 更新 `v2/CONTRACT.md` §2.6：标注"已自动化"及工具入口

## 验收标准

- [ ] tables 契约摘要 + ≥2 模板填充实测（读回数据齐全）+ 三步法文档 + 场景分工
- [ ] 4 类图表重算器可用；同数据渲染对比与手写版一致（附对比图路径）
- [ ] §2.6 更新
- [ ] 全部产物四道质检全过；vendor 零 diff
- [ ] 交付 `docs/a1-report.md`；提交：`feat(tools): table-fill + v2 chart automation (T-A1)`

## 异议区

如 tables 契约与 chars 模式差异大（如需原生 `--native-charts-and-tables` 类似开关），按官方文档执行并记录；
如 v2 坐标自动化更适合"改造骨架为数据驱动模板"而非工具生成，给出对比方案再定。
