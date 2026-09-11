# 任务卡 T-FIX2 · 修复 `check_title_consistency` 对 free-design 的系统性误报（P1 · 预计 1-2 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：E2E 首跑已交付

## 背景（指挥官读码级复核确认）

E2E 首跑暴露 C-002：free-design（quick）产物上 14 项 P1 **全为误报**（例：封面 48pt 与正文 18pt 被判"同级"）。
根因：`_tier()` 对非占位符文本回退 `shape:text`，令封面标题/页标题/卡片标题/正文落入同一 tier；
`_looks_like_title`（len≤16 且 size≥18）把 48pt 与 18pt 都选入该 tier。
定性：D-2 检测器第二个判据缺陷（第一个 = T-FIX1 的 wrap 假 P0）。

## 修复框架（指挥官指定）

**双路径**（不互斥，按 shape 分流）：

1. **占位符路径**：保持现有判据不变（template-fill 场景已证明有效）
2. **非占位符路径**：**全局字号聚类分档**——
   - 收集 deck 内全部标题候选的 `size_pt`，按间距阈值聚类（默认 4pt，CLI 参数 `--size-bucket-gap`，类型 float 可调）
   - tier key 改为 `text@{bucket}`（例如 `text@48-51` / `text@27-30` / `text@18-21`）
   - 同一档位内执行原有的「同页 spread」与「跨页偏离」检测
   - 目的：消除跨档假报（48 vs 18/21），保留同档漂移检测（如 28→24）

**README 必须写明已知局限**：无角色信息时，**跨档漂移（如 28→18）不可检**——这是分档法的本质边界，不掩饰。

## 允许修改

`deltas/pptx-fill-check/check_title_consistency.py`、`README.md`、`docs/windows-notes.md`（新增 W-5 节）。其余零触碰。

## 验收标准

- [ ] **靶场对比**：e2e 产物重跑，14 P1 → ？（附前后命令与摘要；期望 0）
- [ ] **真阳性保留**：构造 free-design 样张——7 页页面标题全 28pt，其中 1 页改 24pt → 正确报 P1（附输出）
- [ ] **回归**：原占位符样张（sample_* / smoke 产物）结果不变
- [ ] **人工核对**：修复后若仍有报告项，逐项说明真伪
- [ ] **W-5 速查**（顺带，执行者建议 2 采纳）：`docs/windows-notes.md` 新增——
      ① 根级 `<g>` 必带 `data-pptx-bounds`；② 整页背景独立成组；③ 多行文本单 `<text>`+多 `<tspan>`；
      ④ bounds 直接取 checker 输出的 `content (...)` 坐标；⑤ 观察：多行 tspan 导出后读回无换行符（PowerShell/下游解析注意）
- [ ] 只改 3 文件；vendor 零 diff；样张仅临时目录

## 异议区

如你认为"字号聚类分档"不如替代设计（例如"页面主标题专用跨页通道"），给出设计与数据对比再定。
