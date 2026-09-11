# M0 集成冒烟报告（T-SMOKE）

> 执行者：开发工程师 ｜ 日期：2026-09-11 ｜ 卡：`tasks/T-SMOKE.md`
> 目标：跑通 vendor 确定性代码链路，暴露环境级问题（不评测 AI 生成质量）。

## 0. 环境基线（注记 2）

| 项 | 值 |
|---|---|
| 平台 | Windows（PowerShell 5.1）+ WSL 混合调用；git 只用 Windows git |
| Python | **3.12.3**（`C:\Users\EDY\AppData\Local\Programs\Python\Python312\python.exe`） |
| python-pptx | **1.0.2** |
| lxml | **6.1.1** |
| vendor | ppt-master 5.0.0（MIT） |
| TSD 加密 | Windows 侧 python 透明解密正常（探针 `DECRYPT-OK`） |

## S1 · SVG → PPTX 导出链路

**输入（注记 1：真实资产优先）**：直接使用 vendor 真实 SVG
- `vendor-ppt-master/templates/tables/metric_table.svg` → `svg_output/P01.svg`
- `vendor-ppt-master/templates/tables/comparison_matrix.svg` → `svg_output/P02.svg`

**命令序列（原样）**

```powershell
# 1) 项目初始化
python D:\...\vendor-ppt-master\scripts\project_manager.py init smoke-demo --format ppt169
# [exit=0] Project created: ...\smoke-demo_ppt169_20260911（1280×720）

# 2) 首次导出（失败，暴露前置条件）
python D:\...\vendor-ppt-master\scripts\svg_to_pptx.py <proj> --no-notes
# [exit=0 但输出 Error] spec_lock.md is required for release SVG export

# 3) 生成 lock 脚手架
python D:\...\vendor-ppt-master\scripts\project_manager.py scaffold-lock <proj>
# [exit=0] 生成 spec_lock.md（含 [fill] 占位符）

# 4) 再试（暴露第二前置条件）
python D:\...\vendor-ppt-master\scripts\svg_to_pptx.py <proj> --no-notes
# [exit=0 但输出 Error] default release export requires a passing final SVG
#   quality report; found not-provided

# 5) 质量检查（失败：1 blocking）
python D:\...\vendor-ppt-master\scripts\svg_quality_checker.py <proj> --stage final --json
# blocking: spec_lock typography-size recurrence: undeclared font-size 18
#   (6 occurrences) exceeds the sparse-display limit of 2
# introduced: P01.svg / P02.svg missing root data-pptx-page-role

# 6) 修正 lock（声明 18px role）+ 补 data-pptx-page-role 后复检
python D:\...\svg_quality_checker.py <proj> --stage final --json
# [OK] P01.svg - Passed / [OK] P02.svg - Passed / Fully passed: 2 (100%)

# 7) 导出（成功）
python D:\...\svg_to_pptx.py <proj> --no-notes
# [exit=0] [Done] Saved: exports\smoke-demo_20260911_111556.pptx
#   [POSTFLIGHT] status=passed quality_gate=passed slides=2 warning_categories=0
```

**产物**：`exports/smoke-demo_20260911_111556.pptx`（18135 bytes）、`validation/svg_quality_report.json`、`validation/*.report.json`

**读回验证（python-pptx，递归遍历 GROUP）**

| 项 | 结果 |
|---|---|
| 页数 | **2** ✅ |
| 文本帧（递归） | **67**（page1: 37 / page2: 30）✅ |
| 中文/字符乱码 | **0**（`\ufffd` 计数 0）✅ |
| 文本真实存在 | `slide1.xml` 含 37 个 `<a:t>`，含 "Metric Table" ✅ |

> **观察**：顶层 `slide.shapes` 只有 2 个 GROUP 形状、`has_text_frame=False`；文本嵌套在组内。
> 直接遍历顶层会误判"0 文本帧"。**读回必须递归**（`MSO_SHAPE_TYPE.GROUP`）。

## S2 · 备注链路

**输入**：按 `executor-notes` 契约手写 `notes/total.md`（2 页，`# <number>_<title>` 分页，纯口语，无 Markdown 标记）

**命令**

```powershell
python D:\...\vendor-ppt-master\scripts\total_md_split.py <proj>
# [OK] SVG files and notes have one-to-one correspondence
# Generated: P01.md / P02.md
# [Done] Successfully generated 2/2 file(s)   [exit=0]

python D:\...\vendor-ppt-master\scripts\svg_to_pptx.py <proj> --with-notes
# [exit=0] postflight status=passed; Saved: smoke-demo_20260911_111637.pptx
```

**产物**：`notes/P01.md`(354B)、`notes/P02.md`(333B)、带备注 PPTX

**读回验证**

| 项 | 结果 |
|---|---|
| 拆分产物与页序一一对应 | ✅ 2/2 |
| UTF-8 编码 | ✅ `file` 报告 UTF-8；中文正常解码 |
| 备注写入 PPTX | ✅ 两页均有 `notes_slide` |
| 备注内容无乱码 | ✅ 逐字匹配原文（见下"编码注意"） |

