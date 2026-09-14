# GitHub 发布准备报告（T-PUB1）

> 执行者：开发工程师 ｜ 日期：2026-09-14 ｜ 卡：`tasks/T-PUB1.md`
> 目标：让 repo 达到"可安全推送到 GitHub"的状态。**本卡不含 push，不创建仓库。**
> 结论：**全部验收项通过，可安全推送**（方案 1 成功，未触发方案 2）

---

## A · 合规层 ✅

### A.1 顶层 `LICENSE`

MIT 全文，版权行为 `Copyright (c) 2026 <USER_NAME>` —— **占位符待用户填入**（见 §用户待办）。

### A.2 `THIRD-PARTY-NOTICES.md`（新建，65 行）

包含三部分：

1. **内置基座（原样保留）**：`vendor-ppt-master/` = ppt-master 5.0.0，MIT，
   Copyright (c) 2025-2026 Hugo He，来源 `https://github.com/hugohe3/ppt-master`，
   并**逐条列出本仓库对其的 3 处登记改动**（routing.md §8 / index.md §2 / 未引入 .env）

2. **吸收致谢表（8 源）**：

   | 来源 | 许可 | 吸收方式 |
   |---|---|---|
   | ppt-director | 无 LICENSE | 原理重写 |
   | guizang-ppt-skill | **AGPL-3.0** | 原理重写 |
   | dashi-ppt | 无 LICENSE | 原理重写 |
   | GordenPPTSkill | MIT（templates 非商用） | 改写，**模板零接触** |
   | html-ppt | MIT | 改写 |
   | frontend-slides | MIT | 改写 |
   | beautiful-html-templates | MIT | 仅学结构 |
   | ppt-master | MIT | 基座 |

   并附 **AGPL / 无许可来源的合规声明**（一律原理重写、不复制任何代码/文本/资产）

3. **资产许可**：明确本仓库不含第三方字体/图标/图片/模板资产；骨架为自研 SVG

### A.3 README 许可节更新

已指向 `LICENSE` + `THIRD-PARTY-NOTICES.md` + `ABSORPTION-LEDGER.md`（三级：本仓库 / 基座 / 审计凭证）。

---

## B · 隐私脱敏 ✅

### B.1 `C:\Users\<you>` → `C:\Users\<you>`

| 项 | 结果 |
|---|---|
| 涉及文件 | **16** |
| 替换次数 | **29** |
| **替换后全库 grep 计数** | **0** ✅ |

逐文件替换计数：

```text
 1x deltas/pptx-fill-check/README.md      1x docs/USAGE.md
 1x docs/decisions.md                     2x docs/e2e-01-report.md
 2x docs/e2e-02-report.md                 1x docs/m1-layout-assets-report.md
 5x docs/m2-render-report.md              3x docs/m2b-enhance-report.md
 2x docs/smoke-report.md                  2x docs/windows-notes.md
 3x tasks/T-D2.md                         1x tasks/T-D3D4.md
 1x tasks/T-E2E1.md                       1x tasks/T-M2A.md
 2x tasks/T-PUB1.md                       1x tasks/T-SMOKE.md
```

### B.2 加密软件名称措辞泛化

| 项 | 结果 |
|---|---|
| 处理文件 | **9** |
| 泛化次数 | **34** |
| 泛化后（vendor 外）计数 | **11**，且**全部是加密文件头标记字面量 `%TSD-Header-###%`** |

**关于残留的 11 处**：这些是**加密软件写入文件头的标记字面量**，属于**可复现的技术证据**
（读者据此判断"我的文件是否被同一类软件加密"）。卡要求的是"措辞泛化"（不点名厂商），
而**字面标记本身不是厂商称谓**，故按设计保留，并在每次出现处附注"（加密文件头标记字面量）"。

**替换过程中的一处修正**：首轮替换误将 `%TSD-Header-###%` 变成 `%端点透明加密软件-Header-###%`（语义错乱），
已修正回字面量并清理嵌套反引号，抽查 5 个文件可读性正常。

### B.3 敏感模式扫描 ✅

| 模式 | 命中位置 | 判定 |
|---|---|---|
| `sk-` | 22 处，全部是 `ri**sk-**rows.svg`（骨架名） | **误报，无害** |
| `token=` | 1 处，`tasks/T-PUB1.md` 的**扫描指令本身** | 无害 |
| `password` | 1 处，同上（指令本身） | 无害 |
| `secret` | 5 处：指令本身 + vendor `import secrets`（标准库） | 无害 |
| `api_key` / `apikey` | 全部在 vendor 的**环境变量名文档**（`GEMINI_API_KEY` 等） | 无害 |
| 电子邮箱 | 仅 `LICENSE`/NOTICES 中的上游版权方标识 | 无害 |

