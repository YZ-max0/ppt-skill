# Decisions —— 指挥官裁决记录（append-only）

## 2026-09-10 · T-D6 / T-D2 交付裁决

### 接受项（偏离核准）

| # | 事项 | 裁决 |
|---|---|---|
| 1 | T-D6 新节编号 §8（卡内写 §6，实际已有 §6/§7） | **核准**。编号重复会破坏权威结构，执行者的处理正确；"§1-§7 unchanged"声明有效 |
| 2 | T-D6 触发器按 director.md 实际 5 行（卡内写 4 行） | **核准**。以 director.md 事实为准 |
| 3 | T-D2 判档统一 120%（卡内 80-125） | **核准**。80% 下限无实据（Gorden 实际 TOLERANCE=1.2 且无 80% 档），执行者纠正正确。我方原卡为臆测值，责任在指挥侧 |
| 4 | T-D2 标题一致性 0.5pt 判据 + tier 分组 + 跨页无 keeper 修正 | **核准**。"中位值×1.2"语义错误（字号为档位）；tier 分组防止 32pt 主标题 vs 40pt 副标题误报，正确 |

### 驳回/维持项

| # | 事项 | 裁决 |
|---|---|---|
| 5 | 更新 SKILL.md Mandatory Load Order | **维持不改**。SKILL.md 第 3 步强制读 routing.md，§8 随读即达；Director 非"路由/profile"，不属加载映射表。功能自足，漏读属执行错误非文档缺陷。若未来出现实际漏触案例再议 |
| 6 | 前置预算选择（Gorden compute_capacity 另一用途） | **关闭**。base Step 5 `check-plan` 已是前置预算；D-2 后置检测与其互补，无冗余缺口 |

### 授权的后续动作

| # | 动作 | 执行者 | 说明 |
|---|---|---|---|
| 7 | index.md §2 登记 Director（input stage，一行） | 执行者（小修卡） | base 维护纪律（index.md §3 规则 2，先例：apply-template-workspace）。同时检查 `prompt_audit_manifest.json` 同步成本；若成本高，在本文档记豁免理由 |
| 8 | `TOLERANCE` 提为 `--tolerance` CLI 参数 | 执行者（小修卡） | 一行改动，保留默认 1.2 |
| 9 | `check_title_consistency.py` 183-187 行注释同步 | 执行者（小修卡） | 注释仍描述旧"同页有 keeper"设计，与实现不符；指挥官复核发现 |

### 环境约束（长期生效）

1. **TSD 透明加密**：vendor 内 17 个 JSON/XML 带 `%TSD-Header-###%`；WSL 读密文，Windows 侧（PowerShell/git/python）透明解密。**vendor 全链路必须在 Windows 侧执行**；跨侧比对用明文 SHA256，禁用 WSL `cmp`
2. **git 验收法失效**：repo 无任何 commit，全文件 untracked。后续增量验收暂时依赖"官方基线逐字节比对"。**建议尽快做基线 commit（待用户授权，指挥官不自行操作）**
3. `tasks/EXECUTION-PACK.md` 于执行期从磁盘消失（非本指挥官创建/未参与），已向用户报告非本项目产物，待用户侧排查

### 复核结论

- routing.md §8：4 要素（触发器/唯一权威/相对引用/无新路由）齐全，纯追加 ✅
- detect_overflow.py：判档与裁决一致，CLI/退出码/JSON 完备 ✅
- check_title_consistency.py：判据正确，注释不一致（见 #9）⚠️
- 红线静态检查：repo 内 `*.pptx` = 0、`*gorden*` 匹配 = 0 ✅
- 临时证据：3+1 样张、双脚本 JSON、退出码、追加 patch 全部存在 ✅

## 2026-09-10 · T-REV1 交付裁决

### 复核结论（逐项读过文件）

- R1：`index.md` §2 第 26 行新增 `director` 行，Class/Path/Parent 列对齐既有格式 ✅
- R2：`--tolerance`（default=TOLERANCE=1.2）已入 argparse 且调用链穿透（main → run_detect → diagnose）；回归三样张结果与修订前一致，`--tolerance 1.0` 冒烟判档随参数变化 ✅
- R3：183-187 行注释已同步为 "no keeper prerequisite" ✅
- 红线：改动面仅 3 文件，验收产物零进 repo ✅

