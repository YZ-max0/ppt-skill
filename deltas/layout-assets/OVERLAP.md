# 跨组重叠检查（check_overlap）

> T-FIX5 产出 ｜ 落点 `deltas/layout-assets/check_overlap.py`
> 定位：**第三类"测不出"问题的自动闸**——单组几何合法、跨组整体冲突

## 1. 为什么需要它

本项目已有三道闸，各管一层，但有一个共同的盲区：

| 闸 | 管什么 | 拦得住 | **拦不住** |
|---|---|---|---|
| `svg_quality_checker`（base） | 几何 | 元素超出自身 `<g>` bounds / 画布 | 跨组冲突 |
| `detect_overflow.py` + `check_title_consistency.py`（D-2） | 填充后出框、标题一致性 | 文本溢出容器 | 跨组冲突 |
| `check_hygiene.py`（T-FIX4） | 内容泄漏 | 骨架示例内容残留 | 跨组冲突 |
| **`check_overlap.py`（本工具）** | **跨组重叠** | 图例压字、标签叠印 | — |

### 两起真实事故（同根）

| 编号 | 现象 | 为什么前三道闸都没拦住 |
|---|---|---|
| **C-011** | T-03 的品牌字 `KB` 出现在 T-02 封面上 | 内容泄漏：几何完全合法 |
| **C-015** | 图例文字压住横轴类目标签（`legend` 与 `chart-plot` 同在 `y=600`） | **跨组重叠**：两个组各自的 bounds 都合法，checker 报 `blocking: 0` |

两起的共性：**每一组单独看都没问题，合起来才是错的**。这类缺陷此前**只能靠人眼看
contact sheet 发现**——C-011 与 C-015 都是这样被发现的。本工具把 C-015 这一类变成自动断言。

> C-011 属内容层，已由 `check_hygiene.py` 覆盖（T-FIX4）。本工具补的是**几何-视觉层**。

## 2. 检测项

1. **文本 × 文本**（跨组）：两文本估算 bbox 相交
2. **文本 × 图形标记**（跨组）：文本 bbox 与**标记类**图形相交
3. 图例/轴标签类重叠：由 1、2 自然覆盖（C-015 即"`legend` 组的 line × `chart-plot` 组的轴标签"）

### 关键设计：区分「底纹」与「标记」

卡内只规定"**同组内**文本-图形重叠合法（深色格反白字、色块上的标签）"。
**实测发现跨组的文本-图形重叠也大量合法**，且是刻意设计：

- `v2/cover-bold`：白色标题压在 `bold-geometry` 的 520×720 蓝色块上（**不同组**）
- 图表页：数值标签压在柱体/轨道条上

若一律上报，正样本会产生大量误报（实测 T-02 报 3 处、T-04 报 2 处，**全为设计意图**）。
故判据收紧为：**只有"标记类"图形才与文本比对**。

| 元素 | 判定 |
|---|---|
| `line` / `circle` / `polyline` / `polygon` | **标记类**（细笔画、按数据定位）→ 参与比对 |
| `rect` 面积 < 文本 bbox 面积 × 3 | **标记类**（小色块）→ 参与比对 |
| `rect` 面积 ≥ 文本 bbox 面积 × 3 | **底纹/面板**（刻意承载其上文字）→ 放行 |

真正的病灶 C-015 是**图例线（细笔画标记）压住轴标签文字**，落在"标记类"内，故被拦住。

## 3. 豁免机制

| 机制 | 用法 | 适用 |
|---|---|---|
| 整页背景自动跳过 | `id="page-bg"` 的组；或根级满画布 rect（≥1200×660） | 骨架与 chart-fill 产物都可能把背景 rect 裸放根级 |
| 同组放行 | 同一 `<g id>` 内的元素不比较 | 设计固有叠放（柱+柱顶数值同组） |
| 显式豁免 | 元素或其祖先组标 `data-ok-overlap="true"` | 刻意叠放（装饰压字等） |
| 面积阈值 | `--threshold`（默认 `0.05`，即较小者面积的 5%） | 过滤贴边/擦边，避免误报 |

