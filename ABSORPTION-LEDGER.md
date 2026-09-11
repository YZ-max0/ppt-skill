# Absorption Ledger

> 用途：每一条借鉴都必须入账；本台账是**合规审计凭证**（与许可筛查双向链接）。
> 规则：任何"从外部 skill 学到的东西"未入账 = 视为未发生；入账标准见下方模板。

## 台账条目（每条一行）

| # | 来源 skill (仓库+许可) | 吸收内容 | 怎么改写 | 落盘文件 | 许可处理 |
|---|---|---|---|---|---|
| A-001 | ppt-master 5.0.0 (MIT, hugohe3/ppt-master) | 入口路由：92 行承载"路由+全局纪律"，其余按需加载；`workflows/routing.md` 为唯一路由权威 | 改写（结构保留、文案自写） | `SKILL.md`、`workflows/routing.md` | MIT；保留原版权声明即可 |
| A-002 | ppt-master (MIT) | `references/pptx-structure-interface.md` 原生 PPTX 对象映射 + `references/executor-*.md` 结构/图表/可视化构建器 | 引用（保留版权声明） | `references/pptx/` | MIT |
| A-003 | ppt-master (MIT) | `scripts/batch_validate.py` 批量校验 + `workflows/governance/failure-recovery.md` 失败恢复 | 引用/改写 | `scripts/validate.py` | MIT |
| A-004 | ppt-master (MIT) | `references/visual-styles/*`（20+ 风格，swiss/zine/editorial 等）+ `create-style.md`/`create-layout.md` 模板创作流程 | 引用（可直接用作设计层资产） | `references/styles/` | MIT；注意风格文案中可能含第三方命名，入库前校验 |
| A-005 | GordenPPTSkill 源码 (MIT；templates/ 非商用) | 出框检测（按文本框尺寸）+ 同级标题字号一致校验 + `build_pptx.py` edits.json 填充管线 + `render_slides.py` 渲染 PNG 审查 | 改写（读源码自写；模板资产一律不碰） | `scripts/pptx/fill.py`、`scripts/pptx/render-preview.py` | 源码 MIT；该 skill 模板目录禁止入库 |
| A-006 | guizang (AGPL-3.0, op7418/guizang-ppt-skill) | `references/checklist.md` P0/P1/P2 分级 + `layouts.md` 版式库写法 + "锁定版式+锁主题色"设计哲学 + 演前检查列表 | 按原理重写，不引用任何文本/代码 | `references/checklist.md`、`references/layouts.md` | AGPL 不合并、不引用 |
| A-007 | ppt-director（无 LICENSE = 默认保留版权） | 阶段判断（A 灵感/B 内容/B2 视觉导演/E 迭代）+ 标准交付文档 + 页面结构导演稿（含区域词清洗规则）+ registry 注册表机制（audience/reviewer/style/toolchain） | 按原理重写 | `workflows/director.md`、`references/registry.md` | 无许可：只学原理，不引用文档 |
| A-008 | dashi-ppt（无 LICENSE；内部包 MIT） | schema 设计理念：先 JSON 计划再生成、内容/视觉分离（content vs fillPlan/props）、按容量选版式（layout-query 理念）、3 模板+1 bespoke 方案 | 按原理重写，参考形状不复制文件 | `schemas/slide.schema.json`（设计依据） | 无许可：只学原理 |
| A-009 | frontend-slides (MIT, Zara Zhang) | 固定 1920×1080 舞台规则（不重排内容）+ 内容密度模式（reading vs speaking）+ 渐进披露（先 preview 后 design） | 改写 | `references/fixed-stage.md`、`references/density.md` | MIT |
| A-010 | html-ppt (MIT, lewis) | 演讲者模式：逐字稿 3 规则（提示信号/150-300 字/口语化）+ 4 卡弹窗（当前/下一/逐字稿/计时） | 改写（PPTX 版为备注区/演讲稿双轨） | `references/presenter-mode.md` | MIT |
| A-011 | beautiful-html-templates (MIT, Zara Zhang) | 模板包组织：`index.json` 索引 + 每模板 `screenshots/*.png` 预览的"可看图选模板"范式 | 只学结构 | `references/template-index.md` | MIT |

## 字段说明

- **来源**：仓库 URL + 许可类型，许可写许可证全名（MIT / AGPL-3.0 / 无许可）
- **怎么改写**，三选一：
  - `引用`：开源兼容许可（或 MIT），直接引用并保留版权声明
  - `改写`：结构保留、实现自写（限宽松许可）
  - `按原理重写`：只吸收设计原理，不参考任何代码/文本（AGPL 与**无许可**源统一按此项处理）
- **落盘文件**：本 repo 内路径
- **许可处理**：与 Step 3 许可筛查结论一致，写"结论 + 依据"

## 合规审计流程

1. 入库时：填台账 → 许可筛查反向核对（双向链接：台账列 → 许可结论）
2. 分享前：全表跑一遍 `许可检查`，任何 `按原理重写` 之外来自 AGPL/无许可源的条目 = 发布阻断项
3. 资产（字体/图标/图片/模板）单独建 `assets/ASSETS-LICENSE.md` 清单，不受仓库许可代管

## 红线

- 禁止：把 AGPL/无许可源的文件或原文拷进本 repo 任何目录（含 references、scripts）
- 禁止：Gorden `templates/` 任何 .pptx 或图片进入本 repo；即使 MIT 源码入库，其模板目录整体排除
- 例外：仅用于学习分析、从不进入产物链路的材料，写成一条"学习笔记"归档即可，不入台账

## 待定

- A-002/A-003/A-004 若最终采用"ppt-master 为基座"方案，吸收级别可能从"引用"降级为"依赖+自定义"（见 CONTRACT 决策记录）