### 决策：prompt_audit_manifest.json 不修改（核准执行者判断）

理由：① index.md 本就不在 runtime load sets 内（§3 规则 5）；② routing.md 已在 `bootstrap.routing` load set，§8 为同文件内容；③ deltas/ 不在 manifest `documents.include` 范围，纳入属 base 维护策略改动；④ manifest 为 `audit_only: true`、`runtime_consumed: false` 惰性文件。

**由此确立边界：`deltas/` 目录豁免于 base prompt_audit_manifest 审计；vendor 内修改仅限"挂载/登记"类最小改动（routing.md §8、index.md §2），并逐条记录于本文件。**

### Backlog（小项积压，下次批量修卡处理）

- [ ] `deltas/pptx-fill-check/README.md` 补 `--tolerance` 参数说明（乘数语义：1.0=严格几何、1.5=宽松）

### 状态

D-2 质检链路：定义（T-D2 卡）→ 实现 → 修订（T-REV1）→ 验收关闭 ✅

## 2026-09-10 · 第二批指令裁决（commit / 排查 / 探针 / A 先行）

### 1. 基线 commit —— 有条件授权

验证链（缺一不可）：
a) 信任链：Windows git `git hash-object <raw>` 对比 PowerShell 读明文后手算的 blob SHA1；一致 = git.exe 被 TSD 信任
b) **提交后复查**：`git status` 必须干净。防"假 dirty"（TSD 可能对 checkout 回工作区的文件重新加密，导致 index/工作区哈希不符）——此步为指挥官补充，执行者的方案未覆盖
c) 只在验证 a+b 通过后用 **Windows git** 提交；任一失败立即停手报告，禁止 WSL git 提交
d) commit message：`chore: baseline M0 — CONTRACT/ledger/DELTAS + vendor ppt-master 5.0.0 + deltas D-1/D-2/D-6 + test set v1`
e) 若出现假 dirty：停止后续动作，把 `git status` 明细带回指挥官决策（预案：.gitattributes 标记 or 接受 dirty 记录成因）

### 2. EXECUTION-PACK 只读排查 —— 批准

范围：回收站元数据扫描 + tasks/ 时间戳时间线；不碰任何现有文件。结论直接回报。

### 3. 探针 —— 批准执行，但设计修正

执行者原探针 `import pptx_animations` **不采用**：该模块存在性未证实，且探针目标错位。
核心未知是 **"TSD 透明解密对 python 进程是否生效"**，探针必须打在**加密资产本身**上：

```
python -c "import json; raw=open(r'D:\OpenCode_Spaces\PPT skill制作\vendor-ppt-master\scripts\prompt_audit_manifest.json','rb').read(); print(raw[:12]); json.loads(raw); print('DECRYPT-OK')"
```
- 通过标准：头字节非 `%TSD-Header%` 且 `json.loads` 成功 → TSD 对 python 解密生效
- 补一条：在 Windows python 下跑任一 vendor 脚本 `--help`（如 `batch_validate.py --help`）验证可执行性
- 失败处理：带回原始错误，指挥官决定是否升级为冒烟卡前置任务

### 4. A 先行 —— 核准

D-3（style-lock）/ D-4（presenter-mode）任务卡已发布（`tasks/T-D3D4.md`）。探针结果不论成败都要先回报，成功则 D-3/D-4 照常执行。

## 2026-09-10 · 探针 / commit / T-D3D4 裁决

### 复核结论

- 探针（修正版设计）：TSD 对 Windows python 透明解密生效（json.loads OK）；`batch_validate --help` 可执行；pptx_animations 203 预设加载成功 ✅
- 基线 commit `f4b765b` 存在；Windows git 下 0 假 dirty；vendor 零 diff；探针证明冒烟最大风险解除 ✅
- T-D3D4：`deltas/style-lock.md`（108 行）+ `deltas/presenter-mode.md`（145 行），锚点准确、吸收对照与合规声明齐备，指挥官逐行复核通过 ✅

