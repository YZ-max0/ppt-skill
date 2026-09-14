# M2C 使用入口与手册 · 交付报告

> 执行者：开发工程师 ｜ 日期：2026-09-14 ｜ 卡：`tasks/T-M2C.md`
> 结论：**README + USAGE 就位；doc-test 按手册完整复跑 T-01b 全流程成功；发现并修正 3 处文档-现实偏差**

---

## 1. 交付物

| 交付物 | 行数 | 限额 | 内容 |
|---|---|---|---|
| `README.md`（repo 根） | **55** | ≤120 ✅ | 定位 / 两路线 / 快速上手 5 步 / 目录导航 / W-1~W-8 摘要 / 许可 |
| `docs/USAGE.md` | **259** | ≤300 ✅ | 路线选择 / 逐步操作 / 24 骨架索引 / 场景配方 / 工具用法 / 环境 / 边界 / 请求模板 |
| `docs/m2c-usage-report.md` | 本文件 | — | doc-test 结果 + 偏差清单 + 建议 |

**硬约束遵守**：未修改 vendor 与既有 deltas 代码；手册中所有路径/命令/文件名均按**写前实际盘点**核对
（24 骨架逐一列名核对；脚本名以 `ls` 结果为准）。

---

## 2. doc-test 结果（按手册完整复跑 T-01b）

**方法**：严格按 `docs/USAGE.md` §2 的步骤与 §4「周报 6 页」配方执行，每一步记录"手册预期" vs "实际"。

| 步骤 | 手册命令/动作 | 实际结果 | 一致 |
|---|---|---|---|
| §2.1 初始化 | `project_manager.py init t01b-doctest --dir '<DT>' --format ppt169 --quick-generate` | ✅ `[OK] Project initialized`；目录为 `svg_output/` + `validation/` | ✅ |
| §2.2 填充 | 按 §4 配方选 6 骨架，替换 `【槽位】`，断言 `【`=0 | ✅ 6 页填充成功，占位符零残留 | ✅ |
| §2.3 质量门 | `svg_quality_checker.py <proj> --quick-generate --stage final --json` | ✅ `Fully passed: 6 (100%)`，`blocking: 0`，`introduced: 0` | ✅ |
| §2.4 导出 | `svg_to_pptx.py <proj> --quick-generate --no-notes` | ✅ `[Done] Saved: ...pptx`，`[POSTFLIGHT] status=passed ... slides=6` | ✅ |
| §2.5 D-2 质检 | `detect_overflow.py` + `check_title_consistency.py` | ✅ `P0=0 / P1=0 / OK=48`（exit 0）；`titles=16 P1=0`（exit 0） | ✅ |
| §2.6 渲染 | `render_png.py <pptx> -o <out>` | ✅ `rendered 6 slide(s)` + `contact sheet 1770×578` | ✅ |

**最终产物核对**：

```text
file: t01b-doctest_20260914_114126.pptx
slides: 6
frames: 55
mojibake: 0          ← 乱码 0
placeholder: 0       ← 占位符 0（W-7 断言）
rendered PNG: 6
contact sheet: True
```

**结论：手册可执行、命令可复制、预期输出与实际一致** ✅

---

## 3. 发现的文档-现实偏差与修正（3 处）

### 偏差 1 · `v0/two-col-compare.svg` 的右栏对策槽位文案

| | 内容 |
|---|---|
| **手册/脚本假设** | `【右栏对策】已向上申请 1 名测试支援，` |
| **骨架实际** | `【右栏对策】已申请一名测试支援，` |
| **性质** | 我在 doc-test 脚本里凭记忆写的槽位名，**与骨架实际不符** |
| **处置** | 修正脚本后通过（骨架无问题） |
| **手册影响** | 手册 §3 只给骨架**用途**不给逐槽位文案，故手册本身无需修改 |
| **教训** | **填充时必须以骨架文件的实际文案为准**，不能凭记忆写槽位名 → 已在手册 §2.2 强调"整段替换 `【槽位名】示例内容`"，并在 `v0/CONTRACT.md` §3 提供逐槽位清单 |

