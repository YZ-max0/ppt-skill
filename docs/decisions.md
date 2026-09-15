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

1. **端点透明加密软件对文件做透明加密**：vendor 内 17 个 JSON/XML 带 `%TSD-Header-###%`（加密文件头标记字面量）；WSL 读密文，Windows 侧（PowerShell/git/python）透明解密。**vendor 全链路必须在 Windows 侧执行**；跨侧比对用明文 SHA256，禁用 WSL `cmp`
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
a) 信任链：Windows git `git hash-object <raw>` 对比 PowerShell 读明文后手算的 blob SHA1；一致 = git.exe 被 端点透明加密软件 信任
b) **提交后复查**：`git status` 必须干净。防"假 dirty"（端点透明加密软件 可能对 checkout 回工作区的文件重新加密，导致 index/工作区哈希不符）——此步为指挥官补充，执行者的方案未覆盖
c) 只在验证 a+b 通过后用 **Windows git** 提交；任一失败立即停手报告，禁止 WSL git 提交
d) commit message：`chore: baseline M0 — CONTRACT/ledger/DELTAS + vendor ppt-master 5.0.0 + deltas D-1/D-2/D-6 + test set v1`
e) 若出现假 dirty：停止后续动作，把 `git status` 明细带回指挥官决策（预案：.gitattributes 标记 or 接受 dirty 记录成因）

### 2. EXECUTION-PACK 只读排查 —— 批准

范围：回收站元数据扫描 + tasks/ 时间戳时间线；不碰任何现有文件。结论直接回报。

### 3. 探针 —— 批准执行，但设计修正

执行者原探针 `import pptx_animations` **不采用**：该模块存在性未证实，且探针目标错位。
核心未知是 **"端点透明加密软件 透明解密对 python 进程是否生效"**，探针必须打在**加密资产本身**上：

```
python -c "import json; raw=open(r'D:\OpenCode_Spaces\PPT skill制作\vendor-ppt-master\scripts\prompt_audit_manifest.json','rb').read(); print(raw[:12]); json.loads(raw); print('DECRYPT-OK')"
```
- 通过标准：头字节非 `%TSD-Header%`（加密文件头标记字面量） 且 `json.loads` 成功 → 该加密软件对 python 解密生效
- 补一条：在 Windows python 下跑任一 vendor 脚本 `--help`（如 `batch_validate.py --help`）验证可执行性
- 失败处理：带回原始错误，指挥官决定是否升级为冒烟卡前置任务

### 4. A 先行 —— 核准

D-3（style-lock）/ D-4（presenter-mode）任务卡已发布（`tasks/T-D3D4.md`）。探针结果不论成败都要先回报，成功则 D-3/D-4 照常执行。

## 2026-09-10 · 探针 / commit / T-D3D4 裁决

### 复核结论

- 探针（修正版设计）：该加密软件对 Windows python 透明解密生效（json.loads OK）；`batch_validate --help` 可执行；pptx_animations 203 预设加载成功 ✅
- 基线 commit `f4b765b` 存在；Windows git 下 0 假 dirty；vendor 零 diff；探针证明冒烟最大风险解除 ✅
- T-D3D4：`deltas/style-lock.md`（108 行）+ `deltas/presenter-mode.md`（145 行），锚点准确、吸收对照与合规声明齐备，指挥官逐行复核通过 ✅

### 环境约束（追加，长期生效）

1. **git 操作仅限 Windows git**：WSL git 读到 端点透明加密软件 密文会产生 17 条永久假 dirty（密文重加密导致字节不同）。Windows git hash-object 与明文 4/4 一致，为权威工具
2. 该加密软件对 Windows 侧 git.exe/python 均为信任进程（已实测）；WSL 侧不可用

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

## 2026-09-11 · E2E 首跑复核与 C-002 修复裁决

### 复核结论

