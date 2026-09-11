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
