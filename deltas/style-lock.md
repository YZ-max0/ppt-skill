# D-3 Style Lock —— 锁定版式与主题色纪律（原理重写版）

> 依据：guizang 版式锁 / 主题色预设 / 检查清单原理（AGPL-3.0，**只学原理、不引原文**）。
> 定位：Generate PPTX 生成期的**设计纪律**，供 base 管线在执行期按需加载。
> 冲突处理：`design_spec.md` + `spec_lock.md` 仍是唯一规划权威；本文件只规定"生成期不得做什么"。
> 吸收对照见文末。

## 1. 锁定语义（PPTX 语境）

"锁"= 在 Design Spec 的锁定门（Gate 2）之后，本 deck 的设计决策不再新增。
三条锁定对象：

| 锁定对象 | 锁定物 | base 锚点 |
|---|---|---|
| 版式集 | 本 deck 允许使用的版式清单 | `spec_lock.md` 的 `page_pptx_layouts` / `page_layouts`；flat 模式下为页面结构契约 |
| 主题色 | 语义色角色与其取值 | `spec_lock.md` 的 `colors` |
| 视觉风格 | 单一 `visual_style`（+ 渲染族） | `design_spec §VII` + `spec_lock` |

**硬规则 L-0（反向纪律）**：内容形状决定版式，不是版式决定内容。
先确定一页要表达的关系（分层/流程/对比/递进/矩阵/账本），再从登记集挑承载该关系的版式。
禁止"先选好看的版式，再编内容硬塞进去"。这条优先于本文其余所有条款。

## 2. 锁版式

**L-1 登记即用**：每页在生成前必须归入 `spec_lock` 已声明的版式键之一（`page_pptx_layouts`，或 flat 模式的页面结构契约）。
生成期不得发明未登记的版式键。

**L-2 禁止临时发明**：不得在 Executor 阶段新增 `P23`/`P24` 式的未登记页型；
需要新页型时，必须回到 Strategist 修 `design_spec` 并重新过锁门（Spec repair），而不是在生成期就地创造。

**L-3 图片槽位与比例绑定**：先定槽位几何，再定图片比例；同一组图片必须同高同宽、同一容器背景。
槽位比例一旦登记，不得由图片自身的原始比例反向决定容器尺寸。

**L-4 结构升级禁令**：free-design / brand-only / style-only 产出一律保持 `pptx_structure.mode: flat`。
重复出现的页面局部对象**不会**触发 `structured` 提升、Master/Layout 推断或占位符推断。

**L-5 模板复用范围**：`template_reuse_scope: mirror|layout` 的页面必须从完整版式骨架起步，保留继承的可见对象与 Master/Layout 身份；
仅 `layout` 且 Design Spec 已授权时，才允许在**不变的槽位边界内**做承载文本回流。
Executor 不得就地修改 `spec_lock`。

## 3. 锁主题色

**L-6 预设内取值**：色板只能来自已确认的语义色角色集合（`design_spec.colors` / `spec_lock.colors`，含 fallback 色板）。
**禁止自定义 hex**：生成期遇到"想要某个颜色"的诉求，不得直接写新 hex，必须回到已声明的角色里选，或回到锁门修 Design Spec。

**L-7 单一锚点色**：一份 deck 只保留一个高饱和强调色锚点。
禁止混搭两个及以上高饱和色作强调（例如两种亮色同屏）。
强调色的对比前景色（深底配浅字 / 浅底配深字）必须按已声明角色取，不得就地试色。

**L-8 不做的事**：不给强调色加渐变、阴影、圆角或透明度（除非已锁的风格本身要求）。
灰阶与底色角色跨主题统一（已锁的中间灰阶），不得顺手改成纯黑或纯白。

**L-9 主题节奏**：用 `page_rhythm`（`anchor|dense|breathing`）控制明暗与密度交替。
- 禁止连续 3 页以上同节奏、同明暗取向
- anchor（封面/章节/关键结论）与 dense（证据/细节）应交替出现
- 节奏是**页级**声明，不是生成期即兴发挥

**L-10 风格唯一**：一份 deck 只解析一个 `visual_style`（或一个 `custom` 行为）。
Style 不携带 HEX、不定义色板；它只决定"已锁颜色如何参与构图"。
禁止在生成期换风格，或在同 deck 混用两套形状语言。

