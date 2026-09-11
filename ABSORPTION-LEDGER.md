# Absorption Ledger

> 用途：每一条借鉴都必须入账；本台账是**合规审计凭证**（与许可筛查双向链接）。
> 规则：任何"从外部 skill 学到的东西"未入账 = 视为未发生；入账标准见下方模板。

## 台账条目（每条一行）

| # | 来源 skill (仓库+许可) | 吸收内容 | 怎么改写 | 落盘文件（实际） | 许可处理 |
|---|---|---|---|---|---|
| A-001 | ppt-master 5.0.0 (MIT, hugohe3/ppt-master) | 路由式入口：92 行承载"路由+全局纪律"，其余按需加载；routing.md 为唯一路由权威 | 引用基座 + 增量挂载（§8 Director） | `vendor-ppt-master/`（整体复制，LICENSE 保留）、`vendor-ppt-master/workflows/routing.md`（+§8） | MIT；保留版权声明 |
| A-002 | ppt-master (MIT) | 原生 PPTX 对象映射 + executor 系列构建器 | 引用（不复制，直接使用 base 文件） | `vendor-ppt-master/references/pptx-structure-interface.md`、`references/executor-*.md` | MIT |
| A-003 | ppt-master (MIT) | batch_validate 批量校验 + failure-recovery 失败恢复 | 引用（原样使用） | `vendor-ppt-master/scripts/batch_validate.py`、`workflows/governance/failure-recovery.md` | MIT |
| A-004 | ppt-master (MIT) | visual-styles 20+ 风格 + create-style/create-layout 创作流程 | 引用（原样使用） | `vendor-ppt-master/references/visual-styles/`、`workflows/create-template/` | MIT |
| A-005 | GordenPPTSkill 源码 (MIT；templates/ 非商用) | 出框检测（按文本框容量）+ 同级标题字号一致性 + 渲染审查思路 | 改写（读源码自写） | `deltas/pptx-fill-check/capacity.py`、`detect_overflow.py`、`check_title_consistency.py`、`README.md` | 源码 MIT；templates/ 零接触 |
| A-006 | guizang (AGPL-3.0, op7418/guizang-ppt-skill) | 版式"登记即锁"+色板纪律+内容形状决定版式+清单分级（P0-P3 四级） | 按原理重写，不引用任何文本/代码 | `deltas/style-lock.md` | AGPL 不合并、不引用；吸收对照表内置于文档 |
| A-007 | ppt-director（无 LICENSE = 默认保留版权） | 导演式阶段序列 + 标准交付文档 + 页面结构导演稿（区域词清洗）+ registry 机制 | 按原理重写 | `deltas/director.md` | 无许可：只学原理，不引用文档 |
| A-008 | dashi-ppt（无 LICENSE；内部包 MIT） | schema 理念：先 JSON 计划再生成、内容/视觉分离、按容量选版式 | 按原理重写，参考形状不复制文件 | （设计依据，未直接落盘；见 `deltas/director.md` §5 映射） | 无许可：只学原理 |
| A-009 | frontend-slides (MIT, Zara Zhang) | 固定舞台规则 + 内容密度模式 + 渐进披露 | 改写 | 留待 M2 验稿器（HTML 预览）；当前未落盘 | MIT |
| A-010 | html-ppt (MIT, lewis) | 逐字稿 3 规则（提示信号/150-300 字/口语化） | 改写（PPTX 版为备注区/提词文档双轨） | `deltas/presenter-mode.md`（P-1/P-2/P-3） | MIT |
| A-011 | beautiful-html-templates (MIT, Zara Zhang) | 模板包组织：index.json + screenshots 预览范式 | 只学结构 | 留待 M2 验稿器；当前未落盘 | MIT |

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
