# 任务卡 T-D3D4 · Style Lock 与 Presenter Mode 文档（P1 · 预计 2-3 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：探针通过后执行

## 背景

M0 最后两块文档增量。契约场景 = 重要汇报/演讲（原生 PPTX 优先）。
两份文档都是"生成期纪律"，供未来 base 管线执行时按需加载。

## 输入材料（只读）

| 材料 | 路径 | 用途 |
|---|---|---|
| guizang checklist | `C:\Users\EDY\.workbuddy\skills\guizang-ppt-skill\references\checklist.md` | P0-P3 分级结构原理 |
| guizang 版式锁 | ...`\references\swiss-layout-lock.md` | "登记即锁"机制原理 |
| guizang 主题色 | ...`\references\themes-swiss.md` | 色板纪律原理（禁自定义/禁混搭） |
| guizang 演讲者 | ...`\references\presenter-mode.md` | 数据契约/稳定 ID/排练原理 |
| 本国定稿 | `D:\OpenCode_Spaces\PPT skill制作\deltas\director.md` | 内容/视觉分离纪律、集成契约 |
| base 风格体系 | `vendor-ppt-master\references\visual-styles\` + `workflows\create-template\create-style.md` | D-3 的落点（版式/风格如何在 base 表达） |
| base 备注体系 | `vendor-ppt-master\references\executor-notes.md` + `workflows\stages\generate-audio.md` | D-4 的落点（speaker notes 如何进 PPTX） |

**指挥官转述的 guizang 深读要点**（原理级，可直接用）：
- 清单四级：P0 慎败 / P1 节奏 / P2 打磨 / P3 操作细节
- 锁两条硬条款：① 颜色只从预设挑、禁自定义 hex、禁混搭高亮色；② 正文版式必须先登记后使用，未登记版式 = 校验器硬失败
- 反向纪律："绝不能先选版式再编内容硬塞"——内容形状决定版式选择
- 主题节奏：禁连续 3 页同主题；hero/非 hero 交替
- 演讲者数据契约：`minutes`（讲述计划）与 `autoAdvanceSeconds`（播放行为）必须分离；总时长 ≤ 现场 90%；缺失字段隐藏不猜；稳定 slug 主键（禁页码）；排练记录只做汇总不做 AI 评分

## 交付物

### 1. `deltas/style-lock.md`（≤200 行）

- **锁版式**（PPTX 语境）：风格包选定即锁定；本 deck 内版式只从登记集选择；禁止生成期临时发明新版式；图片槽位比例预登记；"内容形状决定版式"反向纪律
- **锁主题色**：色板从预设选；禁自定义 hex；禁混搭高亮色；主题节奏规则（light/dark/hero 交替、禁连续 3 页同主题）
- **校验对接**：每条规则标「可自动检测 / 人工检查」两栏；可自动检测的写明建议挂载点（扩展 D-2 脚本 or base batch_validate）
- **与 base 集成**：锚定 `visual-styles/` + `create-style.md`，说明纪律如何施加于 base 的 flat/structured 产出

### 2. `deltas/presenter-mode.md`（≤200 行）

- **双轨**：默认提词卡（要点式）；明确要求才写逐字稿
- **逐字稿 3 规则**（吸收 html-ppt MIT 原理）：提示信号非讲稿 / 每页 150-300 字 / 口语非书面语
- **必备字段结构**：`id / title / purpose / talk(3-5条) / transition` + 可选（`minutes / cue / interaction / delivery / fallback / pronunciation`）；缺失隐藏不猜
- **稳定 ID 纪律**：页面 slug 主键，禁页码
- **承载映射（PPTX 语境）**：备注区（base executor-notes 链路）+ 可选独立提词文档（markdown）；HTML 观众屏同步类机制标注"不适用/留给 M2 验稿器"
- **排练数据契约**：minutes vs autoAdvance 分离；≤90% 规则；汇总不评分
- **能力边界**：无实时字幕/语音转写/AI 教练

## 硬约束

1. AGPL 原理重写：**禁止任何原文句子/表格结构照搬**；两文档末尾各附「吸收对照」表（借鉴原理 → 来源 → 去向条款号）
2. PPTX 语境优先：一切机制必须能映射到 base 的能力（speaker notes / export / enhance）；HTML-only 机制要么转化要么显式标注不适用
3. 只新增 `deltas/style-lock.md`、`deltas/presenter-mode.md` 两个文件；其他任何文件零触碰（vendor 零改动）
4. 中文写；精悍：每份 ≤200 行，能删的删

## 验收标准

- [ ] 两文件产出，各 ≤200 行，含吸收对照表
- [ ] style-lock 每条规则有「可自动检测/人工检查」标注
- [ ] presenter-mode 的字段结构/ID/排练契约齐全，PPTX 承载路径明确（引用 base 文件路径）
- [ ] `git status` 差异仅两个新文件（探针/commit 完成后跑）
- [ ] 无 AGPL 原文痕迹：自查一遍，不确定的句子改写

## 异议区（交付时附）

1. "版式登记集"在 PPTX 语境下应长什么样（一组 layout workspace？还是冻结的版式函数清单？）——如你有更优表达写建议
2. 逐字稿与 base `executor-notes` 的字段映射是否需要新增约定（如 notes 前置 marker）
3. 两文档是否应合并为一份 + 两个章节（如你认为更利于加载）