- commit 链：`8764d6b`（FIX1 3 文件）+ `10836f9`（治理 4 文件），两者范围达标、工作区干净 ✅
- E2E 报告（197 行）：T-01 六项验收全达标；链路 join 打通；quick 入口确认为 `--quick-generate` 标志（非默认路径），解释了两道 lock 门的出现条件 ✅
- FIX1 在真实 AI 产物上验证：`detect_overflow` 45 项全 OK，零误报 ✅
- C-002 指挥官读码复核：`_tier()` 非占位符回退 + `_looks_like_title` 门槛组合定性准确 ✅

### 原则沉淀（本项目的第三条硬经验）

> **D-2 类校验器的每一个判据都必须在真实产物靶场上验证，且必须同时保住"真阳性通道"。**
> 已两次验证：T-FIX1（wrap 假 P0）、T-FIX2（tier 假 P1）。
> 推论：任何新判据的验收标准必须含"靶场前后对比 + 真阳性样张"两项，缺一不可。

### 裁决

1. **e2e 报告提交**：授权，`docs(e2e): M1 first-run report — T-01 quick path`
2. **C-002 修复卡发布**：`tasks/T-FIX2.md`（双路径：占位符保持 + 非占位符全局字号聚类分档；含真阳性验收 + W-5 速查顺带交付）
3. 建议 3（tspan 观察）→ 并入 W-5；建议 4（七阶段耗时表沿用）→ 采纳为后续 e2e 标准记录格式
4. 耗时基线的战略含义：瓶颈在"人工 SVG 撰写（25 分钟）+ 契约修正（8 分钟）"，机器侧仅 10 秒 → M1 下一方向候选：用 base 的 create-layout/visual-styles 预生成"版式资产"，压缩手写成本

## 2026-09-11 · T-FIX2 复核裁决

### 复核结论

- 双路径实现：占位符保持 + 非占位符字号聚类分档（`assign_size_buckets`），主导门槛 `DOMINANCE_MIN` 仅作用于 bucket 路径（占位符跳过）✅
- 主导门槛的必要性有数据支撑（gap 扫描 4.0→4 假报 vs 门槛后 0 假报 + 真阳性保留）✅
- README 三条已知局限如实记录（跨档漂移不可检等）✅；W-5 速查交付 ✅
- **指挥官发现未覆盖缝隙**：同页 spread 检测（detect() 第一段）对 bucket tier **未应用主导门槛**——同页 28+24 双候选（不同角色）会假报。e2e 靶场未覆盖该场景。→ 发 T-FIX2B 收尾
- 第三判据缺陷模式再验证：本次是"修复路径不完整"而非判据方向错误——**复核必须覆盖修复后的所有路径分支**（补充进原则沉淀）

### 裁决

1. **T-FIX2B 小修发布**（同页 bucket 门槛 + `--dominance-min` 参数化 + 合并提交）
2. 建议 2（跨档漂移独立通道）→ **backlog · M2 评估**（需真实产物误报率数据后再定）
3. 提交：FIX2 + FIX2B 合并为一个 commit（`fix(d2): dual-path title tiers for free-design (T-FIX2 + FIX2B)`）

## 2026-09-11 · T-FIX2B 复核与 M1A 发布

### 复核结论

- 同页门槛（bucket tier 才应用 `dominance_min`，占位符路径跳过）实现正确 ✅
- 去重（已报 same-page spread 的 shape 在跨页路径跳过）实现正确 ✅；`--dominance-min` 参数化 + JSON 字段 ✅
- 全量回归 8/8 + 参数双向验证；commit `956faa8` 范围精确（3 文件）✅
- **D-2 质检器缺陷系列关闭**：wrap 假 P0（T-FIX1）｜tier 假 P1（T-FIX2）｜同页门槛缺失（T-FIX2B）——三缺陷全部由"真实产物 + 复核"双轨打出并修复

### 原则沉淀（复核清单正式化——第 4 条）