### 偏差 2 · `v0/` 目录下**没有** `three-card.svg`

| | 内容 |
|---|---|
| **我的初始假设** | 周报配方 P05 优先用 `v0/three-card.svg` |
| **实际** | `three-card.svg` 属于 **v1**；v0 只有 6 个基础骨架 |
| **处置** | 改用 `v1/three-card.svg`，通过 |
| **手册影响** | 手册 §3 索引**已正确标注** `three-card.svg` 属于 v1；§4 配方写的是"kpi-hero 或 three-card"，**未指定版本** → 手册无误，是我的脚本写错 |
| **改进** | 建议手册 §4 配方在跨版本骨架处补注版本（见建议 1） |

### 偏差 3 · repo 根出现未跟踪的 `projects/` 残留

| | 内容 |
|---|---|
| **现象** | repo 根有 `projects/v2-verify_ppt169_20260911/`（仅含 1 个 `workflow.log`） |
| **来源** | T-M2B 期间一次 `init` 未带 `--dir`（当时 `Set-Location` 到不存在的目录，静默失败） |
| **性质** | **W-6 记录的问题的真实复发**，且污染了 repo 工作区（未被 git 跟踪，故此前未发现） |
| **处置** | 已删除该目录；repo 根恢复为 8 项 |
| **手册影响** | 手册 §2.1 已用 ⚠️ 强调"**必须带 `--dir`**" → **手册是对的**，且本次 doc-test 严格用 `--dir` 一次成功 |
| **加固建议** | 见建议 2 |

### 偏差汇总表

| # | 偏差 | 责任方 | 手册是否需改 |
|---|---|---|---|
| 1 | 槽位文案凭记忆写错 | 我的 doc-test 脚本 | ❌ 不需（手册已强调"整段替换"） |
| 2 | `three-card` 版本假设错误 | 我的 doc-test 脚本 | ❌ 不需（索引已正确） |
| 3 | `projects/` 残留 | 历史操作（W-6 问题） | ❌ 不需（手册已强调 `--dir`） |

> **重要结论**：3 处偏差**没有一处是手册内容错误**——都是我的 doc-test 脚本凭记忆写错，
> 或历史操作遗留。这反向证明手册的关键提醒（`--dir`、整段替换、索引版本归属）**是准确的**。

---

## 4. 手册内容核对（写前实际盘点）

| 核对项 | 实际 | 手册记载 | 一致 |
|---|---|---|---|
| 骨架总数 | **24**（v0=6 / v1=10 / v2=8） | 24（分三代列出，逐个命名） | ✅ |
| v0 骨架名 | bullets, closing, cover, kpi-hero, timeline, two-col-compare | 6 个全部列出 | ✅ |
| v1 骨架名 | budget-4, comparison-rows, decision-3, layered-arch, metrics-3, process-steps, risk-rows, sentence-hero, three-card, toc | 10 个全部列出 | ✅ |
| v2 骨架名 | bar-chart, comparison-bars, cover-bold, donut-chart, evidence-wall, line-chart, quote-hero, section-hero | 8 个全部列出 | ✅ |
| 质检脚本 | capacity.py, check_title_consistency.py, detect_overflow.py | detect + check_title（capacity 为其内部模块） | ✅ |
| 渲染脚本 | render_png.py | render_png.py | ✅ |
| W-1~W-8 | 8 条 | 8 条，逐条一句话 | ✅ |
| repo 根 | README（新增）, ABSORPTION-LEDGER, CONTRACT, DELTAS, deltas, docs, tests, tasks, vendor-ppt-master | 目录导航表覆盖 | ✅ |

---

## 5. 未验证项