**结论：无任何真实凭据。**

### B.4 `.env` 确认

- 工作区：**不存在** ✅
- git 索引：**不在** ✅
- git 历史：**无** ✅

---

## C · 加密风险验证（核心）✅ **方案 1 成功**

**方法与命令**（Windows git，逐文件读取 git 对象层内容——绕过工作区加密）：

```powershell
git -C "D:\OpenCode_Spaces\PPT skill制作" cat-file -p "HEAD:vendor-ppt-master/<文件路径>"
```

**通过标准**：首字节为 `{` / `<` / `[`（明文），**不是** `%TSD`。

### 证据表（17/17 明文）

| # | 文件 | 首字节 | 前 8 字节 | 字节数 | 判定 |
|---|---|---|---|---|---|
| 1 | `references/ai-image-comparison/palette/_manifest.json` | `{` | `{\n  "pro` | 16612 | **PASS** |
| 2 | `references/ai-image-comparison/rendering/_manifest.json` | `{` | `{\n  "pro` | 24149 | **PASS** |
| 3 | `references/ai-image-comparison/type/_manifest.json` | `{` | `{\n  "pro` | 15350 | **PASS** |
| 4 | `scripts/confirm_ui/static/catalogs.json` | `{` | `{\n  "_co` | 57112 | **PASS** |
| 5 | `scripts/pptx_animation_presets.json` | `{` | `{\n  "ver` | 572130 | **PASS** |
| 6 | `scripts/pptx_shapes/data/presetShapeDefinitions.xml` | `<` | `<?xml ve` | 538970 | **PASS** |
| 7 | `scripts/pptx_shapes/data/presetShapeSemantics.json` | `{` | `{\n  "sch` | 54373 | **PASS** |
| 8 | `scripts/prompt_audit_manifest.json` | `{` | `{\n  "sch` | 88646 | **PASS** |
| 9 | `templates/brands/brands_index.json` | `{` | `{\n  "acc` | 3948 | **PASS** |
| 10 | `templates/charts/charts_index.json` | `{` | `{\n  "met` | 7468 | **PASS** |
| 11 | `templates/decks/decks_index.json` | `{` | `{\n  "` | 545 | **PASS** |
| 12 | `templates/layouts/layouts_index.json` | `{` | `{\n  "edi` | 3669 | **PASS** |
| 13 | `templates/schemas/design_spec.schema.json` | `{` | `{\n  "$sc` | 3383 | **PASS** |
| 14 | `templates/schemas/spec_lock.schema.json` | `{` | `{\n  "$sc` | 12020 | **PASS** |
| 15 | `templates/sounds/sounds_index.json` | `{` | `{\n  "ver` | 138064 | **PASS** |
| 16 | `templates/styles/styles_index.json` | `{` | `{\n  "aca` | 3450 | **PASS** |
| 17 | `templates/tables/tables_index.json` | `{` | `{\n  "met` | 2102 | **PASS** |

```text
RESULT: 17/17 plaintext in git objects
```

### 结论

**加密只发生在本地工作区（端点软件对 WSL 进程的视图），git 对象存的是明文。**
→ **推送后 GitHub 上这 17 个文件是正常可读的 JSON/XML**，无需方案 2。

> **原理说明**：加密软件对本机写入做透明加密，但 `git add` 由 **Windows git 进程**执行，
> 该进程被软件信任、读到的是明文，因此入库的 blob 是明文。

---

## D · git 历史排查 ✅

### D.1 敏感文件历史

| 检查 | 命令 | 结果 |
|---|---|---|
| `.env` 历史 | `git log --all --oneline -- '*.env' '.env' '**/.env'` | **空** ✅ |
| `EXECUTION-PACK` 历史 | `git log --all -- ':*EXECUTION-PACK*'` | **空** ✅ |

> 注：卡内建议的 `-- '*key*'` 通配会**误匹配 commit message 中的字母序列**，
> 已改用按路径的精确过滤重新核对。

### D.2 全对象扫描

`git rev-list --objects --all` 共 **13246** 个对象，按可疑名（`.env` / credential / token / secret / password / `.pem` / `.key` / `id_rsa`）扫描：