> **判据类修复的验收必查两条**：① 本判据有几条比较路径？是否都已施加同一语义约束？② 靶场前后对比 + 真阳性样张是否齐备？

### 建议处置

1. "路径覆盖复核固化为验收项" → **采纳**（即上条原则）
2. `--size-bucket-gap 4.0 / --dominance-min 0.6` 默认组合 → 记录为已验证配置（8 用例）；密集层级产物出现时再实测调整（backlog 观察）
3. 同页/跨页语义重叠 → 记录观察点，样本积累后再评估单路径化（本卡不做）

### M1A 发布

`tasks/T-M1A.md`：版式资产库 v0（6 骨架 + 契约 + T-01b 复跑 + 耗时对照）。目标：6 页 deck 人工时间 36 → ≤15 分钟。

## 2026-09-11 · T-M1A 复核裁决

### 复核结论

- 骨架实物抽验（bullets.svg）：合规（根级 g bounds / page-role / 背景独立组 / 统一占位标记）✅
- CONTRACT.md（143 行）：槽位表 + "最坏文案"设计原则 + 实测右界记录（timeline 节点三 x=900）+ 删除规则 ✅
- T-01b：checker 6/6 一次通过、D-2 P0=0、占位符 0、耗时 **36 → 4.2 分钟（↓88%）**——超目标达成 ✅
- commit `41e92fa` + `b31e596` 干净 ✅

### C-004 裁决（同档不同角色误报）

**观察，暂不修。** 理由：① 误报率已降至 1/7（P1 咨询级，人工数秒可辨）；② 执行者的"文本特征辅助分档"是启发式套启发式，假阴性风险未经数据验证；③ M1 当前优先级是让 v0 服务测试集（T-02~T-06）。触发条件：若后续 5 个测试输入出现 >3 个同类误报 → 发 C-004 修复卡。README 已声明该边界。

### 建议处置

1. C-004 缓解 → 归入上述观察项
2. 不升级 create-layout workspace → **同意**（数据驱动：先收集页型复用数据，稳定至 10-12 个再一次性 workspace 化）
3. W-6（init 的 cd 陷阱）+ W-7（`【` 计数断言）→ **采纳**，并入下一卡顺带交付
4. v1 骨架扩充方向 → 记录，按测试集实际需求驱动

### T-E2E2 发布

`tasks/T-E2E2.md`：T-03 方案提案 · **导演式完整版首战**（A 受众卡 → B 逐页导演稿 → B2 视觉导演优化 → C 映射生成；18-22 页；按需扩充 v1 骨架）。

## 2026-09-11 · T-E2E2 复核与 C-007 修复裁决

### 复核结论

- v1 骨架抽验（layered-arch.svg）：合规、层次清晰、占位标记统一 ✅
- T-03：21 页、checker 21/21 一次通过、D-2 P0=0、读回 199 帧零乱码、占位符 0 ✅
- 机器侧成本与页数近乎无关（T-01b 1.2min → T-03 1.3min，页数 ×3.5）✅
- W-6/W-7 增量落地 ✅；素材模拟假设诚实声明 ✅
- **D-1 实战结论**：四阶段可执行、B2 门禁未跳步、无阻断性冲突（3 个小摩擦点记 backlog）

### C-007 裁决（触发条件达成）

T-03 出现 6 项误报（噪声率 11% > 阈值 3）→ **观察状态结束，发 T-FIX3 修复卡**。
框架：bucket 路径内文本特征 subtier（seq 编号 / short 短标签 / long 长句），同档同 subtier 才比较；
**止损条款**：若出现第三类误报，放弃特征方案切换「页面主标题通道」。

### 建议处置

1. C-008（骨架字号密度与 gap 耦合）→ **CONTRACT 增加"骨架层级字号差 ≥6pt"约束**（未来骨架遵守；已有骨架不回改，待 C-007 修复后观察残留）
2. C-009（填充脚本槽位校验）→ backlog（低）
3. D-1 摩擦点（字段 4/§5 重叠、B2 vs 字段 8 关系）→ backlog · M2 合并处理（附原文建议）
4. workspace 化 → 维持不升级；触发条件采纳执行者版本（骨架 ≥20 且复用中位数 ≥2，或 M2 需要）