## S3 · 质量链路（D-2 对接）

**命令**

```powershell
python D:\...\deltas\pptx-fill-check\detect_overflow.py <pptx> --json
# [exit=2] P0=32 P1=0 OK=25 (items=57)

python D:\...\deltas\pptx-fill-check\check_title_consistency.py <pptx> --json
# [exit=0] titles=1 p1=0
```

| 检测器 | 结果 | 判定 |
|---|---|---|
| `detect_overflow.py` | **未崩溃**，57 项全部产出分级 | ⚠️ **32 个 P0 为误报**（见问题 P-2） |
| `check_title_consistency.py` | **未崩溃**，识别 1 个标题（"Metric Table" 24pt），0 发现 | ✅ 合理 |

## S4 · 批量校验链路

```powershell
# 4-1 对单个项目目录
python D:\...\batch_validate.py <proj>
# [WARN] No projects found / [ERROR] No projects were found   [exit=0]

# 4-2 对 projects/ 父目录（正确用法）
python D:\...\batch_validate.py <tmp>\projects
# Total projects: 1 | OK: 0 | WARN: 1 (100%) | ERROR: 0
# Common issues: Missing design spec: 1
# Canvas format distribution: PPT 16:9: 1      [exit=0]

# 4-3 空目录
python D:\...\batch_validate.py <tmp>\empty-dir
# [WARN] No projects found / [ERROR] ...        [exit=0]
```

**观察**：`batch_validate.py` 期望**父目录**（扫描其下项目），传单个项目目录会报 "No projects found"；
该错误信息用 `[ERROR]` 前缀但 **exit code 仍为 0**，脚本层面无法据此判定失败。

---

## 环境问题清单（按严重度分级）

### 🔴 阻断级

**P-1 · 导出存在两道未文档化的前置门（首次接触即卡住）**
- 现象：`svg_to_pptx.py` 直接导出失败两次
  1. `spec_lock.md is required for release SVG export`
  2. `default release export requires a passing final SVG quality report; found not-provided`
- 复现：`init` → 放 SVG → 直接 `svg_to_pptx.py` （见 S1 步骤 2/4）
- 定性：**非缺陷**，是设计上的质量门（先 lock、先过 checker 再导出），但 base 的 Generate 工作流文档里有说明，**独立调用脚本时无前置提示**。
- 影响：任何"直接调 `svg_to_pptx.py`"的自动化/冒烟都会踩。
- 建议（不属本卡修复范围）：在冒烟/自动化脚本里固化为 `init → lock → quality_checker → svg_to_pptx` 四步序列。

**P-2 · `detect_overflow.py` 对 `wrap=False` 文本产生系统性假 P0（我方 D-2 代码缺陷）**
- 现象：真实 vendor 产物（vendor 官方模板 `metric_table.svg` / `comparison_matrix.svg`）上检出 **32 个 P0**，例如：
  ```
  [P0] p1 'TextBox 22' text='CURRENT' box=[1.59, 0.53]cm size=10.0pt
       cpl=3 max_lines=1 demand_lines=2 usage=2.0
  ```
- 根因：`capacity_for()` 在 `wrap=False` 时 `max_lines` 恒为 1，而 `demand_lines` 仍按 `ceil(vw/cpl)` 估算；当估算 `cpl` 偏小（窄容器/小字号）时 `demand=2`，`usage=2.0` 直接判 P0。
  **全部 57 项的 `wrap` 均为 `False`，32 个 P0 全部落在此分支**（`wrap=True` 的 P0 = 0）。
- 定性：**执行者（我）在 D-2 引入的算法缺陷**，非 vendor 问题。
- 影响：对含不换行 `<text>`（表头、标签、KPI 数字）的真实产物误报率极高，**P0 退出码（2）失去阻断意义**。
- 建议修复方向（需新卡授权，本卡只记录）：
  1. `wrap=False` 时不应使用"行数"判档，改用**单行视觉宽度 vs 容器宽度**直接比较；
  2. 或对 `wrap=False` 项降级为 P1/信息级，不参与 P0 阻断；
  3. 增加 SVG 原生 `<text>`（带 `text-anchor`）的豁免/白名单判定。

### 🟡 需绕行级

**P-3 · PowerShell 控制台中文/UTF-8 输出乱码（误导性极强）**
- 现象：`python script.py` 输出中文在 PowerShell 中显示为 `��һҳ...`；但写入 PPTX 的内容**完全正确**。
- 验证：改用"python 写 UTF-8 结果文件 → WSL 读取"后，中文完全正常（备注逐字匹配原文）。
- 影响：**容易把编码问题误判为数据损坏**（我本人先用 python-pptx 读回时就被误导过一次）。
- 绕行：需要可读中文输出时，让 python 写 UTF-8 文件（或设 `PYTHONIOENCODING=utf-8` + `[Console]::OutputEncoding`）；**不要以控制台显示判定乱码**。
- 建议：冒烟/M1 脚本统一采用"结果写 UTF-8 文件回读"。

