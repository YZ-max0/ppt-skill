# 任务卡 T-D6 · 将 Director 挂载进基座路由（P1 · 预计 30 分钟）

指挥官：opencode ｜ 执行者：待指派 ｜ 版本：v1.0

## 背景

基座 `vendor-ppt-master` 已落地（MIT 原样）。D-1 导演式工作流文档 `deltas/director.md`（中文）已定稿。
本任务把它作为 **Generate PPTX 的可选 Pre-spec 输入阶段**挂进路由，避免"基座不知道还有导演环节"。

## 唯一授权改动

编辑 `D:\OpenCode_Spaces\PPT skill制作\vendor-ppt-master\workflows\routing.md`：
**在文件末尾追加一节 §6 "Director Pre-spec Input Stage"（沿用全文英文），结构如下：**

- 触发条件（逐条列表，对应 director.md §1 路线裁决的四行：仅主题/重要汇报≥10页/快速通道/已成稿走其他路由）
- 挂载位置：应注明"Director 位于 Generate PPTX 的 Step 0（Spec 之前），产出作为 Strategist 的入料；**design_spec.md + spec_lock.md 仍是唯一规划权威**"——这是集成契约，必须写下
- 引用路径：`../../deltas/director.md`（从 vendor-ppt-master/workflows/ 出发的相对路径）
- 一句边界声明：不新增第 5 条顶层路由；§1-§5 全部行内容不动

## 硬约束（违反即退回）

1. 只允许**追加**，不允许修改/删除 §1-§5 任何已有行文
2. 不新增顶层路由（`One artifact lifecycle` 规则保持 4 条）
3. 全文英文，与既有 Markdown 表格/列表风格一致
4. 不得改动 vendored 内任何其他文件（含 SKILL.md 的 Mandatory Load Order——routing.md 本身就是加载权威，新增条件在 §6 足够）

## 执行前必读（按顺序）

1. `vendor-ppt-master/workflows/routing.md`（全文，弄清 §3 风格与措辞）
2. `deltas/director.md`（§1 路线裁决、§6 冲突决策）
3. `vendor-ppt-master/workflows/index.md`（确认 §3 Maintenance Rules：顶层路由注册规则，避免与"五层"纪律冲突）

## 验收标准（自检全 Yes 才交付）

- [ ] 追加节完整含：触发器 / 挂载位置+唯一权威声明 / 相对路径引用 / 不新增路由声明
- [ ] `git -C "D:\OpenCode_Spaces\PPT skill制作" diff -- vendor-ppt-master/workflows/routing.md` 显示只有纯追加
- [ ] 读一遍确认：Director 与既有无冲突（尤其是 §3 的"Spec/Confirm UI"门在 Director 之后出现顺序正确）

## 异议区（交付时附上，可选）

如你认为"Direct 挂载"与本卡有以下任一冲突，请写《建议》一节并给理由（我会与指挥官对质）：
1. 触发器判定是否应当更早/更晚
2. 是否应同时更新 `SKILL.md` 的 Mandatory Load Order
3. 追加是否符合 base 维护者视角的"五层纪律"（index.md §3）