### 提交授权

- commit 1：`feat(m1): layout assets v1 + T-03 director-mode e2e report`（v1/ + e2e-02-report.md + windows-notes）
- commit 2：`chore(governance): E2E2 decisions + cards`（decisions + T-E2E2 + T-FIX3）

## 2026-09-11 · T-FIX3 复核与 M2 启动

### 复核结论

- `classify_subtier`：seq 判定显式限定 ASCII（修复 `'风险'.isalpha()` 陷阱）、阈值常量清晰、只在 bucket 内切分不跨档（不会制造/隐藏跨档误报）✅
- 靶场 T-03 6→0；历史回归 10/10；真阳性矩阵 3/3（seq/short/long 各一）✅
- 止损条款未触发 → 特征方案保留 ✅；CONTRACT 第 7 条（层级字号差 ≥6pt）落地 ✅
- commit 链（4bb87b6/29b57bc/f9cb260）干净 ✅

### "第三类误报"定义明确化（采纳建议 2）

> 止损条款中的"第三类误报" = 误报项不属于 `text@*/{seq,short,long}` 任一形态，**或**涉及占位符路径。
> 用于下次复查的可判定标准。

### 建议处置

1. subtier 阈值（SHORT_MAX_VW=5.0 / SEQ_MAX_LEN=4）→ **暂不参数化**，更多真实 deck 采样后再定
2. 期望值 vs 修复目标分开记录 → backlog（回归脚本规范化）
3. **M1 质检链路终局关闭**：D-2 全部缺陷（wrap 假 P0 / tier 假 P1 / 同页门槛 / subtier 混角色）四连关闭

### M2A 发布（M2 开门）

`tasks/T-M2A.md`：视觉验证能力建设——渲染器探针（PowerPoint COM / LibreOffice）→ 渲染 3 份现有产物 →
脚本化 `deltas/render-preview/`。**理由：至今所有验收都是结构级，从未渲染过一页真实视觉**——
"效果更好"的用户目标必须在视觉层验证。

## 2026-09-11 · M2A 复核与视觉闭环打通

### 复核结论

- 渲染器：**WPS Office COM**（注册 `PowerPoint.Application` ProgID）可用，1280×720 精确渲染 ✅
- 3 deck 全部渲染（t01 6p / t01b 6p / t03 21p）+ contact sheet；程序化空白/深色页验证通过 ✅
- 脚本入库（render_png.py 221 行 + README，3 个实现缺陷已修复）✅；commit 链干净 ✅
- **W-8 修正（指挥官实测）**：渲染产物的 端点透明加密仅限制 **WSL 进程**；**Windows 进程（含 opencode read 工具）可读明文**——
  指挥官已直接读取两张 contact sheet 完成视觉评估。**W-8 表述应从"agent 无法读取"修正为"WSL 进程不可读；Windows 侧全链路可读"**

### 视觉评估结论（首份，详见 `docs/visual-review-01.md`）

- 一致性 5.5/6、层级 5/6；**视觉冲击 2.5/6 = 骨架级短板**
- 定性：当前风格"克制企业管理风"对汇报场景合适，但缺图表/视觉锚点/封面设计 → v2 视觉增强候选方向

### 裁决

1. M2A **关闭**；视觉闭环固化：今后每批渲染 → 指挥官直接读图评估（L3 的 AI 侧）
2. 建议 3（渲染自动回归基线：唯一色数 + 像素 diff）→ 采纳为 M2 后续小项
3. 建议 4（渲染器冗余）：单点依赖 WPS COM 记录为风险；LibreOffice 安装与否待用户决定
4. 建议 5（contact sheet 分片）→ backlog（低）
5. **下一步三选项**（待用户偏好）：a) v2 视觉增强（对应"效果更好"）；b) 继续测试集 T-02/T-04/T-05/T-06；c) D-4 演讲者模式落地

