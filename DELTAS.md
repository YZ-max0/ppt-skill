# DELTAS — 定制蓝图（base = vendor-ppt-master 5.0.0, MIT）

> 本文件是本 repo 定制的唯一权威。所有增量（D-*）从这里调度。
> 基座纪律（base SKILL.md：不建 tests/、不做通用工程结构）继续生效于 skill 包内部；repo 级 tests/、docs/ 与 vendor/ 平级，互不侵入。

## 增量清单

| ID | 增量 | 来源（许可） | 落点 | 状态 |
|---|---|---|---|---|
| D-1 | 导演式工作流：受众画像→内容打磨→页面结构导演稿→映射进 base Generate 的 Design Spec 之前 | ppt-director 原理（无许可） | `deltas/director.md` | ✅ 已定稿 |
| D-2 | 填充质检：按文本框尺寸出框检测 + 同级标题字号一致校验（Fill Native PPTX 路由） | Gorden 源码（MIT） | `deltas/pptx-fill-check/` | 未开始 |
| D-3 | 锁定版式纪律：版式登记即锁（禁未登记版式、禁自定义色）——注意 guizang 清单实为 **P0-P3 四级** | guizang 原理（AGPL） | `deltas/style-lock.md` | 未开始 |
| D-4 | 演讲者模式：逐字稿 3 规则 + 提词卡/逐字稿双轨 + 稳定 ID + 排练数据契约 | html-ppt（MIT）+ guizang presenter-mode 原理 | `deltas/presenter-mode.md` | 未开始 |
| D-5 | 质量闭环：测试集 v1 + golden samples + 失败模式编号（C-XXX） | 自有设计 | `tests/`（v1 已落盘）、`docs/failures.md` | 部分完成 |
| D-6 | 路由扩展：`director` 作为 Generate PPTX 的 **Pre-spec 输入阶段**（不新增第 5 条顶层路由） | D-1 | `vendor-ppt-master/workflows/routing.md` 增量条款 | 未开始 |

## 定制规则

1. **不改 base 源码原则性内容**；增量为：(a) 挂载条款（routing.md 增量段），或 (b) repo 级 deltas/ 文档。base 文件如确需修改，先记录到 docs/decisions.md。
2. **许可边界**：任何 base 仓库外文本/代码进入 repo，先履行 ABSORPTION-LEDGER.md 台账 + 许可处理（AGPL/无许可 = 原理重写，禁止原文拷入）。
3. **Windows 运行前提**：base 文档中的 `python3` 在本机 = `python`；Image-to-PPTX/音频/生成等 Codex-support 或外部 API 功能标注"受限"。
4. **验收标准**（每项增量完成时）：
   - 增量功能在测试集 v1 全部输入上跑通无 P0 失败
   - 对应的失败模式已编号并写入 docs/failures.md
   - 台账/许可无新风险

## 已知冲突与处理

| 冲突 | 处理 |
|---|---|
| base SKILL.md 禁止 tests/ | repo 级 tests/ 与 vendor/ 平级，不进入 skill 包 |
| base 生成音视频/图片依赖外部 API | 主链路（Generate Default / Fill Native / Enhance）python3 本地可跑；外部依赖标注受限 |
| base Routing 是唯一权威 | D-6 只在 routing.md 追加"Pre-spec 输入阶段"条款，不修改既有路由矩阵 |
| 双重规划权威（导演稿 vs design_spec+lock） | design_spec+lock 唯一权威；导演稿只作入料（director.md §6） |
| HTML vs SVG 内容基准 | SVG 唯一可见内容源；HTML 仅作视觉确认物（director.md §6） |

## 分析结论速记（深读汇总，实施 D-2/D-3/D-4 时引用）

- **guizang 校验器（validate-swiss-deck.mjs）检测项分两类**：静态（版式登记/未登记版式/顶部标题居中/自绘网格/SVG 文字/图片槽位等 ~14 项）+ 实测渲染（DOM 溢出/上下视觉溢出/nav-safe 越线/修过头/标题间距等 ~6 项，Playwright 1600×900）
- **溢出修正阶梯**：≤40px 微调 → 40-90 压间距 → 90-160 压标题 → 160+ 换版式（guizang 实测经验，直接用于我们的 P0 输出建议）
- **guizang 清单分级实为 P0（慎败）/P1（节奏）/P2（打磨）/P3（操作细节）四级**；早前"P0/P1/P2"说法作废
- **"锁定"哲学的两个硬条款**：颜色只从预设挑、禁混搭（如瑞士风禁 IKB+柠檬黄同屏）；版式先选登记后写代码、未登记版式=校验器硬失败
- **ppt-director 集成要点已全部落进 director.md §3-§6**（受众卡 5 字段、导演稿 10 字段、区域词清洗、5 冲突决策）
