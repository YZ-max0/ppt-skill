---
name: ppt-skill
description: >
  用 AI 把"一个主题"做成可交付的原生 .pptx：先想清楚给谁讲、每页要证明什么，
  再落到 29 个已验证合规的版式骨架上，最后过四道自动质检 + 渲染目视。
  当用户提出要"做一份 PPT / 汇报 / 述职 / 方案 / 路演 BP / 技术分享 / 评审答辩 / 周报"，
  或要求美化、填充、增强已有 PPTX 时使用。
  也适用于用户只给一个主题、甚至只说一句话的场景。
license: MIT
metadata:
  version: "1.0.0"
  工作语言: 中文（用户用其他语言时跟随用户）
  base: "vendor-ppt-master 5.0.0 (MIT, Copyright (c) 2025-2026 Hugo He)"
  repository: "https://github.com/YZ-max0/ppt-skill"
---

# PPT Skill

本 skill = **MIT 基座（`vendor-ppt-master/`，只读）+ 仓库定制层（`deltas/`）**。
定制层提供：发起引导协议、导演式工作流、29 个版式骨架、图表/表格生成器、
四道自动质检、渲染预览管线。

---

## 0. 路径纪律（硬规则，先读）

**paths before commands**：把"包含本文件的绝对目录"记为 `${SKILL_DIR}`，
此后每次工具调用都用 `${SKILL_DIR}/...` 展开，**不要 `cd`、不要依赖当前工作目录、
不要假设是 git checkout**。拿不到该目录就直接问用户，**不要搜索或猜**。

> 本 skill 同时提供 `AGENTS.md`（指向本文件），供按该约定发现入口的 agent 使用。
> **两份内容以本文件为准**，`AGENTS.md` 只做转发。

---

## 1. 强制加载顺序

1. 读本文件。
2. **读 `${SKILL_DIR}/deltas/intake-guide.md`** —— 这是**发起引导协议**，
   定义"怎么问、怎么定路线、默认值是什么"。**不得跳过**。
3. 按引导协议与用户的对话，确定走**「尽可能好」**还是**「要快」**分支。
4. 按 §2 的路由表，**只读**该分支需要的文档。
5. 按所读文档执行；**不得跨阶段打包**（见 §4）。

> 基座自身还有一层路由（`${SKILL_DIR}/vendor-ppt-master/SKILL.md`）。
> 当引导协议判定需要"Fill Native / Enhance Native / Image to PPTX"等基座专有路由时，
> 再读它并按它的路由表走；否则**不必读**（避免上下文膨胀）。

---

## 2. 路由表：按分支只读这些

| 分支 | 必读 | 按需读 |
|---|---|---|
| **尽可能好**（默认） | `deltas/intake-guide.md`（§2 质量协议）<br>`docs/USAGE.md`（逐步命令） | 页数 >12 或重要场景 → `deltas/director.md`（完整流程）<br>视觉 → `deltas/layout-assets/v0/CONTRACT.md` + `v2/CONTRACT.md` + `v3/CONTRACT.md`<br>图表/表格 → `deltas/chart-fill/README.md`、`deltas/table-fill/README.md`<br>配图 → `docs/image-strategy.md`<br>要讲 → `deltas/presenter-mode.md` |
| **要快** | `deltas/intake-guide.md`（§3 轻量通道）<br>`docs/USAGE.md` §2 | `docs/QUALITY-TIERS.md`（档位与耗时） |

**质量档位对照**（不确定时读）→ `${SKILL_DIR}/docs/QUALITY-TIERS.md`

**绝不能省的一步**：无论哪个分支，**质检都必须跑**（§4.2）。

---

## 3. 与用户对话（摘要，完整见 intake-guide）

1. **先问一句**：「这份 PPT：是要快，还是要尽可能做好？」（默认：尽可能好）
2. 用**场景语言**提问，禁用内部术语（不说"导演式/骨架/视觉增强/受众卡"）
3. 每个问题都给"**其他，你来定**"选项；用户跳过 → 用默认值 + **标注假设**
4. **一次最多 3 问**；能推断的（页数/时长/风格）**不问**，直接默认并注明
5. 用户一句话就够，**不要要求用户填模板**（模板是"精确模式"，见 `docs/USAGE.md` §8.2）

---

## 4. 执行纪律

### 4.1 阶段与门禁