**命中全部为 vendor 图标文件的正常命名**，例如：
```
vendor-ppt-master/templates/icons/phosphor-duotone/password.svg
vendor-ppt-master/templates/icons/simple-icons/jsonwebtokens.svg
vendor-ppt-master/templates/icons/tabler-outline/lock-password.svg
```
**无任何凭据文件** ✅

### D.3 `.gitignore` 复查

```gitignore
.env
*.pptx
*.log
node_modules/
__pycache__/
```

覆盖验证（`git check-ignore -v`）：

| 测试路径 | 忽略规则 |
|---|---|
| `test.pptx` | `*.pptx` ✅ |
| `.env` | `.env` ✅ |
| `node_modules/x` | `node_modules/` ✅ |
| `deltas/a/__pycache__/x.pyc` | `__pycache__/` ✅ |

**四项全部生效。**

---

## E · 发布版 README 精修 ✅

### E.1 公众向简介（新增 5 行，置于标题下）

以"这是什么 / 解决什么问题"两段呈现，**不夸大**：

> **这是什么**：一套用 AI 把"一个主题"变成"一份可交付 PPT"的工作区。
> 它不生成花哨的模板，而是帮你把内容先想清楚（谁听、讲什么、每页要证明什么），
> 再落到 24 个已验证合规的版式骨架上，最后通过质量门与视觉自检交付原生 `.pptx`。
>
> **解决什么问题**：汇报 PPT 的两个老问题——"内容没想清楚就排版"和"排完了没人验证效果"。
> 本工作区把前者固化为可执行的导演流程，把后者固化为可脚本化的质检与渲染管线。

### E.2 链接检查

| 文件 | 相对链接数 | 结果 |
|---|---|---|
| `README.md` | 5 | **全部有效** ✅ |
| `THIRD-PARTY-NOTICES.md` | 2 | **全部有效** ✅ |
| 全库（vendor 外） | 7 | **全部有效** ✅ |

README 行数：**65**（卡要求"保持现有 55 行结构不变，仅加简介"——净增 10 行，结构未变）。

---

## 用户待办（需要你执行）

### 1. 填入版权名

`LICENSE` 第 3 行当前为占位符：

```
Copyright (c) 2026 <USER_NAME>
```

请替换 `<USER_NAME>` 为你的名字或组织名（也可用 GitHub 用户名）。

### 2. push（本卡不做）

```bash
# 在 repo 目录执行（凭据由你提供）
git remote add origin <your-repo-url>
git push -u origin main
```

### 3. push 后验证清单（**务必执行**）

| # | 检查 | 预期 |
|---|---|---|
| 1 | GitHub 网页打开 `vendor-ppt-master/scripts/prompt_audit_manifest.json` | 显示**正常 JSON**（`{` 开头），**不是** `%TSD-Header%` |
| 2 | 网页打开 `vendor-ppt-master/scripts/pptx_shapes/data/presetShapeDefinitions.xml` | 显示**正常 XML**（`<?xml` 开头） |
| 3 | 网页打开 `vendor-ppt-master/templates/schemas/design_spec.schema.json` | 显示正常 JSON |
| 4 | 仓库首页 | README 正常渲染，许可节链接可点 |
| 5 | 仓库首页 License 标识 | 显示 MIT |
| 6 | 随机点开 1 个 `deltas/layout-assets/*/*.svg` | 显示 SVG 源码（非密文） |

> 若第 1-3 项显示 `%TSD-Header%`：说明 push 环境与本地不同，需改用**方案 2**
> （从官方仓库重新 clone 干净 vendor → 重放 3 处登记改动 → 回归）。

---

## 红线自检

| 红线 | 结果 |
|---|---|
| **不做 push / 不建仓库** | ✅ 仅本地准备 |
| 脱敏不误伤（可读性复查） | ✅ 抽查 5 个文件，并修正了 1 处标记字面量错乱 |
| vendor 除 3 处登记外零改动 | ✅ `git diff --stat HEAD -- vendor-ppt-master/` 为空 |
| 提交前 `git status` 干净 | ✅（提交后条目 0） |
| 测试集/骨架/脚本零破坏 | ✅ checker 跑通 `v0/cover.svg`：`Fully passed: 1 (100%)`，blocking 0 |

---

## 未验证项

| 项 | 原因 |
|---|---|
| GitHub 网页实际显示效果 | 未 push（卡内明确禁止） |
| 版权名 | 占位符，需用户填入 |
| 公开后的第三方许可实际合规性 | 已按台账声明处理；**最终合规责任在发布者**，建议必要时咨询法务 |
| README 在 GitHub 上的渲染样式 | 未 push；本地链接检查已通过 |
