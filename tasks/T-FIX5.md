# 任务卡 T-FIX5 · 跨组重叠检查器 check_overlap.py（P1 · 预计 1-2 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-FIX4/T-E2E4 已交付

## 背景（第三类"测不出"问题）

C-011（内容泄漏）与 C-015（图例压字）同根：**单组几何合法、跨组整体冲突**——checker/D-2/卫生检查都拦不住。
目前只能靠人眼看 contact sheet。本卡把这一类做成可自动化的第三道闸。

## 范围

### R1 · `check_overlap.py`（落点 `deltas/layout-assets/`）

输入 SVG 目录（填充后、导出前），检测：
1. **文本 × 文本重叠**（跨组）：两文本 bbox 相交 → 报
2. **文本 × 图形重叠**（跨组）：文本 bbox 与图形 element bbox 相交，且**不同组** → 报
   （同组内文本-图形重叠合法：深色格反白字、色块上的标签等）
3. **图例/轴标签类重叠**（C-015 的类）：跨组相交已可覆盖

**bbox 来源**：`data-pptx-bounds`（组）+ 元素坐标 + 文本 vw 估算（复用 `pptx-fill-check/capacity.py` 的 `vw_of` 口径）。

### R2 · 白名单与阈值

- 重叠面积比例阈值（CLI 可调，默认如相交 >5% 报 P1）
- 显式豁免机制（元素 `data-ok-overlap="true"` 或词表）
- 输出：`[P1] 页N A元素 × B元素 重叠 X%` + 退出码（0/2）

### R3 · 双向验证（按本项目标准）

- **正样本**：T-02/T-04 产物跑一遍 → 必须通过（误报 = 0；若历史产物存在真实重叠，如实列出并人工确认真伪）
- **负样本**：C-015 的历史样本（图例压字版本，若已修复则用构造样本）→ 必须被拦

### R4 · 流程接入

- USAGE 质检流程增补一行（③ 导演式必跑；①② 推荐）
- HYGIENE.md 或独立 README 说明用法

### 顺带（C-017 收尾）

`deltas/chart-fill/README.md` 增一行：column 渲染器的多序列能力**不等同** base `grouped_bar_chart` 模板，
选型时多序列并排场景按契约优先 `grouped_bar`（命名偏差说明，防后人混淆）。

## 验收标准

- [ ] check_overlap.py + 用法文档；正样本 0 误报（或真重叠逐项说明）；负样本被拦
- [ ] USAGE 增补；chart-fill README 一行补充
- [ ] vendor 零 diff；提交 `feat(tools): cross-group overlap checker (T-FIX5)`