## 4. 校验对接

| 条款 | 检测方式 | 建议挂载点 |
|---|---|---|
| L-1 登记即用 | 可自动检测：每页版式键是否在 lock 声明集内 | 扩展 `deltas/pptx-fill-check` 或 base `batch_validate.py` |
| L-2 禁止临时发明 | 可自动检测：出现未声明版式键/页型即报错 | 同上 |
| L-3 槽位比例绑定 | 可自动检测：同组图片容器宽高比是否一致 | 扩展 D-2 脚本 |
| L-4 结构升级禁令 | 可自动检测：flat 产物是否含结构化映射段 | base `svg_quality_checker.py` 已有结构性校验，建议复用 |
| L-5 模板复用范围 | 半自动：骨架对象是否保留可 diff；语义变更需人工 | 人工 + 质量门 |
| L-6 禁止自定义 hex | 可自动检测：产物颜色是否全部落在 lock `colors` 声明集 | 扩展校验器 |
| L-7 单一锚点色 | 半自动：统计高饱和色种类数；"高饱和"阈值需人工确认 | 自动统计 + 人工判定 |
| L-8 不做的事 | 半自动：渐变/阴影/圆角语法可 grep；"已锁风格是否允许"需人工 | grep + 人工 |
| L-9 主题节奏 | 可自动检测：`page_rhythm` 连续值与交替规则 | 扩展校验器 |
| L-10 风格唯一 | 可自动检测：`visual_style` 在产物中是否唯一 | base 校验器 |
| L-0 反向纪律 | 人工检查：每页"内容关系 → 版式"的对应是否成立 | 人工（Strategist/评审） |

**校验结果分级**（吸收台账既有分级约定）：结构违规 = 阻断；节奏/密度建议 = 提示；
打磨类（间距、字重微调）= 咨询。禁止把可自动检测的硬规则降级为"建议"。

## 5. 与 base 的集成

**落点一：色彩**——`visual-styles/` 明确"不带 HEX、不定义色板"，D-3 的色纪律因此锚定
`design_spec.colors` + `spec_lock.colors`，而不是风格文件。

**落点二：版式**——flat 产物（free-design / style-only / brand-only）用页面结构契约约束；
structured 产物用 `page_pptx_layouts` / `page_layouts` + `pptx_masters` / `pptx_layouts` 约束。
两种模式下 L-1/L-2 同样生效，只是"登记集"的载体不同。

**落点三：节奏**——复用 base 已存在的 `page_rhythm` 字段（`anchor|dense|breathing`），
不新增字段。

**落点四：执行期加载**——本文件是"生成期纪律"，与 base 的 `executor-*` 同层按需加载；
不进入 `SKILL.md` 的强制加载顺序，也不修改 vendor 任何文件。

## 吸收对照

| 借鉴原理 | 来源（许可） | 去向条款 | 改写方式 |
|---|---|---|---|
| 版式登记集、"未登记版式=硬失败" | guizang swiss-layout-lock（AGPL-3.0） | L-1 / L-2 | 按原理重写（载体改为 `spec_lock` 版式键） |
| 图片槽位与生成比例绑定 | guizang swiss-layout-lock（AGPL-3.0） | L-3 | 按原理重写 |
| 颜色只从预设挑、禁自定义 hex、禁混搭 | guizang themes-swiss（AGPL-3.0） | L-6 / L-7 / L-8 | 按原理重写（锚点改为 base 语义色角色） |
| "先选版式再编内容"是反向纪律 | guizang checklist 0-S 系列（AGPL-3.0） | L-0 | 按原理重写 |
| 检查项分级（阻断/建议） | guizang checklist（AGPL-3.0） | §4 校验分级 | 按原理重写（对齐本 repo 既有台账分级） |
| flat/structured 结构边界、`page_rhythm` | base vendor-ppt-master（MIT） | L-4 / L-5 / L-9 | 引用（base 既有字段，直接锚定） |

> 合规声明：本文档不含 guizang 任何原文句子或表格结构；所有条款为原理级重写。
> 台账登记见 `ABSORPTION-LEDGER.md`（A-006）。