## 2026-09-11 · 用户拍板与 T-M2B 发布

### 用户决策（已录入）

- 方向：**A. 视觉增强 v2：图表与锚点骨架**
- 视觉尺度：**增强视觉表现力**（非保持克制）——封面更强、色块/几何更多、页间节奏更丰富
- 边界（指挥官设定）：增强 ≠ 花哨；一致性优先；语义色系统不破坏

### T-M2B 发布

`tasks/T-M2B.md`：8 个 v2 骨架（4 图表 + 4 锚点）+ t03-v2 增强版对照复跑 + 接触表对照。
对照实验设计：同内容双版本（v1 克制版 vs v2 增强版）供用户直接比较。

## 2026-09-11 · T-M2B 复核（目视对照）与修订裁决

### 目视对照结论（详见 `docs/visual-review-02.md`）

**成功**：封面变强（"方案感"）、章节页/图表/证据墙/对比条/金句页到位、节奏松紧交替；
视觉冲击评分 2.5 → 4/6；一致性维持（仅新增同色系浅蓝）。

**问题（3 项）**：
1. **V2-R1 内容完整性疑点（最高优先）**：v1 P09"平台由四个模块组成"（架构内容）在 v2 中疑似丢失（被章节页替换）→ 必须澄清映射或恢复
2. V2-R2 章节体系不完整（03/05 有、01/02/04 无）
3. V2-R3 深色页需预算约束（≤15% 页数）

### 裁决

1. **T-M2B-R1 修订卡发布**：R1 内容完整性（含 v2 页级映射表）/ R2 章节体系二选一（推荐撤）/ R3 CONTRACT 补充 / R4 C-010 `value` 类（**硬止损：value 后再出现任何 free-design 误报即无条件切换主标题通道**——特征方案累计三次机会已用满）/ R5 W-6 更新
2. 建议 5（图表坐标自动计算工具）→ backlog
3. 经验再沉淀：**"程序化指标（色数等）不能替代目视评估"** ——本次内容丢失问题是目视对照抓到的，色数指标完全测不出

## 2026-09-11 · T-M2B-R1 复核裁决

### 复核结论

- **内容丢失确认并恢复**：执行者承认 P09 替换失误，已恢复 layered-arch；页级映射表 21 项全追踪 ✅
- **止损条款真实触发（首次）**：value 类加入后误报未改善（T-03 指标为文字非数字）→ 按硬止损切换"页面主标题通道"；执行者如实报告已知代价（samepage_3 同页检测失效）✅
- 目视复评（`visual-review-03.md`）：P09 恢复、章节撤、深色 10%、增强保留 ✅
- 回归：t03-v2 3→0；真阳性矩阵 seq/short/long/value 各过；跨页 truepos 过 ✅
- commit `fdf8cab` 干净 ✅

### 裁决

1. T-M2B-R1 **关闭**；`samepage_3` 正式移入**能力边界**记录（free-design 同页检测已移除，非回归失败）
2. `value` 类**保留**（数字型 deck 未来有效）
3. 建议 4/5 → backlog 小项（CONTRACT 章节页成套约束 + section-hero 标注"仅 ≥3 章 deck"），下批顺带
4. 项目状态：M0/M1 全关闭；M2 渲染管线/视觉闭环/v2 增强已完成；资产库 24 骨架；质检器 6 缺陷全修（含止损机制实战验证一次）

## 2026-09-11 · 用户决策与 T-M2C 发布

### 用户决策（已录入）

- 方向：**A. 产品化收尾：使用入口与手册**
- 节奏：**手册完成后暂停，用户亲自实测**（指挥官同意——内部卷太久后，真实使用反馈 > 继续跑测试集）

### T-M2C 发布