**P-4 · WSL 路径不能传给 Windows python/PowerShell**
- 现象：`cd /mnt/c/...` 在 PowerShell 中被解析为 `D:\mnt\c\...` → `PathNotFound`；但脚本可能**仍继续执行**，产生误导性二次错误。
- 绕行：跨侧调用一律使用 Windows 路径（`C:\...`）；调用前先 `Set-Location -LiteralPath '<win path>'`。

### 🟢 提示级

**P-5 · `svg_quality_checker.py` 的 typography recurrence 规则会拦真实模板资产**
- 现象：vendor 官方 `metric_table.svg` 因 `font-size 18`（6 处）被列为 blocking（超过 sparse 上限 2）。
- 定性：规则本身合理（要求声明 role），但**真实模板与默认 lock 模板天然不匹配**；需在 lock 补 `table_label: 18` 之类 role 才放行。
- 提示：`scaffold-lock` 产出的 lock 是 `[fill]` 占位符，**必须先填真实值**才能通过 gate。

**P-6 · `data-pptx-page-role` 为必填但脚手架不提示**
- 现象：`introduced` 报 `page SVG is missing root data-pptx-page-role`（P01/P02）。
- 提示：手写/复制 SVG 时必须补根属性。

**P-7 · `batch_validate.py` 的 `[ERROR]` 与实际退出码不一致**
- 现象：`No projects were found` 以 `[ERROR]` 输出，但 exit code = 0。
- 提示：自动化不能只依赖退出码判定失败，需解析输出文本。

---

## 未验证项（因依赖/权限未跑通）

| 项 | 原因 | 复现命令（待环境就绪时） |
|---|---|---|
| S1 的 AI 图片/图表→PPTX 原生对象路径 | 需外部 API / 图像资产，超出确定性冒烟范围 | `svg_to_pptx.py <proj> --native-charts-and-tables` |
| `finalize_svg.py` 自包含预览链路 | 本卡 S1-S4 未要求；且需完整 SVG 资产链 | `python vendor-ppt-master/scripts/finalize_svg.py <proj>` |
| 备注→音频（TTS）链路 | 需 TTS 后端与外部服务，属"受限"能力（DELTAS 已标注） | `python vendor-ppt-master/scripts/notes_to_audio.py <proj>` |
| 结构化模板（structured mode）导出 | 需先跑 `create-template` 产出 workspace，超出本卡范围 | `create-template` → `generate-pptx` |
| `batch_validate.py --export` 报告输出 | 本卡未要求，未测 | `... --export --output <path>` |
| 备注在 PowerPoint 客户端中的实际渲染 | 无 GUI 自动化能力；仅验证了 XML/notes_slide 层 | 人工打开 PPTX 目视 |

---

## 《建议》附录

1. **把 P-2（假 P0）列为 D-2 的必修缺陷**（优先级高于新的文档增量）。理由：P0 退出码是 D-2 的核心交付价值（"阻断建议"），当前对任何含不换行文本的真实产物都会误报，等于该功能在真实场景不可用。建议单开修复卡：`wrap=False` 走"单行宽度 vs 容器宽度"判据，不参与行数判据。

2. **固化为四步冒烟序列并写进自动化**：`project_manager init` → `scaffold-lock`（填值）→ `svg_quality_checker --stage final` → `svg_to_pptx`。理由：P-1 的两道门是设计意图，但独立调用时无提示，自动化必须固化顺序。

3. **M1 端到端测试建议增加"读回断言库"**，覆盖：
   - 递归遍历 GROUP 的文本读回（避免 P-1 观察中的"0 文本帧"误判）
   - 中文往返一致性（用 UTF-8 文件，不用控制台）
   - notes_slide 与 `notes/total.md` 的逐页逐字比对
   - 产出 PPTX 的 `postflight status == passed` 断言

4. **建议在 `docs/` 增补一份"Windows 侧执行注意"**，收录 P-3（控制台编码）、P-4（路径）、P-5（lock 必填值）三条，避免后续执行者重复踩坑（本次三条我都实际踩到并各花了一轮排查）。

5. **`batch_validate.py` 退出码问题（P-7）建议向 vendor 上游反馈**（MIT 项目），或在我们的自动化里改用输出文本解析。

---

## 红线自检

| 红线 | 结果 | 证据 |
|---|---|---|
| vendor 零 diff | ✅ | `git diff --stat HEAD -- vendor-ppt-master/` 为空（commit 后） |
| 临时产物零进 repo | ✅ | 全部产物在 `C:\Users\EDY\AppData\Local\Temp\opencode\ppt-smoke\`；repo 无 `.pptx`/`.svg` 新增 |
| 报告为唯一 repo 新增 | ✅ | `git status` 仅 `docs/smoke-report.md` |
| 未做任何修复 | ✅ | 仅记录，未改 vendor 或 D-2 代码 |