- **串行执行**：按所读文档的步骤顺序走，不跳步、不提前准备后续阶段的产物
- **遇到阻断门就停**：需要用户确认处（视觉候选选择、方向确认）**等用户明确回答**，
  不替用户决定
- **修正后必须重跑质检**：对已过检的 SVG 做任何改动（改标题/换数字/加行），
  都要重跑 §4.2 的质检流程 —— 文字变长会破坏几何（实测踩过）

### 4.2 质检（任何分支都不得省）

```powershell
python "${SKILL_DIR}/vendor-ppt-master/scripts/svg_quality_checker.py" "<项目路径>" --quick-generate --stage final --json
python "${SKILL_DIR}/deltas/layout-assets/check_hygiene.py"   "<项目>\svg_output"
python "${SKILL_DIR}/deltas/layout-assets/check_overlap.py"   "<项目>\svg_output"
# 导出后：
python "${SKILL_DIR}/deltas/pptx-fill-check/detect_overflow.py"           "<导出.pptx>"
python "${SKILL_DIR}/deltas/pptx-fill-check/check_title_consistency.py"   "<导出.pptx>"
```

**全部要求 exit 0 / 零阻断项**。四道自动闸**查不出内容错误**（语义、事实、数字矛盾），
所以「尽可能好」分支还要求**渲染目视**：

```powershell
python "${SKILL_DIR}/deltas/render-preview/render_png.py" "<导出.pptx>" -o "<输出目录>"
```

**拿到 contact sheet 后必须交给用户看**（或按其反馈复核）—— 人眼是最后一道闸。

---

## 5. 环境硬约束（否则必踩坑）

| # | 约束 |
|---|---|
| 1 | **Windows 上用 `python`，不是 `python3`**（基座文档里的 `python3` = 本机 `python`） |
| 2 | `project_manager.py init` **必须带 `--dir`**，否则项目落到默认 `projects/` 污染仓库 |
| 3 | 填充后断言产物中 `【` 计数 = **0** |
| 4 | 渲染产物可能被端点加密软件加密 → **图片处理必须走 Windows 进程**；跨侧读图会得到密文 |
| 5 | 控制台中文乱码 ≠ 数据损坏：**看文件字节，别看屏幕** |
| 6 | 校验行数/字符数用**字节级统计**，不要用 PowerShell `Get-Content`（受默认编码影响会少计） |

完整环境说明 → `${SKILL_DIR}/docs/windows-notes.md`（W-1 ~ W-8）

---

## 6. 仓库地图

| 路径 | 内容 |
|---|---|
| `deltas/intake-guide.md` | **发起引导协议**（入口必读） |
| `docs/USAGE.md` | 逐步操作命令（真实命令 + 预期输出） |
| `docs/QUALITY-TIERS.md` | 三档质量与耗时对照 |
| `deltas/director.md` | 导演式工作流（A/B/B2/B3/C 五阶段） |
| `deltas/layout-assets/` | **29 个版式骨架**（v0×6 / v1×12 / v2×8 / v3×3）+ 填写契约 |
| `deltas/chart-fill/` | 图表生成器（9 类）+ v2 坐标重算 + 读回验证 |
| `deltas/table-fill/` | 表格生成器（原生表格）+ 读回验证 |
| `deltas/pptx-fill-check/` | 出框检测 + 标题一致性 |
| `deltas/render-preview/` | pptx → PNG + contact sheet |
| `deltas/presenter-mode.md` | 逐字稿 / 提词卡契约 |
| `docs/image-strategy.md` | 图片素材策略（来源/比例/限制） |
| `vendor-ppt-master/` | 基座 ppt-master 5.0.0（MIT，**只读，禁止修改**） |

---

## 7. 边界

- **不改 `vendor-ppt-master/`**。需要新增能力时写在 `deltas/`，或用生成器产出合规 SVG。
- **不产出图片素材**：图片位已支持（v3 三个骨架），但素材需用户提供或程序生成
  （搜图/生图需 API key 与外网，本机默认不可用）。
- **不承诺像素级还原**：骨架是固定几何，填充文本显著长于占位文案时会触发质检报错，
  此时应删减文案或换骨架，**而不是硬压坐标**。
- **产物放临时目录**，不要留在仓库内（`.gitignore` 已忽略 `*.pptx`）。