`tasks/T-M2C.md`：README（≤120 行）+ USAGE.md（≤300 行）+ **手册自测（按手册复跑 T-01b，doc-test）** + 报告。
关键验收：手册命令"可复制可执行"——用自己写的手册复跑一次全流程。

### 对用户实测的说明（指挥官）

实测时可用 USAGE 的"请求模板"六输入项（主题/受众/页数/时长/素材/风格偏好）发起；
预期交付物 = .pptx + contact sheet 图。首次实测建议从"快速通道 6-8 页"起步（路径最短），再试"导演式"。

## 2026-09-11 · T-M2C 复核关闭与项目实测阶段

### 复核结论

- README（55 行）+ USAGE（265 行）结构与限额达标；24 骨架索引与实物逐一核对 ✅
- doc-test：按手册复跑 T-01b 六步全过（含 checker/导出/D-2/渲染）✅
- 3 处偏差均反向验证了手册提醒的准确性（`--dir`/整段替换/版本归属）✅
- 指挥官修正 1 处笔误（`PowerPoit` → `PowerPoint`，字符级）；`projects/` 残留已由执行者清理
- 建议 4（Skill 形态入口暂不改造）→ **同意**（等真实使用反馈后再议）

### 项目状态：进入用户实测阶段

- 全交付关闭：M0 / M1 / M2（渲染管线 + 视觉闭环 + v2 增强 + 手册）
- 资产库 24 骨架 ｜ 质检器 6 缺陷全修 ｜ 视觉评分 2.5→4/6 ｜ vendor 改动仅 3 处登记
- **下一步 = 用户亲自实测**（快速通道起步 → 导演式 → 反馈收集）

## 2026-09-11 · GitHub 发布决策与 T-PUB1 发布

### 用户询问与指挥官结论

用户问"是否可以发到 GitHub" → **可以**。三层许可审计：基座 MIT（可发布，须保留声明）/ 增量原创 / 吸收源全部原理重写（无代码资产混入，无 AGPL 传染）。

### 发布前五项必做（已入 T-PUB1 卡）

1. **加密资产文件验证**（core）：17 个加密文件的 git 对象须为明文，否则 GitHub 上文件不可用；push 后网页抽查
2. 隐私脱敏：`C:\Users\<you>` 全库替换占位符；"加密软件名"措辞泛化
3. 顶层 LICENSE（默认 MIT，用户可改）+ THIRD-PARTY-NOTICES（ppt-master 归属 + 8 源致谢表）
4. git 历史排查（.env 等敏感文件从未入库）
5. 发布版 README 精修（公众向简介 3-5 行）

### 决策

- 默认：**MIT 许可 + 公开仓库标准**（用户若想改，告知执行者）
- **push 与建库由用户执行**；卡提供 push 后验证清单

## 2026-09-14 · 发布完成确认 + 未完成清单评审 + T-E2E3 发布

### 发布状态确认（指挥官读盘核实）

- T-PUB1 已执行全闭环：LICENSE（版权人 `YZ-max0`）/ THIRD-PARTY-NOTICES（含 3 处 vendor 登记改动披露）/ 全库脱敏（16 文件 29 处，grep=0）/ TSD 验证 **17/17 明文**（方案 1 成功）/ 历史排查干净
- **push 已完成**：`https://github.com/YZ-max0/ppt-skill`（**Private**，20 commits，main），push 后验证已由执行者完成
- `docs/QUALITY-TIERS.md`（三档质量决策表）来源未在任何回执中报告（第二写入源痕迹），内容复核无误 → **追认采纳**
- 公开化（Private → Public）为将来选项：届时复核第三方资产表述，最终合规责任在发布者

### 未完成清单评审（用户提供）与裁决

