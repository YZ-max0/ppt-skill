# 项目全景评估（引导协议 + Agent 入口版）

> 日期：2026-09-15 ｜ 状态：测试集 v1 全部跑完 + 工程收尾 + 引导协议 + Agent 入口 ｜ **39 commits**
>
> 历史快照：本文件此前版本为「测试集收官版」（32 commits / 26 骨架 / 图片位缺失），
> 那三条均已被后续任务卡推进，**以本版为准**。

## 一、轨迹一句话

从"吸收 8 个外部 PPT skill"出发，建成了一套**自有的 PPT 制作系统**：
MIT 基座 + 导演式工作流 + **29 版式骨架** + **9 类图表 + 通用表格生成器** +
**四道自动质检闸** + 渲染目视闭环 + **发起引导协议** + **Agent 入口**。

## 二、交付物总账

| 层 | 数量 | 明细 |
|---|---|---|
| 基座 | 1 | ppt-master 5.0.0（vendor 仅登记改动，**零 diff**） |
| 骨架 | **29** | v0×6 + v1×12（含答辩 2）+ v2×8 + **v3×3（图片位）** |
| 图表 | **9 类**（base 契约） | column / grouped_bar / line / area / dual_axis / bullet / progress / waterfall / funnel |
| 图表 | **4 类**（v2 骨架契约） | bar-chart / line-chart / donut-chart / comparison-bars（**坐标已自动化**） |
| 表格 | 通用 | `fill_table.py`（任意行列 → 原生 Table 标记 + metadata） |
| 图片 | 3 骨架 + 链路 | `image-hero` / `image-split` / `image-grid`；内嵌 Picture 已验证 |
| 工具 | **10 个脚本** | 见 §六 |
| 工作流文档 | **4** | director / style-lock / presenter-mode / **intake-guide** |
| Agent 入口 | 2 | `SKILL.md`（主）+ `AGENTS.md`（转发） |
| 测试报告 | **16 + 4 评审** | e2e-01~06（6）+ img1 / a1 / guide1（3）+ m1 / m2 / m2b / m2b-r1 / m2c / pub1 / smoke（7）；另 visual-review-01~04 |
| 失败模式台账 | **C-001 ~ C-035** | 全部闭环或如实记录 |

## 三、测试集 v1 结果（6/6）

| 输入 | 档位 | 结果 | 特色验证 |
|---|---|---|---|
| T-01 周报 | ①快速 | 6 页全过 | 快速通道 / 资产库压缩 88% |
| T-02 述职 | ②标准 | 14 页全过 | base 图表接入首战 |
| T-03 方案 | ③导演 | 21 页全过 | 导演四阶段首战 |
| T-04 技术分享 | ②标准 | 25 页全过 | 逐字稿轨道首落地（5061 字） |
| T-05 BP 路演 | ③导演 | 17 页全过 | 视觉巅峰（4.5/6） |
| T-06 答辩 | ③导演 | 20 页全过 | 评审卡首战（24 检查→7 真问题） |

## 四、质量体系终态

```
四道自动闸：checker → D-2（出框/标题）→ hygiene（泄漏）→ overlap（跨组重叠）
                     ↓ 全绿之后
永久责任：指挥官/用户 目视 contact sheet（不可省略）
```

**"测不出"问题谱系（五次实锤）**：
P09 内容丢失（色数测不出）→ C-011 泄漏（质检器测不出）→ C-015 重叠（checker 测不出）
→ C-019 语义（全部测不出）→ **C-023/C-024 事实错误（评审卡才发现）**。

**结论**：闸门证明"没违反已知规则"；**语义与事实正确性只能靠内容审查 + 目视**。

> **新增手段（C-032）**：T-A1 的几何比对工具**首次由自动化发现手写骨架缺陷**
> （donut 首段弧长 50% vs 数据 75%）——这是继"人眼看图"之后的第二类发现途径。

## 五、视觉评分轨迹

2.5（t03 初版）→ 4.0（t03-v2 增强）→ **4.5（t05 BP）** / 6。

