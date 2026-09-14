# 版式资产库 v0 · 填写契约

> 位置：`deltas/layout-assets/v0/`（repo 定制层，vendor 零改动）
> 用途：把"每页从零手写 SVG"变为"选骨架 + 机械填充"，压缩 T-01 类快速出稿的耗时。
> 形态：**合规 SVG 骨架 + 本契约**（轻量；base 原生 `create-layout` workspace 化留作 M2+ 候选）。

## 1. 骨架清单与适配页型

| 骨架文件 | 页型 | `data-pptx-page-role` | 适配场景 |
|---|---|---|---|
| `cover.svg` | 封面 | `cover` | 汇报/提案/分享的开场页 |
| `bullets.svg` | 要点列表 | `content` | 3–4 项并列成果、清单、并列论据 |
| `two-col-compare.svg` | 双栏对比 | `content` | 风险/对策、A/B 方案、前后对照 |
| `timeline.svg` | 时间轴 | `content` | 3 节点计划、实施路径、阶段路线 |
| `kpi-hero.svg` | 数据大字 | `content` | 1–3 个关键数字、指标达成、成绩单 |
| `closing.svg` | 结尾收束 | `ending` | 总结句 + 呼吁/下一步 |

## 2. 统一占位标记

骨架中所有待填内容用 **`【槽位名】示例内容`** 形式标记：

```xml
<text x="80" y="90" font-size="40" font-weight="700" fill="#0A0A0A">【页面标题】本周完成四项工作，整体进度符合预期</text>
```

**填充规则（硬性）**：

1. **必须整段替换**"`【槽位名】示例内容`"整体，不得只替换方括号部分
2. 填充后产物中 `【` 计数必须为 **0**（验收项）
3. 骨架中的示例文案是**长度上限参照**：替换文本不应显著长于示例（示例已按最坏情况收口，
   并通过 checker 验证）

## 3. 各骨架槽位定义

### cover.svg

| 槽位 | 元素 | 字号 | 上限 | 必填 |
|---|---|---|---|---|
| `【主标题】` | x=120,y=300 | 56pt Bold | 示例 18 字 | ✅ |
| `【副标题】` | x=120,y=360 | 24pt | 示例 22 字 | ✅ |
| `【汇报人】` | x=120,y=600 | 18pt | — | 可省 |
| `【周期】` | x=120,y=640 | 18pt | — | 可省 |

> 主标题实际容量：容器宽 1040px，56pt 中文约 18 字/行；超出会触发 checker。

### bullets.svg（3–4 条）

| 槽位 | 元素 | 字号 | 上限 |
|---|---|---|---|
| `【页面标题】` | x=80,y=90 | 40pt Bold | 示例 21 字 |
| `【要点N】` ×4 | x=185 | 22pt SemiBold | 示例 13 字 |
| `【说明N】` ×4 | x=185 | 16pt | 示例 26 字 |

> 4 条为满配；少于 4 条时删除对应 `<rect>` 底纹 + 3 个 `<text>`（成组删除）。
> 每条的 y 坐标固定：165/281/397/513（行高 116px）。

### two-col-compare.svg

| 槽位 | 字号 | 上限 |
|---|---|---|
| `【页面标题】` | 40pt Bold | 示例 18 字 |
| `【左栏标题】`/`【右栏标题】` | 28pt Bold | 示例 5 字 |
| `【左栏主句】`/`【右栏主句】` | 22pt SemiBold | 示例 12 字 |
| `【左栏影响】`/`【右栏影响】` | 16pt | 示例 14 字 |
| `【左栏评估】`/`【右栏评估】` | 16pt | 示例 9 字 |
| `【左栏对策】`/`【右栏对策】` | 16pt（2 行 tspan） | 每行示例 14 字 |

> 左右栏 x 起点：80 / 655；栏宽 545px。

### timeline.svg（3 节点）

| 槽位 | 字号 | x 位置 | 上限 |
|---|---|---|---|
| `【页面标题】` | 40pt Bold | 80 | 示例 18 字 |
| `【节点N标题】` | 22pt Bold | 150/580/900 | 示例 5 字 |
| `【节点N主句】` | 20pt SemiBold | 150/580/900 | 示例 10 字 |
| `【节点N说明】` | 16pt（2 行 tspan） | 150/580/900 | 每行示例 12 字 |
| `【小结标题】` | 20pt SemiBold | 120 | 示例 4 字 |
| `【小结正文】` | 18pt（2 行 tspan） | 120 | 每行示例 20 字 |