### 环境约束（追加，长期生效）

1. **git 操作仅限 Windows git**：WSL git 读到 TSD 密文会产生 17 条永久假 dirty（密文重加密导致字节不同）。Windows git hash-object 与明文 4/4 一致，为权威工具
2. TSD 对 Windows 侧 git.exe/python 均为信任进程（已实测）；WSL 侧不可用

### EXECUTION-PACK 排查结论（结案待用户确认）

未进回收站、tasks/ 无痕迹、repo 当时零 commit 无历史可恢复。非执行者所为。Recuva 级深度恢复需用户明示，否则结案。

### 裁决：采纳执行者三项建议

1. 版式登记集"双载体"表达（flat=页面结构契约 / structured=版式键+映射）——采纳，与 base `pptx_structure.mode` 两态一致
2. 不新增 notes 前置 marker（元字段不进备注区，防 TTS 污染）——采纳，D-4 P-10 已落实
3. D-3/D-4 保持两份不合并（加载时机不同）——采纳

### 台账快照修正

A-001~A-011 的"落盘文件"列已按实际形态修正（基座引用 vs deltas 新建 vs 留待 M2），A-006/A-010 指向实际文档。

## 2026-09-10 · 第二批复核与提交授权（本会话指挥官）

### 独立复核（本会话指挥官执行）

- D-3 `style-lock.md`：107 行；条款 L-0~L-10 体系完整；base 锚点抽验全部真实——`page_rhythm`（anchor|dense|breathing，spec_lock_reference.md:28）、`page_pptx_layouts`（:68）、`template_reuse_scope: mirror|layout|style`、flat/structured 边界（artifact-ownership.md:79-80）✅
- D-4 `presenter-mode.md`：145 行；P-0~P-14 体系完整；承载链路抽验全部真实——`--no-notes`（svg_to_pptx cli.py:1092）、`notes/total.md`→`total_md_split.py`（:290/334）、`notes_to_audio.py`（:213）✅
- 台账 diff 定性：A-001~A-011 "落盘文件"列由计划态修正为实际态（账实对齐），**内容正确，追认采纳**
- decisions.md 的"探针 / commit / T-D3D4 裁决"段（+27 行）：非本会话指挥官写入；内容与盘上事实一致，追认采纳

### 治理警报：存在第二写入源

`tasks/EXECUTION-PACK.md`（出现后消失）、`tasks/T-SMOKE.md`、上述 decisions 追加段均**非本会话指挥官所写**，但以"指挥官：opencode"名义落盘。处置：
1. T-SMOKE 卡经本会话指挥官复核（S1-S4 引用的 `svg_to_pptx.py`/`total_md_split.py`/`batch_validate.py` 均确认存在，范围合理）→ **正式采纳为 M0 冒烟卡**
2. 已向用户报告，请用户澄清第二写入源身份；在澄清前，**本会话指挥官为唯一指令源**，第二写入源产物一律经复核后追认方可执行

### 提交授权（定向，两个 commit）

- commit 1：`docs(deltas): D-3 style-lock + D-4 presenter-mode`
- commit 2：`chore(governance): ledger reconciliation + decisions + T-SMOKE intake + task cards`
- 范围：deltas 两文件 / `ABSORPTION-LEDGER.md` / `docs/decisions.md` / `tasks/T-SMOKE.md` / `tasks/T-D3D4.md`（未入库的卡一并）；执行者用 Windows git

### 冒烟授权（T-SMOKE 执行注记）

核准开跑，附三条注记：
1. S1 输入优先使用真实资产 `templates/tables/*.svg`，自写 SVG 作为补充而非首选
2. 报告必须记录 `python --version` + 关键依赖版本（python-pptx/lxml），环境问题才能定性
3. 顺序：commit 1 → commit 2 → 冒烟；报告唯一 repo 新增 `docs/smoke-report.md`

## 2026-09-11 · 第三批复核与 P-2 修复裁决（本会话指挥官）

### 复核结论