## 六、工具与文档清单（实测存在）

**工具脚本（10）**

| 路径 | 用途 |
|---|---|
| `deltas/layout-assets/check_hygiene.py` | 骨架示例内容泄漏检查 |
| `deltas/layout-assets/check_overlap.py` | 跨组重叠检查（C-015 类） |
| `deltas/pptx-fill-check/detect_overflow.py` | 出框检测 |
| `deltas/pptx-fill-check/check_title_consistency.py` | 标题字号一致性 |
| `deltas/chart-fill/fill_chart.py` | base 图表生成（9 类） |
| `deltas/chart-fill/v2_chart_gen.py` | v2 图表坐标重算（4 类） |
| `deltas/chart-fill/compare_v2.py` | 生成版 vs 手写版几何比对 |
| `deltas/chart-fill/fill_skeleton.py` | 骨架槽位填充器 |
| `deltas/table-fill/fill_table.py` | 表格生成（原生 Table） |
| `deltas/render-preview/render_png.py` | pptx → PNG + contact sheet |

（另有读回验证 3 个：`verify_picture.py` / `verify_table.py` / `check_notes.py`，
以及 5 个可复现示例 deck 构建脚本）

**关键文档**

| 路径 | 用途 |
|---|---|
| `SKILL.md` / `AGENTS.md` | **Agent 入口**（路径纪律 / 加载顺序 / 路由 / 纪律） |
| `deltas/intake-guide.md` | **发起引导协议**（二分入口 / 质量协议 / 4 原则 / 2 示例对话） |
| `docs/USAGE.md` | 逐步操作（§8 主轨引导 + 辅轨精确模式） |
| `docs/QUALITY-TIERS.md` | 三档质量与耗时 |
| `docs/image-strategy.md` | 图片素材策略 |
| `docs/windows-notes.md` | 环境绕行 W-1~W-8 |

## 七、遗留清单（已逐项复核）

| 项 | 状态 |
|---|---|
| ~~图片位能力~~ | ✅ **已完成**（T-IMG1）：v3 三个图片骨架 + 内嵌链路验证 |
| ~~tables/ 族~~ | ✅ **已完成**（T-A1）：`fill_table.py` 通用生成 + 原生 Table 读回 |
| ~~评审卡 B3 登记~~ | ✅ **已完成**（T-GUIDE1 前序）：`director.md` §2 已登记为 B3 硬门禁 |
| ~~返修后重跑纪律~~ | ✅ **已完成**（T-GUIDE1 前序）：已写入 `USAGE.md` §2.2（C-028） |
| ~~Skill 形态入口~~ | ✅ **已完成**：根级 `SKILL.md` + `AGENTS.md`（本轮补） |
| **渲染器冗余** | ⚠️ **未解**：单点依赖 WPS COM（LibreOffice 未装，需用户授权） |
| **公开化** | ⚠️ 待定：仓库 Private/Public 需用户决策；公开前复核第三方资产表述 |
| **图片素材获取** | ⚠️ 受限：搜图/生图需 API key + 外网，本机不可用（见 `image-strategy.md` §1） |
| **术语审计常驻化** | ⚠️ 未做：当前是一次性脚本，建议 `check_terms.py`（`guide1-report.md` 建议 1） |
| **`line-chart` 骨架缺陷** | ⚠️ 已记录未修（C-033）：折线 6 点 vs 标签 3 点，自相矛盾 |
| **文档计数漂移** | ⚠️ 反复出现（24→29 已修，但无自动同步机制） |

## 八、结论

**能力与验证双达标**：6 个真实场景全部一次通过四道质检；四要素能力面（文字/图表/图片/表格）齐备；
视觉从"能看"到"像专业作品"；**发起门槛已降到"一句话"**，且已有 Agent 入口可供本地实测。

**当前阶段**：进入**用户实测期**。最需要验证的是——本地 agent 是否按 `SKILL.md` §1
的加载顺序先读 `intake-guide.md` 并执行引导协议。