> **节点三 x=900 是实测右界**（曾用 960/1010 触发 checker 越界）；不可再右移。

### kpi-hero.svg（1–3 个数字）

| 槽位 | 字号 | x 位置 | 上限 |
|---|---|---|---|
| `【页面标题】` | 40pt Bold | 80 | 示例 18 字 |
| `【值1】`/`【值2】`/`【值3】` | 96pt Bold | 80/490/860 | **槽位名+值**合计 ≤5 字符（96pt 列宽约束，T-FIX4） |
| `【指标N名称】` | 22pt SemiBold | 80/490/860 | 示例 10 字 |
| `【指标N说明】` | 16pt | 80/490/860 | 示例 12 字 |
| `【结论标题】` | 20pt SemiBold | 120 | 示例 6 字 |
| `【结论文本】` | 18pt（2 行 tspan） | 120 | 每行示例 19 字 |

> **指标三 x=860 是实测右界**（曾用 900 触发越界）。只用 1–2 个数字时，保留首个数字组、
> 删除其余两组的 `<text>`；数字 x 可保持不变（左对齐留白）。

### closing.svg

| 槽位 | 字号 | 上限 |
|---|---|---|
| `【结尾标题】` | 56pt Bold | 示例 5 字 |
| `【核心句】` | 26pt | 示例 16 字 |
| `【收束文本】` | 20pt（2 行 tspan） | 每行示例 24 字 |

## 4. 骨架硬标准（吸收 C-001/C-003/W-5）

入库骨架必须同时满足：

1. **根级 `<g>` 全带 `data-pptx-bounds`**；整页背景独立为 `page-bg` 组，不裸放 `<rect>`
2. **根 `<svg>` 带 `data-pptx-page-role`**（cover / content / ending）
3. **多行文本用单个 `<text>` + 多个 `<tspan>`**，不用同级多个 `<text>`
4. **字号只用既有档位**：56 / 40 / 28 / 26 / 24 / 22 / 20 / 18 / 16 / 96(pt)
5. **入库前必须过 checker**：`svg_quality_checker.py <proj> --quick-generate --stage final --json`
   须 **blocking = 0 且 introduced = 0**
6. **bounds 已按最坏情况占位文案验证**：填充时不需重新测量/试探 bounds（见 §5）
7. **骨架内相邻层级的字号差 ≥ 6pt**（如说明行 16pt → 标题 22pt，而非 16 → 18）。
   理由：`check_title_consistency.py` 的 free-design 路径按字号聚类分档（`--size-bucket-gap`
   默认 4pt），字号过于密集会让不同层级落进同一档，产生"档内混角色"误报（C-004/C-007）。
   拉开 ≥6pt 可从源头避免该耦合。**此约束自 T-FIX3 起对未来骨架生效；已有骨架不回改。**

## 5. 填充流程（推荐顺序）

```powershell
# 1) 新建 quick 项目
python <vendor>\scripts\project_manager.py init <name> --format ppt169 --quick-generate

# 2) 按页型选骨架，复制为 P01.svg / P02.svg / ...
#    复制后仅替换【槽位】文本，不动 bounds / 坐标 / 字号

# 3) 质量门（必须 0 blocking）
python <vendor>\scripts\svg_quality_checker.py <proj> --quick-generate --stage final --json

# 4) 导出
python <vendor>\scripts\svg_to_pptx.py <proj> --quick-generate --no-notes

# 5) 后置质检
python <deltas>\pptx-fill-check\detect_overflow.py <pptx> --json
python <deltas>\pptx-fill-check\check_title_consistency.py <pptx> --json
```

## 6. 已知边界

- 骨架是**固定几何**：填充文本显著长于示例文案时仍会触发 checker 越界，须删减或换骨架。
- 骨架为 **free-design flat**（无 Master/Layout 结构），`data-pptx-page-role` 必填。
- 未覆盖页型（如需 5 列矩阵、复杂图表、图片页）需手写或等待 v1 扩充。
- 配色固定为 IKB 蓝 + 灰阶（`#002FA7` / `#0A0A0A` / `#737373` / `#F0F0EE` / `#E2E8F0`）；
  换主题需同步替换色值，当前无参数化机制。