清单质量高，优先级判断（"验证不足 > 能力不足，先跑测试集"）成立。**指挥官修正一处**：
把"接 base 33 图表"（清单优先 2）**合并进"跑测试集"**（清单优先 1）——T-02 数字密集，是图表接入的天然靶场，
一轮完成"验证 + 补能力"。其余 backlog 照单收纳（工程债/文档欠账/战略级均记录在案）。

### T-E2E3 发布

`tasks/T-E2E3.md`：T-02 年终述职（② 标准档）+ base 图表接入（3 模板试验 → ≥2 页实战）+ 图表使用说明与场景分工。

## 2026-09-14 · T-E2E3 复核裁决 + T-FIX4/T-E2E4 发布

### 复核结论

- 验收全过：14 页、3 页 base 图表（line/bullet/column）、checker 14/14、D-2 全 0、乱码 0、占位符 0 ✅
- **chart-fill 三步接入法**（校验契约→读数据模型→重算几何）质量极高；选型严格按 `charts_index.json` 规则，
  **正确否决指挥官卡内建议**（waterfall 无 running total / grouped_bar 维度不符）→ 采纳执行者修正
- 场景分工口诀入库（"能填槽位用 v2 / 要算坐标用 base / 要能改数用 base 原生"）
- **C-011 内容泄漏（靠看图抓到，checker 与 D-2 均测不出）**：骨架无标记示例内容会随机械填充泄漏 →
  升级为 **T-FIX4 全库卫生专项**（扫描 24 骨架 + 修复 + 自动化阻断 + 写进 USAGE）
- 环境事实（执行者自纠）：D 盘 WSL 侧只读是 mount namespace 的 ro 标志（非沙箱）；
  可行链路 = WSL 读写文本 + Windows 进程跑 Python/git + `\\wsl.localhost\` 互通 —— 记入长期环境事实

### git 远端状态澄清（指挥官核实）

- 本地 24 commits 与 `origin/main` **完全同步**（无未推送）；decisions 早前"20 commits"为旧快照
- Remote：`https://github.com/YZ-max0/ppt-skill`；**可见性待用户查证**
  （GitHub → 仓库 Settings → General 看 Visibility；若为 Public 亦已按公开标准清理过）

### 发布

- `tasks/T-FIX4.md`：骨架卫生全线复查（P0，先行）
- `tasks/T-E2E4.md`：T-04 技术分享 + 演讲者逐字稿（图表演兵 + D-4 逐字稿轨道首落地）

## 2026-09-14 · T-FIX4/T-E2E4 复核裁决 + T-FIX5/T-E2E5 发布

### 复核结论

- FIX4：24 处 HIGH 泄漏全部槽位化（7 骨架）；`check_hygiene.py` **双模式**（交付物=词表精确 / 骨架=+启发式）双向验证通过；槽位名长度=几何约束（96pt 列放长槽位名溢出 35.4%）已记入 HYGIENE.md；新骨架入库流程含 `--skeleton-mode` 硬门 ✅
- E2E4：25 页一次通过（checker 25/25、D-2 全 0、213 OK）；图表 3→6 类；**D-4 逐字稿首次落地**（25/25 逐字一致、5061 字、P-7 未触发、给出语速灵敏度区间而非单点）✅
- C-015（图例压字，跨组）已修复（LEGEND_Y=648）；C-016（progress 行高）已修复；C-017（多序列 column 命名偏差）如实披露 → 顺带文档化
- commit 链（e336743/de1b6f9）核实；工作区干净 ✅

### 原则强化（第三次验证）

**"单层合法、整体错误"类问题无法被单组校验拦截**——已出现三次（P09 内容丢失/色数测不出；C-011 内容泄漏/质检器测不出；C-015 跨组重叠/checker 测不出）。
**双轨对策**：① 目视（人/模型看 contact sheet，永久保留）；② 本卡新增第三道自动闸——`check_overlap.py`。

### 发布

- `tasks/T-FIX5.md`：跨组重叠检查器（含 C-017 顺带文档化）
- `tasks/T-E2E5.md`：T-05 BP 路演（③ 导演式 + 视觉锚点 + 财务图表；"效果更好"的终极靶场）