- commit 链：`26102bb`（deltas 2 文件）/ `034787e`（治理 3 文件）均达标，当前工作区仅 `docs/smoke-report.md` 未提交 ✅
- S1/S2/S4 跑通；S3 暴露 P-2 ✅（报告 236 行，四段 + 分级问题清单 + 未验证项 + 建议，结构完整）
- **P-2 指挥官代码级复核**：`capacity.py:193` + `detect_overflow.py:82` 组合缺陷实锤——wrap=False 恒 `max_lines=1` 与折行 demand 估算组合产出假 P0（usage=2.0）。定性：D-2 实现缺陷，责任在本 repo ✅

### 裁决

1. **smoke-report 提交**：授权，message `docs(smoke): M0 integration smoke report + env findings`
2. **P-2 修复卡发布**：`tasks/T-FIX1.md`，优先级 P0（高于任何新文档增量）。裁决理由：P0 退出码是 D-2 核心价值，当前在真实产物上不可用
3. 修复框架：首选水平判据（最长段 vw/cpl，1.0/1.2 档不变、语义改为水平超宽）；备选"wrap=False 最高 P1"须附 ≥5 样本误差分析
4. P-1/P-3/P-4/P-5 绕行知识：并入 T-FIX1 次要交付 `docs/windows-notes.md`
5. P-7（batch_validate 退出码）记 backlog：自动化解文本、不依赖退出码；不向上游提 issue（非阻塞）

### 治理警报（第二次记录，仍未澄清）

T-SMOKE / decisions 追加段 / EXECUTION-PACK 的"第二写入源"：执行者亦确认非其创建。三方（指挥官/执行者原文/用户侧）均未认领。**在用户澄清前，第二源产物一律经指挥官复核追认后方可执行**；本会话为唯一指令源。

## 2026-09-11 · T-FIX1 复核与 M0 关闭裁决

### 复核结论（指挥官读码验证）

- `detect_overflow.py` 分轴判据：wrap → vertical（demand/max_lines）、nowrap → horizontal（longest_vw/cpl），`axis`/`overflow_horizontal` 字段与按轴 remedy 完整正确 ✅
- `auto_size` 采集端扩展为 `(TEXT_TO_FIT_SHAPE, SHAPE_TO_FIT_TEXT)` 并附物理语义注释 ✅
- `capacity.py` 双轴契约 docstring 含历史缺陷记录（防回退）✅
- 靶场 32 P0 → 0 P0；回归 3 样张不变；新增 wrap_ok/wrap_over 双向验证；`docs/windows-notes.md`（67 行）四条绕行准确 ✅
- 工作区核对：M 3 文件 + ?? windows-notes + 指挥官侧 decisions/T-FIX1 卡，与声明一致 ✅

### 建议处置

1. 判据正确性依赖"物理保证识别" → **采纳**，作为 D-2 设计原则记录（本条 + README 软放行表）
2. 水平轴 inset 固定 0.25cm 精度风险 → **backlog**（出现自定义 margin 争议时才修，届时读 `tf.margin_left/right`）
3. wrap_over 收编为固定回归样张 → **采纳，转为 backlog 执行项**：把样张生成脚本（make_samples.py 等）收编到 `tests/scripts/`，运行时生成 .pptx 到临时目录（.pptx 仍不进 repo）；并入 M1 阶段小卡
4. 提交 FIX1 改动 → **授权**（见下）

### 提交授权（两个 commit）

- commit 1：`fix(d2): wrap-axis judgment + auto_size soft-pass (T-FIX1)`（capacity/detect/README）
- commit 2：`docs: windows-notes + T-FIX1 governance`（windows-notes + decisions + T-FIX1 卡）

## M0 关闭宣言

M0 全部交付关闭：导演工作流（D-1）｜基座挂载（D-6）｜填充质检（D-2 + FIX1）｜风格锁（D-3）｜演讲者模式（D-4）｜测试集 v1（D-5）｜集成冒烟（S1-S4，7 条问题清单 + windows-notes）。vendor 累计改动仅 2 处最小登记（routing.md §8 / index.md §2），其余零触碰。下一步进入 M1 策划（端到端真实生成首跑）。
