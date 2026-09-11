# 任务卡 T-FIX1 · 修复 D-2 `wrap=False` 系统性假 P0（P0 优先级）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-SMOKE 已交付

## 背景（指挥官代码级复核确认）

冒烟 S3 暴露（`docs/smoke-report.md` P-2）：真实 vendor 产物上 `detect_overflow.py` 报 32 个 P0，**全为误报**。
根因链（指挥官已亲自读码确认）：
- `capacity.py:193`：`max_lines = 1 if not wrap else ...`
- `detect_overflow.py:82`：`demand = sum(ceil(vw / cpl))`（折行估算）→ `usage = demand / max_lines`
- 组合结果：wrap=False 的长文本（表头/标签/KPI）恒得 `usage ≥ 2.0` → 假 P0，**阻断语义失效**。
定性：D-2 实现缺陷，非 vendor 问题。

## 修复框架（指挥官指定，细节自定）

**首选方案**：wrap=False 改用**水平判据**——取最长段（多段取最大）的 `vw / cpl` 作为 ratio：
`≤1.0 → OK`；`1.0–1.2 → P1`；`>1.2 → P0`（语义标注为"水平超宽"）。
理论依据：wrap=False 文本不折行，其溢出必然是水平方向，行数判据不适用。

**备选方案**（仅在首选实测不可靠时可用，且必须附数据）：wrap=False 整项最高 P1、不参与 P0 阻断。
选此路必须给出 ≥5 个真实样本的 cpl 估计误差分析，并在 README 记录理由。

**参考**：Gorden `compute_capacity.py` 对 wrap 参数的处理（只读对照，不抄）。

## 允许修改

`deltas/pptx-fill-check/` 下 `capacity.py`、`detect_overflow.py`、`README.md`；次要交付 `docs/windows-notes.md`。
其余一切零触碰（vendor 零修改）。

## 验收标准

- [ ] **靶场对比**：修复后对 smoke 产物重跑，输出 32 P0 → ?（附前后对比命令与摘要）
- [ ] **人工抽验**：从"仍报 P0/P1"的项中抽 3-5 项，逐一说明是否真超宽（水平判据的语义正确性）
- [ ] **回归**：原 3 个自建样张结果不变
- [ ] **新增样张**：wrap=False 正常表头 → OK；wrap=False 真超宽 → P0（或按备选 P1）
- [ ] **README 更新**：判据说明（含 wrap 语义）+ 补 `--tolerance` 参数说明（backlog 项）
- [ ] **次要交付** `docs/windows-notes.md`：收录 P-1 四步导出序列 / P-3 控制台编码 / P-4 WSL 路径 / P-5 lock 必填值（各 3-5 行）
- [ ] 未改 vendor；样张仅在临时目录

## 异议区

如你认为首选方案会在某类真实产物上仍失准（例如 cpl 的 inset 假设误差），给出反例数据与替代设计。