## 2026-09-14 · T-FIX5/T-E2E5 复核 + T-E2E6 发布（测试集收官卡）

### 复核结论

- FIX5：`check_overlap.py` 双向验证通过（正样本 0 误报 / C-015 负样本 32% 重叠被拦 / 豁免机制可用）；
  **执行者修正卡内假设**（跨组文本-图形重叠亦大量合法 → 收紧为"标记类图形才参与比对"）——正确；
  历史真阳性（T-02 P06 图例 y=593 vs 类目 y=600）被准确捕获 ✅
- E2E5：17 页、③ 导演式、四道质检全绿；图表 9 类渲染器；waterfall 正当性论证正确（T-05 有 running total）；
  融资用途刻意用 budget-4 而非图表（面积预算裁决）✅
- **指挥官目视验收**（`visual-review-04.md`）：三缺陷修复图上可验证；视觉冲击 **4.5/6**（2.5→4→4.5）；
  仍需图片能力才能再上台阶 ✅

### 第四类问题与自动化边界（终局结论）

C-019（未达标渲染为超额 122%，"画对形状、画错含义"）确认第四类问题。
**谱系**：P09 丢失（色数测不出）→ C-011 泄漏（质检器测不出）→ C-015 重叠（checker 测不出）→ C-019 语义（全部测不出）。
**结论：闸门证明"没违反已知规则"；语义正确性 = AI 目视的永久责任（每轮渲染→指挥官读图，不可省略）。**
C-020/C-021/C-022 均已修复；C-019 已加 `lower_is_better` 支持。

### 发布

`tasks/T-E2E6.md`：T-06 评审答辩（测试集收官）——首次实战评审卡机制（§8 五视角）+ 5 质询应答页组。
完成后测试集 6/6 全部跑完。

## 2026-09-15 · T-E2E6 复核 + 测试集收官 + 全景评估

### 复核结论

- 20 页、四道质检全过；新增 2 答辩骨架（defense-answer / qa-mapping）；质询映射单一数据源 + 自动自检 5/5 ✅
- **评审卡首战**：24 项检查 → 7 项真实问题（含 2 项语义/事实错误：P06 标题 57% vs"四成"、P13 证据链 98 倍矛盾）
  → 均为自动闸放过的"第四类问题"（语义），再次印证目视/内容审查不可替代 ✅
- **指挥官目视验收**：P06 修复可见（"反降六成"）、P04/P16 橙色警示语义正确、质询链结构清晰、金句页有设计 ✅

### 裁决

1. **评审卡登记为 B3 阶段**：接受执行者建议（实战数据：评审卡天然落于 B2 后、C 前，是"生成前最后一道内容闸"）→ 下批小修写入 director.md §2 + §8 措辞
2. **C-028 教训**（返修破坏几何）→ 采纳建议：USAGE 增补"任何返修后必须重跑质检流程"（下批小修）
3. **测试集 v1 六输入全收官**：T-01~T-06 全部一次通过四道质检
4. 全景评估落盘：`docs/PROJECT-STATUS.md`

### 下一步选项（待用户选择）

| 选项 | 说明 |
|---|---|
| **A. 图片位骨架**（推荐） | 26 骨架无图片位 = "效果更好"最后大缺口；需设计骨架 + 验证 base 图片嵌入链路 + 素材策略 |
| B. tables/ 族接入 | base 5 表格模板 + vocabulary，低成本补齐"汇报刚需" |
| C. 渲染器冗余 | 需用户授权安装 LibreOffice（消除单点依赖） |
| D. 用户实测 / 公开化 | 测试集已收官，实测与公开是自然的下一步 |

### 用户决策

**A. 图片位骨架** → 发 `tasks/T-IMG1.md`（链路研究 + 3 骨架 v3 + 端到端实测 + 素材策略 + 顺带小修 B3/USAGE）。