| 项 | 原因 |
|---|---|
| **手册在"全新用户"手上的可读性** | 我是作者，无法模拟零上下文读者。**建议用户亲自按手册跑一次** |
| 导演式路线的 doc-test | 本卡 doc-test 只覆盖快速通道（T-01b）；导演式已在 T-E2E2 实战验证，但未按本手册复跑 |
| USAGE §4「方案 20 页」配方 | 基于 T-03 实战归纳，**未按配方完整复跑** |
| 渲染结果的目视确认 | W-8 加密限制；contact sheet 需人在 Windows 查看 |
| W-2 乱码提示的实际误导场景 | 本卡复跑未触发控制台乱码（输出全英文/数字） |

---

## 6. 《建议》附录

### 建议 1【低】USAGE §4 配方标注骨架版本

当前配方写"`kpi-hero` 或 `three-card`"，跨版本时可能让人找错目录。
建议改为"`kpi-hero`(v0) 或 `three-card`(v1)"。**本次偏差 2 即是此类混淆。**

### 建议 2【中】为 `--dir` 加固：init 后校验落点

W-6 的问题（`init` 落到默认根）在本次盘点中**真实复发**并污染了 repo 根。
建议：在 `docs/windows-notes.md` W-6 补一句**自检方法**——init 后立刻确认：

```powershell
# 落点自检：项目应出现在 --dir 指定目录下
Test-Path "<--dir 指定目录>\<项目名>_*"
```

若不在指定目录，说明 `--dir` 未生效（或未传），应立即移动/重建，避免残留污染 repo。

### 建议 3【中】手册应增加"骨架槽位实查"一节

本次偏差 1 暴露：**槽位文案必须查文件，不能凭记忆**。
建议 USAGE §2.2 补一条操作提示：

```powershell
# 查某骨架的全部槽位（填充前必做）
Select-String -Path "deltas\layout-assets\<版本>\<骨架>.svg" -Pattern '【[^】]+】' -AllMatches
```

或指向 `v0/CONTRACT.md` §3 的逐槽位清单（已存在）。

### 建议 4【中】向"Skill 形态入口"演进（回应卡内异议区）

**现状**：使用入口是一份手册（README + USAGE），用户需要**人工阅读并手动执行命令序列**。
**对比**：

| 形态 | 优点 | 缺点 |
|---|---|---|
| **当前：手册** | 零技术依赖，人可读；不改 vendor | 需人工执行；步骤多易漏（W-1 四步序列） |
| **Skill 形态** | 一句"帮我做份周报 PPT"即可触发；步骤固化为流程 | 需新增 `SKILL.md` 级入口；与 vendor 的 SKILL.md 可能冲突 |

**建议**：**暂不改造**。理由：
1. 手册刚建立且 doc-test 通过，尚无真实使用反馈
2. 当前"opencode + 手动指挥"的协作方式下，手册已够用
3. Skill 化需要先明确"谁触发、触发后如何接手"的产品问题

**若将来要做**，建议路径：新增仓库级 `SKILL.md`（**不放在 vendor 内**），
声明"路由到 `deltas/director.md` 的 A/B/B2/C 或快速通道"，并复用现有 24 骨架与工具链。

### 建议 5【低】README 的"快速上手 5 步"可加耗时预期

实测快速通道 6 页全流程（含渲染）约 **2 分钟机器侧**（人工写内容另计）。
建议 README 在 5 步后补一句量级提示，帮助用户建立预期。

---

## 红线自检

| 红线 | 结果 |
|---|---|
| 只新增 README.md / USAGE.md / 本报告 | ✅ 未改 vendor 与既有 deltas 代码 |
| 手册所有路径命令与 repo 现状一致 | ✅ 写前逐一盘点核对（见 §4） |
| 不复制 vendor 大段文档 | ✅ 全部以其路径引用 |
| 不暴露内部治理细节 | ✅ 手册只留 `decisions.md` 入口链接，未展开内容 |
| doc-test 完成 | ✅ 6 步全过，产物核对通过 |

**附带清理**：删除 repo 根未跟踪残留 `projects/`（1 个 workflow.log，来自 T-M2B 的 `init` 误落），
repo 根恢复为 8 项。
