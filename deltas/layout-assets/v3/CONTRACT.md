# 版式资产库 v3 · 填写契约（图片骨架族）

> 位置：`deltas/layout-assets/v3/` ｜ 前置：v0 通用契约见 `../v0/CONTRACT.md`
> 本文件只定义 **v3 新增的 3 个图片骨架**；v0 的通用硬标准（bounds / page-role /
> 字号档位 / checker 零 blocking / 层级字号差 ≥6pt / 卫生标记）继续生效。
> 状态：3/3 通过 `svg_quality_checker --quick-generate --stage final`，blocking 0 / introduced 0。

## 1. 与 v0/v1/v2 的关系

v3 是**能力补齐**，不是替代：v0/v1/v2 的全部骨架**不含图片位**，v3 补上图片这一层。
素材策略、比例规范与来源矩阵见 [`docs/image-strategy.md`](../../../docs/image-strategy.md)。

## 2. 通用约束（继承 + 新增）

**v3-1 · 图片引用路径固定为 `../images/<name>`**
SVG 位于项目 `svg_output/`，图片位于项目 `images/`，故相对路径为 `../images/`。
引用位必须带**显式注释**标记，便于检索与批量替换：

```xml
<!-- IMAGE: images/team-4x3-01.jpg 4:3 fill -->
<g id="img-split" data-pptx-bounds="80 170 520 390">
  <image href="../images/split-4x3.png" x="80" y="170" width="520" height="390"
         preserveAspectRatio="xMidYMid slice"/>
</g>
```

**v3-2 · 比例契约：槽位比例固定，图片按 `slice` 裁剪**
槽位宽高比一经确定不得改动；图片比例不符时由 `xMidYMid slice`（≈`cover`）**中心裁剪**适配。
**主体必须靠近画面中心**，否则会被裁掉（`docs/image-strategy.md` §4）。

**v3-3 · `meet` 会改变 Picture shape 尺寸（实测）**
用 `meet`（≈`contain`）时，导出的 **Picture shape 会收缩到图片自身比例并居中**，
**不是**在槽位内留白。若要求 shape 严格等于槽位几何，**必须用 `slice`**。

**v3-4 · 图片元素包裹在带 bounds 的组内**
`<image>` 必须放在带 `data-pptx-bounds` 的 `<g>` 内，且 bounds 与图片的
`x/y/width/height` 一致。

**v3-5 · 图注是槽位，不是示例数据**
所有图注/说明一律用 `【槽位】` 标记（遵守 T-FIX4 卫生标准）；
**不得**留无标记的示例图注。

## 3. 各骨架槽位定义

### 3.1 `image-hero.svg` — 满幅图 + 标题浮层

| 槽位 | 字号 | 上限 | 必填 |
|---|---|---|---|
| `【主标题】` | 56pt Bold（白字） | ≤18 字 | ✅ |
| `【副标题】` | 24pt | ≤22 字 | 可省 |
| `【图片说明】` | 18pt | ≤24 字 | 可省 |

- **构成**：图片满幅 1280×720；底部 252px 高、`#0A0A0A` 68% 透明罩承托文字
- **图片比例**：16:9（也吃 3:2，会裁剪左右）
- `data-pptx-page-role="cover"`
- **用途**：封面 / 章节页 / 愿景页——需要"一张图定调"时

### 3.2 `image-split.svg` — 左图右文

| 槽位 | 字号 | 位置 | 上限 |
|---|---|---|---|
| `【页面标题】` | 40pt Bold | x=80,y=90 | ≤21 字 |
| `【栏目标题】` | 28pt Bold（蓝） | x=660,y=218 | ≤8 字 |
| `【要点N标题】` ×3 | 22pt SemiBold | y=286/424/562 | ≤12 字 |
| `【要点N说明】` ×3 | 16pt（2 行 tspan） | 标题下 36px | 每行 ≤16 字 |
| `【图片说明】` | 18pt | x=80,y=612 | ≤24 字 |
| `【说明补充】` | 16pt | x=80,y=644 | ≤20 字 |

- **构成**：左图 520×390（**精确 4:3**）+ 右文栏 540px
- **反向变体**：把 `img-split` 与 `text-col` 两个组的 x 互换并镜像文字对齐
  （图右侧 x=680、文左侧 x=80）；**当前骨架只提供左图右文**，反向需自行镜像
- **用途**：产品页 / 案例页 / 方案页——图是论据，文是解释

### 3.3 `image-grid.svg` — 3×2 网格 + 图注

| 槽位 | 字号 | 上限 |
|---|---|---|
| `【页面标题】` | 40pt Bold | ≤21 字 |
| `【图N标题】` ×6 | 18pt SemiBold | ≤6 字 |
| `【图N说明】` ×6 | 16pt | ≤16 字 |

- **构成**：3 列 × 2 行，单格 **284×213（精确 4:3）**；列间距 40px，行间距 68px
- **列 x 起点**：174 / 498 / 822（总计 932px，居中）
- **行 y**：第一行图 150、图注 368；第二行图 431、图注 650
- **比例统一 4:3**，**不得混用其他比例**（等高对齐是此页型的前提）
- **用途**：团队页 / 多案例 / 对比墙——需要同规格并列比较时

## 4. 填充流程

```powershell
# 1) 项目初始化（务必带 --dir）
python <vendor>\scripts\project_manager.py init <name> --dir <TEMP> --format ppt169 --quick-generate

# 2) 放图：项目 images/ 目录
Copy-Item <素材> "<proj>\images\<用途>-<比例>.jpg"

# 3) 选 v3 骨架 → 复制为 svg_output/P01.svg …，替换【槽位】与图片 href
#    图片位注释同步改为真实文件名

# 4) 质量门（须 0 blocking）
python <vendor>\scripts\svg_quality_checker.py <proj> --quick-generate --stage final --json

# 5) 卫生 + 重叠（T-FIX4 / T-FIX5 产出）
python deltas\layout-assets\check_hygiene.py "<proj>\svg_output"
python deltas\layout-assets\check_overlap.py "<proj>\svg_output"

# 6) 导出（图片将内嵌为 Picture shape）
python <vendor>\scripts\svg_to_pptx.py <proj> --quick-generate --no-notes
```

## 5. 已知边界

- **图片内容不参与质检**：`check_hygiene` / `check_overlap` 只解析文本与几何，
  不解析图片内容；图片是否合适依赖**人工目视**。
- **无实拍素材**：本骨架族只提供图位，不提供素材；素材来源见 `docs/image-strategy.md` §1。
- **反向变体需手工镜像**：`image-split` 未内置右图左文变体。
- **仅位图实测**：`<image>` 也能引用 SVG，但本轮未实测。
- **`image` 元素不带 `data-pptx-bounds`**：bounds 由外层 `<g>` 承载。