## 4. 用法

```powershell
# 基本：检查项目的 svg_output（填充后、导出前）
python deltas\layout-assets\check_overlap.py "<项目>\svg_output"

# 调阈值 / 输出 JSON
python deltas\layout-assets\check_overlap.py "<项目>\svg_output" --threshold 0.10
python deltas\layout-assets\check_overlap.py "<项目>\svg_output" --json -o overlap.json

# 扫描骨架库
python deltas\layout-assets\check_overlap.py deltas\layout-assets
```

**退出码**：`0` = 无跨组重叠 ｜ `2` = 发现重叠（P1）

**输出示例**：

```
[Overlap] 扫描 14 个 SVG；元素 249（文本 155 / 图形 94）；阈值 5%
[FAIL] 发现 1 处跨组重叠（P1）：
  [P1] P06.svg: [chart-plot] 'Q1' × [legend] 'line' — 重叠 32%
```

## 5. 双向验证结果（T-FIX5 R3）

| 样本 | 期望 | 实测 |
|---|---|---|
| 正样本：T-02 产物（14 页，修复 `LEGEND_Y` 后） | exit 0 | ✅ exit 0，0 误报 |
| 正样本：T-04 产物（25 页） | exit 0 | ✅ exit 0，0 误报 |
| 正样本：全库 24 骨架 | exit 0 | ✅ exit 0 |
| **负样本：C-015 复现**（图例拉回 `CAT_Y` 同排） | 被拦 | ✅ exit 2，报 `[chart-plot] 'W1' × [legend] 'line' 重叠 32%` |
| 负样本：构造 text×text 跨组重叠 | 被拦 | ✅ exit 2，重叠 74% |
| 豁免：给相撞组标 `data-ok-overlap="true"` | 放行 | ✅ exit 0 |
| **历史真阳性**：修复前的 T-02 `P06`（legend 在 y=593） | 被拦 | ✅ 报 `Q1 × line 重叠 32%` —— 与 C-015 现象一致 |

> 阈值敏感性：T-02 在 `--threshold` 取 0.02 / 0.05 / 0.10 时均为 0 命中，说明结论不依赖阈值取值。

## 6. bbox 口径

与 `deltas/pptx-fill-check/capacity.py` 及 vendor checker 对齐：

- **视觉宽度**（vw）：CJK/全角 = 1.0，ASCII = 0.5，空格 = 0.35，其他 = 0.8
- **文本宽** = `vw(text) × font-size`；**高** = `ascent 0.85 + descent 0.35`（× font-size）
  （与 vendor `svg_quality/checker.py` 的 `_text_line_vertical_extent` 同口径）
- **多行文本**：按 `<tspan>` 的 `x`/`dy` 逐行累加，取并集
- **`text-anchor`**：支持 `start` / `middle` / `end`
- **字体继承**：沿祖先链向上找 `font-size` / `text-anchor`
- **图形**：`rect`/`circle` 取几何极值；`polyline`/`polygon` 取点集极值；
  `line` 按 `stroke-width` 补厚度（避免零面积漏检）

## 7. 已知边界

- **bbox 是估算**：不含字距微调（`letter-spacing`）、字形的实际侧承（side bearing）、
  以及 `<tspan>` 之外更复杂的文本布局。它是"足够发现相撞"的近似，不是渲染级精确值。
- **不检测同组内重叠**：同组视为设计意图（柱+柱顶数值等）；若某骨架真的在同组内做错，
  本工具不会报。
- **不检测图形 × 图形**：刻意叠放（色块叠加、装饰条）太常见，误报率会很高。
- **不检测旋转/变换**：骨架与 chart-fill 产物均无 `transform="translate(...)"`
  （实测 24 骨架 0 处），故未实现变换矩阵；若未来骨架引入变换，需扩展。
- **阈值需按项目校准**：默认 5% 对当前产物 0 误报；引入新骨架族时应复跑正样本。
