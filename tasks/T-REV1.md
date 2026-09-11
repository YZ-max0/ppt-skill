# 任务卡 T-REV1 · 交付修订（P2 · 预计 30 分钟）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-D6/T-D2 已验收

## 修订项（仅三项，不做其他）

### R1 · index.md 登记 Director（授权修改 vendor 第二文件）

编辑 `vendor-ppt-master/workflows/index.md` §2 Supporting Documents 表，新增一行：

| `director` | Input stage | (见下) | Generate PPTX Pre-spec (optional Step 0) |

- **Class** 列写 `Input stage`（对齐既有 `apply-template-workspace` 的 `Template-input stage` 类）
- **Path 列**：该行路径指向 `../../deltas/director.md`（vendored 包外，同 routing.md §8 的引用方式）
- 只加这一行；§1、§3 其他内容不动
- 然后检查 `scripts/prompt_audit_manifest.json`：若其 load sets 需要登记 director/routing §8 才能保持审计一致 → 一并最小更新；若改动面大或结构不明 → **不改**，把理由写进交付摘要（指挥官将记录豁免）

### R2 · detect_overflow.py 参数化

`TOLERANCE = 1.2` 提为 CLI 参数 `--tolerance`（type=float，default=1.2），文档串同步一句。不改判档逻辑本身。

### R3 · check_title_consistency.py 注释同步

第 183-187 行注释仍写"only flag pages where one title deviates while another on the same page keeps the common size"（旧设计）。实现已改为不需 keeper。把注释改为与实现一致（跨页偏离 tier 常规即报，无 keeper 前置）。

## 硬约束

1. 允许修改：`vendor-ppt-master/workflows/index.md`（仅 §2 加一行）；`deltas/pptx-fill-check/detect_overflow.py`、`check_title_consistency.py`（仅上述改动）。其他一切文件禁止触碰
2. 不改任何判档逻辑/阈值默认值；不重命名函数
3. 改完自跑三个样张（临时目录已有）+ `--tolerance 1.0` 冒烟验证参数生效
4. 顺带在交付摘要里报告：`prompt_audit_manifest.json` 的决定与理由

## 交付要求

① 三处改动的 diff 摘要 ② 样张回归输出（原样 + --tolerance 冒烟）③ manifest 决定与理由 ④ 《建议》附录（可选）
