# 任务卡 T-E2E4 · T-04 技术分享 + 演讲者逐字稿（P1 · 预计 3-4 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-FIX4 已关闭（骨架已卫生）

## 目标

T-04 是**图表密集 + 演讲场景**的复合靶场：25 页技术分享，4 张折线图数据 → 验证 chart-fill 扩展能力；
演讲者逐字稿 → 首次落地 D-4 演讲者模式的"逐字稿轨道"。

## 输入

| 材料 | 路径 |
|---|---|
| T-04 原文 | `tests/test-sets/v1/inputs.md`（T-04 节） |
| 图表接入协议 | `deltas/chart-fill/README.md`（三步法 + 场景分工） |
| 演讲者规范 | `deltas/presenter-mode.md`（P-0~P-14；**本次走逐字稿轨道**） |
| 备注链路 | `docs/windows-notes.md` + T-SMOKE S2 记录（`total_md_split.py` → `--with-notes`） |
| 卫生检查 | `deltas/layout-assets/HYGIENE.md`（T-FIX4 产出） |

## 执行

1. **Director 轻量稿**（② 标准档）：受众 3 句 + 逐页标题/要点/页型（25 页）
2. **图表扩展**：按三步法为 T-04 的 4 张折线图数据接入 base 图表（优先 `line_chart` / `dual_axis_line_chart`；
   选型必须按 `charts_index.json` 规则并记录理由）→ 扩展 `fill_chart.py` 支持所需类型
3. **骨架填充**：25 页（含封面），高密度模式（工程师受众，信息密度偏高）
4. **D-4 逐字稿轨道**：
   - 按 `deltas/presenter-mode.md` 写 `notes/total.md`（**每页 150-300 字**、提示信号、口语化、数字读法）
   - 走 `total_md_split.py` → `svg_to_pptx.py --with-notes`
   - 验收：备注逐页写入、无乱码、字数合规（抽查 ≥5 页）
5. **质检**：checker + D-2 + 卫生检查（T-FIX4 的）
6. **交付** `docs/e2e-04-report.md`：命令表 / Director 轻量稿附录 / 图表选型理由表 / 逐字稿抽查样本 /
   验收对照 / C-XXX / 耗时 / 未验证项 / 《建议》

## 验收标准

- [ ] 25 页（±2）全链路，checker 零 blocking、D-2 P0=0、乱码 0、占位符 0、卫生检查通过
- [ ] ≥4 页 base 图表（对应 T-04 数据），选型理由按契约记录
- [ ] 逐字稿：备注全页写入；抽查 5 页字数在 150-300 区间；无 Markdown 标记残留
- [ ] 报告完整；vendor 零 diff
- [ ] 提交：`feat(e2e): T-04 tech talk + speaker script (T-E2E4)`

## 异议区

T-04 时长 40 分钟 × 25 页 = 平均 96 秒/页，若逐字稿按 150-300 字（2-3 分钟）会超时——
如遇此矛盾：以 **P-7 总时长 ≤90%** 为准（40 分钟 × 90% = 36 分钟），
逐字稿向"提示信号"侧收（150 字下限可放宽用于纯过渡页，记录处理方式）。
