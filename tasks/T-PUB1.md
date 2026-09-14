# 任务卡 T-PUB1 · GitHub 发布准备（P1 · 预计 2-3 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-M2C 已关闭
> 假设：顶层许可 = MIT（与基座一致）；按**公开仓库**标准清理。若用户另有指示（许可/私有），以用户为准并记录变更。

## 目标

让 repo 达到"可安全推送到 GitHub"的状态。**本卡不含 push 动作**（凭据与账号由用户执行；卡提供 push 后验证清单）。

## 步骤 A · 合规层

1. **顶层 `LICENSE`**：MIT 全文，`Copyright (c) 2026 <USER_NAME>`（占位符，交付时提示用户填入）
2. **`THIRD-PARTY-NOTICES.md`**（新建）：
   - `vendor-ppt-master/`：MIT，Copyright (c) 2025-2026 Hugo He，来源 `https://github.com/hugohe3/ppt-master`，说明"原样保留"
   - **吸收致谢表**（8 源，只列名称 + 吸收方式 + 许可）：ppt-director（无许可/原理重写）、guizang（AGPL-3.0/原理重写）、dashi（无许可/原理重写）、Gorden（MIT 源码/改写，模板零接触）、html-ppt（MIT/改写）、frontend-slides（MIT/改写）、beautiful-html-templates（MIT/学结构）、ppt-master（MIT/基座）
   - 指针：`ABSORPTION-LEDGER.md`
3. README"许可"节更新：指向 LICENSE + THIRD-PARTY-NOTICES

## 步骤 B · 隐私脱敏（全库）

1. 扫 `C:\Users\<you>` → 替换 `C:\Users\<you>`（README/USAGE/windows-notes/全部 docs 报告/tasks 卡）；替换后 grep 计数 = 0
2. "加密软件名" 措辞泛化 → "端点透明加密软件"（windows-notes W-8 / decisions / 各报告），保持技术描述完整、不点名
3. 敏感模式扫描：`sk-` / `token=` / `password` / `secret` / 电子邮箱 → 逐项人工确认为占位符或无害
4. 确认 `.env` 不存在于工作区与 git 对象

## 步骤 C · 端点透明加密风险处置（核心）

**方案 1（推荐，先验证）**：
- 对 17 个加密文件逐一验证 git 对象层内容：
  `git cat-file -p HEAD:vendor-ppt-master/scripts/prompt_audit_manifest.json | Select-Object -First 1`
- **通过标准**：首字节为 `{` / `<`（明文 JSON/XML），**不是** `%TSD-Header%`
- 17/17 明文 → 可安全推送；附逐文件证据表

**方案 2（仅当方案 1 失败）**：
- 从官方仓库重新 clone 干净 vendor → 重放 3 处登记改动（routing.md §8 / index.md §2 / 删除 .env）→ 重新验证全部既有测试（快速回归）→ 记录到 decisions

**push 后验证清单**（写给用户）：
- GitHub 网页打开 `vendor-ppt-master/scripts/prompt_audit_manifest.json` → 应显示正常 JSON（非 `%TSD-Header%`（加密文件头标记字面量））
- 抽查 1 个加密 XML（如 `templates/` 下任意带加密的资产）同样步骤

## 步骤 D · git 历史排查

1. `git log --all --oneline -- '*.env' '*EXECUTION-PACK*' '*secret*' '*key*'` → 确认无敏感文件历史
2. `git rev-list --objects --all` 输出扫可疑文件名（.env / credential / token），逐项确认
3. 确认 `.gitignore` 覆盖 `*.pptx` / `.env` / `node_modules/` / `__pycache__/`

## 步骤 E · 发布版 README 精修

- 保持现有 55 行结构不变，仅：顶部加 3-5 行"这是什么/解决什么问题"面向公众的简介（原味、不夸大）
- 检查所有相对链接在 GitHub 上可点（`vendor-ppt-master/` 等）

## 交付物

1. `LICENSE` / `THIRD-PARTY-NOTICES.md`（新建）
2. `docs/pub1-report.md`：合规清单结果 / 脱敏报告（grep 计数） / 加密风险验证 17 文件证据表 / 历史排查结果 / 用户待办（版权名、push、push 后验证）
3. 提交：`chore(release): github publish preparation (T-PUB1)`

## 硬约束

1. **不做 push**；不创建 GitHub 仓库（用户执行）
2. 脱敏不得误伤：替换后全文可读性复查（至少抽查 5 个文件）
3. vendor 除既有 3 处登记外零改动（方案 2 触发时按登记重放）
4. 提交前 `git status` 干净；测试集/骨架/脚本零破坏（抽查 checker 跑一个骨架）

## 验收标准

- [ ] LICENSE + THIRD-PARTY-NOTICES 就位；README 许可节更新
- [ ] 脱敏：`C:\Users\<you>` 全库计数 0；加密软件名称措辞已泛化
- [ ] 加密风险验证：17/17 git 对象明文（逐文件证据）；或走方案 2 并在 decisions 记录
- [ ] 历史排查：无敏感文件记录在案
- [ ] pub1-report.md 含 push 后验证清单；vendor 零新增改动
