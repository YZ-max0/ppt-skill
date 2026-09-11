# 任务卡 T-FIX2B · FIX2 收尾小修（P2 · 预计 30 分钟）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-FIX2 已交付

## 背景（指挥官复核发现）

FIX2 交付后指挥官读码发现一处**未受保护路径**：
`check_title_consistency.py` 的**同页 spread 检测**（`detect()` 第一段）对 free-design bucket tier
没有应用主导门槛——同页出现 28pt + 24pt 两个标题候选（不同角色）落入同一 bucket `text@24-28` 时，
spread=4pt > 0.5pt → **假报 P1**。e2e 靶场恰好没有"同页双候选"场景，故未暴露。

## 两处修改

### R1 · 同页 spread 的 bucket 门槛（与跨页同语义）

对 bucket tier 的同页 group：
- 组内主导字号占比 < `DOMINANCE_MIN` → 不报（视为多个不同角色共享一档）
- 占比 ≥ 门槛且存在偏离成员（>DIFF_PT）→ 报偏离成员（保留真阳性场景：同页 28pt×2 + 24pt×1）

占位符路径不变（role 是 ground truth，无门槛）。

### R2 · `--dominance-min` 参数化

`DOMINANCE_MIN = 0.6` 提为 CLI 参数（type=float，默认 0.6），JSON 输出追加 `dominance_min` 字段可追溯。
README 同步参数说明 + 同页边界说明。

## 验收标准

- [ ] **缺陷复现→修复**：构造样张（同页 28pt + 24pt 各 1 个候选）——修复前记录实际输出（预期报 P1），修复后不报（附前后对比）
- [ ] **真阳性**：同页 28pt×2 + 24pt×1 → 正确报出 24 偏离（附输出）
- [ ] **回归**：e2e 产物 0 P1；sample_* 占位符路径结果不变；跨页真阳性样张（6×28 + 1×24）仍报
- [ ] README：同页 bucket 门槛说明 + `--dominance-min` 参数说明
- [ ] 只改 `check_title_consistency.py` + `README.md`；vendor 零 diff

## 完成后提交（与 FIX2 合并）

```
git add deltas/pptx-fill-check/check_title_consistency.py deltas/pptx-fill-check/README.md docs/windows-notes.md
→ fix(d2): dual-path title tiers for free-design (T-FIX2 + FIX2B)
```

## 异议区

如你认为同页 bucket 检测应直接跳过而非加门槛，给出真阳性/假阳性数据对比再定。
